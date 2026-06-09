## v2.00d — 2026-06-08

### Tipo da mudança
fix

### Arquivos alterados
- app/services/person_service.py
- tests/unit/test_person_service.py

### Impacto técnico/funcional
`merge_people` deletava os arquivos `.npy` do perfil secundário sem copiá-los
para o primário, descartando embeddings coletados em vídeos distintos. Agora,
antes de deletar, todos os embeddings do secundário são copiados para o primário
(até o limite `FACE_MAX_EMBEDDINGS_PER_PERSON`). Dois testes RED→GREEN adicionados:
um verifica a cópia efetiva, outro confirma que o limite máximo é respeitado.
