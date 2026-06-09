## v2.11 — 2026-06-09

### Tipo da mudança
feat

### Arquivos alterados
- frontend/src/components/VideoPlayer.jsx
- frontend/src/test/VideoPlayer.test.jsx

### Impacto técnico/funcional

**feat(player): legenda de pessoas retrátil por padrão**

- Quando `people.length > 5`, legenda recolhida automaticamente.
- Botão `data-testid="legend-toggle"` exibe "Ver legenda (N pessoas)" / "Recolher legenda".
- Elimina a quebra de layout causada por 67 nomes empilhados sobre o player.
- Quando ≤5 pessoas, legenda sempre visível (comportamento anterior preservado).
