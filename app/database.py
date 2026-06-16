from sqlmodel import create_engine, SQLModel, Session
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./tutores.db")

engine = create_engine(DATABASE_URL, echo=False)


def criar_tabelas():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
