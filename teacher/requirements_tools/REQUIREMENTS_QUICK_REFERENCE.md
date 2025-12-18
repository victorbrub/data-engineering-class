# Requirements Detection - Quick Reference Guide

## 📋 Overview

Three tools are available for managing Python requirements:

1. **`detect_requirements.py`** - Core tool to scan and generate requirements
2. **`check_requirements.sh`** - Interactive checker with diff comparison
3. **`update_all_requirements.sh`** - Batch update multiple projects

## 🚀 Quick Start

### Detect requirements for current directory
```bash
python3 detect_requirements.py
```

### Check requirements with comparison
```bash
./check_requirements.sh
```

### Update all projects
```bash
./update_all_requirements.sh
```

## 📖 Detailed Usage

### 1. detect_requirements.py

#### Basic Usage
```bash
# Current directory
python3 detect_requirements.py

# Specific directory
python3 detect_requirements.py /path/to/project

# With version pinning (uses installed versions)
python3 detect_requirements.py --with-versions

# Custom output file
python3 detect_requirements.py -o my_requirements.txt
```

#### Options
- `directory` - Directory to scan (default: current)
- `-o, --output` - Output file path
- `--no-versions` - Don't include version numbers (default)
- `-h, --help` - Show help message

#### Examples
```bash
# Data warehouse project
cd modelling/data_warehouse
python3 ../../detect_requirements.py

# ETL project without versions
cd modelling/python-etlfact-dim
python3 ../../detect_requirements.py --no-versions

# Data quality with custom output
cd pre-post_processing/cleaning_data_lab
python3 ../../detect_requirements.py -o packages.txt
```

### 2. check_requirements.sh

Interactive tool that compares detected requirements with existing ones.

#### Basic Usage
```bash
# Check current directory (interactive)
./check_requirements.sh

# Check specific directory
./check_requirements.sh modelling/data_warehouse

# Auto-update without prompting
./check_requirements.sh . true
```

#### Features
- ✅ Backs up existing requirements.txt
- 📊 Shows diff (new/removed packages)
- ❓ Prompts before updating (unless auto mode)
- 🔄 Restores backup if declined

#### Example Output
```
🔍 Checking Python requirements...
✓ Found existing requirements.txt
ℹ  Backed up to requirements.txt.backup
🔧 Detecting requirements from Python files...

📊 Comparing with existing requirements...
➕ New packages detected:
   - requests
   - beautifulsoup4
➖ Packages no longer detected:
   - urllib3

❓ Would you like to update requirements.txt? [y/N]
```

### 3. update_all_requirements.sh

Batch process multiple projects at once.

#### Basic Usage
```bash
# Update all configured projects
./update_all_requirements.sh

# Update specific project
./update_all_requirements.sh --project modelling/data_warehouse

# With version pinning
./update_all_requirements.sh --with-versions
```

#### Options
- `--project <path>` - Update only specific project
- `--with-versions` - Include version numbers
- `-h, --help` - Show help message

#### Example
```bash
$ ./update_all_requirements.sh

🔍 Requirements Detection Tool
==============================

📦 Processing: Data Warehouse
   Path: /path/to/modelling/data_warehouse
   
🔍 Scanning Python files...
📄 Found 1 Python file(s)
📦 Found 3 third-party import(s)
  ✓ pandas
  ✓ psycopg
  ✓ PyYAML

✅ Requirements written to: requirements.txt

✅ All projects processed!
```

## 🔧 Integration with Setup Scripts

### Method 1: Source and Call
```bash
# In your setup.sh
source ./check_requirements.sh
check_and_update_requirements "." true
```

### Method 2: Execute Before Install
```bash
# In your setup.sh
echo "Detecting requirements..."
python3 ../../detect_requirements.py

echo "Installing requirements..."
pip install -r requirements.txt
```

### Method 3: Complete Integration
See `setup_with_requirements.sh.example` for full example.

## 📝 Common Workflows

### Workflow 1: New Project Setup
```bash
# 1. Write your Python code
# 2. Detect requirements
python3 detect_requirements.py

# 3. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 4. Install requirements
pip install -r requirements.txt

# 5. Test your code
python3 main.py
```

### Workflow 2: Updating Existing Project
```bash
# 1. Check what changed
./check_requirements.sh

# 2. Review the differences
# 3. Accept or decline update

# 4. Install new packages
pip install -r requirements.txt
```

### Workflow 3: Batch Update All Projects
```bash
# 1. Update all projects
./update_all_requirements.sh

# 2. Review generated files
git diff */requirements.txt

# 3. Commit changes
git add */requirements.txt
git commit -m "Update requirements"
```

## 🎯 Project-Specific Examples

### Data Warehouse Project
```bash
cd modelling/data_warehouse
python3 ../../detect_requirements.py
# Generates: pandas, psycopg, PyYAML
```

### ETL Star Schema
```bash
cd modelling/python-etlfact-dim
python3 ../../detect_requirements.py
# Generates: pandas, other detected packages
```

### Data Quality Lab
```bash
cd pre-post_processing/cleaning_data_lab
python3 ../../detect_requirements.py
# Generates: pandas, json utilities
```

### Tab Processor
```bash
cd fundamentals/exercise2/tab_processor
python3 ../../../detect_requirements.py
# Generates: detected scraper dependencies
```

## 🐛 Troubleshooting

### Issue: "version unknown"
**Cause**: Package is imported but not installed
**Solution**: 
```bash
# Use --no-versions flag
python3 detect_requirements.py --no-versions
# OR install the package first
pip install package_name
```

### Issue: Wrong package name
**Cause**: Import name differs from PyPI name
**Solution**: Add mapping in `detect_requirements.py`:
```python
IMPORT_TO_PACKAGE = {
    'your_import': 'actual-pypi-package',
    # existing mappings...
}
```

### Issue: Package not detected
**Cause**: Dynamic import or in excluded directory
**Solution**: 
1. Check if file is in excluded directory (venv, __pycache__, etc.)
2. Use standard import syntax
3. Manually add to requirements.txt

### Issue: Too many packages
**Cause**: Scanning test files or examples
**Solution**: Move tests to `test/` directory (auto-excluded)

## 📚 Best Practices

1. **Version Pinning**
   - Development: Use `--no-versions` for flexibility
   - Production: Use `--with-versions` for reproducibility

2. **Regular Updates**
   - Run detection after adding new imports
   - Review diffs before committing

3. **Virtual Environments**
   - Always use virtual environments
   - Detect requirements with activated venv for versions

4. **Git Integration**
   ```bash
   # Before committing
   python3 detect_requirements.py
   git add requirements.txt
   git commit -m "Update requirements"
   ```

5. **CI/CD Integration**
   ```yaml
   # In your CI pipeline
   - name: Check requirements
     run: |
       python3 detect_requirements.py --no-versions
       git diff --exit-code requirements.txt
   ```

## 🔍 What Gets Detected?

### ✅ Detected
- Standard `import module`
- `from module import something`
- Nested imports like `azure.storage.blob`
- Relative package imports

### ❌ Not Detected
- Dynamic imports: `__import__('module')`
- Conditional imports inside functions (without static analysis)
- Comments mentioning packages
- Requirements in documentation

## 📦 Package Name Mappings

Common mappings included:

| Import | PyPI Package |
|--------|--------------|
| `yaml` | `PyYAML` |
| `cv2` | `opencv-python` |
| `sklearn` | `scikit-learn` |
| `PIL` | `Pillow` |
| `bs4` | `beautifulsoup4` |
| `dotenv` | `python-dotenv` |
| `dateutil` | `python-dateutil` |
| `psycopg2` | `psycopg2-binary` |

See full list in `detect_requirements.py`

## 🆘 Getting Help

```bash
# Help for any tool
python3 detect_requirements.py --help
./check_requirements.sh --help
./update_all_requirements.sh --help
```

For detailed documentation: [REQUIREMENTS_DETECTOR.md](REQUIREMENTS_DETECTOR.md)
