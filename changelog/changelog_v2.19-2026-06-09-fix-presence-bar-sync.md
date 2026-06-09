## v2.19 — 2026-06-09

### Tipo da mudança
fix

### Arquivos alterados
- frontend/src/components/VideoPlayer.jsx
- frontend/src/pages/VideoDetail.jsx
- frontend/src/test/VideoPlayer.test.jsx

### Impacto técnico/funcional

**fix(videoplayer): sincronização barra de presença ↔ cards de pessoa**

Causa raiz: segmentos de categoria "Desconhecido" usavam cor `#6B7280` (gray-500)
indistinguível do fundo cinza da barra (`bg-slate-200`). Ao clicar no que parecia ser
o fundo cinza, o usuário acertava um segmento Desconhecido adjacente em outro timestamp,
causando dessincronia entre o tempo do player e o card scrollado.

Correções:
1. **Cor de Desconhecido**: `#6B7280` → `#334155` (slate-800) — alto contraste em
   fundo claro e escuro, segmentos agora visíveis na barra.

2. **Background click handler na barra**: `onClick` adicionado ao `div` da barra com
   guarda `e.target !== e.currentTarget`. Clicar em qualquer ponto cinza da barra faz
   seek proporcional à posição do clique (`clientX / width * duration`) e chama
   `onSegmentSeek(null, time)`. Não interfere nos cliques em segmentos (não há
   duplo disparo por conta do guarda de target).

3. **`handleSegmentSeek` inteligente em VideoDetail**: ao receber `person_id=null`
   (clique no fundo) ou `person_id` de um segmento, usa `getPeopleOnScreen(ts, people)`
   para determinar o card correto a scrollar. Preferência: pessoa do segmento clicado
   se visível em `ts`; senão, primeira pessoa visível em `ts`; senão, fallback para
   `person_id`.

Resultado: player e card de pessoa ficam sincronizados independente de onde o usuário
clicar na barra.
