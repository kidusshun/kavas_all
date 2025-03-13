import psycopg2
from psycopg2.extras import RealDictCursor
from fastapi import Depends
from .setup import initialize_database  

# Run database setup on first application start
initialize_database()

DB_NAME = "face"
DB_USER = "root"
DB_PASSWORD = "123456789"
DB_HOST = "localhost"
DB_PORT = "8505"

def get_db():
    db = psycopg2.connect(
            dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT, cursor_factory=RealDictCursor
        )
    try:
        yield db
    finally:
        db.close()
