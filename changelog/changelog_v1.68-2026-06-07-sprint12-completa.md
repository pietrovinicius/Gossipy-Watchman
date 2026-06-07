## v1.68 — 2026-06-07

### Tipo da mudança
chore

### Arquivos alterados
- Anotacoes.txt (seção Sprint 12 adicionada)

### Impacto técnico/funcional

**SPRINT 12 CONCLUÍDA — Catálogo de Vídeos**

Consolidação da Sprint 12 com implementação completa do catálogo de vídeos:

Backend (v1.65):
  - Endpoint GET /api/v1/videos/catalog com busca, filtros, ordenação
  - Suporte a people_desc (ordena por número de pessoas identificadas)
  - Schemas VideoCardResponse, PersonPreview, CatalogResponse
  - 15 testes (9 unitários + 6 integração)

Frontend (v1.66-v1.67):
  - Página VideosCatalog (/videos) com grid/lista toggle
  - Busca com debounce 400ms, filtros de status, ordenação
  - Mini galeria de pessoas (até 4) com overlap + "+N" badge
  - Ações inline: exportar CSV, reprocessar, excluir (com ConfirmModal)
  - Paginação com até 7 números de página visíveis
  - Hook useVideoActions para reutilização de ações
  - 25 testes (15 VideosCatalog + 10 useVideoActions)

Resultado:
  - Backend: 325 testes passando (0 falhas)
  - Frontend: 168 testes passando (0 falhas)
  - Build: 0 erros (npm run build OK)
  - Versionamento: bump de 1.6.4 para 1.6.4 (versão consolidada ao fim da sprint)

Tecnologias consolidadas:
  - Backend: FastAPI, SQLAlchemy, Pydantic, pytest
  - Frontend: React, React Router, Tailwind CSS, Vitest, React Testing Library

Próximos passos:
  - Integração de useVideoActions no Dashboard (refactor para reutilização)
  - Melhorias na UI/UX da página de catálogo (themes/animations)
  - Filtros avançados (data range, pessoas específicas)
