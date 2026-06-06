## v0.19 — 2026-06-06

### Tipo da mudança
feat

### Arquivos alterados
- app/api/v1/people.py
- app/schemas/person.py (+ PersonUpdate com validator)
- app/services/person_service.py (+ list_people, get_person_by_id, update_person_name)
- app/main.py
- tests/integration/test_people.py

### Impacto técnico/funcional
GET /api/v1/people, GET /api/v1/people/{id}, PATCH /api/v1/people/{id}.
PersonUpdate rejeita string vazia via field_validator → HTTP 422 automático pelo Pydantic.
TDD: 6 testes de integração, todos passando.
