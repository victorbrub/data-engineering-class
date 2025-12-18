# Azure PostgreSQL Data Warehouse - Quick Reference

## Quick Commands

### Deployment
```bash
# Bash
chmod +x deploy_postgres.sh
./deploy_postgres.sh

# PowerShell
.\deploy_postgres.ps1
```

### Setup Python Environment
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Test Connection
```bash
python upload_data.py --test
```

### Upload Data
```bash
# Single file
python upload_data.py data/sales.csv

# Entire directory
python upload_data.py data/

# Custom table name
python upload_data.py data/file.csv --table my_table
```

## Project Structure

```
postgresql/
├── deploy_postgres.sh       # Bash deployment script
├── deploy_postgres.ps1      # PowerShell deployment script
├── upload_data.py           # Python upload script
├── requirements.txt         # Python dependencies
├── config.example.yaml      # Configuration template
├── config.yaml             # Your config (not committed)
├── README_DATAWAREHOUSE.md # Full documentation
├── QUICKSTART.md           # This file
├── .gitignore              # Git ignore patterns
└── data/                   # Data files directory
    ├── sample_sales.csv
    └── sample_customers.json
```

## Configuration

1. Copy example config:
   ```bash
   cp config.example.yaml config.yaml
   ```

2. Edit `config.yaml` with your credentials:
   ```yaml
   database:
     host: "your-server.postgres.database.azure.com"
     password: "YourPassword123"
   ```

## Connection String Format

```
postgresql://username:password@host:5432/database?sslmode=require
```

## Common Tasks

### Check Server Status
```bash
az postgres flexible-server show \
  --resource-group pg-datawarehouse-rg \
  --name your-server-name
```

### Add Firewall Rule
```bash
az postgres flexible-server firewall-rule create \
  --resource-group pg-datawarehouse-rg \
  --name your-server-name \
  --rule-name MyIP \
  --start-ip-address YOUR_IP \
  --end-ip-address YOUR_IP
```

### Connect with psql
```bash
psql "host=your-server.postgres.database.azure.com \
      port=5432 \
      dbname=datawarehouse \
      user=pgadmin \
      sslmode=require"
```

### Delete Resources
```bash
az group delete --name pg-datawarehouse-rg --yes
```

## Verify Upload

```sql
-- List all tables
\dt

-- View table structure
\d table_name

-- Count rows
SELECT COUNT(*) FROM table_name;

-- View sample data
SELECT * FROM table_name LIMIT 10;
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Connection timeout | Check firewall rules |
| Auth failed | Verify credentials in config.yaml |
| Module not found | Run `pip install -r requirements.txt` |
| Upload slow | Increase chunk_size in config.yaml |

## Cost Optimization (Students)

- Use Burstable tier: `Standard_B1ms` (default)
- Minimum storage: 32 GB
- Stop server when not in use:
  ```bash
  az postgres flexible-server stop --resource-group pg-datawarehouse-rg --name your-server
  ```
- Start server:
  ```bash
  az postgres flexible-server start --resource-group pg-datawarehouse-rg --name your-server
  ```

## Learn More

- Full docs: `README_DATAWAREHOUSE.md`
- Azure PostgreSQL: https://docs.microsoft.com/azure/postgresql/
- Python psycopg: https://www.psycopg.org/psycopg3/

---
**Got issues?** Check `upload_data.log` for detailed error messages.
