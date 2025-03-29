"""
Query engine for the knowledge graph
"""
import logging
from typing import List, Dict, Any, Optional, Union
import re

from llamagraph.graph.knowledge_graph import KnowledgeGraph

logger = logging.getLogger(__name__)

class QueryEngine:
    """Query engine for the knowledge graph"""
    def __init__(self, knowledge_graph: KnowledgeGraph):
        self.kg = knowledge_graph
        
        # Command patterns for parsing user queries
        self.command_patterns = {
            "find": r"^find\s+(.+)$",
            "path": r"^path\s+from\s+(.+)\s+to\s+(.+)$",
            "related": r"^related\s+(.+)$",
            "count": r"^count\s+(.+)$",
            "export": r"^export\s+(.+)$",
            "help": r"^help$",
        }
        
        # Compile regex patterns
        self.patterns = {
            cmd: re.compile(pattern, re.IGNORECASE)
            for cmd, pattern in self.command_patterns.items()
        }
    
    def execute_query(self, query: str) -> Dict[str, Any]:
        """Execute a query on the knowledge graph"""
        query = query.strip()
        
        # Try to match each command pattern
        for cmd, pattern in self.patterns.items():
            match = pattern.match(query)
            if match:
                method_name = f"_handle_{cmd}"
                if hasattr(self, method_name):
                    handler = getattr(self, method_name)
                    return handler(*match.groups())
        
        # If no pattern matched, try to be flexible
        if "find" in query.lower() or "show" in query.lower():
            # Extract potential entity name
            words = query.split()
            potential_entity = " ".join(words[1:]) if len(words) > 1 else ""
            if potential_entity:
                return self._handle_find(potential_entity)
        
        # Default response for unrecognized commands
        return {
            "success": False,
            "message": "I don't understand that query. Try 'help' for a list of commands.",
            "data": None
        }
    
    def _handle_find(self, entity_name: str) -> Dict[str, Any]:
        """Handle 'find <entity>' queries"""
        entity = self.kg.get_entity(entity_name)
        if not entity:
            # Try case-insensitive search
            for name, e in self.kg.entities.items():
                if name.lower() == entity_name.lower():
                    entity = e
                    break
        
        if entity:
            relations = self.kg.get_relations(entity.text)
            return {
                "success": True,
                "message": f"Found entity: {entity.text}",
                "data": {
                    "entity": entity.to_dict(),
                    "relations": relations
                }
            }
        else:
            return {
                "success": False,
                "message": f"Entity '{entity_name}' not found.",
                "data": None
            }
    
    def _handle_path(self, source: str, target: str) -> Dict[str, Any]:
        """Handle 'path from <entity1> to <entity2>' queries"""
        source_entity = self.kg.get_entity(source)
        target_entity = self.kg.get_entity(target)
        
        if not source_entity:
            return {
                "success": False,
                "message": f"Source entity '{source}' not found.",
                "data": None
            }
        
        if not target_entity:
            return {
                "success": False,
                "message": f"Target entity '{target}' not found.",
                "data": None
            }
        
        path = self.kg.get_path(source_entity.text, target_entity.text)
        
        if path:
            return {
                "success": True,
                "message": f"Found path from '{source}' to '{target}'",
                "data": {
                    "path": path,
                    "length": len(path)
                }
            }
        else:
            return {
                "success": False,
                "message": f"No path found from '{source}' to '{target}'.",
                "data": None
            }
    
    def _handle_related(self, entity_name: str) -> Dict[str, Any]:
        """Handle 'related <entity>' queries to find semantically related entities"""
        entity = self.kg.get_entity(entity_name)
        if not entity:
            return {
                "success": False,
                "message": f"Entity '{entity_name}' not found.",
                "data": None
            }
        
        # Get direct relations
        direct_relations = self.kg.get_relations(entity.text)
        
        # Get entities that share similar relations
        similar_entities = []
        for rel in direct_relations:
            other_entity = rel["entity"]
            # For each entity connected to our target, get their relations
            other_relations = self.kg.get_relations(other_entity)
            for other_rel in other_relations:
                if other_rel["entity"] != entity.text and other_rel["relation_type"] == rel["relation_type"]:
                    # This entity shares a similar relation
                    similar_entities.append({
                        "entity": other_rel["entity"],
                        "shared_relation_type": rel["relation_type"],
                        "via": other_entity
                    })
        
        return {
            "success": True,
            "message": f"Found related entities for '{entity_name}'",
            "data": {
                "direct_relations": direct_relations,
                "similar_entities": similar_entities[:5]  # Limit to top 5
            }
        }
    
    def _handle_count(self, entity_type: str) -> Dict[str, Any]:
        """Handle 'count <entity_type>' queries"""
        counts = {}
        if entity_type.lower() == "entities":
            counts = self.kg._count_entity_types()
        elif entity_type.lower() == "relations":
            counts = self.kg._count_relation_types()
        else:
            # Count entities of a specific type
            count = 0
            for entity in self.kg.entities.values():
                if entity.entity_type.lower() == entity_type.lower():
                    count += 1
            counts = {entity_type: count}
        
        return {
            "success": True,
            "message": f"Count for {entity_type}",
            "data": {
                "counts": counts,
                "total": sum(counts.values())
            }
        }
    
    def _handle_export(self, filename: str) -> Dict[str, Any]:
        """Handle 'export <filename>' queries"""
        try:
            self.kg.save(filename)
            return {
                "success": True,
                "message": f"Knowledge graph exported to {filename}",
                "data": None
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error exporting knowledge graph: {str(e)}",
                "data": None
            }
    
    def _handle_help(self) -> Dict[str, Any]:
        """Handle 'help' queries"""
        commands = [
            {"command": "find <entity>", "description": "Find information about an entity"},
            {"command": "path from <entity1> to <entity2>", "description": "Find the shortest path between two entities"},
            {"command": "related <entity>", "description": "Find entities related to the given entity"},
            {"command": "count entities", "description": "Count entities by type"},
            {"command": "count relations", "description": "Count relations by type"},
            {"command": "export <filename>", "description": "Export the knowledge graph to a file"},
            {"command": "help", "description": "Show this help message"},
            {"command": "exit", "description": "Exit the program"}
        ]
        
        return {
            "success": True,
            "message": "Available commands:",
            "data": {
                "commands": commands
            }
        } 