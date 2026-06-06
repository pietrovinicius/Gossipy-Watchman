## v1.26 — 2026-06-06

### Tipo da mudança
feat

### Arquivos alterados
- frontend/src/hooks/useVideoWebSocket.js (novo)
- frontend/src/hooks/useGlobalWebSocket.js (novo)
- frontend/src/pages/Dashboard.jsx (+ WS indicator + useGlobalWebSocket)
- frontend/src/test/useVideoWebSocket.test.jsx (novo — 6 testes TDD)
- frontend/src/test/people-limit.test.jsx (fix mock: + BACKEND_URL export)

### Impacto técnico/funcional
Sprint 7.6: Hooks WebSocket e Dashboard em tempo real.
- useVideoWebSocket(videoId): conecta /ws/video/{id}?token=, retorna {lastEvent, wsStatus}
- useGlobalWebSocket({onEvent}): conecta /ws/global?token=, dispara onEvent por mensagem
- URL WS derivada de BACKEND_URL com replace http→ws
- Dashboard: bolinha verde pulsante quando WS recebe evento de status; fetchData() disparado automaticamente
- 6 testes TDD (MockWebSocket fake); total frontend: 40/40 passando
- Build production: ✓ sem erros
