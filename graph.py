# backend/app/agents/sql_generator.py
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence
from langchain_core.runnables.history import RunnableWithMessageHistory
from ..utils.llm import local_llm
from ..utils.memory import get_memory
import logging
import os

logger = logging.getLogger(__name__)

# Import schema at module level to avoid circular imports
try:
    from ..utils.schema import db_schema
    SCHEMA_AVAILABLE = True
except ImportError:
    SCHEMA_AVAILABLE = False
    logger.warning("Schema utility not available, using fallback")

# Define the prompt template for SQL generation
SQL_PROMPT_TEMPLATE = """
You are an expert Teradata SQL query generator. Your task is to convert natural language queries into valid Teradata SQL.

IMPORTANT GUIDELINES:
1. Use only SELECT statements unless explicitly asked for DML operations
2. Always use proper Teradata SQL syntax
3. Be precise with column names and table names from the schema
4. Handle errors from previous attempts by analyzing and fixing the issues
5. Use appropriate JOINs when querying multiple tables
6. Include proper WHERE clauses for filtering
7. Use appropriate aggregate functions when needed

{schema}

Natural Language Query: {nl_query}

Previous SQL (if any): {previous_sql}
Previous Error (if any): {error}

Instructions:
- If there was a previous error, analyze it carefully and fix the SQL accordingly
- If this is a regeneration request, create an improved version addressing the issues
- Ensure proper table and column names from the schema above
- Use Teradata-specific syntax where needed
- Return only the SQL query, no explanations

Generate a valid Teradata SQL query:
"""

TABLE_NAME_PROMPT_TEMPLATE = """
Your task is to fetch the table name from this user query :{nl_query}, and return a list of 
table names in this format, do not provide anyother information, just fetch the tablename and respond a list. Just a list.
[tablename_1, tablename2]
"""

tablename_prompt = PromptTemplate(
    input_variables=["nl_query"],
    template=TABLE_NAME_PROMPT_TEMPLATE
)

sql_prompt = PromptTemplate(
    input_variables=["nl_query", "schema", "previous_sql", "error"],
    template=SQL_PROMPT_TEMPLATE
)

# LLM chain for SQL generation using modern RunnableSequence
sql_chain = sql_prompt | local_llm

table_sql_chain = tablename_prompt | local_llm


def get_table_sql_chain(session_id: str):
    memory = get_memory(session_id)
    # For now, return the basic chain. Memory integration can be enhanced later
    return table_sql_chain

# Wrap with memory for multi-turn conversations (simplified for now)
def get_sql_chain_with_memory(session_id: str):
    memory = get_memory(session_id)
    # For now, return the basic chain. Memory integration can be enhanced later
    return sql_chain

# ADK Integration: Assuming google-adk is installed, wrap as LlmAgent
try:
    from adk.agents import LlmAgent  # Adjust import based on actual package

    class SqlGeneratorAgent(LlmAgent):
        def __init__(self, session_id: str):
            super().__init__(llm=local_llm)  # ADK LlmAgent takes an LLM
            self.table_chain = get_table_sql_chain(session_id)
            self.chain = get_sql_chain_with_memory(session_id)
            self.session_id = session_id

        def process(self, input_data: dict) -> str:
            try:
                # Add schema to input data
                if SCHEMA_AVAILABLE:
                    input_data["schema"] = db_schema.get_schema_text()
                else:
                    schema_error = os.getenv("SQL_GENERATOR_SCHEMA_ERROR", "Schema service unavailable")
                    raise Exception(schema_error)
                
                tablename_response = self.chain.invoke(input_data)
                print(tablename_response)

                # Modern LangChain returns the content directly
                if hasattr(tablename_response, 'content'):
                    return tablename_response.content
                elif isinstance(tablename_response, str):
                    return tablename_response
                else:
                    return str(tablename_response)
            except Exception as e:
                logger.error(f"SQL generation failed: {str(e)}")
                raise Exception(f"SQL generation failed: {str(e)}")
            
        def process_table_schema(self, input_data: dict) -> str:
            try:
                # Add schema to input data
                if SCHEMA_AVAILABLE:
                    input_data["schema"] = db_schema.get_schema_text()
                else:
                    schema_error = os.getenv("SQL_GENERATOR_SCHEMA_ERROR", "Schema service unavailable")
                    raise Exception(schema_error)
                print('inside Here------------')
                response = self.table_chain.invoke(input_data)
                # Modern LangChain returns the content directly
                if hasattr(response, 'content'):
                    return response.content
                elif isinstance(response, str):
                    return response
                else:
                    return str(response)
            except Exception as e:
                logger.error(f"SQL generation failed: {str(e)}")
                raise Exception(f"SQL generation failed: {str(e)}")
            
except ImportError:
    # Fallback if ADK not available
    class SqlGeneratorAgent:
        def __init__(self, session_id: str):
            self.table_chain = get_table_sql_chain(session_id)
            self.chain = get_sql_chain_with_memory(session_id)
            self.session_id = session_id

        def process(self, input_data: dict) -> str:
            try:
                # Add schema to input data
                if SCHEMA_AVAILABLE:
                    input_data["schema"] = db_schema.get_schema_text()
                else:
                    schema_error = os.getenv("SQL_GENERATOR_SCHEMA_ERROR", "Schema service unavailable")
                    raise Exception(schema_error)
                print('inside Here------------2')
                response = self.chain.invoke(input_data)
                # Modern LangChain returns the content directly
                if hasattr(response, 'content'):
                    return response.content
                elif isinstance(response, str):
                    return response
                else:
                    return str(response)
            except Exception as e:
                logger.error(f"SQL generation failed: {str(e)}")
                raise Exception(f"SQL generation failed: {str(e)}")
        
            
        def process_table_schema(self, input_data: dict) -> str:
            try:
                # Add schema to input data
                if SCHEMA_AVAILABLE:
                    input_data["schema"] = db_schema.get_schema_text()
                else:
                    schema_error = os.getenv("SQL_GENERATOR_SCHEMA_ERROR", "Schema service unavailable")
                    raise Exception(schema_error)
                print('inside Here------------1')
                response = self.table_chain.invoke(input_data)
                print('Input Data-----', input_data)
                #print('Response from tablename---', response)
                # Modern LangChain returns the content directly
                if hasattr(response, 'content'):
                    return response.content
                elif isinstance(response, str):
                    return response
                else:
                    return str(response)
            except Exception as e:
                logger.error(f"SQL generation failed: {str(e)}")
                raise Exception(f"SQL generation failed: {str(e)}")
