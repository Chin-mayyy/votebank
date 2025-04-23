import psycopg2
from psycopg2 import sql

# Database connection parameters
db_params = {
    "dbname": "votebank",
    "user": "chinmay",
    "password": "votebank123",
    "host": "localhost",
    "port": "5432"
}

def init_database():
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(**db_params)
        conn.autocommit = True
        cur = conn.cursor()
        
        # Create tables
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS candidates (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                phone_number VARCHAR(15),
                aadhar_number VARCHAR(12) UNIQUE,
                voter_id VARCHAR(10) UNIQUE,
                address TEXT,
                constituency VARCHAR(100) NOT NULL,
                state VARCHAR(100) NOT NULL,
                party_affiliation VARCHAR(100),
                previous_political_experience TEXT,
                campaign_promises TEXT,
                education TEXT,
                occupation VARCHAR(100),
                criminal_record BOOLEAN DEFAULT FALSE,
                criminal_record_details TEXT,
                social_media_handles JSONB,
                campaign_budget DECIMAL(15,2),
                campaign_team_size INTEGER,
                campaign_strategy TEXT,
                target_voter_demographics JSONB,
                campaign_timeline JSONB,
                fundraising_plan TEXT,
                volunteer_management TEXT,
                media_strategy TEXT,
                opposition_research TEXT,
                voter_outreach_plan TEXT,
                election_day_plan TEXT,
                post_election_plan TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE TABLE IF NOT EXISTS votes (
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(id),
                candidate_id INTEGER REFERENCES candidates(id),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(user_id, candidate_id)
            );
        """)
        
        print("Database tables created successfully!")
        
        # Close the cursor and connection
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"Error initializing database: {e}")

if __name__ == "__main__":
    init_database() 