## v1.17 — 2026-06-06

### Tipo da mudança
feat

### Arquivos alterados
- frontend/src/components/CategoryBadge.jsx (novo)
- frontend/src/components/PersonCard.test.jsx (novo — 5 testes TDD)
- frontend/src/pages/People.jsx (+ CategoryBadge no card da galeria)
- frontend/src/pages/PersonDetail.jsx (+ stats 4-grid, + edição de notes/category)

### Impacto técnico/funcional
Sprint 6.4: Badge de categoria e painel de stats na tela de detalhes.
- CategoryBadge: cor distinta por categoria (Funcionário=azul, Visitante=roxo, Monitorado=vermelho)
- Galeria: badge visível embaixo do nome em cada card
- PersonDetail: painel 4-grid com video_count, total_seconds, first_seen, last_seen (GET /stats)
- PersonDetail: botão de edição para notes (textarea) e category (select) com PATCH
- Total frontend: 25 testes passando
