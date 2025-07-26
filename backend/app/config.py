import os
from dotenv import load_dotenv

def get_database_uri():
    # Load environment variables
    load_dotenv()
    
    # Get database connection details from environment variables with defaults for development
    db_user = os.environ.get('POSTGRES_USER')
    db_password = os.environ.get('POSTGRES_PASSWORD')
    db_name = os.environ.get('POSTGRES_DB')
    db_host = os.environ.get('POSTGRES_HOST')
    db_port = os.environ.get('POSTGRES_PORT')
    
    # Debug print all environment variables
    print("\n=== Database Configuration ===")
    print(f"POSTGRES_USER: {db_user}")
    print(f"POSTGRES_PASSWORD: {'*' * len(db_password) if db_password else ''}")
    print(f"POSTGRES_HOST: {db_host}")
    print(f"POSTGRES_PORT: {db_port}")
    print(f"POSTGRES_DB: {db_name}")
    print("============================\n")
    
    # Construct the database URL
    db_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    print(f"Using database URL: postgresql://{db_user}:{'*' * len(db_password) if db_password else ''}@{db_host}:{db_port}/{db_name}")
    return db_url

class Config:
    SQLALCHEMY_DATABASE_URI = get_database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "super-secret-key")
