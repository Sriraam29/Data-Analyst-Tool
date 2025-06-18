import streamlit as st
import pandas as pd
import os
import tempfile
from pathlib import Path

# Import custom modules
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.db.duckdb_manager import init_db_connection, load_data_to_db, close_connection
from core.db.schema_inference import infer_schema
from utils.file_utils import validate_file_size, get_supported_file_types
from utils.config import MAX_FILE_SIZE_MB

def file_upload_component(current_file, current_connection, container=st):
    """
    Component for handling file uploads, data parsing, and schema inference.
    Placed within the specified container (e.g., st.sidebar or st).
    
    Args:
        current_file: The currently uploaded file in session state
        current_connection: The current DuckDB connection in session state
        container: The Streamlit container to place the component in (defaults to main page)
        
    Returns:
        tuple: (uploaded_file_object, db_connection, table_name, schema)
    """
    # Initialize return values based on current state
    uploaded_file_object = current_file
    db_connection = current_connection
    table_name = None
    schema = None

    # File uploader within the specified container
    uploaded_file = container.file_uploader(
        "Upload your CSV or Excel file",
        type=get_supported_file_types(),
        help=f"Supported formats: {', '.join(get_supported_file_types())}. Max size: {MAX_FILE_SIZE_MB}MB"
    )
    
    # Process the uploaded file if it's new or different
    if uploaded_file is not None and (current_file is None or uploaded_file.name != current_file.name):
        print(f"[DEBUG] New file uploaded: {uploaded_file.name}") # Debug print
        
        # Close previous connection if it exists
        if current_connection:
            print("[DEBUG] Closing previous DB connection.") # Debug print
            close_connection(current_connection)
            db_connection = None # Reset connection

        with st.spinner("Processing your data..."):
            try:
                # Validate file size
                if not validate_file_size(uploaded_file, MAX_FILE_SIZE_MB):
                    container.error(f"File exceeds maximum size of {MAX_FILE_SIZE_MB}MB.")
                    return uploaded_file, None, None, None # Return error state
                
                # Get file extension
                file_extension = Path(uploaded_file.name).suffix.lower()
                
                # Read the data based on file type
                if file_extension == '.csv':
                    delimiter = container.selectbox(
                        "Select CSV delimiter", options=[",", ";", "\t", "|"], index=0, 
                        key=f"delimiter_{uploaded_file.name}_{uploaded_file.size}" # Use name and size for key
                    )
                    df = pd.read_csv(uploaded_file, sep=delimiter)
                    
                elif file_extension in ['.xlsx', '.xls']:
                    # Use name and size for the selectbox key
                    sheet_key = f"sheet_name_{uploaded_file.name}_{uploaded_file.size}"
                    xls = pd.ExcelFile(uploaded_file)
                    sheet_name = container.selectbox(
                         "Select sheet", options=xls.sheet_names, index=0, key=sheet_key
                    )
                    df = pd.read_excel(xls, sheet_name=sheet_name)
                else:
                    # This case should ideally not be reached due to 'type' filter
                    container.error(f"Unsupported file type: {file_extension}")
                    return uploaded_file, None, None, None # Return error state
                
                # Basic data info
                container.write(f"Rows: {df.shape[0]}, Columns: {df.shape[1]}")
                
                # Display data preview
                with container.expander("Data Preview (first 5 rows)", expanded=False):
                    st.dataframe(df.head(5), use_container_width=True) # Use st.dataframe for main area display
                
                # Infer schema
                schema = infer_schema(df)
                container.write("Schema inferred.") # Status update
                
                # Display inferred schema
                with container.expander("Inferred Schema", expanded=False):
                    schema_df = pd.DataFrame(schema.items(), columns=['Column', 'Inferred Type'])
                    st.dataframe(schema_df, use_container_width=True) # Use st.dataframe for main area display
                
                # Initialize DuckDB connection
                db_connection = init_db_connection()
                print("[DEBUG] Initialized new DB connection.") # Debug print
                
                # Load data to DuckDB
                table_name = load_data_to_db(db_connection, df, uploaded_file.name)
                print(f"[DEBUG] Loaded data into table: {table_name}") # Debug print
                
                container.success(f"Successfully processed '{uploaded_file.name}'")
                uploaded_file_object = uploaded_file # Update the file object state
                
            except Exception as e:
                print(f"[ERROR] Error processing file: {str(e)}") # Debug print
                container.error(f"Error processing file: {str(e)}")
                # Ensure connection is closed on error
                if db_connection:
                     close_connection(db_connection)
                return uploaded_file, None, None, None # Return error state
    
    elif uploaded_file is None and current_file is not None:
        # If the file is deselected/cleared, reset the state
        print("[DEBUG] File removed by user.") # Debug print
        if db_connection:
             close_connection(db_connection)
        uploaded_file_object = None
        db_connection = None
        table_name = None
        schema = None
        # Reset relevant session state parts (handled in app.py now)

    # Return the current state (might be unchanged if no new file)    
    return uploaded_file_object, db_connection, table_name, schema 