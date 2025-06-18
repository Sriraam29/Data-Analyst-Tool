# Data-Analyst-tool
Build an intelligent web application that empowers non-technical users to analyze tabular data through natural language, eliminating the need for SQL knowledge or programming skills.

## Core Architecture

### High-Level Components
1. **Frontend Interface** (Streamlit)
   - File upload component
   - Natural language query input
   - Results display (tables, charts, statistics)

2. **Data Processing Pipeline**
   - File parsing and schema inference
   - DuckDB in-memory database integration
   - Query execution engine

3. **AI Language Understanding**
   - Natural language to SQL conversion
   - Query refinement and disambiguation
   - Visualization recommendation

### Technical Architecture
```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│                 │      │                 │      │                 │
│   Streamlit     │◄────►│  Data Pipeline  │◄────►│  OpenAI API     │
│   Web Interface │      │  (DuckDB)       │      │  (LLM Services) │
│                 │      │                 │      │                 │
└─────────────────┘      └─────────────────┘      └─────────────────┘
```

## Technology Stack

### Core Technologies
- **Python 3.9+**: Primary development language
- **Streamlit**: Web interface framework
- **DuckDB**: In-memory analytical database
- **OpenAI API**: Large language model for NL→SQL conversion
- **Pandas**: Initial data loading and manipulation
- **Plotly**: Interactive data visualization
- **pytest**: For testing framework

### Key Design Decisions
1. Use **Streamlit** for rapid development of data applications with minimal frontend code
2. Choose **DuckDB** over SQLite for superior analytical query performance
3. Leverage **OpenAI's GPT models** for natural language understanding and SQL generation
4. Implement **in-memory processing** to avoid persisting user data unnecessarily

## Constraints and Considerations

### Technical Constraints
- **Memory Usage**: In-memory processing limits dataset size (recommend <100MB initially)
- **API Rate Limits**: OpenAI API has rate limits and costs per token
- **Stateless Design**: Streamlit's stateless nature requires careful state management

### Security Considerations
- No persistent storage of user data beyond session
- Sanitize all user inputs before processing
- Validate generated SQL queries before execution

## Project Structure
```
/data          # Sample datasets for testing
/src
  /components  # Streamlit UI components
  /core        # Core business logic
    /db        # DuckDB integration
    /nlp       # NL→SQL conversion logic
    /viz       # Visualization generation
  /utils       # Helper functions and utilities
/tests         # Test cases
/configs       # Configuration files
```

## Development Approach
1. **Modular Development**: Build independent modules that can be tested separately
2. **Iterative Testing**: Continuously test with various datasets and query types
3. **Progressive Enhancement**: Start with core functionality, then add advanced features 
