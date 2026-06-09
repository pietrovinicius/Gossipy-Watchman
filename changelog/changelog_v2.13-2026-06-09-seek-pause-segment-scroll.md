## v2.13 — 2026-06-09

### Tipo da mudança
feat

### Arquivos alterados
- frontend/src/pages/VideoDetail.jsx
- frontend/src/components/VideoPlayer.jsx
- frontend/src/test/VideoDetail.test.jsx
- frontend/src/test/VideoPlayer.test.jsx

### Impacto técnico/funcional

**feat(videodetail): timestamp clicável seek+pause e barra de presença scroll para card**

**A — Botão de timestamp separado no card da pessoa:**
- Ícone ▶ (PlayCircle) → seek + play (comportamento existente preservado).
- Texto `MM:SS` ao lado → seek + **pause** (novo: `data-testid="seek-pause-{id}"`).
- Implementado via `handleSeekAndPause(ts)` → `setPauseSeekTo({ time: ts })` + scroll até o player.
- VideoPlayer recebe novo prop `pauseSeekTo` com useEffect que chama `.pause()` sem `.play()`.

**B — Segmento da barra de presença → scroll para card da pessoa:**
- VideoPlayer recebe novo prop `onSegmentSeek(person_id, timestamp)`.
- Ao clicar num segmento, VideoDetail chama `handleSegmentSeek` → seek + `cardRefs.current[person_id].scrollIntoView()`.
- Usuário clica no traço cinza da timeline → vídeo pula para o instante E tela rola para o card da pessoa.
