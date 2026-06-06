## v1.34 — 2026-06-06

### Tipo da mudança
feat

### Arquivos alterados
- frontend/src/pages/Alerts.jsx (novo)
- frontend/src/router.jsx (+ rota /alerts)
- frontend/src/components/Layout.jsx (+ nav item Alertas com badge de não vistos)
- frontend/src/test/Alerts.test.jsx (novo — 5 testes TDD)

### Impacto técnico/funcional
Sprint 8.6: página de alertas de watchlist no frontend.
- /alerts: lista todos os alertas com indicador visual (seen/unseen via data-seen attr)
- Botão "Marcar como visto" chama PATCH /alerts/seen e atualiza estado local imutavelmente
- Toast WebSocket: useGlobalWebSocket detecta watchlist_alert → toast 5s + refresh da lista
- Layout.jsx: badge no nav item "Alertas" mostrando contagem de não vistos (GET /alerts/count)
- Estado de loading com spinner role="status"
- Estado vazio com mensagem "Nenhum alerta registrado"
- 5/5 vitest passando; total frontend: 45 testes
