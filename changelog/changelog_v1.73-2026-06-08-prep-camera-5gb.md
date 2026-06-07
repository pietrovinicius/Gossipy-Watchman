## v1.73 — 2026-06-08

### Tipo da mudança
chore

### Arquivos alterados
- app/core/settings.py
- app/api/v1/upload.py
- .env + .env.example
- tests/unit/test_settings.py
- Anotacoes.txt

### Impacto técnico/funcional

**Prep para câmeras de segurança — suporte até 5GB**

Config changes:
- MAX_UPLOAD_SIZE_MB: 500 → 5120 (5GB para câmeras CFTV)
- FRAMES_PER_SECOND_SAMPLE: 1 → 2 (melhor precisão em pessoas rápidas)

Upload — novos formatos:
- Formatos agora: .mp4, .avi, .mkv, .mov, .ts
- Magic bytes validação adicionada:
  - .mp4: bytes[4:8] == 'ftyp'
  - .avi: RIFF + AVI magic
  - .mkv: Matroska signature
  - .mov: QuickTime ftyp
  - .ts: sync byte 0x47

Documentação Anotacoes.txt:
- Seção dedicada "Para vídeos de câmera de segurança"
- Comando uvicorn com timeout estendido
- Dicas de conversão ffmpeg para formatos não-nativos
- Tratamento de MemoryError em vídeos longos

Testes:
- test_settings.py: MAX_UPLOAD atualizado para 5120
- test_settings.py: FRAMES_PER_SECOND atualizado para 2
- Upload magic bytes funcionais (TDD passando)

Tradeoffs:
- 2 frames/s vs 1: ~2x tempo processamento (1h vídeo = ~2h proc com CNN)
- Recomendação: extrair trechos 15-20min para vídeos muito longos

Próximos passos:
- Testar upload real de câmera CFTV
- Calibrar detecção com vídeos reais antes batch processing
