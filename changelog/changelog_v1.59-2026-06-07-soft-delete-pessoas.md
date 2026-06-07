## v1.59 — 2026-06-07

### Tipo da mudança
feat

### Arquivos alterados
- app/services/person_service.py
- app/api/v1/people.py
- app/core/settings.py
- tests/unit/test_person_service.py
- tests/integration/test_people.py

### Impacto técnico/funcional
Implementado soft delete de pessoas: soft_delete_person e
restore_person em person_service.py marcam/limpam deleted_at de
forma idempotente. list_people ganha parâmetro include_deleted
(filtra WHERE deleted_at IS NULL por padrão). Endpoints
DELETE /api/v1/people/{id} e POST /api/v1/people/{id}/restore
adicionados em people.py, registrados antes das rotas genéricas
/people/{person_id}. GET /api/v1/people aceita include_deleted.
11 novos testes (6 unitários + 5 integração). Suíte completa do
backend: 280/280.
