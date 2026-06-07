## v1.62 — 2026-06-07

### Tipo da mudança
feat

### Arquivos alterados
- frontend/src/components/ConfirmModal.jsx
- frontend/src/test/ConfirmModal.test.jsx
- frontend/package.json

### Impacto técnico/funcional
Criado componente reutilizável ConfirmModal (React Portal) para
confirmações de ações destrutivas/sensíveis: título, mensagem,
labels customizáveis, variantes de cor (danger/warning/info),
fechamento via Escape e overlay, e modo requireTyping que exige
digitar uma palavra exata (confirmWord) para habilitar o botão de
confirmação. Base para soft delete e reprocessamento na UI
(People, PersonDetail, Dashboard, VideoDetail). 8 novos testes.
Suíte completa do frontend: 122/122.
