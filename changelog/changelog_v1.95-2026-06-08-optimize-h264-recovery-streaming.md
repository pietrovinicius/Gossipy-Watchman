## v1.9.5 — 2026-06-08

### Tipo da mudança
refactor

### Arquivos alterados
- app/services/conversion_service.py
- tests/unit/test_conversion_service.py

### Impacto técnico/funcional
Otimiza a rotina de recuperação por fallback de vídeos MP4 sem o "moov atom". Em vez de extrair e gravar um arquivo temporário intermediário `.h264` em disco (o que causava falhas do tipo 'No space left on device' para arquivos grandes de 1.4 GB+), a rotina passa a processar e transmitir a stream raw H.264 (Annex B) diretamente para a entrada padrão (`stdin`) do processo `ffmpeg` via streaming de pipe (`subprocess.Popen`).
