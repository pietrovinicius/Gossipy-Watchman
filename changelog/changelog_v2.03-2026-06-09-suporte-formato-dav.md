## v2.03 — 2026-06-09

### Tipo da mudança
feat

### Arquivos alterados
- app/services/conversion_service.py
- app/api/v1/upload.py
- frontend/src/pages/Upload.jsx
- tests/unit/test_conversion_service.py
- tests/integration/test_upload_security.py

### Impacto técnico/funcional
Suporte ao formato `.dav` (Dahua Technology — câmeras CFTV proprietárias).

- `CONVERTIBLE_FORMATS` em `conversion_service.py` passa a incluir `.dav`.
  O arquivo é convertido para `.mp4` via `ffmpeg -c copy` no upload, igual a `.mkv`/`.mov`/`.ts`.
- `_ALLOWED_EXTENSIONS` em `upload.py` aceita `.dav`. Como o formato não possui magic bytes
  padronizados, a validação de conteúdo é pulada (comportamento existente para extensões sem
  entrada em `_MAGIC`).
- Frontend `Upload.jsx`: `.dav` adicionado à lista `ALLOWED`, ao atributo `accept` do input e
  às mensagens de texto da interface.
- 3 novos testes RED→GREEN: `test_needs_conversion_true_for_dav`,
  `test_native_formats_does_not_include_dav`, `test_valid_dav_returns_202`.
