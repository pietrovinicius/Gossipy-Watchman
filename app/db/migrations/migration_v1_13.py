import logging
import sqlite3

logger = logging.getLogger(__name__)


def run(database_url: str | None = None) -> None:
    from app.core.settings import settings

    url = database_url or settings.DATABASE_URL
    db_path = url.replace("sqlite:///", "").replace("sqlite://", "")

    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.execute("SELECT name FROM pragma_table_info('people')")
        existing = {row[0] for row in cursor.fetchall()}

        if "notes" not in existing:
            conn.execute("ALTER TABLE people ADD COLUMN notes TEXT")
            logger.info("migration_v1_13: coluna 'notes' adicionada")
        else:
            logger.info("migration_v1_13: coluna 'notes' já existe, ignorando")

        if "category" not in existing:
            conn.execute(
                "ALTER TABLE people ADD COLUMN category VARCHAR(20) NOT NULL DEFAULT 'Desconhecido'"
            )
            logger.info("migration_v1_13: coluna 'category' adicionada")
        else:
            logger.info("migration_v1_13: coluna 'category' já existe, ignorando")

        conn.commit()
    finally:
        conn.close()
