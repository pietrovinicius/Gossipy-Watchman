## v1.74 — 2026-06-08

### Tipo da mudança
feat

### Arquivos alterados
- app/core/ffmpeg_check.py (novo)
- app/core/settings.py
- app/api/v1/health.py
- tests/unit/test_ffmpeg_check.py (novo)
- .env + .env.example

### Impacto técnico/funcional

**14.1 — ffmpeg Detecção e Health Check**

Nova função check_ffmpeg():
- Detecta disponibilidade de ffmpeg no PATH
- Timeout 10s para evitar hangs
- Log com versão detectada
- Fallback para disabled se não encontrado

get_ffmpeg_status() retorna:
- available (bool)
- path (str da config)
- message (status legível)

Endpoint público GET /api/v1/health/ffmpeg:
- Sem JWT (diagnóstico)
- Retorna status dict
- Útil para verificar se conversão está disponível

TDD: 6 testes de unidade (mocked subprocess):
- check_ffmpeg True quando disponível
- check_ffmpeg False quando FileNotFoundError
- check_ffmpeg False quando TimeoutExpired
- check_ffmpeg False quando returncode != 0
- get_ffmpeg_status dict com available=True
- get_ffmpeg_status dict com available=False

Testes totais: 338 passando (+6)

Próximo: 14.2 conversion_service.py com conversão .ts/.mkv/.mov → .mp4
