from typing import Dict, Any, Optional
from services.openai_client import OpenAIClient
import re


class ListingGenerator:
    def __init__(self):
        self.client = OpenAIClient()
    
    async def generate_listing(self, 
                             item_data: Dict[str, Any], 
                             price_data: Dict[str, Any],
                             market_insights: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate complete listing with title, description, and keywords."""
        
        # Generate the listing content
        listing_text = await self.client.generate_listing(item_data, price_data)
        
        # Parse the generated text
        parsed = self._parse_listing_text(listing_text)
        
        # Add pricing recommendation
        parsed["suggested_price"] = self._calculate_suggested_price(price_data, market_insights)
        
        # Generate platform-specific versions
        parsed["platform_versions"] = {
            "ebay": self._format_for_ebay(parsed),
            "craigslist": self._format_for_craigslist(parsed),
            "facebook": self._format_for_facebook(parsed)
        }
        
        return parsed
    
    def _parse_listing_text(self, text: str) -> Dict[str, Any]:
        """Parse the generated listing text into components."""
        result = {
            "title": "",
            "description": "",
            "keywords": []
        }
        
        # Extract title
        title_match = re.search(r'TITLE:\s*(.+?)(?:\n|$)', text, re.IGNORECASE)
        if title_match:
            result["title"] = title_match.group(1).strip()
        
        # Extract description
        desc_match = re.search(r'DESCRIPTION:\s*(.+?)(?:KEYWORDS:|$)', text, re.IGNORECASE | re.DOTALL)
        if desc_match:
            result["description"] = desc_match.group(1).strip()
        
        # Extract keywords
        keywords_match = re.search(r'KEYWORDS:\s*(.+?)$', text, re.IGNORECASE)
        if keywords_match:
            keywords_text = keywords_match.group(1).strip()
            result["keywords"] = [k.strip() for k in keywords_text.split(',')]
        
        # Fallback if parsing fails
        if not result["title"] and not result["description"]:
            # Use the entire text as description
            result["description"] = text.strip()
            result["title"] = text.split('\n')[0][:80] if text else "Item for Sale"
        
        return result
    
    def _calculate_suggested_price(self, price_data: Dict[str, Any], 
                                 market_insights: Optional[Dict[str, Any]] = None) -> float:
        """Calculate suggested price based on research and insights."""
        if not price_data.get("avg_price"):
            return 0.0
        
        avg_price = price_data["avg_price"]
        
        # Adjust based on pricing strategy
        if market_insights and market_insights.get("pricing_strategy") == "slightly below market":
            suggested = avg_price * 0.95  # 5% below average
        elif market_insights and market_insights.get("pricing_strategy") == "premium":
            suggested = avg_price * 1.05  # 5% above average
        else:
            suggested = avg_price  # Competitive pricing
        
        # Round to nice number
        if suggested > 100:
            suggested = round(suggested / 5) * 5  # Round to nearest $5
        elif suggested > 20:
            suggested = round(suggested)  # Round to nearest dollar
        else:
            suggested = round(suggested, 2)  # Keep cents for low prices
        
        return suggested
    
    def _format_for_ebay(self, listing: Dict[str, Any]) -> Dict[str, Any]:
        """Format listing for eBay."""
        return {
            "title": listing["title"][:80],  # eBay title limit
            "description": f"""
<div style="font-family: Arial, sans-serif;">
{listing['description']}

<h3>Condition</h3>
<p>Please see photos for exact condition.</p>

<h3>Shipping</h3>
<p>Item will be carefully packaged and shipped within 1 business day.</p>

<h3>Returns</h3>
<p>30-day returns accepted.</p>
</div>
            """.strip(),
            "item_specifics": {
                "Condition": "Used",
                "Brand": "See Description"
            }
        }
    
    def _format_for_craigslist(self, listing: Dict[str, Any]) -> Dict[str, Any]:
        """Format listing for Craigslist."""
        return {
            "title": listing["title"],
            "description": f"""
{listing['description']}

Price: ${listing.get('suggested_price', 'Make offer')}
Condition: Used

Cash only, local pickup.
No trades please.

Keywords: {', '.join(listing['keywords'][:5])}
            """.strip()
        }
    
    def _format_for_facebook(self, listing: Dict[str, Any]) -> Dict[str, Any]:
        """Format listing for Facebook Marketplace."""
        return {
            "title": listing["title"][:100],  # Facebook limit
            "description": f"""
{listing['description']}

✅ Available for pickup
💵 Cash or Venmo accepted
📍 Local sales only

{' '.join(['#' + k.replace(' ', '') for k in listing['keywords'][:5]])}
            """.strip(),
            "category": "General"
        }
    
    async def generate_platform_listing(self, 
                                      item_data: Dict[str, Any], 
                                      price_data: Dict[str, Any],
                                      market_insights: Optional[Dict[str, Any]],
                                      platform: str) -> Dict[str, Any]:
        """Generate a platform-specific listing."""
        # First generate the base listing
        base_listing = await self.generate_listing(item_data, price_data, market_insights)
        
        # Return the platform-specific version
        if platform == "ebay":
            return self._format_for_ebay(base_listing)
        elif platform == "craigslist":
            return self._format_for_craigslist(base_listing)
        elif platform == "facebook":
            return self._format_for_facebook(base_listing)
        else:
            return base_listing