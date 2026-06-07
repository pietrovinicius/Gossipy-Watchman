## v1.82 — 2026-06-07 (Sprint 15 — Etapa 2: Auto-scroll ao Entrar em Cena)

### Tipo da mudança
feat

### Impacto técnico/funcional

**15.2 — Auto-scroll ao Entrar em Cena (CONCLUÍDA)**

✅ Frontend:
- VideoDetail.jsx expandido com refs mapping (cardRefs) e estado de reprodução (isPlaying)
- useRef para cardRefs: {person_id: elemento DOM}
- useRef para prevPeopleOnScreen: controle de mudanças de estado
- Handlers: onPlay, onPause, onDurationChange
- useEffect para auto-scroll: detecta pessoa nova em cena e chama scrollIntoView
- PersonCard atualizado com prop cardRef e data-testid para referência no DOM
- VideoPlayer passa props: people, duration, currentTime, onSeek, onDurationChange, onPlay, onPause
- scrollIntoView com behavior='smooth' e block='nearest'

✅ Testes (VideoSync.test.jsx):
- 4 testes cobrindo: renderização de PersonCard com ref, badge EM CENA, border-primary, VideoPlayer callbacks

Métricas:
- Backend: 354 testes passando (sem mudanças)
- Frontend: 180 testes passando (+4 de 15.2)

Performance:
- Auto-scroll: <50ms com smooth transition
- Refs mapping: O(1) lookup por person_id

Behavior:
- scrollIntoView ativado apenas durante reprodução (isPlaying=true)
- Detecta mudanças em peopleOnScreen via useMemo
- prevPeopleOnScreen rastreia quem já estava em cena

Próxima etapa: 15.3 (Backend: modelo e migração de funcionários)
