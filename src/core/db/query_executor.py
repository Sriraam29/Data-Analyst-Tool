import pandas as pd
import re

def sanitize_sql(sql_query):
    """
    Sanitize a SQL query to prevent SQL injection.
    
    Args:
        sql_query: The SQL query to sanitize
        
    Returns:
        str: The sanitized SQL query
    """
    # Remove multiple semicolons
    sanitized = re.sub(r';\s*;', ';', sql_query)
    
    # Prevent multiple queries by keeping only the first query
    if ';' in sanitized:
        sanitized = sanitized.split(';')[0] + ';'
        
    # Check for dangerous operations
    dangerous_operations = [
        r'\bDROP\s+TABLE\b',
        r'\bDROP\s+DATABASE\b',
        r'\bDELETE\s+FROM\b',
        r'\bTRUNCATE\b',
        r'\bALTER\s+TABLE\b',
        r'\bCREATE\s+TABLE\b',
        r'\bINSERT\s+INTO\b',
        r'\bUPDATE\b'
    ]
    
    for pattern in dangerous_operations:
        if re.search(pattern, sanitized, re.IGNORECASE):
            raise ValueError(f"SQL query contains potentially harmful operations: {pattern}")
    
    return sanitized

def validate_query(sql_query, table_name):
    """
    Validate that a SQL query is only accessing the specified table.
    
    Args:
        sql_query: The SQL query to validate
        table_name: The name of the allowed table
        
    Returns:
        bool: True if the query is valid
    """
    # Very basic validation
    # In a real application, you would use a proper SQL parser
    
    # Check for table mentions that aren't the allowed table
    tables = re.findall(r'FROM\s+([a-zA-Z0-9_]+)', sql_query, re.IGNORECASE)
    tables.extend(re.findall(r'JOIN\s+([a-zA-Z0-9_]+)', sql_query, re.IGNORECASE))
    
    for table in tables:
        if table.strip() != table_name:
            raise ValueError(f"Query contains unauthorized table: {table}")
    
    return True

def execute_query(connection, sql_query, table_name=None):
    """
    Execute a SQL query against the DuckDB connection.
    
    Args:
        connection: The DuckDB connection
        sql_query: The SQL query to execute
        table_name: Optional. If provided, validates the query only accesses this table
        
    Returns:
        pandas.DataFrame: The query results as a DataFrame
    """
    # Sanitize the query
    sanitized_query = sanitize_sql(sql_query)
    
    # Validate the query if table_name is provided
    if table_name:
        validate_query(sanitized_query, table_name)
    
    # Execute the query
    try:
        result = connection.execute(sanitized_query).fetchdf()
        return result
    except Exception as e:
        # Log the error and re-raise
        print(f"Error executing query: {str(e)}")
        raise 