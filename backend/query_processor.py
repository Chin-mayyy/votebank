import vanna
from vanna.remote import VannaDefault
import psycopg2
from openai import OpenAI
import os
from dotenv import load_dotenv
import asyncio
import logging
import time
from tenacity import retry, stop_after_attempt, wait_exponential

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize Vanna AI
vn = VannaDefault(
    api_key=os.getenv("VANNA_API_KEY"),
    model="chinmay/votebank"
)

# Initialize OpenAI client
try:
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key or openai_api_key.startswith("your_"):
        raise ValueError("OpenAI API key is not properly configured in .env file")
    client = OpenAI(api_key=openai_api_key)
    logger.info("OpenAI client initialized successfully")
except Exception as e:
    logger.error(f"Error initializing OpenAI client: {str(e)}")
    raise

# Database connection parameters
db_params = {
    "dbname": "votebank",
    "user": "chinmay",
    "password": "votebank123",
    "host": "localhost",
    "port": "5432"
}

def connect_to_database():
    """Establish connection to PostgreSQL database"""
    try:
        conn = psycopg2.connect(**db_params)
        return conn
    except Exception as e:
        logger.error(f"Error connecting to database: {e}")
        return None

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def process_user_query(question: str):
    """
    Process the user's query using GPT-3.5-turbo with retry logic
    """
    try:
        logger.info(f"Processing query: {question}")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that answers questions about voting data."},
                {"role": "user", "content": question}
            ],
            max_tokens=150,
            temperature=0.7,
            stream=True
        )
        logger.info("Successfully got response from OpenAI")
        return response
    except Exception as e:
        logger.error(f"Error in process_user_query: {str(e)}")
        raise Exception(f"Error processing query: {str(e)}")

async def stream_response(response):
    """
    Stream the response from GPT-3.5-turbo
    """
    try:
        for chunk in response:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content
    except Exception as e:
        logger.error(f"Error streaming response: {str(e)}")
        raise Exception(f"Error streaming response: {str(e)}")

def process_user_query_complete(user_question):
    """
    Process user question through the complete workflow
    """
    try:
        response = process_user_query(user_question)
        return response
    except Exception as e:
        logger.error(f"Error in process_user_query_complete: {str(e)}")
        raise Exception(f"Error processing query: {str(e)}") 