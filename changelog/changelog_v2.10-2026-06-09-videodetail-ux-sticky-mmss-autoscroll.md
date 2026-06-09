## v2.10 — 2026-06-09

### Tipo da mudança
feat

### Arquivos alterados
- frontend/src/pages/VideoDetail.jsx
- frontend/src/test/VideoDetail.test.jsx
- frontend/package.json
- app/core/settings.py

### Impacto técnico/funcional

**feat(videodetail): player sticky + formato MM:SS + auto-scroll ao clicar**

**A — Player sticky:**
- Wrapper do `VideoPlayer` agora tem `sticky top-0 z-20 bg-background pb-3`.
- Player permanece visível enquanto o usuário rola pelos cards de pessoas.
- `data-testid="player-sticky-wrapper"` para testabilidade.

**B — Formato MM:SS:**
- Substituída `fmtSec(s)` (retornava `"1208.4s"`) por `fmtMmSs(s)` (retorna `"20:08"`).
- Afeta: Presente por, Primeira vez, Última vez, Início e Fim da tabela de aparições, botão PlayCircle.

**C — Auto-scroll ao clicar em timestamp:**
- `handleSeekClick(ts)` chama `setSeekTo(ts)` + `playerRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' })`.
- Usuário clica na linha da timeline → vídeo salta para o instante + tela rola até o player automaticamente.
