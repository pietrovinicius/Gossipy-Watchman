## v2.06 — 2026-06-09

### Tipo da mudança
feat

### Arquivos alterados
- frontend/src/components/VideoPlayer.jsx
- frontend/src/test/VideoPlayer.test.jsx

### Impacto técnico/funcional

**feat(player): adiciona velocidades de reprodução 6x, 10x e 25x**
- Array de velocidades expandido de `[0.5, 1, 1.5, 2]` para `[0.5, 1, 1.5, 2, 6, 10, 25]`.
- `videoElement.playbackRate` é 100% client-side — zero impacto no backend ou processador do servidor.
- Novo teste cobre presença dos três botões adicionados.
