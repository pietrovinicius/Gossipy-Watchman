## v1.07 — 2026-06-06

### Tipo da mudança
feat (segurança)

### Arquivos alterados
- app/api/v1/faces.py (novo — endpoint autenticado /api/v1/faces/{filename})
- app/main.py (remove StaticFiles /faces, adiciona faces_router + security_headers_middleware)
- tests/integration/test_faces.py (novo — 5 testes)
- tests/integration/test_security_headers.py (novo — 5 testes)
- frontend/src/pages/People.jsx (FACES_BASE → /api/v1/faces)
- frontend/src/pages/PersonDetail.jsx (FACES_BASE → /api/v1/faces)

### Impacto técnico/funcional
5.6 (ALTO): StaticFiles /faces removido. GET /api/v1/faces/{filename} exige JWT.
  Validação de path: rejeita "..", "/", "\\". Confinamento via resolve().relative_to().
5.7 (MÉDIO): Middleware adiciona 5 security headers em todas as respostas:
  X-Content-Type-Options, X-Frame-Options, X-XSS-Protection, Referrer-Policy, CSP.
TDD: 10 novos testes, 125 total.
