from typing import Dict, Any, Optional
from services.openai_client import OpenAIClient
import json


class ItemAnalyzer:
    def __init__(self):
        self.client = OpenAIClient()
    
    async def analyze_item(self, image_path: str) -> Dict[str, Any]:
        """Analyze item from image and extract detailed information."""
        # Use OpenAI client to analyze the image
        analysis = await self.client.analyze_image(image_path)
        
        # Ensure we have all required fields with defaults
        default_analysis = {
            "item_name": "Unknown Item",
            "category": "General",
            "brand": None,
            "model": None,
            "condition": "Unknown",
            "key_features": [],
            "color": None,
            "size": None,
            "material": None,
            "estimated_age": None,
            "notable_details": None
        }
        
        # Merge with defaults
        for key in default_analysis:
            if key not in analysis or analysis[key] is None:
                analysis[key] = default_analysis[key]
        
        # Clean up the analysis
        analysis = self._clean_analysis(analysis)
        
        return analysis
    
    def _clean_analysis(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and validate the analysis results."""
        # Ensure key_features is a list
        if isinstance(analysis.get("key_features"), str):
            analysis["key_features"] = [f.strip() for f in analysis["key_features"].split(",")]
        elif not isinstance(analysis.get("key_features"), list):
            analysis["key_features"] = []
        
        # Standardize condition
        condition_map = {
            "new": "New",
            "like new": "Like New",
            "excellent": "Like New",
            "very good": "Good",
            "good": "Good",
            "fair": "Fair",
            "poor": "Poor",
            "for parts": "Poor"
        }
        
        condition = analysis.get("condition", "").lower()
        analysis["condition"] = condition_map.get(condition, "Unknown")
        
        # Clean up strings
        for field in ["item_name", "category", "brand", "model", "color", "size", "material"]:
            if field in analysis and analysis[field]:
                analysis[field] = str(analysis[field]).strip()
        
        return analysis
    
    async def get_search_queries(self, item_name: str, brand: Optional[str] = None) -> list[str]:
        """Generate search queries for price research."""
        queries = await self.client.generate_search_queries(item_name, brand)
        
        # Add some fallback queries if needed
        if len(queries) < 3:
            base_query = f"{brand} {item_name}" if brand else item_name
            queries.extend([
                base_query,
                f"{base_query} used",
                f"{base_query} for sale"
            ])
        
        # Remove duplicates while preserving order
        seen = set()
        unique_queries = []
        for q in queries:
            if q.lower() not in seen:
                seen.add(q.lower())
                unique_queries.append(q)
        
        return unique_queries[:5]