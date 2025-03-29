#!/usr/bin/env python3
"""
Example demonstrating knowledge graph visualization in LlamaGraph
"""
import os
from pathlib import Path

from llamagraph.config import LlamaGraphConfig
from llamagraph.utils.cache import Cache
from llamagraph.extractor.entity_extractor import EntityExtractor
from llamagraph.extractor.relation_extractor import RelationExtractor
from llamagraph.graph.knowledge_graph import KnowledgeGraph
from llamagraph.utils.visualization import (
    plot_knowledge_graph, 
    create_interactive_graph,
    export_graph_to_formats
)

def main():
    """
    Create and visualize a knowledge graph from example text
    """
    # Initialize components
    config = LlamaGraphConfig()
    cache = Cache(config.cache_dir, config.max_size)
    entity_extractor = EntityExtractor(config, cache)
    relation_extractor = RelationExtractor(config, cache)
    kg = KnowledgeGraph()
    
    # Example text about tech companies
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
    
    print("Processing text...")
    
    # Extract entities
    print("Extracting entities...")
    entities = entity_extractor.extract(text)
    print(f"Found {len(entities)} entities!")
    
    # Print entities
    print("\nEntities:")
    for entity in entities:
        print(f"  - {entity.text} ({entity.entity_type})")
    
    # Extract relations
    print("\nExtracting relationships...")
    relations = relation_extractor.extract(text, entities)
    print(f"Found {len(relations)} relationships!")
    
    # Print relations
    print("\nRelations:")
    for relation in relations:
        print(f"  - {relation.source.text} --{relation.relation_type}--> {relation.target.text}")
    
    # Build the knowledge graph
    print("\nBuilding knowledge graph...")
    for entity in entities:
        kg.add_entity(entity)
    
    for relation in relations:
        kg.add_relation(relation)
    
    # Create output directory if it doesn't exist
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    # 1. Create a static matplotlib visualization
    print("\nCreating static visualization...")
    try:
        plot_path = output_dir / "knowledge_graph.png"
        plot_knowledge_graph(
            kg.graph,
            title="Tech Companies Knowledge Graph",
            node_size=1500,
            save_path=plot_path,
            show=False
        )
        print(f"Static visualization saved to {plot_path}")
    except Exception as e:
        print(f"Could not create static visualization: {e}")
        print("Try installing matplotlib: pip install matplotlib")
    
    # 2. Create an interactive HTML visualization
    print("\nCreating interactive visualization...")
    try:
        html_path = output_dir / "interactive_graph.html"
        html_file = create_interactive_graph(
            kg.graph,
            title="Interactive Tech Companies Knowledge Graph",
            save_path=html_path
        )
        print(f"Interactive visualization saved to {html_path}")
        print(f"Open this file in your browser to explore the graph.")
    except Exception as e:
        print(f"Could not create interactive visualization: {e}")
        print("Try installing pyvis: pip install pyvis")
    
    # 3. Export to various formats
    print("\nExporting graph to various formats...")
    try:
        export_base = output_dir / "tech_companies_graph"
        exports = export_graph_to_formats(
            kg.graph,
            export_base,
            formats=["json", "gexf", "graphml"]
        )
        
        for fmt, path in exports.items():
            print(f"Exported to {fmt.upper()}: {path}")
    except Exception as e:
        print(f"Could not export graph: {e}")
    
    print("\nDone! Check the 'output' directory for visualization files.")

if __name__ == "__main__":
    main() 