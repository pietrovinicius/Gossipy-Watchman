## v1.65 — 2026-06-07

### Tipo da mudança
feat

### Arquivos alterados
- app/services/video_service.py
- app/api/v1/videos.py
- app/schemas/video.py
- tests/unit/test_video_service.py
- tests/integration/test_videos.py

### Impacto técnico/funcional

**Backend - Catálogo com busca, filtros e paginação:**

Adicionada `search_videos()` em VideoService com suporte a:
- Busca case-insensitive por nome de arquivo (LIKE %query%)
- Filtro exato por status (Pendente/Processando/Concluído/Erro)
- Ordenação por: uploaded_at_desc (padrão), uploaded_at_asc, name_asc, name_desc, people_desc
- Paginação com OFFSET/LIMIT (page, page_size)
- Exclusão de deletados por padrão (include_deleted param)
- Contagem de pessoas distintas identificadas por vídeo (subquery COUNT)
- Mini galeria de até 4 pessoas com profile_image_path

Novo endpoint GET `/api/v1/videos/catalog`:
- Query params: q, status, sort_by, page, page_size, include_deleted
- Response: CatalogResponse com estrutura paginada
- Requer JWT (autenticado)

Schemas adicionados:
- PersonPreview: person_id, person_name, profile_image_path
- VideoCardResponse: estende VideoResponse com people_count e people_previews[]
- CatalogResponse: items[], total, page, page_size, total_pages, has_next, has_prev

TDD: 9 testes unitários + 6 testes de integração escritos antes da implementação.
Total de testes no projeto: 325 passando.

### Próximo passo
Frontend (12.2): página VideosCatalog com grid de cards, busca, filtros, paginação.
