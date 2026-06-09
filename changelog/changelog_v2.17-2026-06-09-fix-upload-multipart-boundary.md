## v2.17 — 2026-06-09

### Tipo da mudança
fix

### Arquivos alterados
- frontend/src/pages/Upload.jsx
- frontend/src/test/Upload.test.jsx

### Impacto técnico/funcional

**fix(upload): corrige 400 Bad Request ao enviar arquivos .dav (e todos os formatos)**

Causa raiz: `handleUpload` definia manualmente `headers: { 'Content-Type': 'multipart/form-data' }`
sem o parâmetro `boundary`. O browser/Axios gera o boundary automaticamente ao detectar
FormData, mas o header manual sobrescrevia esse valor — resultando em `Content-Type: multipart/form-data`
sem boundary. O python-multipart (usado pelo FastAPI/Starlette) exige o boundary para parsear o
corpo da requisição, retornando `400 Bad Request` antes mesmo de chegar na validação de extensão.

Correções aplicadas:
- Remove `headers: { 'Content-Type': 'multipart/form-data' }` do `api.post()` — Axios detecta
  FormData e injeta o boundary correto automaticamente.
- `setError(err.message)` → `setError(err.response?.data?.detail ?? err.message)` — agora exibe
  o detalhe do erro FastAPI na tela em vez da mensagem genérica do Axios.
- `reset()`: substituiu `setProgress(0)` (ReferenceError) por `resetProgress()` (fn correta do hook).

Testes adicionados (3 novos em `Upload.test.jsx`):
- Verifica que o Content-Type manual não está presente na chamada ao api.post
- Verifica que o detalhe do backend é exibido na tela em caso de erro
- Verifica que reset() não lança ReferenceError
