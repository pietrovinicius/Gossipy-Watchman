## v1.22 — 2026-06-06

### Tipo da mudança
feat

### Arquivos alterados
- app/services/export_service.py (novo)
- app/api/v1/export.py (novo)
- app/main.py (+ export_router)
- tests/unit/test_export_service.py (novo — 8 testes TDD)
- tests/integration/test_export.py (novo — 8 testes TDD)

### Impacto técnico/funcional
Sprint 7.2: Export CSV de timeline de aparições.
- generate_timeline_csv(): JOIN appearances+people+videos, filtros opcionais person_id/video_id,
  3 linhas de comentário de auditoria (# Gossipy Watchman, # Gerado em, # Total de registros),
  9 colunas CSV via stdlib csv.DictWriter
- GET /export/timeline: global com filtros opcionais via query params, 400 se ambos fornecidos,
  404 se ID não existe, StreamingResponse text/csv com Content-Disposition
- GET /export/timeline/person/{id}: atalho semântico por pessoa
- GET /export/timeline/video/{id}: atalho semântico por vídeo
- Total: 175 testes passando (159 anteriores + 16 novos)
