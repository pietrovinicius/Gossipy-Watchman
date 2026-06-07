## v1.58 — 2026-06-07

### Tipo da mudança
feat

### Arquivos alterados
- app/db/migrations/migration_v1_30.py
- app/main.py
- app/models/person.py
- app/models/video.py
- app/schemas/person.py
- app/schemas/video.py
- tests/unit/test_migration_v1_30.py

### Impacto técnico/funcional
Migração idempotente migration_v1_30 adiciona coluna deleted_at
(TIMESTAMP NULL) nas tabelas people e videos via pragma_table_info,
registrada no lifespan após migration_v1_20 e antes de init_db().
Modelos Person e Video ganham campo deleted_at nullable; schemas
PersonResponse e VideoResponse expõem deleted_at: datetime | None.
Base para soft delete de pessoas e vídeos nos próximos passos da
Sprint 11. 5 novos testes cobrindo criação de coluna, idempotência
e mapeamento ORM. Suíte completa do backend: 268/268.
