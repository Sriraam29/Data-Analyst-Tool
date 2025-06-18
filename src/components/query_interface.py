import streamlit as st
import pandas as pd
import time

# Import custom modules
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.nlp.nl_to_sql import generate_sql_from_nl_query
from core.db.query_executor import execute_query

def query_interface_component(db_connection, table_name, schema):
    """
    Component for handling natural language queries and converting them to SQL.
    
    Args:
        db_connection: The DuckDB connection
        table_name: The name of the table in DuckDB
        schema: The schema of the data
        
    Returns:
        tuple: (nl_query, generated_sql, query_results)
    """
    st.header("Ask Questions About Your Data")
    
    # Query input
    nl_query = st.text_area(
        "Ask a question about your data in plain English",
        placeholder="Example: What is the average of sales by region?",
        help="You can ask complex questions, request charts, or ask for statistical analysis"
    )
    
    # Initialize return values
    generated_sql = None
    query_results = None
    
    # Process query on button click
    if st.button("Run Query") and nl_query:
        print(f"[DEBUG] Run Query button clicked. Query: {nl_query}")
        with st.spinner("Analyzing your question..."):
            try:
                print("[DEBUG] Attempting to generate SQL...")
                # Generate SQL from natural language
                generated_sql = generate_sql_from_nl_query(nl_query, table_name, schema)
                print(f"[DEBUG] Generated SQL: {generated_sql}")
                
                # Display the generated SQL with a copy button
                with st.expander("Generated SQL Query", expanded=False):
                    st.code(generated_sql, language="sql")
                    
                print("[DEBUG] Attempting to execute query...")
                # Execute the query
                query_start_time = time.time()
                query_results = execute_query(db_connection, generated_sql, table_name)
                query_execution_time = time.time() - query_start_time
                print(f"[DEBUG] Query executed successfully. Result rows: {len(query_results)}")
                
                # Show query stats
                st.info(f"Query executed in {query_execution_time:.2f} seconds, returning {len(query_results)} rows")
                
            except Exception as e:
                print(f"[ERROR] Exception occurred: {str(e)}")
                st.error(f"Error processing query: {str(e)}")
                generated_sql = None
                query_results = None
    
    return nl_query, generated_sql, query_results 