## v1.04 — 2026-06-06

### Tipo da mudança
feat

### Arquivos alterados
- app/core/settings.py (reescrito com SettingsConfigDict + model_validator)
- app/main.py (docs_url/redoc_url condicionais via DOCS_ENABLED)
- tests/unit/test_settings.py (+ 7 testes para novas constantes)

### Impacto técnico/funcional
Settings migrado para SettingsConfigDict com suporte a .env. Novas constantes:
JWT_SECRET_KEY (fallback para testes), JWT_ALGORITHM, JWT_EXPIRE_MINUTES,
ADMIN_USERNAME, ADMIN_PASSWORD_HASH, MAX_UPLOAD_SIZE_MB, MAX_UPLOAD_SIZE_BYTES
(calculado via model_validator), DOCS_ENABLED. TDD: 7 testes novos, 102 total.
