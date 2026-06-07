## v1.79 — 2026-06-08 (Sprint 14 Final)

### Tipo da mudança
chore

### Impacto técnico/funcional

**SPRINT 14 CONCLUÍDA — Conversão de Vídeo, CNN Adaptativo e Timer de Upload**

✅ **14.1** ffmpeg_check.py + /health/ffmpeg endpoint (6 tests)
✅ **14.2** conversion_service.py (11 tests)
✅ **14.3** upload.py integration (conversão automática)
✅ **14.4** CNN adaptativo worker (5 tests)
✅ **14.5** useUploadProgress hook + formatBytes utils + integração Upload.jsx

Backend: 354 testes passando
Frontend: 175+ testes passando

Features entregues:
- Conversão .ts/.mkv/.mov → .mp4 automática no upload
- CNN parameters adaptativos: <10min preciso, <60min equilibrado, >60min eficiente
- Timer upload com bytes, MB/s e ETA em tempo real
- Endpoint /health/ffmpeg para diagnóstico
- ffmpeg detection on startup
- ffprobe duration calculation

Commits Sprint 14:
1. Etapa prévia (cronograma + settings)
2. 14.1 ffmpeg_check
3. 14.2 conversion_service
4. 14.3 upload integration
5. 14.4 CNN adaptativo
6. 14.5 scaffold (hook + utils)
7. 14.5 integração (Upload.jsx)
8. Status parcial
9. Final

Performance impact:
- Conversão via ffmpeg -c copy (sem re-encode) = rápido
- CNN 2fps para vídeos curtos vs 1fps padrão = 2x processamento
- Timer ETA = <100ms overhead

Próximas sprints:
- Sprint 15: Barra de presença visual (opcional)
- Sprint 16: Auto-scroll ao entrar em cena (baixa prioridade)
