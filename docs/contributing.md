# Contributing to LlamaGraph

Thank you for your interest in contributing to LlamaGraph! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Environment](#development-environment)
- [Workflow](#workflow)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Documentation](#documentation)
- [Submitting Changes](#submitting-changes)
- [Review Process](#review-process)

## Code of Conduct

Please read and follow our [Code of Conduct](https://github.com/llamagraph/llamagraph/blob/main/CODE_OF_CONDUCT.md).

## Getting Started

1. **Fork the repository**: Click the Fork button at the top right of the [repository page](https://github.com/llamagraph/llamagraph).

2. **Clone your fork**:
   ```bash
   git clone https://github.com/YOUR-USERNAME/llamagraph.git
   cd llamagraph
   ```

3. **Set up the upstream remote**:
   ```bash
   git remote add upstream https://github.com/llamagraph/llamagraph.git
   ```

4. **Create a new branch** for your feature or bugfix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Environment

1. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install development dependencies**:
   ```bash
   pip install -e ".[dev]"
   ```

3. **Install pre-commit hooks** (recommended):
   ```bash
   pre-commit install
   ```

## Workflow

1. **Keep your branch up to date**:
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

2. **Make your changes**.

3. **Run tests** to ensure your changes don't break anything:
   ```bash
   pytest
   ```

4. **Check code quality**:
   ```bash
   flake8 llamagraph
   black llamagraph
   isort llamagraph
   mypy llamagraph
   ```

5. **Commit your changes** with a descriptive commit message:
   ```bash
   git add .
   git commit -m "Add feature: your feature description"
   ```

6. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a pull request** from your branch to the main repository.

## Coding Standards

We follow these coding standards:

- **PEP 8**: We use [Black](https://black.readthedocs.io/) for code formatting
- **Type hints**: All functions should include type hints
- **Docstrings**: All modules, classes, and functions should have descriptive docstrings (Google style)
- **Comments**: Use comments to explain complex parts of the code
- **Tests**: All new features should include tests

Example of good function style:

```python
def do_something(param1: str, param2: int = 0) -> bool:
    """
    Do something with the parameters.
    
    Args:
        param1: The first parameter
        param2: The second parameter (default: 0)
        
    Returns:
        True if successful, False otherwise
    
    Raises:
        ValueError: If param1 is empty
    """
    if not param1:
        raise ValueError("param1 cannot be empty")
    
    # Do something here
    return True
```

## Testing

We use pytest for testing. Write tests for all new features and bug fixes.

- **Unit tests**: Test individual functions and classes
- **Integration tests**: Test how components work together
- **Test coverage**: Aim for at least 80% test coverage

Run tests with:

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=llamagraph

# Run specific test
pytest tests/test_entity_extractor.py
```

## Documentation

Good documentation is crucial. Update or add documentation for any code changes:

- **Code docstrings**: Update docstrings for any modified code
- **README.md**: Update if you change installation, dependencies, or usage instructions
- **Documentation files**: Update relevant .md files in the docs/ directory
- **Examples**: Consider adding examples for new features

## Submitting Changes

1. Ensure all tests pass
2. Update documentation as needed
3. Commit your changes with a descriptive message
4. Push to your fork
5. Create a pull request with:
   - A clear title and description
   - Reference to any related issues
   - Description of what was changed and why
   - Mention any breaking changes

## Review Process

Once you submit a pull request:

1. The maintainers will review your code
2. Automated tests will run on GitHub Actions
3. You may need to make changes based on feedback
4. Once approved, your pull request will be merged

Thank you for contributing to LlamaGraph! Your efforts help make this project better for everyone. 