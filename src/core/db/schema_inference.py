import pandas as pd
import numpy as np
from datetime import datetime

def infer_schema(df):
    """
    Infer the schema from a pandas DataFrame.
    
    Args:
        df: The pandas DataFrame to analyze
        
    Returns:
        dict: A dictionary mapping column names to their data types
    """
    schema = {}
    
    for column in df.columns:
        # Get the pandas dtype first
        dtype = df[column].dtype
        
        # Check for numeric types
        if pd.api.types.is_integer_dtype(dtype):
            schema[column] = "INTEGER"
        elif pd.api.types.is_float_dtype(dtype):
            schema[column] = "FLOAT"
        
        # Check for boolean
        elif pd.api.types.is_bool_dtype(dtype):
            schema[column] = "BOOLEAN"
        
        # Check for datetime
        elif pd.api.types.is_datetime64_dtype(dtype):
            schema[column] = "DATETIME"
        
        # For string/object types, do a deeper inspection
        elif pd.api.types.is_string_dtype(dtype) or pd.api.types.is_object_dtype(dtype):
            # Skip empty columns
            if df[column].isna().all():
                schema[column] = "TEXT"
                continue
                
            # Try to infer datetime from string
            if is_probable_datetime(df[column]):
                schema[column] = "DATETIME"
            
            # Check if it's categorical (low number of unique values relative to total)
            elif is_probable_categorical(df[column]):
                schema[column] = "CATEGORICAL"
            
            # Default to text
            else:
                schema[column] = "TEXT"
        
        # Default for any other types
        else:
            schema[column] = "TEXT"
    
    return schema

def is_probable_datetime(series):
    """
    Determine if a series likely contains datetime values.
    
    Args:
        series: The pandas Series to check
        
    Returns:
        bool: True if the series likely contains datetime values
    """
    # Skip if too many nulls
    if series.isna().mean() > 0.5:
        return False
    
    # Sample a few non-NA values
    sample = series.dropna().sample(min(10, len(series.dropna()))).astype(str)
    
    # Common date patterns
    date_patterns = [
        # Try a few common date formats
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%m/%d/%Y",
        "%Y/%m/%d",
        "%d-%m-%Y",
        "%m-%d-%Y",
        
        # With time
        "%Y-%m-%d %H:%M:%S",
        "%d/%m/%Y %H:%M:%S",
        "%m/%d/%Y %H:%M:%S"
    ]
    
    success_count = 0
    for value in sample:
        for pattern in date_patterns:
            try:
                datetime.strptime(value, pattern)
                success_count += 1
                break
            except ValueError:
                continue
                
    # If more than 80% of samples are valid dates
    return success_count >= 0.8 * len(sample)

def is_probable_categorical(series):
    """
    Determine if a series likely contains categorical values.
    
    Args:
        series: The pandas Series to check
        
    Returns:
        bool: True if the series likely contains categorical values
    """
    # Count unique values
    n_unique = series.nunique()
    n_total = len(series)
    
    # If too few values, not meaningful to test
    if n_total < 10:
        return False
        
    # If few unique values relative to total rows
    if n_unique <= 20 or (n_unique / n_total) < 0.05:
        return True
        
    return False 