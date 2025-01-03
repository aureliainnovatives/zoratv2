ai-engine/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI entry point
│   ├── config/                 # Configuration files for different environments
│   │   ├── __init__.py
│   │   ├── settings.py         # Dynamically loads settings based on environment
│   │   ├── development.py      # Development-specific settings
│   │   ├── production.py       # Production-specific settings
│   │   ├── staging.py          # Staging-specific settings
│   │   ├── details.txt         # Description of the config folder
│   ├── dependencies.py         # Dependency injection (DB, ES, Redis connections)
│   ├── models/                 # MongoDB models
│   │   ├── __init__.py
│   │   ├── agents.py           # Agent registry schema
│   │   ├── documents.py        # Document storage schema
│   │   ├── details.txt         # Description of the models folder
│   ├── services/               # Core business logic and RAG operations
│   │   ├── __init__.py
│   │   ├── search.py           # ElasticSearch + Haystack operations
│   │   ├── rag.py              # Retrieval-Augmented Generation pipelines
│   │   ├── memory.py           # Memory management and Redis integration
│   │   ├── details.txt         # Description of the services folder
│   ├── routes/                 # API routes for exposing endpoints
│   │   ├── __init__.py
│   │   ├── search.py           # Endpoints for RAG search
│   │   ├── agents.py           # Endpoints for agent workflows
│   │   ├── details.txt         # Description of the routes folder
│   ├── ai_components/          # AI-related components
│   │   ├── __init__.py
│   │   ├── llm_providers/      # LLM wrappers for LangChain/LangGraph compatibility
│   │   │   ├── __init__.py
│   │   │   ├── openai.py       # OpenAI wrapper
│   │   │   ├── llama.py        # Llama2 wrapper
│   │   │   ├── details.txt     # Description of the llm_providers folder
│   │   ├── capabilities/       # Vertical agents and tools
│   │   │   ├── __init__.py
│   │   │   ├── calculator.py   # Calculator capability
│   │   │   ├── web_search.py   # Web search capability
│   │   │   ├── details.txt     # Description of the capabilities folder
│   │   ├── details.txt         # Description of the ai_components folder
│   ├── utils/                  # Utility functions and helpers
│   │   ├── __init__.py
│   │   ├── elastic.py          # ElasticSearch connection helpers
│   │   ├── mongo.py            # MongoDB connection helpers
│   │   ├── redis.py            # Redis connection helpers
│   │   ├── env_loader.py       # Loads .env files based on environment
│   │   ├── details.txt         # Description of the utils folder
├── Dockerfile                  # Docker configuration
├── requirements.txt            # Python dependencies
├── README.md                   # Project documentation
├── .env                        # Default environment variables
├── .env.development            # Development environment variables
├── .env.production             # Production environment variables
├── .env.staging                # Staging environment variables