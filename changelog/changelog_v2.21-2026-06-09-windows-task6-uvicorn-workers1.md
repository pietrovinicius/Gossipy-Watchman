## v2.21 — 2026-06-09

### Tipo da mudança
docs

### Arquivos alterados
- CLAUDE.md

### Impacto técnico/funcional
Task 6/6 de otimizações Windows: comando de startup do uvicorn atualizado para `--workers 1 --host 0.0.0.0`. Windows não suporta `fork` — múltiplos workers causam falha silenciosa na inicialização do ONNX Runtime. `--workers 1` é obrigatório. `--host 0.0.0.0` necessário para acesso via IP local em redes Windows (127.0.0.1 só aceita loopback).
