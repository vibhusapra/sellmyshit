#!/usr/bin/env python3
"""Test script to verify API keys and basic functionality."""

import asyncio
from openai import OpenAI
from app.config import settings

def test_openai():
    """Test OpenAI connection."""
    print("Testing OpenAI connection...")
    try:
        client = OpenAI(api_key=settings.openai_api_key)
        
        # Test basic completion with new API
        response = client.responses.create(
            model=settings.openai_model,
            input=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": "Say 'Hello, OpenAI is working!'"
                        }
                    ]
                }
            ]
        )
        
        # Extract content based on response structure
        if hasattr(response, 'content'):
            content = response.content
        elif hasattr(response, 'choices') and response.choices:
            content = response.choices[0].message.content
        else:
            content = str(response)
        print("✅ OpenAI:", content)
        return True
    except Exception as e:
        print("❌ OpenAI Error:", str(e))
        return False

def test_replicate():
    """Test Replicate connection."""
    print("\nTesting Replicate connection...")
    try:
        import httpx
        headers = {
            "Authorization": f"Token {settings.replicate_api_token}",
            "Content-Type": "application/json"
        }
        
        # Test API access
        response = httpx.get(
            "https://api.replicate.com/v1/models",
            headers=headers,
            params={"limit": 1}
        )
        
        if response.status_code == 200:
            print("✅ Replicate: API connection successful")
            return True
        else:
            print(f"❌ Replicate Error: Status {response.status_code}")
            return False
    except Exception as e:
        print("❌ Replicate Error:", str(e))
        return False

def test_database():
    """Test database connection."""
    print("\nTesting database connection...")
    try:
        from app.database import SessionLocal, init_db
        from app.models import Listing
        
        init_db()
        db = SessionLocal()
        count = db.query(Listing).count()
        db.close()
        
        print(f"✅ Database: Connected successfully ({count} listings)")
        return True
    except Exception as e:
        print("❌ Database Error:", str(e))
        return False

if __name__ == "__main__":
    print("🔧 Testing Sell My Shit Setup\n")
    print("=" * 50)
    
    tests = [
        test_openai(),
        test_replicate(),
        test_database()
    ]
    
    print("\n" + "=" * 50)
    if all(tests):
        print("✅ All tests passed! Ready to run the app.")
    else:
        print("❌ Some tests failed. Please check your configuration.")