## v0.09 — 2026-06-06

### Tipo da mudança
feat

### Arquivos alterados
- app/schemas/video.py
- app/schemas/person.py
- app/schemas/__init__.py
- tests/unit/test_schemas.py

### Impacto técnico/funcional
Cria schemas Pydantic para Video (VideoCreate, VideoResponse, VideoStatusResponse)
e Person (PersonResponse) com from_attributes=True para serialização ORM.
TDD: 9 testes escritos antes da implementação, todos passando. Sprint 1 intacta (27 testes).
