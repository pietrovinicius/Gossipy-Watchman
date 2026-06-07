## v1.72 — 2026-06-07

### Tipo da mudança
chore

### Arquivos alterados
- Consolidação Sprint 13 completa

### Impacto técnico/funcional

**SPRINT 13 CONCLUÍDA — Player de Vídeo com Sincronização de Timeline**

Backend (v1.69):
  - GET /api/v1/videos/{id}/stream?token=JWT
  - HTTP 206 Range requests (RFC 7233) para seek eficiente
  - StreamingResponse com iterfile() sem carregar na memória
  - 7 testes de integração (auth, deleted, 404, 200, 206, range)

Frontend (v1.70-v1.71):
  - VideoPlayer component com controles HTML5 nativos
  - Velocidade 0.5x 1x 1.5x 2x com toggle ativo
  - Sincronização timeline→player: click em row = seek
  - Sincronização player→timeline: badge "EM CENA" em tempo real
  - useMemo(getPeopleOnScreen) para highlight sem re-renders desnecessários
  - 8 testes VideoPlayer (src, timeUpdate, seekTo, speedButtons)
  - 55 linhas modificadas em VideoDetail para integração

Resultado:
  - Backend: 332 testes (7 novos)
  - Frontend: 176 testes (8 novos)
  - Build: 0 erros
  - 3 commits (v1.69 streaming, v1.70 VideoPlayer, v1.71 sincronização)

Decisões técnicas:
  - Token via query param (não header) para streaming autenticado
  - seekTo={null} pattern para controlar seek sem efeito colateral
  - useMemo + peopleOnScreen para evitar re-renderização custosa
  - Border+badge para highlight ao invés de background change (menos flashy)

Performance:
  - Range requests: seek instantâneo sem buffer (HTTP 206)
  - Debounce não necessário (onTimeUpdate já é throttled pelo navegador)
  - VideoPlayer componente puro (sem hooks pesados)

Próximos passos:
  - Barra de presença visual (Sprint 14, opcional)
  - Auto-scroll quando pessoa entra em cena (baixa prioridade)
  - Cache de Range requests (muito avançado)
