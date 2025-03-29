# LlamaGraph 🦙

A llama-themed knowledge graph construction tool that extracts entities and relationships from text and builds a queryable knowledge graph.

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Python: 3.9+](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![MLX: Optimized](https://img.shields.io/badge/MLX-Optimized-orange.svg)](https://github.com/ml-explore/mlx)

## Features

- 🦙 **Llama-themed CLI**: Delightful command-line interface with colors, animations, and llama personality.
- 🔍 **Entity & Relation Extraction**: Process text to identify entities and the relationships between them.
- 📊 **Knowledge Graph Construction**: Build a structured, queryable graph representation of extracted knowledge.
- ⚡ **Performance Optimizations**: MLX acceleration for data processing and multi-threading for handling large inputs.
- 🔄 **Interactive Queries**: Find entities, discover relationships, and explore paths between concepts.
- 💾 **Import/Export**: Save and load knowledge graphs in JSON format.
- 🐳 **Docker Support**: Run LlamaGraph in a containerized environment.

## Installation

### Using pip

```bash
pip install llamagraph
```

### From source

```bash
git clone https://github.com/llamagraph/llamagraph.git
cd llamagraph
pip install -e .
```

### Using Docker

```bash
docker pull llamagraph/llamagraph
# or build locally
docker build -t llamagraph .
```

## Quick Start

```bash
# Process text from a file
llamagraph process -f input.txt -o graph.json

# Process text directly
llamagraph process -t "Apple was founded by Steve Jobs, Steve Wozniak, and Ronald Wayne. Tim Cook is the current CEO of Apple."

# Run in interactive mode
llamagraph process
```

## Interactive Commands

Once you've built a knowledge graph, you can query it with these commands:

- `find <entity>`: View information about an entity and its relationships
- `path from <entity1> to <entity2>`: Find the shortest path between two entities
- `related <entity>`: Find entities related to the given entity
- `count entities`: Count entities by type
- `count relations`: Count relations by type
- `export <filename>`: Export the knowledge graph to a file
- `help`: Show available commands
- `exit`: Exit the program

## MLX Acceleration

LlamaGraph can use MLX for faster processing on Apple Silicon:

```bash
# Enable MLX acceleration (default)
llamagraph process --use-mlx

# Disable MLX acceleration
llamagraph process --no-mlx
```

## Using Docker

```bash
# Run interactively
docker run -it --rm llamagraph

# Process a file from your local system
docker run -it --rm -v $(pwd):/data llamagraph process -f /data/input.txt -o /data/graph.json
```

## Example Usage

Here's a complete example of how to use LlamaGraph to process a text and query the resulting knowledge graph:

```python
# example.py
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
    cache = Cache(config.cache_dir, config.max_size)
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
    kg.save(output_file)
    terminal.display_success(f"Knowledge graph saved to {output_file}")
    
    # Run interactive queries
    terminal.run_interactive_mode(kg)

if __name__ == "__main__":
    main()
```

## Architecture

LlamaGraph is built with a modular architecture:

- **Entity Extraction**: Identifies entities in text using SpaCy and optional MLX acceleration
- **Relation Extraction**: Extracts relationships between entities using pattern matching and dependency parsing
- **Knowledge Graph**: Stores and manages entities and relations using NetworkX
- **Query Engine**: Provides structured query capabilities on the knowledge graph
- **Terminal UI**: Colorful, interactive CLI with animations and user-friendly output
- **Performance Utilities**: Threading and MLX optimization modules

## Performance Considerations

LlamaGraph is optimized for efficiency, even with large inputs:

1. **MLX Acceleration**: On Apple Silicon (M1/M2/M3), MLX provides significant performance improvements for vector operations.

2. **Multi-threading**: Text processing is parallelized across multiple threads, with each thread handling a subset of sentences.

3. **Caching**: Extracted entities and relations are cached to avoid redundant processing.

4. **Memory Efficiency**: The knowledge graph is stored as a graph structure, allowing for efficient querying and traversal.

## Development

### Setup development environment

```bash
# Clone repository
git clone https://github.com/llamagraph/llamagraph.git
cd llamagraph

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"
```

### Run tests

```bash
pytest
```

### Project Structure

```
llamagraph/
├── llamagraph/
│   ├── __init__.py
│   ├── cli.py
│   ├── config.py
│   ├── extractor/
│   │   ├── __init__.py
│   │   ├── entity_extractor.py
│   │   └── relation_extractor.py
│   ├── graph/
│   │   ├── __init__.py
│   │   ├── knowledge_graph.py
│   │   └── query_engine.py
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── animations.py
│   │   ├── colors.py
│   │   └── terminal.py
│   └── utils/
│       ├── __init__.py
│       ├── cache.py
│       ├── mlx_utils.py
│       └── threading.py
└── tests/
    ├── __init__.py
    ├── test_entity_extractor.py
    ├── test_relation_extractor.py
    ├── test_knowledge_graph.py
    └── test_query_engine.py
```

## Contributing

We welcome contributions to LlamaGraph! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

LlamaGraph is released under the MIT License. See [LICENSE](LICENSE) for details.

## Acknowledgements

- The project uses [SpaCy](https://spacy.io/) for NLP processing
- Graph operations are powered by [NetworkX](https://networkx.org/)
- Terminal UI components use [Rich](https://github.com/Textualize/rich) and [Textual](https://github.com/Textualize/textual)
- Optional acceleration with [MLX](https://github.com/ml-explore/mlx) on Apple Silicon
- Llamas for inspiration 🦙 