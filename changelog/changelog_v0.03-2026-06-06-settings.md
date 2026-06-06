## v0.03 — 2026-06-06

### Tipo da mudança
feat

### Arquivos alterados
- app/core/settings.py
- tests/unit/test_settings.py

### Impacto técnico/funcional
Cria app/core/settings.py com pydantic-settings centralizando todas as constantes
de configuração do sistema (DATABASE_URL, paths de storage, FACE_RECOGNITION_TOLERANCE,
FRAMES_PER_SECOND_SAMPLE, APP_NAME, API_V1_PREFIX). TDD: 7 testes escritos antes da
implementação, todos passando.
