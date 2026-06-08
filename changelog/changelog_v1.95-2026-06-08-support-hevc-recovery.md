## v1.95 — 2026-06-08

### Tipo da mudança
feat

### Arquivos alterados
- app/services/conversion_service.py
- tests/unit/test_conversion_service.py

### Impacto técnico/funcional
- Adicionada detecção automática do codec de vídeo (HEVC/H.265 ou H.264) nas primeiras NAL units contidas na box `mdat` quando o `moov` atom não é encontrado no início do arquivo.
- Modificado o fallback de reparo do stream bruto no `ffmpeg` para passar dinamicamente o parâmetro `-f hevc` ou `-f h264` conforme o codec detectado. Isso corrige o erro de broken pipe e impossibilidade de leitura de vídeos HEVC sem moov vindos de câmeras de segurança.
