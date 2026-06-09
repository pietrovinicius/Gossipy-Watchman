## v2.00c — 2026-06-08

### Tipo da mudança
fix

### Arquivos alterados
- app/services/cluster_service.py
- tests/unit/test_cluster_service.py

### Impacto técnico/funcional
Algoritmo de clusterização substituído de single linkage (componentes conectados)
para complete linkage. O algoritmo antigo encadeava A≈B≈C num único cluster
mesmo quando dist(A,C) > threshold — pessoas distintas sendo mescladas por
intermediário. O novo algoritmo só funde dois clusters quando a distância máxima
entre todos os pares inter-cluster é < threshold, eliminando o efeito corrente.
Novo teste RED→GREEN demonstra o cenário A-B-C com dist(A,C)>0.4: resultado
correto é 1 grupo de 2 membros (não trio).
