## v0.01 — 2026-06-06

### Tipo da mudança
chore

### Arquivos alterados
- app/__init__.py
- app/api/__init__.py
- app/core/__init__.py
- app/db/__init__.py
- app/models/__init__.py
- app/schemas/__init__.py
- app/services/__init__.py
- app/workers/__init__.py
- tests/__init__.py
- tests/unit/__init__.py
- tests/integration/__init__.py
- storage/videos/.gitkeep
- storage/faces/.gitkeep
- changelog/.gitkeep
- CHANGELOG.md

### Impacto técnico/funcional
Cria estrutura de diretórios canônica do projeto conforme CLAUDE.md seção 2.
Todos os subdiretórios de app/ e tests/ têm __init__.py para importabilidade.
Diretórios de storage e changelog têm .gitkeep para rastreamento pelo git.
