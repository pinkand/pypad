"""
Database connection and session management.
"""
from sqlmodel import SQLModel, create_engine, Session
from config import DATABASE_URL

engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    pool_recycle=3600,
)


def create_db_and_tables():
    """Create all tables defined by SQLModel metadata."""
    SQLModel.metadata.create_all(engine)


def get_session():
    """FastAPI dependency: yields a database session."""
    with Session(engine) as session:
        yield session
