## v1.75 — 2026-06-08

### Tipo da mudança
feat

### Arquivos alterados
- app/services/conversion_service.py (novo)
- tests/unit/test_conversion_service.py (novo)

### Impacto técnico/funcional

**14.2 — Serviço de Conversão de Vídeo**

conversion_service.py:

needs_conversion(path) → bool:
- True: .ts, .mkv, .mov
- False: .mp4, .avi (nativo)

convert_to_mp4(input_path, output_dir=None) → Path:
- Converte via ffmpeg -c copy (sem re-encode)
- Retorna path com sufixo _converted.mp4
- RuntimeError se ffmpeg indisponível
- CalledProcessError se ffmpeg falhar
- Timeout 1h para vídeos longos

get_video_duration_seconds(path) → float | None:
- ffprobe + json parse
- Retorna duração em segundos
- None se ffprobe indisponível ou falhar

TDD: 11 testes (mocked subprocess):
- needs_conversion para cada formato
- convert_to_mp4 com ffmpeg disponível/indisponível
- convert_to_mp4 error handling
- get_video_duration_seconds válido/erro/indisponível

Testes totais: 349 passando (+11)

Próximo: 14.3 integração no endpoint upload
