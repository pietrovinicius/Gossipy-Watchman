## v1.99c — 2026-06-08

### Tipo da mudança
feat

### Arquivos alterados
- app/services/face_service.py
- app/core/settings.py
- tests/unit/test_face_service.py

### Impacto técnico/funcional

**Task 4 — Filtro de pose facial (ângulos extremos):**
`is_good_quality_frame` recebia rostos de perfil e adicionava embeddings de baixa qualidade ao track, degradando a média. Fix: novos parâmetros `pose: np.ndarray | None`, `max_yaw_deg` (default 40°), `max_pitch_deg` (default 30°). Quando `pose` é informado e `abs(yaw) > 40°` ou `abs(pitch) > 30°`, frame descartado antes da extração de embedding.

`extract_embeddings` agora lê `face.pose` do objeto InsightFace (atributo presente em buffalo_l) e passa ao filtro. Rostos de perfil ou com inclinação excessiva não entram no FaceTracker.

Constantes `FACE_MAX_YAW_DEG = 40.0` e `FACE_MAX_PITCH_DEG = 30.0` adicionadas em `app/core/settings.py`.

305 testes passando.
