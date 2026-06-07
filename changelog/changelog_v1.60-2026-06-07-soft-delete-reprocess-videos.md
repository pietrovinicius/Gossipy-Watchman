## v1.60 — 2026-06-07

### Tipo da mudança
feat

### Arquivos alterados
- app/services/video_service.py
- app/api/v1/videos.py
- app/core/settings.py
- tests/unit/test_video_service.py
- tests/integration/test_videos.py

### Impacto técnico/funcional
Implementado soft delete e reprocessamento de vídeos: soft_delete_video
e restore_video em video_service.py marcam/limpam deleted_at de forma
idempotente. reprocess_video valida existência do arquivo em disco
(Path.exists), levanta HTTPException 409 quando ausente e reseta status
para Pendente. list_videos ganha include_deleted e status_filter.
Endpoints DELETE /api/v1/videos/{id}, POST /api/v1/videos/{id}/restore
e POST /api/v1/videos/{id}/reprocess (dispara process_video via
BackgroundTask) adicionados em videos.py. GET /api/v1/videos aceita
include_deleted e status. 19 novos testes (10 unitários + 9 integração).
Suíte completa do backend: 299/299.
