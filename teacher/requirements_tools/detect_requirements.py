#!/usr/bin/env python3
"""
Automatically detect Python package requirements by analyzing import statements.
This script scans Python files and generates a requirements.txt file.
"""

import os
import sys
import ast
import re
from pathlib import Path
from typing import Set, Dict, List
import subprocess

# Mapping of import names to PyPI package names
IMPORT_TO_PACKAGE = {
    'yaml': 'PyYAML',
    'cv2': 'opencv-python',
    'sklearn': 'scikit-learn',
    'PIL': 'Pillow',
    'bs4': 'beautifulsoup4',
    'dotenv': 'python-dotenv',
    'dateutil': 'python-dateutil',
    'azure.eventhub': 'azure-eventhub',
    'azure.identity': 'azure-identity',
    'azure.storage': 'azure-storage-blob',
    'psycopg2': 'psycopg2-binary',
    'psycopg': 'psycopg',
}

# Standard library modules (don't need to be installed)
STDLIB_MODULES = {
    'abc', 'aifc', 'argparse', 'array', 'ast', 'asynchat', 'asyncio', 'asyncore',
    'atexit', 'audioop', 'base64', 'bdb', 'binascii', 'binhex', 'bisect', 'builtins',
    'bz2', 'calendar', 'cgi', 'cgitb', 'chunk', 'cmath', 'cmd', 'code', 'codecs',
    'codeop', 'collections', 'colorsys', 'compileall', 'concurrent', 'configparser',
    'contextlib', 'contextvars', 'copy', 'copyreg', 'cProfile', 'crypt', 'csv',
    'ctypes', 'curses', 'dataclasses', 'datetime', 'dbm', 'decimal', 'difflib',
    'dis', 'distutils', 'doctest', 'email', 'encodings', 'enum', 'errno', 'faulthandler',
    'fcntl', 'filecmp', 'fileinput', 'fnmatch', 'formatter', 'fractions', 'ftplib',
    'functools', 'gc', 'getopt', 'getpass', 'gettext', 'glob', 'graphlib', 'grp',
    'gzip', 'hashlib', 'heapq', 'hmac', 'html', 'http', 'imaplib', 'imghdr', 'imp',
    'importlib', 'inspect', 'io', 'ipaddress', 'itertools', 'json', 'keyword',
    'lib2to3', 'linecache', 'locale', 'logging', 'lzma', 'mailbox', 'mailcap',
    'marshal', 'math', 'mimetypes', 'mmap', 'modulefinder', 'multiprocessing',
    'netrc', 'nis', 'nntplib', 'numbers', 'operator', 'optparse', 'os', 'ossaudiodev',
    'parser', 'pathlib', 'pdb', 'pickle', 'pickletools', 'pipes', 'pkgutil',
    'platform', 'plistlib', 'poplib', 'posix', 'posixpath', 'pprint', 'profile',
    'pstats', 'pty', 'pwd', 'py_compile', 'pyclbr', 'pydoc', 'queue', 'quopri',
    'random', 're', 'readline', 'reprlib', 'resource', 'rlcompleter', 'runpy',
    'sched', 'secrets', 'select', 'selectors', 'shelve', 'shlex', 'shutil', 'signal',
    'site', 'smtpd', 'smtplib', 'sndhdr', 'socket', 'socketserver', 'sqlite3',
    'ssl', 'stat', 'statistics', 'string', 'stringprep', 'struct', 'subprocess',
    'sunau', 'symbol', 'symtable', 'sys', 'sysconfig', 'syslog', 'tabnanny',
    'tarfile', 'telnetlib', 'tempfile', 'termios', 'test', 'textwrap', 'threading',
    'time', 'timeit', 'token', 'tokenize', 'trace', 'traceback', 'tracemalloc',
    'tty', 'turtle', 'turtledemo', 'types', 'typing', 'unicodedata', 'unittest',
    'urllib', 'uu', 'uuid', 'venv', 'warnings', 'wave', 'weakref', 'webbrowser',
    'winreg', 'winsound', 'wsgiref', 'xdrlib', 'xml', 'xmlrpc', 'zipapp', 'zipfile',
    'zipimport', 'zlib', '_thread'
}


class ImportDetector(ast.NodeVisitor):
    """AST visitor to detect import statements."""
    
    def __init__(self):
        self.imports: Set[str] = set()
    
    def visit_Import(self, node):
        """Handle 'import module' statements."""
        for alias in node.names:
            module_name = alias.name.split('.')[0]
            self.imports.add(module_name)
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node):
        """Handle 'from module import ...' statements."""
        if node.module:
            module_name = node.module.split('.')[0]
            self.imports.add(module_name)
        self.generic_visit(node)


def extract_imports_from_file(file_path: Path) -> Set[str]:
    """Extract all import statements from a Python file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content, filename=str(file_path))
        detector = ImportDetector()
        detector.visit(tree)
        return detector.imports
    except SyntaxError as e:
        print(f"⚠️  Syntax error in {file_path}: {e}", file=sys.stderr)
        return set()
    except Exception as e:
        print(f"⚠️  Error reading {file_path}: {e}", file=sys.stderr)
        return set()


def find_python_files(directory: Path, exclude_dirs: Set[str] = None) -> List[Path]:
    """Recursively find all Python files in a directory."""
    if exclude_dirs is None:
        exclude_dirs = {'venv', '.venv', 'env', '.env', '__pycache__', 
                       '.git', 'node_modules', 'dist', 'build', '.ipynb_checkpoints',
                       'myenv', 'logs', 'files', 'test', 'tests', 'solutions'}
    
    python_files = []
    for root, dirs, files in os.walk(directory):
        # Remove excluded directories from the search
        dirs[:] = [d for d in dirs if d not in exclude_dirs and not d.startswith('.')]
        
        for file in files:
            if file.endswith('.py') and not file.startswith('.'):
                python_files.append(Path(root) / file)
    
    return python_files


def get_package_name(import_name: str) -> str:
    """Convert import name to PyPI package name."""
    # Check custom mappings first
    if import_name in IMPORT_TO_PACKAGE:
        return IMPORT_TO_PACKAGE[import_name]
    
    # Check for nested imports
    for key, value in IMPORT_TO_PACKAGE.items():
        if import_name.startswith(key + '.'):
            return value
    
    # Default: assume package name is same as import name
    return import_name


def get_installed_version(package_name: str) -> str:
    """Get the installed version of a package."""
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'show', package_name],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                if line.startswith('Version:'):
                    return line.split(':', 1)[1].strip()
    except Exception:
        pass
    return None


def detect_requirements(directory: Path, output_file: str = None, 
                       include_versions: bool = True) -> Dict[str, str]:
    """
    Detect all required packages from Python files in a directory.
    
    Args:
        directory: Directory to scan for Python files
        output_file: Output file path (default: requirements.txt in directory)
        include_versions: Whether to include version numbers
    
    Returns:
        Dictionary mapping package names to versions (or empty string)
    """
    print(f"🔍 Scanning Python files in: {directory}")
    
    # Find all Python files
    python_files = find_python_files(directory)
    print(f"📄 Found {len(python_files)} Python file(s)")
    
    # Extract imports from all files
    all_imports = set()
    for py_file in python_files:
        imports = extract_imports_from_file(py_file)
        all_imports.update(imports)
    
    # Filter out standard library modules and local imports
    third_party_imports = set()
    for imp in all_imports:
        if imp not in STDLIB_MODULES and not imp.startswith('_'):
            third_party_imports.add(imp)
    
    print(f"📦 Found {len(third_party_imports)} third-party import(s)")
    
    # Convert to package names and get versions
    requirements = {}
    for import_name in sorted(third_party_imports):
        package_name = get_package_name(import_name)
        
        if include_versions:
            version = get_installed_version(package_name)
            if version:
                requirements[package_name] = version
                print(f"  ✓ {package_name}=={version}")
            else:
                requirements[package_name] = ""
                print(f"  ⚠ {package_name} (version unknown)")
        else:
            requirements[package_name] = ""
            print(f"  ✓ {package_name}")
    
    # Write to requirements file
    if output_file is None:
        output_file = directory / 'requirements.txt'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Auto-generated requirements file\n")
        f.write("# Generated by detect_requirements.py\n\n")
        
        for package, version in sorted(requirements.items()):
            if version and include_versions:
                f.write(f"{package}=={version}\n")
            else:
                f.write(f"{package}\n")
    
    print(f"\n✅ Requirements written to: {output_file}")
    return requirements


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Detect Python package requirements from source files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scan current directory
  python detect_requirements.py
  
  # Scan specific directory
  python detect_requirements.py /path/to/project
  
  # Specify output file
  python detect_requirements.py -o my_requirements.txt
  
  # Without version pinning
  python detect_requirements.py --no-versions
        """
    )
    
    parser.add_argument(
        'directory',
        nargs='?',
        default='.',
        help='Directory to scan (default: current directory)'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Output file path (default: requirements.txt in scanned directory)'
    )
    
    parser.add_argument(
        '--no-versions',
        action='store_true',
        help='Do not include version numbers'
    )
    
    args = parser.parse_args()
    
    directory = Path(args.directory).resolve()
    
    if not directory.exists():
        print(f"❌ Error: Directory not found: {directory}", file=sys.stderr)
        sys.exit(1)
    
    if not directory.is_dir():
        print(f"❌ Error: Not a directory: {directory}", file=sys.stderr)
        sys.exit(1)
    
    try:
        detect_requirements(
            directory=directory,
            output_file=args.output,
            include_versions=not args.no_versions
        )
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
