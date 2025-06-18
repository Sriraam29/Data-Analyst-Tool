import os
import streamlit as st
from dotenv import load_dotenv
import pandas as pd

# Import custom modules first
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from components.file_upload import file_upload_component
from components.query_interface import query_interface_component
from components.results_display import results_display_component
from core.db.query_executor import execute_query

# Load environment variables
load_dotenv()

# Set page configuration
st.set_page_config(
    page_title="AI Data Analyst",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# App title and description
st.title("AI-Powered Data Analysis Agent")
st.markdown("""
    Upload your data and ask questions in plain English - no SQL knowledge required!
    This tool uses AI to analyze your tabular data and generate visualizations automatically.
""")

# Session state initialization
if 'uploaded_file_info' not in st.session_state:
    st.session_state.uploaded_file_info = {
        "file_object": None,
        "db_connection": None,
        "table_name": None,
        "schema": None,
        "initial_data": None
    }
if 'query_history' not in st.session_state:
    st.session_state.query_history = []
if 'last_query_results' not in st.session_state:
    st.session_state.last_query_results = None
if 'last_query' not in st.session_state:
    st.session_state.last_query = None

# --- File Upload Section --- (Always shown)
st.sidebar.header("1. Upload Data")
(st.session_state.uploaded_file_info["file_object"], 
 st.session_state.uploaded_file_info["db_connection"], 
 st.session_state.uploaded_file_info["table_name"], 
 st.session_state.uploaded_file_info["schema"]) = file_upload_component(
    st.session_state.uploaded_file_info["file_object"], 
    st.session_state.uploaded_file_info["db_connection"],
    st.sidebar # Pass sidebar as the container
)

# --- Main Area --- #

# Check if data has been loaded
data_loaded = (st.session_state.uploaded_file_info["db_connection"] is not None and 
               st.session_state.uploaded_file_info["table_name"] is not None)

if data_loaded:
    # Fetch initial data if not already done
    if st.session_state.uploaded_file_info["initial_data"] is None:
        try:
            with st.spinner("Loading initial data view..."):
                table = st.session_state.uploaded_file_info["table_name"]
                # Fetch first 1000 rows as initial preview
                initial_sql = f'SELECT * FROM "{table}" LIMIT 1000;' 
                st.session_state.uploaded_file_info["initial_data"] = execute_query(
                    st.session_state.uploaded_file_info["db_connection"], 
                    initial_sql, 
                    table # Pass table name for validation
                )
        except Exception as e:
            st.error(f"Error loading initial data: {e}")
            st.session_state.uploaded_file_info["initial_data"] = pd.DataFrame() # Set empty df on error

    # --- Query Interface Section --- #
    st.header("2. Ask Questions")
    query, sql, query_results = query_interface_component(
        st.session_state.uploaded_file_info["db_connection"],
        st.session_state.uploaded_file_info["table_name"],
        st.session_state.uploaded_file_info["schema"]
    )
    
    # Update history and last results if a new query ran successfully
    if query and sql and query_results is not None:
        st.session_state.query_history.append({
            "query": query,
            "sql": sql,
            "timestamp": pd.Timestamp.now()
        })
        st.session_state.last_query_results = query_results
        st.session_state.last_query = query
    elif query and query_results is None:
        # If query ran but failed, potentially clear old results
        # st.session_state.last_query_results = None # Optional: Decide if failed queries clear results
        pass

    # --- Results Display Section --- #
    st.divider()
    st.header("3. Analysis Results")
    
    # Decide what data to display
    if st.session_state.last_query_results is not None:
        # If a query has been run successfully, show its results
        st.markdown("**Showing results for your last query:**")
        results_display_component(
            st.session_state.last_query_results,
            st.session_state.last_query # Pass the query for context
        )
    elif st.session_state.uploaded_file_info["initial_data"] is not None:
        # Otherwise, show the initial data analysis if available
        st.markdown("**Initial Data Overview (first 1000 rows):**")
        results_display_component(
            st.session_state.uploaded_file_info["initial_data"],
            query=None # No specific query for initial view
        )
    else:
        # If initial data failed loading
        st.warning("Could not load initial data preview.")

else:
    # Shown when no file is loaded
    st.info("☝️ Please upload a data file using the sidebar to begin analysis")
    st.markdown("### Example queries you can ask:")
    st.markdown("""
    - "What is the average value of [column] by [category]?"
    - "Show me the top 5 rows sorted by [column] in descending order"
    - "Create a bar chart showing total [metric] by [dimension]"
    - "What is the correlation between [column1] and [column2]?"
    - "Show me the trend of [column] over time"
    """) 