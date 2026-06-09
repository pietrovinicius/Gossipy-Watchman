## v1.99d — 2026-06-08

### Tipo da mudança
fix

### Arquivos alterados
- app/workers/video_worker.py
- tests/unit/test_worker_adaptive_cnn.py

### Impacto técnico/funcional

**Task 5 — Atualização do cache known_embeddings para pessoa conhecida:**
O cache `known_embeddings` era carregado uma vez antes do loop e nunca atualizado quando uma pessoa conhecida era identificada num track. Isso causava degradação progressiva: o k-NN não se beneficiava dos embeddings coletados durante o próprio vídeo.

Fix: após `save_face_sample`, `_process_track` agora faz `known_embeddings.append((person_id, mean_embedding))`. Cada track de pessoa conhecida enriquece o cache in-memory para os tracks subsequentes do mesmo vídeo.

455 testes passando.
