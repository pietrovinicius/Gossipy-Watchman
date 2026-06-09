## v2.20 — 2026-06-09

### Tipo da mudança
feat

### Arquivos alterados
- frontend/src/pages/VideoDetail.jsx
- frontend/src/test/VideoDetail.test.jsx

### Impacto técnico/funcional

**feat(video-detail): split layout — player fixo esquerda, cards de pessoas direita**

Problema anterior: layout coluna única forçava scroll para ver o vídeo e os cards
ao mesmo tempo, tornando a análise de identificação confusa e difícil de operar.

Solução: layout split de duas colunas com `display: flex; align-items: flex-start`.

- **Coluna esquerda (58%)**: `position: sticky; top: 1rem` — VideoPlayer + barra de
  presença + controles de velocidade ficam sempre visíveis durante o scroll dos cards.
- **Coluna direita (42%)**: people panel com scroll normal da página. Ao clicar em
  segmento na barra de presença, o card da pessoa aparece à direita sem o player
  desaparecer do campo visual.
- **Header + summary cards**: mantidos em largura total acima do split, sem alteração
  de funcionalidade.
- `max-w-4xl` → `max-w-7xl` para aproveitar telas largas (monitores de vigilância).

Testes: 2 novos (RED→GREEN) verificando `data-testid="split-layout"` com classe `flex`
e `data-testid="people-panel"` como filho do split. Sticky wrapper mantém mesmo
`data-testid` para compatibilidade com testes existentes.
