from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Form
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
import os
import json
import asyncio
from datetime import datetime

from app.database import init_db, get_db
from app.models import Listing
from services.image_enhancer import ImageEnhancer
from services.item_analyzer import ItemAnalyzer
from services.price_researcher import PriceResearcher
from services.listing_generator import ListingGenerator
from services.smart_image_generator import SmartImageGenerator
from services.image_insights import ImageInsightsService

# Initialize FastAPI app
app = FastAPI(
    title="Sell My Shit API",
    description="AI-powered item listing generator",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
init_db()

# Initialize services
enhancer = ImageEnhancer()
analyzer = ItemAnalyzer()
researcher = PriceResearcher()
generator = ListingGenerator()
smart_generator = SmartImageGenerator()
insights_service = ImageInsightsService()


@app.get("/")
async def root():
    return {
        "message": "Sell My Shit API",
        "endpoints": {
            "POST /process-item": "Process an item image and generate listing",
            "POST /generate-images": "Generate multiple enhanced images",
            "GET /listing/{listing_id}": "Get listing details",
            "GET /listings": "Get all listings",
            "GET /image/{image_path}": "Get enhanced image",
            "GET /market-insights/{item_name}/{category}": "Get market insights"
        }
    }


@app.post("/process-item")
async def process_item(
    file: UploadFile = File(...),
    enhancement_mode: str = Form("quick"),
    custom_prompts: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """Process an item image and generate a complete listing."""
    
    # Validate file
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    try:
        # Parse custom prompts if provided
        prompts_list = None
        if custom_prompts:
            prompts_list = json.loads(custom_prompts)
        
        # Read image data
        image_data = await file.read()
        
        # Step 1: Initial analysis
        # Save temp image for analysis
        temp_path = f"uploads/{file.filename}"
        os.makedirs("uploads", exist_ok=True)
        with open(temp_path, "wb") as f:
            f.write(image_data)
        
        item_analysis = await analyzer.analyze_item(temp_path)
        
        # Step 2: Generate enhanced images based on mode
        enhanced_images = []
        image_insights = None
        
        if enhancement_mode == "smart":
            # Generate smart images with marketing portfolio
            portfolio = await smart_generator.generate_listing_portfolio(
                image_data,
                item_analysis,
                enhancement_mode="smart"
            )
            enhanced_images = portfolio["generated_images"]
            
        elif enhancement_mode == "custom" and prompts_list:
            # Generate custom images
            portfolio = await smart_generator.generate_custom_images(
                image_data,
                prompts_list
            )
            enhanced_images = portfolio["generated_images"]
            
        else:  # quick mode
            # Just do background removal
            enhanced_data, enhanced_path = await enhancer.enhance_image(
                image_data, 
                "background_removal"
            )
            enhanced_images = [{
                "type": "background_removal",
                "description": "Clean white background",
                "path": enhanced_path,
                "url": f"/image/{os.path.basename(enhanced_path)}"
            }]
        
        # Step 3: Use estimated price from OpenAI
        price_data = {
            "sources": [],
            "items_found": 1,
            "avg_price": float(item_analysis.get("estimated_price", 0)),
            "min_price": float(item_analysis.get("estimated_price", 0)),
            "max_price": float(item_analysis.get("estimated_price", 0)),
            "median_price": float(item_analysis.get("estimated_price", 0)),
            "price_range": f"${item_analysis.get('estimated_price', 0)}",
            "ai_estimated": True
        }
        
        # Step 4: Get market insights
        market_insights = await researcher.get_market_insights(
            item_analysis["item_name"],
            item_analysis["category"]
        )
        
        # Step 5: Generate listing content for all platforms
        listing_content = await generator.generate_listing(
            item_analysis, price_data, market_insights
        )
        
        # Generate platform-specific versions
        platforms = ["ebay", "craigslist", "facebook"]
        platform_listings = {}
        
        for platform in platforms:
            platform_listing = await generator.generate_platform_listing(
                item_analysis, price_data, market_insights, platform
            )
            platform_listings[platform] = platform_listing
        
        # Save to database
        db_listing = Listing(
            item_name=item_analysis["item_name"],
            category=item_analysis["category"],
            brand=item_analysis.get("brand"),
            model=None,  # Not extracted anymore
            original_image_path=file.filename,
            enhanced_image_path=enhanced_images[0]["path"] if enhanced_images else "",
            condition=item_analysis["condition"],
            key_features=item_analysis["key_features"],
            color=None,  # Not extracted anymore
            size=None,  # Not extracted anymore
            material=None,  # Not extracted anymore
            suggested_price=listing_content["suggested_price"],
            min_price=price_data.get("min_price"),
            max_price=price_data.get("max_price"),
            avg_price=price_data.get("avg_price"),
            listing_title=listing_content["title"],
            listing_description=listing_content["description"],
            keywords=",".join(listing_content["keywords"]),
            analysis_data=item_analysis,
            price_research_data=price_data
        )
        db.add(db_listing)
        db.commit()
        db.refresh(db_listing)
        
        # Clean up temp file
        os.remove(temp_path)
        
        return {
            "listing_id": db_listing.id,
            "item_analysis": {
                **item_analysis,
                "potential_issues": item_analysis.get("potential_issues", [])
            },
            "price_data": {
                **price_data,
                "demand_level": market_insights.get("demand_level", "medium"),
                "best_time_to_sell": market_insights.get("best_time_to_sell", "Anytime"),
                "items_found": price_data.get("items_found", 0)
            },
            "market_insights": market_insights,
            "image_insights": image_insights,
            "listing": listing_content,
            "platform_listings": platform_listings,
            "enhanced_images": enhanced_images,
            "enhancement_mode": enhancement_mode
        }
        
    except Exception as e:
        import traceback
        error_detail = {
            "error": str(e),
            "type": type(e).__name__,
            "traceback": traceback.format_exc()
        }
        print(f"[ERROR] in process_item: {error_detail}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/generate-images")
async def generate_images(
    file: UploadFile = File(...),
    mode: str = Form("smart"),
    custom_prompts: Optional[str] = Form(None),
    item_analysis: Optional[str] = Form(None)
):
    """Generate enhanced images for a listing."""
    
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    try:
        # Parse inputs
        prompts_list = json.loads(custom_prompts) if custom_prompts else None
        analysis_data = json.loads(item_analysis) if item_analysis else None
        
        # Read image data
        image_data = await file.read()
        
        # Generate images based on mode
        if mode == "custom" and prompts_list:
            portfolio = await smart_generator.generate_custom_images(
                image_data,
                prompts_list
            )
        else:
            # Need item analysis for smart mode
            if not analysis_data:
                # Analyze the item first
                temp_path = f"uploads/temp_{file.filename}"
                os.makedirs("uploads", exist_ok=True)
                with open(temp_path, "wb") as f:
                    f.write(image_data)
                
                analysis_data = await analyzer.analyze_item(temp_path)
                os.remove(temp_path)
            
            portfolio = await smart_generator.generate_listing_portfolio(
                image_data,
                analysis_data,
                enhancement_mode=mode
            )
        
        return portfolio
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/market-insights/{item_name}/{category}")
async def get_market_insights(item_name: str, category: str):
    """Get market insights for an item."""
    try:
        insights = await researcher.get_market_insights(item_name, category)
        return insights
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/listing/{listing_id}")
async def get_listing(listing_id: int, db: Session = Depends(get_db)):
    """Get listing details by ID."""
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    
    return {
        "id": listing.id,
        "item_name": listing.item_name,
        "category": listing.category,
        "brand": listing.brand,
        "model": listing.model,
        "condition": listing.condition,
        "color": listing.color,
        "size": listing.size,
        "material": listing.material,
        "suggested_price": listing.suggested_price,
        "min_price": listing.min_price,
        "max_price": listing.max_price,
        "avg_price": listing.avg_price,
        "title": listing.listing_title,
        "description": listing.listing_description,
        "keywords": listing.keywords.split(",") if listing.keywords else [],
        "key_features": listing.key_features,
        "created_at": listing.created_at,
        "enhanced_image_url": f"/image/{os.path.basename(listing.enhanced_image_path)}" if listing.enhanced_image_path else None,
        "analysis_data": listing.analysis_data,
        "price_research_data": listing.price_research_data
    }


@app.get("/listings")
async def get_listings(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get all listings with pagination."""
    listings = db.query(Listing).order_by(Listing.created_at.desc()).offset(skip).limit(limit).all()
    total = db.query(Listing).count()
    
    return {
        "total": total,
        "listings": [
            {
                "id": l.id,
                "item_name": l.item_name,
                "category": l.category,
                "suggested_price": l.suggested_price,
                "created_at": l.created_at,
                "enhanced_image_url": f"/image/{os.path.basename(l.enhanced_image_path)}"
            }
            for l in listings
        ]
    }


@app.get("/image/{filename}")
async def get_image(filename: str):
    """Serve enhanced images."""
    filepath = os.path.join("enhanced", filename)
    
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Image not found")
    
    return FileResponse(filepath)


@app.post("/generate-variations")
async def generate_variations(
    file: UploadFile = File(...)
):
    """Generate 5 different variations of an uploaded image using FLUX.1 Kontext."""
    
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    try:
        # Read image data
        image_data = await file.read()
        
        # Generate variations
        result = await smart_generator.generate_variations(image_data)
        
        return {
            "success": True,
            "total_requested": result["total_requested"],
            "total_generated": result["total_generated"],
            "variations": [
                {
                    "type": v["type"],
                    "prompt": v["prompt"],
                    "url": v["url"],
                    "error": v["error"]
                }
                for v in result["variations"]
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/download-listing/{listing_id}")
async def download_listing(listing_id: int, db: Session = Depends(get_db)):
    """Download listing data as JSON."""
    listing = db.query(Listing).filter(Listing.id == listing_id).first()
    
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    
    listing_data = {
        "item_name": listing.item_name,
        "category": listing.category,
        "brand": listing.brand,
        "model": listing.model,
        "condition": listing.condition,
        "color": listing.color,
        "size": listing.size,
        "material": listing.material,
        "suggested_price": listing.suggested_price,
        "price_range": {
            "min": listing.min_price,
            "max": listing.max_price,
            "average": listing.avg_price
        },
        "title": listing.listing_title,
        "description": listing.listing_description,
        "keywords": listing.keywords.split(",") if listing.keywords else [],
        "key_features": listing.key_features,
        "created_at": listing.created_at.isoformat(),
        "analysis_data": listing.analysis_data,
        "price_research_data": listing.price_research_data
    }
    
    return JSONResponse(
        content=listing_data,
        headers={
            "Content-Disposition": f"attachment; filename=listing_{listing_id}.json"
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)