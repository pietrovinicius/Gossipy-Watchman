## v2.22.0 — 2026-06-09

### Tipo da mudança
feat | test

### Arquivos alterados
- frontend/src/hooks/useLanguage.js
- frontend/src/components/LanguageToggle.jsx
- frontend/src/components/Layout.jsx
- frontend/src/test/LanguageToggle.test.jsx

### Impacto técnico/funcional
Adiciona hook `useLanguage` (wrapper sobre `i18n.changeLanguage`) e componente `LanguageToggle`, posicionado na sidebar acima do `ThemeToggle`. Alterna entre inglês (🇧🇷 para mudar) e português BR (🇺🇸 para mudar), com persistência via localStorage (`gw-language`). 5 testes novos cobrindo renderização, troca de idioma e persistência.
