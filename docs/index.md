# LlamaGraph Documentation

Welcome to the official documentation for LlamaGraph, a llama-themed knowledge graph construction tool.

## Introduction

LlamaGraph is a Python library for extracting knowledge graphs from text. It identifies entities and their relationships, constructing a queryable graph representation of the extracted knowledge.

## Features

- 🦙 **Llama-themed CLI**: Delightful command-line interface with colors, animations, and llama personality.
- 🔍 **Entity & Relation Extraction**: Process text to identify entities and the relationships between them.
- 📊 **Knowledge Graph Construction**: Build a structured, queryable graph representation of extracted knowledge.
- ⚡ **Performance Optimizations**: MLX acceleration for data processing and multi-threading for handling large inputs.
- 🔄 **Interactive Queries**: Find entities, discover relationships, and explore paths between concepts.
- 💾 **Import/Export**: Save and load knowledge graphs in JSON format.
- 🐳 **Docker Support**: Run LlamaGraph in a containerized environment.

## Table of Contents

- [Installation](./installation.md)
- [Quick Start](./quickstart.md)
- [Command Line Interface](./cli.md)
- [API Reference](./api/index.md)
- [Examples](./examples/index.md)
- [Development Guide](./development.md)
- [FAQ](./faq.md)
- [Contributing](./contributing.md)
- [License](./license.md)

## Getting Started

To get started with LlamaGraph, install the package:

```bash
pip install llamagraph
```

Then, you can process a text file to extract a knowledge graph:

```bash
llamagraph process -f input.txt -o graph.json
```

For more detailed instructions, check the [Quick Start](./quickstart.md) guide. 