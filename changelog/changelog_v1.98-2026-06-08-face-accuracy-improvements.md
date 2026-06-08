## v1.98 — 2026-06-08

### Tipo da mudança
feat + fix + perf

### Arquivos alterados
- app/core/settings.py
- app/services/face_service.py
- app/workers/video_worker.py
- tests/unit/test_face_service.py
- tests/unit/test_worker_adaptive_cnn.py
- tests/integration/test_video_worker.py
- FACE_ACCURACY_PLAN.md (novo)

### Impacto técnico/funcional

**Task 1 — Fix person_counter (bug crítico):**
`person_counter` agora inicializa com `db.query(Person).count()` em vez de `db.query(Video).count()`. Pessoas novas recebiam índice baseado no número de vídeos, não de pessoas existentes.

**Task 2 — Cache de embeddings por vídeo (performance):**
`get_all_embeddings` é chamado uma única vez no início de `process_video` e passado como parâmetro para `_process_track`. Ao criar nova pessoa, o embedding é adicionado ao cache local imediatamente, evitando re-leitura de disco a cada track. `_process_track` agora retorna `(person_counter, known_embeddings)`.

**Tasks 3+5 — FaceTrack: crop + média ponderada por det_score (memória + acurácia):**
`FaceTrack._frames_data` armazena apenas o crop da face (não o frame completo), reduzindo uso de memória de ~900KB/frame para alguns KB. `add_frame_data` aceita `det_score` e o armazena para ponderação. `mean_embedding` usa `np.average` ponderado por `det_score`, melhorando a qualidade do embedding médio. `extract_embeddings` retorna 3-tuples `(embedding, location, det_score)`.

**Task 4 — Motion Gating com fallback periódico (detecção em cenas estáticas):**
Novo setting `MOTION_GATING_FORCE_INTERVAL: int = 5`. Worker força detecção a cada 5 segundos mesmo sem movimento detectado, evitando que pessoas paradas sejam completamente ignoradas. `last_forced_detection` rastreia o último segundo com detecção executada.

**Testes:** 441 passando (0 falhas). Testes legados atualizados para 3-tuples em `extract_embeddings` e nova assinatura de `_process_track`.
