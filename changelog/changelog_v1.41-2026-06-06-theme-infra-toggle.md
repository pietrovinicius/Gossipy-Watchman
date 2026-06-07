## v1.41 — 2026-06-06

### Tipo da mudança
feat

### Arquivos alterados
- frontend/src/contexts/ThemeContext.jsx (novo)
- frontend/src/main.jsx (envolve app com ThemeProvider)
- frontend/tailwind.config.js (darkMode: 'class' + tokens semânticos via CSS vars)
- frontend/src/index.css (define --color-* para .dark/.light, --chart-grid/--chart-text, transições suaves)
- frontend/src/components/Layout.jsx (componente ThemeToggle na sidebar)
- frontend/src/pages/AnalyticsDashboard.jsx (recharts usa var(--chart-grid)/var(--chart-text))
- frontend/src/test/setup.js (polyfill localStorage/matchMedia para jsdom)
- frontend/src/test/ThemeContext.test.jsx (novo — 7 testes)
- frontend/src/test/ThemeToggle.test.jsx (novo — 5 testes)

### Impacto técnico/funcional
Implementa modo diurno (light) com alternância dark/light persistida.

Tokens do light mode (fallback oficial da spec — skill ui-ux-pro-max
indisponível neste projeto):
- Fundo #F8FAFC · Superfície #FFFFFF · Card #F1F5F9 · Borda #E2E8F0
- Texto #0F172A · Texto muted #475569 · Primária #3B82F6 · Acento #DC2626

Decisão de arquitetura: em vez de migrar centenas de classes para
`dark:` variant arquivo a arquivo, os tokens semânticos já existentes
(`bg-surface`, `text-text-base`, `border-border`, `bg-bg`, etc — usados
uniformemente em ~250 ocorrências) tiveram seus VALORES redefinidos via
CSS custom properties (`--color-*`) que trocam de acordo com a classe
`.dark`/`.light` aplicada ao `<html>` pelo ThemeContext. Tailwind
referencia esses tokens como `rgb(var(--color-x) / <alpha-value>)`.
Resultado: suporte dual completo, zero edição por arquivo, zero risco
de classe esquecida — DRY/KISS preservados.

Gráficos recharts (Sprint 8) passam a usar `var(--chart-grid)` e
`var(--chart-text)` para grid/eixos, reagindo ao tema sem JS adicional.

ThemeContext: prioridade localStorage → preferência do sistema → dark.
Toggle na sidebar com ícones Sun/Moon (lucide), aria-label dinâmico,
foco visível via ring, transição rotate-0→rotate-180.

Testes: 12 novos (ThemeContext + ThemeToggle), 70/70 vitest passando.
Build de produção: sucesso, 0 erros.
