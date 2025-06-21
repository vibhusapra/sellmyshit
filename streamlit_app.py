import streamlit as st
import asyncio
from PIL import Image
from io import BytesIO
import json
import pandas as pd
from datetime import datetime

# Import services
from services.image_enhancer import ImageEnhancer
from services.item_analyzer import ItemAnalyzer
from services.price_researcher import PriceResearcher
from services.listing_generator import ListingGenerator
from app.database import init_db, SessionLocal
from app.models import Listing

# Initialize database
init_db()

# Page config
st.set_page_config(
    page_title="Sell My Shit - AI Listing Generator",
    page_icon="🛍️",
    layout="wide"
)

# Initialize services
@st.cache_resource
def init_services():
    return {
        "enhancer": ImageEnhancer(),
        "analyzer": ItemAnalyzer(),
        "researcher": PriceResearcher(),
        "generator": ListingGenerator()
    }

services = init_services()

# Title and description
st.title("🛍️ Sell My Shit - AI-Powered Listing Generator")
st.markdown("Upload a photo of your item and let AI create the perfect listing!")

# Sidebar for settings
with st.sidebar:
    st.header("Settings")
    enhancement_type = st.selectbox(
        "Image Enhancement",
        ["background_removal", "quality_enhancement"],
        help="Choose how to enhance your product image"
    )
    
    st.header("Recent Listings")
    db = SessionLocal()
    recent_listings = db.query(Listing).order_by(Listing.created_at.desc()).limit(5).all()
    for listing in recent_listings:
        st.write(f"📦 {listing.item_name}")
        st.caption(f"${listing.suggested_price} - {listing.created_at.strftime('%Y-%m-%d')}")
    db.close()

# Main content
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📸 Upload Your Item")
    
    uploaded_file = st.file_uploader(
        "Choose an image...",
        type=["jpg", "jpeg", "png", "webp"],
        help="Upload a clear photo of your item"
    )
    
    if uploaded_file is not None:
        # Display original image
        image = Image.open(uploaded_file)
        st.image(image, caption="Original Image", use_column_width=True)
        
        # Process button
        if st.button("🚀 Generate Listing", type="primary"):
            with st.spinner("Processing your item..."):
                # Create placeholder for progress
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                async def process_item():
                    # Step 1: Enhance image
                    status_text.text("🎨 Enhancing image...")
                    progress_bar.progress(20)
                    
                    image_bytes = uploaded_file.getvalue()
                    enhanced_data, enhanced_path = await services["enhancer"].enhance_image(
                        image_bytes, enhancement_type
                    )
                    
                    # Step 2: Analyze item
                    status_text.text("🔍 Analyzing item...")
                    progress_bar.progress(40)
                    
                    image_path = services["enhancer"].get_image_path(enhanced_path)
                    item_analysis = await services["analyzer"].analyze_item(image_path)
                    
                    # Step 3: Research prices
                    status_text.text("💰 Researching market prices...")
                    progress_bar.progress(60)
                    
                    search_queries = await services["analyzer"].get_search_queries(
                        item_analysis["item_name"],
                        item_analysis.get("brand")
                    )
                    price_data = await services["researcher"].research_prices(search_queries)
                    
                    # Step 4: Get market insights
                    status_text.text("📊 Analyzing market trends...")
                    progress_bar.progress(80)
                    
                    market_insights = await services["researcher"].get_market_insights(
                        item_analysis["item_name"],
                        item_analysis["category"]
                    )
                    
                    # Step 5: Generate listing
                    status_text.text("✍️ Creating listing...")
                    progress_bar.progress(90)
                    
                    listing = await services["generator"].generate_listing(
                        item_analysis, price_data, market_insights
                    )
                    
                    # Save to database
                    db = SessionLocal()
                    db_listing = Listing(
                        item_name=item_analysis["item_name"],
                        category=item_analysis["category"],
                        brand=item_analysis.get("brand"),
                        model=item_analysis.get("model"),
                        original_image_path=uploaded_file.name,
                        enhanced_image_path=enhanced_path,
                        condition=item_analysis["condition"],
                        key_features=item_analysis["key_features"],
                        color=item_analysis.get("color"),
                        size=item_analysis.get("size"),
                        material=item_analysis.get("material"),
                        suggested_price=listing["suggested_price"],
                        min_price=price_data.get("min_price"),
                        max_price=price_data.get("max_price"),
                        avg_price=price_data.get("avg_price"),
                        listing_title=listing["title"],
                        listing_description=listing["description"],
                        keywords=",".join(listing["keywords"]),
                        analysis_data=item_analysis,
                        price_research_data=price_data
                    )
                    db.add(db_listing)
                    db.commit()
                    db.close()
                    
                    progress_bar.progress(100)
                    status_text.text("✅ Complete!")
                    
                    return {
                        "enhanced_image": enhanced_data,
                        "analysis": item_analysis,
                        "price_data": price_data,
                        "market_insights": market_insights,
                        "listing": listing
                    }
                
                # Run async function
                result = asyncio.run(process_item())
                
                # Store in session state
                st.session_state.result = result

# Display results
with col2:
    if "result" in st.session_state:
        st.header("📝 Your Listing")
        
        result = st.session_state.result
        
        # Enhanced image
        enhanced_image = Image.open(BytesIO(result["enhanced_image"]))
        st.image(enhanced_image, caption="Enhanced Product Image", use_column_width=True)
        
        # Item details
        with st.expander("📋 Item Analysis", expanded=True):
            analysis = result["analysis"]
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Item:** {analysis['item_name']}")
                st.write(f"**Category:** {analysis['category']}")
                st.write(f"**Brand:** {analysis.get('brand', 'N/A')}")
                st.write(f"**Condition:** {analysis['condition']}")
            with col2:
                st.write(f"**Color:** {analysis.get('color', 'N/A')}")
                st.write(f"**Size:** {analysis.get('size', 'N/A')}")
                st.write(f"**Material:** {analysis.get('material', 'N/A')}")
            
            if analysis.get("key_features"):
                st.write("**Key Features:**")
                for feature in analysis["key_features"]:
                    st.write(f"• {feature}")
        
        # Pricing
        with st.expander("💰 Pricing Analysis", expanded=True):
            price_data = result["price_data"]
            listing = result["listing"]
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Suggested Price", f"${listing['suggested_price']}")
            with col2:
                st.metric("Market Average", f"${price_data.get('avg_price', 'N/A')}")
            with col3:
                st.metric("Price Range", price_data.get('price_range', 'N/A'))
            
            # Market insights
            insights = result["market_insights"]
            st.write(f"**Demand Level:** {insights['demand_level']}")
            st.write(f"**Best Time to Sell:** {insights['best_time_to_sell']}")
            st.write(f"**Recommended Platforms:** {', '.join(insights['recommended_platforms'])}")
        
        # Generated listing
        st.subheader("📄 Generated Listing")
        
        # Platform tabs
        tab1, tab2, tab3 = st.tabs(["eBay", "Craigslist", "Facebook"])
        
        with tab1:
            ebay = listing["platform_versions"]["ebay"]
            st.text_input("Title", ebay["title"], key="ebay_title")
            st.text_area("Description", ebay["description"], height=200, key="ebay_desc")
            if st.button("📋 Copy eBay Listing", key="copy_ebay"):
                st.code(f"{ebay['title']}\n\n{ebay['description']}")
        
        with tab2:
            craigslist = listing["platform_versions"]["craigslist"]
            st.text_input("Title", craigslist["title"], key="cl_title")
            st.text_area("Description", craigslist["description"], height=200, key="cl_desc")
            if st.button("📋 Copy Craigslist Listing", key="copy_cl"):
                st.code(f"{craigslist['title']}\n\n{craigslist['description']}")
        
        with tab3:
            facebook = listing["platform_versions"]["facebook"]
            st.text_input("Title", facebook["title"], key="fb_title")
            st.text_area("Description", facebook["description"], height=200, key="fb_desc")
            if st.button("📋 Copy Facebook Listing", key="copy_fb"):
                st.code(f"{facebook['title']}\n\n{facebook['description']}")
        
        # Keywords
        st.write("**SEO Keywords:**")
        st.write(", ".join(listing["keywords"]))
        
        # Export options
        st.download_button(
            label="💾 Download Listing Data",
            data=json.dumps(result, indent=2, default=str),
            file_name=f"listing_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )

# Footer
st.markdown("---")
st.markdown("Built with ❤️ using Streamlit, FLUX.1, and Replicate")