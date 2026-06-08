## v1.8.7 — 2026-06-07

### Corrigido

**Upload.jsx**: Referência não definida em `selectFile()`.

- Linha 31: `setProgress(0)` → `resetProgress()`
- `setProgress` não existe (hook retorna `reset`, não setter direto)
- Bug impedia seleção de arquivo — clique em drop zone não funcionava

**Impacto:** Página /upload agora aceita seleção de vídeos novamente.

**Testes:** Todos 183 testes continuam passando.
