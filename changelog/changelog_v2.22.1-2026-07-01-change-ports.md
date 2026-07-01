## v2.22.1 — 2026-07-01

### Tipo da mudança
chore | fix

### Arquivos alterados
- app/main.py
- frontend/src/components/VideoPlayer.jsx
- frontend/src/pages/Login.jsx
- frontend/src/services/api.js
- frontend/vite.config.js
- tests/unit/test_settings.py

### Impacto técnico/funcional
- Alteração das portas padrão para evitar conflitos: backend alterado de 8000 para 8001 e frontend alterado de 5173 para 5174.
- Atualização do CORS no backend para permitir conexões do frontend na porta 5174.
- Correção de testes de caminhos no Windows substituindo str() por .as_posix() para garantir independência de plataforma.
- Configuração do arquivo .env com chaves seguras e otimizações de execução.
