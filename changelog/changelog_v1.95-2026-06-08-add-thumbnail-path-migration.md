## v1.9.5 — 2026-06-08

### Tipo da mudança
fix

### Arquivos alterados
- app/main.py
- app/db/migrations/migration_v1_35.py
- tests/unit/test_migration_v1_35.py

### Impacto técnico/funcional
Corrige o erro de OperationalError (no such column: videos.thumbnail_path) ao tentar listar vídeos em bancos de dados existentes onde o campo `thumbnail_path` não havia sido criado. Adiciona a migração automatizada `migration_v1_35` para criar a coluna `thumbnail_path` na tabela `videos` caso esteja ausente, com testes de unidade correspondentes.
