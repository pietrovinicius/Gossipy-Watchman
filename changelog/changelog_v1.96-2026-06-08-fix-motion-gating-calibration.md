## v1.96.0 — 2026-06-08

### Tipo da mudança
fix

### Arquivos alterados
- app/core/settings.py
- app/workers/video_worker.py
- tests/unit/test_settings.py

### Impacto técnico/funcional
Corrige a falha na detecção de movimento e no reconhecimento facial para vídeos de baixa qualidade/resolução.
- Altera a rotina de desfoque gaussiano do Motion Gating para usar tamanho de kernel adaptativo (proporcional a 1% da largura do frame, mínimo 3), impedindo que frames de baixa resolução sejam completamente apagados.
- Torna os parâmetros de movimento mais sensíveis por padrão: `MOTION_GATING_THRESHOLD = 15` (antes 25) e `MOTION_GATING_AREA_RATIO = 0.001` (antes 0.005).
- Flexibiliza o filtro de qualidade de rostos para vídeos de menor qualidade: `FACE_BLUR_THRESHOLD = 30.0` (antes 100.0) e `FACE_MIN_SIZE_PX = 40` (antes 60).
- Adicionados testes de unidade correspondentes em `test_settings.py`.
