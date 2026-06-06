## v1.23 — 2026-06-06

### Tipo da mudança
feat

### Arquivos alterados
- frontend/src/utils/downloadCsv.js (novo)
- frontend/src/test/downloadCsv.test.js (novo — 3 testes TDD)
- frontend/src/pages/PersonDetail.jsx (+ botão "Exportar CSV" com loading)
- frontend/src/pages/Dashboard.jsx (+ coluna "Exportar" por linha de vídeo)

### Impacto técnico/funcional
Sprint 7.3: Botões de export CSV no frontend.
- downloadCsv(blob, filename): URL.createObjectURL → <a> hidden → click → revokeObjectURL
- PersonDetail: botão "Exportar CSV" com Loader2 durante download, chama GET /export/timeline/person/{id}
- Dashboard: coluna "Exportar" na tabela, loading por linha (exportingId), chama GET /export/timeline/video/{id}
- Total frontend: 34 testes passando
