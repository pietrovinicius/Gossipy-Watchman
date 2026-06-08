## v1.96.0 — 2026-06-08

### Tipo da mudança
feat

### Arquivos alterados
- app/core/settings.py
- app/services/frame_service.py
- app/workers/video_worker.py
- tests/unit/test_frame_service.py
- tests/integration/test_video_worker.py

### Impacto técnico/funcional
Implementa a funcionalidade de Motion Gating (filtragem por detecção de movimento) clássica e levíssima no pipeline de processamento do worker de vídeo. Frames estáticos ou sem movimento significativo agora são pulados antes de acionar o pipeline neural de detecção e alinhamento facial, reduzindo drasticamente o consumo de CPU. O primeiro frame do vídeo é sempre processado para garantir captura inicial de qualquer pessoa. Adicionados testes unitários e de integração correspondentes.
