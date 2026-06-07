## v1.67 — 2026-06-07

### Tipo da mudança
refactor

### Arquivos alterados
- frontend/src/hooks/useVideoActions.js (novo)
- frontend/src/test/useVideoActions.test.js (novo)

### Impacto técnico/funcional

**Frontend - Hook reutilizável para ações de vídeo:**

Criado hook `useVideoActions({ onSuccess, onError })` que centraliza a lógica
de ações compartilhadas entre Dashboard e VideosCatalog:

Funções retornadas:
- `exportCsv(videoId, fileName)` — GET /export/timeline/video/{id}, download CSV
- `reprocess(videoId)` — POST /videos/{id}/reprocess
- `softDelete(videoId)` — DELETE /videos/{id}
- `restore(videoId)` — POST /videos/{id}/restore

Loading states:
- `loadingId` — ID do vídeo em carregamento (null quando ocioso)
- `loadingAction` — Tipo de ação ('export', 'reprocess', 'delete', 'restore')

Callbacks:
- `onSuccess(action, videoId)` — chamado após sucesso
- `onError(action, errorMessage)` — chamado após erro (extrai detail da resposta)

TDD: 10 testes unitários cobrindo sucesso/erro e loading states.
Total de testes frontend: 168 passando.

### Próximos passos
- Atualizar Dashboard e VideosCatalog para usar useVideoActions
- Integração de ações no Dashboard (refactor cleanup)
