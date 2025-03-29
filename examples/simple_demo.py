"""
Simple demo script to demonstrate the use of LlamaGraph
"""
import sys
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
    knowledge_graph = KnowledgeGraph()
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
        knowledge_graph.add_entity(entity)
    
    for relation in relations:
        knowledge_graph.add_relation(relation)
    
    terminal.display_success("Knowledge graph built successfully!")
    
    # Save the graph
    output_file = Path("tech_companies_graph.json")
    knowledge_graph.save(output_file)
    terminal.display_success(f"Knowledge graph saved to {output_file}")
    
    # Create a query engine
    query_engine = QueryEngine(knowledge_graph)
    
    # Run some example queries
    terminal.animate_typing("Running example queries...")
    
    # Find information about Apple
    apple_query = query_engine.execute_query("find Apple")
    terminal.display_query_result(apple_query)
    
    # Find path between Steve Jobs and Google
    path_query = query_engine.execute_query("path from Steve Jobs to Google")
    terminal.display_query_result(path_query)
    
    # Count entities by type
    count_query = query_engine.execute_query("count entities")
    terminal.display_query_result(count_query)
    
    # Exit message
    terminal.animate_typing("Demo completed! You can now run your own queries using the CLI.")
    terminal.animate_typing("Try: llamagraph process -t \"Your text here\"")

if __name__ == "__main__":
    main() 