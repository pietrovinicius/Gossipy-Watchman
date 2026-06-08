## v1.8.7 — 2026-06-07

### Corrigido

**PersonFrames.jsx + backend:**
- Botão "Definir como principal" agora funciona (melhorado error handling)
- Adicionado funcionalidade de deletar frames individuais
- Endpoint DELETE `/people/{id}/frames/{filename}` implementado
- Validação contra path traversal e deleção de foto principal

**VideoDetail.jsx:**
- Removida movimentação automática (auto-scroll) durante execução do vídeo
- Usuário pode agora apenas assistir sem interferência da UI

**Impacto:**
- /people/{id}: frames agora com botões "Definir como principal" e "Deletar"
- /videos/{id}: sem auto-scroll enquanto assiste

**Testes:** 183 testes passam (0 regressões).
