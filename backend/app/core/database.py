from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import get_settings

settings = get_settings()


class Base(DeclarativeBase):
    pass


# Engine is created lazily on first use so the app can start without a DB
# configured (useful for the upload/extract endpoints during development).
_engine = None
_SessionLocal = None


def get_engine():
    global _engine
    if _engine is None:
        settings.require_database()
        _engine = create_engine(settings.database_url, pool_pre_ping=True)
    return _engine


def get_sessionmaker():
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(
            bind=get_engine(),
            autoflush=False,
            expire_on_commit=False,
        )
    return _SessionLocal


def init_db() -> None:
    """Enable the pgvector extension and create tables. Run once on startup."""
    from sqlalchemy import text

    # Import models so they are registered on the metadata before create_all.
    from app.models.chunk import Chunk  # noqa: F401

    engine = get_engine()
    with engine.begin() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    Base.metadata.create_all(bind=engine)
