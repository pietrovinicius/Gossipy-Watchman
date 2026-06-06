## v1.03 — 2026-06-06

### Tipo da mudança
chore

### Arquivos alterados
- requirements.txt

### Impacto técnico/funcional
Adiciona dependências de segurança: python-jose[cryptography] (JWT), passlib[bcrypt]
(hash de senha), python-magic (validação de magic bytes), python-dotenv (carregamento .env).
Todas instaladas sem conflito.
