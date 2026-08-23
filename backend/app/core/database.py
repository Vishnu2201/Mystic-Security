from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from app.core.config import settings

# SQLAlchemy 2.x engine configuration
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    echo=settings.DEBUG,
)

# Session factory for synchronous DB operations
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,
)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a transactional database session per request.
    Session is automatically closed after the request completes.
    
    Note: Database tables must be created via Alembic migrations.
    Do NOT invoke Base.metadata.create_all(bind=engine) on application startup.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
