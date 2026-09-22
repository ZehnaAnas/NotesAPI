from sqlalchemy import create_engine
from sqlalchemy.orm import Session,sessionmaker
from sqlalchemy.pool import NullPool
from sqlmodel import Field,Session,SQLModel,create_engine
import datetime
from dotenv import load_dotenv
import os

load_dotenv()

PASSWORD = os.getenv("PASSWORD")

engine = create_engine(f"postgresql+psycopg://postgres.oloqhvknggmcpmfuyiib:{PASSWORD}@aws-0-ap-northeast-1.pooler.supabase.com:5432/postgres",echo=True,poolclass=NullPool)
SessionLocal = sessionmaker(bind=engine,autoflush=False,autocommit=False)

class Note(SQLModel,table=True):
    note_id : int | None = Field(default=None,primary_key=True)
    note : str = Field(index=True)
    created_at : datetime.date = Field(index=True)

def create_db_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

