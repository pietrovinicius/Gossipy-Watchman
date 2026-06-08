## v1.8.8 — 2026-06-07

### Corrigido

**PersonDetail.jsx:**
- Exclusão de pessoa agora navega para `/people` após sucesso (antes permanecia na página)
- `handleDeletePerson()` + `navigate('/people')` após `api.delete()` bem-sucedido

**Testes:**
- Novo teste em PersonDetailActions.test.jsx valida navegação pós-delete

**Impacto:**
- /people/{id}: Clicar "Excluir perfil" → confirmar → retorna para lista de pessoas automaticamente
- Usuário já não fica preso em tela vazia após deletar pessoa

**Testes:** 6 testes passam (0 regressões).
