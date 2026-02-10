import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    DATABASE_URL = os.getenv("DATABASE_URL")
    print("DATABASE_URL =", os.getenv("DATABASE_URL"))

    if not DATABASE_URL:
        raise Exception("DATABASE_URL not found. Check your .env file.")

    return psycopg2.connect(DATABASE_URL)
