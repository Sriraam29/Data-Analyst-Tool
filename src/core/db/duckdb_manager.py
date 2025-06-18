import duckdb
import pandas as pd
import os
import re
from pathlib import Path

def init_db_connection():
    """
    Initialize an in-memory DuckDB connection.
    
    Returns:
        duckdb.DuckDBPyConnection: A DuckDB connection object
    """
    return duckdb.connect(database=':memory:')

def load_data_to_db(connection, dataframe, filename):
    """
    Load a pandas DataFrame into a DuckDB table.
    
    Args:
        connection: The DuckDB connection
        dataframe: The pandas DataFrame to load
        filename: The original filename, used to generate a table name
        
    Returns:
        str: The name of the created table
    """
    # Generate a safe table name from the file name
    base_name = Path(filename).stem
    table_name = re.sub(r'[^a-zA-Z0-9_]', '_', base_name).lower()
    
    # Ensure the table name is unique and valid
    if not table_name or table_name[0].isdigit():
        table_name = f"data_{table_name}"
    
    # Register the DataFrame as a table
    connection.register(table_name, dataframe)
    
    # Create a persistent table from the registered view
    connection.execute(f"CREATE TABLE {table_name} AS SELECT * FROM {table_name}")
    
    return table_name

def get_table_info(connection, table_name):
    """
    Get information about a table in DuckDB.
    
    Args:
        connection: The DuckDB connection
        table_name: The name of the table
        
    Returns:
        dict: Information about the table, including columns and types
    """
    # Get column information
    column_info = connection.execute(f"PRAGMA table_info({table_name})").fetchall()
    
    # Convert to dict format
    table_info = {
        'name': table_name,
        'columns': [{'name': col[1], 'type': col[2]} for col in column_info]
    }
    
    return table_info

def drop_table(connection, table_name):
    """
    Drop a table from DuckDB.
    
    Args:
        connection: The DuckDB connection
        table_name: The name of the table to drop
    """
    connection.execute(f"DROP TABLE IF EXISTS {table_name}")

def close_connection(connection):
    """
    Close a DuckDB connection.
    
    Args:
        connection: The DuckDB connection to close
    """
    if connection:
        connection.close() 