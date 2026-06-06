## v1.32 — 2026-06-06

### Tipo da mudança
feat

### Arquivos alterados
- app/services/search_service.py (novo)
- app/schemas/search.py (novo)
- app/api/v1/search.py (novo)
- app/main.py (+ search_router)
- tests/unit/test_search_service.py (novo — 6 testes TDD)
- tests/integration/test_search.py (novo — 4 testes TDD)

### Impacto técnico/funcional
Sprint 8.4: busca por similaridade facial.
- POST /api/v1/search/by-face: multipart JPEG/PNG, max 10 MB, auth obrigatório
- search_by_face() carrega todos os embeddings .npy do disco via get_all_embeddings() a cada requisição (custo propositalmente visível via query_time_ms no response — ponto técnico para evolução futura com cache em memória)
- Múltiplas faces na imagem: usa a de maior área (best_idx via _area())
- Filtragem por tolerance + ordenação ASC por distância + top_k limitante
- confidence_pct = int((1 - distance) * 100)
- Mocks incluem cv2.imdecode e cv2.cvtColor para isolar testes do filesystem
- 10/10 testes TDD passando; total: 213 pytest
