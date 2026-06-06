## v0.13 — 2026-06-06

### Tipo da mudança
feat

### Arquivos alterados
- app/services/appearance_service.py
- tests/unit/test_appearance_service.py

### Impacto técnico/funcional
Implementa upsert_appearance() com lógica de gap de 2s para decidir entre estender
ou criar nova aparição. Decisão arquitetural: a condição de gap para timestamp_end=None
usa timestamp_start (não None genérico) para evitar match incorreto de aparições
antigas sem timestamp_end definido. Confidence atualizada somente se o novo valor for
menor (distância euclidiana menor = match mais confiante).
TDD: 5 testes com banco em memória, todos passando.
