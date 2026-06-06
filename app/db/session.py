from collections.abc import Generator

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.settings import settings

_engine: Engine | None = None
_SessionLocal: sessionmaker | None = None


def _get_engine(engine: Engine | None = None) -> Engine:
    global _engine
    if engine is not None:
        return engine
    if _engine is None:
        _engine = create_engine(
            settings.DATABASE_URL,
            connect_args={"check_same_thread": False},
        )
    return _engine


def get_db(engine: Engine | None = None) -> Generator[Session, None, None]:
    eng = _get_engine(engine)
    factory = sessionmaker(autocommit=False, autoflush=False, bind=eng)
    session = factory()
    try:
        yield session
    finally:
        session.close()
