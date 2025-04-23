import vanna
from vanna.remote import VannaDefault
import psycopg2
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Vanna AI
vn = VannaDefault(
    api_key=os.getenv("VANNA_API_KEY"),
    model="chinmay/votebank"
)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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
        print(f"Error connecting to database: {e}")
        return None

def process_user_query(user_question):
    """
    Process user question through the complete workflow:
    1. Generate SQL query using Vanna AI
    2. Execute query on PostgreSQL
    3. Format results
    4. Generate natural language response using GPT-4
    """
    try:
        # Step 1: Generate SQL query using Vanna AI
        sql_query = vn.generate_sql(user_question)
        print(f"Generated SQL Query: {sql_query}")

        # Step 2: Execute query on PostgreSQL
        conn = connect_to_database()
        if not conn:
            return "Error connecting to database"

        cur = conn.cursor()
        cur.execute(sql_query)
        results = cur.fetchall()
        column_names = [desc[0] for desc in cur.description]
        
        # Format results into a readable string
        formatted_results = []
        for row in results:
            row_dict = dict(zip(column_names, row))
            formatted_results.append(str(row_dict))
        
        results_str = "\n".join(formatted_results)
        
        # Close database connection
        cur.close()
        conn.close()

        # Step 3: Generate natural language response using GPT-4
        prompt = f"""
        Based on the following database query results, provide a clear and concise answer to the user's question.
        
        User's question: {user_question}
        
        Query results:
        {results_str}
        
        Please provide a natural language response that directly answers the user's question using the data from the query results.
        """
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that provides clear and concise answers based on database query results."},
                {"role": "user", "content": prompt}
            ],
            stream=True
        )
        
        return response
        
    except Exception as e:
        return f"Error processing query: {str(e)}"

def stream_response(response):
    """Stream the GPT-4 response back to the client"""
    for chunk in response:
        if chunk.choices[0].delta.content is not None:
            yield chunk.choices[0].delta.content

# Example usage
if __name__ == "__main__":
    # Test the workflow
    test_question = "How many candidates are registered in the database?"
    response = process_user_query(test_question)
    for chunk in stream_response(response):
        print(chunk, end="", flush=True) 