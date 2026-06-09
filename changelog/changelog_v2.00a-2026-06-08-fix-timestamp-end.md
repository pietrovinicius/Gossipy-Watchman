## v2.00a — 2026-06-08

### Tipo da mudança
fix

### Arquivos alterados
- app/services/appearance_service.py
- app/workers/video_worker.py
- tests/unit/test_appearance_service.py

### Impacto técnico/funcional
`upsert_appearance` recebia um único `timestamp` (= `track.start_time`) e gravava
`timestamp_end = timestamp` — o campo nunca refletia o fim real da aparição.

Nova assinatura: `timestamp_start: float, timestamp_end: float`. O worker passa
`track.start_time` e `track.last_seen` respectivamente. Aparições próximas
(gap < `FACE_TRACK_GAP_TOLERANCE`) têm `timestamp_end` estendido para o máximo
entre o fim existente e o novo. Todos os testes antigos atualizados para a nova
assinatura; 3 novos testes RED→GREEN adicionados.
