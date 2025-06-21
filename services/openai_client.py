import openai
from openai import OpenAI
import base64
from typing import Dict, Any, Optional, List
import json
from app.config import settings


class OpenAIClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.openai_api_key
        self.client = OpenAI(api_key=self.api_key)
    
    def encode_image_to_base64(self, image_path: str) -> str:
        """Encode a local image to base64 string."""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    async def analyze_image(self, image_path: str) -> Dict[str, Any]:
        """Analyze image using o1 model to identify item and extract features."""
        
        print(f"[DEBUG] Starting image analysis for: {image_path}")
        
        # Encode image to base64
        base64_image = self.encode_image_to_base64(image_path)
        print(f"[DEBUG] Image encoded to base64, length: {len(base64_image)}")
        
        print(f"[DEBUG] Using model: {settings.openai_model}")
        
        prompt = """Analyze this image and provide a JSON response with the following structure:
        {
            "item_name": "specific name of the item",
            "category": "general category",
            "brand": "brand name if visible",
            "condition": "new/like new/good/fair/poor",
            "key_features": ["top 3-5 features"]
        }
        Be concise and accurate. Return ONLY the JSON object, no additional text."""
        
        try:
            response = self.client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1024,
                temperature=1
            )
        except Exception as e:
            print(f"[DEBUG] Error in analyze_image: {str(e)}")
            raise
        
        # Parse the response
        try:
            result_text = response.choices[0].message.content
            print(f"[DEBUG] Raw OpenAI response: {result_text}")
            
            # Try to extract JSON from the response
            start_idx = result_text.find("{")
            end_idx = result_text.rfind("}") + 1
            if start_idx != -1 and end_idx > start_idx:
                json_str = result_text[start_idx:end_idx]
                print(f"[DEBUG] Extracted JSON: {json_str}")
                parsed = json.loads(json_str)
                print(f"[DEBUG] Successfully parsed JSON with keys: {list(parsed.keys())}")
                return parsed
            else:
                print(f"[DEBUG] No JSON found in response")
        except Exception as e:
            print(f"[DEBUG] Error parsing response: {type(e).__name__}: {str(e)}")
        
        # Fallback
        return {
            "item_name": "Unknown Item",
            "category": "General",
            "brand": "Unknown",
            "condition": "unknown",
            "key_features": []
        }
    
    async def generate_listing(self, item_data: Dict[str, Any], price_data: Dict[str, Any]) -> str:
        """Generate optimized listing description using GPT-4."""
        
        prompt = f"""Create a compelling product listing description for online marketplaces.

Item Details:
{json.dumps(item_data, indent=2)}

Price Research:
Average Price: ${price_data.get('avg_price', 'N/A')}
Price Range: ${price_data.get('min_price', 'N/A')} - ${price_data.get('max_price', 'N/A')}

Create a listing that includes:
1. Attention-grabbing title (max 80 characters)
2. Detailed description highlighting key features and benefits
3. Condition details
4. Why someone should buy this item
5. SEO-optimized keywords naturally integrated

Format the response as:
TITLE: [title here]

DESCRIPTION:
[full description here]

KEYWORDS: [comma-separated keywords]"""
        
        response = self.client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert at creating compelling product listings that sell. You understand SEO and marketplace best practices."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=1024,
            temperature=1
        )
        
        return response.choices[0].message.content
    
    async def generate_search_queries(self, item_name: str, brand: Optional[str] = None) -> List[str]:
        """Generate search queries for price research."""
        
        prompt = f"""Generate 5 search queries to find pricing information for this item:
Item: {item_name}
Brand: {brand if brand else 'Unknown'}

Create specific search queries that would help find this exact item or very similar items on marketplace websites like eBay, Facebook Marketplace, or Craigslist.
Return only the queries, one per line, no numbering or bullets."""
        
        response = self.client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=256,
            temperature=1
        )
        
        # Split into queries and clean
        output = response.choices[0].message.content
        queries = [q.strip() for q in output.split('\n') if q.strip()]
        return queries[:5]  # Return top 5 queries
    
    async def enhance_listing_with_insights(self, listing: str, market_insights: Dict[str, Any]) -> str:
        """Enhance the listing with market insights."""
        
        prompt = f"""Enhance this listing with the following market insights:

Current Listing:
{listing}

Market Insights:
- Demand Level: {market_insights.get('demand_level')}
- Best Time to Sell: {market_insights.get('best_time_to_sell')}
- Recommended Platforms: {', '.join(market_insights.get('recommended_platforms', []))}

Add a brief section at the end of the description mentioning why now is a good time to buy based on the market insights.
Keep the same format (TITLE, DESCRIPTION, KEYWORDS) but enhance the description."""
        
        response = self.client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=1024,
            temperature=1
        )
        
        return response.choices[0].message.content