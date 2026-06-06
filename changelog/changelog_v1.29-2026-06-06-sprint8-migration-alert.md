## v1.29 — 2026-06-06

### Tipo da mudança
feat

### Arquivos alterados
- app/db/migrations/migration_v1_20.py (novo)
- app/models/alert.py (novo)
- app/models/__init__.py (+ Alert)
- app/schemas/alert.py (novo)
- app/main.py (+ migration_v1_20 no lifespan)
- tests/unit/test_migration_v1_20.py (novo — 4 testes TDD)

### Impacto técnico/funcional
Sprint 8.1: Migração de banco e modelo Alert.
- Tabela alerts: id, person_id (FK), video_id (FK), timestamp_in_video, message, seen, created_at
- Migração idempotente via sqlite_master; cria índice idx_alerts_seen
- Modelo SQLAlchemy Alert com todos os campos; exportado em models/__init__.py
- AlertResponse Pydantic com person_name e video_file_name (enriquecimento no endpoint)
- migration_v1_20() chamada no lifespan antes de init_db()
- 4/4 testes TDD passando; total: 190 pytest
