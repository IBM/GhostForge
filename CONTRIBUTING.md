# Contributing to GhostForge

Thank you for your interest in contributing to GhostForge! This document provides guidelines and instructions for contributing.

## 🤝 How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with:
- A clear, descriptive title
- Steps to reproduce the issue
- Expected vs actual behavior
- Your environment (OS, Python version, libvirt version)
- Relevant logs or error messages

### Suggesting Features

Feature requests are welcome! Please:
- Check if the feature has already been requested
- Clearly describe the feature and its use case
- Explain why it would be useful to most users

### Pull Requests

1. **Fork the repository** and create your branch from `main`
2. **Make your changes** following our coding standards
3. **Add tests** if applicable
4. **Update documentation** if needed
5. **Ensure tests pass** by running `pytest`
6. **Submit a pull request** with a clear description

## 🛠 Development Setup

### Prerequisites
- Python 3.8 or higher
- KVM/libvirt installed on your system
- Git

### Setup Development Environment

```bash
# Clone your fork
git clone https://github.com/yourusername/ghostforge.git
cd ghostforge

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode with dev dependencies
pip install -e ".[dev]"

# Install pre-commit hooks (optional)
pip install pre-commit
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=ghostforge --cov-report=html

# Run specific test file
pytest tests/test_specific.py

# Run with verbose output
pytest -v
```

### Code Style

We use:
- **Black** for code formatting
- **isort** for import sorting
- **flake8** for linting
- **mypy** for type checking

```bash
# Format code
black ghostforge tests

# Sort imports
isort ghostforge tests

# Check linting
flake8 ghostforge tests

# Type checking
mypy ghostforge
```

## 📝 Coding Standards

### Python Style
- Follow PEP 8 guidelines
- Use type hints where appropriate
- Write docstrings for all public functions/classes
- Keep functions focused and small
- Use meaningful variable names

### Documentation
- Update README.md for user-facing changes
- Add docstrings to new functions/classes
- Include examples for new features
- Update CHANGELOG.md

### Commit Messages
Follow conventional commits format:
```
type(scope): subject

body (optional)

footer (optional)
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Examples:
```
feat(network): add support for custom DNS servers
fix(disk): resolve overlay creation on NFS mounts
docs(readme): update installation instructions
```

## 🧪 Testing Guidelines

### Writing Tests
- Write tests for new features
- Ensure tests are isolated and repeatable
- Use descriptive test names
- Mock external dependencies (libvirt, system calls)

### Test Structure
```python
def test_feature_description():
    """Test that feature does X when Y."""
    # Arrange
    setup_test_data()
    
    # Act
    result = function_under_test()
    
    # Assert
    assert result == expected_value
```

## 📦 Release Process

Maintainers will handle releases:
1. Update version in `ghostforge/__init__.py` and `setup.py`
2. Update CHANGELOG.md
3. Create a git tag
4. Build and publish to PyPI

## 🔍 Code Review Process

All submissions require review:
- At least one maintainer approval
- All tests must pass
- Code must follow style guidelines
- Documentation must be updated

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

## 💬 Questions?

- Open an issue for questions
- Join discussions in existing issues
- Check the README for common questions

## 🙏 Thank You!

Your contributions make GhostForge better for everyone!