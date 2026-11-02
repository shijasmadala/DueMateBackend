from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

# One Engine per process. The URL comes from Settings, never from hardcoded credentials.
engine = create_engine(
    settings.database_url,
    echo=settings.db_echo,
    pool_pre_ping=True,
)

# expire_on_commit=False keeps attributes usable after commit in API handlers later.
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency that opens a session and always closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
