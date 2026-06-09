## v2.14 — 2026-06-09

### Tipo da mudança
feat

### Arquivos alterados
- frontend/src/pages/VideoDetail.jsx
- frontend/src/test/VideoDetail.test.jsx

### Impacto técnico/funcional

**feat(videodetail): botões seek+pause dinâmicos — um por aparição visível**

- Antes: um único botão `[▶] [28:56]` usando `first_seen_at`.
- Agora: `[▶] [28:56] [29:09] [29:55]` — um botão por aparição em `visibleAppearances`.
- `data-testid` atualizado para `seek-pause-{person_id}-{appearance_id}` para identificação única.
- Se a timeline estiver recolhida, mostra botões apenas das 3 primeiras aparições; ao expandir, exibe todas.
- `[▶]` continua reproduzindo da primeira aparição; cada timestamp pausa exatamente naquele instante.
