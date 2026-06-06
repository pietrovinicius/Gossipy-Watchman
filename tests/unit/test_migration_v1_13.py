import sqlite3
import tempfile
from pathlib import Path

import pytest


def _create_db_without_new_columns(db_path: str) -> None:
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE people (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(255) NOT NULL,
            profile_image_path VARCHAR(512),
            created_at DATETIME
        )
    """)
    conn.commit()
    conn.close()


def _get_column_names(db_path: str) -> list[str]:
    conn = sqlite3.connect(db_path)
    cursor = conn.execute("SELECT name FROM pragma_table_info('people')")
    names = [row[0] for row in cursor.fetchall()]
    conn.close()
    return names


def test_migration_adds_notes_column():
    from app.db.migrations.migration_v1_13 import run

    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    _create_db_without_new_columns(db_path)
    cols_before = _get_column_names(db_path)
    assert "notes" not in cols_before

    run(database_url=f"sqlite:///{db_path}")

    cols_after = _get_column_names(db_path)
    assert "notes" in cols_after
    Path(db_path).unlink(missing_ok=True)


def test_migration_adds_category_column():
    from app.db.migrations.migration_v1_13 import run

    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    _create_db_without_new_columns(db_path)
    run(database_url=f"sqlite:///{db_path}")

    cols_after = _get_column_names(db_path)
    assert "category" in cols_after
    Path(db_path).unlink(missing_ok=True)


def test_migration_is_idempotent():
    from app.db.migrations.migration_v1_13 import run

    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    _create_db_without_new_columns(db_path)
    run(database_url=f"sqlite:///{db_path}")
    run(database_url=f"sqlite:///{db_path}")  # segunda execução não deve falhar

    cols = _get_column_names(db_path)
    assert cols.count("notes") == 1
    assert cols.count("category") == 1
    Path(db_path).unlink(missing_ok=True)


def test_migration_category_has_default():
    from app.db.migrations.migration_v1_13 import run

    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name

    _create_db_without_new_columns(db_path)
    conn = sqlite3.connect(db_path)
    conn.execute("INSERT INTO people (name) VALUES ('Teste')")
    conn.commit()
    conn.close()

    run(database_url=f"sqlite:///{db_path}")

    conn = sqlite3.connect(db_path)
    row = conn.execute("SELECT category FROM people WHERE name='Teste'").fetchone()
    conn.close()
    assert row[0] == "Desconhecido"
    Path(db_path).unlink(missing_ok=True)
