## v1.61 — 2026-06-07

### Tipo da mudança
feat

### Arquivos alterados
- app/services/person_service.py
- app/api/v1/people.py
- app/core/settings.py
- tests/unit/test_person_service.py
- tests/integration/test_people.py

### Impacto técnico/funcional
Adicionada função reset_person_name em person_service.py, que
restaura o nome de uma pessoa para o padrão "Desconhecido #{id}".
Endpoint POST /api/v1/people/{id}/reset-name adicionado em
people.py, registrado antes das rotas genéricas /people/{person_id}.
5 novos testes (3 unitários + 2 integração). Suíte completa do
backend: 304/304.
