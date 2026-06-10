## v2.22.0 — 2026-06-10

### Tipo da mudança
feat | fix

### Arquivos alterados
- frontend/src/pages/Upload.jsx
- frontend/src/pages/VideosCatalog.jsx
- frontend/src/pages/Alerts.jsx
- frontend/src/pages/AnalyticsDashboard.jsx
- frontend/src/components/Layout.jsx
- frontend/src/pages/Login.jsx
- frontend/src/i18n/locales/en/translation.json
- frontend/src/i18n/locales/pt-BR/translation.json
- frontend/src/test/Upload.test.jsx
- frontend/src/test/VideosCatalog.test.jsx
- frontend/src/test/Alerts.test.jsx
- frontend/src/test/ThemeToggle.test.jsx
- frontend/vite.config.js
- frontend/src/test/setup-i18n.js (novo)

### Impacto técnico/funcional
Migração da Prioridade 2 (17.4) para react-i18next: Upload, VideosCatalog, Alerts e
AnalyticsDashboard agora usam `useTranslation()`/`t()`, com novas chaves nos namespaces
`upload`, `videos`, `alerts` e `analytics` (en/pt-BR). VideosCatalog reutiliza o padrão
`STATUS_COLORS`/`key` (já usado no Dashboard) para mapear status do backend (Pendente/
Processando/Concluído/Erro) para chaves `status.*`. Datas em VideosCatalog e Alerts
passam a usar `i18n.language === 'pt-BR' ? 'pt-BR' : 'en-US'` para `toLocaleDateString`/
`toLocaleString`.

Também commitados arquivos remanescentes da etapa 17.3 (LanguageToggle/sidebar) que
ficaram sem commit anteriormente: `Layout.jsx` (nav items via `nav.*`, aria-labels),
`Login.jsx` (textos via `auth.*`), `vite.config.js` (registro de `setup-i18n.js` nos
`setupFiles` do Vitest) e ajustes em `ThemeToggle.test.jsx`.

**Correção crítica (bugfix global de pluralização):** i18next v26 (API v4) não reconhece
mais o sufixo legado `_plural`. Chaves como `people_plural`/`videos_plural`/
`appearances_plural`/`resultsCount_plural`/`count_plural`/`totalCount_plural`
caíam silenciosamente no singular para qualquer contagem. `compatibilityJSON: 'v3'`
NÃO resolve em v26 (testado). Correção: renomeado globalmente `_plural` → `_other`
em ambos os arquivos de tradução (`sed -i '' 's/_plural"/_other"/g'`), restaurando
pluralização correta em todos os módulos já migrados (Dashboard, VideoDetail, People,
PersonDetail, Employees) e nos novos (VideosCatalog, Analytics).

Suite completa: PASS(234) FAIL(1) — única falha pré-existente e não relacionada
(`PersonFrames.test.jsx`).
