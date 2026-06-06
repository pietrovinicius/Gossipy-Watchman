## v1.0.0 — 2026-06-06

### Tipo da mudança
docs + chore

### Arquivos alterados
- CHANGELOG.md (consolidado a partir dos fragmentos v0.01–v0.28)
- README.md (criado do zero)
- app/core/settings.py (+ APP_VERSION = "1.0.0")
- app/api/v1/health.py (expõe version no response)
- frontend/package.json (version bump 0.0.0 → 1.0.0)

### Impacto técnico/funcional
Release v1.0.0 — MVP completo. CHANGELOG.md consolidado no formato Keep a Changelog.
README.md com business case, stack, instruções de execução, endpoints, decisões
arquiteturais e próximos passos. Versão 1.0.0 refletida em backend (settings + health)
e frontend (package.json). Total: 95 testes passando, 9 endpoints, 8 serviços, 5 páginas React.
