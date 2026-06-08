## v1.96.0 — 2026-06-08

### Tipo da mudança
feat | fix

### Arquivos alterados
- app/core/settings.py
- app/services/face_service.py
- app/db/migrate_embeddings.py
- tests/unit/test_face_service.py
- tests/unit/test_settings.py

### Impacto técnico/funcional
- Implementa normalização L2 nos embeddings gerados pelo SFace para assegurar que a distância Euclidiana seja estritamente equivalente à similaridade de cosseno.
- Atualiza o valor padrão de `FACE_RECOGNITION_TOLERANCE` no `settings.py` para `1.1` (limiar L2 equivalente à similaridade de cosseno recomendada de ~0.4 para SFace).
- Reduz o `score_threshold` do detector de faces YuNet de `0.8` para `0.6` para permitir a detecção de rostos mais distantes, de perfil ou sob resoluções mais baixas.
- Cria o script utilitário `app/db/migrate_embeddings.py` que permite recalibrar embeddings salvos anteriormente em `storage/faces/` com base nas imagens de referência usando o novo pipeline do SFace.
- Adicionados testes de unidade e verificação correspondentes.
