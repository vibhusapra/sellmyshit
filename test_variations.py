import asyncio
import httpx
import json

async def test_variations():
    """Test the new meme variation generation."""
    
    # Use test image
    with open("uploads/test.png", "rb") as f:
        image_data = f.read()
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        files = {
            "file": ("test.png", image_data, "image/png")
        }
        
        print("Generating meme variations...")
        response = await client.post(
            "http://localhost:8000/generate-variations",
            files=files
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"\nSuccess! Generated {result['total_generated']} out of {result['total_requested']} variations")
            
            for i, variation in enumerate(result['variations']):
                print(f"\nVariation {i+1}:")
                print(f"  Type: {variation.get('type', 'N/A')}")
                print(f"  Meme Title: {variation.get('meme_title', 'N/A')}")
                print(f"  Context: {variation.get('meme_context', 'N/A')}")
                print(f"  URL: {variation.get('url', 'N/A')}")
                if variation.get('error'):
                    print(f"  Error: {variation['error']}")
        else:
            print(f"Error: {response.status_code}")
            print(response.text)

if __name__ == "__main__":
    asyncio.run(test_variations())