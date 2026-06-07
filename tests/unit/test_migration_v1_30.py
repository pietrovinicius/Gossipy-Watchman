from sqlalchemy import create_engine, inspect
from sqlalchemy.pool import StaticPool


def _make_engine():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    with engine.connect() as conn:
        conn.exec_driver_sql(
            "CREATE TABLE people (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL)"
        )
        conn.exec_driver_sql(
            "CREATE TABLE videos (id INTEGER PRIMARY KEY AUTOINCREMENT, file_name TEXT NOT NULL)"
        )
        conn.commit()
    return engine


def _columns(engine, table):
    return {c["name"] for c in inspect(engine).get_columns(table)}


def test_migration_adiciona_deleted_at_em_people_quando_ausente():
    from app.db.migrations.migration_v1_30 import run
    engine = _make_engine()
    run(engine=engine)
    assert "deleted_at" in _columns(engine, "people")


def test_migration_adiciona_deleted_at_em_videos_quando_ausente():
    from app.db.migrations.migration_v1_30 import run
    engine = _make_engine()
    run(engine=engine)
    assert "deleted_at" in _columns(engine, "videos")


def test_migration_e_idempotente():
    from app.db.migrations.migration_v1_30 import run
    engine = _make_engine()
    run(engine=engine)
    run(engine=engine)  # segunda chamada não deve levantar exceção
    assert "deleted_at" in _columns(engine, "people")
    assert "deleted_at" in _columns(engine, "videos")


def test_modelo_person_tem_campo_deleted_at_nullable():
    from app.models.person import Person
    col = Person.__table__.columns["deleted_at"]
    assert col.nullable is True


def test_modelo_video_tem_campo_deleted_at_nullable():
    from app.models.video import Video
    col = Video.__table__.columns["deleted_at"]
    assert col.nullable is True
