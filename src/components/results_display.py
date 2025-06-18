import streamlit as st
import pandas as pd
import numpy as np

# Import custom modules
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.viz.chart_generator import generate_chart
from core.viz.chart_recommendations import recommend_chart_type

def results_display_component(results, query=None):
    """
    Component for displaying query results and visualizations.
    
    Args:
        results: The pandas DataFrame with query results
        query: The natural language query that generated the results
        
    Returns:
        visualization: The generated visualization if any
    """
    # Initialize return value
    visualization = None
    
    # Only proceed if we have results
    if results is not None and not results.empty:
        st.header("Results")
        
        # Display tabs for different views of the data
        tab1, tab2, tab3 = st.tabs(["Data Table", "Visualization", "Statistics"])
        
        with tab1:
            # Data table display with search and sorting capabilities
            st.dataframe(results, use_container_width=True)
            
            # Download button for results
            csv = results.to_csv(index=False)
            st.download_button(
                label="Download Results as CSV",
                data=csv,
                file_name="query_results.csv",
                mime="text/csv"
            )
        
        with tab2:
            # Chart generation based on results and query
            if len(results) > 0:
                # Get chart recommendation
                chart_type = recommend_chart_type(results, query)
                
                # Let user override chart type
                available_charts = ["bar", "line", "scatter", "pie", "histogram", "heatmap", "box"]
                selected_chart = st.selectbox(
                    "Select visualization type",
                    options=available_charts,
                    index=available_charts.index(chart_type) if chart_type in available_charts else 0
                )
                
                # Generate and display the chart
                try:
                    with st.spinner("Generating visualization..."):
                        visualization = generate_chart(results, selected_chart, query)
                        st.plotly_chart(visualization, use_container_width=True)
                except Exception as e:
                    st.error(f"Error generating visualization: {str(e)}")
            else:
                st.info("No data available to visualize")
        
        with tab3:
            # Statistical summary of the results
            if results.shape[1] > 0 and results.shape[0] > 0:
                # Numeric columns
                numeric_cols = results.select_dtypes(include=[np.number]).columns.tolist()
                if numeric_cols:
                    st.subheader("Numeric Columns")
                    st.dataframe(results[numeric_cols].describe(), use_container_width=True)
                
                # Categorical columns
                cat_cols = results.select_dtypes(exclude=[np.number]).columns.tolist()
                if cat_cols:
                    st.subheader("Categorical Columns")
                    for col in cat_cols:
                        with st.expander(f"{col} - Value Counts"):
                            # Calculate value counts and reset index
                            value_counts_df = results[col].value_counts().reset_index()
                            # Explicitly assign final column names to avoid duplicates
                            value_counts_df.columns = [col, 'count'] 
                            st.dataframe(value_counts_df, use_container_width=True)
            else:
                st.info("No data available for statistical analysis")
    
    return visualization 