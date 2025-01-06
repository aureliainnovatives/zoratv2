"""Document analysis and processing utilities."""
import re
import nltk
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from langdetect import detect
import spacy
from datetime import datetime

# Download required NLTK data
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('maxent_ne_chunker')
nltk.download('words')

# Load spaCy model
try:
    nlp = spacy.load('en_core_web_sm')
except OSError:
    spacy.cli.download('en_core_web_sm')
    nlp = spacy.load('en_core_web_sm')

@dataclass
class TextSegment:
    """Represents a segment of text with metadata."""
    content: str
    start_char: int
    end_char: int
    segment_type: str
    level: Optional[int] = None
    metadata: Dict = None

class DocumentAnalyzer:
    """Analyzes document content and structure."""
    
    def __init__(self):
        self.heading_patterns = [
            r'^#{1,6}\s+(.+)$',  # Markdown headings
            r'^(\d+\.)+\s+(.+)$',  # Numbered headings
            r'^[A-Z][A-Za-z\s]+:',  # Title-like headings
        ]
    
    def detect_language(self, text: str) -> str:
        """Detect the language of the text."""
        try:
            return detect(text)
        except:
            return 'unknown'
    
    def extract_metadata(self, text: str) -> Dict:
        """Extract metadata from document content."""
        doc = nlp(text[:5000])  # Process first 5000 chars for metadata
        
        return {
            'language': self.detect_language(text),
            'keywords': [ent.text for ent in doc.ents],
            'created_date': datetime.now(),  # This should be from file metadata
            'modified_date': datetime.now()  # This should be from file metadata
        }
    
    def identify_section_type(self, text: str) -> Tuple[str, Optional[int]]:
        """Identify the type and level of a section."""
        # Check for headings
        for pattern in self.heading_patterns:
            match = re.match(pattern, text.strip())
            if match:
                level = text.count('#') if '#' in text else 1
                return 'heading', level
        
        # Check for other types
        if re.match(r'^\s*[-*]\s', text):
            return 'list', None
        elif re.match(r'^\s*\d+\.\s', text):
            return 'list', None
        elif re.match(r'```.*```', text, re.DOTALL):
            return 'code', None
        elif len(text.strip()) < 100 and text.endswith('?'):
            return 'question', None
        elif re.match(r'^\s*>.+', text):
            return 'quote', None
        elif re.search(r'\|\s*[-]+\s*\|', text):
            return 'table', None
        
        return 'paragraph', None

    def analyze_content(self, text: str) -> Dict:
        """Analyze content for statistics and key phrases."""
        doc = nlp(text)
        
        # Basic statistics
        stats = {
            'word_count': len(doc),
            'char_count': len(text),
            'sentence_count': len(list(doc.sents)),
            'key_phrases': []
        }
        
        # Extract key phrases (noun phrases)
        key_phrases = []
        for chunk in doc.noun_chunks:
            if len(chunk.text.split()) > 1:  # Multi-word phrases
                key_phrases.append(chunk.text)
        stats['key_phrases'] = key_phrases[:5]  # Top 5 key phrases
        
        return stats

    def calculate_chunk_quality(self, chunk: str) -> Dict[str, float]:
        """Calculate quality metrics for a chunk."""
        # Coherence score based on sentence flow
        sentences = nltk.sent_tokenize(chunk)
        coherence_score = 1.0 if len(sentences) == 1 else min(1.0, len(sentences) / 10)
        
        # Completeness score based on sentence completeness
        complete_sentences = sum(1 for s in sentences if s.strip()[-1] in '.!?')
        completeness_score = complete_sentences / len(sentences) if sentences else 0.0
        
        # Relevance score (placeholder - should be calculated based on context)
        relevance_score = 0.8  # Default score
        
        return {
            'coherence_score': coherence_score,
            'completeness_score': completeness_score,
            'relevance_score': relevance_score
        }

class SmartChunker:
    """Implements intelligent document chunking strategies."""
    
    def __init__(self, analyzer: DocumentAnalyzer):
        self.analyzer = analyzer
        self.min_chunk_size = 100
        self.max_chunk_size = 1000
        self.overlap_size = 50
    
    def find_break_point(self, text: str, around_position: int) -> int:
        """Find the best position to break the text."""
        # Try to break at paragraph
        if '\n\n' in text[max(0, around_position-100):min(len(text), around_position+100)]:
            return text.find('\n\n', around_position)
        
        # Try to break at sentence
        sentences = nltk.sent_tokenize(text[max(0, around_position-100):min(len(text), around_position+100)])
        if sentences:
            current_pos = 0
            for sent in sentences:
                current_pos += len(sent)
                if current_pos >= 100:
                    return around_position + current_pos
        
        # Fall back to word boundary
        words = text[max(0, around_position-50):min(len(text), around_position+50)].split()
        if words:
            return around_position + len(words[0])
        
        return around_position

    def create_chunks(self, text: str, doc_id: str) -> List[Dict]:
        """Create intelligent chunks from text."""
        chunks = []
        current_pos = 0
        chunk_number = 0
        
        while current_pos < len(text):
            # Determine chunk size based on content
            if self.analyzer.identify_section_type(text[current_pos:])[0] == 'heading':
                target_size = self.min_chunk_size
            else:
                target_size = self.max_chunk_size
            
            # Find break point
            end_pos = self.find_break_point(text, current_pos + target_size)
            if end_pos <= current_pos:
                end_pos = min(current_pos + self.max_chunk_size, len(text))
            
            # Extract chunk content
            chunk_text = text[current_pos:end_pos]
            
            # Analyze chunk
            section_type, level = self.analyzer.identify_section_type(chunk_text)
            content_stats = self.analyzer.analyze_content(chunk_text)
            quality_metrics = self.analyzer.calculate_chunk_quality(chunk_text)
            
            # Create chunk
            chunk = {
                'document_id': doc_id,
                'content': chunk_text,
                'position': {
                    'chunk_number': chunk_number,
                    'start_char': current_pos,
                    'end_char': end_pos
                },
                'metadata': {
                    'section_type': section_type,
                    'section_level': level,
                    'section_number': chunk_number,
                    'is_table_content': section_type == 'table',
                    'is_figure_content': 'figure' in chunk_text.lower() or 'img' in chunk_text.lower(),
                    'content_classification': 'technical' if section_type in ['code', 'table'] else 'narrative'
                },
                'content_stats': content_stats,
                'quality': quality_metrics
            }
            
            chunks.append(chunk)
            
            # Move position and handle overlap
            current_pos = end_pos - self.overlap_size
            chunk_number += 1
        
        return chunks 