# Contributing to LlamaGraph

Thank you for your interest in contributing to LlamaGraph! This document provides guidelines and instructions for contributing to this project.

## Code of Conduct

Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md). We expect all contributors to adhere to it.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR-USERNAME/llamagraph.git
   cd llamagraph
   ```
3. **Set up a development environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -e ".[dev]"
   ```
4. **Create a new branch** for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Workflow

1. **Make your changes** in your local branch
2. **Write tests** for new features or bug fixes
3. **Run the tests** to make sure everything works:
   ```bash
   pytest
   ```
4. **Format your code** using black:
   ```bash
   black llamagraph tests
   ```
5. **Check for code quality issues** with flake8:
   ```bash
   flake8 llamagraph tests
   ```
6. **Commit your changes** with a clear commit message:
   ```bash
   git commit -m "Add feature: description of your changes"
   ```
7. **Push your branch** to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```
8. **Submit a pull request** from your fork to the main repository

## Pull Request Guidelines

- Ensure your PR addresses a specific issue. If an issue doesn't exist, create one first.
- Include tests for any new functionality.
- Update documentation if necessary.
- Keep your PR focused on a single topic rather than including multiple unrelated changes.
- Make sure CI passes on your PR.

## Code Style

We follow these coding conventions:

- Use [Black](https://black.readthedocs.io/en/stable/) for code formatting
- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guidelines
- Write comprehensive docstrings using [Google style](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)

## Testing

- All code contributions should include appropriate tests.
- We use pytest for testing.
- Aim for high test coverage for new code.

## Documentation

- Update the README.md if you make changes to the project's features or usage.
- Add docstrings to all public functions, classes, and methods.
- Consider adding examples to the `examples` directory for significant features.

## Adding Dependencies

If your contribution requires new dependencies:

1. Add them to `setup.py` under `install_requires` or `extras_require`.
2. Update `requirements.txt` if necessary.
3. Explain why the new dependency is necessary in your PR.

## Reporting Bugs

When reporting bugs, please include:

- A clear and descriptive title
- Steps to reproduce the issue
- Expected vs. actual behavior
- Version information (Python, OS, etc.)
- Any relevant error messages or logs

## Feature Requests

For feature requests:

- Describe the feature in detail
- Explain why it would be valuable to the project
- Suggest possible implementations if you have ideas

## Code Review Process

All submissions require review. The maintainers will review your PR and may suggest changes, improvements, or alternative approaches.

## Recognition

All contributors will be recognized in the project's CONTRIBUTORS.md file.

## Contact

If you have questions, feel free to open an issue or contact the maintainers at info@llamagraph.com.

Thank you for contributing to LlamaGraph! 🦙 