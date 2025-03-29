#!/usr/bin/env python3
"""
Example demonstrating advanced knowledge graph visualizations in LlamaGraph
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
    create_3d_graph,
    create_knowledge_map,
    export_graph_to_formats
)

def main():
    """
    Create and visualize a knowledge graph with advanced 3D and hierarchical visualizations
    """
    # Initialize components
    config = LlamaGraphConfig()
    cache = Cache(config.cache_dir, config.max_size)
    entity_extractor = EntityExtractor(config, cache)
    relation_extractor = RelationExtractor(config, cache)
    kg = KnowledgeGraph()
    
    # More complex example text with various entity types
    text = """
    Apple Inc. was founded by Steve Jobs, Steve Wozniak, and Ronald Wayne in 1976 in California. 
    Steve Jobs was the CEO of Apple until 2011, and Tim Cook is the current CEO.
    Apple is headquartered in Cupertino, California and is known for products like the iPhone, iPad, and MacBook.
    
    Microsoft was founded by Bill Gates and Paul Allen in 1975 in Albuquerque, New Mexico.
    Satya Nadella is the current CEO of Microsoft, succeeding Steve Ballmer.
    Microsoft is based in Redmond, Washington and develops Windows, Office, and Azure.
    
    Google was founded by Larry Page and Sergey Brin in 1998 while they were students at Stanford University.
    Sundar Pichai is the CEO of Google, which is a subsidiary of Alphabet Inc.
    Google is headquartered in Mountain View, California and is known for its search engine, Android, and Chrome.
    
    Amazon was founded by Jeff Bezos in 1994 in Seattle, Washington. Andy Jassy became the CEO in 2021.
    Amazon is known for its e-commerce platform, AWS cloud services, and the Echo smart speaker with Alexa.
    
    Meta Platforms (formerly Facebook) was founded by Mark Zuckerberg in 2004 at Harvard University.
    Meta owns Instagram, WhatsApp, and Oculus VR. Their headquarters is in Menlo Park, California.
    
    The AI revolution includes technologies developed by these companies, such as Apple's Siri, 
    Amazon's Alexa, Google's Assistant, Microsoft's Copilot, and Meta's AI research.
    
    OpenAI was founded in 2015 by Elon Musk, Sam Altman, and others. 
    Microsoft has invested heavily in OpenAI, which created ChatGPT and DALL-E.
    """
    
    print("Processing text...")
    
    # Extract entities
    print("Extracting entities...")
    entities = entity_extractor.extract(text)
    print(f"Found {len(entities)} entities!")
    
    # Extract relations
    print("Extracting relationships...")
    relations = relation_extractor.extract(text, entities)
    print(f"Found {len(relations)} relationships!")
    
    # Build the knowledge graph
    print("Building knowledge graph...")
    for entity in entities:
        kg.add_entity(entity)
    
    for relation in relations:
        kg.add_relation(relation)
    
    # Create output directory if it doesn't exist
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    # 1. Create a static visualization
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
    
    # 2. Create a 3D interactive visualization
    print("\nCreating 3D visualization...")
    try:
        html_3d_path = output_dir / "3d_graph.html"
        html_3d_file = create_3d_graph(
            kg.graph,
            title="Interactive 3D Tech Companies Knowledge Graph",
            node_size=10,
            edge_width=2,
            save_path=html_3d_path
        )
        print(f"3D visualization saved to {html_3d_path}")
        print(f"Open this file in your browser to explore the 3D graph interactively.")
    except Exception as e:
        print(f"Could not create 3D visualization: {e}")
        print("Try installing plotly: pip install plotly")
    
    # 3. Create a hierarchical knowledge map
    print("\nCreating hierarchical knowledge map...")
    try:
        map_path = output_dir / "knowledge_map.html"
        map_file = create_knowledge_map(
            kg.graph,
            title="Hierarchical Tech Companies Knowledge Map",
            save_path=map_path
        )
        print(f"Knowledge map saved to {map_path}")
        print(f"Open this file in your browser to explore the hierarchical map.")
    except Exception as e:
        print(f"Could not create knowledge map: {e}")
        print("Try installing plotly: pip install plotly")
    
    # 4. Create a 2D interactive visualization
    print("\nCreating 2D interactive visualization...")
    try:
        html_2d_path = output_dir / "interactive_graph.html"
        html_2d_file = create_interactive_graph(
            kg.graph,
            title="Interactive Tech Companies Knowledge Graph",
            save_path=html_2d_path
        )
        print(f"2D interactive visualization saved to {html_2d_path}")
        print(f"Open this file in your browser to explore the graph.")
    except Exception as e:
        print(f"Could not create interactive visualization: {e}")
        print("Try installing pyvis: pip install pyvis")
    
    # 5. Export to various formats
    print("\nExporting graph to various formats...")
    try:
        export_base = output_dir / "tech_companies_graph"
        exports = export_graph_to_formats(
            kg.graph,
            export_base,
            formats=["json", "gexf", "graphml", "cytoscape"]
        )
        
        for fmt, path in exports.items():
            print(f"Exported to {fmt.upper()}: {path}")
    except Exception as e:
        print(f"Could not export graph: {e}")
    
    print("\nDone! Check the 'output' directory for visualization files.")
    print("\nAdvanced Visualization Tips:")
    print("-----------------------------")
    print("1. 3D Graph: Click and drag to rotate, scroll to zoom, right-click to pan")
    print("2. Knowledge Map: Click on entity types to drill down, click center to go back up")
    print("3. Interactive Graph: Drag nodes to rearrange, hover for details, scroll to zoom")
    print("4. Cytoscape Export: Can be imported into Cytoscape desktop app for advanced analysis")

if __name__ == "__main__":
    main() 