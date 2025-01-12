# AutoDepend

AutoDepend is a Python tool that automatically analyzes Python projects to detect dependencies, determine required Python versions, and generate environment specifications.

## Features

- 🔍 Automatic dependency detection from Python files and Jupyter notebooks
- 🐍 Python version requirement analysis based on syntax features
- 📦 Generation of base requirements with minimum versions
- 🔧 Conda environment configuration generation
- 📊 Detailed dependency report including:
  - Third-party packages
  - Standard library imports
  - Unknown/uninstalled dependencies

## Installation

```
pip install autodepend
```

## Usage

### Get the python version and conda dependencies in the current directory
```
autodepend --conda --output environment.yml
```

### Get the pip dependencies in the current directory
```
autodepend --output requirements.txt
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.