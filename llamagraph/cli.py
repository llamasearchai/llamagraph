"""
Command-line interface for LlamaGraph
"""
import os
import sys
import json
import logging
import click
from pathlib import Path
from typing import Optional, List, Dict, Any

from rich.console import Console
from rich.logging import RichHandler
from rich.prompt import Prompt, Confirm

from llamagraph.config import DEFAULT_CONFIG
from llamagraph.ui.terminal import LlamaGraphTerminal
from llamagraph.extractor.entity_extractor import EntityExtractor
from llamagraph.extractor.relation_extractor import RelationExtractor
from llamagraph.graph.knowledge_graph import KnowledgeGraph
from llamagraph.utils.cache import Cache

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)
logger = logging.getLogger("llamagraph")

# Create console for output
console = Console()

@click.group()
@click.version_option()
def cli():
    """LlamaGraph - A llama-themed knowledge graph construction tool from text"""
    pass

@cli.command()
@click.option("--input-text", "-t", help="Input text for processing")
@click.option("--input-file", "-f", type=click.Path(exists=True), help="Input file for processing")
@click.option("--output-file", "-o", type=click.Path(), help="Output file for saving the knowledge graph")
@click.option("--threads", "-n", type=int, default=DEFAULT_CONFIG.num_threads, help="Number of threads to use")
@click.option("--use-mlx/--no-mlx", default=DEFAULT_CONFIG.use_mlx, help="Use MLX for acceleration")
@click.option("--interactive/--non-interactive", default=True, help="Run in interactive mode")
def process(
    input_text: Optional[str],
    input_file: Optional[str],
    output_file: Optional[str],
    threads: int,
    use_mlx: bool,
    interactive: bool,
):
    """Process text to extract entities and relations"""
    # Create the terminal UI
    terminal = LlamaGraphTerminal()
    
    # Display welcome banner
    terminal.display_welcome()
    
    # Configure settings
    config = DEFAULT_CONFIG
    config.num_threads = threads
    config.use_mlx = use_mlx
    
    # Initialize components
    cache = Cache(config.cache_dir, config.max_cache_size)
    entity_extractor = EntityExtractor(config, cache)
    relation_extractor = RelationExtractor(config, cache)
    knowledge_graph = KnowledgeGraph()
    
    # Get input text
    if not input_text and not input_file:
        if interactive:
            terminal.animate_typing("Enter text to analyze (or '@load <filename>' to load from a file):")
            input_text = Prompt.ask("🦙")
            
            # Check if user wants to load from file
            if input_text.startswith("@load "):
                filename = input_text[6:].strip()
                if os.path.exists(filename):
                    with open(filename, "r") as f:
                        input_text = f.read()
                    terminal.animate_typing(f"Loaded text from {filename}")
                else:
                    terminal.display_error(f"File not found: {filename}")
                    return
        else:
            terminal.display_error("Error: Either --input-text or --input-file must be provided in non-interactive mode")
            return
    
    # Load from file if specified
    if input_file:
        with open(input_file, "r") as f:
            input_text = f.read()
    
    # Process the text
    terminal.animate_processing("Processing text...")
    
    # Extract entities
    terminal.animate_processing("Extracting entities...")
    entities = entity_extractor.extract(input_text)
    terminal.display_success(f"Found {len(entities)} entities!")
    
    # Extract relations
    terminal.animate_processing("Extracting relationships...")
    relations = relation_extractor.extract(input_text, entities)
    terminal.display_success(f"Found {len(relations)} relationships!")
    
    # Build the knowledge graph
    terminal.animate_processing("Building knowledge graph...")
    for entity in entities:
        knowledge_graph.add_entity(entity)
    
    for relation in relations:
        knowledge_graph.add_relation(relation)
    
    terminal.display_success("Knowledge graph built successfully!")
    
    # Save graph if output file specified
    if output_file:
        with open(output_file, "w") as f:
            json.dump(knowledge_graph.to_dict(), f, indent=2)
        terminal.display_success(f"Knowledge graph saved to {output_file}")
    
    # Run interactive query mode
    if interactive:
        terminal.run_interactive_mode(knowledge_graph)
    else:
        # Print summary in non-interactive mode
        terminal.display_graph_summary(knowledge_graph)

@cli.command()
@click.option("--host", default="0.0.0.0", help="Host to bind the server to")
@click.option("--port", "-p", default=8000, help="Port to run the server on")
def serve(host: str, port: int):
    """Start the LlamaGraph REST API server"""
    try:
        # Try to import the server module
        from llamagraph.server.api import start_api_server, HAS_FASTAPI
        
        if not HAS_FASTAPI:
            console.print("[red]Error: FastAPI is required for the REST API server[/red]")
            console.print("Install with: pip install fastapi uvicorn")
            return
        
        console.print(f"[green]Starting LlamaGraph API server on http://{host}:{port}[/green]")
        console.print("Press Ctrl+C to stop the server")
        
        # Start the server
        start_api_server(host=host, port=port)
        
    except ImportError as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        console.print("Required packages for the REST API server are not installed.")
        console.print("Install with: pip install fastapi uvicorn")
        return

def main():
    """Main entry point for the CLI"""
    try:
        cli()
    except KeyboardInterrupt:
        console.print("\n🦙 [yellow]Goodbye! The llama waves farewell.[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n🦙 [red]Oops! The llama stumbled:[/red] {str(e)}")
        if "--debug" in sys.argv:
            console.print_exception()
        sys.exit(1)

if __name__ == "__main__":
    main() 