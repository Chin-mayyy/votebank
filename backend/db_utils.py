import os
import logging
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database connection parameters
DB_PARAMS = {
    'dbname': os.getenv('DB_NAME', 'votebank'),
    'user': os.getenv('DB_USER', 'chinmay'),
    'password': os.getenv('DB_PASSWORD', '1234'),
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432')
}


def get_connection_string():
    """Get PostgreSQL connection string"""
    return f"postgresql://{DB_PARAMS['user']}:{DB_PARAMS['password']}@{DB_PARAMS['host']}:{DB_PARAMS['port']}/{DB_PARAMS['dbname']}"


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def get_db_connection():
    """Get a database connection with retry logic"""
    try:
        return psycopg2.connect(**DB_PARAMS, cursor_factory=RealDictCursor)
    except Exception as e:
        logger.error(f"Error connecting to database: {str(e)}")
        raise


def get_db_schema():
    """Get the database schema"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                # Get list of tables
                cur.execute("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                """)
                tables = [row['table_name'] for row in cur.fetchall()]
                
                schema = []
                
                # Get columns for each table
                for table in tables:
                    cur.execute(f"""
                        SELECT column_name, data_type 
                        FROM information_schema.columns 
                        WHERE table_schema = 'public' AND table_name = '{table}'
                    """)
                    columns = [f"{row['column_name']} {row['data_type']}" for row in cur.fetchall()]
                    
                    # Get primary key
                    cur.execute(f"""
                        SELECT c.column_name
                        FROM information_schema.table_constraints tc 
                        JOIN information_schema.constraint_column_usage AS ccu USING (constraint_schema, constraint_name) 
                        JOIN information_schema.columns AS c ON c.table_schema = tc.constraint_schema
                          AND tc.table_name = c.table_name AND ccu.column_name = c.column_name
                        WHERE constraint_type = 'PRIMARY KEY' AND tc.table_name = '{table}'
                    """)
                    pk_result = cur.fetchall()
                    primary_keys = [row['column_name'] for row in pk_result] if pk_result else []
                    
                    # Get foreign keys
                    cur.execute(f"""
                        SELECT
                            kcu.column_name,
                            ccu.table_name AS foreign_table_name,
                            ccu.column_name AS foreign_column_name
                        FROM
                            information_schema.table_constraints AS tc
                            JOIN information_schema.key_column_usage AS kcu
                              ON tc.constraint_name = kcu.constraint_name
                              AND tc.table_schema = kcu.table_schema
                            JOIN information_schema.constraint_column_usage AS ccu
                              ON ccu.constraint_name = tc.constraint_name
                              AND ccu.table_schema = tc.table_schema
                        WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_name='{table}'
                    """)
                    foreign_keys = [f"{row['column_name']} REFERENCES {row['foreign_table_name']}({row['foreign_column_name']})" 
                                  for row in cur.fetchall()]
                    
                    # Create CREATE TABLE statement
                    create_table = f"CREATE TABLE {table} (\n"
                    create_table += ",\n".join([f"    {col}" for col in columns])
                    
                    if primary_keys:
                        create_table += f",\n    PRIMARY KEY ({', '.join(primary_keys)})"
                    
                    for fk in foreign_keys:
                        create_table += f",\n    FOREIGN KEY ({fk})"
                    
                    create_table += "\n);"
                    
                    schema.append(create_table)
                
                return "\n\n".join(schema)
    except Exception as e:
        logger.error(f"Error getting database schema: {str(e)}")
        return ""
