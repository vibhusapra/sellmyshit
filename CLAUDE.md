# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Backend Development
```bash
# Install dependencies (uses uv)
./run.sh

# Run FastAPI backend
uvicorn app.main:app --reload

# Run the full application (React + Backend)
./run_app.sh

# Test API setup and connections
python test_setup.py

# Format code
black .

# Lint code
flake8
```

### Frontend Development (React)
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start

# Build for production
npm build

# Run tests
npm test
```

### Database Operations
```bash
# Initialize database (automatically done by run.sh)
python -c "from app.database import init_db; init_db()"

# Database is SQLite, located at sellmyshit.db
```

## Architecture

### Core Services Architecture
The application follows a service-oriented architecture with specialized AI components:

1. **Image Enhancement Pipeline**
   - `services/image_enhancer.py`: Basic image processing and storage
   - `services/smart_image_generator.py`: AI-driven multi-image generation using FLUX.1
   - Uses Replicate API for FLUX.1 model integration

2. **Analysis Pipeline**
   - `services/item_analyzer.py`: GPT-4.1 vision model for item identification
   - `services/price_researcher.py`: Market research and price analysis
   - `services/listing_generator.py`: AI-powered listing content generation

3. **API Layer**
   - FastAPI backend (`app/main.py`) with async endpoints
   - RESTful API design with comprehensive error handling
   - CORS enabled for frontend integration

4. **Frontend**
   - **React** (`frontend/`): Modern web interface with TypeScript

### AI Model Integration
- **OpenAI GPT-4.1**: Multimodal analysis and text generation (`services/openai_client.py`)
- **FLUX.1 via Replicate**: Professional image enhancement (`services/replicate_client.py`)

### Data Flow
1. User uploads image → Saved to `uploads/`
2. Image analyzed by GPT-4.1 vision
3. Enhanced images generated via FLUX.1 → Saved to `enhanced/`
4. Market research performed
5. Listing generated with platform-specific versions
6. All data persisted to SQLite database

### Key Design Patterns
- Async/await throughout for non-blocking operations
- Service classes with single responsibilities
- Configuration centralized in `app/config.py` using pydantic-settings
- Environment-based configuration via `.env` file