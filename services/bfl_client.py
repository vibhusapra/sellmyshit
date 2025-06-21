import httpx
import asyncio
import base64
from typing import Dict, Any, Optional, List, Tuple
from io import BytesIO
from PIL import Image
import json
import uuid
import os
from app.config import settings


class BFLClient:
    """Client for interacting with BFL API for FLUX.1 Kontext image generation."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.bfl_api_key
        self.base_url = settings.bfl_api_base_url
        self.headers = {
            "x-key": self.api_key,
            "Content-Type": "application/json"
        }
        # BFL API limits
        self.max_image_size_mb = 20
        self.max_megapixels = 20
    
    def _compress_image(self, image_data: bytes) -> Tuple[bytes, bool]:
        """Compress image to meet BFL API requirements.
        
        Returns:
            Tuple of (compressed_image_bytes, was_compressed)
        """
        # Open image
        img = Image.open(BytesIO(image_data))
        
        # Check current size
        size_mb = len(image_data) / (1024 * 1024)
        width, height = img.size
        megapixels = (width * height) / 1_000_000
        
        print(f"[DEBUG] Original image: {width}x{height}, {megapixels:.1f}MP, {size_mb:.1f}MB")
        
        # If image is within limits, return as-is
        if size_mb <= self.max_image_size_mb and megapixels <= self.max_megapixels:
            return image_data, False
        
        # Need to compress
        compressed = False
        quality = 95
        
        # First, resize if megapixels exceed limit
        if megapixels > self.max_megapixels:
            # Calculate scaling factor
            scale_factor = (self.max_megapixels / megapixels) ** 0.5
            new_width = int(width * scale_factor * 0.95)  # 95% to ensure we're under limit
            new_height = int(height * scale_factor * 0.95)
            
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            print(f"[DEBUG] Resized to: {new_width}x{new_height}")
            compressed = True
        
        # Convert to RGB if necessary (removes alpha channel which can increase size)
        if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
            # Create white background
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
            img = background
            compressed = True
        elif img.mode not in ('RGB', 'L'):
            img = img.convert('RGB')
            compressed = True
        
        # Compress with decreasing quality until size is acceptable
        output = BytesIO()
        while quality >= 70:
            output.seek(0)
            output.truncate()
            
            # Save as JPEG for better compression
            img.save(output, format='JPEG', quality=quality, optimize=True)
            
            size_mb = len(output.getvalue()) / (1024 * 1024)
            
            if size_mb <= self.max_image_size_mb * 0.95:  # 95% to ensure we're under limit
                print(f"[DEBUG] Compressed to {size_mb:.1f}MB with quality {quality}")
                return output.getvalue(), True
            
            quality -= 5
            compressed = True
        
        # If still too large, do more aggressive resize
        scale = 0.7
        while scale > 0.3:
            new_size = (int(img.width * scale), int(img.height * scale))
            resized = img.resize(new_size, Image.Resampling.LANCZOS)
            
            output.seek(0)
            output.truncate()
            resized.save(output, format='JPEG', quality=85, optimize=True)
            
            size_mb = len(output.getvalue()) / (1024 * 1024)
            
            if size_mb <= self.max_image_size_mb * 0.95:
                print(f"[DEBUG] Final compression: {new_size[0]}x{new_size[1]}, {size_mb:.1f}MB")
                return output.getvalue(), True
            
            scale -= 0.1
        
        raise ValueError(f"Unable to compress image to under {self.max_image_size_mb}MB")
    
    async def generate_image_edit(self, 
                                 image_data: bytes, 
                                 prompt: str,
                                 aspect_ratio: str = "1:1",
                                 output_format: str = "png",
                                 safety_tolerance: int = 2) -> bytes:
        """Generate an edited image using FLUX.1 Kontext."""
        
        # Compress image if needed
        compressed_data, was_compressed = self._compress_image(image_data)
        if was_compressed:
            print("[DEBUG] Image was compressed to meet BFL API limits")
        
        # Convert image to base64
        image_base64 = base64.b64encode(compressed_data).decode('utf-8')
        
        # Prepare the request payload
        payload = {
            "prompt": prompt,
            "input_image": image_base64,
            "aspect_ratio": aspect_ratio,
            "output_format": output_format,
            "safety_tolerance": safety_tolerance
        }
        
        async with httpx.AsyncClient(timeout=300.0) as client:
            # Submit the generation request
            response = await client.post(
                f"{self.base_url}/flux-kontext-pro",
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            
            result = response.json()
            
            # Get the polling URL and request ID
            polling_url = result.get("polling_url")
            request_id = result.get("id")
            
            if not polling_url:
                raise Exception("No polling URL returned from API")
            
            print(f"[DEBUG] Request ID: {request_id}")
            print(f"[DEBUG] Polling URL: {polling_url}")
            
            # Poll for completion
            generated_image_url = await self._poll_for_completion(polling_url, request_id)
            
            # Download the generated image
            print(f"[DEBUG] Downloading image from: {generated_image_url}")
            
            # The signed URL should work without additional auth headers
            # Create a new client without auth headers for the download
            download_client = httpx.AsyncClient(timeout=30.0)
            try:
                # The URL might already be properly encoded, try using it directly
                image_response = await download_client.get(
                    generated_image_url,
                    follow_redirects=True
                )
                image_response.raise_for_status()
                
                print(f"[DEBUG] Image downloaded successfully, size: {len(image_response.content)} bytes")
                return image_response.content
            except httpx.HTTPStatusError as e:
                print(f"[DEBUG] Download failed with status {e.response.status_code}")
                print(f"[DEBUG] Response headers: {e.response.headers}")
                print(f"[DEBUG] Response body: {e.response.text}")
                raise
            finally:
                await download_client.aclose()
    
    async def _poll_for_completion(self, polling_url: str, request_id: Optional[str] = None, max_attempts: int = 60) -> str:
        """Poll the API until the image generation is complete."""
        
        print(f"[DEBUG] Starting to poll: {polling_url}")
        
        # Prepare params - only add id if not already in the URL
        params = {}
        if request_id and f"id={request_id}" not in polling_url:
            params["id"] = request_id
            print(f"[DEBUG] Adding request ID to params: {request_id}")
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            for attempt in range(max_attempts):
                response = await client.get(
                    polling_url,
                    headers={"x-key": self.api_key},
                    params=params if params else None
                )
                response.raise_for_status()
                
                result = response.json()
                status = result.get("status")
                
                print(f"[DEBUG] Poll attempt {attempt + 1}: Status = {status}")
                
                if status == "Ready":
                    # Get the generated image URL
                    sample = result.get("result", {}).get("sample")
                    if not sample:
                        raise Exception("No sample URL in completed result")
                    print(f"[DEBUG] Got image URL: {sample}")
                    return sample
                
                elif status == "Failed":
                    error_msg = result.get("error", "Unknown error")
                    raise Exception(f"Image generation failed: {error_msg}")
                
                elif status == "Pending" or status == "Processing":
                    # Wait before polling again
                    await asyncio.sleep(2)
                
                else:
                    raise Exception(f"Unknown status: {status}")
            
            raise Exception("Polling timeout: Image generation took too long")
    
    async def generate_multiple_variations(self,
                                         image_data: bytes,
                                         prompts: List[str],
                                         save_directory: str = "enhanced") -> List[Dict[str, Any]]:
        """Generate multiple image variations with different prompts."""
        
        os.makedirs(save_directory, exist_ok=True)
        results = []
        
        # Process prompts in batches to avoid overwhelming the API
        batch_size = 2
        for i in range(0, len(prompts), batch_size):
            batch = prompts[i:i + batch_size]
            
            # Create tasks for parallel processing
            tasks = []
            for j, prompt in enumerate(batch):
                task = self._generate_single_variation(
                    image_data, 
                    prompt, 
                    f"variation_{i+j+1}",
                    save_directory
                )
                tasks.append(task)
            
            # Execute batch
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            for idx, result in enumerate(batch_results):
                if isinstance(result, Exception):
                    results.append({
                        "type": f"variation_{i+idx+1}",
                        "prompt": batch[idx],
                        "error": str(result),
                        "path": None,
                        "url": None
                    })
                else:
                    results.append(result)
            
            # Small delay between batches
            if i + batch_size < len(prompts):
                await asyncio.sleep(2)
        
        return results
    
    async def _generate_single_variation(self,
                                       image_data: bytes,
                                       prompt: str,
                                       variation_type: str,
                                       save_directory: str) -> Dict[str, Any]:
        """Generate a single image variation."""
        
        try:
            # Generate the image
            generated_image = await self.generate_image_edit(image_data, prompt)
            
            # Save the image
            filename = f"{variation_type}_{uuid.uuid4()}.png"
            filepath = os.path.join(save_directory, filename)
            
            with open(filepath, 'wb') as f:
                f.write(generated_image)
            
            return {
                "type": variation_type,
                "prompt": prompt,
                "path": filepath,
                "url": f"/image/{filename}",
                "error": None
            }
            
        except Exception as e:
            raise Exception(f"Failed to generate {variation_type}: {str(e)}")