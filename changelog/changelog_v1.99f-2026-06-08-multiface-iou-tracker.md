## v1.99f — 2026-06-08

### Tipo da mudança
feat

### Arquivos alterados
- app/services/face_service.py
- app/workers/video_worker.py
- app/core/settings.py
- tests/unit/test_face_tracker.py
- tests/unit/test_face_service.py
- tests/integration/test_video_worker.py

### Impacto técnico/funcional

**Task 1 — FaceTracker multi-face com associação por IoU:**
O FaceTracker anterior usava `active_track` singular, impossibilitando distinguir múltiplas pessoas simultâneas — todos os embeddings iam para o mesmo track, gerando perfil híbrido inválido.

Fix:
- `active_track: FaceTrack | None` substituído por `active_tracks: list[tuple[np.ndarray, FaceTrack]]` (last_bbox, track)
- `_iou(bbox_a, bbox_b)` adicionado como helper módulo-level para calcular Intersection-over-Union entre bboxes [x1,y1,x2,y2]
- `add_detection` aceita novo parâmetro `bbox: np.ndarray | None`; quando presente, associa detecção ao track com maior IoU ≥ `FACE_TRACK_IOU_THRESHOLD (0.3)`; sem match → novo track
- `_close_stale_tracks(current_time)` fecha tracks expirados (gap > tolerance) a cada frame
- `flush()` fecha todos os tracks ativos restantes
- `active_track` mantido como property para retrocompatibilidade (retorna track único se houver exatamente 1)
- `extract_embeddings` passa a retornar 4-tuple: `(embedding, location, det_score, bbox)`
- Worker desempacota 4-tuple e passa `bbox` ao tracker; chama `_close_stale_tracks` antes de cada rodada de detecções
- Setting `FACE_TRACK_IOU_THRESHOLD: float = 0.3` adicionado

464 testes passando.
