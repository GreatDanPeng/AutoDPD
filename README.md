# AutoDPD (Automatic Dependency Detector)

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

## Usage

Generate Dependencies:
```bash
autodpd
```

Analyze specific directory:
```bash
autodpd --d /path/to/your/project
```

Check the current version of autodpd:
```bash
autodpd --v
```

Include recommended version of dependencies:
```bash
autodpd --versions
```

Generate with a quiet output:
```bash
autodpd --q
```

Skip saving output files:
```bash
autodpd --no-save 
```

Follow steps below to creat the conda enviornment with suggested packages:
```bash
conda env create -f environment.yml
conda activate PROJECT_NAME
pip install -r requirements.txt
```

### Generated Files & Tutorials

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