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
        # 1. Criar cluster_groups
        exists_groups = conn.execute(
            text("SELECT name FROM sqlite_master WHERE type='table' AND name='cluster_groups'")
        ).fetchone()

        if not exists_groups:
            conn.execute(text("""
                CREATE TABLE cluster_groups (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    status VARCHAR(20) NOT NULL DEFAULT 'Pendente',
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    deleted_at TIMESTAMP NULL DEFAULT NULL
                )
            """))
            logger.info("migration_v1_40: tabela cluster_groups criada")
        else:
            logger.info("migration_v1_40: tabela cluster_groups já existe, ignorando")

        # 2. Criar cluster_suggestions
        exists_suggestions = conn.execute(
            text("SELECT name FROM sqlite_master WHERE type='table' AND name='cluster_suggestions'")
        ).fetchone()

        if not exists_suggestions:
            conn.execute(text("""
                CREATE TABLE cluster_suggestions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    group_id INTEGER NOT NULL REFERENCES cluster_groups(id),
                    person_id INTEGER NOT NULL REFERENCES people(id),
                    is_primary BOOLEAN NOT NULL DEFAULT 0,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    deleted_at TIMESTAMP NULL DEFAULT NULL
                )
            """))
            logger.info("migration_v1_40: tabela cluster_suggestions criada")
        else:
            logger.info("migration_v1_40: tabela cluster_suggestions já existe, ignorando")

        # 3. Índices
        conn.execute(text(
            "CREATE INDEX IF NOT EXISTS idx_cluster_groups_status ON cluster_groups(status) WHERE deleted_at IS NULL"
        ))
        conn.execute(text(
            "CREATE INDEX IF NOT EXISTS idx_cluster_suggestions_group ON cluster_suggestions(group_id) WHERE deleted_at IS NULL"
        ))
        conn.execute(text(
            "CREATE INDEX IF NOT EXISTS idx_cluster_suggestions_person ON cluster_suggestions(person_id) WHERE deleted_at IS NULL"
        ))
        logger.info("migration_v1_40: índices de clusterização garantidos")
        conn.commit()

    if _owns:
        engine.dispose()
