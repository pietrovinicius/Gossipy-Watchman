## v1.86 — 2026-06-07 (Sprint 15 — Etapa 6: Tela /employees)

### Tipo da mudança
feat

### Impacto técnico/funcional

**15.6 — Frontend: Tela /employees (CONCLUÍDA)**

✅ Frontend:
- frontend/src/pages/Employees.jsx: tela principal de funcionários
  - Cabeçalho com título "Funcionários (X)", botão "Cadastrar Funcionário"
  - Toggle "Mostrar inativos" para filtro
  - Tabela com colunas: Foto (avatar 40x40), Nome, Matrícula, Setor, Cargo, Perfil (link), Status (badge), Ações
  - Ações: Edit (ícone), Delete/Desativar (ícone Trash2)
  - Estados: loading, erro, vazio, listagem
  - Integração com api.get('/employees?active_only=...')
  - ConfirmModal para desativação

- frontend/src/router.jsx:
  - Adicionado lazy load: Employees
  - Rota: { path: '/employees', element: <Protected><Employees /></Protected> }

- frontend/src/components/Layout.jsx:
  - Adicionado ícone BadgeCheck do lucide-react
  - Adicionado navItem: { to: '/employees', label: 'Funcionários', icon: BadgeCheck }
  - Posicionado entre Pessoas e Alertas

Métricas:
- Frontend: 180 testes (sem mudança — nova página não requer testes de integração agora)

Próxima etapa: 15.7 (Verificação final + encerramento Sprint 15)
