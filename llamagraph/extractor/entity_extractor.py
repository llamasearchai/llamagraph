"""
Entity extraction module for LlamaGraph
"""
import time
import logging
from typing import List, Dict, Any, Set, Optional
import spacy
from spacy.tokens import Doc

# Conditionally import MLX
try:
    import mlx.core as mx
    HAS_MLX = True
except ImportError:
    HAS_MLX = False

from llamagraph.config import LlamaGraphConfig
from llamagraph.utils.cache import Cache
from llamagraph.utils.threading import parallel_process

logger = logging.getLogger(__name__)

class Entity:
    """Entity class representing a node in the knowledge graph"""
    def __init__(self, text: str, entity_type: str, start: int, end: int):
        self.text = text
        self.normalized_text = text.lower().strip()
        self.entity_type = entity_type
        self.start = start
        self.end = end
        self.occurrences = 1
        self.mentions = set([text])
        
    def __repr__(self):
        return f"Entity(text='{self.text}', type='{self.entity_type}')"
    
    def to_dict(self):
        """Convert entity to dictionary"""
        return {
            "text": self.text,
            "entity_type": self.entity_type,
            "occurrences": self.occurrences,
            "mentions": list(self.mentions)
        }
    
    def update(self, other: 'Entity'):
        """Update entity with information from another entity"""
        self.occurrences += other.occurrences
        self.mentions.update(other.mentions)

class EntityExtractor:
    """Extract entities from text using SpaCy and MLX acceleration"""
    def __init__(self, config: LlamaGraphConfig, cache: Cache):
        self.config = config
        self.cache = cache
        
        # Load spaCy model
        self.nlp = spacy.load("en_core_web_sm")
        
        # Initialize MLX if available and enabled
        self.use_mlx = HAS_MLX and config.use_mlx
        logger.info(f"MLX acceleration: {'Enabled' if self.use_mlx else 'Disabled'}")
    
    def extract(self, text: str) -> List[Entity]:
        """Extract entities from text"""
        # Check cache first
        cache_key = f"entities_{hash(text)}"
        cached_result = self.cache.get(cache_key)
        if cached_result:
            logger.info("Using cached entity extraction results")
            return [Entity(e["text"], e["entity_type"], e["start"], e["end"]) 
                   for e in cached_result]
        
        # Split text into chunks for parallel processing
        sentences = list(self.nlp(text).sents)
        
        # Process sentences in parallel
        results = parallel_process(
            items=sentences,
            process_func=self._process_sentence,
            num_threads=self.config.num_threads,
            description="Extracting entities"
        )
        
        # Merge and deduplicate entities
        entities_dict = {}
        for sentence_entities in results:
            for entity in sentence_entities:
                key = (entity.normalized_text, entity.entity_type)
                if key in entities_dict:
                    entities_dict[key].update(entity)
                else:
                    entities_dict[key] = entity
        
        entities = list(entities_dict.values())
        
        # Cache the results
        self.cache.set(cache_key, [
            {"text": e.text, "entity_type": e.entity_type, "start": e.start, "end": e.end}
            for e in entities
        ])
        
        return entities
    
    def _process_sentence(self, sentence: Doc) -> List[Entity]:
        """Process a single sentence to extract entities"""
        sentence_text = sentence.text
        doc = self.nlp(sentence_text)
        
        entities = []
        for ent in doc.ents:
            if ent.label_ in self.config.entity_types:
                entity = Entity(
                    text=ent.text,
                    entity_type=ent.label_,
                    start=ent.start_char,
                    end=ent.end_char
                )
                entities.append(entity)
        
        # If using MLX, perform additional processing
        if self.use_mlx:
            entities.extend(self._extract_with_mlx(sentence_text))
        
        return entities
    
    def _extract_with_mlx(self, text: str) -> List[Entity]:
        """Extract entities using MLX for better performance"""
        # This is a simplified example of MLX usage
        # In a real implementation, you'd use MLX for more complex computations
        
        additional_entities = []
        # Example: using MLX to quickly find capitalized phrases not caught by spaCy
        # (This is a simplified example - real implementation would be more sophisticated)
        
        # In a real implementation, you'd implement more complex entity extraction
        # using MLX arrays and operations for performance
        
        return additional_entities 