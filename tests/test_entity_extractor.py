"""
Tests for the EntityExtractor
"""
import pytest
from pathlib import Path

from llamagraph.config import LlamaGraphConfig
from llamagraph.utils.cache import Cache
from llamagraph.extractor.entity_extractor import EntityExtractor, Entity

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

def test_entity_extraction_basic(test_config, test_cache):
    """Test basic entity extraction"""
    extractor = EntityExtractor(test_config, test_cache)
    
    # Test with a simple sentence
    text = "Apple is headquartered in Cupertino. Tim Cook is the CEO of Apple."
    entities = extractor.extract(text)
    
    # Convert to a simpler representation for testing
    entity_texts = [e.text for e in entities]
    entity_types = [e.entity_type for e in entities]
    
    # Check that we found the expected entities
    assert "Apple" in entity_texts
    assert "Tim Cook" in entity_texts
    assert "Cupertino" in entity_texts
    
    # Check that the entities have the correct types
    apple_index = entity_texts.index("Apple")
    assert entity_types[apple_index] in ["ORG", "PRODUCT"]
    
    tim_cook_index = entity_texts.index("Tim Cook")
    assert entity_types[tim_cook_index] == "PERSON"
    
    cupertino_index = entity_texts.index("Cupertino")
    assert entity_types[cupertino_index] in ["GPE", "LOC"]

def test_entity_normalization(test_config, test_cache):
    """Test entity normalization"""
    extractor = EntityExtractor(test_config, test_cache)
    
    # Test with variations of the same entity
    text = "Google is a tech company. GOOGLE has offices in Mountain View."
    entities = extractor.extract(text)
    
    # Check that the normalized text is the same
    google_entities = [e for e in entities if e.text.lower() == "google"]
    assert len(google_entities) == 1
    
    # Check that both mentions are recorded
    assert "Google" in google_entities[0].mentions
    assert "GOOGLE" in google_entities[0].mentions

def test_entity_caching(test_config, test_cache):
    """Test entity caching"""
    extractor = EntityExtractor(test_config, test_cache)
    
    # Extract entities from a text
    text = "Microsoft was founded by Bill Gates. Bill Gates is now a philanthropist."
    entities1 = extractor.extract(text)
    
    # Extract again - should use cache
    entities2 = extractor.extract(text)
    
    # Check that the results are the same
    assert len(entities1) == len(entities2)
    
    # Check that all entities are found in both results
    for e1 in entities1:
        assert any(e2.text == e1.text and e2.entity_type == e1.entity_type 
                  for e2 in entities2) 