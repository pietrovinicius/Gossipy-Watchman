## v1.50 — 2026-06-06

### Tipo da mudança
feat

### Arquivos alterados
- app/services/person_service.py (save_face_sample, list_face_samples, MAX_FACE_SAMPLES)
- app/workers/video_worker.py (chama save_face_sample em cada reconhecimento de pessoa conhecida)
- app/schemas/person.py (FaceFrameResponse)
- app/api/v1/people.py (GET /people/{id}/frames)
- app/core/settings.py, frontend/package.json (bump 1.5.0)
- tests/unit/test_person_service.py, tests/integration/test_people.py

### Impacto técnico/funcional
Investigação prévia de storage/faces/ confirmou Opção B: o pipeline
salva apenas um recorte por pessoa ({id}.jpg + {id}_embedding.npy),
sem amostras adicionais por aparição.

Implementado save_face_sample(db, person_id, appearance_id, face_crop),
que persiste recortes em storage/faces/{person_id}_sample_{appearance_id}.jpg
(limite de 10 amostras por pessoa via MAX_FACE_SAMPLES, nunca propaga
exceção — log de warning e retorno None em falha de I/O). Integrado ao
video_worker para cada reconhecimento de pessoa já conhecida.

Novo endpoint GET /people/{person_id}/frames retorna a lista de imagens
faciais da pessoa (foto principal + amostras), cada uma com filename,
is_primary e url para /api/v1/faces/{filename}.

7 novos testes (5 unitários de serviço + 2 de integração de endpoint).
228/228 testes passando.
