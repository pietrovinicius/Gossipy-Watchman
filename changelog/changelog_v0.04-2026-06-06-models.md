## v0.04 — 2026-06-06

### Tipo da mudança
feat

### Arquivos alterados
- app/models/base.py
- app/models/person.py
- app/models/video.py
- app/models/appearance.py
- app/models/__init__.py
- tests/unit/test_models.py

### Impacto técnico/funcional
Cria os três modelos SQLAlchemy (Person, Video, Appearance) conforme schema do CLAUDE.md.
VideoStatus é um Enum Python com os quatro estados do ciclo de vida.
Appearance tem ForeignKeys para people.id e videos.id.
Base declarativa centralizada em app/models/base.py para uso pelo db/session.py.
TDD: 12 testes escritos antes da implementação, todos passando.
