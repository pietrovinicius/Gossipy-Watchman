## v1.64 — 2026-06-07

### Tipo da mudança
feat

### Arquivos alterados
- frontend/src/pages/Dashboard.jsx
- frontend/src/pages/VideoDetail.jsx
- frontend/src/test/DashboardActions.test.jsx
- frontend/src/test/VideoDetailActions.test.jsx
- frontend/package.json

### Impacto técnico/funcional
Conclui a 11.7: filtros, exclusão, restauração e reprocessamento de
vídeos na UI. Em Dashboard: pills de filtro por status
(Todos/Pendente/Processando/Concluído/Erro com `?status=`), toggle
"Mostrar excluídos" (`include_deleted=true`), badge "Excluído" com
opacidade reduzida, e ícones por linha para excluir (ConfirmModal),
restaurar (POST /videos/{id}/restore) e reprocessar
(POST /videos/{id}/reprocess, somente para vídeos Concluído/Erro,
com ConfirmModal de aviso). Em VideoDetail: botões "Excluir vídeo"
(ConfirmModal com requireTyping="excluir"), "Reprocessar" e
"Restaurar vídeo", condicionados a status e deleted_at. 9 novos
testes (5 Dashboard + 4 VideoDetail). Suíte completa do frontend:
143/143. Suíte backend: 304/304.
