"""
Relation extraction module for LlamaGraph
"""
import re
import logging
from typing import List, Dict, Any, Tuple, Set, Optional
import spacy

# Conditionally import MLX
try:
    import mlx.core as mx
    HAS_MLX = True
except ImportError:
    HAS_MLX = False

from llamagraph.config import LlamaGraphConfig
from llamagraph.utils.cache import Cache
from llamagraph.utils.threading import parallel_process
from llamagraph.extractor.entity_extractor import Entity

logger = logging.getLogger(__name__)

class Relation:
    """Relation class representing an edge in the knowledge graph"""
    def __init__(
        self, 
        source: Entity, 
        relation_type: str, 
        target: Entity, 
        sentence: str
    ):
        self.source = source
        self.target = target
        self.relation_type = relation_type
        self.sentence = sentence
    
    def __repr__(self):
        return f"Relation({self.source.text} --{self.relation_type}--> {self.target.text})"
    
    def to_dict(self):
        """Convert relation to dictionary"""
        return {
            "source": self.source.text,
            "relation_type": self.relation_type,
            "target": self.target.text,
            "sentence": self.sentence
        }

class RelationExtractor:
    """Extract relations between entities from text"""
    def __init__(self, config: LlamaGraphConfig, cache: Cache):
        self.config = config
        self.cache = cache
        
        # Load spaCy model
        self.nlp = spacy.load("en_core_web_sm")
        
        # Compile regex patterns
        self.patterns = {
            rel_type: re.compile(pattern, re.IGNORECASE)
            for rel_type, pattern in config.relation_patterns.items()
        }
        
        # Initialize MLX if available and enabled
        self.use_mlx = HAS_MLX and config.use_mlx
        logger.info(f"MLX acceleration: {'Enabled' if self.use_mlx else 'Disabled'}")
    
    def extract(self, text: str, entities: List[Entity]) -> List[Relation]:
        """Extract relations from text between the given entities"""
        # Check cache first
        cache_key = f"relations_{hash(text)}_{hash(tuple([(e.text, e.entity_type) for e in entities]))}"
        cached_result = self.cache.get(cache_key)
        if cached_result:
            logger.info("Using cached relation extraction results")
            # Reconstruct relations from cache
            entity_dict = {e.text: e for e in entities}
            relations = []
            for r in cached_result:
                source = entity_dict.get(r["source"])
                target = entity_dict.get(r["target"])
                if source and target:
                    relations.append(
                        Relation(source, r["relation_type"], target, r["sentence"])
                    )
            return relations
        
        # Create entity lookup dictionary for faster access
        entity_lookup = {}
        for entity in entities:
            entity_lookup[entity.text.lower()] = entity
            # Also add the entity with its type to handle cases where the same text
            # could refer to different entity types
            entity_lookup[f"{entity.text.lower()}_{entity.entity_type}"] = entity
        
        # Split text into sentences for processing
        doc = self.nlp(text)
        sentences = [sent.text for sent in doc.sents]
        
        # Process sentences in parallel with entity context
        results = parallel_process(
            items=sentences,
            process_func=lambda sent: self._process_sentence(sent, entity_lookup),
            num_threads=self.config.num_threads,
            description="Extracting relations"
        )
        
        # Combine results
        relations = []
        for sentence_relations in results:
            relations.extend(sentence_relations)
        
        # Cache the results
        self.cache.set(cache_key, [
            {
                "source": r.source.text, 
                "relation_type": r.relation_type, 
                "target": r.target.text,
                "sentence": r.sentence
            }
            for r in relations
        ])
        
        return relations
    
    def _process_sentence(self, sentence: str, entity_lookup: Dict[str, Entity]) -> List[Relation]:
        """Process a single sentence to extract relations between entities"""
        relations = []
        
        # First, extract relations using pattern matching
        relations.extend(self._extract_with_patterns(sentence, entity_lookup))
        
        # Then, extract relations using syntax parsing
        relations.extend(self._extract_with_syntax(sentence, entity_lookup))
        
        # If using MLX, perform additional processing
        if self.use_mlx:
            relations.extend(self._extract_with_mlx(sentence, entity_lookup))
        
        return relations
    
    def _extract_with_patterns(self, sentence: str, entity_lookup: Dict[str, Entity]) -> List[Relation]:
        """Extract relations using regex patterns"""
        relations = []
        
        # Check each pattern against the sentence
        for relation_type, pattern in self.patterns.items():
            matches = pattern.finditer(sentence)
            for match in matches:
                # The pattern structure determines how we extract entities
                # This is a simplified approach - real implementation would be more robust
                if relation_type in ["works_for", "founded", "created"]:
                    # Pattern: (person) (verb) (organization)
                    person = match.group(1)
                    org = match.group(3)
                    
                    source_entity = self._find_entity(person, entity_lookup)
                    target_entity = self._find_entity(org, entity_lookup)
                    
                    if source_entity and target_entity:
                        relation = Relation(
                            source=source_entity,
                            relation_type=relation_type,
                            target=target_entity,
                            sentence=sentence
                        )
                        relations.append(relation)
                
                elif relation_type == "has_role":
                    # Pattern: (person) is (person)'s (role)
                    person1 = match.group(1)
                    person2 = match.group(3)
                    role = match.group(4)
                    
                    source_entity = self._find_entity(person1, entity_lookup)
                    target_entity = self._find_entity(person2, entity_lookup)
                    
                    if source_entity and target_entity:
                        relation = Relation(
                            source=source_entity,
                            relation_type=f"is_{role}_of",
                            target=target_entity,
                            sentence=sentence
                        )
                        relations.append(relation)
        
        return relations
    
    def _extract_with_syntax(self, sentence: str, entity_lookup: Dict[str, Entity]) -> List[Relation]:
        """Extract relations using dependency syntax parsing"""
        relations = []
        
        # Parse the sentence with spaCy
        doc = self.nlp(sentence)
        
        # Find entities in the parsed sentence
        sentence_entities = {}
        for token in doc:
            entity_key = token.text.lower()
            if entity_key in entity_lookup:
                sentence_entities[token.i] = entity_lookup[entity_key]
        
        # Look for subject-verb-object patterns
        for token in doc:
            if token.dep_ == "ROOT" and token.pos_ == "VERB":
                # This is a main verb
                subject = None
                object = None
                
                # Find the subject
                for child in token.children:
                    if child.dep_ in ["nsubj", "nsubjpass"] and child.i in sentence_entities:
                        subject = sentence_entities[child.i]
                        break
                
                # Find the object
                for child in token.children:
                    if child.dep_ in ["dobj", "pobj"] and child.i in sentence_entities:
                        object = sentence_entities[child.i]
                        break
                
                # If we found both subject and object, create a relation
                if subject and object:
                    relation = Relation(
                        source=subject,
                        relation_type=token.lemma_,  # Use the verb lemma as relation type
                        target=object,
                        sentence=sentence
                    )
                    relations.append(relation)
        
        return relations
    
    def _extract_with_mlx(self, sentence: str, entity_lookup: Dict[str, Entity]) -> List[Relation]:
        """Extract relations using MLX for better performance"""
        # This is a simplified example of MLX usage
        # In a real implementation, you'd use MLX for more complex computations
        
        relations = []
        # Example: Using MLX to vectorize pattern matching across multiple patterns
        # (This is a simplified example - real implementation would be more sophisticated)
        
        # In a real implementation, you'd implement more complex relation extraction
        # using MLX arrays and operations for performance
        
        return relations
    
    def _find_entity(self, text: str, entity_lookup: Dict[str, Entity]) -> Optional[Entity]:
        """Find an entity by text in the lookup dictionary"""
        text_lower = text.lower()
        
        # Try exact match
        if text_lower in entity_lookup:
            return entity_lookup[text_lower]
        
        # Try fuzzy matching (simplified)
        for key, entity in entity_lookup.items():
            if text_lower in key or key in text_lower:
                return entity
        
        return None 