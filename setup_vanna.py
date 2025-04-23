import vanna
from vanna.remote import VannaDefault
import psycopg2

# Initialize Vanna with your API key and model
vn = VannaDefault(
    api_key="vn-c7db6b0693d1423f98025922000ef51e",
    model="chinmay/votebank"
)

# Test PostgreSQL connection first
try:
    conn = psycopg2.connect(
        dbname="votebank",
        user="chinmay",
        password="votebank123",
        host="localhost",
        port="5432"
    )
    print("PostgreSQL connection successful!")
    
    # Get database schema
    cur = conn.cursor()
    cur.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
    """)
    tables = cur.fetchall()
    print("\nTables in database:")
    for table in tables:
        print(f"- {table[0]}")
    
    # Close the connection
    cur.close()
    conn.close()
    
    # Now connect with Vanna
    vn.connect_to_postgres(
        host="localhost",
        port=5432,
        database="votebank",
        user="chinmay",
        password="votebank123"
    )
    
    # Train the model
    ddl = vn.get_ddl()
    vn.train(ddl=ddl)
    print("\nModel trained successfully!")
    
    # Test a query
    sql = vn.generate_sql("Show me all tables in the database")
    print("\nGenerated SQL:")
    print(sql)
    
except Exception as e:
    print(f"Error: {str(e)}") 