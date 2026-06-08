# Design: Melhoria de Acurácia — InsightFace (RetinaFace + ArcFace)

**Data:** 2026-06-08
**Status:** Aprovado
**Versão alvo:** v1.97.0

---

## Problema

O pipeline atual (`face_recognition` / dlib) apresenta dois problemas observados:

- **D — Rostos não detectados:** dlib CNN falha em câmeras de segurança (rostos pequenos, distantes, angulados), vídeos de celular (movimento, blur) e reuniões (perfil, oclusão parcial).
- **C — Falsos positivos e negativos:** embeddings de 128 dimensões têm discriminação limitada; pessoas semelhantes colidem, e variações de iluminação/ângulo da mesma pessoa divergem além do threshold.

---

## Solução

Substituir a camada de detecção e embedding por **InsightFace `buffalo_l`**:

| Componente | Atual | Novo |
|---|---|---|
| Detector | dlib CNN | RetinaFace (multi-escala) |
| Embeddings | 128-dim euclidiana | 512-dim ArcFace coseno |
| Backend | dlib C++ CPU | ONNX Runtime + CoreML (M4) |
| Embeddings por pessoa | 1 `.npy` | até 5 `.npy` (multi-embedding) |

---

## Arquitetura

O worker, o tracker e a camada de API **não mudam**. Apenas a camada `face_service.py` e partes de `person_service.py` são alteradas.

```
[video_worker] → [frame_service] → [face_service]
                                        ↓
                                  FaceAnalysis("buffalo_l")  ← singleton lazy
                                  RetinaFace detector
                                  ArcFace encoder (512-dim, L2-norm)
                                        ↓
                                  FaceTracker (sem mudança)
                                  find_matching_person (coseno)
                                  MultiEmbeddingStore (top-5 por pessoa)
```

---

## Especificação por Componente

### 1. `face_service.py`

**Singleton:**
```python
_face_app: FaceAnalysis | None = None

def get_face_app() -> FaceAnalysis:
    global _face_app
    if _face_app is None:
        _face_app = FaceAnalysis(name=settings.INSIGHTFACE_MODEL)
        _face_app.prepare(ctx_id=0, det_size=(settings.INSIGHTFACE_DET_SIZE, settings.INSIGHTFACE_DET_SIZE))
    return _face_app
```

- `ctx_id=0` → ONNX Runtime tenta CoreML automaticamente no Apple Silicon
- Inicializado no `lifespan` do FastAPI para pre-warm (evitar latência no primeiro vídeo)

**`extract_embeddings(frame)`:**
- Chama `get_face_app().get(frame)` → lista de `Face`
- Cada `Face` tem: `bbox` (x1,y1,x2,y2), `det_score` (0-1), `embedding` (np.ndarray 512-dim, já L2-normalizado)
- Converte `bbox` para formato `(top, right, bottom, left)` para manter interface com `FaceTracker`
- Filtra: `det_score < INSIGHTFACE_DET_SCORE` e tamanho mínimo `FACE_MIN_SIZE_PX`
- Retorna `list[tuple[np.ndarray, tuple]]` — mesma assinatura de antes

**`is_good_quality_frame`:**
- Mantém filtro de tamanho e variância Laplaciana
- Adiciona: `det_score` como parâmetro opcional (repassado de `extract_embeddings`)

**`find_matching_person`:**
- Troca `face_recognition.face_distance` por distância coseno: `1 - np.dot(embedding, known_vec)` (válido pois embeddings são L2-normalizados)
- Lógica k-NN e votação permanecem idênticas
- `FACE_RECOGNITION_TOLERANCE = 0.4` (coseno — equivale a ~0.6 euclidiano no espaço ArcFace)

**`FaceTrack` / `FaceTracker`:** sem nenhuma mudança.

---

### 2. `person_service.py`

**`save_new_person`:** sem mudança de interface — salva `mean_embedding` do track como `embedding_0.npy`.

**`save_face_sample`:** após aparição confirmada, avalia se o embedding do novo track tem qualidade superior à média atual dos embeddings gravados. Se sim, e se o total for menor que `FACE_MAX_EMBEDDINGS_PER_PERSON`, grava `embedding_N.npy` adicional.

**`get_all_embeddings`:** carrega **todos** os `.npy` de cada pessoa (padrão `embedding_*.npy`) e retorna `list[tuple[person_id, np.ndarray]]`. O k-NN vota contra cada embedding individualmente — mais cobertura de pose/iluminação.

---

### 3. `app/core/settings.py`

Novos parâmetros:

```python
INSIGHTFACE_MODEL: str = "buffalo_l"
INSIGHTFACE_DET_SIZE: int = 640
INSIGHTFACE_DET_SCORE: float = 0.7
FACE_MAX_EMBEDDINGS_PER_PERSON: int = 5
# Alterado:
FACE_RECOGNITION_TOLERANCE: float = 0.4  # coseno (era 0.6 euclidiano)
```

---

### 4. Migration: `app/db/migrations/migration_insightface.py`

Executada no lifespan **antes** de `init_db()`. Idempotente.

**Lógica:**
1. Varre `storage/faces/` e `storage/employees/` por arquivos `.npy`
2. Carrega cada `.npy` com `np.load`
3. Se `shape == (128,)` → arquivo dlib incompatível → deleta
4. Zera `Person.profile_image_path` para pessoas cujo embedding foi deletado (`.jpg` do recorte permanece intacto)
5. Loga quantos arquivos foram removidos

**Não apaga:** pessoas, aparições, vídeos, recortes `.jpg`.

---

### 5. `requirements.txt`

```
insightface>=0.7.3
onnxruntime>=1.17.0
```

Remove: `face-recognition`, `dlib`, `setuptools<71`.

---

### 6. `app/main.py` — lifespan

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    run_all_migrations()
    init_db()
    face_service.get_face_app()   # pre-warm InsightFace
    ws_manager.set_loop(asyncio.get_event_loop())
    yield
```

---

## Fluxo de Dados (por frame processado)

```
frame (BGR np.ndarray)
    └→ get_face_app().get(frame)
           └→ [Face(bbox, det_score, embedding), ...]
                  └→ filtro det_score >= 0.7
                  └→ filtro tamanho >= FACE_MIN_SIZE_PX
                  └→ filtro blur (Laplaciano)
                  └→ FaceTracker.add_detection(embedding, location, frame, timestamp)

fim do vídeo:
    └→ tracker.flush() → [FaceTrack, ...]
           └→ _process_track(track)
                  └→ mean_embedding = track.mean_embedding()
                  └→ get_all_embeddings(db) → [(person_id, emb_0), (person_id, emb_1), ...]
                  └→ find_matching_person(mean_embedding, known) [coseno k-NN]
                  └→ nova pessoa OU upsert_appearance + save_face_sample
```

---

## Testes

| Arquivo | Cobertura |
|---|---|
| `tests/unit/test_face_service.py` | `extract_embeddings` (mock FaceAnalysis), `find_matching_person` com coseno, `is_good_quality_frame` + det_score, singleton `get_face_app` |
| `tests/unit/test_person_service.py` | `get_all_embeddings` com múltiplos `.npy`, lógica de adição de embedding |
| `tests/unit/test_migration_insightface.py` | idempotência, detecção shape 128 vs 512, preservação de `.jpg` |
| `tests/integration/test_video_worker.py` | pipeline end-to-end com mock de `get_face_app` |

---

## Fora do Escopo

- GPU NVIDIA / CUDA (hardware não disponível)
- Re-identificação entre vídeos (re-clustering de desconhecidos) — sprint futura
- Super-resolução de frames — complexidade não justificada agora
- Fine-tuning do modelo ArcFace — requer dataset proprietário

---

## Ordem de Implementação

1. `requirements.txt` — adicionar deps, remover dlib
2. `settings.py` — novos parâmetros
3. `migration_insightface.py` — RED → GREEN → REFACTOR
4. `face_service.py` — substituição do detector/encoder — RED → GREEN → REFACTOR
5. `person_service.py` — multi-embedding — RED → GREEN → REFACTOR
6. `main.py` — pre-warm no lifespan
7. `pytest` completo
8. Changelog + commit + push
