## v2.18 — 2026-06-09

### Tipo da mudança
feat

### Arquivos alterados
- frontend/src/pages/People.jsx
- frontend/src/pages/PersonDetail.jsx
- frontend/src/pages/VideoDetail.jsx
- frontend/src/test/PeopleTableView.test.jsx
- frontend/src/test/PersonDetail.test.jsx

### Impacto técnico/funcional

**feat(people): toggle grade/tabela com ordenação por nome**
- Barra de toggle (Grade / Tabela) adicionada abaixo do campo de busca.
- Visão de tabela exibe colunas: Nome (ordenável), Categoria, Cadastrado.
- Por padrão ordenado A→Z; clicar no header Nome inverte para Z→A (ChevronDown/Up visual).
- Ordenação também aplicada na visão grade (consistência).
- Modo mescla funciona nas duas visões (checkboxes na tabela).

**feat(timeline): timestamps como MM:SS e Início clicável para navegar ao vídeo**
- `fmtSec()` substituído por `fmtTime()`: converte segundos para `MM:SS`
  (ex.: 3618.4s → "60:18", 65.5s → "1:05").
- Coluna "Início" na Timeline de aparições é agora um botão clicável (cor primary,
  `data-testid="timeline-seek-{video_id}-{appearance_id}"`).
- Ao clicar, navega para `/videos/{video_id}` passando `state.seekTo = timestamp_start`.

**feat(video-detail): suporte a seekTo via navigation state**
- `VideoDetail` lê `location.state?.seekTo` na inicialização do estado.
- Quando navegado a partir do clique em "Início" na timeline, o player busca
  automaticamente o momento exato do vídeo e inicia a reprodução.
