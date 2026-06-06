import asyncio
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from starlette.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from app.models import Base
from app.db.session import get_db


@pytest.fixture(scope="module")
def sync_engine():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture(scope="module")
def sync_client(sync_engine):
    from app.main import app

    def override_get_db():
        Session = sessionmaker(bind=sync_engine)
        session = Session()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture(scope="module")
def token(sync_client):
    res = sync_client.post(
        "/api/v1/auth/login",
        data={"username": "admin", "password": "watchman"},
    )
    return res.json()["access_token"]


# ── 1: sem token → rejeitado ──────────────────────────────────────────────────
def test_ws_video_rejects_missing_token(sync_client):
    with pytest.raises(WebSocketDisconnect):
        with sync_client.websocket_connect("/api/v1/ws/video/1") as ws:
            ws.receive_json()


# ── 2: token inválido → rejeitado ─────────────────────────────────────────────
def test_ws_video_rejects_invalid_token(sync_client):
    with pytest.raises(WebSocketDisconnect):
        with sync_client.websocket_connect("/api/v1/ws/video/1?token=TOKEN_INVALIDO") as ws:
            ws.receive_json()


# ── 3: token válido → conexão aceita ──────────────────────────────────────────
def test_ws_video_accepts_valid_token(sync_client, token):
    with sync_client.websocket_connect(f"/api/v1/ws/video/99?token={token}") as ws:
        ws.close()


# ── 4: ws global → token válido → conexão aceita ─────────────────────────────
def test_ws_global_accepts_valid_token(sync_client, token):
    with sync_client.websocket_connect(f"/api/v1/ws/global?token={token}") as ws:
        ws.close()


# ── 5: _broadcast_sync usa asyncio.run_coroutine_threadsafe ──────────────────
def test_broadcast_sync_schedules_coroutine():
    from app.workers.video_worker import _broadcast_sync
    from app.core.ws_manager import ws_manager

    mock_loop = MagicMock()
    mock_loop.is_running.return_value = True
    mock_future = MagicMock()
    ws_manager._loop = mock_loop

    def fake_rcf(coro, loop):
        coro.close()  # evita "coroutine never awaited" warning
        return mock_future

    with patch(
        "app.workers.video_worker.asyncio.run_coroutine_threadsafe",
        side_effect=fake_rcf,
    ) as mock_rcf:
        _broadcast_sync(42, {"event": "frame_processed", "second": 5})

        mock_rcf.assert_called_once()
        _, loop_arg = mock_rcf.call_args[0]
        assert loop_arg is mock_loop
        mock_future.result.assert_called_once_with(timeout=2)

    ws_manager._loop = None
