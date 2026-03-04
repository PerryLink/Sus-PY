# Contributing to sus-py

## Project Status

This is currently a personal project maintained by [PerryLink](https://github.com/PerryLink). While contributions are welcome, please note that this project is primarily developed and maintained by a single person.

## How to Report Issues

If you encounter any bugs or have feature requests, please:

1. Check the [existing issues](https://github.com/PerryLink/sus-py/issues) to avoid duplicates
2. Create a new issue with a clear title and description
3. Include:
   - Your Python version
   - Your operating system
   - Steps to reproduce the issue
   - Expected vs actual behavior
   - Any relevant code samples or error messages

## Development Environment Setup

### Prerequisites

- Python 3.8 or higher
- Poetry (for dependency management)

### Setup Steps

1. Fork and clone the repository:
```bash
git clone https://github.com/PerryLink/sus-py.git
cd sus-py
```

2. Install dependencies:
```bash
poetry install
```

3. Run tests to verify setup:
```bash
poetry run pytest
```

4. Try the CLI locally:
```bash
poetry run sus tests/samples/dangerous.py
```

## Code Standards

This project follows [PEP 8](https://peps.python.org/pep-0008/) style guidelines:

- Use 4 spaces for indentation (no tabs)
- Maximum line length: 100 characters
- Use descriptive variable names
- Add docstrings for functions and classes
- Keep functions focused and concise

### Code Style Examples

**Good:**
```python
def analyze_code(code: str, rules: dict) -> List[Dict[str, Any]]:
    """Analyze Python code and return list of security issues."""
    tree = ast.parse(code)
    visitor = SecurityVisitor(rules)
    visitor.visit(tree)
    return visitor.issues
```

**Bad:**
```python
def analyze(c, r):  # Unclear parameter names
    t = ast.parse(c)
    v = SecurityVisitor(r)
    v.visit(t)
    return v.issues
```

## Pull Request Process

1. **Create a feature branch:**
```bash
git checkout -b feature/your-feature-name
```

2. **Make your changes:**
   - Write clean, readable code following PEP 8
   - Add tests for new functionality
   - Update documentation if needed

3. **Test your changes:**
```bash
# Run all tests
poetry run pytest

# Run specific test file
poetry run pytest tests/test_analyzer.py

# Check code style (optional but recommended)
poetry run flake8 src/sus_py
```

4. **Commit your changes:**
```bash
git add .
git commit -m "feat: add your feature description"
```

Use conventional commit messages:
- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation changes
- `test:` for test additions/changes
- `refactor:` for code refactoring

5. **Push to your fork:**
```bash
git push origin feature/your-feature-name
```

6. **Create a Pull Request:**
   - Go to the [sus-py repository](https://github.com/PerryLink/sus-py)
   - Click "New Pull Request"
   - Select your branch
   - Provide a clear description of your changes
   - Link any related issues

## Testing Guidelines

- Write tests for all new features
- Ensure all tests pass before submitting PR
- Aim for high code coverage
- Test both success and failure cases

Example test structure:
```python
def test_detect_dangerous_import():
    """Test detection of dangerous imports."""
    code = "import os"
    rules = get_rules('strict')
    issues = analyze_code(code, rules)
    assert len(issues) == 1
    assert issues[0]['name'] == 'os'
```

## Questions?

If you have questions about contributing, feel free to:
- Open an issue with the `question` label
- Contact the maintainer at novelnexusai@outlook.com

## License

By contributing to sus-py, you agree that your contributions will be licensed under the Apache License 2.0.

---

Thank you for contributing to sus-py! 🎉
