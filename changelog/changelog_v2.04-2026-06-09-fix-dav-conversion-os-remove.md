## v2.04 — 2026-06-09

### Tipo da mudança
fix

### Arquivos alterados
- app/api/v1/upload.py
- app/services/conversion_service.py
- tests/unit/test_conversion_service.py
- tests/integration/test_upload_security.py

### Impacto técnico/funcional

**fix(upload): os.remove() com missing_ok causava TypeError → HTTP 500**
- `os.remove(dest_path, missing_ok=True)` no handler de erro de conversão não é uma
  assinatura válida de `os.remove` — lançava TypeError mascarando o erro real (422).
- Corrigido: `dest_path.unlink(missing_ok=True)` (método Path, aceita missing_ok).
- Idem no caminho feliz: `os.remove(dest_path)` → `dest_path.unlink(missing_ok=True)`.
- `import os` removido (sem mais usos).

**fix(upload): arquivo convertido parcial não era limpo em falha de conversão**
- Quando ffmpeg falhava (ex.: disco cheio), o arquivo `*_converted.mp4` parcial
  permanecia em `storage/videos/` ocupando espaço.
- Corrigido: `converted_partial.unlink(missing_ok=True)` no bloco except.

**fix(conversion_service): .dav sem -avoid_negative_ts causava Non-monotonic DTS**
- Arquivos Dahua (.dav / dhav) têm timestamps descontínuos entre sessões de gravação.
- Adicionado `_FORMAT_EXTRA_ARGS = {".dav": ["-avoid_negative_ts", "make_zero"]}`.
- `convert_to_mp4` injeta os args extras antes dos flags de codec quando o suffix
  tem entrada no dict. Outros formatos não são afetados.
