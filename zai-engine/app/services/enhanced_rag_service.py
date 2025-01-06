"""Enhanced RAG service with hybrid search capabilities using Haystack 2.x."""
from typing import Dict, List, Optional
from haystack import Pipeline, Document
from haystack.components.embedders import OpenAITextEmbedder
from haystack_integrations.components.retrievers.elasticsearch import (
    ElasticsearchBM25Retriever,
    ElasticsearchEmbeddingRetriever
)
from haystack.components.generators import OpenAIGenerator
from haystack.components.builders import PromptBuilder
from haystack.components.joiners import DocumentJoiner
from haystack.components.rankers import TransformersSimilarityRanker
from haystack.utils import Secret
from haystack_integrations.document_stores.elasticsearch import ElasticsearchDocumentStore
import asyncio
from dataclasses import dataclass
from typing import Dict, List, Optional

from app.services.llm_service import LLMService
from app.core.database import db
from config import config
from app.services.query_service import QueryService, QueryIntent
from app.services.response_service import ResponseService, ResponseStyle

class WeightValidationError(Exception):
    """Exception raised for invalid weight configurations."""
    pass

@dataclass
class SearchWeights:
    """Weights configuration for hybrid search."""
    semantic_weight: float = 0.5
    keyword_weight: float = 0.3
    rerank_weight: float = 0.2

    def __post_init__(self):
        """Validate weights after initialization."""
        self.validate()
    
    def validate(self):
        """Validate weight configuration."""
        # Check individual weights are between 0 and 1
        for weight_name, weight_value in self.__dict__.items():
            if not isinstance(weight_value, (int, float)):
                raise WeightValidationError(
                    f"{weight_name} must be a number, got {type(weight_value)}"
                )
            if not 0 <= weight_value <= 1:
                raise WeightValidationError(
                    f"{weight_name} must be between 0 and 1, got {weight_value}"
                )
        
        # Check weights sum to 1 (allowing for small floating-point errors)
        total = sum(self.__dict__.values())
        if not 0.99 <= total <= 1.01:
            raise WeightValidationError(
                f"Weights must sum to 1.0, got {total:.2f}"
            )

class EnhancedRAGService:
    """Enhanced RAG service using Haystack 2.x pipeline architecture."""
    
    def __init__(self):
        """Initialize enhanced RAG service."""
        self.llm_service = LLMService()
        self.document_store = None
        self.pipeline = None
        self.current_llm_id = None
        self.query_service = QueryService()
        self.response_service = ResponseService()
        try:
            self.current_weights = SearchWeights()
        except WeightValidationError as e:
            raise RuntimeError(f"Invalid default weights: {str(e)}")
        
        self.prompt_template = """Answer the question based on the given context. If you cannot find 
        the answer in the context, say "I cannot answer this question based on the provided context." 
        Do not make up any information.

        Context (ranked by relevance):
        {% for document in documents %}
        [Score: {{document.score}}] {{document.content}}
        {% endfor %}

        Question: {{ query }}

        Answer: """

    async def initialize(self, llm_id: str):
        """Initialize Haystack 2.x pipeline with multiple retrievers."""
        # Get LLM provider
        provider = await self.llm_service.get_provider(llm_id)
        if not provider:
            raise ValueError(f"Failed to initialize LLM provider: {llm_id}")
        
        # Initialize document store
        self.document_store = ElasticsearchDocumentStore(
            hosts=[config["elasticsearch"]["connection"]["url"]],
            basic_auth=(
                config["elasticsearch"]["connection"]["user"],
                config["elasticsearch"]["connection"]["password"]
            ),
            index=f"{config['elasticsearch']['index']['prefix']}_chunks"
        )
        
        # Initialize pipeline components
        embedder = OpenAITextEmbedder(
            api_key=Secret.from_token(config["openai"]["api_key"]),
            model_name="text-embedding-ada-002"
        )
        
        # Initialize retrievers with enhanced metadata fields
        semantic_retriever = ElasticsearchEmbeddingRetriever(
            document_store=self.document_store,
            top_k=5,
            embedding_field="embedding",
            metadata_fields=[
                "section_type",
                "section_level",
                "content_classification",
                "quality.coherence_score",
                "quality.completeness_score"
            ]
        )
        
        keyword_retriever = ElasticsearchBM25Retriever(
            document_store=self.document_store,
            top_k=5,
            fields={
                # Primary content fields
                "content": 1.0,
                "content.english": 0.8,
                
                # Important structural metadata
                "metadata.section_type": 1.2,
                "metadata.section_level": 1.1,
                "metadata.content_classification": 1.1,
                
                # Quality-based boosting
                "quality.coherence_score": 0.8,
                "quality.completeness_score": 0.8
            }
        )
        
        # Initialize re-ranker
        reranker = TransformersSimilarityRanker(
            model_name_or_path="cross-encoder/ms-marco-MiniLM-L-6-v2",
            top_k=5
        )
        
        # Initialize document joiner with validated weights
        joiner = DocumentJoiner(
            join_mode="reciprocal_rank_fusion",
            weights={
                "semantic": self.current_weights.semantic_weight,
                "keyword": self.current_weights.keyword_weight
            }
        )
        
        # Initialize prompt builder and generator
        prompt_builder = PromptBuilder(template=self.prompt_template)
        generator = OpenAIGenerator(
            api_key=Secret.from_token(provider.api_key),
            model=provider.model_name,
            generation_kwargs={
                "max_tokens": provider.max_tokens,
                "temperature": provider.temperature
            }
        )
        
        # Create pipeline
        self.pipeline = Pipeline()
        
        # Add components
        self.pipeline.add_component("embedder", embedder)
        self.pipeline.add_component("semantic_retriever", semantic_retriever)
        self.pipeline.add_component("keyword_retriever", keyword_retriever)
        self.pipeline.add_component("joiner", joiner)
        self.pipeline.add_component("reranker", reranker)
        self.pipeline.add_component("prompt_builder", prompt_builder)
        self.pipeline.add_component("generator", generator)
        
        # Connect components
        self.pipeline.connect("embedder.embedding", "semantic_retriever.query_embedding")
        self.pipeline.connect("semantic_retriever.documents", "joiner.documents_1")
        self.pipeline.connect("keyword_retriever.documents", "joiner.documents_2")
        self.pipeline.connect("joiner.documents", "reranker.documents")
        self.pipeline.connect("reranker.documents", "prompt_builder.documents")
        self.pipeline.connect("prompt_builder", "generator")
        
        self.current_llm_id = llm_id

    def update_weights(self, weights: Dict[str, float]):
        """Update search weights with validation."""
        try:
            # Create and validate new weights
            new_weights = SearchWeights(
                semantic_weight=weights.get("semantic", self.current_weights.semantic_weight),
                keyword_weight=weights.get("keyword", self.current_weights.keyword_weight),
                rerank_weight=weights.get("rerank", self.current_weights.rerank_weight)
            )
            
            if self.pipeline:
                # Update joiner weights
                joiner = self.pipeline.get_component("joiner")
                joiner.weights = {
                    "semantic": new_weights.semantic_weight,
                    "keyword": new_weights.keyword_weight
                }
                
                # Update reranker weight
                reranker = self.pipeline.get_component("reranker")
                reranker.weight = new_weights.rerank_weight
                
                self.current_weights = new_weights
                
        except WeightValidationError as e:
            raise ValueError(f"Invalid weight configuration: {str(e)}")

    def _optimize_context_window(self, documents: List[Document], query: str) -> List[Document]:
        """Optimize context window for better answer generation."""
        # Sort by score
        ranked_docs = sorted(documents, key=lambda x: x.score, reverse=True)
        
        # Calculate optimal window size
        total_tokens = sum(len(doc.content.split()) for doc in ranked_docs)
        if total_tokens <= 2000:  # If within token limit, use all
            return ranked_docs
        
        # Smart selection based on relevance and coverage
        selected_docs = []
        selected_content = set()
        token_count = 0
        
        for doc in ranked_docs:
            # Skip if too similar to already selected content
            doc_content = set(doc.content.lower().split())
            overlap = len(doc_content.intersection(selected_content)) / len(doc_content)
            
            if overlap < 0.7:  # Add if content is sufficiently different
                selected_docs.append(doc)
                selected_content.update(doc_content)
                token_count += len(doc.content.split())
                
                if token_count >= 2000:  # Stop if token limit reached
                    break
        
        return selected_docs

    async def query(self, query: str, **kwargs) -> Dict:
        """Execute RAG query using Haystack 2.x pipeline."""
        if not self.pipeline:
            raise RuntimeError("Pipeline not initialized. Call initialize() first.")
        
        try:
            # Get parameters
            top_k = kwargs.get("top_k", 5)
            
            # Enhance query
            enhanced_query = await self.query_service.enhance_query(query)
            
            # Adjust weights based on query intent and complexity
            if enhanced_query.context.intent in [QueryIntent.TECHNICAL, QueryIntent.ANALYTICAL]:
                weights = {
                    "semantic": 0.6,
                    "keyword": 0.2,
                    "rerank": 0.2
                }
            elif enhanced_query.context.intent == QueryIntent.FACTUAL:
                weights = {
                    "semantic": 0.3,
                    "keyword": 0.5,
                    "rerank": 0.2
                }
            else:
                weights = kwargs.get("weights", {
                    "semantic": 0.4,
                    "keyword": 0.4,
                    "rerank": 0.2
                })
            
            self.update_weights(weights)
            
            # Update retrievers' top_k
            self.pipeline.get_component("semantic_retriever").top_k = top_k
            self.pipeline.get_component("keyword_retriever").top_k = top_k
            self.pipeline.get_component("reranker").top_k = top_k
            
            # Process sub-queries if they exist
            if enhanced_query.sub_queries:
                all_results = []
                for sub_query in enhanced_query.sub_queries:
                    result = self.pipeline.run({
                        "embedder": {"text": sub_query},
                        "keyword_retriever": {"query": sub_query},
                        "prompt_builder": {"query": sub_query}
                    })
                    all_results.extend(result["reranker"]["documents"])
                
                # Deduplicate and sort results
                seen = set()
                unique_results = []
                for doc in sorted(all_results, key=lambda x: x.score, reverse=True):
                    if doc.content not in seen:
                        seen.add(doc.content)
                        unique_results.append(doc)
                results = unique_results[:top_k]
            else:
                # Run pipeline with enhanced query
                result = self.pipeline.run({
                    "embedder": {"text": enhanced_query.expanded},
                    "keyword_retriever": {"query": enhanced_query.expanded},
                    "prompt_builder": {"query": query}  # Use original query for answer generation
                })
                results = result["reranker"]["documents"]
            
            # Optimize context window
            optimized_results = self._optimize_context_window(results, query)
            
            # Get appropriate response style and prompt template
            response_style = self.response_service._determine_style(
                query, 
                {"is_technical": enhanced_query.context.is_technical}
            )
            prompt_template = self.response_service.get_prompt_template(response_style)
            
            # Update prompt template for answer generation
            self.pipeline.get_component("prompt_builder").template = prompt_template
            
            # Generate answer with optimized context
            final_result = self.pipeline.run({
                "prompt_builder": {
                    "query": query,
                    "documents": optimized_results
                }
            })
            
            # Format response
            formatted_response = self.response_service.format_response(
                answer=final_result["generator"]["replies"][0],
                documents=[{
                    "content": doc.content,
                    "score": doc.score,
                    "meta": doc.meta
                } for doc in optimized_results],
                query=query,
                context={
                    "is_technical": enhanced_query.context.is_technical,
                    "intent": enhanced_query.context.intent.value,
                    "complexity": enhanced_query.context.complexity
                }
            )
            
            # Prepare final response
            return {
                "answer": formatted_response.answer,
                "formatted_answer": formatted_response.formatted_answer,
                "sources": [
                    {
                        "content": source.content,
                        "score": source.score,
                        "document_id": source.document_id,
                        "section": source.section,
                        "page": source.page
                    }
                    for source in formatted_response.sources
                ],
                "metadata": {
                    "response_style": formatted_response.style.value,
                    "context_window": formatted_response.context_window,
                    "query": {
                        "original": query,
                        "enhanced": enhanced_query.expanded,
                        "intent": enhanced_query.context.intent.value,
                        "complexity": enhanced_query.context.complexity,
                        "is_technical": enhanced_query.context.is_technical,
                        "sub_queries": enhanced_query.sub_queries
                    },
                    "weights": {
                        "semantic": self.current_weights.semantic_weight,
                        "keyword": self.current_weights.keyword_weight,
                        "rerank": self.current_weights.rerank_weight
                    }
                },
                "llm_id": self.current_llm_id
            }
            
        except Exception as e:
            raise RuntimeError(f"Enhanced RAG pipeline error: {str(e)}")

    def update_prompt_template(self, template: str):
        """Update the prompt template used by the RAG pipeline."""
        if self.pipeline:
            prompt_builder = self.pipeline.get_component("prompt_builder")
            prompt_builder.template = template
        self.prompt_template = template

    async def close(self):
        """Close connections."""
        if self.document_store:
            await self.document_store.close() 