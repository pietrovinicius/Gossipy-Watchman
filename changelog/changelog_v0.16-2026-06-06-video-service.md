## v0.16 — 2026-06-06

### Tipo da mudança
feat

### Arquivos alterados
- app/services/video_service.py
- tests/unit/test_video_service.py

### Impacto técnico/funcional
Centraliza CRUD de vídeos em video_service: create_video_record, get_video_by_id,
list_videos (com paginação skip/limit, ordem uploaded_at DESC) e update_video_status.
TDD: 8 testes com banco em memória, todos passando.
