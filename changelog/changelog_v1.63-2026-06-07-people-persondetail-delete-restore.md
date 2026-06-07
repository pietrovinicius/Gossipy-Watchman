## v1.63 — 2026-06-07

### Tipo da mudança
feat

### Arquivos alterados
- frontend/src/pages/People.jsx
- frontend/src/pages/PersonDetail.jsx
- frontend/src/test/PeopleDelete.test.jsx
- frontend/src/test/PersonDetailActions.test.jsx
- frontend/src/test/PersonDetail.test.jsx
- frontend/package.json

### Impacto técnico/funcional
Adiciona exclusão (soft delete) e restauração de pessoas na UI.
Em People: ícone de excluir por card (com ConfirmModal de confirmação),
toggle "Exibir excluídos" (recarrega lista com include_deleted=true),
botão de restaurar e badge "Excluído" com opacidade reduzida nos cards
deletados. Em PersonDetail: botão "Excluir perfil" com ConfirmModal
exigindo digitar "excluir" (requireTyping), e botão "Restaurar nome"
(POST /people/{id}/reset-name), visível apenas quando o nome não
começa com "Desconhecido". 12 novos testes (7 People + 5 PersonDetail).
Suíte completa do frontend: 134/134.
