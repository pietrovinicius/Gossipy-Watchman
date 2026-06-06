import logging

from fastapi import APIRouter, Query
from fastapi import WebSocket
from starlette.websockets import WebSocketDisconnect

from app.core.ws_manager import ws_manager
from app.services.auth_service import verify_token

logger = logging.getLogger(__name__)

router = APIRouter()

# video_id=0 é reservado para assinantes globais
_GLOBAL_CHANNEL = 0


def _auth_ws(token: str) -> bool:
    try:
        verify_token(token)
        return True
    except Exception:
        return False


@router.websocket("/ws/video/{video_id}")
async def ws_video(
    video_id: int,
    websocket: WebSocket,
    token: str = Query(default=""),
) -> None:
    if not _auth_ws(token):
        await websocket.close(code=1008)
        return
    await ws_manager.connect(video_id, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        await ws_manager.disconnect(video_id, websocket)


@router.websocket("/ws/global")
async def ws_global(
    websocket: WebSocket,
    token: str = Query(default=""),
) -> None:
    if not _auth_ws(token):
        await websocket.close(code=1008)
        return
    await ws_manager.connect(_GLOBAL_CHANNEL, websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        await ws_manager.disconnect(_GLOBAL_CHANNEL, websocket)
