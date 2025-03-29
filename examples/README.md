# LlamaGraph Examples

This directory contains example scripts and applications demonstrating how to use LlamaGraph for various knowledge graph tasks.

## Available Examples

### 1. Simple Demo (`simple_demo.py`)

A basic demonstration of LlamaGraph's core features including entity extraction, relation extraction, and knowledge graph construction. This example processes text about tech companies and demonstrates how to query the resulting knowledge graph.

**Features demonstrated:**
- Entity extraction
- Relation extraction
- Knowledge graph building
- Basic queries
- Terminal UI

**How to run:**
```bash
python simple_demo.py
```

## Creating Your Own Knowledge Graph

To create your own knowledge graph using LlamaGraph, follow these general steps:

1. **Initialize the components**:
   ```python
   from llamagraph.config import LlamaGraphConfig
   from llamagraph.utils.cache import Cache
   from llamagraph.extractor.entity_extractor import EntityExtractor
   from llamagraph.extractor.relation_extractor import RelationExtractor
   from llamagraph.graph.knowledge_graph import KnowledgeGraph
   
   config = LlamaGraphConfig()
   cache = Cache(config.cache_dir, config.max_cache_size)
   entity_extractor = EntityExtractor(config, cache)
   relation_extractor = RelationExtractor(config, cache)
   kg = KnowledgeGraph()
   ```

2. **Extract entities and relations from text**:
   ```python
   text = "Your text here..."
   entities = entity_extractor.extract(text)
   relations = relation_extractor.extract(text, entities)
   ```

3. **Build the knowledge graph**:
   ```python
   for entity in entities:
       kg.add_entity(entity)
   
   for relation in relations:
       kg.add_relation(relation)
   ```

4. **Query the graph**:
   ```python
   from llamagraph.graph.query_engine import QueryEngine
   
   query_engine = QueryEngine(kg)
   result = query_engine.execute_query("find Apple")
   print(result)
   ```

5. **Save the graph for later use**:
   ```python
   kg.save("my_knowledge_graph.json")
   ```

## Additional Resources

For more advanced examples and detailed documentation, refer to:

- Main LlamaGraph documentation in the `/docs` directory
- API reference for each module
- The LlamaGraph tutorial series on the LlamaSearch.ai website 