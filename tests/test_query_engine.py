"""
Tests for the QueryEngine
"""
import pytest
from pathlib import Path

from llamagraph.extractor.entity_extractor import Entity
from llamagraph.extractor.relation_extractor import Relation
from llamagraph.graph.knowledge_graph import KnowledgeGraph
from llamagraph.graph.query_engine import QueryEngine

@pytest.fixture
def test_knowledge_graph():
    """Create a test knowledge graph"""
    kg = KnowledgeGraph()
    
    # Create entities
    entities = [
        Entity("Google", "ORG", 0, 6),
        Entity("Microsoft", "ORG", 0, 9),
        Entity("Apple", "ORG", 0, 5),
        Entity("Sundar Pichai", "PERSON", 0, 13),
        Entity("Satya Nadella", "PERSON", 0, 13),
        Entity("Tim Cook", "PERSON", 0, 8),
        Entity("Mountain View", "GPE", 0, 13),
        Entity("Redmond", "GPE", 0, 7),
        Entity("Cupertino", "GPE", 0, 9),
    ]
    
    # Add entities
    for entity in entities:
        kg.add_entity(entity)
    
    # Create relations
    google = kg.get_entity("Google")
    microsoft = kg.get_entity("Microsoft")
    apple = kg.get_entity("Apple")
    sundar = kg.get_entity("Sundar Pichai")
    satya = kg.get_entity("Satya Nadella")
    tim = kg.get_entity("Tim Cook")
    mountain_view = kg.get_entity("Mountain View")
    redmond = kg.get_entity("Redmond")
    cupertino = kg.get_entity("Cupertino")
    
    relations = [
        Relation(sundar, "is_CEO_of", google, "Sundar Pichai is the CEO of Google."),
        Relation(satya, "is_CEO_of", microsoft, "Satya Nadella is the CEO of Microsoft."),
        Relation(tim, "is_CEO_of", apple, "Tim Cook is the CEO of Apple."),
        Relation(google, "competitor_of", microsoft, "Google competes with Microsoft."),
        Relation(google, "competitor_of", apple, "Google competes with Apple."),
        Relation(microsoft, "competitor_of", apple, "Microsoft competes with Apple."),
        Relation(google, "headquartered_in", mountain_view, "Google is headquartered in Mountain View."),
        Relation(microsoft, "headquartered_in", redmond, "Microsoft is headquartered in Redmond."),
        Relation(apple, "headquartered_in", cupertino, "Apple is headquartered in Cupertino."),
    ]
    
    # Add relations
    for relation in relations:
        kg.add_relation(relation)
    
    return kg

def test_find_query(test_knowledge_graph):
    """Test 'find' queries"""
    query_engine = QueryEngine(test_knowledge_graph)
    
    # Test finding Google
    result = query_engine.execute_query("find Google")
    assert result["success"] is True
    assert result["data"]["entity"]["text"] == "Google"
    assert len(result["data"]["relations"]) > 0
    
    # Test finding a non-existent entity
    result = query_engine.execute_query("find Nonexistent")
    assert result["success"] is False

def test_path_query(test_knowledge_graph):
    """Test 'path' queries"""
    query_engine = QueryEngine(test_knowledge_graph)
    
    # Test finding a path from Sundar Pichai to Redmond
    result = query_engine.execute_query("path from Sundar Pichai to Redmond")
    assert result["success"] is True
    assert result["data"]["length"] == 3  # Sundar -> Google -> Microsoft -> Redmond
    
    # Test finding a path that doesn't exist
    result = query_engine.execute_query("path from Sundar Pichai to Tim Cook")
    assert result["success"] is False

def test_related_query(test_knowledge_graph):
    """Test 'related' queries"""
    query_engine = QueryEngine(test_knowledge_graph)
    
    # Test finding entities related to Google
    result = query_engine.execute_query("related Google")
    assert result["success"] is True
    assert "direct_relations" in result["data"]
    assert "similar_entities" in result["data"]

def test_count_query(test_knowledge_graph):
    """Test 'count' queries"""
    query_engine = QueryEngine(test_knowledge_graph)
    
    # Test counting entities
    result = query_engine.execute_query("count entities")
    assert result["success"] is True
    assert "counts" in result["data"]
    assert sum(result["data"]["counts"].values()) == 9  # 9 entities total
    
    # Test counting relations
    result = query_engine.execute_query("count relations")
    assert result["success"] is True
    assert "counts" in result["data"]
    assert sum(result["data"]["counts"].values()) == 9  # 9 relations total

def test_help_query(test_knowledge_graph):
    """Test 'help' queries"""
    query_engine = QueryEngine(test_knowledge_graph)
    
    # Test help command
    result = query_engine.execute_query("help")
    assert result["success"] is True
    assert "commands" in result["data"]
    assert len(result["data"]["commands"]) > 0 