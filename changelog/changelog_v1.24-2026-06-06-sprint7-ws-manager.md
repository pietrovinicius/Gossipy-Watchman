## v1.24 — 2026-06-06

### Tipo da mudança
feat

### Arquivos alterados
- app/core/ws_manager.py (novo)
- tests/unit/test_ws_manager.py (novo — 6 testes TDD)

### Impacto técnico/funcional
Sprint 7.4: ConnectionManager para WebSocket assíncrono.
- ConnectionManager: dict[video_id → list[WebSocket]] + asyncio.Lock
- connect(): ws.accept() → append ao dict
- disconnect(): remove do dict; remove chave se lista vazia
- broadcast(video_id): asyncio.gather + return_exceptions=True → desconecta falhos
- broadcast_all(): itera todas as chaves, chama broadcast por video_id
- Singleton ws_manager = ConnectionManager() pronto para importação
- 6/6 testes TDD passando (pytest-asyncio + AsyncMock)
- Total: 181 pytest passando
