## v0.10 — 2026-06-06

### Tipo da mudança
feat

### Arquivos alterados
- app/services/frame_service.py
- tests/unit/test_frame_service.py

### Impacto técnico/funcional
Implementa extract_frames() com amostragem configurável via fps_sample.
frame_interval = max(1, round(fps_real / fps_sample)) garante intervalo mínimo de 1.
VideoCapture.release() garantido via finally mesmo em FileNotFoundError.
TDD: 6 testes com mock de cv2.VideoCapture, todos passando.
