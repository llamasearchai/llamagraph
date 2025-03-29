#!/usr/bin/env python3
"""
Example LlamaGraph script that processes text about tech companies
and builds a knowledge graph.
"""
import json
from pathlib import Path

from llamagraph.config import LlamaGraphConfig
from llamagraph.utils.cache import Cache
from llamagraph.extractor.entity_extractor import EntityExtractor
from llamagraph.extractor.relation_extractor import RelationExtractor
from llamagraph.graph.knowledge_graph import KnowledgeGraph
from llamagraph.graph.query_engine import QueryEngine
from llamagraph.ui.terminal import LlamaGraphTerminal

def main():
    # Initialize components
    config = LlamaGraphConfig()
    cache = Cache(config.cache_dir, config.max_cache_size)
    entity_extractor = EntityExtractor(config, cache)
    relation_extractor = RelationExtractor(config, cache)
    kg = KnowledgeGraph()
    terminal = LlamaGraphTerminal()
    
    # Display welcome banner
    terminal.display_welcome()
    
    # Sample text about tech companies
    text = """
    Apple was founded by Steve Jobs, Steve Wozniak, and Ronald Wayne in 1976. 
    Steve Jobs was the CEO of Apple until 2011, and Tim Cook is the current CEO. 
    Apple is headquartered in Cupertino, California and is known for products like the iPhone and MacBook.
    
    Microsoft was founded by Bill Gates and Paul Allen in 1975. 
    Satya Nadella is the current CEO of Microsoft, succeeding Steve Ballmer. 
    Microsoft is based in Redmond, Washington and develops Windows, Office, and Azure.
    
    Google was founded by Larry Page and Sergey Brin while they were students at Stanford University. 
    Sundar Pichai is the CEO of Google, which is a subsidiary of Alphabet Inc. 
    Google is headquartered in Mountain View, California and is known for its search engine, Android, and Chrome.
    
    Amazon was founded by Jeff Bezos in 1994. Andy Jassy became the CEO in 2021, succeeding Bezos.
    Amazon is based in Seattle, Washington and specializes in e-commerce, cloud computing, and AI.
    
    Facebook, now called Meta, was founded by Mark Zuckerberg in 2004. 
    Zuckerberg remains the CEO of Meta. The company is headquartered in Menlo Park, California.
    """
    
    # Process the text
    terminal.animate_processing("Processing text...")
    
    # Extract entities
    terminal.animate_processing("Extracting entities...")
    entities = entity_extractor.extract(text)
    terminal.display_success(f"Found {len(entities)} entities!")
    
    # Extract relations
    terminal.animate_processing("Extracting relationships...")
    relations = relation_extractor.extract(text, entities)
    terminal.display_success(f"Found {len(relations)} relationships!")
    
    # Build the knowledge graph
    terminal.animate_processing("Building knowledge graph...")
    for entity in entities:
        kg.add_entity(entity)
    
    for relation in relations:
        kg.add_relation(relation)
    
    terminal.display_success("Knowledge graph built successfully!")
    
    # Save the graph
    output_file = Path("tech_companies_graph.json")
    kg.save(str(output_file))
    terminal.display_success(f"Knowledge graph saved to {output_file}")
    
    # Create query engine
    query_engine = QueryEngine(kg)
    
    # Run some example queries
    terminal.display_info("\nRunning example queries:")
    
    example_queries = [
        "find Apple",
        "find Tim Cook",
        "path from Steve Jobs to Cupertino",
        "related Google",
        "count entities",
        "count relations"
    ]
    
    for query in example_queries:
        terminal.display_info(f"\nQuery: {query}")
        result = query_engine.execute_query(query)
        
        if result["success"]:
            terminal.display_success(result["message"])
            
            # Display query-specific results
            data = result["data"]
            if data:
                if "entity" in data and "relations" in data:
                    # Display entity and its relations
                    terminal.display_entity(data["entity"])
                    terminal.display_relations(data["relations"])
                
                elif "path" in data:
                    # Display path between entities
                    terminal.display_path(data["path"])
                
                elif "counts" in data:
                    # Display counts in table format
                    terminal.display_info(f"Total: {data['total']}")
                    for k, v in data["counts"].items():
                        terminal.display_info(f"  {k}: {v}")
                
                elif "commands" in data:
                    # Display help commands
                    terminal.display_help(data["commands"])
                
                elif "direct_relations" in data and "similar_entities" in data:
                    # Display similar entities
                    if data["similar_entities"]:
                        terminal.display_info("Similar entities:")
                        for item in data["similar_entities"]:
                            terminal.display_info(f"  {item['entity']} (via {item['shared_relation_type']} to {item['via']})")
                    else:
                        terminal.display_info("No similar entities found.")
        else:
            terminal.display_error(result["message"])
    
    # Display summary
    terminal.display_graph_summary(kg)
    
    # Run interactive mode
    terminal.display_info("\nEntering interactive mode. Type 'help' for available commands or 'exit' to quit.")
    terminal.run_interactive_mode(kg)

if __name__ == "__main__":
    main() 