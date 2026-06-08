## v1.9.1 — 2026-06-08

### Tipo da mudança
feat

### Arquivos alterados
- app/core/settings.py
- .env.example
- app/services/face_service.py
- app/workers/video_worker.py
- tests/unit/test_face_service.py
- tests/integration/test_video_worker.py

### Impacto técnico/funcional
Sprint 16.1 — filtro de qualidade de frame antes da extração de embeddings.

Nova função `is_good_quality_frame(location, frame, min_face_size, blur_threshold)`:
descarta rostos menores que `FACE_MIN_SIZE_PX` (60px) e rostos borrados, medidos
pela variância do Laplaciano abaixo de `FACE_BLUR_THRESHOLD` (100.0).

`extract_embeddings` refatorada: filtra `face_locations` pela qualidade antes de
gerar encodings (evita custo de encoding em rostos ruins) e agora retorna
`list[tuple[embedding, location]]` em vez de `list[embedding]` — necessário para
16.2 (FaceTracker) que precisa da posição do rosto para agregação por track.

Atualizado `video_worker.process_video` para desempacotar `(embedding, location)`.
Novas settings `FACE_MIN_SIZE_PX`, `FACE_BLUR_THRESHOLD`, `FACE_TRACK_GAP_TOLERANCE`,
`FACE_TRACK_MIN_SAMPLES`, `FACE_KNN_K` documentadas em `.env.example` (as três
últimas preparam 16.2/16.3).

6 novos testes unitários (`is_good_quality_frame` × 3, `extract_embeddings` × 3)
+ 4 mocks de integração ajustados para o novo formato de retorno. RED → GREEN
confirmado, suíte completa (381 testes) passando.
