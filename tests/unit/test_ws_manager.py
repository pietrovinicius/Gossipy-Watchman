import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest


@pytest.fixture
def manager():
    from app.core.ws_manager import ConnectionManager
    return ConnectionManager()


@pytest.mark.asyncio
async def test_connect_adds_ws_to_video_id(manager):
    ws = AsyncMock()
    await manager.connect(1, ws)
    assert ws in manager._connections[1]


@pytest.mark.asyncio
async def test_disconnect_removes_ws(manager):
    ws = AsyncMock()
    await manager.connect(1, ws)
    await manager.disconnect(1, ws)
    assert ws not in manager._connections.get(1, [])


@pytest.mark.asyncio
async def test_disconnect_last_ws_removes_key(manager):
    ws = AsyncMock()
    await manager.connect(1, ws)
    await manager.disconnect(1, ws)
    assert 1 not in manager._connections


@pytest.mark.asyncio
async def test_broadcast_sends_to_all_ws_of_video(manager):
    ws1 = AsyncMock()
    ws2 = AsyncMock()
    await manager.connect(1, ws1)
    await manager.connect(1, ws2)

    await manager.broadcast(1, {"event": "test"})

    ws1.send_json.assert_awaited_once_with({"event": "test"})
    ws2.send_json.assert_awaited_once_with({"event": "test"})


@pytest.mark.asyncio
async def test_broadcast_ignores_ws_with_exception(manager):
    ws_ok = AsyncMock()
    ws_bad = AsyncMock()
    ws_bad.send_json.side_effect = Exception("conexão encerrada")

    await manager.connect(1, ws_ok)
    await manager.connect(1, ws_bad)

    # não deve levantar exceção
    await manager.broadcast(1, {"event": "test"})

    ws_ok.send_json.assert_awaited_once()


@pytest.mark.asyncio
async def test_broadcast_all_sends_to_all_video_ids(manager):
    ws1 = AsyncMock()
    ws2 = AsyncMock()
    await manager.connect(1, ws1)
    await manager.connect(2, ws2)

    await manager.broadcast_all({"event": "global"})

    ws1.send_json.assert_awaited_once_with({"event": "global"})
    ws2.send_json.assert_awaited_once_with({"event": "global"})
