# Requirements Detection System - Visual Guide

```
┌─────────────────────────────────────────────────────────────────────┐
│                 REQUIREMENTS DETECTION SYSTEM                       │
│                                                                     │
│  Automatically detect and manage Python dependencies               │
└─────────────────────────────────────────────────────────────────────┘

╔═══════════════════════════════════════════════════════════════════╗
║                      SYSTEM ARCHITECTURE                          ║
╚═══════════════════════════════════════════════════════════════════╝

    ┌─────────────────┐
    │  Python Files   │
    │    (.py)        │
    └────────┬────────┘
             │
             ▼
    ┌─────────────────────────┐
    │  detect_requirements.py │◄──── Core Detection Engine
    │                         │
    │  • AST Parser           │
    │  • Import Extractor     │
    │  • Package Mapper       │
    │  • Version Detector     │
    └────────┬────────────────┘
             │
             ▼
    ┌─────────────────┐
    │ requirements.txt│
    └─────────────────┘


╔═══════════════════════════════════════════════════════════════════╗
║                      THREE MAIN TOOLS                             ║
╚═══════════════════════════════════════════════════════════════════╝

┌───────────────────────────────────────────────────────────────────┐
│ 1️⃣  detect_requirements.py - Core Scanner                        │
├───────────────────────────────────────────────────────────────────┤
│                                                                   │
│  python3 detect_requirements.py [directory]                       │
│                                                                   │
│  INPUT:  Python source files (.py)                                │
│  OUTPUT: requirements.txt                                         │
│                                                                   │
│  ✓ Fast and accurate                                              │
│  ✓ Standalone tool                                                │
│  ✓ Configurable output                                            │
└───────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────┐
│ 2️⃣  check_requirements.sh - Interactive Checker                  │
├───────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ./check_requirements.sh [directory]                              │
│                                                                   │
│  INPUT:  Python files + existing requirements.txt                 │
│  OUTPUT: Updated requirements.txt (after confirmation)            │
│                                                                   │
│  ✓ Shows differences                                              │
│  ✓ Backs up existing file                                         │
│  ✓ User confirmation                                              │
└───────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────┐
│ 3️⃣  update_all_requirements.sh - Batch Processor                 │
├───────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ./update_all_requirements.sh                                     │
│                                                                   │
│  INPUT:  Multiple project directories                             │
│  OUTPUT: requirements.txt for each project                        │
│                                                                   │
│  ✓ Process all projects                                           │
│  ✓ Configurable project list                                      │
│  ✓ Progress reporting                                             │
└───────────────────────────────────────────────────────────────────┘


╔═══════════════════════════════════════════════════════════════════╗
║                     WORKFLOW EXAMPLES                             ║
╚═══════════════════════════════════════════════════════════════════╝

┌───────────────────────────────────────────────────────────────────┐
│ Scenario 1: New Project Setup                                    │
└───────────────────────────────────────────────────────────────────┘

    1. Write Code              2. Detect              3. Install
    ┌─────────┐               ┌─────────┐            ┌─────────┐
    │ main.py │──────────────▶│detect.py│───────────▶│   pip   │
    │ utils.py│               │         │            │ install │
    └─────────┘               └─────────┘            └─────────┘
         │                          │                      │
         │                          ▼                      ▼
    import pandas             requirements.txt      Installed!
    import yaml                pandas
    import psycopg            PyYAML
                              psycopg


┌───────────────────────────────────────────────────────────────────┐
│ Scenario 2: Update Existing Project                              │
└───────────────────────────────────────────────────────────────────┘

    1. Modify Code            2. Check Diff          3. Confirm
    ┌─────────┐               ┌─────────┐            ┌─────────┐
    │Add new  │──────────────▶│ check.sh│───────────▶│Update?  │
    │imports  │               │         │            │ [y/N]   │
    └─────────┘               └─────────┘            └─────────┘
         │                          │                      │
         │                          ▼                      ▼
    +import requests          ➕ requests              Updated!
    +import bs4               ➕ beautifulsoup4        


┌───────────────────────────────────────────────────────────────────┐
│ Scenario 3: Batch Update All Projects                            │
└───────────────────────────────────────────────────────────────────┘

    ┌────────────────────┐
    │update_all_reqs.sh  │
    └──────────┬─────────┘
               │
         ┌─────┴─────┬─────────┬─────────┐
         ▼           ▼         ▼         ▼
    ┌────────┐  ┌────────┐ ┌────────┐ ┌────────┐
    │Project1│  │Project2│ │Project3│ │Project4│
    └────────┘  └────────┘ └────────┘ └────────┘
         │           │         │         │
         ▼           ▼         ▼         ▼
     reqs.txt    reqs.txt  reqs.txt  reqs.txt


╔═══════════════════════════════════════════════════════════════════╗
║                    HOW IT WORKS                                   ║
╚═══════════════════════════════════════════════════════════════════╝

Step 1: SCAN
┌──────────────────────────────────────────┐
│ Find all .py files                       │
│ (excluding venv, __pycache__, etc.)      │
└────────────┬─────────────────────────────┘
             │
             ▼
Step 2: PARSE
┌──────────────────────────────────────────┐
│ Use Python AST to extract:               │
│ • import statements                      │
│ • from...import statements               │
└────────────┬─────────────────────────────┘
             │
             ▼
Step 3: FILTER
┌──────────────────────────────────────────┐
│ Remove:                                  │
│ • Standard library (os, sys, json...)    │
│ • Built-ins (__future__, abc...)         │
│ • Local modules                          │
└────────────┬─────────────────────────────┘
             │
             ▼
Step 4: MAP
┌──────────────────────────────────────────┐
│ Convert import names to packages:        │
│ yaml → PyYAML                            │
│ cv2 → opencv-python                      │
│ sklearn → scikit-learn                   │
└────────────┬─────────────────────────────┘
             │
             ▼
Step 5: VERSION (Optional)
┌──────────────────────────────────────────┐
│ Check installed versions:                │
│ pandas → pandas==2.1.0                   │
└────────────┬─────────────────────────────┘
             │
             ▼
Step 6: WRITE
┌──────────────────────────────────────────┐
│ Generate requirements.txt:               │
│                                          │
│ # Auto-generated                         │
│ pandas==2.1.0                            │
│ PyYAML==6.0.1                            │
│ requests==2.31.0                         │
└──────────────────────────────────────────┘


╔═══════════════════════════════════════════════════════════════════╗
║                  PACKAGE NAME MAPPING                             ║
╚═══════════════════════════════════════════════════════════════════╝

    Import Name          →          PyPI Package
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    yaml                 →          PyYAML
    cv2                  →          opencv-python
    sklearn              →          scikit-learn
    PIL                  →          Pillow
    bs4                  →          beautifulsoup4
    dotenv               →          python-dotenv
    dateutil             →          python-dateutil
    psycopg2             →          psycopg2-binary
    azure.eventhub       →          azure-eventhub
    azure.identity       →          azure-identity


╔═══════════════════════════════════════════════════════════════════╗
║                   DIRECTORY STRUCTURE                             ║
╚═══════════════════════════════════════════════════════════════════╝

data-engineering-class/
├── detect_requirements.py          ← Core scanner
├── check_requirements.sh            ← Interactive checker
├── update_all_requirements.sh       ← Batch processor
├── setup_with_requirements.sh.example  ← Integration example
├── REQUIREMENTS_DETECTOR.md         ← Full documentation
├── REQUIREMENTS_QUICK_REFERENCE.md  ← Quick guide
├── REQUIREMENTS_SYSTEM_SUMMARY.md   ← Overview
├── REQUIREMENTS_VISUAL_GUIDE.md     ← This file
└── README.md                        ← Updated with tools

Projects:
├── modelling/
│   ├── data_warehouse/
│   │   └── requirements.txt         ← Auto-generated
│   └── python-etlfact-dim/
│       └── requirements.txt         ← Auto-generated
└── pre-post_processing/
    └── cleaning_data_lab/
        └── requirements.txt         ← Auto-generated


╔═══════════════════════════════════════════════════════════════════╗
║                    COMMAND CHEATSHEET                             ║
╚═══════════════════════════════════════════════════════════════════╝

┌─────────────────────────────────────────────────────────────────┐
│ Basic Commands                                                  │
├─────────────────────────────────────────────────────────────────┤
│ python3 detect_requirements.py           # Current directory    │
│ python3 detect_requirements.py /path     # Specific directory   │
│ python3 detect_requirements.py --help    # Show help            │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ With Options                                                    │
├─────────────────────────────────────────────────────────────────┤
│ python3 detect_requirements.py --no-versions                    │
│ python3 detect_requirements.py -o custom.txt                    │
│ python3 detect_requirements.py /path --no-versions              │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ Interactive Check                                               │
├─────────────────────────────────────────────────────────────────┤
│ ./check_requirements.sh                  # Current directory    │
│ ./check_requirements.sh /path            # Specific directory   │
│ ./check_requirements.sh /path true       # Auto-update          │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ Batch Update                                                    │
├─────────────────────────────────────────────────────────────────┤
│ ./update_all_requirements.sh                                    │
│ ./update_all_requirements.sh --project modelling/data_warehouse │
│ ./update_all_requirements.sh --with-versions                    │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ After Detection                                                 │
├─────────────────────────────────────────────────────────────────┤
│ cat requirements.txt                     # View generated file  │
│ pip install -r requirements.txt          # Install packages     │
│ pip list                                 # Verify installation  │
└─────────────────────────────────────────────────────────────────┘


╔═══════════════════════════════════════════════════════════════════╗
║                    SUCCESS INDICATORS                             ║
╚═══════════════════════════════════════════════════════════════════╝

✅ System is working when you see:
   
   🔍 Scanning Python files in: /path
   📄 Found X Python file(s)
   📦 Found Y third-party import(s)
   ✓ package1==1.0.0
   ✓ package2==2.0.0
   ✅ Requirements written to: requirements.txt

❌ Issues to watch for:

   ⚠️  version unknown          → Package not installed
   ⚠️  Syntax error in file.py  → Fix Python syntax first
   ❌ Directory not found        → Check path


╔═══════════════════════════════════════════════════════════════════╗
║                         TIPS & TRICKS                             ║
╚═══════════════════════════════════════════════════════════════════╝

💡 Development Workflow
   1. Write code
   2. python3 detect_requirements.py
   3. git add requirements.txt
   4. git commit

💡 For Teams
   1. Detect requirements before committing
   2. Share requirements.txt with team
   3. Everyone runs: pip install -r requirements.txt

💡 CI/CD Integration
   Add to your pipeline:
   python3 detect_requirements.py --no-versions
   git diff --exit-code requirements.txt

💡 Version Control
   # Without versions - flexible for development
   python3 detect_requirements.py --no-versions
   
   # With versions - stable for production
   python3 detect_requirements.py


╔═══════════════════════════════════════════════════════════════════╗
║                       QUICK START                                 ║
╚═══════════════════════════════════════════════════════════════════╝

    For the impatient:

    cd your_project/
    python3 ../detect_requirements.py
    pip install -r requirements.txt

    Done! 🎉


Need more details? Check:
• REQUIREMENTS_DETECTOR.md - Full documentation
• REQUIREMENTS_QUICK_REFERENCE.md - Command reference
• REQUIREMENTS_SYSTEM_SUMMARY.md - Complete overview
