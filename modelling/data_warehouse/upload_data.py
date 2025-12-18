"""
PostgreSQL Data Uploader
This script uploads CSV and JSON files to Azure PostgreSQL Flexible Server,
automatically creating tables based on file names.
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Union
import yaml
import psycopg
import pandas as pd
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('upload_data.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class PostgreSQLUploader:
    """Handles uploading CSV/JSON files to PostgreSQL database."""
    
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize uploader with configuration."""
        self.config = self._load_config(config_path)
        self.conn_string = self._build_connection_string()
        self.chunk_size = self.config.get('upload', {}).get('chunk_size', 1000)
        
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            logger.info(f"Configuration loaded from {config_path}")
            return config
        except FileNotFoundError:
            logger.error(f"Config file not found: {config_path}")
            raise
        except yaml.YAMLError as e:
            logger.error(f"Error parsing config file: {e}")
            raise
    
    def _build_connection_string(self) -> str:
        """Build PostgreSQL connection string from config."""
        db_config = self.config['database']
        
        # Validate required fields
        required_fields = ['host', 'port', 'database', 'user', 'password']
        for field in required_fields:
            if not db_config.get(field):
                raise ValueError(f"Missing required database config: {field}")
        
        conn_string = (
            f"host={db_config['host']} "
            f"port={db_config['port']} "
            f"dbname={db_config['database']} "
            f"user={db_config['user']} "
            f"password={db_config['password']} "
            f"sslmode={db_config.get('sslmode', 'require')}"
        )
        
        logger.info(f"Connection string built for database: {db_config['database']}")
        return conn_string
    
    def test_connection(self) -> bool:
        """Test database connection."""
        try:
            with psycopg.connect(self.conn_string) as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT version();")
                    version = cursor.fetchone()[0]
                    logger.info(f"Successfully connected to PostgreSQL: {version}")
                    return True
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False
    
    def _sanitize_table_name(self, filename: str) -> str:
        """Convert filename to valid PostgreSQL table name."""
        # Remove extension and path
        table_name = Path(filename).stem
        
        # Replace invalid characters with underscores
        table_name = ''.join(c if c.isalnum() else '_' for c in table_name)
        
        # Ensure it starts with a letter
        if not table_name[0].isalpha():
            table_name = 'table_' + table_name
        
        # Convert to lowercase
        table_name = table_name.lower()
        
        logger.info(f"Sanitized table name: {filename} -> {table_name}")
        return table_name
    
    def _pandas_dtype_to_postgres(self, dtype) -> str:
        """Map pandas dtypes to PostgreSQL data types."""
        dtype_str = str(dtype)
        
        if 'int' in dtype_str:
            return 'BIGINT'
        elif 'float' in dtype_str:
            return 'DOUBLE PRECISION'
        elif 'bool' in dtype_str:
            return 'BOOLEAN'
        elif 'datetime' in dtype_str:
            return 'TIMESTAMP'
        elif 'date' in dtype_str:
            return 'DATE'
        else:
            return 'TEXT'
    
    def _create_table_from_dataframe(self, conn, table_name: str, df: pd.DataFrame):
        """Create table schema based on DataFrame structure."""
        # Generate column definitions
        column_defs = []
        for col_name, dtype in df.dtypes.items():
            # Sanitize column name
            sanitized_col = ''.join(c if c.isalnum() else '_' for c in str(col_name)).lower()
            pg_type = self._pandas_dtype_to_postgres(dtype)
            column_defs.append(f'"{sanitized_col}" {pg_type}')
        
        # Add auto-increment ID and timestamp
        column_defs.insert(0, 'id SERIAL PRIMARY KEY')
        column_defs.append('uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP')
        
        # Create table
        create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            {', '.join(column_defs)}
        );
        """
        
        with conn.cursor() as cursor:
            cursor.execute(create_table_sql)
            conn.commit()
            logger.info(f"Table '{table_name}' created/verified successfully")
    
    def _truncate_table(self, conn, table_name: str):
        """Truncate existing table data."""
        with conn.cursor() as cursor:
            cursor.execute(f"TRUNCATE TABLE {table_name} RESTART IDENTITY CASCADE;")
            conn.commit()
            logger.info(f"Table '{table_name}' truncated")
    
    def _insert_dataframe(self, conn, table_name: str, df: pd.DataFrame):
        """Insert DataFrame data into table using batch inserts."""
        if df.empty:
            logger.warning(f"DataFrame is empty, skipping insert for {table_name}")
            return
        
        # Sanitize column names to match table
        df.columns = [''.join(c if c.isalnum() else '_' for c in str(col)).lower() 
                      for col in df.columns]
        
        # Get column names (excluding id and uploaded_at which are auto-generated)
        columns = df.columns.tolist()
        placeholders = ', '.join(['%s'] * len(columns))
        columns_str = ', '.join([f'"{col}"' for col in columns])
        
        insert_sql = f"""
        INSERT INTO {table_name} ({columns_str})
        VALUES ({placeholders})
        """
        
        # Insert in chunks
        total_rows = len(df)
        inserted_rows = 0
        
        with conn.cursor() as cursor:
            for i in range(0, total_rows, self.chunk_size):
                chunk = df.iloc[i:i + self.chunk_size]
                rows = [tuple(row) for row in chunk.values]
                
                cursor.executemany(insert_sql, rows)
                inserted_rows += len(rows)
                logger.info(f"Inserted {inserted_rows}/{total_rows} rows into {table_name}")
            
            conn.commit()
        
        logger.info(f"Successfully inserted {total_rows} rows into '{table_name}'")
    
    def upload_csv(self, file_path: str, table_name: Optional[str] = None):
        """Upload CSV file to PostgreSQL."""
        try:
            logger.info(f"Processing CSV file: {file_path}")
            
            # Read CSV with pandas
            df = pd.read_csv(file_path)
            logger.info(f"Loaded {len(df)} rows from CSV")
            
            # Determine table name
            if not table_name:
                table_name = self._sanitize_table_name(file_path)
            
            # Connect and upload
            with psycopg.connect(self.conn_string) as conn:
                # Create or recreate table
                self._create_table_from_dataframe(conn, table_name, df)
                
                # Truncate existing data
                self._truncate_table(conn, table_name)
                
                # Insert new data
                self._insert_dataframe(conn, table_name, df)
            
            logger.info(f"CSV upload completed: {file_path} -> {table_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error uploading CSV {file_path}: {e}")
            return False
    
    def upload_json(self, file_path: str, table_name: Optional[str] = None):
        """Upload JSON file to PostgreSQL."""
        try:
            logger.info(f"Processing JSON file: {file_path}")
            
            # Read JSON with pandas (supports both array of objects and nested structures)
            df = pd.read_json(file_path)
            
            # If JSON is a single object, convert to single-row DataFrame
            if not isinstance(df, pd.DataFrame):
                df = pd.DataFrame([df])
            
            logger.info(f"Loaded {len(df)} rows from JSON")
            
            # Determine table name
            if not table_name:
                table_name = self._sanitize_table_name(file_path)
            
            # Connect and upload
            with psycopg.connect(self.conn_string) as conn:
                # Create or recreate table
                self._create_table_from_dataframe(conn, table_name, df)
                
                # Truncate existing data
                self._truncate_table(conn, table_name)
                
                # Insert new data
                self._insert_dataframe(conn, table_name, df)
            
            logger.info(f"JSON upload completed: {file_path} -> {table_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error uploading JSON {file_path}: {e}")
            return False
    
    def upload_file(self, file_path: str, table_name: Optional[str] = None):
        """Upload file (CSV or JSON) based on extension."""
        file_path = Path(file_path)
        
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            return False
        
        extension = file_path.suffix.lower()
        
        if extension == '.csv':
            return self.upload_csv(str(file_path), table_name)
        elif extension == '.json':
            return self.upload_json(str(file_path), table_name)
        else:
            logger.error(f"Unsupported file type: {extension}")
            return False
    
    def upload_directory(self, directory_path: str):
        """Upload all CSV and JSON files from a directory."""
        directory = Path(directory_path)
        
        if not directory.exists() or not directory.is_dir():
            logger.error(f"Directory not found: {directory_path}")
            return
        
        # Find all CSV and JSON files
        files = list(directory.glob('*.csv')) + list(directory.glob('*.json'))
        
        if not files:
            logger.warning(f"No CSV or JSON files found in {directory_path}")
            return
        
        logger.info(f"Found {len(files)} files to upload")
        
        success_count = 0
        fail_count = 0
        
        for file_path in files:
            if self.upload_file(str(file_path)):
                success_count += 1
            else:
                fail_count += 1
        
        logger.info(f"Upload summary: {success_count} succeeded, {fail_count} failed")


def main():
    """Main execution function."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Upload CSV/JSON files to Azure PostgreSQL'
    )
    parser.add_argument(
        'path',
        help='Path to file or directory to upload'
    )
    parser.add_argument(
        '--table',
        help='Custom table name (only for single file uploads)',
        default=None
    )
    parser.add_argument(
        '--config',
        help='Path to config file',
        default='config.yaml'
    )
    parser.add_argument(
        '--test',
        help='Test database connection only',
        action='store_true'
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize uploader
        uploader = PostgreSQLUploader(args.config)
        
        # Test connection if requested
        if args.test:
            if uploader.test_connection():
                print("Database connection successful!")
                sys.exit(0)
            else:
                print("Database connection failed!")
                sys.exit(1)
        
        # Process path
        path = Path(args.path)
        
        if path.is_file():
            success = uploader.upload_file(str(path), args.table)
            sys.exit(0 if success else 1)
        elif path.is_dir():
            uploader.upload_directory(str(path))
            sys.exit(0)
        else:
            logger.error(f"Invalid path: {args.path}")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
