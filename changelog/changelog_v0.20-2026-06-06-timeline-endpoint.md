## v0.20 — 2026-06-06

### Tipo da mudança
feat

### Arquivos alterados
- app/api/v1/timeline.py
- app/schemas/appearance.py
- app/services/appearance_service.py (+ AppearanceWithVideo dataclass + get_timeline)
- app/main.py
- tests/integration/test_timeline.py

### Impacto técnico/funcional
GET /api/v1/people/{id}/timeline: retorna aparições com file_name do vídeo via JOIN,
ordenadas por video_id ASC, timestamp_start ASC. HTTP 404 se pessoa inexistente.
AppearanceWithVideo é dataclass de projeção — evita acoplamento do ORM Appearance
ao campo file_name que pertence ao modelo Video. Serialização via model_validate(__dict__).
TDD: 4 testes de integração, todos passando.
