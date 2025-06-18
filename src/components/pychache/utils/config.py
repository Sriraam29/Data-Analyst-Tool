import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# OpenAI API configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")  # Default to gpt-4o if not specified

# File upload settings
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "100"))  # Default 100MB
SUPPORTED_FILE_TYPES = ["csv", "xlsx", "xls"]  # Default supported file types

# Database settings
DB_IN_MEMORY = True  # Using in-memory DuckDB
MAX_QUERY_RESULTS = 10000  # Maximum number of rows to return from a query

# Application settings
APP_NAME = "AI Data Analysis Agent"
APP_DESCRIPTION = "Upload your data and analyze it using natural language queries" 