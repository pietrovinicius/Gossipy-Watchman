# Plano de Melhorias — Identificação de Rostos

**Versão alvo:** 1.98.0  
**Data:** 2026-06-08  
**Base:** análise do pipeline InsightFace pós-migração v1.97.0

---

## Objetivo

Corrigir bugs críticos e melhorar a acurácia/performance do pipeline de reconhecimento facial, sem alterar a interface pública da API.

---

## Arquitetura das mudanças

```
app/workers/video_worker.py     → Tasks 1, 2
app/services/face_service.py    → Tasks 3, 4, 5
app/services/frame_service.py   → Task 4
app/core/settings.py            → Tasks 2, 4, 5
tests/unit/test_face_service.py → Tasks 3, 4, 5
tests/unit/test_face_tracker.py → Tasks 3, 5
tests/integration/test_video_worker.py → Tasks 1, 2
```

---

## Task 1 — Corrigir person_counter (bug trivial)

**Arquivo:** `app/workers/video_worker.py:156`

**Bug:**
```python
person_counter = db.query(Video).count()  # ERRADO — usa contagem de vídeos
```

**Fix:**
```python
person_counter = db.query(Person).count()  # conta pessoas existentes
```

**Teste RED:**
```python
# tests/integration/test_video_worker.py
def test_person_counter_usa_contagem_de_pessoas(video_in_db):
    """person_counter deve iniciar com número de pessoas, não de vídeos."""
    # criar 3 pessoas e 7 vídeos → counter deve iniciar em 3, não em 7
```

---

## Task 2 — Cache de embeddings no worker (performance crítica)

**Arquivo:** `app/workers/video_worker.py`

**Problema:** `get_all_embeddings` é chamado em `_process_track` para CADA track, relendo todos os `.npy` do disco a cada vez.

**Fix:** carregar embeddings UMA VEZ em `process_video` e passar para `_process_track` como parâmetro. Ao criar nova pessoa, adicionar o embedding ao cache local imediatamente.

**Assinatura após fix:**
```python
def _process_track(
    db,
    video_id: int,
    track,
    person_counter: int,
    alerted_in_this_video: set[int],
    known_embeddings: list[tuple[int, np.ndarray]],  # novo parâmetro
) -> tuple[int, list[tuple[int, np.ndarray]]]:       # retorna counter + cache atualizado
```

**Teste RED:**
```python
def test_get_all_embeddings_chamado_uma_vez_por_video(video_in_db):
    """get_all_embeddings deve ser chamado 1x por vídeo, não N vezes por track."""
    with patch("app.workers.video_worker.person_service.get_all_embeddings") as mock:
        ...
    assert mock.call_count == 1
```

---

## Task 3 — FaceTrack armazena crop, não frame completo (memória)

**Arquivo:** `app/services/face_service.py`

**Problema:** `FaceTrack._frames_data` guarda frames BGR completos (~900KB cada). 100 frames = ~90MB por track.

**Fix:** extrair e guardar apenas o crop da face no momento do `add_frame_data`.

**Mudança em `FaceTrack`:**
```python
def add_frame_data(self, embedding, location, frame, timestamp, det_score=1.0):
    top, right, bottom, left = location
    crop = frame[top:bottom, left:right].copy()   # só o crop
    self._frames_data.append({
        "crop": crop,
        "area": (right - left) * (bottom - top),
        "timestamp": timestamp,
        "det_score": det_score,
    })
    self.last_seen = timestamp
```

**`get_best_crop` simplificado:**
```python
def get_best_crop(self) -> np.ndarray:
    best = max(self._frames_data, key=lambda d: d["area"])
    return best["crop"]
```

**Teste RED:**
```python
def test_face_track_armazena_crop_nao_frame_completo():
    """_frames_data deve guardar crop extraído, não o frame inteiro."""
    track = FaceTrack(start_time=0.0)
    big_frame = np.zeros((1080, 1920, 3), dtype=np.uint8)
    location = (100, 200, 160, 140)  # crop 60x60
    track.add_frame_data(make_embedding(), location, big_frame, timestamp=1.0)
    # crop 60x60 << frame 1920x1080
    assert track._frames_data[0]["crop"].shape == (60, 60, 3)
```

---

## Task 4 — Motion Gating com fallback periódico

**Arquivo:** `app/services/frame_service.py`, `app/core/settings.py`, `app/workers/video_worker.py`

**Problema:** cena estática com pessoa parada → Motion Gating pula todos os frames indefinidamente.

**Fix:** forçar detecção a cada `MOTION_GATING_FORCE_INTERVAL` segundos, mesmo sem movimento.

**Novo setting:**
```python
MOTION_GATING_FORCE_INTERVAL: int = 5  # segundos
```

**Lógica no worker:**
```python
last_forced_detection = -999.0
...
force_detect = (segundo - last_forced_detection) >= settings.MOTION_GATING_FORCE_INTERVAL
if run_detection or force_detect:
    ...
    if force_detect:
        last_forced_detection = segundo
```

**Teste RED:**
```python
def test_motion_gating_forca_deteccao_periodica():
    """Deve rodar detecção mesmo sem movimento a cada FORCE_INTERVAL segundos."""
```

---

## Task 5 — Média de embeddings ponderada por det_score

**Arquivo:** `app/services/face_service.py`

**Problema:** `mean_embedding` trata todos os frames com mesmo peso. Frames com baixo `det_score` degradam o embedding médio.

**Fix:** guardar `det_score` em `_frames_data` (Task 3 já prepara isso) e usar como peso:

```python
def mean_embedding(self) -> np.ndarray:
    weights = np.array([d["det_score"] for d in self._frames_data], dtype=np.float32)
    embs = np.array(self.embeddings, dtype=np.float32)
    mean = np.average(embs, axis=0, weights=weights)
    norm = np.linalg.norm(mean)
    return mean / norm if norm > 0 else mean
```

**Teste RED:**
```python
def test_mean_embedding_pondera_por_det_score():
    """Frame com det_score alto deve ter maior contribuição no embedding médio."""
    track = FaceTrack(start_time=0.0)
    emb_strong = np.zeros(512, dtype=np.float32); emb_strong[0] = 1.0
    emb_weak   = np.zeros(512, dtype=np.float32); emb_weak[1] = 1.0
    frame = make_bgr_frame()
    track.add_frame_data(emb_strong, make_location(), frame, timestamp=1.0, det_score=0.99)
    track.add_frame_data(emb_weak,   make_location(), frame, timestamp=2.0, det_score=0.50)
    mean = track.mean_embedding()
    # embedding resultante deve ser mais próximo de emb_strong
    assert np.dot(mean, emb_strong) > np.dot(mean, emb_weak)
```

**Nota:** Tasks 3 e 5 são implementadas juntas (Task 3 prepara o campo `det_score` que Task 5 consome).

---

## Task 6 — FaceTracker multi-face com associação por IoU

**Arquivo:** `app/services/face_service.py`

**Problema:** `FaceTracker` mantém apenas `active_track` único. Com múltiplas pessoas simultâneas, embeddings de pessoas diferentes são mesclados.

**Fix:** dicionário `active_tracks: dict[int, FaceTrack]` com associação por IoU entre bboxes de frames consecutivos.

**Estrutura:**
```python
class FaceTracker:
    def __init__(self, gap_tolerance, min_samples, iou_threshold=0.3):
        self.active_tracks: list[tuple[np.ndarray, FaceTrack]] = []
        # (last_bbox, track)
    
    def add_detection(self, embedding, location, frame, timestamp, bbox=None):
        # associar por IoU com bbox mais próxima nos active_tracks
        # bbox não associada → novo track
```

**Requer:** `bbox` como parâmetro adicional em `add_detection` (já disponível no `face.bbox` do InsightFace).

**Atualizar `video_worker.py`:**
```python
for embedding, location, bbox in embeddings:  # extract_embeddings retorna bbox tbm
    tracker.add_detection(embedding, location, frame, timestamp, bbox=bbox)
```

**Atualizar `extract_embeddings`** para retornar `(embedding, location, bbox)`.

**Complexidade:** Alta. Implementar separado.

---

## Task 7 — det_size adaptativo à resolução do vídeo

**Arquivo:** `app/workers/video_worker.py`, `app/services/face_service.py`

**Problema:** `INSIGHTFACE_DET_SIZE = 640` fixo para todos os vídeos.

**Fix:** calcular det_size baseado no primeiro frame e reinicializar o modelo se necessário, ou escalar o frame antes de enviar para o InsightFace.

**Abordagem simples (sem reinicializar modelo):** redimensionar frame para width máximo de 1280 antes de enviar para `extract_embeddings` em vídeos 4K.

---

## Ordem de execução

| Task | Complexidade | Impacto | Pré-requisito |
|------|-------------|---------|--------------|
| 1 — person_counter bug | Trivial | Bug fix | — |
| 2 — cache embeddings | Baixa | Performance crítica | — |
| 3+5 — crop + det_score weight | Baixa | Memória + acurácia | — |
| 4 — motion gating fallback | Baixa | Detecção perdida | — |
| 6 — multi-face tracking | Alta | Acurácia crítica | 3 |
| 7 — det_size adaptativo | Média | Detecção 4K | — |

**Execução imediata:** Tasks 1 → 2 → 3+5 → 4 → 6 → 7

---

## Versão alvo dos arquivos

- `app/workers/video_worker.py` — Tasks 1, 2, 4
- `app/services/face_service.py` — Tasks 3, 5, 6
- `app/core/settings.py` — Tasks 2, 4
- `tests/unit/test_face_service.py` — Tasks 3, 5, 6
- `tests/unit/test_face_tracker.py` — Tasks 3, 5, 6
- `tests/integration/test_video_worker.py` — Tasks 1, 2, 4
