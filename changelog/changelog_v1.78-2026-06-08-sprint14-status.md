## v1.78 — 2026-06-08 (Sprint 14 Status)

### Tipo da mudança
chore

### Impacto técnico/funcional

**SPRINT 14 — STATUS 3/4 COMPLETA**

✅ Concluído:
- 14.1: ffmpeg_check.py + /health/ffmpeg endpoint (6 tests)
- 14.2: conversion_service.py (11 tests + needs_conversion + convert_to_mp4 + duration)
- 14.3: upload.py integration (conversão automática .ts/.mkv/.mov → .mp4)
- 14.4: CNN adaptativo worker (5 tests + get_adaptive_params)

🚧 Em progresso:
- 14.5: useUploadProgress hook + formatBytes utils (scaffold)
  - Faltam: integração no Upload.jsx + 12 testes JS + Upload.jsx UI update

⏳ Pendente:
- 14.6: Verificação final + changelog encerramento

Métricas:
- Backend testes: 354 passando (7 de 14.1-14.4)
- Frontend testes: 175+ (sem testes 14.5 ainda)
- Commits: 7 (ETAPA PRÉVIA + 14.1 + 14.2 + 14.3 + 14.4 + 14.5-scaffold)

Decisões:
- Conversão .ts/.mkv/.mov automática no upload com delete de original
- CNN parameters auto-adjust: <10min preciso, <60min equilibrado, >60min eficiente
- Timer ETA em segundos com formatação min/s ou h/m

Próximo turno:
- 14.5: Integrar useUploadProgress no Upload.jsx
- 14.5: Criar 12 testes JS (useUploadProgress + formatBytes)
- 14.6: Verificação final, changelog encerramento, commit final

Sprint 14 será entregue com ~360+ testes backend + frontend.
