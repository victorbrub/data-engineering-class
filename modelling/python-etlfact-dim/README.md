# Domestic Violence Data ETL Pipeline

This ETL pipeline processes domestic violence reports from the Colombian National Police, cleaning the data and transforming it into a star schema for analytical purposes.

## Files

- **`clean_data.py`** - Cleans and standardizes the raw CSV data
- **`transform_to_star_schema.py`** - Transforms cleaned data into fact and dimension tables
- **`run_etl.py`** - Main script that executes the complete ETL pipeline
- **`requirements.txt`** - Python dependencies

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Option 1: Run Complete Pipeline
```bash
python run_etl.py
```

### Option 2: Run Steps Individually

1. Clean the data:
```bash
python clean_data.py
```

2. Transform to star schema:
```bash
python transform_to_star_schema.py
```

## Output

### Cleaned Data
- **`cleaned_data.csv`** - Cleaned and standardized source data

### Star Schema Tables

**Dimension Tables:**
- **`transformed_data/dim_date.csv`** - Date dimension
  - Columns: `date_id`, `date`, `year`, `month`, `day`, `quarter`, `day_of_week`, `day_name`, `month_name`, `week_of_year`, `is_weekend`

- **`transformed_data/dim_location.csv`** - Location dimension
  - Columns: `location_id`, `CODIGO DANE`, `DEPARTAMENTO`, `MUNICIPIO`

- **`transformed_data/dim_tool.csv`** - Tool/Weapon dimension
  - Columns: `tool_id`, `ARMAS MEDIOS`

**Fact Table:**
- **`transformed_data/fact_domestic_violence.csv`** - Main fact table
  - Columns: `fact_id`, `date_id`, `location_id`, `tool_id`, `genero`, `grupo_etario`, `cantidad`

## Data Cleaning Process

The cleaning script performs the following operations:
1. Removes duplicate records
2. Handles missing values in critical columns
3. Standardizes text fields (uppercase, trim whitespace)
4. Validates and converts CODIGO DANE to integer
5. Converts dates to standard format (YYYY-MM-DD)
6. Ensures CANTIDAD (quantity) is a positive integer
7. Sorts data by date and location

## Star Schema Design

The star schema consists of:
- **1 Fact Table**: Contains measures (cantidad) and foreign keys to dimensions
- **3 Dimension Tables**: Date, Location, and Tool dimensions

This design enables efficient querying for analytical purposes such as:
- Trend analysis over time
- Geographic analysis by department and municipality
- Analysis by weapon/tool type
- Gender and age group analysis

## Example Queries

After loading into a database, you can perform queries like:

```sql
-- Total incidents by year
SELECT d.year, SUM(f.cantidad) as total_incidents
FROM fact_domestic_violence f
JOIN dim_date d ON f.date_id = d.date_id
GROUP BY d.year
ORDER BY d.year;

-- Incidents by department
SELECT l.DEPARTAMENTO, SUM(f.cantidad) as total_incidents
FROM fact_domestic_violence f
JOIN dim_location l ON f.location_id = l.location_id
GROUP BY l.DEPARTAMENTO
ORDER BY total_incidents DESC;

-- Incidents by weapon type
SELECT t.ARMAS_MEDIOS, SUM(f.cantidad) as total_incidents
FROM fact_domestic_violence f
JOIN dim_tool t ON f.tool_id = t.tool_id
GROUP BY t.ARMAS_MEDIOS
ORDER BY total_incidents DESC;
```
