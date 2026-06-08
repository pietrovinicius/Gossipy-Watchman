## v1.9.4 — 2026-06-08

### Tipo da mudança
refactor

### Arquivos alterados
- app/workers/video_worker.py
- tests/integration/test_video_worker.py

### Impacto técnico/funcional
Sprint 16.4 — integração do `FaceTracker` no pipeline de `process_video`.

Antes: cada detecção de rosto era resolvida (match + persistência) frame a
frame, isoladamente — fonte direta do problema relatado em produção ("vídeo X
mostra pessoas do vídeo Y" e falsos positivos por ruído de frames isolados).

Agora: durante a varredura de frames, cada detecção é alimentada a um
`FaceTracker` (`add_detection`); identidade só é resolvida ao final, por track
completo, via novo helper `_process_track`:
- usa `track.mean_embedding()` (média de todas as amostras da aparição) para
  o matching — muito mais estável que um embedding de frame isolado;
- usa `track.get_best_crop()` (frame com maior área de rosto) como recorte
  salvo, em vez do frame inteiro;
- aplica a mesma lógica de pessoa nova / aparição conhecida / alerta de
  monitorado, agora em granularidade de track.

Tracks com menos de `FACE_TRACK_MIN_SAMPLES` amostras são descartados pelo
próprio `FaceTracker.flush()` e nunca chegam a `_process_track` — eliminando
ruído de detecções pontuais.

Suíte de integração reescrita para o novo fluxo: 9 testes (status, pessoa
nova, track curto descartado, aparição conhecida, embedding médio usado no
matching, alertas de monitorado/funcionário, alerta único por pessoa mesmo com
múltiplos tracks). Suíte completa: 398 testes passando.
