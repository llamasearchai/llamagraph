# Quick Start Guide

This guide will help you get started with LlamaGraph quickly. For more detailed information, refer to the specific documentation sections.

## Installation

First, install LlamaGraph:

```bash
pip install llamagraph
```

For more installation options, see the [Installation Guide](./installation.md).

## Command Line Interface

LlamaGraph provides a friendly command-line interface for processing text and building knowledge graphs.

### Processing Text Directly

You can process text directly from the command line:

```bash
llamagraph process -t "Apple was founded by Steve Jobs, Steve Wozniak, and Ronald Wayne in 1976. Tim Cook is the current CEO of Apple."
```

This will:
1. Extract entities (Apple, Steve Jobs, etc.)
2. Extract relationships between entities (founded, is_CEO_of, etc.)
3. Build a knowledge graph
4. Launch an interactive query mode

### Processing Text from a File

For longer texts, process from a file:

```bash
llamagraph process -f input.txt
```

### Saving the Graph

Save the knowledge graph to a file:

```bash
llamagraph process -f input.txt -o graph.json
```

### Performance Options

Use multiple threads for faster processing:

```bash
llamagraph process -f input.txt -n 8  # Use 8 threads
```

On Apple Silicon, enable or disable MLX acceleration:

```bash
# Enable MLX (default)
llamagraph process --use-mlx

# Disable MLX
llamagraph process --no-mlx
```

## Interactive Queries

After processing, LlamaGraph enters an interactive query mode where you can explore the knowledge graph.

### Finding Entities

```
🦙 > find Apple
```

This will show information about the "Apple" entity and its relationships.

### Finding Paths

Discover paths between entities:

```
🦙 > path from Steve Jobs to Tim Cook
```

### Other Commands

```
🦙 > related Apple
🦙 > count entities
🦙 > count relations
🦙 > export graph.json
🦙 > help
```

## Programmatic Usage

You can also use LlamaGraph in your Python code:

```python
from llamagraph.config import LlamaGraphConfig
from llamagraph.utils.cache import Cache
from llamagraph.extractor.entity_extractor import EntityExtractor
from llamagraph.extractor.relation_extractor import RelationExtractor
from llamagraph.graph.knowledge_graph import KnowledgeGraph
from llamagraph.graph.query_engine import QueryEngine

# Initialize components
config = LlamaGraphConfig()
cache = Cache(config.cache_dir, config.max_size)
entity_extractor = EntityExtractor(config, cache)
relation_extractor = RelationExtractor(config, cache)
kg = KnowledgeGraph()

# Process text
text = "Apple was founded by Steve Jobs, Steve Wozniak, and Ronald Wayne in 1976."
entities = entity_extractor.extract(text)
relations = relation_extractor.extract(text, entities)

# Build knowledge graph
for entity in entities:
    kg.add_entity(entity)

for relation in relations:
    kg.add_relation(relation)

# Query the graph
query_engine = QueryEngine(kg)
result = query_engine.execute_query("find Apple")
print(result)

# Save the graph
kg.save("apple_graph.json")
```

## Visualization

You can visualize your knowledge graph using the visualization utilities:

```python
from llamagraph.utils.visualization import plot_knowledge_graph, create_interactive_graph

# Create a static visualization
plot_knowledge_graph(kg.graph, title="My Knowledge Graph", save_path="graph.png")

# Create an interactive HTML visualization
create_interactive_graph(kg.graph, save_path="interactive_graph.html")
```

## Next Steps

- Learn about the [knowledge graph structure](./knowledge_graph.md)
- Explore the [API Reference](./api/index.md)
- Check out [Examples](./examples/index.md) for more use cases
- Contribute to the project by reading the [Contributing Guide](./contributing.md) 