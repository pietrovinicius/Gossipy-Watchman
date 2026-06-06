## v1.08 — 2026-06-06

### Tipo da mudança
chore

### Arquivos alterados
- Todos os arquivos criados/alterados durante a Sprint 5

### Impacto técnico/funcional
Encerramento da Sprint 5 — hardening completo. Verificação final:
- 125 testes passando (95 anteriores + 30 novos da Sprint 5)
- .env não rastreado pelo git; .env.example commitado
- GET /api/v1/health sem token → 200; GET /api/v1/videos sem token → 401
- Upload com ../../../etc/passwd.mp4 → salvo como UUID (sem traversal)
- /faces/ StaticFiles removido → 404
- Build frontend: 506ms, 0 erros
- Security headers em todas as respostas
