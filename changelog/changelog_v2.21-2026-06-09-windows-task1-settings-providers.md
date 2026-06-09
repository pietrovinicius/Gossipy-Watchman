## v2.21 — 2026-06-09

### Tipo da mudança
feat

### Arquivos alterados
- app/core/settings.py
- tests/unit/test_settings.py

### Impacto técnico/funcional
Task 1/6 de otimizações Windows: adicionada configuração `INSIGHTFACE_PROVIDERS` com default `["CPUExecutionProvider"]` (remove dependência de CoreML inexistente no Windows) e ajustado default de `INSIGHTFACE_DET_SIZE` para 640 no código-fonte (economia ~30% RAM por frame). Dois novos testes RED→GREEN adicionados para verificar ambos os defaults de código sem .env.
