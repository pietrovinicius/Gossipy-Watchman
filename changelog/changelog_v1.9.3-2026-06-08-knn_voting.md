## v1.9.3 — 2026-06-08

### Tipo da mudança
feat

### Arquivos alterados
- app/services/face_service.py
- tests/unit/test_face_service.py

### Impacto técnico/funcional
Sprint 16.3 — votação k-NN em `find_matching_person`, substituindo argmin simples.

Antes: aceitava cegamente o vizinho mais próximo isolado (argmin), vulnerável a
falsos positivos quando uma pessoa está super-representada no banco de
embeddings (muitas aparições aumentam a chance de ela ser "a mais próxima" por
acaso).

Agora: filtra candidatos dentro de `tolerance`, pega os `k` (`FACE_KNN_K=3`)
vizinhos mais próximos e faz votação por maioria entre `person_id`s. Vencedor =
maior número de votos; empate desfeito pela menor distância. Distância
retornada = menor distância entre os votos do vencedor.

5 novos testes: vitória por maioria mesmo sem ser o vizinho mais próximo
isolado, ignorar vizinhos fora da tolerância, todos fora da tolerância →
nenhuma pessoa, validação do parâmetro `k` com default `settings.FACE_KNN_K`.
Suíte completa: 396 testes passando.
