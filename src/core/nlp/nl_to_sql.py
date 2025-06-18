import os
import openai
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Set OpenAI API key from environment
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_sql_from_nl_query(nl_query, table_name, schema):
    """
    Convert a natural language query to SQL using OpenAI's API.
    
    Args:
        nl_query: The natural language query from the user
        table_name: The name of the table to query
        schema: The schema of the table (dict mapping column names to types)
        
    Returns:
        str: The generated SQL query
    """
    if not openai.api_key:
        raise ValueError("OpenAI API key not found. Please set OPENAI_API_KEY environment variable.")
    
    # Construct schema information for the prompt
    schema_info = "\n".join([f"- {col_name} ({col_type})" for col_name, col_type in schema.items()])
    
    # Build system message with context
    system_message = f"""
    You are an expert SQL query generator. Your task is to convert natural language questions about data into SQL queries. 
    
    The table name is: `{table_name}`
    
    The schema of the table is:
    {schema_info}
    
    Rules for generating SQL:
    1. Only use the columns that exist in the schema.
    2. Always use proper SQL syntax compatible with DuckDB.
    3. Do not include any explanations, only return the SQL query.
    4. Always use double quotes for column names, especially if they contain spaces or special characters.
    5. For aggregate queries with GROUP BY, include the grouping columns in the SELECT clause.
    6. Make educated guesses about what columns to use based on the query and schema.
    7. Always limit results to at most 1000 rows by default with LIMIT 1000.
    8. If the question asks for a specific number of results (e.g. "top 5"), use LIMIT appropriately.
    """
    
    try:
        # Create a chat completion
        response = openai.ChatCompletion.create(
            model="gpt-4o",  # Use gpt-4o
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": nl_query}
            ],
            temperature=0.1,  # Low temperature for more deterministic output
            max_tokens=300    # Limit response length
        )
        
        # Extract the SQL query from the response
        sql_query = response.choices[0].message['content'].strip()
        
        # If the response includes backticks, extract just the SQL part
        if "```sql" in sql_query:
            sql_query = sql_query.split("```sql")[1].split("```")[0].strip()
        elif "```" in sql_query:
            sql_query = sql_query.split("```")[1].strip()
            
        return sql_query
        
    except Exception as e:
        raise Exception(f"Error generating SQL from natural language: {str(e)}")


def extract_query_intent(nl_query):
    """
    Extract the user's intent from a natural language query.
    
    Args:
        nl_query: The natural language query from the user
        
    Returns:
        dict: Information about the query intent (aggregation, filters, etc.)
    """
    try:
        # Create a chat completion
        response = openai.ChatCompletion.create(
            model="gpt-4o", # Use gpt-4o
            messages=[
                {"role": "system", "content": """
                You need to extract the query intent from a natural language question about data.
                Return a JSON object with the following properties:
                - aggregation_type: The type of aggregation (count, sum, average, etc.) or "none"
                - dimensions: List of columns to group by or []
                - measures: List of columns to aggregate or []
                - filters: List of filter conditions or []
                - sort: List of columns to sort by with direction or []
                - limit: Number of records to return or null
                """},
                {"role": "user", "content": nl_query}
            ],
            temperature=0.1,
            max_tokens=200,
            response_format={"type": "json_object"}
        )
        
        # Extract the JSON response
        intent = json.loads(response.choices[0].message['content'])
        return intent
        
    except Exception as e:
        # If we can't get the intent, return a default structure
        return {
            "aggregation_type": "none",
            "dimensions": [],
            "measures": [],
            "filters": [],
            "sort": [],
            "limit": None
        } 