# Azure PostgreSQL Data Warehouse Project

A complete solution for deploying Azure PostgreSQL Flexible Server and uploading CSV/JSON data files to create a data warehouse.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Deployment](#deployment)
- [Data Upload](#data-upload)
- [Configuration](#configuration)
- [Usage Examples](#usage-examples)
- [Troubleshooting](#troubleshooting)

## Overview

This project provides:
- **Deployment Scripts**: Bash and PowerShell scripts to create Azure PostgreSQL Flexible Server instances
- **Data Upload Tool**: Python script to automatically upload CSV/JSON files to PostgreSQL
- **Auto Table Creation**: Tables are created automatically based on file structure
- **Data Overwrite**: Existing tables are truncated and data is overwritten on each upload

### Features

- Azure PostgreSQL Flexible Server deployment (Bash & PowerShell)  
- Automatic table creation from CSV/JSON structure  
- Data type inference from pandas DataFrames  
- Batch insert for large datasets  
- Overwrite existing data (truncate before insert)  
- Comprehensive logging  
- Connection testing  
- Directory batch upload

## Prerequisites

### Required Software

1. **Azure CLI** - [Install instructions](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)
   ```bash
   # Verify installation
   az --version
   ```

2. **Python 3.8+** - [Download](https://www.python.org/downloads/)
   ```bash
   # Verify installation
   python --version
   ```

3. **Azure Subscription** - [Azure for Students](https://azure.microsoft.com/en-us/free/students/)

### Azure Permissions

You need permission to:
- Create resource groups
- Create PostgreSQL Flexible Server instances
- Configure firewall rules
- Create databases

## Quick Start

### 1. Clone/Navigate to Project

```bash
cd /home/vbarcelo/repos/azure-sandbox/postgresql
```

### 2. Deploy PostgreSQL Server

**Using Bash (Linux/macOS/WSL):**
```bash
chmod +x deploy_postgres.sh
./deploy_postgres.sh
```

**Using PowerShell (Windows):**
```powershell
.\deploy_postgres.ps1
```

The script will:
- Create a resource group
- Deploy PostgreSQL Flexible Server (Burstable tier for students)
- Configure firewall rules
- Create initial database
- Generate `config.yaml` with connection details

### 3. Configure Connection

Edit `config.yaml` with your password:
```yaml
database:
  password: "YourSecurePassword123"
```

### 4. Install Python Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 5. Test Connection

```bash
python upload_data.py --test --config config.yaml
```

### 6. Upload Data

```bash
# Upload single file
python upload_data.py data/sales.csv

# Upload entire directory
python upload_data.py data/
```

## Deployment

### Deployment Script Options

Both scripts support environment variables for customization:

```bash
# Bash example
export RESOURCE_GROUP="my-datawarehouse-rg"
export LOCATION="westus2"
export SERVER_NAME="my-postgres-server"
export ADMIN_USER="myadmin"
export DATABASE_NAME="warehouse"
./deploy_postgres.sh
```

```powershell
# PowerShell example
$env:RESOURCE_GROUP = "my-datawarehouse-rg"
$env:LOCATION = "westus2"
$env:SERVER_NAME = "my-postgres-server"
$env:ADMIN_USER = "myadmin"
$env:DATABASE_NAME = "warehouse"
.\deploy_postgres.ps1
```

### Configuration Options

| Variable | Default | Description |
|----------|---------|-------------|
| `RESOURCE_GROUP` | `pg-datawarehouse-rg` | Azure resource group name |
| `LOCATION` | `eastus` | Azure region |
| `SERVER_NAME` | `pg-datawarehouse-<random>` | PostgreSQL server name (must be globally unique) |
| `ADMIN_USER` | `pgadmin` | Database admin username |
| `DATABASE_NAME` | `datawarehouse` | Initial database name |
| `SKU_NAME` | `Standard_B1ms` | Server SKU (Burstable tier) |
| `STORAGE_SIZE` | `32` | Storage size in GB |
| `POSTGRES_VERSION` | `15` | PostgreSQL version |

### Cleanup Resources

To delete all created resources:

```bash
# Bash
az group delete --name pg-datawarehouse-rg --yes

# PowerShell
az group delete --name pg-datawarehouse-rg --yes
```

## Data Upload

### Upload Single File

```bash
# CSV file
python upload_data.py data/customers.csv

# JSON file
python upload_data.py data/orders.json

# Custom table name
python upload_data.py data/sales.csv --table monthly_sales
```

### Upload Directory

```bash
# Upload all CSV and JSON files from directory
python upload_data.py data/
```

### File Format Requirements

**CSV Format:**
```csv
id,name,email,created_at
1,John Doe,john@example.com,2024-01-01
2,Jane Smith,jane@example.com,2024-01-02
```

**JSON Format (Array of Objects):**
```json
[
  {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "created_at": "2024-01-01"
  },
  {
    "id": 2,
    "name": "Jane Smith",
    "email": "jane@example.com",
    "created_at": "2024-01-02"
  }
]
```

### Table Creation Rules

- **Table names** are derived from filenames (sanitized)
  - `sales_data.csv` → `sales_data` table
  - `My Orders.json` → `my_orders` table
- **Columns** are created based on DataFrame structure
- **Data types** are inferred automatically:
  - Integers → `BIGINT`
  - Floats → `DOUBLE PRECISION`
  - Booleans → `BOOLEAN`
  - Dates → `DATE` or `TIMESTAMP`
  - Strings → `TEXT`
- **Auto-generated columns**:
  - `id` (SERIAL PRIMARY KEY)
  - `uploaded_at` (TIMESTAMP)

### Data Overwrite Behavior

When uploading to an existing table:
1. Table structure is verified/recreated
2. **All existing data is deleted** (TRUNCATE)
3. New data is inserted

## Configuration

### config.yaml Structure

```yaml
# PostgreSQL Connection Configuration
database:
  host: "your-server.postgres.database.azure.com"
  port: 5432
  database: "datawarehouse"
  user: "pgadmin"
  password: "YourSecurePassword"
  sslmode: "require"

# Azure Resource Information
azure:
  resource_group: "pg-datawarehouse-rg"
  server_name: "your-server-name"
  location: "eastus"

# Data upload settings
upload:
  chunk_size: 1000  # Rows per batch insert
  data_directory: "./data"
```

### Security Best Practices

1. **Never commit `config.yaml` with passwords** to version control
2. Use environment variables for sensitive data:
   ```bash
   export DB_PASSWORD="YourPassword"
   ```
3. Use Azure Key Vault for production environments
4. Enable SSL/TLS connections (sslmode: require)
5. Rotate passwords regularly

## Usage Examples

### Example 1: Sales Data Warehouse

```bash
# Create data directory
mkdir -p data

# Place your CSV files
# data/sales_2024.csv
# data/customers.csv
# data/products.csv

# Upload all files
python upload_data.py data/
```

### Example 2: Single Large File

```python
# For very large files, adjust chunk_size in config.yaml
upload:
  chunk_size: 5000  # Larger batches for better performance
```

### Example 3: Automated Pipeline

```bash
#!/bin/bash
# automated_upload.sh

# Test connection
python upload_data.py --test || exit 1

# Upload data
python upload_data.py data/

# Log results
echo "Upload completed at $(date)" >> upload_history.log
```

### Example 4: Query Uploaded Data

```bash
# Connect to database
psql "host=your-server.postgres.database.azure.com \
      port=5432 \
      dbname=datawarehouse \
      user=pgadmin \
      sslmode=require"

# Query data
SELECT * FROM sales_2024 LIMIT 10;
SELECT COUNT(*) FROM customers;
```

## Troubleshooting

### Connection Issues

**Problem:** "Connection refused" or "Connection timeout"
- **Solution:** Check firewall rules in Azure Portal
- Add your IP: `az postgres flexible-server firewall-rule create ...`

**Problem:** "Authentication failed"
- **Solution:** Verify username and password in `config.yaml`
- Reset password: Azure Portal → Your Server → Reset password

### Upload Issues

**Problem:** "No module named 'psycopg'"
- **Solution:** Install dependencies: `pip install -r requirements.txt`

**Problem:** "Table already exists" error
- **Solution:** Script automatically handles this - check logs for details

**Problem:** "File not found"
- **Solution:** Use absolute paths or verify current directory

### Data Type Issues

**Problem:** Dates uploaded as text
- **Solution:** Ensure proper date format in CSV: `YYYY-MM-DD`
- Or use pandas datetime: `pd.to_datetime(df['date_column'])`

### Performance Issues

**Problem:** Slow upload for large files
- **Solution:** Increase `chunk_size` in config.yaml
- Use fewer columns if possible
- Consider splitting files

## Sample Data

Create sample data for testing:

```bash
mkdir -p data
```

**data/sample_sales.csv:**
```csv
product,quantity,price,sale_date
Laptop,5,999.99,2024-01-15
Mouse,20,19.99,2024-01-16
Keyboard,15,49.99,2024-01-17
```

**data/sample_customers.json:**
```json
[
  {"customer_id": 1, "name": "Alice Johnson", "email": "alice@example.com"},
  {"customer_id": 2, "name": "Bob Smith", "email": "bob@example.com"}
]
```

## Logging

Logs are written to:
- Console (stdout)
- `upload_data.log` file

Log levels:
- INFO: Normal operations
- WARNING: Non-critical issues
- ERROR: Failed operations

## Contributing

Feel free to submit issues or pull requests for improvements.

## License

MIT License - See project root for details.

## Additional Resources

- [Azure PostgreSQL Documentation](https://docs.microsoft.com/en-us/azure/postgresql/)
- [psycopg Documentation](https://www.psycopg.org/psycopg3/docs/)
- [pandas Documentation](https://pandas.pydata.org/docs/)
- [Azure CLI Reference](https://docs.microsoft.com/en-us/cli/azure/)

---

**Need help?** Check the logs or open an issue with:
- Error messages
- Log file contents
- Configuration (without passwords!)
- Steps to reproduce
