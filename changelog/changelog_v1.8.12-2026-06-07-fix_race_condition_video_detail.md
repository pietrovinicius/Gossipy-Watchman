## v1.8.12 — 2026-06-07

### Tipo da mudança
fix

### Arquivos alterados
- frontend/src/pages/VideoDetail.jsx
- frontend/src/test/VideoDetailRaceCondition.test.jsx

### Impacto técnico/funcional
Bug de "vídeo X exibe pessoas reconhecidas no vídeo Y": ao navegar rapidamente
entre páginas de detalhe de vídeo, `fetchDetail` é recriado a cada troca de `id`
(closure captura o `id` antigo). Se a requisição do vídeo anterior resolvesse
*depois* da requisição do vídeo atual, seu guard comparava a resposta contra o
próprio `id` capturado (sempre igual) e sobrescrevia `detail` com dados do
vídeo errado.

Corrigido comparando a resposta contra `idRef.current` — uma ref sempre
atualizada com o `id` mais recente da página — descartando qualquer resposta
cuja requisição não corresponda mais ao vídeo exibido. Removidos também os
`console.log`/`console.error` de debug deixados durante a investigação
(proibidos em código de produção pelo CLAUDE.md).

Teste `VideoDetailRaceCondition.test.jsx` reproduz o cenário (resposta atrasada
do vídeo anterior chegando após a navegação) — falha sem o guard correto (RED)
e passa com `idRef` (GREEN).
