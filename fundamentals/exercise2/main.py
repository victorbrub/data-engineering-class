import requests
import pandas as pd
from io import BytesIO

# Make GET request to download the Excel file
url = "https://www.zaragoza.es/contenidos/bici/aforo_permanente_Goya.xlsx"

def main () -> None:
    try:
        print("Downloading Excel file...")
        response = requests.get(url)
        response.raise_for_status()
        
        print("Reading Excel data...")
        # Read the Excel file directly from the response content
        excel_data = pd.read_excel(BytesIO(response.content))
        
        print("Data successfully downloaded and processed!")
        print(f"Shape of data: {excel_data.shape}")
        
        # Convert to CSV format and display
        csv_string = excel_data.to_csv(index=False)
        
        # Display the CSV data (first 2000 characters to avoid too much output)
        print("\n" + "="*50)
        print("DATA IN CSV FORMAT:")
        print("="*50)
        print(csv_string[:2000])
        if len(csv_string) > 2000:
            print("...\n(Data truncated for display - showing first 2000 characters)")
        
        # Save as CSV file
        csv_filename = "aforo_permanente_Goya.csv"
        excel_data.to_csv(csv_filename, index=False)
        print(f"\nCSV file saved as: {csv_filename}")
        
        # Show basic info about the data
        print(f"\nTotal rows: {len(excel_data)}")
        print(f"Columns: {list(excel_data.columns)}")

    except requests.exceptions.RequestException as e:
        print(f"Error downloading the file: {e}")
    except Exception as e:
        print(f"Error processing the file: {e}")



if __name__ == "__main__":
    main()