## v2.22.0 — 2026-06-09

### Tipo da mudança
feat

### Arquivos alterados
- frontend/src/pages/Dashboard.jsx
- frontend/src/pages/VideoDetail.jsx
- frontend/src/i18n/locales/en/translation.json
- frontend/src/i18n/locales/pt-BR/translation.json
- frontend/src/test/Dashboard.test.jsx
- frontend/src/test/DashboardActions.test.jsx
- frontend/src/test/VideoDetail.test.jsx
- frontend/src/test/VideoDetailActions.test.jsx

### Impacto técnico/funcional
Migração completa de Dashboard.jsx e VideoDetail.jsx para react-i18next (EN/PT-BR), incluindo
ConfirmModals de exclusão/reprocessamento, badges de status, AddPersonModal e cards de pessoa.
Adicionadas novas chaves de tradução (videoDetail.* para timeline, modal de adicionar pessoa,
mensagens de confirmação com interpolação de nome). Testes atualizados para asserções em inglês
(idioma padrão). Suíte segue com 234/235 (1 falha pré-existente em PersonFrames.test.jsx, fora de escopo).
