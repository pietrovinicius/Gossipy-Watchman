## v0.23 — 2026-06-06

### Tipo da mudança
feat

### Arquivos alterados
- frontend/src/pages/Login.jsx
- frontend/src/components/ProtectedRoute.jsx
- frontend/src/router.jsx
- frontend/src/main.jsx

### Impacto técnico/funcional
Login com validação local (admin/watchman), sessionStorage, toggle de senha,
focus states, contraste conforme checklist UI/UX. ProtectedRoute redireciona
para / se sem token. Router com lazy loading das 4 rotas protegidas.
