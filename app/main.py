from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Optional
import os

from app.database import init_db, get_db
from app.models import Listing
from services.image_enhancer import ImageEnhancer
from services.item_analyzer import ItemAnalyzer
from services.price_researcher import PriceResearcher
from services.listing_generator import ListingGenerator

# Initialize FastAPI app
app = FastAPI(
    title="Sell My Shit API",
    description="AI-powered item listing generator",
    version="1.0.0"
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


@app.get("/")
async def root():
    return {
        "message": "Sell My Shit API",
        "endpoints": {
            "POST /process-item": "Process an item image and generate listing",
            "GET /listing/{listing_id}": "Get listing details",
            "GET /listings": "Get all listings",
            "GET /image/{image_path}": "Get enhanced image"
        }
    }


@app.post("/process-item")
async def process_item(
    file: UploadFile = File(...),
    enhancement_type: str = "background_removal",
    db: Session = Depends(get_db)
):
    """Process an item image and generate a complete listing."""
    
    # Validate file
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    try:
        # Read image data
        image_data = await file.read()
        
        # Step 1: Enhance image
        enhanced_data, enhanced_path = await enhancer.enhance_image(image_data, enhancement_type)
        
        # Step 2: Analyze item
        image_path = enhancer.get_image_path(enhanced_path)
        item_analysis = await analyzer.analyze_item(image_path)
        
        # Step 3: Research prices
        search_queries = await analyzer.get_search_queries(
            item_analysis["item_name"],
            item_analysis.get("brand")
        )
        price_data = await researcher.research_prices(search_queries)
        
        # Step 4: Get market insights
        market_insights = await researcher.get_market_insights(
            item_analysis["item_name"],
            item_analysis["category"]
        )
        
        # Step 5: Generate listing
        listing_content = await generator.generate_listing(
            item_analysis, price_data, market_insights
        )
        
        # Save to database
        db_listing = Listing(
            item_name=item_analysis["item_name"],
            category=item_analysis["category"],
            brand=item_analysis.get("brand"),
            model=item_analysis.get("model"),
            original_image_path=file.filename,
            enhanced_image_path=enhanced_path,
            condition=item_analysis["condition"],
            key_features=item_analysis["key_features"],
            color=item_analysis.get("color"),
            size=item_analysis.get("size"),
            material=item_analysis.get("material"),
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
        
        return {
            "listing_id": db_listing.id,
            "item_analysis": item_analysis,
            "price_data": price_data,
            "market_insights": market_insights,
            "listing": listing_content,
            "enhanced_image_url": f"/image/{os.path.basename(enhanced_path)}"
        }
        
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
        "condition": listing.condition,
        "suggested_price": listing.suggested_price,
        "title": listing.listing_title,
        "description": listing.listing_description,
        "keywords": listing.keywords.split(",") if listing.keywords else [],
        "created_at": listing.created_at,
        "enhanced_image_url": f"/image/{os.path.basename(listing.enhanced_image_path)}"
    }


@app.get("/listings")
async def get_listings(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get all listings with pagination."""
    listings = db.query(Listing).offset(skip).limit(limit).all()
    total = db.query(Listing).count()
    
    return {
        "total": total,
        "listings": [
            {
                "id": l.id,
                "item_name": l.item_name,
                "category": l.category,
                "suggested_price": l.suggested_price,
                "created_at": l.created_at
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)