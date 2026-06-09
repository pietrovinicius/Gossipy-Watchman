## v2.22.0 — 2026-06-09

### Tipo da mudança
chore

### Arquivos alterados
- frontend/src/i18n/locales/en/translation.json
- frontend/src/i18n/locales/pt-BR/translation.json

### Impacto técnico/funcional
Cria o catálogo completo de strings da interface organizado por namespace (common, nav, auth, dashboard, upload, videos, videoDetail, people, personDetail, employees, alerts, analytics, status, confirmModal, errors), em inglês (idioma padrão) e português BR. Chaves idênticas entre os dois arquivos; ausências em pt-BR fazem fallback para inglês.
