from sqlalchemy import create_engine
from langchain_community.utilities.sql_database import SQLDatabase
import os
from dotenv import load_dotenv

load_dotenv()

def get_engine():
    host = os.getenv("HOST")
    port = int(os.getenv("DBPORT"))
    db_name = os.getenv("DBNAME")
    user = os.getenv("USER")
    password = os.getenv("PASSWORD")

    db_url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db_name}"
    
    engine = create_engine(
        db_url,
        pool_size=10,
        max_overflow=20,
        pool_timeout=30,
        pool_recycle=1800,
    )
    return engine

engine = get_engine()
db = SQLDatabase(engine)