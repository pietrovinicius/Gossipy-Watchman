## v1.40 — 2026-06-06

### Tipo da mudança
chore

### Arquivos alterados
- Anotacoes.txt (versão, contagem de testes, tabela de endpoints, decisões #9 e #10)
- app/core/settings.py (APP_VERSION 1.3.0 → 1.4.0)
- frontend/package.json (version 1.3.0 → 1.4.0)

### Impacto técnico/funcional
Encerramento da Sprint 8 (Watchlist, Busca por Similaridade e Analytics).

Verificação final (8.9):
- pytest completo: 220 passed
- npm test (vitest) completo: 58 passed
- npm run build: sucesso

Resumo da sprint (8.1–8.9):
- Watchlist: marcação "Monitorado" + alertas em tempo real (WS) com dedupe por vídeo
- search_by_face(): busca por similaridade via embeddings, com query_time_ms exposto no response (carga de embeddings do disco a cada request — ponto de discussão técnica documentado em Anotacoes.txt #9)
- Endpoints /analytics/* (overview, timeline, top-people, appearances-per-video)
- Frontend: páginas Alerts, busca por face em People, AnalyticsDashboard com recharts
- Documentação consolidada em Anotacoes.txt; versão sincronizada (backend + frontend) em 1.4.0
