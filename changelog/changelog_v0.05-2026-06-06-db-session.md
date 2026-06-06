## v0.05 — 2026-06-06

### Tipo da mudança
feat

### Arquivos alterados
- app/db/session.py
- app/db/init_db.py
- app/db/__init__.py
- tests/integration/test_db.py

### Impacto técnico/funcional
Cria app/db/session.py com engine SQLAlchemy e get_db() injetável via FastAPI Depends().
get_db() aceita parâmetro engine opcional para facilitar testes com banco em memória.
init_db() cria todas as tabelas via Base.metadata.create_all().
TDD: 5 testes de integração escritos antes da implementação, todos passando.
