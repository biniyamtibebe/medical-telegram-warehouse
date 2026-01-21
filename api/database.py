from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv(r"C:\Users\hp\Desktop\medical-telegram-warehouse\medical-telegram-warehouse\.env")

DATABASE_URL = f"postgresql+psycopg2://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"

engine = create_engine(DATABASE_URL, pool_pre_ping=True)  # pool_pre_ping for connection health
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Export SessionLocal so main.py can use it
__all__ = ["SessionLocal"]