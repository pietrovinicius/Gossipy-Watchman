## v1.19 — 2026-06-06

### Tipo da mudança
chore

### Arquivos alterados
- (nenhum arquivo de código — verificação apenas)

### Impacto técnico/funcional
Sprint 6.6: Verificação final da Sprint 6 — Gestão de Pessoas.

Resultados:
- pytest: 159 testes passando (era 125 no início da sprint)
- vitest: 31 testes passando (6 arquivos)
- npm run build: limpo, sem erros
- SQLite PRAGMA table_info(people): colunas notes e category presentes com defaults corretos

Sprint 6 entregue: migração de banco, 3 endpoints novos/ampliados (update_person_details,
get_person_stats, merge_people), InlineEdit, CategoryBadge, MergeActionBar, stats em PersonDetail,
edição de notes/category, merge de perfis com multi-select.
