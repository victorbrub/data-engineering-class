"""
Data Cleaning Script for Domestic Violence Report
Cleans and standardizes the raw CSV data
"""
import pandas as pd
import os

def clean_data(input_file, output_file):
    """
    Clean the raw CSV data by:
    - Removing duplicates
    - Handling missing values
    - Standardizing text (strip whitespace, proper casing)
    - Validating data types
    - Removing invalid records
    """
    print(f"Reading data from {input_file}...")
    df = pd.read_csv(input_file)
    
    print(f"Initial record count: {len(df)}")
    
    # Display initial info
    print("\nInitial data info:")
    print(df.info())
    print("\nFirst few rows:")
    print(df.head())
    
    # 1. Strip whitespace from all string columns
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].str.strip()
    
    # 2. Remove duplicates
    initial_count = len(df)
    df = df.drop_duplicates()
    print(f"\nRemoved {initial_count - len(df)} duplicate rows")
    
    # 3. Handle missing values
    missing_before = df.isnull().sum()
    print("\nMissing values per column:")
    print(missing_before[missing_before > 0])
    
    # Remove rows with missing critical values
    critical_columns = ['DEPARTAMENTO', 'MUNICIPIO', 'CODIGO DANE', 'FECHA HECHO', 'CANTIDAD']
    df = df.dropna(subset=critical_columns)
    print(f"Removed rows with missing critical values. New count: {len(df)}")
    
    # 4. Standardize text columns
    text_columns = ['DEPARTAMENTO', 'MUNICIPIO', 'ARMAS MEDIOS', 'GENERO', 'GRUPO ETARIO']
    for col in text_columns:
        if col in df.columns:
            df[col] = df[col].str.upper().str.strip()
    
    # 5. Clean CODIGO DANE (ensure it's numeric)
    df['CODIGO DANE'] = pd.to_numeric(df['CODIGO DANE'], errors='coerce')
    df = df.dropna(subset=['CODIGO DANE'])
    df['CODIGO DANE'] = df['CODIGO DANE'].astype(int)
    
    # 6. Standardize date format (convert to YYYY-MM-DD)
    df['FECHA HECHO'] = pd.to_datetime(df['FECHA HECHO'], format='%d/%m/%Y', errors='coerce')
    df = df.dropna(subset=['FECHA HECHO'])
    df['FECHA HECHO'] = df['FECHA HECHO'].dt.strftime('%Y-%m-%d')
    
    # 7. Ensure CANTIDAD is positive integer
    df['CANTIDAD'] = pd.to_numeric(df['CANTIDAD'], errors='coerce')
    df = df.dropna(subset=['CANTIDAD'])
    df = df[df['CANTIDAD'] > 0]
    df['CANTIDAD'] = df['CANTIDAD'].astype(int)
    
    # 8. Sort by date and location
    df = df.sort_values(['FECHA HECHO', 'DEPARTAMENTO', 'MUNICIPIO'])
    
    print(f"\nFinal record count: {len(df)}")
    print("\nCleaned data summary:")
    print(df.describe(include='all'))
    
    # Save cleaned data
    df.to_csv(output_file, index=False)
    print(f"\nCleaned data saved to {output_file}")
    
    return df

if __name__ == "__main__":
    input_file = "Reporte_Delito_Violencia_Intrafamiliar_Polic_a_Nacional.csv"
    output_file = "cleaned_data.csv"
    
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found!")
    else:
        clean_data(input_file, output_file)
