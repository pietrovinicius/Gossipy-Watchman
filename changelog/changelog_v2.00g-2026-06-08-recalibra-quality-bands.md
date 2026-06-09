## v2.00g — 2026-06-08

### Tipo da mudança
fix

### Arquivos alterados
- app/services/person_service.py
- tests/unit/test_person_service.py

### Impacto técnico/funcional
Bandas de qualidade em `_QUALITY_BANDS` estavam calibradas para distância
euclidiana (valores 0–2+). Após migração para ArcFace/coseno (valores 0–1),
quase todo match válido caía em "excelente" (qualquer score > 60% = threshold).

Novas bandas calibradas para coseno:
- excelente: score > 90% (dist < 0.1 — match muito próximo)
- bom:        score > 80% (dist < 0.2)
- regular:    score > 70% (dist < 0.3)
- insuficiente: score > 60% (dist < 0.4)
- fraco:      score ≤ 60% (dist ≥ 0.4, acima do threshold)

Docstring corrigida: "euclidiana" → "coseno ArcFace". Testes antigos atualizados
com confidence values coerentes com coseno. Novo teste RED→GREEN confirma que
dist=0.3 deixou de ser classificado como "excelente".
