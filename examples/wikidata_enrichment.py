#!/usr/bin/env python3
"""
Example demonstrating how to enrich a knowledge graph with data from Wikidata
"""
import os
from pathlib import Path
import json

from llamagraph.config import LlamaGraphConfig
from llamagraph.utils.cache import Cache
from llamagraph.extractor.entity_extractor import EntityExtractor
from llamagraph.extractor.relation_extractor import RelationExtractor
from llamagraph.graph.knowledge_graph import KnowledgeGraph
from llamagraph.graph.query_engine import QueryEngine
from llamagraph.api.wikidata import WikidataEnricher
from llamagraph.utils.visualization import (
    create_interactive_graph,
    create_knowledge_map
)

def print_section(title):
    """Print a section title with formatting"""
    print(f"\n{'=' * 40}")
    print(f"  {title}")
    print(f"{'=' * 40}\n")

def main():
    """
    Create a knowledge graph, enrich it with Wikidata data, and visualize the results
    """
    # Initialize components
    config = LlamaGraphConfig()
    cache = Cache(config.cache_dir, config.max_size)
    entity_extractor = EntityExtractor(config, cache)
    relation_extractor = RelationExtractor(config, cache)
    kg = KnowledgeGraph()
    
    # Sample text about technology companies for the knowledge graph
    text = """
    OpenAI was founded in 2015 by Elon Musk, Sam Altman, and others. 
    It created ChatGPT, a language model that became widely used in 2022.
    OpenAI is based in San Francisco, California.
    
    DeepMind was founded by Demis Hassabis in 2010.
    Google acquired DeepMind in 2014. DeepMind created AlphaGo, which defeated Lee Sedol in Go.
    DeepMind is headquartered in London, United Kingdom.
    """
    
    print_section("Creating Knowledge Graph")
    
    # Extract entities
    print("Extracting entities...")
    entities = entity_extractor.extract(text)
    print(f"Found {len(entities)} entities:")
    for entity in entities:
        print(f"  - {entity.text} ({entity.entity_type})")
    
    # Extract relations
    print("\nExtracting relationships...")
    relations = relation_extractor.extract(text, entities)
    print(f"Found {len(relations)} relationships:")
    for relation in relations:
        print(f"  - {relation.source.text} --{relation.relation_type}--> {relation.target.text}")
    
    # Build the knowledge graph
    print("\nBuilding knowledge graph...")
    for entity in entities:
        kg.add_entity(entity)
    
    for relation in relations:
        kg.add_relation(relation)
    
    print(f"Knowledge graph built with {len(kg.entities)} entities and {len(kg.relations)} relations.")
    
    # Create output directory if it doesn't exist
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    # Create a visualization before enrichment
    try:
        print("\nCreating visualization before enrichment...")
        before_path = output_dir / "graph_before_enrichment.html"
        create_interactive_graph(
            kg.graph,
            title="Knowledge Graph (Before Wikidata Enrichment)",
            save_path=before_path
        )
        print(f"Visualization saved to {before_path}")
    except Exception as e:
        print(f"Could not create visualization: {e}")
    
    print_section("Enriching Knowledge Graph with Wikidata")
    
    # Create a Wikidata enricher
    wikidata_enricher = WikidataEnricher(user_agent="LlamaGraph_Example/1.0.0")
    
    # Enrich entities with Wikidata data
    print("Enriching entities with Wikidata data...")
    wikidata_enricher.enrich_knowledge_graph(kg)
    
    # Find additional relations from Wikidata
    print("\nFinding additional relations from Wikidata...")
    new_relations = wikidata_enricher.find_additional_relations(kg)
    
    print(f"Found {len(new_relations)} additional relations from Wikidata:")
    for rel in new_relations:
        print(f"  - {rel['source']} --{rel['relation_type']}--> {rel['target']}")
        
        # Add the new relation to the graph
        source_entity = kg.get_entity(rel['source'])
        target_entity = kg.get_entity(rel['target'])
        
        if source_entity and target_entity:
            from llamagraph.extractor.relation_extractor import Relation
            new_relation = Relation(
                source=source_entity,
                relation_type=rel['relation_type'],
                target=target_entity,
                sentence=rel['sentence']
            )
            kg.add_relation(new_relation)
    
    # Save the enriched knowledge graph
    enriched_path = output_dir / "enriched_graph.json"
    kg.save(str(enriched_path))
    print(f"\nEnriched knowledge graph saved to {enriched_path}")
    
    print_section("Exploring Enriched Knowledge Graph")
    
    # Print Wikidata attributes for each entity
    print("Entity attributes from Wikidata:")
    for entity_text, entity in kg.entities.items():
        node_data = kg.graph.nodes[entity_text]
        wikidata_attrs = {k: v for k, v in node_data.items() if k.startswith("wikidata_")}
        
        if wikidata_attrs:
            print(f"\n  Entity: {entity_text} ({entity.entity_type})")
            for key, value in wikidata_attrs.items():
                # Format the key for better readability
                nice_key = key.replace("wikidata_", "").replace("_", " ").title()
                
                # Format the value
                if isinstance(value, list):
                    if len(value) == 1:
                        display_value = value[0]
                    else:
                        display_value = ", ".join(str(v) for v in value)
                else:
                    display_value = value
                
                print(f"    - {nice_key}: {display_value}")
    
    # Create visualizations of the enriched graph
    try:
        print("\nCreating visualizations of the enriched graph...")
        
        # Interactive graph
        after_path = output_dir / "graph_after_enrichment.html"
        create_interactive_graph(
            kg.graph,
            title="Knowledge Graph (After Wikidata Enrichment)",
            save_path=after_path
        )
        print(f"Interactive visualization saved to {after_path}")
        
        # Knowledge map (hierarchical visualization)
        map_path = output_dir / "knowledge_map_enriched.html"
        create_knowledge_map(
            kg.graph,
            title="Enriched Knowledge Map",
            save_path=map_path
        )
        print(f"Knowledge map saved to {map_path}")
        
    except Exception as e:
        print(f"Could not create visualizations: {e}")
    
    print("\nDone! Check the 'output' directory for the saved files.")
    print("\nNotes on Wikidata enrichment:")
    print("  1. Wikidata integration adds descriptions, aliases, and property data to entities")
    print("  2. Additional relations between entities can be discovered via Wikidata")
    print("  3. The enriched graph has more semantic context that can be used for analysis")
    print("  4. Wikidata IDs allow linking to other external knowledge bases")

if __name__ == "__main__":
    main() 