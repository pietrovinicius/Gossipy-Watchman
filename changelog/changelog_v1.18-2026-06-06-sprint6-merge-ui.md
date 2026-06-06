## v1.18 — 2026-06-06

### Tipo da mudança
feat

### Arquivos alterados
- frontend/src/components/MergeActionBar.jsx (novo)
- frontend/src/components/PeopleMerge.test.jsx (novo — 6 testes TDD)
- frontend/src/pages/People.jsx (modo mescla com multi-select, definição de perfil principal e POST /merge)

### Impacto técnico/funcional
Sprint 6.5: UI de merge de perfis duplicados.
- Botão "Mesclar perfis" ativa modo multi-seleção na galeria
- Cards selecionados destacados com ring/border primary
- MergeActionBar flutuante: contagem, botão "Definir principal", "Mesclar", "Cancelar"
- Merge desabilitado até primary definido e ≥2 selecionados
- POST /people/merge → refetch da lista → cancel state
- Total frontend: 31 testes passando
