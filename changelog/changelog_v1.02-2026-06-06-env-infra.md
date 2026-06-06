## v1.02 — 2026-06-06

### Tipo da mudança
chore

### Arquivos alterados
- .env.example
- .gitignore (+ entradas storage/*, frontend/dist, *.db)
- README.md (instrução cp .env.example .env)

### Impacto técnico/funcional
Infraestrutura .env: .env.example com todas as variáveis documentadas e comandos
de geração de JWT_SECRET_KEY e ADMIN_PASSWORD_HASH. .env criado localmente (não commitado).
.gitignore atualizado com entradas de storage, frontend e banco.
