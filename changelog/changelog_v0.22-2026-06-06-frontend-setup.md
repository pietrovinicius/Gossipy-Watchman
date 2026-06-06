## v0.22 — 2026-06-06

### Tipo da mudança
chore

### Arquivos alterados
- frontend/ (projeto Vite React inicializado)
- frontend/tailwind.config.js
- frontend/src/index.css
- frontend/src/services/api.js

### Impacto técnico/funcional
Setup completo do frontend: Vite + React, Tailwind CSS 3, Lucide React, Axios,
React Router DOM. Design system: Dark Mode OLED, cores primária #3B82F6 / acento
#DC2626, fontes Fira Code + Fira Sans. api.js com baseURL, timeout 30s e
interceptor de erro extraindo data.detail.
