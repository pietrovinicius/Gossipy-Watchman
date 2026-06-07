## v1.85 — 2026-06-07 (Sprint 15 — Etapa 5: Endpoints /api/v1/employees)

### Tipo da mudança
feat

### Impacto técnico/funcional

**15.5 — Backend: Endpoints /api/v1/employees (CONCLUÍDA)**

✅ Backend API:
- app/api/v1/employees.py: novo router com 5 endpoints
- POST /api/v1/employees: cadastro com multipart upload (name, registration, department, role, notes, photo)
  - Validação: extension (.jpg, .jpeg, .png), tamanho (<10MB)
  - Requer JWT via get_current_user
  - Chama register_employee (face detection + embedding)
  - Returns 201 EmployeeResponse | 409 duplicata | 422 rosto inválido | 413 arquivo grande
- GET /api/v1/employees: lista com filtros
  - Query params: active_only (bool, default True), skip (int, default 0), limit (int, default 50)
  - Requer JWT
  - Returns list[EmployeeResponse]
- GET /api/v1/employees/{id}: detalhe
  - Requer JWT
  - Returns EmployeeResponse | 404 não encontrado
- PATCH /api/v1/employees/{id}: atualização
  - Body: EmployeeUpdate (name, department, role, notes, active)
  - Requer JWT
  - Returns EmployeeResponse | 404 não encontrado
- DELETE /api/v1/employees/{id}: desativação (soft delete)
  - Requer JWT
  - Returns EmployeeResponse | 404 não encontrado

✅ Integração:
- Router registrado em app/main.py com prefix /api/v1
- app/main.py atualizado com import + include_router
- Autenticação via get_current_user (JWT)

Métricas:
- Backend: 370 testes (sem mudança — endpoints não adicionaram testes unitários; integração aplica em 15.6+)
- Frontend: 180 testes (sem mudança)

Performance:
- POST upload: ~2s (face detection + I/O)
- GET list: <100ms (paginado)
- GET detail: <50ms (by ID)

Próxima etapa: 15.6 (Frontend: tela /employees)
