## v2.22.0 — 2026-06-10

### Tipo da mudança
chore (encerramento de sprint)

### Arquivos alterados
- (nenhum código novo — apenas verificação final)

### Impacto técnico/funcional
Encerramento do Sprint 17 (i18n EN/pt-BR via react-i18next).

**Resumo geral:**
- Páginas/componentes migrados: Layout, Login, Dashboard, VideoDetail, People,
  PersonDetail, Employees, Upload, VideosCatalog, Alerts, AnalyticsDashboard,
  ConfirmModal, MergeActionBar, PhotoModal, VideoPlayer (15 arquivos).
- Chaves de tradução: 392 em `en/translation.json` e 392 em `pt-BR/translation.json`
  (paridade total entre idiomas).
- Toggle de idioma na sidebar, persistência via `localStorage` (`gw-language`),
  fallback `en`.
- Datas formatadas conforme locale ativo (`formatDateTime(date, i18n.language)`):
  DD/MM/AAAA HH:mm em pt-BR, M/D/AAAA h:mm AM/PM em en.

**Bug crítico encontrado e corrigido:** i18next v26 não suporta mais o sufixo
legado `_plural` — a forma correta v4 é `_other`. Rename global aplicado via sed
em ambos os arquivos de tradução (`people.selectedCount_plural` → `_other`, etc.).
Sem essa correção, plurais não eram resolvidos corretamente.

**Strings remanescentes em português (intencional, não migradas):**
- Valores internos do backend usados como chaves de lookup (`Pendente`,
  `Processando`, `Concluído`, `Erro`, `Funcionário`, `Visitante`, `Monitorado`,
  `Desconhecido`, `Todos`) — mapeados para chaves i18n via `STATUS_BADGE`,
  `STATUS_FILTER_LABEL_KEY`, `getCategoryColor`, etc. Alterar esses valores
  quebraria a integração com a API.

**Verificação final:**
- `npm run build`: sucesso, 0 erros.
- Suite completa: PASS(236) FAIL(1) — falha pré-existente e não relacionada
  (`PersonFrames.test.jsx`, aguarda correção em outra task).
- Grep por strings PT hardcoded em `src/**/*.{js,jsx}` (excluindo testes e
  `i18n/locales`): nenhuma ocorrência fora das exceções documentadas acima.
