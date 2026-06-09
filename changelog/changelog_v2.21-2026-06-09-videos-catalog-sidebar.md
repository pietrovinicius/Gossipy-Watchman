## v2.21 — 2026-06-09

### Tipo da mudança
feat

### Arquivos alterados
- frontend/src/components/Layout.jsx
- frontend/src/pages/VideosCatalog.jsx

### Impacto técnico/funcional
- **Layout.jsx**: reposicionou item "Vídeos" na sidebar — agora entre "Funcionários" e "Alertas" (era entre Upload e Pessoas).
- **VideosCatalog.jsx**: card completo é clicável (onClick no wrapper, não só na thumbnail); `stopPropagation` na div de ações impede navegação acidental ao clicar botões; refatorado para usar `useVideoActions` hook (exportCsv, reprocess, softDelete) eliminando lógica inline duplicada; adicionado `refreshKey` para forçar re-fetch após delete/reprocess/restore.
