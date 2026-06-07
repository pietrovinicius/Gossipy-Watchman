## v1.83 — 2026-06-07 (Sprint 15 — Etapa 3: Modelo e Migração de Funcionários)

### Tipo da mudança
feat

### Impacto técnico/funcional

**15.3 — Backend: Modelo e Migração de Funcionários (CONCLUÍDA)**

✅ Backend:
- app/db/migrations/migration_v1_40.py expandido com tabela employees
- Tabela employees: id, name, registration (UNIQUE), department, role, photo_path, embedding_path, person_id (FK), active (default 1), notes, created_at, updated_at
- Índice unique: idx_employees_registration
- Migração idempotente (verifica IF NOT EXISTS)
- app/models/employee.py: modelo SQLAlchemy Employee com relationship bidirecional Person ↔ Employee
- app/models/person.py: adicionado relationship employee
- app/schemas/employee.py: Pydantic schemas EmployeeCreate, EmployeeUpdate, EmployeeResponse

✅ Testes (test_migration_v1_40.py):
- 6 testes cobrindo: criação de tabela, colunas corretas, índice único, constraint, idempotência, default value

Métricas:
- Backend: 360 testes passando (+6 de 15.3)
- Frontend: 180 testes passando (sem mudanças)

Performance:
- Migração run: <100ms
- Lookup registration: O(1) via índice

Próxima etapa: 15.4 (Serviço de funcionários com extração de embedding)
