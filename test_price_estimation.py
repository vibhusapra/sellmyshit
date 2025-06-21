import asyncio
import httpx
import json

async def test_price_estimation():
    """Test the new AI price estimation in image analysis."""
    
    # Use a smaller test image
    with open("uploads/380e0573-f157-4b90-b4be-90f28a5d0797.png", "rb") as f:
        image_data = f.read()
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        files = {
            "file": ("test.png", image_data, "image/png")
        }
        data = {
            "enhancement_mode": "quick"
        }
        
        print("Testing AI price estimation...")
        response = await client.post(
            "http://localhost:8000/process-item",
            files=files,
            data=data
        )
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"\n✅ Success! Item processed")
            print(f"📝 Item: {result['item_analysis']['item_name']}")
            print(f"🏷️  Category: {result['item_analysis']['category']}")
            print(f"🏢 Brand: {result['item_analysis'].get('brand', 'N/A')}")
            print(f"📊 Condition: {result['item_analysis']['condition']}")
            print(f"💰 AI Estimated Price: ${result['item_analysis'].get('estimated_price', 'N/A')}")
            print(f"💵 Suggested Price: ${result['listing']['suggested_price']}")
            print(f"🤖 AI Estimated: {result['price_data'].get('ai_estimated', False)}")
            
            print(f"\n🔍 Key Features:")
            for feature in result['item_analysis']['key_features']:
                print(f"  • {feature}")
            
            print(f"\n📈 Price Data:")
            print(f"  • Average: ${result['price_data']['avg_price']}")
            print(f"  • Range: {result['price_data']['price_range']}")
            print(f"  • AI Estimated: {result['price_data']['ai_estimated']}")
            
        else:
            print(f"❌ Error: {response.status_code}")
            print(response.text)

if __name__ == "__main__":
    asyncio.run(test_price_estimation())