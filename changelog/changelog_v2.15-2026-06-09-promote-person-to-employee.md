## v2.15 — 2026-06-09

### Tipo da mudança
feat

### Arquivos alterados
- app/schemas/employee.py (PromoteToEmployeeRequest)
- app/schemas/person.py (PersonEmployeeInfo + employee em PersonResponse)
- app/services/employee_service.py (promote_person_to_employee)
- app/api/v1/people.py (POST /people/{id}/promote)
- frontend/src/pages/PersonDetail.jsx (botão + formulário de promoção)
- frontend/src/test/PersonDetail.test.jsx (5 novos testes)
- tests/unit/test_employee_service.py (4 novos testes RED→GREEN)

### Impacto técnico/funcional

**feat(people): fluxo "Promover a Funcionário" em PersonDetail**

- Quando `category === "Funcionário"` e `person.employee === null`, exibe botão
  "Promover a Funcionário" no card de perfil.
- Formulário inline com campos: Matrícula* (required), Departamento, Cargo.
- Submit chama `POST /api/v1/people/{id}/promote` → cria registro `Employee`
  vinculado à pessoa existente (sem nova foto/embedding necessário).
- Após sucesso, recarrega pessoa e exibe badge de funcionário com matrícula.
- Se `person.employee` já existir, exibe badge informativo em vez do botão.
- Backend valida: pessoa existe, não é já funcionária, matrícula única (HTTP 404/409).
- `PersonResponse` agora inclui campo `employee: PersonEmployeeInfo | None`.
