## v1.56 — 2026-06-07

### Tipo da mudança
feat

### Arquivos alterados
- app/services/video_service.py
- app/api/v1/videos.py
- app/schemas/video.py
- app/core/settings.py
- tests/unit/test_video_service.py
- tests/integration/test_videos.py

### Impacto técnico/funcional
Adiciona `get_video_detail()` em video_service e endpoint autenticado
`GET /api/v1/videos/{id}/detail`, retornando metadados do vídeo, pessoas
identificadas (com timeline de aparições, tempo total de presença,
contagem, primeira/última aparição) e resumo agregado (total de pessoas,
total de aparições, duração coberta, status). Pessoas ordenadas por
first_seen_at ASC. Rota registrada antes de `/videos/{video_id}` para
evitar conflito de path. Novos schemas Pydantic: AppearanceDetail,
PersonInVideo, VideoSummary, VideoDetailResponse. 8 novos testes
unitários (agregação, ordenação, total_seconds ignorando timestamp_end
nulo, escopo por vídeo) e 5 testes de integração (auth, 404, estrutura
da resposta, campos obrigatórios das pessoas). Suíte completa: 263/263.
