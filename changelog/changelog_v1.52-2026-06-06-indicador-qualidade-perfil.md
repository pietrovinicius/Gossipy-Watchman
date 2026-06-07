## v1.52 — 2026-06-06

### Tipo da mudança
feat

### Arquivos alterados
- app/services/person_service.py (get_profile_quality, _QUALITY_BANDS)
- app/schemas/person.py (ProfileQualityResponse)
- app/api/v1/people.py (GET /people/{id}/quality)
- app/core/settings.py, frontend/package.json (bump 1.5.2)
- tests/unit/test_person_service.py, tests/integration/test_people.py

### Impacto técnico/funcional
Novo endpoint GET /people/{person_id}/quality traduz a confiança média
das aparições (confidence = distância euclidiana, menor = mais
confiante) em um indicador de qualidade do perfil.

get_profile_quality() calcula avg_confidence, sample_count e
quality_score = (1 - avg_confidence) * 100, classificando em 5 níveis
por faixa de score: excelente (>60, verde), bom (>48, verde), regular
(>44, amarelo), insuficiente (>40 ou sem amostras, amarelo/vermelho) e
fraco (<=40, vermelho), cada um com recomendação textual de ação.

12 novos testes (10 unitários de serviço + 2 de integração de endpoint).
248/248 testes passando.
