## v1.15 — 2026-06-06

### Tipo da mudança
feat

### Arquivos alterados
- app/services/person_service.py (+ update_person_details, get_person_stats, merge_people)
- app/schemas/person.py (PersonUpdate agora com fields opcionais; + PersonStatsResponse, MergeRequest)
- app/api/v1/people.py (PATCH usa update_person_details; + GET /{id}/stats, POST /merge com ordenação correta)
- tests/unit/test_person_service.py (+ 11 testes: update_person_details x5, get_person_stats x2, merge_people x4)
- tests/integration/test_people.py (+ 6 testes: notes/category, stats, merge, self-merge, 404)

### Impacto técnico/funcional
Sprint 6.2: Endpoints e serviços de gestão de pessoas.
- PATCH /people/{id} aceita name/notes/category opcionais; não sobrescreve campos não enviados
- GET /people/{id}/stats retorna video_count, total_seconds, first_seen, last_seen
- POST /people/merge registrado ANTES de GET /{id} para evitar colisão de rota FastAPI
- merge_people reassocia appearances, deleta .npy/.jpg do secundário, deleta Person secundário
- MergeRequest valida secondary_ids não vazio e não contém primary_id (→ 422)
- Total: 159 testes passando (era 142 após 6.1)
