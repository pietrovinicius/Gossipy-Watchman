## v1.53 — 2026-06-06

### Tipo da mudança
feat

### Arquivos alterados
- frontend/src/components/PhotoModal.jsx
- frontend/src/components/PersonFrames.jsx
- frontend/src/components/ProfileQuality.jsx
- frontend/src/pages/PersonDetail.jsx
- frontend/src/test/PhotoModal.test.jsx
- frontend/src/test/PersonFrames.test.jsx
- frontend/src/test/ProfileQuality.test.jsx
- app/core/settings.py
- frontend/package.json

### Impacto técnico/funcional
Integra ao PersonDetail os 3 componentes da Sprint 9 (9.4-9.6): modal de zoom acessível
da foto de perfil (PhotoModal, com Portal/focus trap/Escape/click-outside), galeria de
frames detectados com ação "Definir como principal" (PersonFrames) e painel de qualidade
do perfil com sinal semafórico, score e recomendação (ProfileQuality). 21 novos testes de
componente (vitest), suíte completa: 91/91 frontend e 248/248 backend passando, build de
produção OK.
