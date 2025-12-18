#!/usr/bin/env python3
# analyze_logs.py

import os
from datetime import datetime

LOG_FILE = "./app_logs.txt"
OUTPUT_DIR = "./"

# Create sample log file if it doesn't exist
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, "w") as f:
        f.write("ERROR: Database connection failed\n" * 5)
        f.write("WARNING: High memory usage\n" * 3)

# Process logs
with open(LOG_FILE, "r") as f:
    lines = f.readlines()

# Generate report
today = datetime.now().strftime("%Y-%m-%d")
report_file = f"{OUTPUT_DIR}/daily_report_{today}.txt"

with open(report_file, "w") as f:
    f.write("=== Daily Report ===\n")
    f.write(f"Generated: {datetime.now()}\n")
    f.write(f"Total log entries: {len(lines)}\n")
    f.write(f"Errors: {sum(1 for line in lines if 'ERROR' in line)}\n")
    f.write(f"Warnings: {sum(1 for line in lines if 'WARNING' in line)}\n")
    f.write(f"\nReport saved to: {report_file}\n")

print(f"✅ Report generated: {report_file}")