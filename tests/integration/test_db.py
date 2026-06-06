import pytest
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import Session


@pytest.fixture
def memory_engine():
    from app.models import Base
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


def test_init_db_creates_people_table(memory_engine):
    inspector = inspect(memory_engine)
    assert "people" in inspector.get_table_names()


def test_init_db_creates_videos_table(memory_engine):
    inspector = inspect(memory_engine)
    assert "videos" in inspector.get_table_names()


def test_init_db_creates_appearances_table(memory_engine):
    inspector = inspect(memory_engine)
    assert "appearances" in inspector.get_table_names()


def test_init_db_via_function():
    from app.db import init_db
    # init_db() não deve levantar exceção com banco em memória
    engine = create_engine("sqlite:///:memory:")
    init_db(engine=engine)
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    assert "people" in tables
    assert "videos" in tables
    assert "appearances" in tables
    engine.dispose()


def test_get_db_returns_functional_session(memory_engine):
    from app.db import get_db_with_engine
    gen = get_db_with_engine(memory_engine)
    session = next(gen)
    assert isinstance(session, Session)
    result = session.execute(text("SELECT 1")).scalar()
    assert result == 1
    try:
        next(gen)
    except StopIteration:
        pass
