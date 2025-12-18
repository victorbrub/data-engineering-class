# Requirements Detection Tools

Automated Python requirements detection and management system for the Data Engineering class.

## 📁 Module Contents

### Executable Tools
- **`detect_requirements.py`** - Core detection script
- **`check_requirements.sh`** - Interactive checker with diff comparison
- **`update_all_requirements.sh`** - Batch processor for multiple projects
- **`setup_with_requirements.sh.example`** - Integration example

### Documentation
- **`REQUIREMENTS_DETECTOR.md`** - Full documentation
- **`REQUIREMENTS_QUICK_REFERENCE.md`** - Quick command reference
- **`REQUIREMENTS_SYSTEM_SUMMARY.md`** - Complete overview
- **`REQUIREMENTS_VISUAL_GUIDE.md`** - Visual guide with diagrams

## 🚀 Quick Start

### For Teachers

```bash
# Update requirements for all student projects
cd /path/to/data-engineering-class
./teacher/requirements_tools/update_all_requirements.sh
```

### For Students

```bash
# Detect requirements in current project
cd your_project/
python3 ../../teacher/requirements_tools/detect_requirements.py

# Interactive check with diff
../../teacher/requirements_tools/check_requirements.sh
```

## 📖 Usage Examples

### Detect Requirements for a Single Project

```bash
cd modelling/data_warehouse
python3 ../../teacher/requirements_tools/detect_requirements.py
```

### Check and Compare Requirements

```bash
cd modelling/python-etlfact-dim
../../teacher/requirements_tools/check_requirements.sh
```

### Batch Update All Projects

```bash
# From repository root
./teacher/requirements_tools/update_all_requirements.sh
```

## 🔧 Integration

### In Project Setup Scripts

```bash
# In modelling/data_warehouse/setup.sh
TOOLS_DIR="../../teacher/requirements_tools"

echo "Detecting requirements..."
python3 "${TOOLS_DIR}/detect_requirements.py"

echo "Installing requirements..."
pip install -r requirements.txt
```

### For Grading/Review

```bash
# Check all student submissions
for dir in submissions/*/; do
    echo "Checking $dir"
    cd "$dir"
    python3 /path/to/teacher/requirements_tools/detect_requirements.py
    cd -
done
```

## 📚 Documentation

- **Getting Started**: See `REQUIREMENTS_SYSTEM_SUMMARY.md`
- **Command Reference**: See `REQUIREMENTS_QUICK_REFERENCE.md`
- **Visual Guide**: See `REQUIREMENTS_VISUAL_GUIDE.md`
- **Full Details**: See `REQUIREMENTS_DETECTOR.md`

## ✨ Features

- 🔍 Automatic import detection via AST parsing
- 📦 Smart package name mapping (e.g., `yaml` → `PyYAML`)
- 🚫 Standard library filtering
- 📌 Optional version pinning
- 🎯 Directory exclusion (venv, __pycache__, etc.)
- 📊 Diff comparison with existing requirements
- 🔄 Batch processing for multiple projects

## 🎓 Teaching Use Cases

1. **Environment Setup**: Ensure all students have correct dependencies
2. **Project Grading**: Verify submitted code has proper requirements
3. **Onboarding**: Help new students understand dependency management
4. **Troubleshooting**: Quickly identify missing packages in student code
5. **Best Practices**: Teach proper requirements.txt management

## 🛠️ Maintenance

### Adding Package Mappings

Edit `detect_requirements.py` line 28-42:

```python
IMPORT_TO_PACKAGE = {
    'yaml': 'PyYAML',
    'your_import': 'actual-pypi-package',
    # Add more mappings here
}
```

### Configuring Projects for Batch Update

Edit `update_all_requirements.sh` to add/remove projects:

```bash
declare -A projects=(
    ["Project Name"]="relative/path/to/project"
    ["New Project"]="path/to/new/project"
)
```

## 📞 Support

For help with any tool:
```bash
python3 detect_requirements.py --help
./check_requirements.sh --help
./update_all_requirements.sh --help
```

## 📄 License

Part of the USJ AI Data Engineering Class materials.

---

**Location**: `teacher/requirements_tools/`  
**Purpose**: Simplify Python dependency management  
**Audience**: Teachers and students in the data engineering class
