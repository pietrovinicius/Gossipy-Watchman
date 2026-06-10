## v2.22.0 — 2026-06-10

### Tipo da mudança
feat | test

### Arquivos alterados
- frontend/src/utils/formatDate.js
- frontend/src/utils/formatDate.test.js
- frontend/src/pages/Dashboard.jsx
- frontend/src/pages/VideoDetail.jsx

### Impacto técnico/funcional
`formatDateTime(dateStr, locale = 'pt-BR')` passa a aceitar locale opcional, repassado
para `Date.toLocaleString`. Dashboard e VideoDetail agora chamam
`formatDateTime(date, i18n.language)`, exibindo DD/MM/AAAA HH:mm em pt-BR e
M/D/AAAA h:mm AM/PM em en. Testado via TDD: novos casos cobrindo formato pt-BR
(DD/MM/YYYY, 24h) e en (M/D/YYYY, 12h AM/PM).

Suite completa: PASS(236) FAIL(1) — única falha pré-existente e não relacionada
(`PersonFrames.test.jsx`).
