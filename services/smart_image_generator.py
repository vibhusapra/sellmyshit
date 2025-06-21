from typing import List, Dict, Any, Tuple
import asyncio
import httpx
from PIL import Image
from io import BytesIO
import os
import uuid
from services.bfl_client import BFLClient
from services.image_insights import ImageInsightsService
from app.config import settings


class SmartImageGenerator:
    """Generates multiple optimized product images based on market insights."""
    
    def __init__(self):
        self.bfl_client = BFLClient()
        self.insights_service = ImageInsightsService()
        self.enhanced_dir = "enhanced"
        os.makedirs(self.enhanced_dir, exist_ok=True)
    
    async def generate_listing_portfolio(self, 
                                       original_image: bytes,
                                       item_analysis: Dict[str, Any],
                                       enhancement_mode: str = "smart",
                                       progress_callback=None) -> Dict[str, Any]:
        """Generate a complete portfolio of listing images."""
        
        result = {
            "mode": enhancement_mode,
            "original_analysis": item_analysis,
            "generated_images": [],
            "insights": {},
            "errors": []
        }
        
        def update_progress(msg):
            if progress_callback:
                progress_callback(msg)
        
        if enhancement_mode == "quick":
            # Just do background removal
            enhanced_image, path = await self._quick_enhance(original_image)
            result["generated_images"].append({
                "type": "background_removal",
                "description": "Clean white background",
                "path": path,
                "image_data": enhanced_image
            })
        
        elif enhancement_mode == "smart":
            # Full AI-driven portfolio generation
            
            # Get market insights
            insights = await self.insights_service.analyze_successful_listings(
                item_analysis["item_name"],
                item_analysis["category"],
                item_analysis.get("brand")
            )
            result["insights"] = insights
            
            # Generate prompts based on insights
            prompts = self.insights_service.generate_flux_prompts(
                f"{item_analysis.get('brand', '')} {item_analysis['item_name']}".strip(),
                insights
            )
            
            # Generate images in parallel (limit concurrency)
            tasks = []
            for prompt_data in prompts[:5]:  # Limit to 5 images for now
                task = self._generate_single_image(
                    original_image,
                    prompt_data,
                    item_analysis
                )
                tasks.append(task)
            
            # Process in batches of 2 to avoid overwhelming the API
            for i in range(0, len(tasks), 2):
                batch = tasks[i:i+2]
                batch_results = await asyncio.gather(*batch, return_exceptions=True)
                
                for j, result_item in enumerate(batch_results):
                    if isinstance(result_item, Exception):
                        result["errors"].append(str(result_item))
                    else:
                        result["generated_images"].append(result_item)
                
                # Small delay between batches
                if i + 2 < len(tasks):
                    await asyncio.sleep(2)
        
        return result
    
    async def _quick_enhance(self, image_data: bytes) -> Tuple[bytes, str]:
        """Quick enhancement with just background removal."""
        prompt = "Product on clean white background, professional lighting, centered composition"
        
        enhanced_data = await self.bfl_client.generate_image_edit(
            image_data, 
            prompt=prompt
        )
        
        filename = f"quick_enhanced_{uuid.uuid4()}.png"
        filepath = os.path.join(self.enhanced_dir, filename)
        
        with open(filepath, 'wb') as f:
            f.write(enhanced_data)
        
        return enhanced_data, filepath
    
    async def _generate_single_image(self, 
                                   original_image: bytes,
                                   prompt_data: Dict[str, str],
                                   item_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a single enhanced image based on prompt."""
        
        try:
            # Generate the image using BFL
            generated_image = await self.bfl_client.generate_image_edit(
                original_image,
                prompt=prompt_data["prompt"]
            )
            
            # Save the image
            filename = f"{prompt_data['type']}_{uuid.uuid4()}.png"
            filepath = os.path.join(self.enhanced_dir, filename)
            
            with open(filepath, 'wb') as f:
                f.write(generated_image)
            
            return {
                "type": prompt_data["type"],
                "description": prompt_data["description"],
                "prompt": prompt_data["prompt"],
                "path": filepath,
                "url": f"/image/{filename}",
                "image_data": generated_image,
                "priority": prompt_data["priority"]
            }
            
        except Exception as e:
            raise Exception(f"Failed to generate {prompt_data['type']} image: {str(e)}")
    
    def _encode_image(self, image_data: bytes) -> str:
        """Encode image to base64."""
        import base64
        return base64.b64encode(image_data).decode('utf-8')
    
    async def generate_custom_images(self,
                                   original_image: bytes,
                                   custom_prompts: List[str]) -> List[Dict[str, Any]]:
        """Generate images with custom user-provided prompts."""
        
        results = []
        for i, prompt in enumerate(custom_prompts):
            try:
                prompt_data = {
                    "type": "custom",
                    "description": f"Custom image {i+1}",
                    "prompt": prompt,
                    "priority": "high"
                }
                
                result = await self._generate_single_image(
                    original_image,
                    prompt_data,
                    {}
                )
                results.append(result)
                
            except Exception as e:
                results.append({
                    "type": "custom",
                    "description": f"Custom image {i+1}",
                    "path": None,
                    "image_data": None,
                    "error": str(e)
                })
        
        return results
    
    async def generate_variations(self, image_data: bytes) -> Dict[str, Any]:
        """Generate 5 different product image variations using FLUX.1 Kontext."""
        
        # Define 5 different variation prompts
        variation_prompts = [
            "Professional product photography on pure white background, centered composition, soft even lighting, clean shadows",
            "Product in natural lifestyle setting, warm ambient lighting, realistic environment, home or office context",
            "Dramatic product shot with dark background, rim lighting, luxury presentation, premium feel, high contrast",
            "Minimalist product photo with subtle shadows, clean composition, neutral gray background, modern aesthetic",
            "Close-up detail shot highlighting textures and quality, macro perspective, sharp focus on product features"
        ]
        
        # Generate all variations
        variations = await self.bfl_client.generate_multiple_variations(
            image_data,
            variation_prompts,
            self.enhanced_dir
        )
        
        return {
            "total_requested": len(variation_prompts),
            "total_generated": len([v for v in variations if v.get("error") is None]),
            "variations": variations
        }