import httpx
import asyncio
import base64
from typing import Dict, Any, Optional, List
from io import BytesIO
from PIL import Image
import json
from app.config import settings


class ReplicateClient:
    def __init__(self, api_token: Optional[str] = None):
        self.api_token = api_token or settings.replicate_api_token
        self.base_url = "https://api.replicate.com/v1"
        self.headers = {
            "Authorization": f"Token {self.api_token}",
            "Content-Type": "application/json"
        }
    
    async def run_model(self, model_version: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Run a model on Replicate and wait for the result."""
        async with httpx.AsyncClient() as client:
            # Create prediction
            response = await client.post(
                f"{self.base_url}/predictions",
                headers=self.headers,
                json={
                    "version": model_version,
                    "input": inputs
                }
            )
            response.raise_for_status()
            prediction = response.json()
            
            # Poll for completion
            prediction_id = prediction["id"]
            while prediction["status"] not in ["succeeded", "failed", "canceled"]:
                await asyncio.sleep(1)
                response = await client.get(
                    f"{self.base_url}/predictions/{prediction_id}",
                    headers=self.headers
                )
                response.raise_for_status()
                prediction = response.json()
            
            if prediction["status"] == "failed":
                raise Exception(f"Prediction failed: {prediction.get('error')}")
            
            return prediction
    
    async def enhance_image(self, image_data: bytes, enhancement_type: str = "background_removal") -> bytes:
        """Enhance image using FLUX.1 model."""
        # Convert image to base64
        image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        # Prepare inputs based on enhancement type
        if enhancement_type == "background_removal":
            inputs = {
                "image": f"data:image/png;base64,{image_base64}",
                "prompt": "product photography, white background, professional lighting",
                "guidance_scale": 7.5,
                "num_inference_steps": 50,
                "scheduler": "DPMSolverMultistep"
            }
        else:
            inputs = {
                "image": f"data:image/png;base64,{image_base64}",
                "prompt": "enhance quality, improve lighting, sharpen details",
                "guidance_scale": 7.5,
                "num_inference_steps": 50
            }
        
        result = await self.run_model(settings.flux_model, inputs)
        
        # Get the output image URL and download it
        output_url = result["output"]
        if isinstance(output_url, list):
            output_url = output_url[0]
        
        async with httpx.AsyncClient() as client:
            response = await client.get(output_url)
            response.raise_for_status()
            return response.content
    
