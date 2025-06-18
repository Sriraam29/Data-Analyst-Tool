import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

def generate_chart(df, chart_type, query=None):
    """
    Generate a Plotly chart based on the data and specified chart type.
    
    Args:
        df: The pandas DataFrame with query results
        chart_type: The type of chart to generate ("bar", "line", etc.)
        query: The natural language query that generated the results
        
    Returns:
        plotly.graph_objects.Figure: The generated chart
    """
    # Handle empty data
    if df.empty:
        # Return an empty figure with a message
        fig = go.Figure()
        fig.add_annotation(
            text="No data available for visualization",
            showarrow=False,
            font=dict(size=20)
        )
        return fig
    
    # Get numeric and categorical columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df.select_dtypes(exclude=[np.number]).columns.tolist()
    
    # Charts that need both numeric and categorical data
    if chart_type in ["bar", "line", "pie"] and (not numeric_cols or not categorical_cols):
        # Try to find reasonable columns to use
        if df.shape[1] >= 2:
            # If we have at least two columns, use the first as x and second as y
            x_col = df.columns[0]
            y_col = df.columns[1]
        else:
            # Fall back to using the index
            x_col = df.index.name or "Index"
            y_col = df.columns[0]
    else:
        # Default column selection based on data types
        x_col = categorical_cols[0] if categorical_cols else (df.index.name or df.columns[0])
        y_col = numeric_cols[0] if numeric_cols else df.columns[-1]  # Last column as fallback
    
    # Additional columns for color/size dimensions
    color_col = categorical_cols[1] if len(categorical_cols) > 1 else None
    size_col = numeric_cols[1] if len(numeric_cols) > 1 else None
    
    # Chart title generation
    if query:
        # Try to create a title from the query
        title = f"Results for: {query}"
    else:
        # Create a generic title based on selected columns
        title = f"{y_col} by {x_col}"
    
    # Generate specific chart type
    try:
        if chart_type == "bar":
            # Bar chart
            fig = px.bar(
                df, x=x_col, y=y_col, color=color_col,
                title=title,
                labels={x_col: x_col, y_col: y_col},
                template="plotly_white"
            )
            
        elif chart_type == "line":
            # Line chart
            fig = px.line(
                df, x=x_col, y=y_col, color=color_col,
                title=title, 
                labels={x_col: x_col, y_col: y_col},
                template="plotly_white"
            )
            
        elif chart_type == "scatter":
            # Scatter plot
            fig = px.scatter(
                df, x=x_col, y=y_col, color=color_col, size=size_col,
                title=title,
                labels={x_col: x_col, y_col: y_col},
                template="plotly_white"
            )
            
        elif chart_type == "pie":
            # Pie chart - use the first categorical column and first numeric column
            fig = px.pie(
                df, names=x_col, values=y_col,
                title=title,
                template="plotly_white"
            )
            
        elif chart_type == "histogram":
            # Histogram - use the first numeric column
            col_to_use = numeric_cols[0] if numeric_cols else df.columns[0]
            fig = px.histogram(
                df, x=col_to_use, color=color_col,
                title=f"Distribution of {col_to_use}",
                template="plotly_white"
            )
            
        elif chart_type == "box":
            # Box plot
            fig = px.box(
                df, x=categorical_cols[0] if categorical_cols else None, 
                y=numeric_cols[0] if numeric_cols else df.columns[0],
                color=color_col,
                title=f"Distribution of {y_col}" + (f" by {x_col}" if categorical_cols else ""),
                template="plotly_white"
            )
            
        elif chart_type == "heatmap":
            # Try to create a pivot table for the heatmap
            if len(categorical_cols) >= 2 and len(numeric_cols) >= 1:
                # Create a pivot table
                pivot_df = df.pivot_table(
                    index=categorical_cols[0],
                    columns=categorical_cols[1],
                    values=numeric_cols[0],
                    aggfunc='mean'
                )
                
                # Create heatmap
                fig = px.imshow(
                    pivot_df,
                    labels=dict(x=categorical_cols[1], y=categorical_cols[0], color=numeric_cols[0]),
                    title=f"Heatmap of {numeric_cols[0]} by {categorical_cols[0]} and {categorical_cols[1]}",
                    template="plotly_white"
                )
            else:
                # Fallback to correlation heatmap if we have multiple numeric columns
                if len(numeric_cols) >= 2:
                    corr_df = df[numeric_cols].corr()
                    fig = px.imshow(
                        corr_df,
                        labels=dict(x="Features", y="Features", color="Correlation"),
                        title="Correlation Heatmap",
                        template="plotly_white"
                    )
                else:
                    # If we can't create a heatmap, fall back to a bar chart
                    fig = px.bar(
                        df, x=x_col, y=y_col,
                        title="Data visualization (heatmap not applicable)",
                        template="plotly_white"
                    )
        else:
            # Default to bar chart for unknown types
            fig = px.bar(
                df, x=x_col, y=y_col,
                title=title,
                template="plotly_white"
            )
            
        # Add layout improvements
        fig.update_layout(
            autosize=True,
            margin=dict(l=50, r=50, b=100, t=100, pad=4),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
            
        return fig
        
    except Exception as e:
        # On error, return a simple figure with error message
        fig = go.Figure()
        fig.add_annotation(
            text=f"Error generating chart: {str(e)}",
            showarrow=False,
            font=dict(size=14)
        )
        return fig 