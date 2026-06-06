## v1.31 — 2026-06-06

### Tipo da mudança
feat

### Arquivos alterados
- app/workers/video_worker.py (+ lógica watchlist: alerted_in_this_video set, create_alert, broadcast watchlist_alert)
- tests/integration/test_video_worker.py (+ 3 testes TDD watchlist)

### Impacto técnico/funcional
Sprint 8.3: Integração da watchlist no worker.
- Após find_matching_person, verifica se person.category == Monitorado
- alerted_in_this_video: set[int] garante um único alerta por pessoa por vídeo (mesmo em múltiplos frames)
- create_alert() persiste no banco; _broadcast_sync emite evento watchlist_alert via WebSocket
- Payload do evento: event, video_id, person_id, person_name, alert_id, timestamp_in_video, message, severity
- Funcionário/Visitante/Desconhecido: sem alerta
- 3/3 testes TDD passando; total: 203 pytest
