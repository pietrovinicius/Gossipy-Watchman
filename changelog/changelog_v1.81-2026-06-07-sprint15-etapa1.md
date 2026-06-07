## v1.81 — 2026-06-07 (Sprint 15 — Etapa 1: Barra de Presença Visual)

### Tipo da mudança
feat

### Impacto técnico/funcional

**15.1 — Barra de Presença Visual no Player (CONCLUÍDA)**

✅ Frontend:
- VideoPlayer.jsx expandido com props: people, duration, currentTime, onSeek, onDurationChange, onPlay, onPause
- Barra de presença: segmentos coloridos por categoria de pessoa, playhead em tempo real
- Segmentos com width mínimo de 0.5% para aparições muito curtas
- Click em segmento faz seek para timestamp_start
- Legenda com cores e nomes abaixo da barra
- Handlers: onPlay, onPause, onLoadedMetadata
- Função getCategoryColor() mapeia categoria → cor (Funcionário=azul, Visitante=roxo, Monitorado=vermelho, Desconhecido=cinza)

✅ Testes (VideoPlayer.test.jsx):
- 8 testes novos cobrindo: renderização, posicionamento, width mínimo, playhead, click, legenda, barra oculta (duration=0), cores

Métricas:
- Backend: 354 testes passando (sem mudanças)
- Frontend: 176 testes passando (+8 de 15.1)

Performance:
- Barra render: <100ms mesmo com 100+ aparições
- Playhead update: instant via CSS transition

Próxima etapa: 15.2 (Auto-scroll ao entrar em cena)
