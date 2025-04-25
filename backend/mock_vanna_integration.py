import logging
import random

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MockVannaAI:
    """
    Mock implementation of Vanna AI for testing purposes
    """
    def __init__(self):
        self.trained_schema = None
        self.trained_examples = []
        logger.info("MockVannaAI initialized")
    
    def add_ddl(self, schema):
        """
        Mock implementation of add_ddl
        """
        logger.info(f"MockVannaAI: Training with schema")
        self.trained_schema = schema
        return True
    
    def train(self, question, sql):
        """
        Mock implementation of train
        """
        logger.info(f"MockVannaAI: Training with example - Question: {question}")
        self.trained_examples.append({"question": question, "sql": sql})
        return True
    
    def generate_sql(self, question):
        """
        Mock implementation of generate_sql
        """
        logger.info(f"MockVannaAI: Generating SQL for question: {question}")
        
        # Convert question to lowercase for easier matching
        q = question.lower()
        
        # Comprehensive pattern matching for common voting questions
        if any(term in q for term in ["all candidates", "list candidates", "show candidates"]):
            return "SELECT id, name, party FROM candidates ORDER BY id"
            
        elif any(term in q for term in ["all users", "list users", "show users"]):
            return "SELECT id, name, email FROM users ORDER BY id"
            
        elif any(term in q for term in ["how many users", "number of users", "count users", "total users", "how many voters", "number of voters", "count voters", "total voters"]):
            return "SELECT COUNT(*) as total_users FROM users"
            
        elif any(term in q for term in ["all votes", "list votes", "show votes"]):
            return "SELECT v.id, u.name as user, c.name as candidate, c.party FROM votes v JOIN users u ON v.user_id = u.id JOIN candidates c ON v.candidate_id = c.id"
            
        elif "votes" in q and "candidate" in q:
            if "each" in q or "all" in q or "count" in q:
                return """
                    SELECT c.id, c.name, c.party, COUNT(v.id) as vote_count 
                    FROM candidates c
                    LEFT JOIN votes v ON c.id = v.candidate_id
                    GROUP BY c.id, c.name, c.party
                    ORDER BY vote_count DESC
                """
            else:
                # Try to find a specific candidate name in the question
                return """
                    SELECT c.id, c.name, c.party, COUNT(v.id) as vote_count 
                    FROM candidates c
                    LEFT JOIN votes v ON c.id = v.candidate_id
                    GROUP BY c.id, c.name, c.party
                    ORDER BY vote_count DESC
                """
                
        elif "top" in q and "candidate" in q:
            limit = 5  # Default limit
            for word in q.split():
                if word.isdigit():
                    limit = int(word)
                    break
            
            return f"""
                SELECT c.id, c.name, c.party, COUNT(v.id) as vote_count 
                FROM candidates c
                LEFT JOIN votes v ON c.id = v.candidate_id
                GROUP BY c.id, c.name, c.party
                ORDER BY vote_count DESC
                LIMIT {limit}
            """
            
        elif any(term in q for term in ["not voted", "haven't voted", "without vote", "no vote"]):
            return """
                SELECT u.id, u.name, u.email
                FROM users u
                LEFT JOIN votes v ON u.id = v.user_id
                WHERE v.id IS NULL
            """
            
        elif "party" in q and ("most" in q or "highest" in q or "winning" in q):
            return """
                SELECT c.party, COUNT(v.id) as vote_count 
                FROM candidates c
                LEFT JOIN votes v ON c.id = v.candidate_id
                GROUP BY c.party
                ORDER BY vote_count DESC
            """
            
        elif "who" in q and "voted" in q:
            return """
                SELECT u.id, u.name, u.email, c.name as voted_for, c.party
                FROM users u
                JOIN votes v ON u.id = v.user_id
                JOIN candidates c ON v.candidate_id = c.id
                ORDER BY u.id
            """
            
        else:
            # Check if the question is asking for a count of something
            if any(term in q for term in ["how many", "count", "total number", "number of"]):
                if any(term in q for term in ["user", "voter", "people"]):
                    return "SELECT COUNT(*) as total_users FROM users"
                elif any(term in q for term in ["candidate", "contestants"]):
                    return "SELECT COUNT(*) as total_candidates FROM candidates"
                elif any(term in q for term in ["vote", "ballot"]):
                    return "SELECT COUNT(*) as total_votes FROM votes"
                else:
                    # Generic count query that shows counts of all main tables
                    return """
                        SELECT 
                            (SELECT COUNT(*) FROM users) as total_users,
                            (SELECT COUNT(*) FROM candidates) as total_candidates,
                            (SELECT COUNT(*) FROM votes) as total_votes
                    """
            else:
                # Default query that returns useful information
                return "SELECT * FROM users ORDER BY id LIMIT 10"
    
    def explain_sql(self, sql):
        """
        Mock implementation of explain_sql
        """
        logger.info(f"MockVannaAI: Explaining SQL: {sql}")
        return f"This SQL query retrieves data from the database based on the specified conditions."

def initialize_vanna():
    """
    Initialize mock Vanna AI
    
    Returns:
        MockVannaAI: Mock Vanna AI instance
    """
    logger.info("Initializing mock Vanna AI...")
    return MockVannaAI()

def connect_to_database(vn):
    """
    Mock database connection
    
    Args:
        vn: MockVannaAI instance
        
    Returns:
        MockVannaAI: Mock Vanna AI instance
    """
    logger.info("Mock connecting to database...")
    return vn

def train_with_schema(vn):
    """
    Train mock Vanna AI with schema
    
    Args:
        vn: MockVannaAI instance
        
    Returns:
        MockVannaAI: Mock Vanna AI instance
    """
    schema = """
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
    
    logger.info("Training mock Vanna AI with schema...")
    vn.add_ddl(schema)
    return vn

def train_with_examples(vn):
    """
    Train mock Vanna AI with examples
    
    Args:
        vn: MockVannaAI instance
        
    Returns:
        MockVannaAI: Mock Vanna AI instance
    """
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
    
    logger.info(f"Training mock Vanna AI with {len(examples)} examples...")
    for example in examples:
        vn.train(example["question"], example["sql"])
    return vn

def setup_vanna():
    """
    Set up mock Vanna AI
    
    Returns:
        MockVannaAI: Mock Vanna AI instance
    """
    logger.info("Setting up mock Vanna AI...")
    vn = initialize_vanna()
    vn = connect_to_database(vn)
    vn = train_with_schema(vn)
    vn = train_with_examples(vn)
    logger.info("Mock Vanna AI setup completed successfully")
    return vn

def generate_sql(vn, question):
    """
    Generate SQL from question using mock Vanna AI
    
    Args:
        vn: MockVannaAI instance
        question: Natural language question
        
    Returns:
        str: Generated SQL query
    """
    return vn.generate_sql(question)
