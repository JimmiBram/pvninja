# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build and Run Commands
- Setup with Poetry: `poetry install`
- Run application: `poetry run python app/main.py`
- Run electricity price module: `poetry run python app/elpriser.py`
- Add new dependency: `poetry add <package-name>`
- Add dependency with version constraints: `poetry add "<package-name@^x.y.z>"`
- Update dependencies: `poetry update`

## Code Style Guidelines
- Python 3.13+ compatible code (compatible with <4.0)
- Use type hints for function parameters and return values
- Comment complex algorithms and business logic
- Use descriptive variable and function names in English
- Handle exceptions properly with specific exception types
- Error messages in Danish (user-facing strings)
- Organize imports: standard library, then third-party, then local
- Variables for configuration values and MQTT topics
- Follow PEP 8 style guidelines
- Use f-strings for string formatting

## Project Structure
- `/app`: Python application code (main package)
  - `main.py`: Core MQTT service
  - `elpriser.py`: Electricity price utilities

## Dependency Management
- Always specify Python version constraints in pyproject.toml as `>=3.13,<4.0`
- Use environment markers for Python-version specific dependencies
- Check available package versions with `pip index versions <package-name>`
- Example: `"package (>=1.0.0,<2.0.0); python_version >= '3.13' and python_version < '4.0'"`
- For nordpool specifically, use version constraint `(>=0.4.5,<0.5.0)`
- Project uses `package-mode = false` in pyproject.toml (dependency management only)
- This project doesn't need to be installed as a package