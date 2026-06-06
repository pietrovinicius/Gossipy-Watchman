## v1.11 — 2026-06-06

### Tipo da mudança
fix

### Arquivos alterados
- frontend/src/pages/People.jsx
- frontend/src/pages/Dashboard.jsx
- frontend/vite.config.js
- frontend/package.json
- frontend/src/test/setup.js (novo)
- frontend/src/test/people-limit.test.jsx (novo)

### Impacto técnico/funcional
Corrige 422 Unprocessable Content em GET /api/v1/people: frontend enviava limit=500
mas o router people.py aceita no máximo le=200. Corrigido para limit=200 em People.jsx
e Dashboard.jsx. Instalado vitest + @testing-library/react para suporte a testes
unitários no frontend. TDD: 2 testes RED→GREEN validando o valor correto do parâmetro.
