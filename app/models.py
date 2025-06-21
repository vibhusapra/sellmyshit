from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()


class Listing(Base):
    __tablename__ = "listings"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Item identification
    item_name = Column(String(255), nullable=False)
    category = Column(String(100))
    brand = Column(String(100))
    model = Column(String(100))
    
    # Images
    original_image_path = Column(String(500))
    enhanced_image_path = Column(String(500))
    
    # Analysis results
    condition = Column(String(50))
    key_features = Column(JSON)  # Store as JSON array
    color = Column(String(50))
    size = Column(String(50))
    material = Column(String(100))
    
    # Pricing
    suggested_price = Column(Float)
    min_price = Column(Float)
    max_price = Column(Float)
    avg_price = Column(Float)
    
    # Generated content
    listing_title = Column(String(255))
    listing_description = Column(Text)
    keywords = Column(Text)  # Comma-separated
    
    # Metadata
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Additional analysis data
    analysis_data = Column(JSON)  # Store complete analysis results
    price_research_data = Column(JSON)  # Store price research details


class PriceResearch(Base):
    __tablename__ = "price_research"
    
    id = Column(Integer, primary_key=True, index=True)
    listing_id = Column(Integer, index=True)
    
    source = Column(String(50))  # ebay, craigslist, etc.
    item_title = Column(String(500))
    price = Column(Float)
    condition = Column(String(50))
    url = Column(String(1000))
    
    created_at = Column(DateTime, default=func.now())