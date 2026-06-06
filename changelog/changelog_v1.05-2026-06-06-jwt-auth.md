## v1.05 — 2026-06-06

### Tipo da mudança
feat

### Arquivos alterados
- app/services/auth_service.py (novo)
- app/api/v1/auth.py (novo)
- app/api/v1/upload.py, videos.py, people.py, timeline.py (+ get_current_user)
- app/main.py (+ auth_router)
- tests/integration/conftest.py (+ auth_token, auth_headers fixtures)
- tests/integration/test_auth.py (novo — 6 testes)
- tests/integration/test_upload.py, test_videos.py, test_people.py, test_timeline.py (+ auth_headers)
- frontend/src/services/api.js (interceptor de request com Bearer token)
- frontend/src/pages/Login.jsx (login real via POST /api/v1/auth/login)

### Impacto técnico/funcional
JWT real com python-jose. Todos os endpoints protegidos via Depends(get_current_user).
/api/v1/health permanece público. Fallback de senha "watchman" quando ADMIN_PASSWORD_HASH
vazio (desenvolvimento). TDD: 6 testes de auth + suite completa 108 testes passando.
