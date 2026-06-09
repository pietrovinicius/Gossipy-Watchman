## v2.09 — 2026-06-09

### Tipo da mudança
feat

### Arquivos alterados
- frontend/src/components/VideoPlayer.jsx
- frontend/src/test/VideoPlayer.test.jsx

### Impacto técnico/funcional

**feat(player): adiciona velocidades 50x e 100x**
- Array expandido: `[0.5, 1, 1.5, 2, 6, 10, 25, 50, 100]`.
- 100% client-side via `videoElement.playbackRate`, zero impacto no backend.
- Nota: Chrome/Safari limitam `playbackRate` a 16x internamente; Firefox não tem limite.
