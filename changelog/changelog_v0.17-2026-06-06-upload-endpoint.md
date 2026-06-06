## v0.17 — 2026-06-06

### Tipo da mudança
feat

### Arquivos alterados
- app/api/v1/upload.py
- app/services/video_service.py (+ update_file_path)
- app/db/session.py (refactor: get_db sem parâmetro + get_db_with_engine)
- app/db/__init__.py
- app/main.py
- tests/integration/conftest.py
- tests/integration/test_upload.py
- tests/integration/test_db.py (usa get_db_with_engine)

### Impacto técnico/funcional
POST /api/v1/videos/upload: valida .mp4/.avi, salva em chunks de 1MB, registra no banco,
dispara process_video como BackgroundTask, retorna HTTP 202 com VideoStatusResponse.
Refactor: get_db() zero-parâmetro para FastAPI Depends(); get_db_with_engine() para testes.
conftest.py compartilhado injeta DB de teste via dependency_override.
TDD: 7 testes de integração, todos passando.
