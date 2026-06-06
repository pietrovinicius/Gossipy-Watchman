import pytest
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.pool import StaticPool


def _make_engine():
    return create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


def test_migration_cria_tabela_alerts():
    from app.db.migrations.migration_v1_20 import run
    engine = _make_engine()
    run(engine=engine)
    insp = inspect(engine)
    assert "alerts" in insp.get_table_names()


def test_migration_idempotente():
    from app.db.migrations.migration_v1_20 import run
    engine = _make_engine()
    run(engine=engine)
    run(engine=engine)  # segunda chamada não deve levantar exceção
    insp = inspect(engine)
    assert "alerts" in insp.get_table_names()


def test_migration_cria_indice_alerts_seen():
    from app.db.migrations.migration_v1_20 import run
    engine = _make_engine()
    run(engine=engine)
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT name FROM sqlite_master WHERE type='index' AND name='idx_alerts_seen'")
        ).fetchone()
    assert result is not None, "Índice idx_alerts_seen não encontrado"


def test_modelo_alert_tem_campos_obrigatorios():
    from app.models.alert import Alert
    cols = {c.name for c in Alert.__table__.columns}
    required = {"id", "person_id", "video_id", "timestamp_in_video", "message", "seen", "created_at"}
    assert required.issubset(cols), f"Colunas faltando: {required - cols}"
