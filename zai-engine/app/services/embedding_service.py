from typing import List, Optional
from haystack.components.embedders import OpenAITextEmbedder
from haystack.utils import Secret
from config import config

class EmbeddingService:
    """Service for managing different embedding models."""
    
    def __init__(self):
        """Initialize embedding service."""
        self.embedder = None
        self.current_provider = None
        
    async def initialize(self, provider: str = "openai"):
        """Initialize embedder with specified provider."""
        if provider == self.current_provider and self.embedder:
            return
            
        if provider == "openai":
            self.embedder = OpenAITextEmbedder(
                api_key=Secret.from_token(config["openai"]["api_key"]),
                model="text-embedding-ada-002"
            )
        else:
            raise ValueError(f"Unsupported embedding provider: {provider}")
            
        self.current_provider = provider
    
    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings for a list of texts."""
        if not self.embedder:
            await self.initialize()
        
        # Process each text individually since OpenAITextEmbedder only accepts single strings
        embeddings = []
        for text in texts:
            result = self.embedder.run(text=text)
            embeddings.append(result["embedding"])
        return embeddings
    
    async def get_embedding(self, text: str) -> List[float]:
        """Get embedding for a single text."""
        if not self.embedder:
            await self.initialize()
            
        result = self.embedder.run(text=text)
        return result["embedding"]
    
    @property
    def embedding_dim(self) -> int:
        """Get the embedding dimension for the current provider."""
        if self.current_provider == "openai":
            return 1536  # OpenAI ada-002 dimension
        raise ValueError(f"Unknown embedding dimension for provider: {self.current_provider}") 