import os
import logging
from typing import Dict, Any
import psycopg2
from psycopg2.extras import RealDictCursor
from tenacity import retry, stop_after_attempt, wait_exponential
from openai import OpenAI
from dotenv import load_dotenv
import asyncio
import time

# Import the Vanna integration module
try:
    # First try to import the real Vanna integration
    from vanna_integration import setup_vanna, generate_sql
    USING_MOCK = False
except Exception as e:
    # Fall back to mock implementation if real Vanna fails
    logging.warning(f"Failed to import real Vanna integration: {str(e)}")
    from mock_vanna_integration import setup_vanna, generate_sql
    USING_MOCK = True

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Vanna AI using the integration module
try:
    # Set up Vanna AI with proper configuration and training
    vn = setup_vanna()
    logger.info("Vanna AI initialized and trained successfully")
except Exception as e:
    logger.error(f"Error initializing Vanna AI: {str(e)}")
    # Fall back to mock implementation
    from mock_vanna_integration import setup_vanna
    vn = setup_vanna()
    logger.info("Falling back to mock Vanna AI implementation")

# Initialize OpenAI client
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise ValueError("OPENAI_API_KEY environment variable is not set")

# Create OpenAI client
openai_client = OpenAI(api_key=openai_api_key)

# Database connection parameters
DB_PARAMS = {
    'dbname': os.getenv('DB_NAME', 'votebank'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', ''),  # No default password for security
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432')
}


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def get_db_connection():
    """Get a database connection with retry logic"""
    return psycopg2.connect(**DB_PARAMS, cursor_factory=RealDictCursor)


def generate_sql_query(natural_query: str) -> str:
    """Generate SQL query using Vanna AI"""
    try:
        sql_query = generate_sql(vn, natural_query)
        logger.info(f"Generated SQL query: {sql_query}")
        return sql_query
    except Exception as e:
        logger.error(f"Error generating SQL query: {str(e)}")
        raise


def execute_sql_query(sql_query: str) -> list:
    """Execute SQL query and return results"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql_query)
                results = cur.fetchall()
                return results
    except Exception as e:
        logger.error(f"Error executing SQL query: {str(e)}")
        raise


def generate_natural_response(query: str, sql_query: str, results: list) -> str:
    """Generate natural language response using OpenAI"""
    try:
        # Format the results for better readability
        formatted_results = []
        for row in results:
            # Convert RealDictRow to regular dict for better serialization
            row_dict = dict(row)
            formatted_results.append(row_dict)
        
        # Prepare the prompt for OpenAI with better formatting
        prompt = f"""Given the following:
        - User's question: "{query}"
        - SQL query used: "{sql_query.strip()}"
        - Query results: {formatted_results}

        Please provide a natural language response that explains the results in a clear and concise way. 
        Be specific about the numbers and data shown in the results. 
        If the results are empty, explain that no data was found matching the criteria.
        Use the actual names, numbers, and values from the results in your explanation."""

        # Log the prompt for debugging
        logger.info(f"OpenAI prompt: {prompt}")

        # Use the new OpenAI API format
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that explains database query results in natural language. Always refer to the specific data in the results when answering."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )

        # Get the response content
        response_text = response.choices[0].message.content
        
        # Log the response for debugging
        logger.info(f"OpenAI response: {response_text}")
        
        return response_text
    except Exception as e:
        logger.error(f"Error generating natural response: {str(e)}")
        # Provide a fallback response with the raw results
        return f"Based on your question '{query}', I found the following results: {results}"


def process_query(query: str) -> Dict[str, Any]:
    """Process the user query and return results"""
    try:
        # Generate SQL query using Vanna AI
        sql_query = generate_sql_query(query)
        
        # Execute the SQL query
        results = execute_sql_query(sql_query)
        
        # Generate natural language response using OpenAI
        natural_response = generate_natural_response(query, sql_query, results)
        
        return {
            "sql_query": sql_query,
            "results": results,
            "natural_response": natural_response
        }
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise


async def stream_response(response: Dict[str, Any]):
    """
    Stream the response from the model
    """
    try:
        # Extract the natural response from the dictionary
        if isinstance(response, dict) and 'natural_response' in response:
            response_text = response['natural_response']
        else:
            response_text = str(response)
            
        # Split the response into words for streaming
        words = response_text.split()
        for word in words:
            yield word + " "
            await asyncio.sleep(0.1)  # Add a small delay between words
    except Exception as e:
        logger.error(f"Error streaming response: {str(e)}")
        raise Exception(f"Error streaming response: {str(e)}")


def process_user_query_complete(user_question):
    """
    Process user question through the complete workflow
    """
    try:
        response = process_query(user_question)
        return response
    except Exception as e:
        logger.error(f"Error in process_user_query_complete: {str(e)}")
        raise Exception(f"Error processing query: {str(e)}")
