import asyncio
import httpx
import json

async def test_process_item():
    """Test the process-item endpoint with a real image."""
    
    # Read the test image
    with open("uploads/test_coffee_grinder.jpg", "rb") as f:
        image_data = f.read()
    
    # Create form data
    files = {
        "file": ("test_coffee_grinder.jpg", image_data, "image/jpeg")
    }
    data = {
        "enhancement_mode": "smart"
    }
    
    # Make request
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "http://localhost:8000/process-item",
                files=files,
                data=data,
                timeout=30.0
            )
            
            if response.status_code == 200:
                print("✅ Success!")
                print(json.dumps(response.json(), indent=2))
            else:
                print(f"❌ Error {response.status_code}")
                print(response.text)
                
        except Exception as e:
            print(f"❌ Request failed: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_process_item())