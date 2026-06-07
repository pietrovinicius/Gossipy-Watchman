## v1.57 — 2026-06-07

### Tipo da mudança
feat

### Arquivos alterados
- frontend/src/pages/VideoDetail.jsx
- frontend/src/router.jsx
- frontend/src/test/VideoDetail.test.jsx
- frontend/package.json

### Impacto técnico/funcional
Cria página /videos/:id consumindo GET /videos/{id}/detail: cabeçalho com
nome sanitizado, badge de status, data de upload e exportação CSV;
4 cards de resumo (pessoas identificadas, total de aparições, tempo
coberto formatado mm:ss, status); seção "Pessoas neste vídeo" com cards
detalhados (foto via useAuthImage, categoria, contagem e janela de
presença) e timeline de aparições colapsável (>3 aparições exibe preview
+ botão "Ver todas"); link "Ver perfil completo" para /people/{id}.
Estados especiais: skeleton de carregamento, spinner com auto-refresh
a cada 10s enquanto Pendente/Processando, estado vazio com dica sobre
FACE_RECOGNITION_TOLERANCE, e tela de erro com "Tentar novamente".
11 novos testes cobrindo skeleton, cabeçalho, cards de resumo, estados
vazio/processando, card de pessoa, foto, link de navegação, colapso e
expansão da timeline e exportação CSV. Suíte completa do frontend:
108/108.
