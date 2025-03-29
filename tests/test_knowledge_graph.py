"""
Tests for the KnowledgeGraph
"""
import pytest
import json
import tempfile
import os
from pathlib import Path

from llamagraph.extractor.entity_extractor import Entity
from llamagraph.extractor.relation_extractor import Relation
from llamagraph.graph.knowledge_graph import KnowledgeGraph

@pytest.fixture
def test_entities():
    """Create test entities"""
    return [
        Entity("Google", "ORG", 0, 6),
        Entity("Microsoft", "ORG", 0, 9),
        Entity("Apple", "ORG", 0, 5),
        Entity("Sundar Pichai", "PERSON", 0, 13),
        Entity("Satya Nadella", "PERSON", 0, 13),
        Entity("Tim Cook", "PERSON", 0, 8),
    ]

@pytest.fixture
def test_relations(test_entities):
    """Create test relations"""
    google = test_entities[0]
    microsoft = test_entities[1]
    apple = test_entities[2]
    sundar = test_entities[3]
    satya = test_entities[4]
    tim = test_entities[5]
    
    return [
        Relation(sundar, "is_CEO_of", google, "Sundar Pichai is the CEO of Google."),
        Relation(satya, "is_CEO_of", microsoft, "Satya Nadella is the CEO of Microsoft."),
        Relation(tim, "is_CEO_of", apple, "Tim Cook is the CEO of Apple."),
        Relation(google, "competitor_of", microsoft, "Google competes with Microsoft."),
        Relation(google, "competitor_of", apple, "Google competes with Apple."),
        Relation(microsoft, "competitor_of", apple, "Microsoft competes with Apple."),
    ]

def test_graph_construction(test_entities, test_relations):
    """Test constructing a knowledge graph"""
    kg = KnowledgeGraph()
    
    # Add entities
    for entity in test_entities:
        kg.add_entity(entity)
    
    # Check that all entities were added
    assert len(kg.entities) == len(test_entities)
    
    # Add relations
    for relation in test_relations:
        kg.add_relation(relation)
    
    # Check that all relations were added
    assert len(kg.relations) == len(test_relations)
    
    # Check that the graph structure was created correctly
    assert kg.graph.number_of_nodes() == len(test_entities)
    assert kg.graph.number_of_edges() == len(test_relations)

def test_get_entity(test_entities, test_relations):
    """Test getting entities from the graph"""
    kg = KnowledgeGraph()
    
    # Add entities and relations
    for entity in test_entities:
        kg.add_entity(entity)
    
    for relation in test_relations:
        kg.add_relation(relation)
    
    # Get an entity
    google = kg.get_entity("Google")
    assert google is not None
    assert google.text == "Google"
    
    # Get a non-existent entity
    nonexistent = kg.get_entity("Nonexistent")
    assert nonexistent is None

def test_get_relations(test_entities, test_relations):
    """Test getting relations for an entity"""
    kg = KnowledgeGraph()
    
    # Add entities and relations
    for entity in test_entities:
        kg.add_entity(entity)
    
    for relation in test_relations:
        kg.add_relation(relation)
    
    # Get relations for Google
    google_relations = kg.get_relations("Google")
    
    # Check that we have the right number of relations
    # Google should have 3 relations: CEO, and competitor_of with Microsoft and Apple
    assert len(google_relations) == 3
    
    # Check the relation types
    relation_types = [rel["relation_type"] for rel in google_relations]
    assert "competitor_of" in relation_types
    
    # Check the related entities
    related_entities = [rel["entity"] for rel in google_relations]
    assert "Microsoft" in related_entities
    assert "Apple" in related_entities

def test_get_path(test_entities, test_relations):
    """Test finding paths between entities"""
    kg = KnowledgeGraph()
    
    # Add entities and relations
    for entity in test_entities:
        kg.add_entity(entity)
    
    for relation in test_relations:
        kg.add_relation(relation)
    
    # Find path from Sundar Pichai to Microsoft
    path = kg.get_path("Sundar Pichai", "Microsoft")
    
    # The path should be Sundar Pichai -> Google -> Microsoft
    assert len(path) == 2
    assert path[0]["source"] == "Sundar Pichai"
    assert path[0]["target"] == "Google"
    assert path[1]["source"] == "Google"
    assert path[1]["target"] == "Microsoft"

def test_serialization(test_entities, test_relations):
    """Test serializing and deserializing the graph"""
    kg = KnowledgeGraph()
    
    # Add entities and relations
    for entity in test_entities:
        kg.add_entity(entity)
    
    for relation in test_relations:
        kg.add_relation(relation)
    
    # Serialize to dict
    data = kg.to_dict()
    
    # Check that the serialized data is correct
    assert len(data["entities"]) == len(test_entities)
    assert len(data["relations"]) == len(test_relations)
    
    # Serialize to JSON
    json_str = kg.to_json()
    
    # Check that the JSON is valid
    json_data = json.loads(json_str)
    assert len(json_data["entities"]) == len(test_entities)
    assert len(json_data["relations"]) == len(test_relations)
    
    # Save and load
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        kg.save(tmp.name)
        
        # Create a new graph
        kg2 = KnowledgeGraph()
        kg2.load(tmp.name)
        
        # Check that the loaded graph is correct
        assert len(kg2.entities) == len(test_entities)
        assert len(kg2.relations) == len(test_relations)
    
    # Clean up
    os.unlink(tmp.name) 