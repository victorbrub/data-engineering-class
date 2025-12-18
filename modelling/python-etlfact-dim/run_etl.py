"""
Main ETL Pipeline Runner
Executes the complete ETL process: Clean -> Transform
"""
import os
import sys
from clean_data import clean_data
from transform_to_star_schema import transform_to_star_schema

def main():
    """
    Execute the complete ETL pipeline
    """
    print("="*70)
    print("DOMESTIC VIOLENCE DATA ETL PIPELINE")
    print("="*70)
    
    # Configuration
    input_file = "Reporte_Delito_Violencia_Intrafamiliar_Polic_a_Nacional.csv"
    cleaned_file = "cleaned_data.csv"
    
    # Step 1: Check if input file exists
    if not os.path.exists(input_file):
        print(f"\nError: Input file '{input_file}' not found!")
        print("Please ensure the CSV file is in the current directory.")
        sys.exit(1)
    
    # Step 2: Clean data
    print("\n" + "="*70)
    print("STEP 1: DATA CLEANING")
    print("="*70)
    try:
        clean_data(input_file, cleaned_file)
    except Exception as e:
        print(f"\nError during data cleaning: {str(e)}")
        sys.exit(1)
    
    # Step 3: Transform to star schema
    print("\n" + "="*70)
    print("STEP 2: STAR SCHEMA TRANSFORMATION")
    print("="*70)
    try:
        transform_to_star_schema(cleaned_file)
    except Exception as e:
        print(f"\nError during transformation: {str(e)}")
        sys.exit(1)
    
    # Success message
    print("\n" + "="*70)
    print("ETL PIPELINE COMPLETED SUCCESSFULLY!")
    print("="*70)
    print("\nOutput files:")
    print(f"  1. {cleaned_file} - Cleaned source data")
    print(f"  2. transformed_data/dim_date.csv - Date dimension")
    print(f"  3. transformed_data/dim_location.csv - Location dimension")
    print(f"  4. transformed_data/dim_tool.csv - Tool/Weapon dimension")
    print(f"  5. transformed_data/fact_domestic_violence.csv - Fact table")
    print("\nYou can now load these files into your data warehouse!")

if __name__ == "__main__":
    main()
