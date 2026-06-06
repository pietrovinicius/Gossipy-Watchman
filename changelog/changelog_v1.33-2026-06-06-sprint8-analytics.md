## v1.33 — 2026-06-06

### Tipo da mudança
feat

### Arquivos alterados
- app/services/analytics_service.py (novo)
- app/api/v1/analytics.py (novo)
- app/main.py (+ analytics_router)
- tests/unit/test_analytics_service.py (novo — 5 testes TDD)
- tests/integration/test_analytics.py (novo — 2 testes TDD)

### Impacto técnico/funcional
Sprint 8.5: endpoints de analytics agregados.
- GET /analytics/overview: total_videos, total_people, total_appearances
- GET /analytics/appearances-per-video: contagem de aparições por vídeo, DESC
- GET /analytics/top-people: top N pessoas por aparições (limit query param, max 50)
- GET /analytics/activity-timeline: upload de vídeos agrupado por data (days query param, max 365)
- Todos endpoints autenticados (JWT)
- 7/7 testes TDD passando; total: 220 pytest
