## v2.00e — 2026-06-08

### Tipo da mudança
fix

### Arquivos alterados
- app/workers/video_worker.py
- tests/unit/test_worker_adaptive_cnn.py

### Impacto técnico/funcional
`_process_track` adicionava o embedding ao cache `known_embeddings` sem limite
por pessoa. Em vídeos longos com a mesma pessoa re-aparecendo N vezes, o cache
crescia N entradas para esse ID, tornando o k-NN enviesado e lento. Agora, o
append só ocorre se o número de entradas da pessoa no cache for menor que
`FACE_MAX_EMBEDDINGS_PER_PERSON`. Novo teste RED→GREEN confirma o comportamento.
