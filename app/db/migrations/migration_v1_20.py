import logging
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from app.core.settings import settings

logger = logging.getLogger(__name__)


def run(engine: Engine | None = None) -> None:
    _owns = engine is None
    if _owns:
        engine = create_engine(
            settings.DATABASE_URL,
            connect_args={"check_same_thread": False},
        )

    with engine.connect() as conn:
        exists = conn.execute(
            text("SELECT name FROM sqlite_master WHERE type='table' AND name='alerts'")
        ).fetchone()

        if not exists:
            conn.execute(text("""
                CREATE TABLE alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    person_id INTEGER NOT NULL REFERENCES people(id),
                    video_id INTEGER NOT NULL REFERENCES videos(id),
                    timestamp_in_video FLOAT NOT NULL,
                    message TEXT NOT NULL,
                    seen INTEGER NOT NULL DEFAULT 0,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """))
            logger.info("migration_v1_20: tabela alerts criada")
        else:
            logger.info("migration_v1_20: tabela alerts já existe, ignorando")

        conn.execute(text(
            "CREATE INDEX IF NOT EXISTS idx_alerts_seen ON alerts(seen)"
        ))
        logger.info("migration_v1_20: índice idx_alerts_seen garantido")
        conn.commit()

    if _owns:
        engine.dispose()
