## v1.66 — 2026-06-07

### Tipo da mudança
feat

### Arquivos alterados
- frontend/src/router.jsx
- frontend/src/components/Layout.jsx
- frontend/src/pages/VideosCatalog.jsx (novo)
- frontend/src/test/VideosCatalog.test.jsx (novo)

### Impacto técnico/funcional

**Frontend - Página de Catálogo de Vídeos:**

Nova rota `/videos` (protegida) que exibe catálogo completo de vídeos com:
- Grid de cards 16:9 com placeholder estilizado (ícone Film centralizado)
- Badge de status sobreposto (cores: Pendente=amarelo, Processando=azul, Concluído=verde, Erro=vermelho)
- Overlay ao hover com ícone Play centralizado + "Ver detalhes"
- Mini galeria de até 4 avatares das pessoas identificadas (com overlap)
- Badge "+N" quando mais de 4 pessoas
- Metadados: nome arquivo (truncado), data/hora, contagem de pessoas
- Ações inline: Download CSV, Reprocessar (se Concluído/Erro), Excluir

Controles interativos:
- Campo de busca com debounce 400ms (busca por nome de arquivo, case-insensitive)
- Dropdown de filtro de status (Todos/Pendente/Processando/Concluído/Erro)
- Dropdown de ordenação (Mais recente/Mais antigo/Nome A→Z/Nome Z→A/Mais pessoas)
- Toggle de layout: grid (3 colunas desktop/2 tablet/1 mobile) ↔ lista
- Toggle "Mostrar excluídos" (Eye icon) para include_deleted
- Layout preference persistido em localStorage (gw-videos-layout)

Paginação:
- Controle de página com botões ← Próximo e Anterior
- Máximo 7 números de página visíveis com reticências
- Display "Exibindo X-Y de Z vídeos"
- Botões desabilitados no limite (primeira/última página)

Estados:
- Loading: grid de 6 skeleton cards com animação
- Empty: ícone Film + "Nenhum vídeo encontrado" (com sugestões se há filtros ativos)
- Erro: capturado e logado no console

Sidebar:
- Item "Vídeos" com ícone Film adicionado entre Upload e Pessoas

TDD: 15 testes unitários incluindo busca/filtros/paginação/ações.
Total de testes no frontend: 158 passando.

### Próximo passo
12.3: Hook useVideoActions reutilizável (Dashboard + Catálogo).
