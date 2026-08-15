"""
Database connection and session management.
"""
from sqlmodel import SQLModel, create_engine, Session
from config import DATABASE_URL

connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
engine_kwargs = {"echo": False, "connect_args": connect_args}
if "sqlite" not in DATABASE_URL:
    engine_kwargs.update({"pool_pre_ping": True, "pool_recycle": 3600})

engine = create_engine(DATABASE_URL, **engine_kwargs)


def create_db_and_tables():
    """Create all tables defined by SQLModel metadata."""
    SQLModel.metadata.create_all(engine)


def get_session():
    """FastAPI dependency: yields a database session."""
    with Session(engine) as session:
        yield session
