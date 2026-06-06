import asyncio

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self) -> None:
        self._connections: dict[int, list[WebSocket]] = {}
        self._lock = asyncio.Lock()

    async def connect(self, video_id: int, ws: WebSocket) -> None:
        await ws.accept()
        async with self._lock:
            self._connections.setdefault(video_id, []).append(ws)

    async def disconnect(self, video_id: int, ws: WebSocket) -> None:
        async with self._lock:
            conns = self._connections.get(video_id, [])
            if ws in conns:
                conns.remove(ws)
            if not conns:
                self._connections.pop(video_id, None)

    async def broadcast(self, video_id: int, payload: dict) -> None:
        conns = list(self._connections.get(video_id, []))
        if not conns:
            return
        results = await asyncio.gather(
            *[ws.send_json(payload) for ws in conns],
            return_exceptions=True,
        )
        failed = [conns[i] for i, r in enumerate(results) if isinstance(r, Exception)]
        for ws in failed:
            await self.disconnect(video_id, ws)

    async def broadcast_all(self, payload: dict) -> None:
        video_ids = list(self._connections.keys())
        for vid in video_ids:
            await self.broadcast(vid, payload)


ws_manager = ConnectionManager()
