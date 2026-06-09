## v1.99e — 2026-06-08

### Tipo da mudança
feat

### Arquivos alterados
- app/workers/video_worker.py
- app/core/settings.py
- tests/integration/test_video_worker.py

### Impacto técnico/funcional

**Task 7 — Escalonamento adaptativo para vídeos 4K:**
InsightFace com `det_size=640` em frames 4K (3840×2160) causa downscale ≈1/6, perdendo faces pequenas. Fix: quando `w > INSIGHTFACE_HIGH_RES_THRESHOLD (1920px)`, o frame é redimensionado para largura máxima de 1920px antes de `extract_embeddings` usando `cv2.INTER_AREA`. Frames FullHD ou menores não são redimensionados.

Setting `INSIGHTFACE_HIGH_RES_THRESHOLD: int = 1920` adicionado em `settings.py`. Testes de motion gating corrigidos para incluir o novo setting nos MagicMocks.

457 testes passando.
