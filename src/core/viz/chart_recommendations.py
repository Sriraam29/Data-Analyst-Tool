import pandas as pd
import numpy as np
import re

def recommend_chart_type(df, query=None):
    """
    Recommend the best chart type based on the data and query.
    
    Args:
        df: The pandas DataFrame with query results
        query: The natural language query that generated the results
        
    Returns:
        str: The recommended chart type
    """
    # Default chart type
    default_chart = "bar"
    
    # Empty dataframe check
    if df is None or df.empty or df.shape[1] == 0:
        return default_chart
        
    # Use the query to infer intent if available
    if query:
        # Check for explicit chart type mentions
        chart_mentions = {
            "bar": ["bar chart", "bar graph", "barchart", "column chart"],
            "line": ["line chart", "line graph", "linechart", "trend", "over time", "time series"],
            "scatter": ["scatter plot", "scatterplot", "scatter chart", "relationship", "correlation"],
            "pie": ["pie chart", "piechart", "donut chart", "proportion"],
            "histogram": ["histogram", "distribution"],
            "box": ["box plot", "boxplot", "box and whisker", "whisker", "quartile"],
            "heatmap": ["heatmap", "heat map", "correlation matrix"]
        }
        
        # Check for mentions
        query_lower = query.lower()
        for chart_type, keywords in chart_mentions.items():
            if any(keyword in query_lower for keyword in keywords):
                return chart_type
    
    # Data-based recommendation (if no explicit mention in query)
    
    # Get numeric and non-numeric columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df.select_dtypes(exclude=[np.number]).columns.tolist()
    
    num_columns = df.shape[1]
    
    # Small number of columns with numeric and categorical data
    if 1 <= len(categorical_cols) <= 2 and 1 <= len(numeric_cols) <= 3:
        # For just 2 columns with 1 categorical and 1 numeric, use a bar chart
        if num_columns == 2 and len(categorical_cols) == 1 and len(numeric_cols) == 1:
            return "bar"
            
    # Time series detection
    datetime_cols = [col for col in df.columns if is_datetime_like(df[col])]
    if datetime_cols and len(numeric_cols) >= 1:
        return "line"
    
    # For two numeric columns, suggest scatter plot
    if len(numeric_cols) == 2 and len(categorical_cols) <= 1:
        return "scatter"
    
    # If single numeric column, suggest histogram
    if len(numeric_cols) == 1 and len(categorical_cols) == 0:
        return "histogram"
    
    # For many categorical columns and one numeric, suggest a heatmap
    if len(categorical_cols) >= 2 and len(numeric_cols) == 1:
        # Check if the data is suitable for a heatmap (not too sparse)
        if df.shape[0] <= 50:  # Not too many rows
            return "heatmap"
    
    # For proportion data (percentages adding to ~100), suggest pie chart
    if len(numeric_cols) == 1 and len(categorical_cols) == 1:
        if is_proportion_data(df, numeric_cols[0]):
            return "pie"
    
    # Default to bar chart for most other cases
    return default_chart

def is_datetime_like(series):
    """
    Check if a series contains datetime-like data.
    
    Args:
        series: The pandas Series to check
        
    Returns:
        bool: True if the series contains datetime-like data
    """
    # Check actual datetime dtype
    if pd.api.types.is_datetime64_dtype(series.dtype):
        return True
    
    # Check if series name suggests time
    if series.name:
        time_indicators = ["date", "time", "year", "month", "day", "created", "updated", "timestamp"]
        if any(indicator in str(series.name).lower() for indicator in time_indicators):
            return True
    
    return False

def is_proportion_data(df, numeric_col):
    """
    Check if a numeric column represents proportion data (summing to ~100%).
    
    Args:
        df: The DataFrame containing the data
        numeric_col: The name of the numeric column to check
        
    Returns:
        bool: True if the column likely represents proportion data
    """
    # Sum should be close to 100 or 1
    total = df[numeric_col].sum()
    
    # Check if sum is close to 100 (percentage) or 1 (proportion)
    return (0.95 <= total <= 1.05) or (95 <= total <= 105) 