# AutoDPD (Automatic Dependency Detector)

[![PyPI](https://img.shields.io/pypi/v/autodpd.svg)](https://pypi.org/project/autodpd/)

AutoDPD is a Python tool that automatically analyzes Python projects to detect dependencies, determine required Python versions, and generate environment package list.

## Features

### 🔍 Automatic Dependency Detection from:
  - Python files (*.py)
  - Jupyter notebooks (*.ipynb)
  - Local imports
  - Common package aliases (e.g., 'cv2' → 'opencv-python')

### 🔧 Environment Generation:
  - environment.yml for conda
  - requirements.txt for pip

## Installation

```bash
pip install pyyaml requests packaging
pip install autodpd
```

## Tutorials
### Basic Usage
```bash
cd /path/to/your/project
autodpd # Generate Dependencies
conda env create -f environment.yml # default name: the name of current dir e.g. "project"; you can personalize your own conda env name after "name:" 
conda activate PROJECT_NAME # Enter the name in environment.yml
pip install -r requirements.txt # Ensure you installed all dependencies
```
**environment.yml:**
```yaml
name: project_name
channels:
  - defaults
  - conda-forge
dependencies:
  - python>=3.6
  - pip
  - pip:
    - matplotlib
    - numpy
    - pandas
    - scikit-learn
    - tensorflow
```

**requirements.txt:**
```
# Python >= 3.6
matplotlib
numpy
pandas
scikit-learn
tensorflow
```
----------
### Check the current version of autodpd:
```bash
autodpd -v
```
**environment.yml:**
```yaml
name: project_name
channels:
  - defaults
  - conda-forge
dependencies:
  - python>=3.6
  - pip
  - pip:
    - matplotlib==3.4.3
    - numpy==1.21.2
    - pandas==1.3.3
    - scikit-learn==0.24.2
    - tensorflow==2.6.0
```

**requirements.txt:**
```
# Python >= 3.6
matplotlib==3.4.3
numpy==1.21.2
pandas==1.3.3
scikit-learn==0.24.2
tensorflow==2.6.0
```

### Analyze specific directory:
```bash
autodpd -d /path/to/your/project
```
### Include recommended version of dependencies:
```bash
autodpd --versions
```

### Generate with a quiet output:
```bash
autodpd -q
```

### Skip saving output files:
```bash
autodpd --no-save 
```
### (Optional) Python API

```python
from autodpd import autodpd

# Initialize detector
detector = autodpd()

# Generate environment specifications
specs = detector.generate_environment(
    directory='path/to/project',
    include_versions=True
)

# Access results
python_version = specs['recommended_python_version']
dependencies = specs['dependencies']
```

## Contributions

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
