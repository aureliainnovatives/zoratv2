# Zorat AI Engine

## Project Structure
```
zoratv2/ai-engine/
├── app/
│   ├── ai/                    # AI-related modules
│   │   ├── llm/              # LLM implementations
│   │   │   ├── base.py       # Base LLM interface
│   │   │   ├── factory.py    # LLM factory
│   │   │   └── providers/    # LLM providers (OpenAI, etc.)
│   ├── core/                 # Core functionality
│   │   ├── config.py         # Configuration settings
│   │   └── database.py       # Database connection
│   ├── models/               # Pydantic models
│   ├── repositories/         # Database repositories
│   ├── routes/               # API routes
│   ├── schemas/             # Request/Response schemas
│   ├── services/            # Business logic
│   └── utils/               # Utility functions
├── tests/                   # Test files
├── .env                     # Environment variables
├── requirements.txt         # Project dependencies
└── README.md               # Project documentation
```

## Setup Instructions

1. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
- Copy `.env.example` to `.env`
- Update the values in `.env` with your configuration

4. Start MongoDB:
- Ensure MongoDB is running on your system
- Default URL: mongodb://localhost:27017

5. Run the application:
```bash
uvicorn app.main:app --reload --port 5001
```

6. Access the API documentation:
- Swagger UI: http://localhost:5001/api/docs
- ReDoc: http://localhost:5001/api/redoc

## Development

### Code Style
- Use Black for code formatting
- Use isort for import sorting
- Follow PEP 8 guidelines

### Testing
```bash
pytest
```

### API Endpoints

#### Agent Routes
- POST /api/v1/agent/chat
  - Chat with an AI model
  - Requires: user message and LLM name

## Environment Variables

- `DEBUG`: Enable debug mode (default: true)
- `MONGODB_URL`: MongoDB connection URL
- `MONGODB_DB_NAME`: Database name
- `JWT_SECRET_KEY`: Secret key for JWT
- `OPENAI_API_KEY`: OpenAI API key

## Features

- FastAPI-based REST API
- MongoDB integration with Motor
- OpenAI integration
- JWT authentication
- Environment-based configuration
- Comprehensive logging
- CORS support
- API documentation with Swagger/ReDoc 