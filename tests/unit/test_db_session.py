from unittest.mock import MagicMock, call, patch

from sqlalchemy import create_engine


def test_wal_mode_pragma_executed_on_connect():
    """Engine deve executar WAL mode + synchronous=NORMAL ao conectar."""
    from app.db import session as db_session

    db_session._engine = None

    executed_sql: list[str] = []

    def fake_connect(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        executed_sql.extend(["journal_mode=WAL", "synchronous=NORMAL"])

    real_engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})

    with patch("app.db.session.create_engine", return_value=real_engine) as mock_create:
        with patch("app.db.session.event") as mock_event:
            db_session._engine = None
            eng = db_session._get_engine()
            mock_event.listen.assert_called_once_with(eng, "connect", db_session._set_sqlite_pragma)


def test_set_sqlite_pragma_executes_wal():
    """_set_sqlite_pragma deve executar os dois PRAGMAs no cursor."""
    from app.db.session import _set_sqlite_pragma

    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    _set_sqlite_pragma(mock_conn, None)

    mock_cursor.execute.assert_any_call("PRAGMA journal_mode=WAL")
    mock_cursor.execute.assert_any_call("PRAGMA synchronous=NORMAL")
