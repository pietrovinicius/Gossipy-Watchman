## v1.8.10 — 2026-06-07

### Tipo da mudança
fix

### Arquivos alterados
- app/services/video_service.py
- tests/unit/test_video_service.py

### Impacto técnico/funcional
`search_videos` montava o item do catálogo sem o campo `thumbnail_path`, então a página de Vídeos sempre exibia o ícone genérico de filme mesmo quando o vídeo já tinha thumbnail gerada pelo worker. Agora o campo é incluído na resposta, permitindo que o frontend (`VideosCatalog.jsx`) renderize a imagem real do primeiro frame do vídeo.
