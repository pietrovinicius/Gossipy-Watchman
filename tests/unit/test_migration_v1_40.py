from pathlib import Path
import tempfile
import pytest
from sqlalchemy import create_engine, text


@pytest.fixture
def temp_db_engine():
    """Create temporary SQLite database engine for testing."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name

    engine = create_engine(
        f"sqlite:///{db_path}",
        connect_args={"check_same_thread": False},
    )
    yield engine
    engine.dispose()
    Path(db_path).unlink(missing_ok=True)


def test_migration_creates_employees_table(temp_db_engine):
    """Migration should create employees table."""
    from app.db.migrations.migration_v1_40 import run

    # Before migration, table doesn't exist
    with temp_db_engine.connect() as conn:
        result = conn.execute(
            text(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='employees'"
            )
        )
        assert result.fetchone() is None

    # Run migration
    run(temp_db_engine)

    # After migration, table exists
    with temp_db_engine.connect() as conn:
        result = conn.execute(
            text(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='employees'"
            )
        )
        assert result.fetchone() is not None


def test_migration_creates_correct_columns(temp_db_engine):
    """Employees table should have all required columns."""
    from app.db.migrations.migration_v1_40 import run

    run(temp_db_engine)

    with temp_db_engine.connect() as conn:
        result = conn.execute(text("PRAGMA table_info(employees)"))
        columns = {row[1]: row[2] for row in result.fetchall()}

        required_columns = {
            "id": "INTEGER",
            "name": "VARCHAR(200)",
            "registration": "VARCHAR(100)",
            "department": "VARCHAR(100)",
            "role": "VARCHAR(100)",
            "photo_path": "VARCHAR(500)",
            "embedding_path": "VARCHAR(500)",
            "person_id": "INTEGER",
            "active": "INTEGER",
            "notes": "TEXT",
            "created_at": "TIMESTAMP",
            "updated_at": "TIMESTAMP",
        }

        for col, col_type in required_columns.items():
            assert col in columns, f"Column {col} missing"


def test_migration_creates_registration_index(temp_db_engine):
    """Migration should create unique index on registration."""
    from app.db.migrations.migration_v1_40 import run

    run(temp_db_engine)

    with temp_db_engine.connect() as conn:
        result = conn.execute(
            text(
                "SELECT name FROM sqlite_master WHERE type='index' AND name='idx_employees_registration'"
            )
        )
        assert result.fetchone() is not None


def test_migration_registration_unique_constraint(temp_db_engine):
    """Registration field should be unique."""
    from app.db.migrations.migration_v1_40 import run
    from sqlalchemy.exc import IntegrityError

    run(temp_db_engine)

    with temp_db_engine.connect() as conn:
        # Insert first employee
        conn.execute(
            text(
                "INSERT INTO employees (name, registration, active, created_at, updated_at) "
                "VALUES (:name, :registration, :active, datetime('now'), datetime('now'))"
            ),
            {"name": "Alice", "registration": "MAT001", "active": 1},
        )
        conn.commit()

        # Try to insert duplicate registration
        with pytest.raises(IntegrityError):
            conn.execute(
                text(
                    "INSERT INTO employees (name, registration, active, created_at, updated_at) "
                    "VALUES (:name, :registration, :active, datetime('now'), datetime('now'))"
                ),
                {"name": "Bob", "registration": "MAT001", "active": 1},
            )
            conn.commit()


def test_migration_idempotent(temp_db_engine):
    """Migration should be idempotent (can run multiple times)."""
    from app.db.migrations.migration_v1_40 import run

    # Run migration twice
    run(temp_db_engine)
    run(temp_db_engine)  # Should not fail

    with temp_db_engine.connect() as conn:
        result = conn.execute(
            text(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='employees'"
            )
        )
        assert result.fetchone() is not None


def test_migration_default_active_is_one(temp_db_engine):
    """Default value for active column should be 1."""
    from app.db.migrations.migration_v1_40 import run

    run(temp_db_engine)

    with temp_db_engine.connect() as conn:
        # Insert employee without specifying active
        conn.execute(
            text(
                "INSERT INTO employees (name, registration, created_at, updated_at) "
                "VALUES (:name, :registration, datetime('now'), datetime('now'))"
            ),
            {"name": "Charlie", "registration": "MAT002"},
        )
        conn.commit()

        result = conn.execute(
            text("SELECT active FROM employees WHERE registration=:registration"),
            {"registration": "MAT002"},
        )
        row = result.fetchone()
        assert row[0] == 1
