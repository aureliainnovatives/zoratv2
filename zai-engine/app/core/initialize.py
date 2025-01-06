"""Initialization module for NLP components."""
import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)

def initialize_nlp():
    """Initialize NLP components (NLTK and spaCy)."""
    try:
        # Create data directories if they don't exist
        nltk_data_dir = Path.home() / 'nltk_data'
        spacy_data_dir = Path.home() / '.cache/spacy'
        
        nltk_data_dir.mkdir(parents=True, exist_ok=True)
        spacy_data_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize NLTK
        import nltk
        required_nltk_data = ['punkt', 'averaged_perceptron_tagger', 'maxent_ne_chunker', 'words']
        for item in required_nltk_data:
            try:
                if not nltk.data.find(item):
                    nltk.download(item, quiet=True)
            except LookupError:
                nltk.download(item, quiet=True)
        
        # Initialize spaCy
        import spacy
        from spacy.cli import download
        model_name = 'en_core_web_sm'
        try:
            spacy.load(model_name)
        except OSError:
            download(model_name, False)
        
        logger.info("Successfully initialized NLP components")
        return True
        
    except Exception as e:
        logger.error(f"Error initializing NLP components: {str(e)}")
        return False 