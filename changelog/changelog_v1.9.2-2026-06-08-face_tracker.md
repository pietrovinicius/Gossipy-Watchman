## v1.9.2 — 2026-06-08

### Tipo da mudança
feat

### Arquivos alterados
- app/services/face_service.py
- tests/unit/test_face_tracker.py

### Impacto técnico/funcional
Sprint 16.2 — agregação de embeddings por aparição contínua (track).

`FaceTrack`: agrupa detecções consecutivas de um mesmo rosto, mantém
`embeddings`, `start_time`/`last_seen` e calcula `mean_embedding()` (média dos
embeddings da aparição — reduz ruído de frames isolados de baixa qualidade
antes de comparar com pessoas conhecidas). `get_best_crop()` seleciona o
recorte do frame com maior área de rosto na track, substituindo o recorte de
frame inteiro usado anteriormente.

`FaceTracker`: orquestra tracks ao longo do vídeo — continua o track ativo
enquanto o gap entre detecções for ≤ `FACE_TRACK_GAP_TOLERANCE` (2.0s),
encerra e abre novo track quando o gap é maior, e descarta tracks com menos de
`FACE_TRACK_MIN_SAMPLES` (2) amostras (aparições muito curtas — fonte comum de
falsos positivos). `flush()` fecha o track ativo ao final do vídeo.

12 novos testes unitários cobrindo agregação, contagem de amostras, seleção do
melhor recorte, continuidade/encerramento de tracks por gap, e descarte por
amostra insuficiente. Suíte completa: 392 testes passando.
