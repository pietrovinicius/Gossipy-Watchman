## v1.27 — 2026-06-06

### Tipo da mudança
chore

### Arquivos alterados
- Anotacoes.txt (versão 1.1.0 → 1.2.0 + decisões técnicas 6/7/8)

### Impacto técnico/funcional
Sprint 7.7: Verificação final Sprint 7.
- 186 pytest passando (186 backend)
- 40 vitest passando (40 frontend)
- Build production: ✓ sem erros
- Anotacoes.txt atualizado: v1.2.0, decisões técnicas de WS e CSV documentadas
- Sprint 7 completa: Export CSV + WebSocket tempo real (ConnectionManager,
  endpoints /ws/video/{id} e /ws/global, _broadcast_sync no worker,
  hooks useVideoWebSocket e useGlobalWebSocket, indicador WS no Dashboard)
