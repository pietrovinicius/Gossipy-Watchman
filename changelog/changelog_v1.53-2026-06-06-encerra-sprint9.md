## v1.53 — 2026-06-06

### Tipo da mudança
chore

### Arquivos alterados
- Anotacoes.txt

### Impacto técnico/funcional
Encerra Sprint 9 — PersonDetail Avançado. Verificação final: 248/248 testes backend
(pytest), 91/91 testes frontend (vitest), build de produção OK. Atualiza versão em
Anotacoes.txt para 1.5.3.

### Resumo do sprint
- Opção B adotada para 9.1: worker salvava só 1 crop por pessoa (sem amostras por
  aparição); implementado `save_face_sample()` + integração no `video_worker.py` +
  endpoint `GET /people/{id}/frames`.
- 9.2: `PATCH /people/{id}/primary-photo` com cadeia de validação 400 (path traversal)
  → 404 (arquivo/pessoa não encontrados) → 403 (arquivo de outra pessoa), via `shutil.copy2`.
- 9.3: `GET /people/{id}/quality` com avg_confidence, sample_count, quality_score,
  quality_level, recommendation, color (bandas de qualidade calibradas pelos exemplos
  do spec).
- 9.4-9.6: PhotoModal (zoom acessível, Portal/focus trap/Escape/click-outside),
  PersonFrames (galeria com ação "Definir como principal") e ProfileQuality
  (sinal semafórico + score + recomendação) integrados ao PersonDetail.
- Testes novos: ~28 backend (unit+integration) + 21 frontend (componentes) = 49.
- Total acumulado: 248 backend / 91 frontend (339 testes).

### Limitações conhecidas
- A galeria de frames só populará progressivamente com novos vídeos processados —
  vídeos já processados antes desta sprint não geraram amostras (`save_face_sample`
  foi adicionado agora), então pessoas antigas mostrarão só a foto principal até
  novo reconhecimento.
- Limite de 10 amostras por pessoa (`MAX_FACE_SAMPLES`); amostras além do limite
  não são salvas (sem rotação/substituição das mais antigas).
