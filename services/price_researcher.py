import httpx
from bs4 import BeautifulSoup
from typing import Dict, List, Any, Optional
import asyncio
import re
from app.config import settings
import statistics


class PriceResearcher:
    def __init__(self):
        self.headers = {
            "User-Agent": settings.user_agent
        }
        self.timeout = settings.scrape_timeout
    
    async def research_prices(self, search_queries: List[str]) -> Dict[str, Any]:
        """Research prices across multiple sources."""
        all_prices = []
        price_data = {
            "sources": [],
            "items_found": 0,
            "avg_price": None,
            "min_price": None,
            "max_price": None,
            "median_price": None,
            "price_range": None
        }
        
        # Search across multiple queries
        for query in search_queries[:3]:  # Limit to first 3 queries
            results = await self._search_ebay(query)
            all_prices.extend([r["price"] for r in results if r["price"] > 0])
            price_data["sources"].extend(results)
        
        # Calculate statistics
        if all_prices:
            price_data["items_found"] = len(all_prices)
            price_data["avg_price"] = round(statistics.mean(all_prices), 2)
            price_data["min_price"] = round(min(all_prices), 2)
            price_data["max_price"] = round(max(all_prices), 2)
            price_data["median_price"] = round(statistics.median(all_prices), 2)
            price_data["price_range"] = f"${price_data['min_price']} - ${price_data['max_price']}"
        
        return price_data
    
    async def _search_ebay(self, query: str) -> List[Dict[str, Any]]:
        """Search eBay for price data (simplified scraping)."""
        results = []
        
        try:
            # Note: In production, you'd use eBay's API
            # This is a simplified example for demonstration
            search_url = f"https://www.ebay.com/sch/i.html?_nkw={query.replace(' ', '+')}&_sop=15"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    search_url,
                    headers=self.headers,
                    timeout=self.timeout,
                    follow_redirects=True
                )
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Parse eBay listings (simplified)
                    # In reality, you'd need more robust parsing
                    items = soup.find_all('div', class_='s-item__wrapper', limit=10)
                    
                    for item in items:
                        try:
                            title_elem = item.find('h3', class_='s-item__title')
                            price_elem = item.find('span', class_='s-item__price')
                            
                            if title_elem and price_elem:
                                title = title_elem.text.strip()
                                price_text = price_elem.text.strip()
                                
                                # Extract price
                                price = self._extract_price(price_text)
                                
                                if price > 0:
                                    results.append({
                                        "source": "ebay",
                                        "title": title,
                                        "price": price,
                                        "price_text": price_text,
                                        "condition": "Used",  # Would parse from listing
                                        "url": search_url
                                    })
                        except:
                            continue
        except Exception as e:
            print(f"Error searching eBay: {e}")
        
        return results
    
    def _extract_price(self, price_text: str) -> float:
        """Extract numeric price from text."""
        try:
            # Remove currency symbols and extract numbers
            price_text = re.sub(r'[^\d.,]', '', price_text)
            
            # Handle ranges (take the lower value)
            if 'to' in price_text.lower() or '-' in price_text:
                parts = re.split(r'to|-', price_text.lower())
                price_text = parts[0]
            
            # Convert to float
            price = float(price_text.replace(',', ''))
            return price
        except:
            return 0.0
    
    async def get_market_insights(self, item_name: str, category: str) -> Dict[str, Any]:
        """Get additional market insights for the item."""
        insights = {
            "demand_level": "Medium",  # Would calculate from real data
            "best_time_to_sell": "Weekends",
            "pricing_strategy": "competitive",
            "similar_items_selling_rate": "65%",
            "recommended_platforms": ["eBay", "Facebook Marketplace", "Craigslist"]
        }
        
        # Adjust based on category
        if category.lower() in ["electronics", "technology"]:
            insights["demand_level"] = "High"
            insights["pricing_strategy"] = "slightly below market"
            insights["recommended_platforms"].append("Mercari")
        elif category.lower() in ["furniture", "home"]:
            insights["best_time_to_sell"] = "Spring/Summer"
            insights["recommended_platforms"] = ["Facebook Marketplace", "Craigslist", "OfferUp"]
        
        return insights