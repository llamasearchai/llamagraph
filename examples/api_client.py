#!/usr/bin/env python3
"""
Example client for the LlamaGraph API server
"""
import sys
import json
import argparse
from pathlib import Path
import requests
import webbrowser
import time

def print_section(title):
    """Print a section title with dividers"""
    print(f"\n{'=' * 50}")
    print(f" {title}")
    print(f"{'=' * 50}\n")

def process_text(api_url, text):
    """Process text to create a knowledge graph"""
    print_section("Processing Text")
    print(f"Text: {text}")
    
    # Send the request to process the text
    url = f"{api_url}/process"
    response = requests.post(
        url,
        json={"text": text, "use_mlx": True, "num_threads": 4}
    )
    
    # Check for success
    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
        return None
    
    # Get the response
    result = response.json()
    
    if not result["success"]:
        print(f"Error: {result['message']}")
        return None
    
    # Print summary
    print("\nSuccess!")
    print(f"Graph ID: {result['graph_id']}")
    print(f"Message: {result['message']}")
    
    # Print entity and relation counts
    entities = result["knowledge_graph"]["entities"]
    relations = result["knowledge_graph"]["relations"]
    
    print(f"\nEntities ({len(entities)}):")
    for entity in entities[:5]:  # Show first 5 entities
        print(f"  - {entity['text']} ({entity['entity_type']})")
    
    if len(entities) > 5:
        print(f"  ... and {len(entities) - 5} more")
    
    print(f"\nRelations ({len(relations)}):")
    for relation in relations[:5]:  # Show first 5 relations
        print(f"  - {relation['source']} --{relation['relation_type']}--> {relation['target']}")
    
    if len(relations) > 5:
        print(f"  ... and {len(relations) - 5} more")
    
    return result["graph_id"]

def query_graph(api_url, graph_id, query):
    """Query a knowledge graph"""
    print_section(f"Querying Graph: {graph_id}")
    print(f"Query: {query}")
    
    # Send the request to query the graph
    url = f"{api_url}/query/{graph_id}"
    response = requests.post(
        url,
        json={"query": query}
    )
    
    # Check for success
    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
        return None
    
    # Get the response
    result = response.json()
    
    if not result["success"]:
        print(f"Error: {result['message']}")
        return None
    
    # Print result
    print("\nSuccess!")
    print(f"Message: {result['message']}")
    
    # Print data if present
    if result["data"]:
        print("\nResults:")
        # Format the JSON response for better readability
        formatted_json = json.dumps(result["data"], indent=2)
        print(formatted_json)
    
    return result

def visualize_graph(api_url, graph_id, viz_type="interactive"):
    """Visualize a knowledge graph"""
    print_section(f"Visualizing Graph: {graph_id}")
    print(f"Visualization Type: {viz_type}")
    
    # Get the visualization URL
    url = f"{api_url}/visualize/{graph_id}?visualization_type={viz_type}"
    
    # Open in a web browser
    print(f"Opening visualization in web browser: {url}")
    webbrowser.open(url)
    
    # Give the user time to see the visualization
    print("\nPress Enter to continue...")
    input()

def export_graph(api_url, graph_id, export_format="json"):
    """Export a knowledge graph"""
    print_section(f"Exporting Graph: {graph_id}")
    print(f"Format: {export_format}")
    
    # Get the export URL
    url = f"{api_url}/export/{graph_id}?format={export_format}"
    response = requests.get(url)
    
    # Check for success
    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
        return None
    
    # Save the graph to a file
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    # Determine the file extension based on the format
    if export_format == "json":
        ext = ".json"
    elif export_format == "gexf":
        ext = ".gexf"
    elif export_format == "graphml":
        ext = ".graphml"
    elif export_format == "cytoscape":
        ext = ".cyjs"
    else:
        ext = ".txt"
    
    output_file = output_dir / f"exported_graph_{graph_id}{ext}"
    
    with open(output_file, "wb") as f:
        f.write(response.content)
    
    print(f"\nGraph exported to: {output_file}")
    return output_file

def main():
    """
    Run the LlamaGraph API client example
    """
    parser = argparse.ArgumentParser(description="LlamaGraph API Client Example")
    parser.add_argument(
        "--api-url", default="http://localhost:8000",
        help="URL of the LlamaGraph API server (default: http://localhost:8000)"
    )
    parser.add_argument(
        "--graph-id", help="Existing graph ID to use instead of creating a new one"
    )
    args = parser.parse_args()
    
    api_url = args.api_url.rstrip("/")
    
    print(f"LlamaGraph API Client Example\n")
    print(f"API Server: {api_url}")
    
    # Check if the API server is running
    try:
        requests.get(api_url, timeout=2)
    except requests.RequestException:
        print(f"Error: Could not connect to the API server at {api_url}")
        print("Make sure the server is running with: llamagraph serve")
        return
    
    # Use an existing graph ID or create a new one by processing text
    graph_id = args.graph_id
    if not graph_id:
        # Sample text for processing
        sample_text = """
        OpenAI was founded in 2015 by Elon Musk, Sam Altman, and others. 
        It created ChatGPT, a language model that became widely used in 2022.
        OpenAI is based in San Francisco, California.
        
        DeepMind was founded by Demis Hassabis in 2010.
        Google acquired DeepMind in 2014. DeepMind created AlphaGo, which defeated Lee Sedol in Go.
        DeepMind is headquartered in London, United Kingdom.
        """
        
        # Process the text to create a knowledge graph
        graph_id = process_text(api_url, sample_text)
        if not graph_id:
            print("Failed to create a knowledge graph. Exiting.")
            return
    
    # Run some example queries
    queries = [
        "find OpenAI",
        "find DeepMind",
        "path from Elon Musk to Google",
        "count entities",
        "related Google"
    ]
    
    for query in queries:
        result = query_graph(api_url, graph_id, query)
        time.sleep(1)  # Slight pause between queries
    
    # Visualize the graph in different ways
    for viz_type in ["interactive", "3d", "map"]:
        visualize_graph(api_url, graph_id, viz_type)
    
    # Export the graph in different formats
    for export_format in ["json", "gexf", "graphml", "cytoscape"]:
        export_graph(api_url, graph_id, export_format)
    
    print_section("Done!")
    print("This example demonstrated how to use the LlamaGraph API to:")
    print("  1. Process text to create a knowledge graph")
    print("  2. Query the knowledge graph in different ways")
    print("  3. Visualize the knowledge graph using different visualizations")
    print("  4. Export the knowledge graph in different formats")
    print("\nCheck the 'output' directory for the exported files.")

if __name__ == "__main__":
    main() 