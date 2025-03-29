# API Reference

This section provides detailed documentation for LlamaGraph's API. Each module is described with its classes, methods, and functions.

## Core Modules

- [Config](./config.md): Configuration system for LlamaGraph
- [CLI](./cli.md): Command-line interface

## Extraction

- [Entity Extractor](./entity_extractor.md): Extract entities from text
- [Relation Extractor](./relation_extractor.md): Extract relationships between entities

## Graph

- [Knowledge Graph](./knowledge_graph.md): Core knowledge graph implementation
- [Query Engine](./query_engine.md): Tools for querying the knowledge graph

## UI

- [Terminal](./terminal.md): Terminal user interface
- [Animations](./animations.md): Animations for the terminal UI
- [Colors](./colors.md): Color schemes for the terminal UI

## Utilities

- [Cache](./cache.md): Caching system for improved performance
- [MLX Utils](./mlx_utils.md): MLX acceleration utilities
- [Threading](./threading.md): Multi-threading utilities
- [Visualization](./visualization.md): Knowledge graph visualization tools

## Class Hierarchy

```
llamagraph
├── config
│   └── LlamaGraphConfig
├── extractor
│   ├── entity_extractor
│   │   ├── Entity
│   │   └── EntityExtractor
│   └── relation_extractor
│       ├── Relation
│       └── RelationExtractor
├── graph
│   ├── knowledge_graph
│   │   └── KnowledgeGraph
│   └── query_engine
│       └── QueryEngine
├── ui
│   ├── animations
│   ├── colors
│   └── terminal
│       └── LlamaGraphTerminal
└── utils
    ├── cache
    │   └── Cache
    ├── mlx_utils
    │   └── MLXProcessor
    ├── threading
    │   └── parallel_process
    └── visualization
        ├── plot_knowledge_graph
        ├── create_interactive_graph
        └── export_graph_to_formats
``` 