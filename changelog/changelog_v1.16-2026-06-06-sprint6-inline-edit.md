## v1.16 — 2026-06-06

### Tipo da mudança
feat

### Arquivos alterados
- frontend/src/components/InlineEdit.jsx (novo)
- frontend/src/components/InlineEdit.test.jsx (novo — 6 testes TDD)
- frontend/src/pages/People.jsx (PersonCard usa InlineEdit; handleRename via PATCH)

### Impacto técnico/funcional
Sprint 6.3: Componente InlineEdit reutilizável para edição inline de texto.
- Clique → modo edição (input focado)
- Enter → salva via onSave callback
- Escape / blur sem mudança → cancela
- Valor vazio → não chama onSave
- Na galeria de Pessoas: clicar no nome abre InlineEdit; salvar chama PATCH /people/{id}
- Avatar e chevron continuam navegando para PersonDetail
- Total frontend: 20 testes passando
