## v2.22.0 — 2026-06-09

### Tipo da mudança
chore

### Arquivos alterados
- frontend/package.json
- frontend/package-lock.json
- frontend/src/i18n/index.js
- frontend/src/i18n/locales/en/translation.json
- frontend/src/i18n/locales/pt-BR/translation.json
- frontend/src/main.jsx

### Impacto técnico/funcional
Instala e configura react-i18next, i18next e i18next-browser-languagedetector. Idioma padrão: inglês (fallback). Detecção/persistência via localStorage (chave `gw-language`). Configuração importada em main.jsx antes do app renderizar.
