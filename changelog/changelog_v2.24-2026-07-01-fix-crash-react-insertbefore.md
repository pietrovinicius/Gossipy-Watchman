## v2.24 — 2026-07-01

### Tipo da mudança
fix

### Arquivos alterados
- frontend/index.html
- frontend/src/router.jsx
- frontend/src/components/RouteError.jsx
- frontend/src/i18n/locales/en/translation.json
- frontend/src/i18n/locales/pt-BR/translation.json
- frontend/src/test/RouteError.test.jsx

### Impacto técnico/funcional
Corrige crash total do app ("insertBefore" NotFoundError no react-dom)
relatado por um usuário em outra máquina da rede ao subir um vídeo. O
stack trace bate com o bug conhecido de recursos de tradução automática
do navegador (Google Tradutor/extensões) mutando o DOM gerenciado pelo
React fora do ciclo de reconciliação — quando o React tenta reposicionar
nós (ex.: durante updates frequentes da barra de progresso do upload),
encontra a árvore alterada externamente e lança NotFoundError.

Mitigação: `div#root` marcada com `translate="no"` e classe `notranslate`
em `index.html`, instruindo o navegador a não tocar no subtree do React.

Resiliência: adicionado `errorElement={<RouteError />}` em todas as rotas
(`router.jsx`), substituindo a tela branca/overlay de dev do React Router
por uma UI amigável com botão "Tentar novamente" (recarrega a página) —
exatamente a sugestão que aparecia no próprio overlay de erro. Chaves de
tradução reaproveitadas do bloco `errors` já existente (havia uma chave
`errors` duplicada no JSON de en/pt-BR; consolidada em uma só, evitando
que a última ocorrência sobrescrevesse a anterior no parse).

Teste `RouteError.test.jsx` cobre renderização da mensagem e o botão de
reload (RED → GREEN, TDD).
