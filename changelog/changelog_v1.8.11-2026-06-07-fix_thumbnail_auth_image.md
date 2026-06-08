## v1.8.11 — 2026-06-07

### Tipo da mudança
fix

### Arquivos alterados
- frontend/src/hooks/useAuthVideoThumbnail.js
- frontend/src/pages/VideosCatalog.jsx
- frontend/src/test/useAuthVideoThumbnail.test.jsx

### Impacto técnico/funcional
A thumbnail aparecia como imagem quebrada porque `<img src=".../thumbnail">` não envia o header `Authorization`, e o endpoint `/videos/{id}/thumbnail` exige JWT (`get_current_user`). Criado o hook `useAuthVideoThumbnail`, que busca a imagem via `api.get` (com interceptor de auth) como blob e gera uma object URL — mesmo padrão já usado por `useAuthImage` para fotos de pessoas. `VideosCatalog.jsx` agora consome esse hook em vez de montar a URL diretamente.
