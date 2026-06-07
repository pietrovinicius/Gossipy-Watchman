## v1.80 — 2026-06-07 (Sprint 15 Início)

### Tipo da mudança
chore

### Impacto técnico/funcional

**SPRINT 15 INICIADA — Barra de Presença, Auto-scroll e Cadastro de Funcionários**

Cronograma atualizado com 3 funcionalidades:

✅ Cronograma de Sprints — Gossipy Watchman.docx:
- Sprint 15 expandido com "Cadastro de Funcionários"
- Tela dedicada para cadastro prévio de funcionários
- Embedding extraído no cadastro, reconhecimento automático nos vídeos
- Endpoints: POST/GET/PATCH/DELETE /api/v1/employees
- Model Employee vinculado a Person com categoria "Funcionário"
- Storage: storage/employees/ para fotos e embeddings

Próximas etapas (7 fases):
1. Barra de presença visual no player (frontend)
2. Auto-scroll ao entrar em cena (frontend)
3. Modelo e migração de funcionários (backend)
4. Serviço de funcionários (backend)
5. Endpoints /api/v1/employees (backend)
6. Tela /employees (frontend)
7. Verificação final

Métricas esperadas:
- Backend: +50 testes (migration + service + endpoints)
- Frontend: +30 testes (VideoPlayer + VideoSync + Employees)
- Total acumulado: ~434 testes backend + 205 frontend

Performance target:
- register_employee embedding extraction < 2s
- POST /employees upload + conversion < 5s
- barra presença render < 100ms
