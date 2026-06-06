## v1.30 — 2026-06-06

### Tipo da mudança
feat

### Arquivos alterados
- app/services/alert_service.py (novo)
- app/api/v1/alerts.py (novo)
- app/main.py (+ alerts_router)
- tests/unit/test_alert_service.py (novo — 6 testes TDD)
- tests/integration/test_alerts.py (novo — 4 testes TDD)

### Impacto técnico/funcional
Sprint 8.2: Serviço e endpoints de alertas.
- create_alert, list_alerts (unseen_only, paginação, DESC), mark_alerts_seen, get_unseen_count
- GET /alerts, GET /alerts/count, PATCH /alerts/seen (todos autenticados)
- AlertResponse enriquecido com person_name e video_file_name via JOIN em memória
- GET /alerts/count registrado ANTES de GET /alerts/{...} (evita colisão de rota)
- 10/10 testes TDD passando; total: 200 pytest
