"""Query enhancement and optimization service."""
from typing import Dict, List, Optional, Tuple
from enum import Enum
import spacy
import nltk
from nltk.corpus import wordnet
from dataclasses import dataclass
import re
from haystack.components.preprocessors import DocumentCleaner, TextCleaner

# Load NLP models
try:
    nlp = spacy.load('en_core_web_sm')
except OSError:
    spacy.cli.download('en_core_web_sm')
    nlp = spacy.load('en_core_web_sm')

class QueryIntent(Enum):
    """Enumeration of query intent types."""
    FACTUAL = "factual"          # Who, what, when, where questions
    CONCEPTUAL = "conceptual"    # How, why questions
    COMPARATIVE = "comparative"  # Compare, contrast questions
    ANALYTICAL = "analytical"    # Analysis, evaluation questions
    TECHNICAL = "technical"      # Technical/domain-specific queries
    UNKNOWN = "unknown"          # Unclassified queries

@dataclass
class QueryContext:
    """Context and metadata for a query."""
    original_query: str
    intent: QueryIntent
    is_technical: bool = False
    requires_context: bool = False
    domain_terms: List[str] = None
    complexity: int = 1  # 1-5 scale

@dataclass
class EnhancedQuery:
    """Enhanced query with expansions and context."""
    original: str
    expanded: str
    context: QueryContext
    sub_queries: List[str] = None
    keywords: List[str] = None
    metadata: Dict = None

class QueryService:
    """Service for query enhancement and optimization."""

    def __init__(self):
        """Initialize query service."""
        self.text_cleaner = TextCleaner()
        self.technical_terms = set()  # Can be loaded from domain-specific vocabulary
        self.load_technical_terms()

    def load_technical_terms(self):
        """Load technical/domain-specific terms."""
        # TODO: Load from configuration or database
        self.technical_terms = {
            "rag", "retrieval", "augmented", "generation", "embedding",
            "vector", "semantic", "token", "nlp", "api", "query",
            "database", "index", "search", "relevance", "score"
        }

    def _expand_terms(self, term: str) -> List[str]:
        """Expand terms using WordNet synonyms."""
        synonyms = set()
        for syn in wordnet.synsets(term):
            for lemma in syn.lemmas():
                if lemma.name() != term and "_" not in lemma.name():
                    synonyms.add(lemma.name())
        return list(synonyms)[:3]  # Limit to top 3 synonyms

    def _is_technical_query(self, query: str, doc: spacy.tokens.Doc) -> bool:
        """Determine if query is technical in nature."""
        query_terms = set(token.text.lower() for token in doc)
        technical_overlap = query_terms.intersection(self.technical_terms)
        return len(technical_overlap) > 0

    def _get_query_complexity(self, doc: spacy.tokens.Doc) -> int:
        """Determine query complexity on a 1-5 scale."""
        # Factors affecting complexity:
        # 1. Number of technical terms
        # 2. Sentence structure
        # 3. Number of clauses
        # 4. Presence of complex relationships
        
        complexity = 1
        
        # Check for technical terms
        technical_terms = sum(1 for token in doc if token.text.lower() in self.technical_terms)
        complexity += min(2, technical_terms // 2)
        
        # Check sentence structure
        has_subordinate = any(token.dep_ in {'advcl', 'ccomp', 'xcomp'} for token in doc)
        if has_subordinate:
            complexity += 1
        
        # Check for multiple clauses
        clause_count = len([token for token in doc if token.dep_ == 'ROOT'])
        if clause_count > 1:
            complexity += 1
        
        return min(5, complexity)

    def classify_intent(self, query: str, doc: spacy.tokens.Doc) -> QueryIntent:
        """Classify the intent of the query."""
        query_lower = query.lower()
        
        # Check for question types
        if any(query_lower.startswith(w) for w in ['what', 'who', 'when', 'where', 'which']):
            return QueryIntent.FACTUAL
        
        if any(query_lower.startswith(w) for w in ['how', 'why', 'explain', 'describe']):
            return QueryIntent.CONCEPTUAL
        
        if any(w in query_lower for w in ['compare', 'difference', 'versus', 'vs']):
            return QueryIntent.COMPARATIVE
        
        if any(w in query_lower for w in ['analyze', 'evaluate', 'assess', 'examine']):
            return QueryIntent.ANALYTICAL
        
        if self._is_technical_query(query_lower, doc):
            return QueryIntent.TECHNICAL
        
        return QueryIntent.UNKNOWN

    def preprocess_query(self, query: str) -> str:
        """Preprocess the query for better matching."""
        # Use TextCleaner for basic cleaning
        cleaned = self.text_cleaner.run(texts=[query])["texts"][0]
        
        # Additional custom cleaning
        cleaned = re.sub(r'\s+', ' ', cleaned)
        
        # Normalize technical terms
        doc = nlp(cleaned)
        normalized = []
        for token in doc:
            if token.text.lower() in self.technical_terms:
                normalized.append(token.text.lower())
            else:
                normalized.append(token.text)
        
        return ' '.join(normalized)

    def expand_query(self, query: str, context: QueryContext) -> str:
        """Expand query with relevant terms and context."""
        doc = nlp(query)
        expanded_terms = []
        
        # Add original query terms
        expanded_terms.extend(token.text for token in doc if not token.is_stop)
        
        # Add synonyms for non-technical terms
        if not context.is_technical:
            for token in doc:
                if not token.is_stop and token.text.lower() not in self.technical_terms:
                    synonyms = self._expand_terms(token.text)
                    expanded_terms.extend(synonyms)
        
        # Add technical context if needed
        if context.is_technical:
            # Add related technical terms
            tech_terms = [term for term in self.technical_terms 
                         if any(term in expanded_term.lower() 
                               for expanded_term in expanded_terms)]
            expanded_terms.extend(tech_terms[:2])  # Add up to 2 related technical terms
        
        # Combine terms intelligently
        expanded_query = ' '.join(set(expanded_terms))
        return expanded_query

    def break_down_query(self, query: str, context: QueryContext) -> List[str]:
        """Break down complex queries into simpler sub-queries."""
        if context.complexity <= 2:
            return [query]
        
        doc = nlp(query)
        sub_queries = []
        
        # Split on conjunctions and relative clauses
        current_chunk = []
        for token in doc:
            current_chunk.append(token.text)
            
            # Break at meaningful boundaries
            if token.dep_ in {'cc', 'mark'} or token.pos_ == 'PUNCT':
                if len(current_chunk) > 2:  # Ensure meaningful chunks
                    sub_queries.append(' '.join(current_chunk))
                current_chunk = []
        
        # Add the last chunk
        if current_chunk:
            sub_queries.append(' '.join(current_chunk))
        
        # If no good breaking points, return original
        return sub_queries if sub_queries else [query]

    async def enhance_query(self, query: str) -> EnhancedQuery:
        """Enhance a query with expansions, classification, and optimization."""
        # Preprocess
        cleaned_query = self.preprocess_query(query)
        doc = nlp(cleaned_query)
        
        # Analyze and classify
        intent = self.classify_intent(cleaned_query, doc)
        is_technical = self._is_technical_query(cleaned_query, doc)
        complexity = self._get_query_complexity(doc)
        
        # Create context
        context = QueryContext(
            original_query=query,
            intent=intent,
            is_technical=is_technical,
            requires_context=complexity > 2,
            complexity=complexity,
            domain_terms=[term for term in self.technical_terms 
                         if term in cleaned_query.lower()]
        )
        
        # Expand query
        expanded_query = self.expand_query(cleaned_query, context)
        
        # Break down complex queries
        sub_queries = self.break_down_query(cleaned_query, context) if complexity > 2 else None
        
        # Extract keywords
        keywords = [token.text for token in doc 
                   if not token.is_stop and not token.is_punct]
        
        # Create metadata
        metadata = {
            "complexity": complexity,
            "requires_context": context.requires_context,
            "technical_terms": context.domain_terms,
            "query_length": len(doc),
            "has_sub_queries": bool(sub_queries)
        }
        
        return EnhancedQuery(
            original=query,
            expanded=expanded_query,
            context=context,
            sub_queries=sub_queries,
            keywords=keywords,
            metadata=metadata
        ) 