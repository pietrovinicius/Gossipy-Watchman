## v2.21 — 2026-06-09

### Tipo da mudança
feat

### Arquivos alterados
- app/core/settings.py
- app/services/face_service.py
- tests/unit/test_face_service.py

### Impacto técnico/funcional
Task 7/7 de otimizações Windows: adicionado `INSIGHTFACE_INTRA_OP_NUM_THREADS=4` (configurável via .env). `get_face_app()` agora seta `OMP_NUM_THREADS` antes de inicializar o FaceAnalysis. ONNX Runtime por default usa todos os cores disponíveis — em máquinas Windows com 16GB RAM isso causa spike de uso de memória simultâneo. Limitar a 4 threads reduz pressão de memória sem impacto perceptível no throughput de processamento de vídeo (buffalo_l é IO-bound no carregamento, não CPU-bound na inferência com 1fps de amostragem).
