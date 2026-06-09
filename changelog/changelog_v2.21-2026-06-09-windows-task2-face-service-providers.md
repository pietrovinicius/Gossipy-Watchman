## v2.21 — 2026-06-09

### Tipo da mudança
fix

### Arquivos alterados
- app/services/face_service.py
- tests/unit/test_face_service.py

### Impacto técnico/funcional
Task 2/6 de otimizações Windows: `face_service.get_face_app()` substituiu providers hardcoded `["CoreMLExecutionProvider", "CPUExecutionProvider"]` por `settings.INSIGHTFACE_PROVIDERS`. CoreML não existe no Windows — o backend tentava e falhava silenciosamente a cada boot. Agora o default via settings é `["CPUExecutionProvider"]`, configurável via .env para ambientes com GPU.
