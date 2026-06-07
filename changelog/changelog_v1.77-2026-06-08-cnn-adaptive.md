## v1.77 — 2026-06-08

### Tipo da mudança
feat

### Arquivos alterados
- app/workers/video_worker.py
- tests/unit/test_worker_adaptive_cnn.py (novo)

### Impacto técnico/funcional

**14.4 — CNN Adaptativo por Duração**

get_adaptive_params(video_path) → dict:

Detecta duração via ffprobe:
- < 10min  → preciso (upsample=2, fps=2)
- 10-60min → equilibrado (upsample=1, fps=2)
- > 60min  → eficiente (upsample=1, fps=1)
- None     → padrão (settings defaults)

Retorna dict com:
- model, upsample, fps_sample, duration, mode

Uso no worker:
```python
params = get_adaptive_params(video_path)
logger.info(f"CNN: {params['mode']}")
# Passar params a extract_frames e face_recognition
```

TDD: 5 testes
- short/medium/long video modes
- no duration fallback
- dict structure validation

Testes totais: 354 passando (+5)

Próximo: 14.5 timer frontend (12 JS tests), 14.6 verificação
