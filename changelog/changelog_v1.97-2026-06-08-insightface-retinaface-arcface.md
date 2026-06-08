## v1.97 — 2026-06-08

### Tipo da mudança
feat

### Arquivos alterados
- requirements.txt
- .env
- app/core/settings.py
- app/db/migrations/migration_insightface.py (novo)
- app/main.py
- app/services/face_service.py
- app/services/person_service.py
- app/services/search_service.py
- app/services/employee_service.py
- app/workers/video_worker.py
- tests/unit/test_settings.py
- tests/unit/test_migration_insightface.py (novo)
- tests/unit/test_face_service.py
- tests/unit/test_person_service.py
- tests/unit/test_search_service.py
- tests/unit/test_employee_service.py
- tests/unit/test_worker_adaptive_cnn.py
- tests/unit/test_face_tracker.py
- tests/integration/test_search.py
- tests/integration/test_video_worker.py
- docs/superpowers/specs/2026-06-08-insightface-accuracy-design.md (novo)
- docs/superpowers/plans/2026-06-08-insightface-accuracy.md (novo)

### Impacto técnico/funcional
Substitui completamente a stack de reconhecimento facial dlib/face_recognition (128-dim embeddings euclidianos) por InsightFace buffalo_l (RetinaFace detector + ArcFace 512-dim embeddings com distância coseno, threshold 0.4).

Principais mudanças:
- **face_service**: reescrito com InsightFace FaceAnalysis; singleton com CoreMLExecutionProvider para M4 Neural Engine; distância coseno (1 - dot product); k-NN voting e FaceTracker preservados; embeddings L2-normalizados
- **person_service**: suporte a múltiplos embeddings por pessoa (até 5, padrão FACE_MAX_EMBEDDINGS_PER_PERSON); arquivos nomeados `{id}_embedding_{n}.npy`; shape esperado 512
- **search_service**: distância coseno via InsightFace; seleção da maior face por área de bbox
- **employee_service**: detecção e extração de embedding com InsightFace; remove dependência do face_recognition
- **video_worker**: remove `get_adaptive_params` (parâmetros CNN dlib); passa `embedding=mean_embedding` ao `save_face_sample`
- **main.py**: lifespan executa `migration_insightface()` antes de `init_db()` e pre-aquece o modelo InsightFace
- **migration_insightface**: remove automaticamente arquivos `.npy` com shape (128,) em `storage/faces/` e `storage/employees/`
- **settings**: novas constantes INSIGHTFACE_MODEL, INSIGHTFACE_DET_SIZE, INSIGHTFACE_DET_SCORE, FACE_MAX_EMBEDDINGS_PER_PERSON; tolerância 0.4 (coseno); remove CNN_* e FACE_DETECTION_MODEL
- 434 testes passando (0 falhas)
