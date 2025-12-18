# data-engineering-class
Main repo for the data engineering class in AI degree at USJ

## 🔧 Tools & Utilities

### Requirements Detection Tool

Automatically detect and generate `requirements.txt` files by analyzing Python imports in your projects.

**Location**: `teacher/requirements_tools/`

#### Quick Start

**Detect requirements for current directory:**
```bash
python3 teacher/requirements_tools/detect_requirements.py
```

**Detect requirements for specific project:**
```bash
cd modelling/data_warehouse
python3 ../../teacher/requirements_tools/detect_requirements.py
```

**Update all projects at once:**
```bash
./teacher/requirements_tools/update_all_requirements.sh
```

#### Features
- 🔍 Automatically scans all Python files
- 📦 Maps import names to correct PyPI packages (e.g., `yaml` → `PyYAML`)
- 🚫 Filters out standard library modules
- 📌 Optionally includes version pinning
- 🎯 Excludes virtual environments and cache directories

For detailed documentation, see [teacher/requirements_tools/README.md](teacher/requirements_tools/README.md)

#### Examples

```bash
# Scan and generate requirements.txt
cd modelling/data_warehouse
python3 ../../teacher/requirements_tools/detect_requirements.py

# Interactive check with diff
../../teacher/requirements_tools/check_requirements.sh

# Update all projects
./teacher/requirements_tools/update_all_requirements.sh --help
```
