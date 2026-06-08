## v1.96.0 — 2026-06-08

### Tipo da mudança
refactor

### Arquivos alterados
- app/main.py
- app/services/face_service.py
- app/services/employee_service.py
- app/services/search_service.py
- app/core/settings.py
- requirements.txt
- .gitignore
- tests/integration/test_search.py
- tests/unit/test_employee_service.py
- tests/unit/test_face_service.py
- tests/unit/test_search_service.py
- tests/unit/test_settings.py

### Impacto técnico/funcional
Reverte a arquitetura de processamento e reconhecimento facial baseada em OpenCV YuNet + SFace de volta para a biblioteca original `face_recognition` (dlib) devido a testes de qualidade de detecção no ambiente real. 
- Restaura os embeddings do dlib (128 dimensões).
- Restaura a tolerância original de reconhecimento (`FACE_RECOGNITION_TOLERANCE = 0.6`) e os parâmetros de corte de qualidade de rosto (`FACE_MIN_SIZE_PX = 60` e `FACE_BLUR_THRESHOLD = 100.0`).
- Remove o script de download de modelos `model_downloader.py`.
- Reverte todas as suítes de testes unitários e de integração correspondentes.
- Mantém ativas e integradas com o `face_recognition` as novas features do dia (HEVC recovery, faststart fallbacks de MP4 e o Motion Gating).
