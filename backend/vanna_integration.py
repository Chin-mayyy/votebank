import os
import logging
from vanna.remote import VannaDefault
from dotenv import load_dotenv
from db_utils import get_connection_string, get_db_schema

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def initialize_vanna():
    """
    Initialize Vanna AI with proper configuration
    
    Returns:
        VannaDefault: Configured Vanna AI instance
    """
    # Get API key and email from environment variables
    api_key = os.getenv("VANNA_API_KEY")
    email = os.getenv("VANNA_EMAIL")
    
    if not api_key:
        raise ValueError("VANNA_API_KEY environment variable is not set")
    if not email:
        raise ValueError("VANNA_EMAIL environment variable is not set")
    
    # Initialize Vanna with API key, model, and connection string
    logger.info("Initializing Vanna AI...")
    vn = VannaDefault(
        model="votebank",  # Model name for your VoteBank database
        api_key=api_key,
        config={
            "postgres_connection_string": get_connection_string(),
            "user_email": email  # Try using user_email instead of email
        }
    )
    
    return vn

def connect_to_database(vn):
    """
    Connect Vanna AI to your PostgreSQL database
    
    Args:
        vn: VannaDefault instance
        
    Returns:
        VannaDefault: Connected Vanna AI instance
    """
    # Connection is already established in initialize_vanna
    # This function is kept for compatibility
    logger.info("PostgreSQL connection already established in initialization")
    return vn

def train_with_schema(vn):
    """
    Train Vanna AI with database schema
    
    Args:
        vn (VannaDefault): Vanna AI instance
    """
    try:
        logger.info("Training Vanna AI with database schema...")
        
        # Get schema DDL from the database
        schema_ddl = get_db_schema()
        
        # If we couldn't get the schema from the database, use a fallback schema
        if not schema_ddl:
            # Fallback schema
            schema_ddl = """
                CREATE TABLE users (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE candidates (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    party VARCHAR(100) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE votes (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id),
                    candidate_id INTEGER REFERENCES candidates(id),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(user_id)
                );
            """
        
        # Add schema DDL to Vanna AI
        vn.add_ddl(schema_ddl)
        logger.info("Successfully trained Vanna AI with schema")
    except Exception as e:
        logger.error(f"Error training with schema: {str(e)}")
        raise
    
    return vn

def train_with_examples(vn):
    """
    Train Vanna AI with example questions and SQL queries
    
    Args:
        vn: VannaDefault instance
        
    Returns:
        VannaDefault: Trained Vanna AI instance
    """
    # Define example question-SQL pairs
    examples = [
        {
            "question": "How many votes does each candidate have?",
            "sql": """
                SELECT c.name, c.party, COUNT(v.id) as vote_count 
                FROM candidates c
                LEFT JOIN votes v ON c.id = v.candidate_id
                GROUP BY c.id, c.name, c.party
                ORDER BY vote_count DESC
            """
        },
        {
            "question": "Who are the top 5 candidates by vote count?",
            "sql": """
                SELECT c.name, c.party, COUNT(v.id) as vote_count 
                FROM candidates c
                LEFT JOIN votes v ON c.id = v.candidate_id
                GROUP BY c.id, c.name, c.party
                ORDER BY vote_count DESC
                LIMIT 5
            """
        },
        {
            "question": "Which users have not voted yet?",
            "sql": """
                SELECT u.id, u.name, u.email
                FROM users u
                LEFT JOIN votes v ON u.id = v.user_id
                WHERE v.id IS NULL
            """
        }
    ]
    
    # Train with examples
    try:
        logger.info("Training Vanna AI with example questions and SQL queries...")
        for example in examples:
            vn.train(question=example["question"], sql=example["sql"])
        logger.info(f"Successfully trained Vanna AI with {len(examples)} examples")
    except Exception as e:
        logger.error(f"Error training with examples: {str(e)}")
        raise
    
    return vn

def setup_vanna():
    """
    Set up Vanna AI with proper configuration and training
    
    Returns:
        VannaDefault: Initialized Vanna AI instance
    """
    try:
        # Use connection string for PostgreSQL
        logger.info("Using connection string for PostgreSQL")
        
        # Get Vanna API key from environment
        api_key = os.getenv("VANNA_API_KEY")
        if not api_key:
            raise ValueError("VANNA_API_KEY environment variable is not set")
        
        # Get Vanna email from environment
        email = os.getenv("VANNA_EMAIL")
        if not email:
            raise ValueError("VANNA_EMAIL environment variable is not set")
        
        # Initialize Vanna AI
        logger.info("Initializing Vanna AI...")
        vn = VannaDefault(
            model="votebank",  # Model name for your VoteBank database
            api_key=api_key,
            config={
                "postgres_connection_string": get_connection_string(),
                "user_email": email  # Try using user_email instead of email
            }
        )
        
        # Train Vanna AI with database schema
        train_with_schema(vn)
        
        # Train Vanna AI with examples
        train_with_examples(vn)
        
        return vn
    except Exception as e:
        logger.error(f"Error setting up Vanna AI: {str(e)}")
        raise

def generate_sql(vn, question):
    """
    Generate SQL from a natural language question
    
    Args:
        vn: VannaDefault instance
        question: Natural language question
        
    Returns:
        str: Generated SQL query
    """
    try:
        sql = vn.generate_sql(question)
        return sql
    except Exception as e:
        logger.error(f"Error generating SQL: {str(e)}")
        raise

def explain_sql(vn, sql):
    """
    Get an explanation of an SQL query
    
    Args:
        vn: VannaDefault instance
        sql: SQL query
        
    Returns:
        str: Explanation of the SQL query
    """
    try:
        explanation = vn.explain_sql(sql)
        return explanation
    except Exception as e:
        logger.error(f"Error explaining SQL: {str(e)}")
        raise
