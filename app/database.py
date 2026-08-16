import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Chapter 1: no DB yet, this just needs to not explode on import.
# Chapter 2 wires DATABASE_URL to the Postgres container.
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://sentinel:sentinel@localhost:5432/sentinel"
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
