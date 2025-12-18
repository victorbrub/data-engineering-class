"""
DATA CLEANING EXERCISE
=====================
Retrieve, explore, and clean an e-commerce customer orders dataset
"""
from datetime import datetime
import requests
import pandas as pd
import io

print("=" * 70)
print("DATA CLEANING EXERCISE - E-COMMERCE CUSTOMER ORDERS")
print("=" * 70)
print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# ============================================================================
# STEP 1: RETRIEVE DATA FROM WEB SOURCE
# ============================================================================
print("STEP 1: RETRIEVING DATA FROM WEB SOURCE")
print("-" * 70)

url = "https://raw.githubusercontent.com/victorbrub/data-engineering-class/refs/heads/main/pre-post_processing/exercise.csv"

try:
    print(f"Fetching data from: {url}")
    response = requests.get(url, timeout=10)

    print("Response:", response.text)
    
    print("✓ Data fetched from web source, loading into DataFrame...")
    # print("Response:", response.text)  
    df = pd.read_csv(io.StringIO(response.text),sep=',',on_bad_lines='warn')
    
    print(f"✓ Data retrieved successfully!")
    print(f"✓ Status Code: {response.status_code}")
    print(f"✓ Rows: {len(df)}, Columns: {len(df.columns)}\n")
    print(df.head())
    
except Exception as e:
    print(f"✗ Error: {e}")
    raise e



# ============================================================================
# STEP 2: INITIAL EXPLORATION
# ============================================================================

print("STEP 2: INITIAL DATA EXPLORATION")
print("-" * 70)
print(f"\nDataset Shape: {df.shape}")
print(f"\nColumn Names & Types:\n{df.dtypes}")
print(f"\nFirst 5 Rows:\n{df.head()}")
print(f"\nMissing Values:\n{df.isnull().sum()}")
print(f"\nTotal Missing: {df.isnull().sum().sum()}\n")

# ============================================================================
# STEP 3: IDENTIFY QUALITY ISSUES
# ============================================================================

print("STEP 3: DATA QUALITY ISSUES")
print("-" * 70)

print(f"Duplicates: {df.duplicated().sum()}")
print(f"Duplicate OrderIDs: {df['OrderID'].duplicated().sum()}")

if df[df.duplicated(subset=['OrderID'], keep=False)].shape[0] > 0:
    print(f"\nDuplicate Records:\n{df[df.duplicated(subset=['OrderID'], keep=False)].sort_values('OrderID')}\n")


# ============================================================================
# STEP 4: DATA CLEANING
# ============================================================================
print("STEP 4: DATA CLEANING")
print("-" * 70)

# 4.1 Remove Duplicates
print("\n4.1 Removing Duplicates...")
initial_len = len(df)
df = df.drop_duplicates(subset=['OrderID'], keep='first')
print(f"    ✓ Removed {initial_len - len(df)} duplicate rows")


# ============================================================================
# STEP 5: FINAL VALIDATION
# ============================================================================



# ============================================================================
# STEP 6: SAVE CLEANED DATA
# ============================================================================



# ============================================================================
# SUMMARY
# ============================================================================


print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")