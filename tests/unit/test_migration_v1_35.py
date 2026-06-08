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
            "CREATE TABLE videos (id INTEGER PRIMARY KEY AUTOINCREMENT, file_name TEXT NOT NULL)"
        )
        conn.commit()
    return engine


def _columns(engine, table):
    return {c["name"] for c in inspect(engine).get_columns(table)}


def test_migration_adiciona_thumbnail_path_em_videos_quando_ausente():
    from app.db.migrations.migration_v1_35 import run
    engine = _make_engine()
    run(engine=engine)
    assert "thumbnail_path" in _columns(engine, "videos")


def test_migration_v1_35_e_idempotente():
    from app.db.migrations.migration_v1_35 import run
    engine = _make_engine()
    run(engine=engine)
    run(engine=engine)  # Segunda chamada não deve levantar exceção
    assert "thumbnail_path" in _columns(engine, "videos")


def test_modelo_video_tem_campo_thumbnail_path_nullable():
    from app.models.video import Video
    col = Video.__table__.columns["thumbnail_path"]
    assert col.nullable is True
