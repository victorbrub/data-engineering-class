"""
ETL Script for Star Schema Transformation
Transforms cleaned data into fact and dimension tables
"""
import pandas as pd
import os
from datetime import datetime

def create_date_dimension(df, output_file):
    """
    Create date dimension from FECHA HECHO column
    Includes: date, year, month, day, quarter, day_of_week, etc.
    """
    print("\nCreating Date Dimension...")
    
    # Convert to datetime
    dates = pd.to_datetime(df['FECHA HECHO'])
    
    # Create date dimension with unique dates
    date_df = pd.DataFrame({
        'date': dates.dt.strftime('%Y-%m-%d')
    }).drop_duplicates().sort_values('date')
    
    # Convert back to datetime for calculations
    date_df['date_dt'] = pd.to_datetime(date_df['date'])
    
    # Add date_id (surrogate key)
    date_df['date_id'] = range(1, len(date_df) + 1)
    
    # Add date attributes
    date_df['year'] = date_df['date_dt'].dt.year
    date_df['month'] = date_df['date_dt'].dt.month
    date_df['day'] = date_df['date_dt'].dt.day
    date_df['quarter'] = date_df['date_dt'].dt.quarter
    date_df['day_of_week'] = date_df['date_dt'].dt.dayofweek + 1  # 1=Monday, 7=Sunday
    date_df['day_name'] = date_df['date_dt'].dt.day_name()
    date_df['month_name'] = date_df['date_dt'].dt.month_name()
    date_df['week_of_year'] = date_df['date_dt'].dt.isocalendar().week
    date_df['is_weekend'] = date_df['day_of_week'].isin([6, 7]).astype(int)
    
    # Select final columns
    date_df = date_df[['date_id', 'date', 'year', 'month', 'day', 
                       'quarter', 'day_of_week', 'day_name', 'month_name', 
                       'week_of_year', 'is_weekend']]
    
    date_df.to_csv(output_file, index=False)
    print(f"Date dimension created with {len(date_df)} records")
    print(f"Saved to {output_file}")
    
    return date_df

def create_location_dimension(df, output_file):
    """
    Create location dimension from DEPARTAMENTO, MUNICIPIO, CODIGO DANE
    """
    print("\nCreating Location Dimension...")
    
    # Get unique locations
    location_df = df[['DEPARTAMENTO', 'MUNICIPIO', 'CODIGO DANE']].drop_duplicates()
    
    # Add location_id (surrogate key)
    location_df = location_df.sort_values(['DEPARTAMENTO', 'MUNICIPIO'])
    location_df['location_id'] = range(1, len(location_df) + 1)
    
    # Reorder columns
    location_df = location_df[['location_id', 'CODIGO DANE', 'DEPARTAMENTO', 'MUNICIPIO']]
    
    location_df.to_csv(output_file, index=False)
    print(f"Location dimension created with {len(location_df)} records")
    print(f"Saved to {output_file}")
    
    return location_df

def create_tool_dimension(df, output_file):
    """
    Create tool/weapon dimension from ARMAS MEDIOS
    """
    print("\nCreating Tool/Weapon Dimension...")
    
    # Get unique tools/weapons
    tool_df = df[['ARMAS MEDIOS']].drop_duplicates()
    
    # Add tool_id (surrogate key)
    tool_df = tool_df.sort_values('ARMAS MEDIOS')
    tool_df['tool_id'] = range(1, len(tool_df) + 1)
    
    # Reorder columns
    tool_df = tool_df[['tool_id', 'ARMAS MEDIOS']]
    
    tool_df.to_csv(output_file, index=False)
    print(f"Tool dimension created with {len(tool_df)} records")
    print(f"Saved to {output_file}")
    
    return tool_df

def create_fact_table(df, date_df, location_df, tool_df, output_file):
    """
    Create fact table with foreign keys to dimensions and measures
    """
    print("\nCreating Fact Table...")
    
    # Start with original data
    fact_df = df.copy()
    
    # Join with date dimension to get date_id
    date_lookup = date_df[['date', 'date_id']].copy()
    fact_df = fact_df.merge(date_lookup, left_on='FECHA HECHO', right_on='date', how='left')
    fact_df = fact_df.drop('date', axis=1)
    
    # Join with location dimension to get location_id
    location_lookup = location_df[['location_id', 'CODIGO DANE', 'DEPARTAMENTO', 'MUNICIPIO']].copy()
    fact_df = fact_df.merge(location_lookup, 
                            on=['CODIGO DANE', 'DEPARTAMENTO', 'MUNICIPIO'], 
                            how='left')
    
    # Join with tool dimension to get tool_id
    tool_lookup = tool_df[['tool_id', 'ARMAS MEDIOS']].copy()
    fact_df = fact_df.merge(tool_lookup, on='ARMAS MEDIOS', how='left')
    
    # Create fact_id (surrogate key)
    fact_df['fact_id'] = range(1, len(fact_df) + 1)
    
    # Select and reorder columns for fact table
    fact_df = fact_df[['fact_id', 'date_id', 'location_id', 'tool_id', 
                       'GENERO', 'GRUPO ETARIO', 'CANTIDAD']]
    
    # Rename for clarity
    fact_df = fact_df.rename(columns={
        'GENERO': 'genero',
        'GRUPO ETARIO': 'grupo_etario',
        'CANTIDAD': 'cantidad'
    })
    
    fact_df.to_csv(output_file, index=False)
    print(f"Fact table created with {len(fact_df)} records")
    print(f"Saved to {output_file}")
    
    return fact_df

def transform_to_star_schema(cleaned_file):
    """
    Main transformation function to create star schema
    """
    print("="*70)
    print("ETL Process: Transforming to Star Schema")
    print("="*70)
    
    # Read cleaned data
    print(f"\nReading cleaned data from {cleaned_file}...")
    df = pd.read_csv(cleaned_file)
    print(f"Loaded {len(df)} records")
    
    # Create output directory for transformed files
    output_dir = "transformed_data"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"\nCreated output directory: {output_dir}")
    
    # Create dimension tables
    date_df = create_date_dimension(df, f"{output_dir}/dim_date.csv")
    location_df = create_location_dimension(df, f"{output_dir}/dim_location.csv")
    tool_df = create_tool_dimension(df, f"{output_dir}/dim_tool.csv")
    
    # Create fact table
    fact_df = create_fact_table(df, date_df, location_df, tool_df, 
                                 f"{output_dir}/fact_domestic_violence.csv")
    
    print("\n" + "="*70)
    print("ETL Process Completed Successfully!")
    print("="*70)
    print("\nGenerated files:")
    print(f"  - {output_dir}/dim_date.csv ({len(date_df)} records)")
    print(f"  - {output_dir}/dim_location.csv ({len(location_df)} records)")
    print(f"  - {output_dir}/dim_tool.csv ({len(tool_df)} records)")
    print(f"  - {output_dir}/fact_domestic_violence.csv ({len(fact_df)} records)")
    print("\nStar Schema Summary:")
    print(f"  Total Facts: {len(fact_df):,}")
    print(f"  Date Range: {date_df['date'].min()} to {date_df['date'].max()}")
    print(f"  Locations: {len(location_df)}")
    print(f"  Tool Types: {len(tool_df)}")
    
    return {
        'date': date_df,
        'location': location_df,
        'tool': tool_df,
        'fact': fact_df
    }

if __name__ == "__main__":
    cleaned_file = "cleaned_data.csv"
    
    if not os.path.exists(cleaned_file):
        print(f"Error: Cleaned data file '{cleaned_file}' not found!")
        print("Please run clean_data.py first.")
    else:
        transform_to_star_schema(cleaned_file)
