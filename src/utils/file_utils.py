import os
import pandas as pd
import tempfile
from pathlib import Path

def get_file_extension(filename):
    """
    Get the extension of a file.
    
    Args:
        filename: The name of the file
        
    Returns:
        str: The file extension (lowercase, with dot)
    """
    return Path(filename).suffix.lower()

def save_uploaded_file(uploaded_file):
    """
    Save an uploaded file to a temporary location.
    
    Args:
        uploaded_file: The uploaded file from streamlit
        
    Returns:
        str: The path to the saved file
    """
    # Create a temporary file with the same extension
    extension = get_file_extension(uploaded_file.name)
    with tempfile.NamedTemporaryFile(delete=False, suffix=extension) as tmp_file:
        # Write the file to the temporary file
        tmp_file.write(uploaded_file.getvalue())
        tmp_path = tmp_file.name
    
    return tmp_path

def clean_up_file(file_path):
    """
    Remove a temporary file.
    
    Args:
        file_path: The path to the file to remove
    """
    try:
        if os.path.exists(file_path):
            os.unlink(file_path)
    except Exception as e:
        # Log the error but don't raise
        print(f"Error removing temporary file {file_path}: {str(e)}")

def get_supported_file_types():
    """
    Get a list of supported file types.
    
    Returns:
        list: List of supported file extensions
    """
    return ["csv", "xlsx", "xls"]

def validate_file_size(file, max_size_mb=100):
    """
    Validate that a file is not too large.
    
    Args:
        file: The file to validate
        max_size_mb: The maximum allowed file size in MB
        
    Returns:
        bool: True if the file size is acceptable
    """
    # Get file size in bytes
    file_size = file.size
    
    # Convert max size to bytes
    max_size_bytes = max_size_mb * 1024 * 1024
    
    return file_size <= max_size_bytes 