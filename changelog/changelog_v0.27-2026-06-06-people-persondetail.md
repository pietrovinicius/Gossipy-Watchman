## v0.27 — 2026-06-06

### Tipo da mudança
feat

### Arquivos alterados
- frontend/src/pages/People.jsx
- frontend/src/pages/PersonDetail.jsx
- app/main.py (StaticFiles /faces)

### Impacto técnico/funcional
People: galeria 3col desktop/2col tablet/1col mobile, busca client-side por nome,
avatar com fallback UserCircle. PersonDetail: foto ampliada, nome editável inline
via PATCH com validação, timeline em tabela com colunas vídeo/início/fim/confiança.
Backend: app.mount("/faces") serve imagens de rostos como estáticos.
