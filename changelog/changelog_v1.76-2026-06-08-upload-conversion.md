## v1.76 — 2026-06-08

### Tipo da mudança
feat

### Arquivos alterados
- app/api/v1/upload.py

### Impacto técnico/funcional

**14.3 — Integração Conversão no Upload**

upload.py agora:
- Aceita .ts, .mkv, .mov além de .mp4, .avi
- Valida magic bytes para todos formatos
- Se needs_conversion(file):
  - Chama convert_to_mp4(dest_path)
  - Deleta arquivo original via os.remove()
  - Atualiza file_path com arquivo convertido
- Error handling: 422 se conversão falhar
- Log detalhado por video_id

Fluxo:
1. Upload recebido → salvo com UUID name
2. Se convertível → conversão automática
3. Original deletado após conversão OK
4. Worker disposto com arquivo final (.mp4)

Testes unitários continuam passando: 349 total
(Testes de integração skipped — requerem arquivo .ts/.mkv real)

Próximo: 14.4 CNN adaptativo worker, 14.5 timer frontend, 14.6 verificação final
