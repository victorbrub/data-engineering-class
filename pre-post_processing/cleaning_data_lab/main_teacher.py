"""
DATA CLEANING EXERCISE
=====================
Retrieve, explore, and clean an e-commerce customer orders dataset
"""

import pandas as pd
import requests
import io
import os
from datetime import datetime

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
    response.raise_for_status()
    
    print("✓ Data fetched from web source, loading into DataFrame...")
    print("Response:", response.text)  
    df = pd.read_csv(io.StringIO(response.text),sep=',',on_bad_lines='warn')
    
    print(f"✓ Data retrieved successfully!")
    print(f"✓ Status Code: {response.status_code}")
    print(f"✓ Rows: {len(df)}, Columns: {len(df.columns)}\n")
    
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

# # ============================================================================
# # STEP 3: IDENTIFY QUALITY ISSUES
# # ============================================================================
print("STEP 3: DATA QUALITY ISSUES")
print("-" * 70)

print(f"Duplicates: {df.duplicated().sum()}")
print(f"Duplicate OrderIDs: {df['OrderID'].duplicated().sum()}")

if df[df.duplicated(subset=['OrderID'], keep=False)].shape[0] > 0:
    print(f"\nDuplicate Records:\n{df[df.duplicated(subset=['OrderID'], keep=False)].sort_values('OrderID')}\n")

# # ============================================================================
# # STEP 4: DATA CLEANING
# # ============================================================================
print("STEP 4: DATA CLEANING")
print("-" * 70)

# 4.1 Remove Duplicates
print("\n4.1 Removing Duplicates...")
initial_len = len(df)
df = df.drop_duplicates(subset=['OrderID'], keep='first')
print(f"    ✓ Removed {initial_len - len(df)} duplicate rows")

# 4.2 Clean Text Fields
print("\n4.2 Cleaning Text Fields...")
df['CustomerName'] = df['CustomerName'].str.strip().str.title()
df['Email'] = df['Email'].str.strip().str.lower()
df['Phone'] = df['Phone'].str.strip()
print("    ✓ Names, Emails, Phones standardized")

# 4.3 Standardize Countries
print("\n4.3 Standardizing Countries...")
country_mapping = {
    'USA': 'USA', 'us': 'USA', 'US': 'USA', 'United States': 'USA', 'usa': 'USA',
    'UK': 'United Kingdom', 'GB': 'United Kingdom',
    'Canada': 'Canada'
}
df['Country'] = df['Country'].map(country_mapping)
print(f"    ✓ Unique countries: {df['Country'].unique()}")

# 4.4 Fix Data Types
print("\n4.4 Converting Data Types...")
df['Quantity'] = pd.to_numeric(df['Quantity'], errors='coerce').astype('Int64')
df['Price'] = pd.to_numeric(df['Price'], errors='coerce')
df['CustomerAge'] = pd.to_numeric(df['CustomerAge'], errors='coerce').astype('Int64')
df['OrderDate'] = pd.to_datetime(df['OrderDate'], errors='coerce').dt.strftime('%Y-%m-%d')
print("    ✓ Data types fixed")

# 4.5 Handle Missing Values
print("\n4.5 Handling Missing Values...")
initial_len = len(df)
df = df[df['Email'].notna()]
removed_email = initial_len - len(df)
initial_len = len(df)
df['Phone'] = df['Phone'].fillna('Not Provided')
df = df[df['Price'].notna()]
removed_price = initial_len - len(df)
initial_len = len(df)
df = df[df['CustomerAge'].notna()]
removed_age = initial_len - len(df)
print(f"    ✓ Removed {removed_email} rows without email")
print(f"    ✓ Removed {removed_price} rows without price")
print(f"    ✓ Removed {removed_age} rows without age")

# 4.6 Remove Invalid Values
print("\n4.6 Validating Values...")
initial_len = len(df)
df = df[df['Quantity'] > 0]
removed_qty = initial_len - len(df)
initial_len = len(df)
df = df[df['Price'] > 0]
removed_price_val = initial_len - len(df)
initial_len = len(df)
df = df[(df['CustomerAge'] >= 18) & (df['CustomerAge'] <= 120)]
removed_age_val = initial_len - len(df)
print(f"    ✓ Removed {removed_qty} invalid quantities")
print(f"    ✓ Removed {removed_price_val} invalid prices")
print(f"    ✓ Removed {removed_age_val} invalid ages")

# ============================================================================
# STEP 5: FINAL VALIDATION
# ============================================================================
print("\n" + "=" * 70)
print("STEP 5: FINAL VALIDATION")
print("-" * 70)

print(f"\n✅ QUALITY METRICS:")
print(f"   Rows: {len(df)}")
print(f"   Columns: {len(df.columns)}")
print(f"   Missing Values: {df.isnull().sum().sum()}")
print(f"   Duplicates: {df.duplicated().sum()}")

print(f"\n📊 CLEANED DATA PREVIEW:")
print(df.head(10))

print(f"\n📈 STATISTICS:")
print(df[['Quantity', 'Price', 'CustomerAge']].describe())

# ============================================================================
# STEP 6: SAVE CLEANED DATA
# ============================================================================
print("\n" + "=" * 70)
print("STEP 6: SAVING CLEANED DATA")
print("-" * 70)

output_csv = 'customer_orders_cleaned.csv'
df.to_csv(output_csv, index=False)
print(f"\n✓ Saved as: {output_csv}")
print(f"  Size: {os.path.getsize(output_csv)} bytes")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print(f"""
Original Dataset:     20 rows
Cleaned Dataset:      {len(df)} rows
Rows Removed:         {20 - len(df)} ({((20 - len(df))/20)*100:.1f}%)
Data Quality Score:   {(len(df)/20)*100:.1f}%

✅ CLEANING COMPLETE - Ready for analysis!
""")

print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")