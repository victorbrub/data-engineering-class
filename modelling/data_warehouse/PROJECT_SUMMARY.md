# Azure PostgreSQL Data Warehouse - Project Summary

## What Was Created

A complete end-to-end solution for deploying Azure PostgreSQL Flexible Server and uploading data from CSV/JSON files.

## Project Files

### Deployment Scripts
- **`deploy_postgres.sh`** - Bash script for Linux/macOS/WSL
- **`deploy_postgres.ps1`** - PowerShell script for Windows
- **`setup.sh`** - Quick setup script for environment configuration

### Python Application
- **`upload_data.py`** - Main data upload script with features:
  - Automatic table creation from file structure
  - Data type inference
  - Batch inserts with configurable chunk size
  - Truncate and reload (overwrite) functionality
  - Comprehensive logging
  - Connection testing
  - Directory batch upload

### Configuration & Dependencies
- **`requirements.txt`** - Python package dependencies
  - psycopg[binary] - PostgreSQL adapter
  - pandas - Data manipulation
  - PyYAML - Configuration parsing
  - azure-identity - Azure authentication (optional)
  
- **`config.example.yaml`** - Configuration template
- **`.gitignore`** - Git ignore patterns (protects secrets)

### Documentation
- **`README_DATAWAREHOUSE.md`** - Comprehensive documentation
- **`QUICKSTART.md`** - Quick reference guide
- **`PROJECT_SUMMARY.md`** - This file

### Sample Data
- **`data/sample_sales.csv`** - Example CSV file
- **`data/sample_customers.json`** - Example JSON file

## Key Features

### 1. Azure Deployment
- **Student-friendly pricing**: Uses Burstable tier (Standard_B1ms)
- **Automatic firewall configuration**: Adds your IP and Azure services
- **Resource group creation**: Organized infrastructure
- **SSL/TLS enabled**: Secure connections by default

### 2. Data Upload
- **Automatic table creation**: Tables created from file structure
- **Smart data typing**: Infers PostgreSQL types from pandas dtypes
- **Overwrite mode**: Truncates existing data before insert
- **Batch processing**: Configurable chunk size for performance
- **Multiple formats**: Supports CSV and JSON files
- **Bulk upload**: Process entire directories

### 3. Error Handling
- **Connection testing**: Verify database connectivity
- **Comprehensive logging**: File and console output
- **Graceful failures**: Clear error messages
- **Validation**: Config validation and sanitization

## Quick Start Guide

### Initial Setup (One-time)
```bash
# Navigate to project
cd /home/vbarcelo/repos/azure-sandbox/postgresql

# Run setup script
./setup.sh

# Deploy Azure resources
./deploy_postgres.sh

# Edit config.yaml with your password
nano config.yaml
```

### Daily Usage
```bash
# Activate environment
source venv/bin/activate

# Test connection
python upload_data.py --test

# Upload data
python upload_data.py data/your_file.csv
# or
python upload_data.py data/  # Upload entire directory
```

## How Data Upload Works

1. **File Reading**
   - CSV: Read with pandas `read_csv()`
   - JSON: Read with pandas `read_json()`

2. **Table Name Generation**
   - Filename stem extracted
   - Invalid characters replaced with underscores
   - Converted to lowercase
   - Example: `Sales Data 2024.csv` → `sales_data_2024`

3. **Column Type Mapping**
   ```
   pandas dtype → PostgreSQL type
   - int64     → BIGINT
   - float64   → DOUBLE PRECISION
   - bool      → BOOLEAN
   - datetime  → TIMESTAMP
   - object    → TEXT
   ```

4. **Table Creation**
   - Auto-increment `id` (PRIMARY KEY)
   - Data columns based on DataFrame
   - `uploaded_at` timestamp (auto-generated)

5. **Data Loading**
   - TRUNCATE existing data
   - INSERT in configurable chunks
   - COMMIT transaction

## Cost Considerations (Azure for Students)

### Recommended Configuration
- **Tier**: Burstable (Standard_B1ms)
- **vCores**: 1
- **RAM**: 2 GB
- **Storage**: 32 GB (minimum)
- **Estimated cost**: ~$12-15/month (with student credits)

### Cost-Saving Tips
1. **Stop server when not in use**:
   ```bash
   az postgres flexible-server stop --resource-group pg-datawarehouse-rg --name your-server
   ```

2. **Delete resources when project complete**:
   ```bash
   az group delete --name pg-datawarehouse-rg --yes
   ```

3. **Use Azure Calculator**: https://azure.microsoft.com/pricing/calculator/

## Security Best Practices

### What's Protected
- `config.yaml` excluded from git  
- SSL/TLS connections enforced  
- Firewall rules configured  
- Strong password requirements  

### Recommendations
- Use Azure Key Vault for production
- Rotate passwords regularly
- Limit firewall rules to specific IPs
- Enable Microsoft Entra ID authentication for enterprise

## Performance Optimization

### For Small Files (<1000 rows)
```yaml
upload:
  chunk_size: 1000
```

### For Large Files (>100,000 rows)
```yaml
upload:
  chunk_size: 5000
```

### For Very Large Files (>1,000,000 rows)
```yaml
upload:
  chunk_size: 10000
```

### Database Indexing (after upload)
```sql
-- Create indexes for frequently queried columns
CREATE INDEX idx_customer_email ON customers(email);
CREATE INDEX idx_sales_date ON sales(sale_date);
```

## Data Validation

### Verify Upload Success
```sql
-- Connect to database
psql "host=your-server.postgres.database.azure.com \
      port=5432 \
      dbname=datawarehouse \
      user=pgadmin \
      sslmode=require"

-- List all tables
\dt

-- Check table structure
\d table_name

-- Count rows
SELECT COUNT(*) FROM table_name;

-- View sample data
SELECT * FROM table_name LIMIT 10;

-- Check upload timestamps
SELECT 
    COUNT(*) as row_count,
    MIN(uploaded_at) as first_upload,
    MAX(uploaded_at) as last_upload
FROM table_name;
```

## Common Issues & Solutions

### Issue: "Module 'psycopg' not found"
**Solution**: Activate virtual environment and install dependencies
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Issue: "Connection timeout"
**Solution**: Add your IP to firewall rules
```bash
az postgres flexible-server firewall-rule create \
  --resource-group pg-datawarehouse-rg \
  --name your-server \
  --rule-name MyIP \
  --start-ip-address YOUR_IP \
  --end-ip-address YOUR_IP
```

### Issue: "Authentication failed"
**Solution**: Verify credentials in config.yaml match Azure portal

### Issue: "Dates showing as text"
**Solution**: Ensure proper date format in CSV (YYYY-MM-DD)

## Learning Resources

### Azure PostgreSQL
- [Official Documentation](https://docs.microsoft.com/azure/postgresql/)
- [Flexible Server Overview](https://docs.microsoft.com/azure/postgresql/flexible-server/overview)
- [Azure CLI Reference](https://docs.microsoft.com/cli/azure/postgres)

### Python & PostgreSQL
- [psycopg Documentation](https://www.psycopg.org/psycopg3/docs/)
- [pandas Documentation](https://pandas.pydata.org/docs/)
- [SQL Tutorial](https://www.postgresql.org/docs/current/tutorial.html)

## Workflow Examples

### Weekly Data Refresh
```bash
#!/bin/bash
# weekly_refresh.sh

cd /home/vbarcelo/repos/azure-sandbox/postgresql
source venv/bin/activate

# Upload new data (overwrites existing)
python upload_data.py data/weekly_sales.csv

# Log completion
echo "Weekly refresh completed at $(date)" >> refresh.log
```

### Automated Pipeline
```bash
#!/bin/bash
# automated_pipeline.sh

# 1. Download data from source
curl -o data/latest.csv https://source.com/data.csv

# 2. Upload to PostgreSQL
python upload_data.py data/latest.csv

# 3. Run analysis queries
psql "$CONNECTION_STRING" -f analysis.sql

# 4. Notify completion
echo "Pipeline completed successfully"
```

## Example Queries

### Sales Analysis
```sql
-- Total sales by product
SELECT 
    product,
    SUM(quantity) as total_quantity,
    SUM(quantity * price) as total_revenue
FROM sample_sales
GROUP BY product
ORDER BY total_revenue DESC;
```

### Customer Insights
```sql
-- Customers by country
SELECT 
    country,
    COUNT(*) as customer_count
FROM sample_customers
GROUP BY country;
```

### Time Series Analysis
```sql
-- Daily sales trend
SELECT 
    DATE(sale_date) as sale_day,
    COUNT(*) as transaction_count,
    SUM(quantity * price) as daily_revenue
FROM sample_sales
GROUP BY DATE(sale_date)
ORDER BY sale_day;
```

## Next Steps

### Immediate Actions
1. Deploy PostgreSQL server: `./deploy_postgres.sh`
2. Configure credentials: Edit `config.yaml`
3. Test connection: `python upload_data.py --test`
4. Upload sample data: `python upload_data.py data/`

### Future Enhancements
- [ ] Add data validation rules
- [ ] Implement incremental updates (append mode)
- [ ] Create data transformation pipeline
- [ ] Add scheduled refresh with cron
- [ ] Build Power BI/Grafana dashboards
- [ ] Implement data quality checks
- [ ] Add support for Excel files
- [ ] Create backup/restore scripts

## Maintenance

### Regular Tasks
- **Monitor storage usage**: Azure Portal → Your Server → Metrics
- **Review logs**: `cat upload_data.log`
- **Update dependencies**: `pip install --upgrade -r requirements.txt`
- **Backup data**: Use Azure automated backups or manual exports

### Cleanup
```bash
# Stop server (keeps data, stops billing)
az postgres flexible-server stop \
  --resource-group pg-datawarehouse-rg \
  --name your-server

# Delete everything
az group delete --name pg-datawarehouse-rg --yes
```

## Support

### Getting Help
1. Check `upload_data.log` for detailed errors
2. Review documentation: `README_DATAWAREHOUSE.md`
3. Verify Azure resources in portal
4. Test connection: `python upload_data.py --test`

### Reporting Issues
Include:
- Error messages (from terminal and log file)
- Configuration (without passwords!)
- Steps to reproduce
- Azure resource details

---

**Project Created**: December 2024  
**Platform**: Azure PostgreSQL Flexible Server  
**Language**: Python 3.8+  
**Target**: Azure for Students

Enjoy your data warehouse!
