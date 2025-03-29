"""
Knowledge graph module for LlamaGraph
"""
import json
import logging
from typing import List, Dict, Any, Set, Optional, Union
import networkx as nx

from llamagraph.extractor.entity_extractor import Entity
from llamagraph.extractor.relation_extractor import Relation

logger = logging.getLogger(__name__)

class KnowledgeGraph:
    """Knowledge graph representation"""
    def __init__(self):
        self.entities = {}  # text -> Entity
        self.relations = []  # List of Relation objects
        self.graph = nx.DiGraph()  # NetworkX directed graph
    
    def add_entity(self, entity: Entity):
        """Add an entity to the graph"""
        if entity.text not in self.entities:
            self.entities[entity.text] = entity
            self.graph.add_node(entity.text, **entity.to_dict())
        else:
            # Update existing entity
            self.entities[entity.text].update(entity)
            # Update node attributes
            self.graph.nodes[entity.text].update(self.entities[entity.text].to_dict())
    
    def add_relation(self, relation: Relation):
        """Add a relation to the graph"""
        self.relations.append(relation)
        
        # Add the relation as an edge in the graph
        self.graph.add_edge(
            relation.source.text, 
            relation.target.text,
            relation_type=relation.relation_type,
            sentence=relation.sentence
        )
    
    def get_entity(self, entity_text: str) -> Optional[Entity]:
        """Get an entity by its text"""
        return self.entities.get(entity_text)
    
    def get_relations(self, entity_text: str) -> List[Dict[str, Any]]:
        """Get all relations for an entity"""
        entity = self.get_entity(entity_text)
        if not entity:
            return []
        
        relations = []
        
        # Outgoing relations (entity is source)
        for _, target, data in self.graph.out_edges(entity.text, data=True):
            relations.append({
                "direction": "outgoing",
                "relation_type": data["relation_type"],
                "entity": target,
                "sentence": data["sentence"]
            })
        
        # Incoming relations (entity is target)
        for source, _, data in self.graph.in_edges(entity.text, data=True):
            relations.append({
                "direction": "incoming",
                "relation_type": data["relation_type"],
                "entity": source,
                "sentence": data["sentence"]
            })
        
        return relations
    
    def get_path(self, source: str, target: str) -> List[Dict[str, Any]]:
        """Find the shortest path between two entities"""
        try:
            path = nx.shortest_path(self.graph, source, target)
            result = []
            
            # Convert path to a list of entities and relations
            for i in range(len(path) - 1):
                source_node = path[i]
                target_node = path[i + 1]
                edge_data = self.graph.get_edge_data(source_node, target_node)
                
                result.append({
                    "source": source_node,
                    "target": target_node,
                    "relation_type": edge_data["relation_type"],
                    "sentence": edge_data["sentence"]
                })
            
            return result
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the knowledge graph to a dictionary"""
        return {
            "entities": [entity.to_dict() for entity in self.entities.values()],
            "relations": [relation.to_dict() for relation in self.relations]
        }
    
    def to_json(self, indent: int = 2) -> str:
        """Convert the knowledge graph to JSON"""
        return json.dumps(self.to_dict(), indent=indent)
    
    def save(self, filename: str):
        """Save the knowledge graph to a file"""
        with open(filename, "w") as f:
            f.write(self.to_json())
    
    def load(self, filename: str):
        """Load the knowledge graph from a file"""
        with open(filename, "r") as f:
            data = json.load(f)
        
        # Clear existing graph
        self.entities = {}
        self.relations = []
        self.graph = nx.DiGraph()
        
        # Add entities
        for entity_data in data.get("entities", []):
            entity = Entity(
                text=entity_data["text"],
                entity_type=entity_data["entity_type"],
                start=0,  # We don't have position info when loading
                end=0
            )
            entity.occurrences = entity_data.get("occurrences", 1)
            entity.mentions = set(entity_data.get("mentions", [entity_data["text"]]))
            self.add_entity(entity)
        
        # Add relations
        for relation_data in data.get("relations", []):
            source = self.get_entity(relation_data["source"])
            target = self.get_entity(relation_data["target"])
            if source and target:
                relation = Relation(
                    source=source,
                    relation_type=relation_data["relation_type"],
                    target=target,
                    sentence=relation_data.get("sentence", "")
                )
                self.add_relation(relation)
            else:
                logger.warning(f"Couldn't load relation: {relation_data}")
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the knowledge graph"""
        return {
            "num_entities": len(self.entities),
            "num_relations": len(self.relations),
            "entity_types": self._count_entity_types(),
            "relation_types": self._count_relation_types(),
            "most_connected": self._get_most_connected(5)
        }
    
    def _count_entity_types(self) -> Dict[str, int]:
        """Count the occurrences of each entity type"""
        counts = {}
        for entity in self.entities.values():
            counts[entity.entity_type] = counts.get(entity.entity_type, 0) + 1
        return counts
    
    def _count_relation_types(self) -> Dict[str, int]:
        """Count the occurrences of each relation type"""
        counts = {}
        for relation in self.relations:
            counts[relation.relation_type] = counts.get(relation.relation_type, 0) + 1
        return counts
    
    def _get_most_connected(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get the most connected entities"""
        degrees = [(node, self.graph.degree(node)) for node in self.graph.nodes()]
        degrees.sort(key=lambda x: x[1], reverse=True)
        
        result = []
        for node, degree in degrees[:limit]:
            entity = self.get_entity(node)
            if entity:
                result.append({
                    "entity": node,
                    "type": entity.entity_type,
                    "connections": degree
                })
        
        return result 