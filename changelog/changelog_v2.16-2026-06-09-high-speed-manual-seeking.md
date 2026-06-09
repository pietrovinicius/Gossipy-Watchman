## v2.16 — 2026-06-09

### Tipo da mudança
fix

### Arquivos alterados
- frontend/src/components/VideoPlayer.jsx
- frontend/src/test/VideoPlayer.test.jsx

### Impacto técnico/funcional

**fix(videoplayer): velocidades > 16x agora funcionam via manual seeking**

- Antes: `playbackRate = 25/50/100` era silenciosamente limitado pelo browser
  (Chrome caps 16x, Firefox caps 8x) → vídeo não acelerava.
- Agora: velocidades > `MAX_NATIVE_RATE (16)` usam `setInterval` com
  `HIGH_SPEED_INTERVAL_MS = 200ms`:
  - A cada tick, avança `speed * 0.2` segundos em `currentTime`.
  - 25x → +5s por tick | 50x → +10s por tick | 100x → +20s por tick.
  - Ao atingir `duration`, intervalo para automaticamente.
- Velocidades ≤ 16x continuam usando `playbackRate` nativo (sem mudança).
- Ao voltar de high-speed para low-speed, `play()` é chamado automaticamente.
- Cleanup do intervalo no unmount do componente.
- 3 novos testes: setInterval chamado apenas para > 16x; avanço proporcional.
