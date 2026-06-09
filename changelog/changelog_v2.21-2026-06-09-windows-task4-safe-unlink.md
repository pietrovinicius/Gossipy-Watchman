## v2.21 — 2026-06-09

### Tipo da mudança
feat

### Arquivos alterados
- app/core/path_utils.py (novo)
- app/api/v1/upload.py
- app/services/conversion_service.py
- tests/unit/test_path_utils.py (novo)

### Impacto técnico/funcional
Task 4/6 de otimizações Windows: criada função `safe_unlink(path, missing_ok, retries, delay)` em `path_utils.py` que faz retry em `PermissionError` com backoff (padrão 3 tentativas, 200ms delay). Windows mantém file handles abertos após ffmpeg/OpenCV fechar arquivo — `Path.unlink()` puro lançava PermissionError. Aplicado em `upload.py` (limpeza pós-upload) e `conversion_service.py` (remoção de temporários pós-conversão).
