## v2.00b — 2026-06-08

### Tipo da mudança
refactor

### Arquivos alterados
- app/services/face_service.py
- tests/unit/test_face_tracker.py

### Impacto técnico/funcional
Removida chamada redundante a `_close_stale_tracks` dentro de `add_detection`.
O worker já invoca esse método uma vez por frame antes do loop de detecção.
A chamada interna causava execução extra por cada rosto detectado por frame (N
chamadas ao invés de 1). Dois testes atualizados para refletir o novo contrato:
caller (worker) é responsável por chamar `_close_stale_tracks` antes de
`add_detection`. Novo teste RED→GREEN confirma ausência da chamada interna.
