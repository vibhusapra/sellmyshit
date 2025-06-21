from typing import List, Dict, Any, Tuple
import asyncio
import httpx
from PIL import Image
from io import BytesIO
import os
import uuid
from services.bfl_client import BFLClient
from services.image_insights import ImageInsightsService
from services.openai_client import OpenAIClient
from services.item_analyzer import ItemAnalyzer
from app.config import settings


class SmartImageGenerator:
    """Generates multiple optimized product images based on market insights."""
    
    def __init__(self):
        self.bfl_client = BFLClient()
        self.insights_service = ImageInsightsService()
        self.openai_client = OpenAIClient()
        self.analyzer = ItemAnalyzer()
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
                "url": f"/image/{os.path.basename(path)}"
            })
        
        elif enhancement_mode == "smart":
            # Full AI-driven portfolio generation
            
            # First, generate a clean background image
            update_progress("Generating clean product image...")
            try:
                clean_image, clean_path = await self._quick_enhance(original_image)
                result["generated_images"].append({
                    "type": "background_removal",
                    "description": "Clean white background",
                    "path": clean_path,
                    "url": f"/image/{os.path.basename(clean_path)}"
                })
            except Exception as e:
                result["errors"].append(f"Clean image generation failed: {str(e)}")
            
            # Then generate marketing images
            update_progress("Creating viral marketing images...")
            try:
                marketing_result = await self.generate_marketing_portfolio(
                    original_image,
                    item_analysis
                )
                
                # Add marketing images to results
                for img in marketing_result["generated_images"]:
                    result["generated_images"].append(img)
                
                # Add any errors
                result["errors"].extend(marketing_result.get("errors", []))
                
                # Add marketing insights
                result["marketing_prompts_generated"] = marketing_result["total_generated"]
                
            except Exception as e:
                result["errors"].append(f"Marketing image generation failed: {str(e)}")
        
        return result
    
    async def _quick_enhance(self, image_data: bytes) -> Tuple[bytes, str]:
        """Quick enhancement with just background removal."""
        prompt = "Product on clean white background, professional lighting, centered composition"
        
        enhanced_data = await self.bfl_client.generate_image_edit(
            image_data, 
            prompt=prompt
        )
        
        filename = f"enhanced_{uuid.uuid4()}.png"
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
                "priority": prompt_data["priority"]
            }
            
        except Exception as e:
            raise Exception(f"Failed to generate {prompt_data['type']} image: {str(e)}")
    
    def _encode_image(self, image_data: bytes) -> str:
        """Encode image to base64."""
        import base64
        return base64.b64encode(image_data).decode('utf-8')
    
    async def _generate_single_variation_prompt(self, 
                                              item_analysis: Dict[str, Any],
                                              base64_image: str,
                                              index: int) -> Dict[str, str]:
        """Generate a single meme variation prompt using OpenAI."""
        
        scenarios = [
            {
                "location": "Mount Everest summit",
                "context": "extreme adventure",
                "elements": ["blizzard conditions", "achievement flag", "oxygen mask nearby"]
            },
            {
                "location": "Times Square NYC at midnight", 
                "context": "urban chaos",
                "elements": ["giant billboard featuring the product", "yellow cabs", "neon lights everywhere"]
            },
            {
                "location": "International Space Station",
                "context": "zero gravity vibes",
                "elements": ["floating dramatically", "Earth visible through window", "astronaut giving thumbs up"]
            }
        ]
        
        scenario = scenarios[index % len(scenarios)]
        
        prompt = f"""Generate an ultra-specific FLUX.1 Kontext prompt for placing a {item_analysis['item_name']} in {scenario['location']}.

CRITICAL KONTEXT RULES:
- Be RUTHLESSLY specific about exact positions, colors, lighting
- Use "while keeping the original {item_analysis['item_name']} exactly as is, including all details, textures, and proportions"
- Specify exact camera angle and composition
- Name specific visual elements, not vague descriptions

Product: {item_analysis['item_name']}
Category: {item_analysis['category']}
Scenario: {scenario['context']} at {scenario['location']}

Create a prompt that:
1. Places the EXACT product (unchanged) in this wild scenario
2. Adds {', '.join(scenario['elements'])}
3. Makes it meme-worthy and shareable
4. Preserves product identity while changing ONLY the environment

Return JSON:
{{
    "title": "Catchy meme title (5-7 words)",
    "prompt": "Full FLUX Kontext prompt with preservation clauses",
    "context": "{scenario['context']}"
}}

Make it ABSURDLY specific and viral-worthy!"""

        response = self.openai_client.client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            temperature=1.3,
            max_tokens=300
        )
        
        try:
            result_text = response.choices[0].message.content
            # Extract JSON
            start_idx = result_text.find("{")
            end_idx = result_text.rfind("}") + 1
            if start_idx != -1 and end_idx > start_idx:
                import json
                return json.loads(result_text[start_idx:end_idx])
        except Exception as e:
            print(f"[DEBUG] Error parsing variation prompt: {str(e)}")
        
        # Fallback prompt
        return {
            "title": f"{item_analysis['item_name']} Goes {scenario['context'].title()}",
            "prompt": f"Place the exact {item_analysis['item_name']} unchanged at {scenario['location']}, {', '.join(scenario['elements'])}, dramatic lighting, while keeping the original product details, textures, shape, and proportions exactly as they are, ultra detailed 8k",
            "context": scenario['context']
        }
    
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
                    "url": None,
                    "error": str(e)
                })
        
        return results
    
    async def generate_variations(self, image_data: bytes) -> Dict[str, Any]:
        """Generate 3 meme-worthy product variations using FLUX.1 Kontext."""
        
        print("[DEBUG] Starting meme variation generation")
        
        # First analyze the image to understand what we're working with
        temp_path = f"uploads/temp_variation_{uuid.uuid4()}.jpg"
        os.makedirs("uploads", exist_ok=True)
        with open(temp_path, "wb") as f:
            f.write(image_data)
        
        try:
            # Get basic item analysis
            item_analysis = await self.analyzer.analyze_item(temp_path)
            print(f"[DEBUG] Analyzed item: {item_analysis['item_name']}")
            
            # Convert image to base64 for OpenAI
            base64_image = self._encode_image(image_data)
            
            # Generate 3 meme prompts in parallel
            prompt_tasks = []
            for i in range(3):
                task = self._generate_single_variation_prompt(
                    item_analysis,
                    base64_image,
                    i
                )
                prompt_tasks.append(task)
            
            # Wait for all prompts
            meme_prompts = await asyncio.gather(*prompt_tasks)
            print(f"[DEBUG] Generated {len(meme_prompts)} meme prompts")
            for i, mp in enumerate(meme_prompts):
                print(f"[DEBUG] Prompt {i+1}: Title='{mp.get('title', 'N/A')}', Context='{mp.get('context', 'N/A')}'")
            
            # Extract just the prompts for image generation
            variation_prompts = [p["prompt"] for p in meme_prompts]
            
            # Generate all variations in parallel
            variations = await self.bfl_client.generate_multiple_variations(
                image_data,
                variation_prompts,
                self.enhanced_dir
            )
            
            # Add meme context to variations
            for i, variation in enumerate(variations):
                if i < len(meme_prompts) and not variation.get("error"):
                    variation["meme_title"] = meme_prompts[i]["title"]
                    variation["meme_context"] = meme_prompts[i]["context"]
                    print(f"[DEBUG] Added meme data to variation {i+1}: {variation['meme_title']}")
            
            return {
                "total_requested": len(variation_prompts),
                "total_generated": len([v for v in variations if v.get("error") is None]),
                "variations": variations
            }
            
        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    async def generate_marketing_portfolio(self, 
                                         original_image: bytes,
                                         item_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate 5 ultra-memey marketing images for peak AI slop aesthetic."""
        
        print("[DEBUG] Starting marketing portfolio generation")
        
        # Convert image to base64 for OpenAI
        base64_image = self._encode_image(original_image)
        
        # Get meme prompts from OpenAI
        try:
            marketing_prompts = await self.openai_client.generate_marketing_prompts(
                item_analysis, 
                base64_image
            )
            print(f"[DEBUG] Generated {len(marketing_prompts)} marketing prompts")
        except Exception as e:
            print(f"[DEBUG] Error generating prompts: {str(e)}")
            # Use fallback prompts
            marketing_prompts = [
                {
                    "title": "Grindset Mindset",
                    "prompt": f"{item_analysis['item_name']} floating in space with explosions, dramatic lighting, 'SUCCESS' text in flames, 8k hyperrealistic",
                    "style": "motivational"
                },
                {
                    "title": "Apocalypse Mode", 
                    "prompt": f"Person using {item_analysis['item_name']} during zombie apocalypse, determined expression, sunrise through ruins, dramatic composition",
                    "style": "apocalyptic"
                },
                {
                    "title": "Quantum Dimension",
                    "prompt": f"{item_analysis['item_name']} creating portal to another dimension, swirling colors, impossible physics, cinematic lighting",
                    "style": "surreal"
                },
                {
                    "title": "Celebrity Chaos",
                    "prompt": f"Famous person dramatically using {item_analysis['item_name']}, paparazzi in background, luxury setting, chaos ensuing",
                    "style": "celebrity"
                },
                {
                    "title": "Epic Battle",
                    "prompt": f"{item_analysis['item_name']} in medieval battle scene, knights cheering, dragon in background, epic movie poster style",
                    "style": "cinematic"
                }
            ]
        
        # Generate all marketing images
        results = []
        errors = []
        
        # Process in batches of 2
        for i in range(0, len(marketing_prompts), 2):
            batch = marketing_prompts[i:i+2]
            batch_tasks = []
            
            for prompt_data in batch:
                # Create a structured prompt for the image generator
                full_prompt_data = {
                    "type": f"marketing_{prompt_data['style'].replace('/', '_').replace(' ', '_')}",
                    "description": prompt_data['title'],
                    "prompt": prompt_data['prompt'],
                    "priority": "high"
                }
                
                task = self._generate_single_image(
                    original_image,
                    full_prompt_data,
                    item_analysis
                )
                batch_tasks.append(task)
            
            # Execute batch
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            
            for j, result in enumerate(batch_results):
                if isinstance(result, Exception):
                    errors.append(str(result))
                    print(f"[DEBUG] Error generating marketing image: {str(result)}")
                else:
                    # Add the meme title to the result
                    result['meme_title'] = batch[j]['title']
                    results.append(result)
            
            # Delay between batches
            if i + 2 < len(marketing_prompts):
                await asyncio.sleep(2)
        
        return {
            "mode": "marketing",
            "total_requested": len(marketing_prompts),
            "total_generated": len(results),
            "generated_images": results,
            "errors": errors
        }