from collections.abc import Generator

from sqlalchemy import Engine, event, create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.settings import settings

_engine: Engine | None = None


def _set_sqlite_pragma(dbapi_connection, connection_record) -> None:  # noqa: ANN001
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.close()


def _get_engine(engine: Engine | None = None) -> Engine:
    global _engine
    if engine is not None:
        return engine
    if _engine is None:
        _engine = create_engine(
            settings.DATABASE_URL,
            connect_args={"check_same_thread": False},
        )
        event.listen(_engine, "connect", _set_sqlite_pragma)
    return _engine


def get_db() -> Generator[Session, None, None]:
    """Injetável via FastAPI Depends(). Usa engine de produção."""
    eng = _get_engine()
    factory = sessionmaker(autocommit=False, autoflush=False, bind=eng)
    session = factory()
    try:
        yield session
    finally:
        session.close()


def get_db_with_engine(engine: Engine) -> Generator[Session, None, None]:
    """Versão para testes de integração de Sprint 1/2 que injetam engine."""
    factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = factory()
    try:
        yield session
    finally:
        session.close()
