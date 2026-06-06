## v1.06 — 2026-06-06

### Tipo da mudança
feat (segurança)

### Arquivos alterados
- app/api/v1/upload.py (reescrito com 3 correções)
- tests/integration/test_upload_security.py (novo — 7 testes)
- tests/integration/test_upload.py (atualizado: magic bytes reais)

### Impacto técnico/funcional
Correção 1 (CRÍTICO): Path Traversal eliminado — nome do arquivo em disco é UUID4 puro.
  file_name original salvo apenas no banco para exibição.
Correção 2 (CRÍTICO): Magic bytes validados antes de qualquer escrita em disco.
  MP4: bytes[4:8]==b'ftyp'; AVI: bytes[0:4]==b'RIFF' e bytes[8:12]==b'AVI '. HTTP 415 em falha.
Correção 3 (CRÍTICO): Limite de tamanho via MAX_UPLOAD_SIZE_BYTES.
  Arquivo parcial deletado imediatamente ao exceder limite. HTTP 413.
TDD: 7 testes de segurança, 115 total.
