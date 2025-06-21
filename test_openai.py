import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.openai_client import OpenAIClient

async def test_image_analysis():
    client = OpenAIClient()
    
    # Test with the demo coffee image
    image_path = "demo_images/coffee.jpeg"
    
    print("Testing OpenAI image analysis...")
    print(f"Image path: {image_path}")
    
    try:
        result = await client.analyze_image(image_path)
        print("\nSuccess! Analysis result:")
        print(result)
    except Exception as e:
        print(f"\nError occurred: {type(e).__name__}: {str(e)}")
        print("\nFull error details:")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_image_analysis())