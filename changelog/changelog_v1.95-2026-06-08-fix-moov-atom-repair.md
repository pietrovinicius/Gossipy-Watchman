## v1.9.5 — 2026-06-08

### Tipo da mudança
fix

### Arquivos alterados
- app/services/conversion_service.py
- app/workers/video_worker.py
- tests/unit/test_conversion_service.py
- tests/integration/test_video_worker.py
- tests/unit/test_settings.py

### Impacto técnico/funcional
Implementa a funcionalidade de reparo automático de arquivos de vídeo MP4 sem o "moov atom" no início (comum em arquivos de câmera de segurança gravados de forma assíncrona ou interrompidos). O worker do vídeo passa a tentar reparar o arquivo com ffmpeg (faststart) caso o OpenCV não consiga abrir o stream original. Adiciona cobertura completa de testes unitários e de integração correspondentes.
