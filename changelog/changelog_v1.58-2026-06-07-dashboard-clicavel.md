## v1.58 — 2026-06-07

### Tipo da mudança
feat

### Arquivos alterados
- frontend/src/pages/Dashboard.jsx
- frontend/src/test/Dashboard.test.jsx
- frontend/package.json

### Impacto técnico/funcional
Linhas da tabela "Vídeos recentes" do Dashboard tornam-se clicáveis,
navegando para /videos/{id} via useNavigate. Adicionado cursor-pointer,
hover (bg-slate-50 / dark:hover:bg-[#1F2937]) com transition-colors,
tooltip "Ver detalhes do vídeo" e ícone ChevronRight como indicador
visual ao final de cada linha. O botão de exportar CSV usa
stopPropagation para não disparar a navegação ao ser clicado. 4 novos
testes cobrindo navegação por clique na linha, não-navegação ao exportar,
classe cursor-pointer e renderização do ChevronRight. Suíte completa do
frontend: 112/112.
