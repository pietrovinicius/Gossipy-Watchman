## v1.42 — 2026-06-06

### Tipo da mudança
fix

### Arquivos alterados
- app/services/person_service.py
- tests/unit/test_person_service.py

### Impacto técnico/funcional
GET /people/{id}/stats retornava 500 (TypeError: unsupported operand
type(s) for -: 'NoneType' and 'float') quando a pessoa possuía uma
aparição "aberta" (timestamp_end=None — última aparição de um vídeo
cujo intervalo nunca foi fechado pelo pipeline).

get_person_stats() agora ignora aparições com timestamp_end=None no
cálculo de total_seconds, em vez de tentar subtrair None de float.
Comportamento alinhado ao já adotado em export_service (CSV trata
duração como vazia quando timestamp_end é None).

Teste de regressão adicionado:
test_get_person_stats_ignores_open_appearance_without_timestamp_end.
221/221 testes passando.
