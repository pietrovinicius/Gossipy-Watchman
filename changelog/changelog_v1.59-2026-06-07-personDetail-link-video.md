## v1.59 — 2026-06-07

### Tipo da mudança
feat

### Arquivos alterados
- frontend/src/pages/PersonDetail.jsx
- frontend/src/test/PersonDetail.test.jsx
- frontend/package.json

### Impacto técnico/funcional
Na timeline de aparições da página PersonDetail, a coluna "Vídeo"
(antes texto estático com file_name) torna-se um botão clicável
estilizado como link (cor primária, ícone ExternalLink, hover:underline,
cursor-pointer, tooltip "Ver detalhes do vídeo") que navega para
/videos/{video_id} via useNavigate, completando a navegação cruzada
entre perfil de pessoa e detalhe do vídeo. 2 novos testes cobrindo
clicabilidade do link e navegação para a rota correta com o video_id
esperado. Suíte completa do frontend: 114/114.
