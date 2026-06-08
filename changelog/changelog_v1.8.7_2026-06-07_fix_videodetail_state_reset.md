## v1.8.7 — 2026-06-07

### Corrigido

**VideoDetail.jsx**: Reset completo de estado ao trocar videoId.

- `useEffect` agora depende de `[id, fetchDetail]` (antes: `[fetchDetail]` apenas)
- Ao navegar entre vídeos (/videos/1 → /videos/2), estado local é zerado antes do novo fetch:
  - `detail` → `null` (evita mistura visual com dados antigos)
  - `currentTime` → `0`
  - `seekTo` → `null`
  - `videoDuration` → `0`
  - `isPlaying` → `false`
  - `error` → `''`
- `VideoPlayer` agora recebe `key={id}` para forçar remontagem completa do elemento `<video>` ao trocar vídeos

**Impacto:** Bug onde pessoas de vídeos anteriores apareciam visualmente em VideoDetail durante transição foi eliminado.

**Testes:** Adicionado teste de validação de reset de estado. Todos os testes (183) passam.
