## v2.00f — 2026-06-08

### Tipo da mudança
fix

### Arquivos alterados
- app/services/face_service.py
- tests/unit/test_face_service.py

### Impacto técnico/funcional
`find_matching_person` assumia que `known_vecs` eram sempre L2-normalizados.
Embeddings médios de múltiplas amostras ou carregados de disco podem ter escala
ligeiramente diferente de 1.0. Sem normalização, `dot(q, known)` retorna valor
fora de [0,1], tornando `1 - dot` inválido como distância coseno. Fix: normaliza
cada linha de `known_vecs` antes do produto escalar. Novo teste RED→GREEN
demonstra que embedding com escala 0.1 (mesma direção) era incorretamente
rejeitado como falso negativo sem a normalização.
