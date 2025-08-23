# -----------------------------------------------------------------------------
# Template created by Gilbert Ramirez GitHub: https://github.com/MetalCloud1
# Licensed under CC BY-NC-ND (custom) – see LICENSE.md for details
# You may view, study, and modify this template.
# Substantial modifications that add new functionality or transform the project
# may be used as your own work, as long as the original template is properly
# acknowledged.
# -----------------------------------------------------------------------------
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base, Session
import os

POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DB = os.getenv("POSTGRES_DB")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "postgres-service")

DATABASE_URL = (
    f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
    f"@{POSTGRES_HOST}:5432/{POSTGRES_DB}"
)

engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)
Base = declarative_base()


def get_db():
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
