import logging

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from app.core.settings import settings

logger = logging.getLogger(__name__)


def _has_column(conn, table: str, column: str) -> bool:
    rows = conn.execute(text(f"SELECT name FROM pragma_table_info('{table}')")).fetchall()
    return any(row[0] == column for row in rows)


def _add_deleted_at_column(conn, table: str) -> None:
    if _has_column(conn, table, "deleted_at"):
        logger.info("migration_v1_30: coluna deleted_at já existe em %s, ignorando", table)
        return

    conn.execute(text(f"ALTER TABLE {table} ADD COLUMN deleted_at TIMESTAMP NULL"))
    logger.info("migration_v1_30: coluna deleted_at adicionada em %s", table)


def run(engine: Engine | None = None) -> None:
    _owns = engine is None
    if _owns:
        engine = create_engine(
            settings.DATABASE_URL,
            connect_args={"check_same_thread": False},
        )

    with engine.connect() as conn:
        _add_deleted_at_column(conn, "people")
        _add_deleted_at_column(conn, "videos")
        conn.commit()

    if _owns:
        engine.dispose()
