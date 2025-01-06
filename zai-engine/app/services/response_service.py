"""Response formatting and answer generation service."""
from typing import Dict, List, Optional
from enum import Enum
import markdown
from dataclasses import dataclass

class ResponseStyle(Enum):
    """Enumeration of response styles."""
    CONCISE = "concise"      # Brief, to-the-point answers
    DETAILED = "detailed"    # Comprehensive answers with explanations
    TECHNICAL = "technical"  # Technical answers with references
    SIMPLE = "simple"        # Simple, non-technical explanations

@dataclass
class SourceAttribution:
    """Source attribution for answers."""
    content: str
    score: float
    document_id: str
    chunk_id: str
    section: Optional[str] = None
    page: Optional[int] = None

@dataclass
class FormattedResponse:
    """Structured response with formatting and sources."""
    answer: str
    formatted_answer: str  # HTML/Markdown formatted
    sources: List[SourceAttribution]
    style: ResponseStyle
    context_window: Dict
    metadata: Dict

class ResponseService:
    """Service for handling response formatting and generation."""

    def __init__(self):
        """Initialize response service."""
        self.prompt_templates = {
            ResponseStyle.CONCISE: """Provide a brief, direct answer to the question using the given context.
            Focus on key points only.

            Context:
            {% for document in documents %}
            [{{document.meta.section}}] {{document.content}}
            {% endfor %}

            Question: {{query}}

            Answer: """,

            ResponseStyle.DETAILED: """Provide a comprehensive answer with explanations using the given context.
            Include relevant details and examples if available.

            Context:
            {% for document in documents %}
            [{{document.meta.section}}] {{document.content}}
            {% endfor %}

            Question: {{query}}

            Detailed Answer: """,

            ResponseStyle.TECHNICAL: """Provide a technical answer with proper terminology and references.
            Include specific technical details and cite sources.

            Context:
            {% for document in documents %}
            [{{document.meta.section}}] {{document.content}}
            Source: {{document.meta.document_id}}, Section: {{document.meta.section}}
            {% endfor %}

            Question: {{query}}

            Technical Answer: """,

            ResponseStyle.SIMPLE: """Provide a simple, easy-to-understand answer avoiding technical terms.
            Explain concepts in plain language.

            Context:
            {% for document in documents %}
            [{{document.meta.section}}] {{document.content}}
            {% endfor %}

            Question: {{query}}

            Simple Answer: """
        }

    def _determine_style(self, query: str, context: Dict) -> ResponseStyle:
        """Determine appropriate response style based on query and context."""
        query_lower = query.lower()
        
        # Check for explicit style requests
        if any(term in query_lower for term in ["explain in detail", "elaborate", "comprehensive"]):
            return ResponseStyle.DETAILED
        if any(term in query_lower for term in ["briefly", "quick", "short"]):
            return ResponseStyle.CONCISE
        if any(term in query_lower for term in ["technical", "specification", "implementation"]):
            return ResponseStyle.TECHNICAL
        if any(term in query_lower for term in ["simple", "basic", "explain like"]):
            return ResponseStyle.SIMPLE
            
        # Default to context-based decision
        if context.get("is_technical", False):
            return ResponseStyle.TECHNICAL
        return ResponseStyle.DETAILED

    def _format_sources(self, documents: List[Dict]) -> List[SourceAttribution]:
        """Format source attributions from documents."""
        sources = []
        for doc in documents:
            source = SourceAttribution(
                content=doc["content"][:200] + "...",  # Preview
                score=doc["score"],
                document_id=doc["meta"].get("document_id", ""),
                chunk_id=doc["meta"].get("chunk_id", ""),
                section=doc["meta"].get("section", ""),
                page=doc["meta"].get("page_number")
            )
            sources.append(source)
        return sources

    def _format_answer_markdown(self, answer: str, sources: List[SourceAttribution]) -> str:
        """Format answer in Markdown with citations."""
        md_parts = [answer, "\n\n### Sources"]
        
        for idx, source in enumerate(sources, 1):
            md_parts.append(f"\n{idx}. **{source.section or 'Section'}** (Score: {source.score:.2f})")
            md_parts.append(f"\n   > {source.content}")
        
        return "\n".join(md_parts)

    def format_response(self, 
                       answer: str,
                       documents: List[Dict],
                       query: str,
                       context: Dict) -> FormattedResponse:
        """Format the response with appropriate styling and citations."""
        # Determine response style
        style = self._determine_style(query, context)
        
        # Process sources
        sources = self._format_sources(documents)
        
        # Format answer with markdown
        formatted_answer = self._format_answer_markdown(answer, sources)
        
        # Create context window metadata
        context_window = {
            "total_chunks": len(documents),
            "window_size": sum(len(doc["content"].split()) for doc in documents),
            "avg_chunk_score": sum(doc["score"] for doc in documents) / len(documents)
        }
        
        # Compile metadata
        metadata = {
            "response_style": style.value,
            "source_count": len(sources),
            "context_window": context_window,
            **context
        }
        
        return FormattedResponse(
            answer=answer,
            formatted_answer=formatted_answer,
            sources=sources,
            style=style,
            context_window=context_window,
            metadata=metadata
        )

    def get_prompt_template(self, style: ResponseStyle) -> str:
        """Get the appropriate prompt template for the response style."""
        return self.prompt_templates.get(style, self.prompt_templates[ResponseStyle.DETAILED]) 