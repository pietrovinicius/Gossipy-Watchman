## v2.07 — 2026-06-09

### Tipo da mudança
fix

### Arquivos alterados
- app/core/settings.py
- frontend/package.json

### Impacto técnico/funcional

**fix(detection): ajusta parâmetros para câmeras CCTV de vigilância**

Câmeras instaladas em teto/parede geram ângulos de pitch 35–50° nas faces detectadas.
Os parâmetros anteriores foram calibrados para câmeras frontais, descartando silenciosamente
quase todas as detecções em contexto de vigilância.

Mudanças por parâmetro:

| Parâmetro | Antes | Depois | Razão |
|---|---|---|---|
| `FACE_MAX_PITCH_DEG` | 30.0 | 55.0 | CCTV topo vê pitch alto |
| `FACE_MAX_YAW_DEG` | 40.0 | 65.0 | Pessoas em catraca se viram |
| `INSIGHTFACE_DET_SCORE` | 0.7 | 0.45 | CCTV comprimido → scores menores |
| `FACE_BLUR_THRESHOLD` | 100.0 | 40.0 | Compressão H.264/H.265 |
| `FACE_MIN_SIZE_PX` | 60 | 40 | Faces menores/distantes |
| `INSIGHTFACE_DET_SIZE` | 640 | 1024 | Detecta faces menores na imagem |
| `FACE_TRACK_MIN_SAMPLES` | 2 | 1 | Passagem rápida = 1 frame basta |

Causa raiz: filtro de pitch (`is_good_quality_frame` em `face_service.py`) descartava
rostos com pitch > 30° sem logar a rejeição, tornando o problema invisível nos logs.
