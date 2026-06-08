import logging
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from app.core.settings import settings

logger = logging.getLogger(__name__)


def _has_column(conn, table: str, column: str) -> bool:
    rows = conn.execute(text(f"SELECT name FROM pragma_table_info('{table}')")).fetchall()
    return any(row[0] == column for row in rows)


def _add_thumbnail_path_column(conn) -> None:
    if _has_column(conn, "videos", "thumbnail_path"):
        logger.info("migration_v1_35: coluna thumbnail_path já existe em videos, ignorando")
        return

    conn.execute(text("ALTER TABLE videos ADD COLUMN thumbnail_path VARCHAR(512) NULL"))
    logger.info("migration_v1_35: coluna thumbnail_path adicionada em videos")


def run(engine: Engine | None = None) -> None:
    _owns = engine is None
    if _owns:
        engine = create_engine(
            settings.DATABASE_URL,
            connect_args={"check_same_thread": False},
        )

    with engine.connect() as conn:
        _add_thumbnail_path_column(conn)
        conn.commit()

    if _owns:
        engine.dispose()
