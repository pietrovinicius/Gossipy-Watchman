## v1.99-parcial — 2026-06-08

### Tipo da mudança
fix

### Arquivos alterados
- app/services/cluster_service.py
- app/services/appearance_service.py
- tests/unit/test_cluster_service.py
- tests/unit/test_appearance_service.py

### Impacto técnico/funcional

**Task 2 — cluster_service usa distância coseno (não Euclidiana):**
Substituído `np.linalg.norm(emb_i - emb_j)` por `1 - np.dot(emb_i, emb_j)` na construção do grafo de adjacência. ArcFace embeddings são L2-normalizados; usar Euclidiana com threshold 0.4 equivalia a coseno ≈ 0.08 — extremamente restrito, sub-agrupamento severo. Testes legados atualizados para 512-dim L2-normalizados.

**Task 6 — appearance_service usa settings.FACE_TRACK_GAP_TOLERANCE:**
Removido `_GAP_TOLERANCE_SECONDS = 2.0` hardcoded. Adicionado `from app.core.settings import settings` e `gap = settings.FACE_TRACK_GAP_TOLERANCE` em `upsert_appearance`. Gap agora configurável via `.env`/settings sem reimplantação.

445 testes passando.
