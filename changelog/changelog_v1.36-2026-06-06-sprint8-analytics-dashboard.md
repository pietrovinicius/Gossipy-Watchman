## v1.36 — 2026-06-06

### Tipo da mudança
feat

### Arquivos alterados
- frontend/src/pages/AnalyticsDashboard.jsx (novo)
- frontend/src/router.jsx (+ rota /analytics)
- frontend/src/components/Layout.jsx (+ nav item Analytics)
- frontend/src/test/AnalyticsDashboard.test.jsx (novo — 6 testes TDD)
- frontend/package.json (+ recharts)
- frontend/package-lock.json (atualizado)

### Impacto técnico/funcional
Sprint 8.8: dashboard de analytics com recharts.
- /analytics: page com 3 metric cards (vídeos/pessoas/aparições)
- LineChart: atividade de upload nos últimos 30 dias
- BarChart (horizontal): top 10 pessoas por aparições + lista textual para acessibilidade
- BarChart (vertical): aparições por vídeo (top 10)
- Fetch paralelo via Promise.all de 4 endpoints analytics
- Mocks recharts no teste: ResponsiveContainer/LineChart/BarChart/PieChart como divs com data-testid
- recharts adicionado via npm install (sem configuração especial)
- 6/6 vitest passando; total frontend: 58 testes
