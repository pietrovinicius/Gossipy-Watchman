## v2.21 — 2026-06-09

### Tipo da mudança
feat

### Arquivos alterados
- app/workers/video_worker.py
- tests/unit/test_video_worker_windows.py (novo)

### Impacto técnico/funcional
Task 5/6 de otimizações Windows: `video_worker.py` recebeu duas melhorias de memória:
1. `threading.Semaphore(1)` (`_PROCESSING_SEMAPHORE`) via `process_video` → previne processamento concorrente que causaria spike de RAM (ONNX buffalo_l ~1–2GB por instância).
2. `gc.collect()` no bloco `finally` de `_process_video_inner` → força liberação de objetos ONNX após cada vídeo, evitando acúmulo silencioso de memória em sessões longas.
Lógica interna extraída para `_process_video_inner` para facilitar testes e separação de responsabilidades.
