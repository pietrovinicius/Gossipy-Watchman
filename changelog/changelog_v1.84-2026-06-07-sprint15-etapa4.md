## v1.84 — 2026-06-07 (Sprint 15 — Etapa 4: Serviço de Funcionários)

### Tipo da mudança
feat

### Impacto técnico/funcional

**15.4 — Backend: Serviço de Funcionários (CONCLUÍDA)**

✅ Backend:
- app/services/employee_service.py: funções para CRUD de funcionários
- register_employee: detecta 1 rosto via face_recognition, extrai embedding, salva foto + embedding, cria Person+Employee
  - Validação: registration único (409), exatamente 1 rosto (422)
  - Storage: storage/employees/{uuid}.jpg + {uuid}_embedding.npy
- list_employees: com filtro active_only e paginação
- get_employee_by_id, get_employee_by_registration: lookup por ID ou matrícula
- update_employee: PATCH para name, department, role, notes, active
- deactivate_employee: soft delete (active=0)
- app/core/settings.py: STORAGE_EMPLOYEES: Path
- storage/employees/.gitkeep criado

✅ Testes (test_employee_service.py):
- 10 testes cobrindo: criação, duplicata (409), sem rosto (422), múltiplos rostos (422), list, get, update, deactivate

Métricas:
- Backend: 370 testes (+10 de 15.4)
- Frontend: 180 testes (sem mudanças)

Performance:
- register_employee: ~2s (extração embedding + I/O foto)
- list_employees: O(n) com paginação

Próxima etapa: 15.5 (Endpoints POST/GET/PATCH/DELETE /api/v1/employees)
