## v1.99b — 2026-06-08

### Tipo da mudança
fix

### Arquivos alterados
- app/services/frame_service.py
- app/workers/video_worker.py
- tests/unit/test_frame_service.py

### Impacto técnico/funcional

**Task 3 — Timestamps reais em extract_frames:**
`extract_frames` retornava `frame_index // frame_interval` (índice de amostra), não segundos reais. Para fps_real=30 / fps_sample=2: frame_interval=15; frame 15 retornava `segundo=1`, mas tempo real é 0.5s — erro 2×.

Fix: `timestamp_seconds = frame_index / fps_real`. Adicionado fallback `fps_real = 25.0` para vídeos sem metadata de FPS. Return type alterado de `tuple[int, np.ndarray]` para `tuple[float, np.ndarray]`.

`video_worker.py`: renomeado `segundo` → `timestamp_real` em todo o loop de processamento.

447 testes passando.
