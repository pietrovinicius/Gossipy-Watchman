## v0.06 — 2026-06-06

### Tipo da mudança
feat

### Arquivos alterados
- app/main.py
- app/api/v1/__init__.py
- app/api/v1/health.py
- tests/integration/test_health.py
- pytest.ini

### Impacto técnico/funcional
Cria instância FastAPI com CORS configurado para localhost:3000 e localhost:5173.
Startup via asynccontextmanager chama init_db() automaticamente.
Endpoint GET /api/v1/health retorna {"status": "ok", "app": "Gossipy Watchman"}.
pytest.ini configurado com asyncio_mode=auto para suporte a testes assíncronos.
TDD: 3 testes de integração escritos antes da implementação, todos passando.
