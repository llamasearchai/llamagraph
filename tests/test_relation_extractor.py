"""
Tests for the RelationExtractor
"""
import pytest
from pathlib import Path

from llamagraph.config import LlamaGraphConfig
from llamagraph.utils.cache import Cache
from llamagraph.extractor.entity_extractor import EntityExtractor, Entity
from llamagraph.extractor.relation_extractor import RelationExtractor, Relation

# Create a test config
@pytest.fixture
def test_config():
    config = LlamaGraphConfig()
    config.cache_dir = Path("/tmp/llamagraph_test/cache")
    return config

# Create a test cache
@pytest.fixture
def test_cache(test_config):
    cache = Cache(test_config.cache_dir, max_size=10)
    yield cache
    # Clean up
    cache.clear()

# Create test entities
@pytest.fixture
def test_entities():
    return [
        Entity("Google", "ORG", 0, 6),
        Entity("Alphabet", "ORG", 0, 8),
        Entity("Sundar Pichai", "PERSON", 0, 13),
        Entity("CEO", "TITLE", 0, 3),
        Entity("Mountain View", "GPE", 0, 13),
        Entity("California", "GPE", 0, 10),
    ]

def test_relation_extraction_basic(test_config, test_cache, test_entities):
    """Test basic relation extraction"""
    extractor = RelationExtractor(test_config, test_cache)
    
    # Test with a simple sentence
    text = "Google is owned by Alphabet. Sundar Pichai is the CEO of Google. Google is headquartered in Mountain View, California."
    relations = extractor.extract(text, test_entities)
    
    # Check that we found the expected relations
    relation_tuples = [(r.source.text, r.relation_type, r.target.text) for r in relations]
    
    assert ("Alphabet", "own", "Google") in relation_tuples or \
           ("Google", "owned_by", "Alphabet") in relation_tuples
    
    assert ("Sundar Pichai", "is_CEO_of", "Google") in relation_tuples or \
           ("Google", "has_CEO", "Sundar Pichai") in relation_tuples
    
    assert ("Google", "headquartered_in", "Mountain View") in relation_tuples or \
           ("Mountain View", "headquarters_of", "Google") in relation_tuples

def test_relation_caching(test_config, test_cache, test_entities):
    """Test relation caching"""
    extractor = RelationExtractor(test_config, test_cache)
    
    # Extract relations from a text
    text = "Google was founded by Larry Page and Sergey Brin. Larry Page is now working on other projects."
    
    # Create additional test entities
    additional_entities = test_entities + [
        Entity("Larry Page", "PERSON", 0, 10),
        Entity("Sergey Brin", "PERSON", 0, 11),
    ]
    
    relations1 = extractor.extract(text, additional_entities)
    
    # Extract again - should use cache
    relations2 = extractor.extract(text, additional_entities)
    
    # Check that the results are the same
    assert len(relations1) == len(relations2)
    
    # Check that all relations are found in both results
    relation_tuples1 = [(r.source.text, r.relation_type, r.target.text) for r in relations1]
    relation_tuples2 = [(r.source.text, r.relation_type, r.target.text) for r in relations2]
    
    for rel in relation_tuples1:
        assert rel in relation_tuples2 