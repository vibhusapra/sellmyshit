# Sell My Shit - AI-Powered Item Listing Generator

Upload a photo of any item you want to sell, and our AI will:
- Enhance the image with professional background removal
- Identify the item and extract key features
- Research current market prices
- Generate optimized listings for multiple platforms

## Features

- **Image Enhancement**: Uses FLUX.1 Kontext for professional product photography
- **Item Analysis**: Powered by vision models to identify items and extract details
- **Price Research**: Automated market research across multiple platforms
- **Listing Generation**: AI-generated descriptions optimized for each platform
- **Multi-Platform Support**: Formatted listings for eBay, Craigslist, and Facebook Marketplace

## Tech Stack

- **Backend**: FastAPI
- **Frontend**: Streamlit
- **AI Models**: 
  - OpenAI o1 for multimodal item analysis and text generation
  - Replicate FLUX.1 for image enhancement
- **Database**: SQLite with SQLAlchemy
- **Image Processing**: Pillow

## Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/sellmyshit.git
   cd sellmyshit
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys:
   # - OPENAI_API_KEY for o1 model access
   # - REPLICATE_API_TOKEN for FLUX.1 image enhancement
   ```

4. **Run the application**

   **Option 1: Streamlit UI**
   ```bash
   streamlit run streamlit_app.py
   ```

   **Option 2: FastAPI Backend**
   ```bash
   uvicorn app.main:app --reload
   ```

## Usage

### Streamlit Interface

1. Open http://localhost:8501
2. Upload an image of your item
3. Select enhancement type (background removal or quality enhancement)
4. Click "Generate Listing"
5. Review and copy the generated listings for your preferred platform

### API Endpoints

- `POST /process-item`: Upload an image and get a complete listing
- `GET /listing/{listing_id}`: Retrieve a specific listing
- `GET /listings`: Get all listings with pagination
- `GET /image/{filename}`: Access enhanced images

## Configuration

Edit `.env` file to configure:
- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `REPLICATE_API_TOKEN`: Your Replicate API key (required for image enhancement)
- Model versions for OpenAI and FLUX.1
- Upload limits and allowed formats
- Web scraping settings

## Project Structure

```
sellmyshit/
├── app/                 # FastAPI application
│   ├── main.py         # API endpoints
│   ├── models.py       # Database models
│   └── config.py       # Configuration
├── services/           # Core services
│   ├── openai_client.py       # OpenAI API integration
│   ├── replicate_client.py    # Replicate API for FLUX.1
│   ├── image_enhancer.py      # Image processing
│   ├── item_analyzer.py       # Item identification
│   ├── price_researcher.py    # Market research
│   └── listing_generator.py   # Content generation
├── streamlit_app.py    # Streamlit frontend
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## API Example

```python
import requests

# Upload image and generate listing
with open('coffee_grinder.jpg', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/process-item',
        files={'file': f},
        params={'enhancement_type': 'background_removal'}
    )

result = response.json()
print(f"Title: {result['listing']['title']}")
print(f"Suggested Price: ${result['listing']['suggested_price']}")
print(f"Description: {result['listing']['description']}")
```

## License

MIT License

## Contributing

Pull requests are welcome! Please feel free to submit issues or enhancement requests.