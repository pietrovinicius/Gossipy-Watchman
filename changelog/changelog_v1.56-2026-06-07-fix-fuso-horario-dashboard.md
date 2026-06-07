## v1.56 — 2026-06-07

### Tipo da mudança
fix

### Arquivos alterados
- frontend/src/utils/formatDate.js
- frontend/src/utils/formatDate.test.js
- frontend/src/pages/Dashboard.jsx
- frontend/package.json

### Impacto técnico/funcional
Corrige exibição incorreta de horário no Dashboard (vídeo enviado às 9h
aparecia como 12h). Backend serializa `uploaded_at` como datetime naive em
UTC (ex.: "2026-06-07T12:00:02"), sem designador de timezone; `new Date()`
no JS interpretava essa string como horário local em vez de UTC, deixando
o valor exibido 3h adiantado (offset America/Sao_Paulo). Criado utilitário
`parseUtcDate`/`formatDateTime` que força a leitura como UTC quando a string
não traz designador (`Z`/offset), convertendo corretamente para o horário
local do navegador antes de formatar em pt-BR. Dashboard passa a usar
`formatDateTime`. 6 novos testes unitários cobrindo string naive, com `Z`,
com offset explícito e entradas vazias; suíte completa do frontend
(97/97) permanece verde.
