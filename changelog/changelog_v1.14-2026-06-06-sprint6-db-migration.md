## v1.14 — 2026-06-06

### Tipo da mudança
feat

### Arquivos alterados
- app/models/person.py (+ PersonCategory enum, notes, category)
- app/schemas/person.py (+ PersonCategory, notes, category em PersonResponse e PersonUpdate)
- app/db/migrations/migration_v1_13.py (novo)
- app/db/migrations/__init__.py (novo)
- app/main.py (+ migration_v1_13 no lifespan antes do init_db)
- tests/unit/test_models.py (+ 7 testes Sprint 6)
- tests/unit/test_schemas.py (+ 6 testes Sprint 6)
- tests/unit/test_migration_v1_13.py (novo — 4 testes)

### Impacto técnico/funcional
Sprint 6.1: Migração de banco adicionando colunas notes (TEXT NULL) e category
(VARCHAR(20) NOT NULL DEFAULT 'Desconhecido') à tabela people. PersonCategory enum
com 4 valores: Funcionário, Visitante, Desconhecido, Monitorado. Migration idempotente
via pragma_table_info. Validator em PersonResponse garante retrocompatibilidade com
objetos ORM sem category (None → 'Desconhecido'). Total: 142 testes passando.
