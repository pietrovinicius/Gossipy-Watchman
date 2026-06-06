## v1.25 — 2026-06-06

### Tipo da mudança
feat

### Arquivos alterados
- app/api/v1/ws.py (novo)
- app/core/ws_manager.py (+ _loop, set_loop)
- app/workers/video_worker.py (+ _broadcast_sync, broadcasts no processo)
- app/main.py (+ ws_router, set_loop no lifespan)
- tests/integration/test_ws.py (novo — 5 testes TDD)

### Impacto técnico/funcional
Sprint 7.5: Endpoints WebSocket + integração com worker.
- /ws/video/{video_id}?token=JWT — auth via query param (JS WebSocket API não suporta headers)
- /ws/global?token=JWT — canal global (video_id=0 internamente)
- Token inválido/ausente → close(code=1008)
- ws_manager armazena event loop via set_loop() no lifespan; worker usa
  asyncio.run_coroutine_threadsafe() (NUNCA asyncio.run(), que levanta RuntimeError)
- _broadcast_sync emitido em: status Processando, a cada frame, status Concluído, status Erro
- 5/5 testes TDD passando; total: 186 pytest passando
