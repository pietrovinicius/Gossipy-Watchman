## v1.35 — 2026-06-06

### Tipo da mudança
feat

### Arquivos alterados
- frontend/src/hooks/useFaceSearch.js (novo)
- frontend/src/pages/People.jsx (+ painel de busca por face)
- frontend/src/test/useFaceSearch.test.jsx (novo — 7 testes TDD)

### Impacto técnico/funcional
Sprint 8.7: busca por similaridade facial no frontend.
- useFaceSearch: gerencia estado (results, loading, error, queryTimeMs), envia FormData via POST /search/by-face
- Rejeita search(null) sem chamar API; define error
- People.jsx: painel expansível "Buscar por face" com área drag-and-drop
- Upload via drag-and-drop ou click-to-select (input file hidden)
- Resultados listados com pessoa, % de confiança e link para perfil
- queryTimeMs exibido como metadado do custo da busca
- Painel fecha/reseta ao alternar botão
- 7/7 vitest passando; total frontend: 52 testes
