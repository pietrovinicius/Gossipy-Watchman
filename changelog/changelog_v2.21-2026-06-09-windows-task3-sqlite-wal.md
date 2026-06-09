## v2.21 — 2026-06-09

### Tipo da mudança
feat

### Arquivos alterados
- app/db/session.py
- tests/unit/test_db_session.py

### Impacto técnico/funcional
Task 3/6 de otimizações Windows: SQLite agora opera em WAL (Write-Ahead Logging) mode + `synchronous=NORMAL`. WAL permite leituras concorrentes sem bloquear escritas — crítico no Windows onde file locking é mais agressivo. `synchronous=NORMAL` reduz fsync calls mantendo durabilidade adequada. Implementado via `event.listen` no engine singleton (`_set_sqlite_pragma`).
