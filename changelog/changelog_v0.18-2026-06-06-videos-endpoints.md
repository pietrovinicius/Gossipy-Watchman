## v0.18 — 2026-06-06

### Tipo da mudança
feat

### Arquivos alterados
- app/api/v1/videos.py
- app/main.py
- tests/integration/test_videos.py

### Impacto técnico/funcional
GET /api/v1/videos, GET /api/v1/videos/{id}, GET /api/v1/videos/{id}/status.
Paginação via skip/limit com validação Query. HTTP 404 com mensagem em português.
TDD: 6 testes de integração, todos passando.
