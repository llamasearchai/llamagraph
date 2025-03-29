# LlamaGraph Repository Summary

## Overview
LlamaGraph is a llama-themed knowledge graph construction tool that extracts entities and relationships from text and builds a queryable knowledge graph. It enables users to process unstructured text data, extract meaningful information, and represent it in a structured format that can be queried and analyzed.

## Core Features
- Entity extraction using SpaCy with optional MLX acceleration
- Relationship extraction between entities
- Knowledge graph construction using NetworkX
- Interactive query capabilities
- Graph visualization and analysis tools
- Command-line interface with llama-themed UI elements
- REST API for programmatic access

## Technical Architecture
LlamaGraph follows a modular architecture with the following core components:

1. **Entity Extraction**: Identifies named entities in text using SpaCy and custom extractors with MLX acceleration.
2. **Relation Extraction**: Identifies relationships between entities using pattern matching and dependency parsing.
3. **Knowledge Graph**: Builds and manages a graph structure to represent entities and their relationships.
4. **Query Engine**: Provides a flexible interface for querying the knowledge graph.
5. **Terminal UI**: Offers a colorful, interactive command-line interface for users.
6. **Cache System**: Optimizes performance by caching extraction results.
7. **API Server**: Exposes functionality through a REST API.

## Technical Implementation
- Written in Python 3.9+
- Uses SpaCy for NLP processing
- NetworkX for graph representation
- MLX for performance optimization on Apple Silicon
- Rich, textual, and prompt_toolkit for terminal UI
- FastAPI for the API server (optional dependency)

## Directory Structure
```
llamagraph/
├── llamagraph/             # Main package directory
│   ├── __init__.py         # Package initialization
│   ├── cli.py              # Command-line interface
│   ├── config.py           # Configuration management
│   ├── extractor/          # Entity and relation extraction
│   ├── graph/              # Knowledge graph and query engine
│   ├── ui/                 # Terminal UI components
│   ├── utils/              # Utility functions and classes
│   ├── api/                # API components
│   └── server/             # Server implementation
├── tests/                  # Test suite
├── examples/               # Example usage scripts
├── docs/                   # Documentation
├── scripts/                # Utility scripts
└── setup.py                # Package setup
```

## Usage Examples
LlamaGraph can be used in several ways:

1. **Command-line Interface**:
   ```bash
   llamagraph process -f input.txt -o graph.json
   ```

2. **Python API**:
   ```python
   from llamagraph.config import LlamaGraphConfig
   from llamagraph.extractor.entity_extractor import EntityExtractor
   from llamagraph.extractor.relation_extractor import RelationExtractor
   from llamagraph.graph.knowledge_graph import KnowledgeGraph
   
   # Initialize components
   config = LlamaGraphConfig()
   entity_extractor = EntityExtractor(config)
   relation_extractor = RelationExtractor(config)
   kg = KnowledgeGraph()
   
   # Process text
   text = "Apple was founded by Steve Jobs in 1976."
   entities = entity_extractor.extract(text)
   relations = relation_extractor.extract(text, entities)
   
   # Build knowledge graph
   for entity in entities:
       kg.add_entity(entity)
   for relation in relations:
       kg.add_relation(relation)
   
   # Query the graph
   apple = kg.get_entity("Apple")
   relations = kg.get_relations("Apple")
   ```

3. **REST API**:
   ```bash
   llamagraph serve
   ```
   Then send HTTP requests to interact with the API.

## Dependencies
- Core: spacy, networkx, rich, click
- Acceleration: mlx (on Apple Silicon)
- Visualization: matplotlib, pyvis, plotly (optional)
- API: fastapi, uvicorn (optional)

## Known Limitations
- MLX acceleration only works on Apple Silicon devices
- Some complex relationships may not be correctly extracted
- Performance may degrade with very large texts or complex graphs
- Visualization tools require additional dependencies

## Future Work
- Improved entity coreference resolution
- Enhanced relation extraction using transformer models
- More sophisticated query capabilities
- Graph embedding for semantic similarity queries
- Integration with vector databases
- Web-based visualization interface 