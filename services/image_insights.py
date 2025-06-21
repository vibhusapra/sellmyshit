from typing import Dict, List, Any, Optional
from services.openai_client import OpenAIClient
from services.price_researcher import PriceResearcher
from app.config import settings
import json


class ImageInsightsService:
    """Analyzes market trends to recommend optimal product images."""
    
    def __init__(self):
        self.openai_client = OpenAIClient()
        self.price_researcher = PriceResearcher()
    
    async def analyze_successful_listings(self, item_name: str, category: str, 
                                        brand: Optional[str] = None) -> Dict[str, Any]:
        """Research what types of images work best for this item category."""
        
        # First, get market context
        search_query = f"{brand} {item_name}" if brand else item_name
        market_data = await self.price_researcher.research_prices([search_query])
        
        # Use GPT-4.1 to analyze what images would be most effective
        prompt = f"""You are a product photography expert analyzing what images sell best on online marketplaces.

Item: {item_name}
Category: {category}
Brand: {brand or 'Unknown'}
Market Price Range: {market_data.get('price_range', 'Unknown')}

Based on successful listings in this category, recommend specific product images that would maximize sales. Consider:
1. What angles and views buyers need to see
2. What lifestyle/context shots work best
3. What details need close-up shots
4. What comparison or scale images help
5. What staging or backgrounds work best

Provide a detailed JSON response with this structure:
{{
    "recommended_shots": [
        {{
            "type": "angle/lifestyle/detail/comparison",
            "description": "specific description of the shot",
            "prompt_elements": ["key", "visual", "elements"],
            "priority": "high/medium/low"
        }}
    ],
    "styling_recommendations": {{
        "backgrounds": ["white", "lifestyle setting", etc],
        "lighting": "natural/studio/dramatic",
        "props": ["items to include in shots"],
        "mood": "professional/casual/luxury"
    }},
    "category_insights": "specific tips for this product category"
}}

Return ONLY the JSON object."""
        
        response = await self.openai_client.client.responses.create(
            model=settings.openai_model,
            input=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": prompt
                        }
                    ]
                }
            ]
        )
        
        try:
            # Extract content from response
            if hasattr(response, 'content'):
                result_text = response.content
            elif hasattr(response, 'choices') and response.choices:
                result_text = response.choices[0].message.content
            else:
                result_text = str(response)
            start_idx = result_text.find("{")
            end_idx = result_text.rfind("}") + 1
            if start_idx != -1 and end_idx > start_idx:
                json_str = result_text[start_idx:end_idx]
                return json.loads(json_str)
        except:
            pass
        
        # Fallback recommendations
        return self._get_default_recommendations(category)
    
    def _get_default_recommendations(self, category: str) -> Dict[str, Any]:
        """Provide category-based default recommendations."""
        
        category_lower = category.lower()
        
        if "electronic" in category_lower or "tech" in category_lower:
            return {
                "recommended_shots": [
                    {
                        "type": "angle",
                        "description": "Front view showing screen/display",
                        "prompt_elements": ["front facing", "all buttons visible", "clean background"],
                        "priority": "high"
                    },
                    {
                        "type": "angle",
                        "description": "Back view showing ports and connections",
                        "prompt_elements": ["rear view", "all ports visible", "cable compatibility"],
                        "priority": "high"
                    },
                    {
                        "type": "detail",
                        "description": "Close-up of model number and specifications",
                        "prompt_elements": ["macro shot", "serial number", "specifications label"],
                        "priority": "medium"
                    },
                    {
                        "type": "lifestyle",
                        "description": "Device in use on modern desk setup",
                        "prompt_elements": ["workspace", "in use", "modern setting"],
                        "priority": "medium"
                    },
                    {
                        "type": "comparison",
                        "description": "Size comparison with common objects",
                        "prompt_elements": ["next to smartphone", "ruler", "hand for scale"],
                        "priority": "low"
                    }
                ],
                "styling_recommendations": {
                    "backgrounds": ["pure white", "dark gradient", "tech workspace"],
                    "lighting": "studio",
                    "props": ["cables", "accessories", "original box"],
                    "mood": "professional"
                },
                "category_insights": "Electronics sell best with clear technical details and all included accessories visible"
            }
        
        elif "furniture" in category_lower or "home" in category_lower:
            return {
                "recommended_shots": [
                    {
                        "type": "angle",
                        "description": "3/4 view showing full item",
                        "prompt_elements": ["three quarter angle", "full view", "neutral background"],
                        "priority": "high"
                    },
                    {
                        "type": "lifestyle",
                        "description": "Item in beautifully staged room",
                        "prompt_elements": ["living room", "staged", "natural lighting"],
                        "priority": "high"
                    },
                    {
                        "type": "detail",
                        "description": "Close-up of materials and craftsmanship",
                        "prompt_elements": ["texture detail", "material quality", "construction"],
                        "priority": "medium"
                    },
                    {
                        "type": "angle",
                        "description": "Multiple angles showing all sides",
                        "prompt_elements": ["360 degree views", "all angles", "consistent lighting"],
                        "priority": "medium"
                    },
                    {
                        "type": "comparison",
                        "description": "Scale reference with person or room",
                        "prompt_elements": ["human for scale", "room context", "dimensions"],
                        "priority": "high"
                    }
                ],
                "styling_recommendations": {
                    "backgrounds": ["scandinavian interior", "white studio", "home setting"],
                    "lighting": "natural",
                    "props": ["plants", "books", "decor items"],
                    "mood": "casual"
                },
                "category_insights": "Furniture sells best when shown in context with warm, inviting staging"
            }
        
        else:  # General items
            return {
                "recommended_shots": [
                    {
                        "type": "angle",
                        "description": "Clear front view on white background",
                        "prompt_elements": ["centered", "white background", "professional"],
                        "priority": "high"
                    },
                    {
                        "type": "angle",
                        "description": "Multiple angles showing all sides",
                        "prompt_elements": ["multi angle", "360 view", "consistent lighting"],
                        "priority": "high"
                    },
                    {
                        "type": "detail",
                        "description": "Close-ups of important features",
                        "prompt_elements": ["detail shots", "key features", "quality indicators"],
                        "priority": "medium"
                    },
                    {
                        "type": "lifestyle",
                        "description": "Item in use or context",
                        "prompt_elements": ["in use", "lifestyle", "real world"],
                        "priority": "medium"
                    }
                ],
                "styling_recommendations": {
                    "backgrounds": ["pure white", "gradient", "contextual"],
                    "lighting": "studio",
                    "props": ["minimal", "relevant accessories"],
                    "mood": "professional"
                },
                "category_insights": "Focus on clear, honest representation with multiple angles"
            }
    
    def generate_flux_prompts(self, original_description: str, 
                            recommendations: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate specific FLUX.1 prompts based on insights."""
        
        prompts = []
        styling = recommendations.get("styling_recommendations", {})
        
        for shot in recommendations.get("recommended_shots", []):
            if shot["priority"] in ["high", "medium"]:
                # Build comprehensive prompt
                elements = shot.get("prompt_elements", [])
                
                prompt = f"Professional product photography of {original_description}, "
                prompt += f"{shot['description']}, "
                prompt += ", ".join(elements) + ", "
                
                # Add styling elements
                if shot["type"] == "lifestyle":
                    prompt += f"{styling.get('mood', 'professional')} mood, "
                    prompt += f"{styling.get('lighting', 'studio')} lighting, "
                    if styling.get('props'):
                        prompt += f"with {', '.join(styling['props'][:2])}, "
                else:
                    prompt += f"{styling.get('backgrounds', ['white'])[0]} background, "
                    prompt += f"{styling.get('lighting', 'studio')} lighting, "
                
                prompt += "4K quality, ultra detailed, professional product photography"
                
                prompts.append({
                    "type": shot["type"],
                    "description": shot["description"],
                    "prompt": prompt,
                    "priority": shot["priority"]
                })
        
        return prompts