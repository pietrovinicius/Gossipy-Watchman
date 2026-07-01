## v2.25 — 2026-07-01

### Tipo da mudança
chore

### Arquivos alterados
- iniciar.bat

### Impacto técnico/funcional
Adiciona `iniciar.bat` na raiz do projeto para subir backend e frontend
com um duplo-clique, seguindo as premissas documentadas em
`Anotacoes.txt`: ativa a venv e sobe `uvicorn app.main:app --reload
--host 0.0.0.0 --port 8002` (bind em 0.0.0.0 para acesso via rede local,
conforme fix de rede da v2.23) em uma janela, e `npm run dev` do
frontend (porta 5174) em outra. Valida pré-requisitos antes de iniciar
(venv, `.env`, `node_modules`) e aborta com mensagem clara se algo
faltar, evitando erros silenciosos tipo "ModuleNotFoundError: fastapi"
por venv não ativada. Infra pura sem lógica de negócio — sem teste
automatizado aplicável (exceção TDD do CLAUDE.md §7).
