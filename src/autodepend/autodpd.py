import argparse
from pathlib import Path
from importlib.metadata import distributions
import sys
import importlib.util
from typing import Dict, Set, List, Tuple, Optional
import ast
import json
from packaging import version
import requests
import time
import yaml

class autodpd:
    def analyze_imports(self, file_path: Path) -> Set[str]:
        """
        Analyze a Python file and extract all import statements
        """
        with open(file_path, 'r', encoding='utf-8') as file:
            try:
                tree = ast.parse(file.read())
            except SyntaxError:
                print(f"Warning: Syntax error in {file_path}")
                return set()

        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    imports.add(name.name.split('.')[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module.split('.')[0])
        return imports

    def is_standard_library(self, module_name: str) -> bool:
        """
        Check if a module is part of the Python standard library
        """
        if module_name in sys.stdlib_module_names:
            return True
        
        # Try to find the module spec
        spec = importlib.util.find_spec(module_name)
        if spec is None:
            return False
        
        # If the module location contains 'site-packages', it's third-party
        location = spec.origin if spec.origin else ''
        return 'site-packages' not in location and 'dist-packages' not in location

    def analyze_notebook_imports(self, file_path: Path) -> Set[str]:
        """
        Analyze a Jupyter notebook and extract all import statements from code cells
        """
        imports = set()
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                notebook = json.load(file)
                
            # Extract code from all code cells
            code_cells = [
                cell['source'] 
                for cell in notebook['cells'] 
                if cell['cell_type'] == 'code'
            ]
            
            # Combine all code cells and analyze as a single Python file
            combined_code = '\n'.join(
                source if isinstance(source, str) else ''.join(source)
                for source in code_cells
            )
            
            try:
                tree = ast.parse(combined_code)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for name in node.names:
                            imports.add(name.name.split('.')[0])
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            imports.add(node.module.split('.')[0])
            except SyntaxError:
                print(f"Warning: Syntax error in notebook {file_path}")
                
        except (json.JSONDecodeError, KeyError):
            print(f"Warning: Could not parse notebook {file_path}")
        
        return imports

    def analyze_python_version_notebook(self, file_path: Path) -> Set[float]:
        """
        Analyze a Jupyter notebook to determine minimum Python version requirements
        """
        required_versions = set()
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                notebook = json.load(file)
                
            # Extract code from all code cells
            code_cells = [
                cell['source'] 
                for cell in notebook['cells'] 
                if cell['cell_type'] == 'code'
            ]
            
            # Combine all code cells and analyze as a single Python file
            combined_code = '\n'.join(
                source if isinstance(source, str) else ''.join(source)
                for source in code_cells
            )
            
            tree = ast.parse(combined_code)
            # Reuse the same version detection logic
            for node in ast.walk(tree):
                if isinstance(node, ast.AnnAssign):
                    required_versions.add(3.5)
                if isinstance(node, ast.JoinedStr):
                    required_versions.add(3.6)
                if isinstance(node, ast.ClassDef):
                    for decorator in node.decorator_list:
                        if isinstance(decorator, ast.Name) and decorator.id == 'dataclass':
                            required_versions.add(3.7)
                if isinstance(node, ast.NamedExpr):
                    required_versions.add(3.8)
                if isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr):
                    if isinstance(node.left, ast.Dict) or isinstance(node.right, ast.Dict):
                        required_versions.add(3.9)
                if hasattr(ast, 'Match') and isinstance(node, ast.Match):
                    required_versions.add(3.10)
                    
        except (json.JSONDecodeError, KeyError, SyntaxError):
            print(f"Warning: Could not analyze Python version in notebook {file_path}")
        
        return required_versions

    def detect_project_dependencies(self, directory: str = '.') -> Dict[str, List[str]]:
        """
        Detect dependencies by analyzing Python files and Jupyter notebooks in a directory
        """
        dependencies = {
            'third_party': set(),
            'standard_lib': set(),
            'unknown': set()
        }
        
        # Get all installed packages for verification
        installed_packages = {
            dist.metadata['Name'].lower(): dist.version
            for dist in distributions()
        }

        # Scan all Python files and Jupyter notebooks
        for file_path in Path(directory).rglob('*'):
            if file_path.suffix == '.py':
                imports = self.analyze_imports(file_path)
            elif file_path.suffix == '.ipynb':
                imports = self.analyze_notebook_imports(file_path)
            else:
                continue
                
            for import_name in imports:
                import_name_lower = import_name.lower()
                if self.is_standard_library(import_name):
                    dependencies['standard_lib'].add(import_name)
                elif import_name_lower in installed_packages:
                    dependencies['third_party'].add(
                        f"{import_name}=={installed_packages[import_name_lower]}"
                    )
                else:
                    dependencies['unknown'].add(import_name)

        return {
            'third_party': sorted(list(dependencies['third_party'])),
            'standard_lib': sorted(list(dependencies['standard_lib'])),
            'unknown': sorted(list(dependencies['unknown']))
        }

    def analyze_python_version(self, file_path: Path) -> Set[float]:
        """
        Analyze a Python file to determine minimum Python version requirements
        based on syntax features
        """
        with open(file_path, 'r', encoding='utf-8') as file:
            try:
                tree = ast.parse(file.read())
            except SyntaxError:
                return set()

        required_versions = set()
        
        for node in ast.walk(tree):
            # Python 3.5+: Type hints
            if isinstance(node, ast.AnnAssign):
                required_versions.add(3.5)
            
            # Python 3.6+: f-strings
            if isinstance(node, ast.JoinedStr):
                required_versions.add(3.6)
            
            # Python 3.7+: dataclasses
            if isinstance(node, ast.ClassDef):
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Name) and decorator.id == 'dataclass':
                        required_versions.add(3.7)
            
            # Python 3.8+: walrus operator
            if isinstance(node, ast.NamedExpr):
                required_versions.add(3.8)
            
            # Python 3.9+: Dictionary union operators
            if isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr):
                if isinstance(node.left, ast.Dict) or isinstance(node.right, ast.Dict):
                    required_versions.add(3.9)
            
            # Python 3.10+: match statements
            if hasattr(ast, 'Match') and isinstance(node, ast.Match):
                required_versions.add(3.10)

        return required_versions

    def get_minimum_compatible_version(package_name: str) -> Optional[str]:
        """
        Get the minimum compatible version of a package from PyPI
        """
        try:
            # Add delay to avoid hitting PyPI rate limits
            time.sleep(0.1)
            response = requests.get(f"https://pypi.org/pypi/{package_name}/json")
            if response.status_code == 200:
                releases = response.json()['releases']
                # Filter out pre-releases and sort versions
                stable_versions = [
                    ver for ver in releases.keys()
                    if not ('a' in ver or 'b' in ver or 'rc' in ver)
                ]
                if stable_versions:
                    # Sort versions and get the oldest one
                    sorted_versions = sorted(stable_versions, key=lambda x: version.parse(x))
                    return sorted_versions[0]
        except Exception as e:
            print(f"Warning: Could not fetch version info for {package_name}: {str(e)}")
        return None

    def get_python_version(self, directory: str = '.') -> float:
        """
        Get recommended Python version without generating requirements
        """
        min_python_version = 3.5  # Default minimum
        required_versions = set()
        
        # Analyze all Python files and Jupyter notebooks
        for file_path in Path(directory).rglob('*'):
            if file_path.suffix == '.py':
                file_versions = self.analyze_python_version(file_path)
            elif file_path.suffix == '.ipynb':
                file_versions = self.analyze_python_version_notebook(file_path)
            else:
                continue
                
            required_versions.update(file_versions)
        
        if required_versions:
            min_python_version = max(required_versions)
        
        return min_python_version

    def generate_base_requirements(self, directory: str = '.', output_file: str = 'base_requirements.txt') -> Dict[str, str]:
        """
        Generate and save base requirements with minimum threshold versions
        """
        python_version = self.get_python_version(directory)
        deps = self.detect_project_dependencies(directory)
        
        # Rest of the function remains the same...

    def predict_python_environment(self, directory: str = '.', generate_base_reqs: bool = True) -> Dict[str, any]:
        """
        Analyze project files to predict appropriate Python version and
        generate conda environment specifications
        """
        python_version = self.get_python_version(directory)
        deps = self.detect_project_dependencies(directory)
        
        # Create conda environment specification
        environment = {
            'recommended_python_version': python_version,
            'python_version_reasoning': [],
            'dependencies': deps,
            'conda_environment_yaml': {
                'name': Path(directory).name,
                'channels': ['defaults', 'conda-forge'],
                'dependencies': [
                    f'python>={python_version}',
                    'pip',
                    {'pip': deps['third_party']}
                ]
            }
        }
        
        # Add reasoning for Python version
        if python_version >= 3.10:
            environment['python_version_reasoning'].append("Match statements detected (Python 3.10+)")
        if python_version >= 3.9:
            environment['python_version_reasoning'].append("Dictionary union operators detected (Python 3.9+)")
        if python_version >= 3.8:
            environment['python_version_reasoning'].append("Walrus operator detected (Python 3.8+)")
        if python_version >= 3.7:
            environment['python_version_reasoning'].append("Dataclasses detected (Python 3.7+)")
        if python_version >= 3.6:
            environment['python_version_reasoning'].append("F-strings detected (Python 3.6+)")
        if python_version >= 3.5:
            environment['python_version_reasoning'].append("Type hints detected (Python 3.5+)")
        
        # Generate base requirements if requested
        if generate_base_reqs:
            environment['base_requirements'] = self.generate_base_requirements(directory)
        
        return environment

    def display_environment_report(self, env_specs: Dict[str, any]) -> None:
        """
        Display a formatted report of the environment analysis
        """
        # Python Version and Reasoning
        print(f"\nRecommended Python version: {env_specs['recommended_python_version']}")
        if env_specs['python_version_reasoning']:
            print("\nReasoning:")
            for reason in env_specs['python_version_reasoning']:
                print(f"  - {reason}")
        
        # Dependencies
        print("\nThird-party dependencies:")
        for dep in env_specs['dependencies']['third_party']:
            print(f"  - {dep}")
        
        print("\nStandard library imports:")
        for dep in env_specs['dependencies']['standard_lib']:
            print(f"  - {dep}")
        
        if env_specs['dependencies']['unknown']:
            print("\nUnknown/Uninstalled imports:")
            for dep in env_specs['dependencies']['unknown']:
                print(f"  - {dep}")
        
        # Conda Environment
        print("\nSample conda environment.yml:")
        print("name:", env_specs['conda_environment_yaml']['name'])
        print("channels:")
        for channel in env_specs['conda_environment_yaml']['channels']:
            print(f"  - {channel}")
        print("dependencies:")
        for dep in env_specs['conda_environment_yaml']['dependencies']:
            if isinstance(dep, dict):
                print("  - pip:")
                for pip_dep in dep['pip']:
                    print(f"    - {pip_dep}")
            else:
                print(f"  - {dep}")
        
        # Base Requirements Info
        print("\nBase requirements have been saved to base_requirements.txt")
        print("These represent the minimum compatible versions of each package.")
        print("Note: It's recommended to test your code with these versions before deployment.")

    def save_conda_environment(self, env_specs: Dict[str, any], output_file: str = 'environment.yml') -> None:
        """
        Save conda environment specifications to a YAML file
        """
        conda_env = {
            'name': env_specs['conda_environment_yaml']['name'],
            'channels': env_specs['conda_environment_yaml']['channels'],
            'dependencies': env_specs['conda_environment_yaml']['dependencies']
        }
        
        with open(output_file, 'w') as f:
            yaml.safe_dump(conda_env, f, default_flow_style=False, sort_keys=False)
        
        print(f"\nConda environment configuration saved to {output_file}")

def main():
    parser = argparse.ArgumentParser(
        description='Analyze Python project dependencies and generate environment specifications'
    )
    parser.add_argument(
        '-d', '--directory',
        type=str,
        default='.',
        help='Path to the Python project directory (default: current directory)'
    )
    parser.add_argument(
        '--no-base-reqs',
        action='store_true',
        help='Skip generating base_requirements.txt'
    )
    parser.add_argument(
        '--no-conda',
        action='store_true',
        help='Skip generating environment.yml'
    )
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Suppress detailed output'
    )
    
    args = parser.parse_args()
    
    detector = autodpd()
    env_specs = detector.predict_python_environment(
        directory=args.directory,
        generate_base_reqs=not args.no_base_reqs
    )
    
    if not args.quiet:
        detector.display_environment_report(env_specs)
    
    if not args.no_conda:
        detector.save_conda_environment(env_specs)

if __name__ == "__main__":
    main()
