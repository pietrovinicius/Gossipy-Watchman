# InsightFace Accuracy — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Substituir dlib/face_recognition por InsightFace (RetinaFace + ArcFace) para melhorar detecção e discriminação de rostos em todos os tipos de vídeo.

**Architecture:** A camada `face_service.py` é completamente reescrita com InsightFace como backend. `person_service.py` passa a suportar múltiplos embeddings por pessoa (até 5). O worker, tracker e API não mudam. Uma migration limpa os `.npy` dlib (128-dim) incompatíveis.

**Tech Stack:** `insightface>=0.7.3`, `onnxruntime>=1.17.0`, FastAPI, SQLAlchemy, pytest

---

## Mapeamento de Arquivos

| Arquivo | Ação | Responsabilidade |
|---|---|---|
| `requirements.txt` | Modificar | Remove dlib deps, adiciona insightface+onnxruntime |
| `app/core/settings.py` | Modificar | Novos parâmetros InsightFace |
| `app/db/migrations/migration_insightface.py` | Criar | Limpa `.npy` 128-dim incompatíveis |
| `app/services/face_service.py` | Reescrever | Detector RetinaFace + encoder ArcFace |
| `app/services/person_service.py` | Modificar | Multi-embedding (até 5 `.npy` por pessoa) |
| `app/main.py` | Modificar | Chama migration + pre-warm no lifespan |
| `tests/unit/test_settings.py` | Modificar | Testa novos parâmetros |
| `tests/unit/test_migration_insightface.py` | Criar | Testa idempotência e limpeza de 128-dim |
| `tests/unit/test_face_service.py` | Reescrever | Mocks InsightFace, coseno, det_score |
| `tests/unit/test_person_service.py` | Modificar | Multi-embedding: get_all_embeddings, save_face_sample |

---

## Task 1: Dependências

**Files:**
- Modify: `requirements.txt`

- [ ] **Step 1: Atualizar requirements.txt**

Substituir o conteúdo:

```
fastapi>=0.111.0
uvicorn[standard]>=0.29.0
sqlalchemy>=2.0.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
python-multipart>=0.0.9
pytest>=8.0.0
pytest-asyncio>=0.23.0
httpx>=0.27.0
opencv-python>=4.9.0
numpy>=1.26.0
insightface>=0.7.3
onnxruntime>=1.17.0
python-jose[cryptography]>=3.3.0
passlib[bcrypt]>=1.7.4
python-magic>=0.4.27
python-dotenv>=1.0.0
websockets>=12.0
```

- [ ] **Step 2: Instalar dependências**

```bash
source venv/bin/activate
pip install insightface>=0.7.3 onnxruntime>=1.17.0
pip uninstall face-recognition dlib -y
```

Esperado: sem erros. InsightFace vai baixar `buffalo_l` (~300MB) na primeira chamada `get_face_app()`.

---

## Task 2: Settings — novos parâmetros InsightFace

**Files:**
- Modify: `app/core/settings.py`
- Test: `tests/unit/test_settings.py`

- [ ] **Step 1: Escrever teste que falha**

Adicionar ao final de `tests/unit/test_settings.py`:

```python
def test_insightface_model_default():
    from app.core.settings import settings
    assert settings.INSIGHTFACE_MODEL == "buffalo_l"

def test_insightface_det_size_default():
    from app.core.settings import settings
    assert settings.INSIGHTFACE_DET_SIZE == 640

def test_insightface_det_score_default():
    from app.core.settings import settings
    assert settings.INSIGHTFACE_DET_SCORE == 0.7

def test_face_max_embeddings_per_person_default():
    from app.core.settings import settings
    assert settings.FACE_MAX_EMBEDDINGS_PER_PERSON == 5

def test_face_recognition_tolerance_cosine_default():
    from app.core.settings import settings
    assert settings.FACE_RECOGNITION_TOLERANCE == 0.4
```

- [ ] **Step 2: Rodar teste para confirmar falha**

```bash
pytest tests/unit/test_settings.py::test_insightface_model_default -v
```

Esperado: `FAILED` — `AttributeError: 'Settings' object has no attribute 'INSIGHTFACE_MODEL'`

- [ ] **Step 3: Adicionar parâmetros em `app/core/settings.py`**

Na seção `# Visão computacional`, substituir:

```python
    # Visão computacional
    FACE_RECOGNITION_TOLERANCE: float = 0.4  # coseno (ArcFace)
    FRAMES_PER_SECOND_SAMPLE: int = 2

    # InsightFace
    INSIGHTFACE_MODEL: str = "buffalo_l"
    INSIGHTFACE_DET_SIZE: int = 640
    INSIGHTFACE_DET_SCORE: float = 0.7
    FACE_MAX_EMBEDDINGS_PER_PERSON: int = 5

    # Qualidade de frame
    FACE_MIN_SIZE_PX: int = 60
    FACE_BLUR_THRESHOLD: float = 100.0

    # Agregação por aparição contínua (track)
    FACE_TRACK_GAP_TOLERANCE: float = 2.0
    FACE_TRACK_MIN_SAMPLES: int = 2

    # k-NN voting
    FACE_KNN_K: int = 3

    # Motion Gating
    MOTION_GATING_ENABLED: bool = True
    MOTION_GATING_THRESHOLD: int = 15
    MOTION_GATING_AREA_RATIO: float = 0.001
```

Remover as linhas antigas que se tornaram obsoletas (dlib-específicas):
```python
    FACE_DETECTION_MODEL: str = "cnn"    # ← remover
    FACE_UPSAMPLE: int = 1               # ← remover
```

E remover toda a seção `# CNN adaptativo por duração`:
```python
    # CNN adaptativo por duração (segundos)
    CNN_ADAPTIVE_SHORT_MAX: int = 600     # ← remover
    CNN_ADAPTIVE_MEDIUM_MAX: int = 3600   # ← remover
    CNN_SHORT_UPSAMPLE: int = 2           # ← remover
    CNN_SHORT_FPS_SAMPLE: int = 2         # ← remover
    CNN_MEDIUM_UPSAMPLE: int = 1          # ← remover
    CNN_MEDIUM_FPS_SAMPLE: int = 2        # ← remover
    CNN_LONG_UPSAMPLE: int = 1            # ← remover
    CNN_LONG_FPS_SAMPLE: int = 1          # ← remover
```

- [ ] **Step 4: Rodar testes dos settings**

```bash
pytest tests/unit/test_settings.py -v
```

Esperado: todos os testes de settings passando.

- [ ] **Step 5: Commit**

```bash
git add requirements.txt app/core/settings.py tests/unit/test_settings.py
git commit -m "chore(deps): substitui face-recognition/dlib por insightface+onnxruntime"
```

---

## Task 3: Migration — limpar embeddings dlib incompatíveis

**Files:**
- Create: `app/db/migrations/migration_insightface.py`
- Create: `tests/unit/test_migration_insightface.py`

- [ ] **Step 1: Escrever teste que falha**

Criar `tests/unit/test_migration_insightface.py`:

```python
import numpy as np
import pytest
from pathlib import Path


def test_migration_deletes_128dim_npy(tmp_path):
    """Arquivos .npy com shape (128,) são deletados (dlib incompatível)."""
    npy = tmp_path / "1_embedding.npy"
    np.save(str(npy), np.zeros(128))

    from app.db.migrations.migration_insightface import run
    run(storage_dir=tmp_path)

    assert not npy.exists()


def test_migration_preserves_512dim_npy(tmp_path):
    """Arquivos .npy com shape (512,) são preservados (ArcFace compatível)."""
    npy = tmp_path / "1_embedding_0.npy"
    np.save(str(npy), np.zeros(512))

    from app.db.migrations.migration_insightface import run
    run(storage_dir=tmp_path)

    assert npy.exists()


def test_migration_preserves_jpg(tmp_path):
    """Arquivos .jpg nunca são deletados."""
    jpg = tmp_path / "1.jpg"
    jpg.write_bytes(b"\xff\xd8\xff")  # JPEG header

    from app.db.migrations.migration_insightface import run
    run(storage_dir=tmp_path)

    assert jpg.exists()


def test_migration_idempotent(tmp_path):
    """Rodar duas vezes não causa erro."""
    npy = tmp_path / "1_embedding.npy"
    np.save(str(npy), np.zeros(128))

    from app.db.migrations.migration_insightface import run
    run(storage_dir=tmp_path)
    run(storage_dir=tmp_path)  # segunda chamada: não deve explodir


def test_migration_handles_missing_directory(tmp_path):
    """Diretório inexistente não causa erro."""
    from app.db.migrations.migration_insightface import run
    run(storage_dir=tmp_path / "nonexistent")


def test_migration_deletes_old_single_embedding_npy(tmp_path):
    """Padrão antigo {id}_embedding.npy (sem índice) também é deletado se 128-dim."""
    npy = tmp_path / "42_embedding.npy"
    np.save(str(npy), np.zeros(128))

    from app.db.migrations.migration_insightface import run
    run(storage_dir=tmp_path)

    assert not npy.exists()
```

- [ ] **Step 2: Rodar para confirmar falha**

```bash
pytest tests/unit/test_migration_insightface.py -v
```

Esperado: `FAILED` — `ModuleNotFoundError: No module named 'app.db.migrations.migration_insightface'`

- [ ] **Step 3: Implementar `app/db/migrations/migration_insightface.py`**

```python
import logging
from pathlib import Path

import numpy as np

from app.core.settings import settings

logger = logging.getLogger(__name__)


def run(storage_dir: Path | None = None) -> None:
    """Remove embeddings dlib (128-dim) de storage_dir.

    Idempotente: arquivos já deletados ou inexistentes são ignorados.
    Preserva arquivos .jpg e embeddings ArcFace (512-dim) intactos.
    """
    dirs = [storage_dir] if storage_dir is not None else [
        settings.STORAGE_FACES,
        settings.STORAGE_EMPLOYEES,
    ]

    total_deleted = 0
    for directory in dirs:
        if not directory.exists():
            continue
        for npy_path in directory.glob("*.npy"):
            try:
                arr = np.load(str(npy_path))
                if arr.shape == (128,):
                    npy_path.unlink()
                    total_deleted += 1
                    logger.info("migration_insightface: removido %s (shape=128)", npy_path.name)
            except Exception:
                logger.warning("migration_insightface: falha ao inspecionar %s", npy_path, exc_info=True)

    logger.info("migration_insightface: %d arquivos dlib removidos", total_deleted)
```

- [ ] **Step 4: Rodar testes**

```bash
pytest tests/unit/test_migration_insightface.py -v
```

Esperado: 6 testes PASSED.

- [ ] **Step 5: Commit**

```bash
git add app/db/migrations/migration_insightface.py tests/unit/test_migration_insightface.py
git commit -m "feat(migrations): adiciona migration_insightface para limpar embeddings dlib 128-dim"
```

---

## Task 4: `face_service.py` — InsightFace (RetinaFace + ArcFace)

**Files:**
- Rewrite: `app/services/face_service.py`
- Rewrite: `tests/unit/test_face_service.py`

- [ ] **Step 1: Escrever testes que falham**

Substituir completamente `tests/unit/test_face_service.py`:

```python
from unittest.mock import MagicMock, patch

import numpy as np
import pytest

from app.core.settings import settings


def make_bgr_frame(h: int = 480, w: int = 640) -> np.ndarray:
    return np.zeros((h, w, 3), dtype=np.uint8)


def make_l2_embedding(dim: int = 512) -> np.ndarray:
    v = np.random.rand(dim).astype(np.float32)
    return v / np.linalg.norm(v)


def make_face_location(size: int = 120) -> tuple:
    """(top, right, bottom, left)"""
    return (0, size, size, 0)


def make_mock_face(
    bbox: list | None = None,
    det_score: float = 0.95,
    embedding: np.ndarray | None = None,
):
    face = MagicMock()
    face.bbox = np.array(bbox or [0, 0, 120, 120], dtype=np.float32)
    face.det_score = det_score
    face.embedding = embedding if embedding is not None else make_l2_embedding()
    return face


# ── is_good_quality_frame ─────────────────────────────────────────────────────

def test_is_good_quality_frame_rejects_small_face():
    from app.services.face_service import is_good_quality_frame

    frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    small_location = make_face_location(size=30)

    assert is_good_quality_frame(small_location, frame, min_face_size=60) is False


def test_is_good_quality_frame_rejects_blurred_face():
    from app.services.face_service import is_good_quality_frame

    blurred_frame = np.full((480, 640, 3), 128, dtype=np.uint8)
    location = make_face_location(size=120)

    assert is_good_quality_frame(location, blurred_frame, blur_threshold=100.0) is False


def test_is_good_quality_frame_accepts_sharp_large_face():
    from app.services.face_service import is_good_quality_frame

    frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    location = make_face_location(size=120)

    assert is_good_quality_frame(location, frame, min_face_size=60, blur_threshold=10.0) is True


def test_is_good_quality_frame_rejects_low_det_score():
    from app.services.face_service import is_good_quality_frame

    frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    location = make_face_location(size=120)

    assert is_good_quality_frame(location, frame, det_score=0.5, det_score_threshold=0.7) is False


def test_is_good_quality_frame_accepts_high_det_score():
    from app.services.face_service import is_good_quality_frame

    frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    location = make_face_location(size=120)

    assert is_good_quality_frame(location, frame, det_score=0.9, det_score_threshold=0.7, blur_threshold=10.0) is True


# ── extract_embeddings ────────────────────────────────────────────────────────

def test_extract_embeddings_no_face_returns_empty():
    from app.services.face_service import extract_embeddings

    with patch("app.services.face_service.get_face_app") as mock_get:
        mock_app = MagicMock()
        mock_app.get.return_value = []
        mock_get.return_value = mock_app

        result = extract_embeddings(make_bgr_frame())

    assert result == []


def test_extract_embeddings_one_face_returns_one_tuple():
    from app.services.face_service import extract_embeddings

    face = make_mock_face(bbox=[10, 10, 130, 130], det_score=0.95)

    with patch("app.services.face_service.get_face_app") as mock_get:
        mock_app = MagicMock()
        mock_app.get.return_value = [face]
        mock_get.return_value = mock_app

        result = extract_embeddings(make_bgr_frame())

    assert len(result) == 1
    embedding, location = result[0]
    assert embedding.shape == (512,)
    assert len(location) == 4  # (top, right, bottom, left)


def test_extract_embeddings_discards_low_det_score():
    from app.services.face_service import extract_embeddings

    face = make_mock_face(det_score=0.3)

    with patch("app.services.face_service.get_face_app") as mock_get:
        mock_app = MagicMock()
        mock_app.get.return_value = [face]
        mock_get.return_value = mock_app

        result = extract_embeddings(make_bgr_frame())

    assert result == []


def test_extract_embeddings_discards_small_face():
    from app.services.face_service import extract_embeddings

    # bbox pequeno: x1=0, y1=0, x2=20, y2=20 → width=20, height=20 < FACE_MIN_SIZE_PX
    face = make_mock_face(bbox=[0, 0, 20, 20], det_score=0.95)

    with patch("app.services.face_service.get_face_app") as mock_get:
        mock_app = MagicMock()
        mock_app.get.return_value = [face]
        mock_get.return_value = mock_app

        result = extract_embeddings(make_bgr_frame())

    assert result == []


def test_extract_embeddings_two_faces_returns_two():
    from app.services.face_service import extract_embeddings

    faces = [
        make_mock_face(bbox=[0, 0, 120, 120], det_score=0.95),
        make_mock_face(bbox=[200, 200, 320, 320], det_score=0.90),
    ]

    with patch("app.services.face_service.get_face_app") as mock_get:
        mock_app = MagicMock()
        mock_app.get.return_value = faces
        mock_get.return_value = mock_app

        result = extract_embeddings(make_bgr_frame())

    assert len(result) == 2


# ── bbox_to_location ──────────────────────────────────────────────────────────

def test_bbox_to_location_converts_correctly():
    from app.services.face_service import bbox_to_location

    # InsightFace bbox: [x1, y1, x2, y2]
    # Esperado: (top=y1, right=x2, bottom=y2, left=x1)
    location = bbox_to_location(np.array([10.0, 20.0, 110.0, 120.0]))
    assert location == (20, 110, 120, 10)


# ── find_matching_person (coseno) ─────────────────────────────────────────────

def test_find_matching_empty_list_returns_none():
    from app.services.face_service import find_matching_person

    result_id, result_dist = find_matching_person(make_l2_embedding(), [])
    assert result_id is None
    assert result_dist is None


def test_find_matching_below_tolerance_returns_match():
    from app.services.face_service import find_matching_person

    query = make_l2_embedding()
    known = [(1, query.copy())]  # distância coseno = 0.0

    match_id, dist = find_matching_person(query, known, tolerance=0.4)

    assert match_id == 1
    assert dist is not None
    assert dist < 0.01


def test_find_matching_above_tolerance_returns_none():
    from app.services.face_service import find_matching_person

    query = np.zeros(512, dtype=np.float32)
    query[0] = 1.0  # vetor unitário eixo 0

    opposite = np.zeros(512, dtype=np.float32)
    opposite[1] = 1.0  # vetor unitário eixo 1 — distância coseno = 1.0

    match_id, dist = find_matching_person(query, [(1, opposite)], tolerance=0.4)

    assert match_id is None


def test_find_matching_picks_closest():
    from app.services.face_service import find_matching_person

    query = np.zeros(512, dtype=np.float32)
    query[0] = 1.0

    close = np.zeros(512, dtype=np.float32)
    close[0] = 0.99
    close[1] = 0.01
    close = close / np.linalg.norm(close)

    far = np.zeros(512, dtype=np.float32)
    far[0] = 0.7
    far[1] = 0.3
    far = far / np.linalg.norm(far)

    match_id, dist = find_matching_person(query, [(1, close), (2, far)], tolerance=0.4)
    assert match_id == 1


def test_find_matching_knn_majority_vote():
    from app.services.face_service import find_matching_person

    query = np.zeros(512, dtype=np.float32)
    query[0] = 1.0

    # Pessoa 2 tem 2 embeddings próximos, pessoa 1 tem 1 mais próximo ainda
    emb_p1 = query.copy()  # distância 0.0
    emb_p2a = np.zeros(512, dtype=np.float32)
    emb_p2a[0] = 0.98
    emb_p2a[1] = 0.02
    emb_p2a = emb_p2a / np.linalg.norm(emb_p2a)

    emb_p2b = np.zeros(512, dtype=np.float32)
    emb_p2b[0] = 0.97
    emb_p2b[1] = 0.03
    emb_p2b = emb_p2b / np.linalg.norm(emb_p2b)

    known = [(1, emb_p1), (2, emb_p2a), (2, emb_p2b)]
    match_id, _ = find_matching_person(query, known, tolerance=0.4, k=3)
    # Pessoa 2 tem 2 votos vs 1 da pessoa 1 → deve vencer
    assert match_id == 2


# ── get_face_app singleton ────────────────────────────────────────────────────

def test_get_face_app_returns_same_instance():
    from app.services import face_service

    face_service._face_app = None  # reset singleton

    with patch("app.services.face_service.FaceAnalysis") as mock_cls:
        mock_instance = MagicMock()
        mock_cls.return_value = mock_instance

        app1 = face_service.get_face_app()
        app2 = face_service.get_face_app()

    assert app1 is app2
    assert mock_cls.call_count == 1


# ── FaceTrack / FaceTracker (sem mudança — smoke test) ───────────────────────

def test_face_tracker_aggregates_detections():
    from app.services.face_service import FaceTracker

    tracker = FaceTracker(gap_tolerance=2.0, min_samples=2)
    emb = make_l2_embedding()
    frame = make_bgr_frame()

    tracker.add_detection(emb, make_face_location(), frame, timestamp=1.0)
    tracker.add_detection(emb, make_face_location(), frame, timestamp=2.0)

    tracks = tracker.flush()
    assert len(tracks) == 1
    assert tracks[0].sample_count == 2


def test_face_tracker_discards_short_tracks():
    from app.services.face_service import FaceTracker

    tracker = FaceTracker(gap_tolerance=2.0, min_samples=2)
    emb = make_l2_embedding()
    frame = make_bgr_frame()

    tracker.add_detection(emb, make_face_location(), frame, timestamp=1.0)

    tracks = tracker.flush()
    assert len(tracks) == 0
```

- [ ] **Step 2: Rodar para confirmar falhas**

```bash
pytest tests/unit/test_face_service.py -v 2>&1 | head -40
```

Esperado: `FAILED` — vários erros de import e `AttributeError` (face_service ainda usa dlib).

- [ ] **Step 3: Reescrever `app/services/face_service.py`**

```python
import logging

import cv2
import numpy as np

from app.core.settings import settings

logger = logging.getLogger(__name__)

try:
    from insightface.app import FaceAnalysis
except ImportError:  # pragma: no cover
    FaceAnalysis = None  # type: ignore

_face_app = None


def get_face_app():
    global _face_app
    if _face_app is None:
        if FaceAnalysis is None:
            raise RuntimeError("insightface não está instalado")
        _face_app = FaceAnalysis(
            name=settings.INSIGHTFACE_MODEL,
            providers=["CoreMLExecutionProvider", "CPUExecutionProvider"],
        )
        _face_app.prepare(
            ctx_id=0,
            det_size=(settings.INSIGHTFACE_DET_SIZE, settings.INSIGHTFACE_DET_SIZE),
        )
        logger.info(
            "InsightFace inicializado: model=%s det_size=%d",
            settings.INSIGHTFACE_MODEL,
            settings.INSIGHTFACE_DET_SIZE,
        )
    return _face_app


def bbox_to_location(bbox: np.ndarray) -> tuple[int, int, int, int]:
    """Converte bbox InsightFace [x1,y1,x2,y2] → (top, right, bottom, left)."""
    x1, y1, x2, y2 = bbox
    return (int(y1), int(x2), int(y2), int(x1))


def is_good_quality_frame(
    location: tuple[int, int, int, int],
    frame: np.ndarray,
    min_face_size: int = settings.FACE_MIN_SIZE_PX,
    blur_threshold: float = settings.FACE_BLUR_THRESHOLD,
    det_score: float = 1.0,
    det_score_threshold: float = settings.INSIGHTFACE_DET_SCORE,
) -> bool:
    top, right, bottom, left = location
    width = right - left
    height = bottom - top

    if width < min_face_size or height < min_face_size:
        return False

    if det_score < det_score_threshold:
        return False

    face_crop = frame[top:bottom, left:right]
    if face_crop.size == 0:
        return False
    gray = cv2.cvtColor(face_crop, cv2.COLOR_BGR2GRAY)
    variance = cv2.Laplacian(gray, cv2.CV_64F).var()

    return bool(variance >= blur_threshold)


def extract_embeddings(frame: np.ndarray) -> list[tuple[np.ndarray, tuple]]:
    app = get_face_app()
    faces = app.get(frame)

    logger.debug("[EXTRACT] faces_detectadas=%d", len(faces))

    result = []
    for face in faces:
        location = bbox_to_location(face.bbox)
        if not is_good_quality_frame(
            location,
            frame,
            det_score=float(face.det_score),
        ):
            continue
        result.append((face.embedding, location))

    logger.debug(
        "[EXTRACT] faces_boa_qualidade=%d descartadas=%d",
        len(result),
        len(faces) - len(result),
    )
    return result


class FaceTrack:
    """Agrega detecções de uma mesma aparição contínua de rosto no vídeo."""

    def __init__(self, start_time: float):
        self.start_time = start_time
        self.last_seen = start_time
        self.embeddings: list[np.ndarray] = []
        self._frames_data: list[dict] = []

    def add_frame_data(
        self,
        embedding: np.ndarray,
        location: tuple[int, int, int, int],
        frame: np.ndarray,
        timestamp: float,
    ) -> None:
        self.embeddings.append(embedding)
        self._frames_data.append(
            {"location": location, "frame": frame, "timestamp": timestamp}
        )
        self.last_seen = timestamp

    @property
    def sample_count(self) -> int:
        return len(self.embeddings)

    def mean_embedding(self) -> np.ndarray:
        mean = np.mean(self.embeddings, axis=0).astype(np.float32)
        norm = np.linalg.norm(mean)
        return mean / norm if norm > 0 else mean

    def get_best_crop(self) -> np.ndarray:
        def face_area(data: dict) -> int:
            top, right, bottom, left = data["location"]
            return (right - left) * (bottom - top)

        best = max(self._frames_data, key=face_area)
        top, right, bottom, left = best["location"]
        return best["frame"][top:bottom, left:right]


class FaceTracker:
    """Agrupa detecções consecutivas em tracks, descartando aparições muito curtas."""

    def __init__(
        self,
        gap_tolerance: float = settings.FACE_TRACK_GAP_TOLERANCE,
        min_samples: int = settings.FACE_TRACK_MIN_SAMPLES,
    ):
        self.gap_tolerance = gap_tolerance
        self.min_samples = min_samples
        self.active_track: FaceTrack | None = None
        self.closed_tracks: list[FaceTrack] = []

    def add_detection(
        self,
        embedding: np.ndarray,
        location: tuple[int, int, int, int],
        frame: np.ndarray,
        timestamp: float,
    ) -> None:
        if self.active_track is None:
            self.active_track = FaceTrack(start_time=timestamp)
        elif timestamp - self.active_track.last_seen > self.gap_tolerance:
            self._close_active_track()
            self.active_track = FaceTrack(start_time=timestamp)

        self.active_track.add_frame_data(embedding, location, frame, timestamp)

    def _close_active_track(self) -> None:
        if (
            self.active_track is not None
            and self.active_track.sample_count >= self.min_samples
        ):
            self.closed_tracks.append(self.active_track)
            logger.debug(
                "[TRACKER] track fechado start=%.1fs last_seen=%.1fs samples=%d",
                self.active_track.start_time,
                self.active_track.last_seen,
                self.active_track.sample_count,
            )
        elif self.active_track is not None:
            logger.debug(
                "[TRACKER] track descartado samples=%d < min_samples=%d",
                self.active_track.sample_count,
                self.min_samples,
            )
        self.active_track = None

    def flush(self) -> list[FaceTrack]:
        self._close_active_track()
        return self.closed_tracks


def find_matching_person(
    embedding: np.ndarray,
    known_embeddings: list[tuple[int, np.ndarray]],
    tolerance: float = settings.FACE_RECOGNITION_TOLERANCE,
    k: int = settings.FACE_KNN_K,
) -> tuple[int | None, float | None]:
    """Vota entre os k vizinhos mais próximos usando distância coseno.

    ArcFace embeddings são L2-normalizados → coseno = 1 - dot(a, b).
    """
    if not known_embeddings:
        return None, None

    known_vecs = np.array([emb for _, emb in known_embeddings], dtype=np.float32)
    person_ids = [pid for pid, _ in known_embeddings]

    q = embedding.astype(np.float32)
    q_norm = np.linalg.norm(q)
    if q_norm > 0:
        q = q / q_norm

    dots = known_vecs @ q
    distances = (1.0 - dots).tolist()

    logger.debug(
        "[MATCH] comparando contra %d embeddings k=%d threshold=%.4f",
        len(known_vecs),
        k,
        tolerance,
    )

    candidates = sorted(zip(person_ids, distances), key=lambda pair: pair[1])
    within_tolerance = [
        (pid, float(dist)) for pid, dist in candidates if dist <= tolerance
    ]

    if not within_tolerance:
        logger.info(
            "[MATCH REJEITADO] melhor_distancia=%.4f > threshold=%.4f → nova_pessoa",
            float(candidates[0][1]),
            tolerance,
        )
        return None, None

    top_k = within_tolerance[:k]
    votes: dict[int, list[float]] = {}
    for pid, dist in top_k:
        votes.setdefault(pid, []).append(dist)

    winner_id, winner_votes = max(
        votes.items(), key=lambda item: (len(item[1]), -min(item[1]))
    )
    winner_dist = min(winner_votes)

    logger.info(
        "[MATCH ACEITO] person_id=%d distancia=%.4f votos=%d/%d threshold=%.4f",
        winner_id,
        winner_dist,
        len(winner_votes),
        len(top_k),
        tolerance,
    )
    return winner_id, winner_dist
```

- [ ] **Step 4: Rodar testes**

```bash
pytest tests/unit/test_face_service.py -v
```

Esperado: todos os testes PASSED.

- [ ] **Step 5: Commit**

```bash
git add app/services/face_service.py tests/unit/test_face_service.py
git commit -m "feat(face): substitui dlib por InsightFace (RetinaFace + ArcFace 512-dim coseno)"
```

---

## Task 5: `person_service.py` — multi-embedding por pessoa

**Files:**
- Modify: `app/services/person_service.py`
- Test: `tests/unit/test_person_service.py`

- [ ] **Step 1: Escrever testes que falham**

Adicionar ao final de `tests/unit/test_person_service.py`:

```python
def test_get_all_embeddings_loads_multiple_npy_per_person(tmp_path, monkeypatch):
    """get_all_embeddings carrega todos os embedding_*.npy de cada pessoa."""
    import numpy as np
    from unittest.mock import MagicMock, patch
    from app.services.person_service import get_all_embeddings

    # Dois embeddings ArcFace para pessoa id=1
    (tmp_path / "1_embedding_0.npy").parent.mkdir(parents=True, exist_ok=True)
    np.save(str(tmp_path / "1_embedding_0.npy"), np.ones(512, dtype=np.float32))
    np.save(str(tmp_path / "1_embedding_1.npy"), np.zeros(512, dtype=np.float32))

    monkeypatch.setattr("app.services.person_service.settings.STORAGE_FACES", tmp_path)

    mock_person = MagicMock()
    mock_person.id = 1

    mock_db = MagicMock()
    mock_db.query.return_value.all.return_value = [mock_person]

    result = get_all_embeddings(mock_db)

    assert len(result) == 2
    assert all(pid == 1 for pid, _ in result)


def test_get_all_embeddings_skips_legacy_single_npy_if_128dim(tmp_path, monkeypatch):
    """Embedding antigo {id}_embedding.npy com shape (128,) é ignorado."""
    import numpy as np
    from unittest.mock import MagicMock
    from app.services.person_service import get_all_embeddings

    np.save(str(tmp_path / "1_embedding.npy"), np.zeros(128, dtype=np.float32))

    monkeypatch.setattr("app.services.person_service.settings.STORAGE_FACES", tmp_path)

    mock_person = MagicMock()
    mock_person.id = 1
    mock_db = MagicMock()
    mock_db.query.return_value.all.return_value = [mock_person]

    result = get_all_embeddings(mock_db)
    assert result == []


def test_save_new_person_creates_embedding_0_npy(tmp_path, monkeypatch):
    """save_new_person grava {id}_embedding_0.npy (não {id}_embedding.npy)."""
    import numpy as np
    from unittest.mock import MagicMock
    from app.services.person_service import save_new_person

    monkeypatch.setattr("app.services.person_service.settings.STORAGE_FACES", tmp_path)

    embedding = np.ones(512, dtype=np.float32)
    face_crop = np.zeros((80, 80, 3), dtype=np.uint8)

    mock_person = MagicMock()
    mock_person.id = 7
    mock_db = MagicMock()
    mock_db.get.return_value = mock_person
    mock_db.refresh.side_effect = lambda p: None

    with patch("app.services.person_service.Person") as MockPerson:
        MockPerson.return_value = mock_person

        def fake_commit():
            pass
        mock_db.commit.side_effect = fake_commit
        mock_db.refresh.side_effect = lambda p: None

        save_new_person(mock_db, embedding, face_crop, person_index=7)

    assert (tmp_path / "7_embedding_0.npy").exists()
    assert not (tmp_path / "7_embedding.npy").exists()
```

- [ ] **Step 2: Rodar para confirmar falhas**

```bash
pytest tests/unit/test_person_service.py::test_get_all_embeddings_loads_multiple_npy_per_person tests/unit/test_person_service.py::test_get_all_embeddings_skips_legacy_single_npy_if_128dim tests/unit/test_person_service.py::test_save_new_person_creates_embedding_0_npy -v
```

Esperado: `FAILED`

- [ ] **Step 3: Atualizar `get_all_embeddings` em `person_service.py`**

Substituir a função `get_all_embeddings`:

```python
def get_all_embeddings(db: Session) -> list[tuple[int, np.ndarray]]:
    people = db.query(Person).all()
    result: list[tuple[int, np.ndarray]] = []
    for person in people:
        npy_files = sorted(settings.STORAGE_FACES.glob(f"{person.id}_embedding_*.npy"))
        if not npy_files:
            logger.warning(
                "Nenhum embedding encontrado para pessoa id=%s", person.id
            )
            continue
        for npy_path in npy_files:
            try:
                embedding = np.load(str(npy_path))
                if embedding.shape != (512,):
                    logger.warning(
                        "Embedding com shape inesperado %s ignorado: %s",
                        embedding.shape,
                        npy_path.name,
                    )
                    continue
                result.append((person.id, embedding))
            except Exception:
                logger.warning("Falha ao carregar %s", npy_path, exc_info=True)
    logger.info("[EMBEDDINGS TOTAIS] carregados=%d", len(result))
    return result
```

- [ ] **Step 4: Atualizar `save_new_person` — gravar como `_embedding_0.npy`**

Substituir as linhas de gravação do `.npy` dentro de `save_new_person`:

```python
    jpg_path = settings.STORAGE_FACES / f"{person.id}.jpg"
    npy_path = settings.STORAGE_FACES / f"{person.id}_embedding_0.npy"

    cv2.imwrite(str(jpg_path), face_crop)
    np.save(str(npy_path), embedding)
```

- [ ] **Step 5: Atualizar `save_face_sample` — adicionar embedding adicional quando há qualidade**

Substituir a função `save_face_sample`:

```python
MAX_FACE_SAMPLES = 10


def save_face_sample(
    db: Session,
    person_id: int,
    appearance_id: int,
    face_crop: np.ndarray,
    embedding: np.ndarray | None = None,
) -> str | None:
    """Salva recorte facial como amostra adicional. Se embedding ArcFace fornecido
    e o total for menor que FACE_MAX_EMBEDDINGS_PER_PERSON, grava embedding adicional.
    """
    try:
        existing = list(settings.STORAGE_FACES.glob(f"{person_id}_sample_*.jpg"))
        if len(existing) >= MAX_FACE_SAMPLES:
            return None

        sample_path = settings.STORAGE_FACES / f"{person_id}_sample_{appearance_id}.jpg"
        cv2.imwrite(str(sample_path), face_crop)

        if embedding is not None:
            existing_embs = list(
                settings.STORAGE_FACES.glob(f"{person_id}_embedding_*.npy")
            )
            if len(existing_embs) < settings.FACE_MAX_EMBEDDINGS_PER_PERSON:
                idx = len(existing_embs)
                emb_path = settings.STORAGE_FACES / f"{person_id}_embedding_{idx}.npy"
                np.save(str(emb_path), embedding.astype(np.float32))
                logger.debug(
                    "Embedding adicional salvo: %s (total=%d)",
                    emb_path.name,
                    idx + 1,
                )

        return str(sample_path)
    except Exception:
        logger.warning(
            "Falha ao salvar amostra facial para pessoa id=%s", person_id, exc_info=True
        )
        return None
```

- [ ] **Step 6: Atualizar `merge_people` — limpar padrão `_embedding_*.npy`**

Dentro do loop de `secondary_ids`, substituir o trecho de remoção de arquivos:

```python
        # Remover embeddings e foto principal do secundário
        for npy_path in settings.STORAGE_FACES.glob(f"{sec_id}_embedding_*.npy"):
            npy_path.unlink(missing_ok=True)
            logger.info("merge_people: removido %s", npy_path)
        for suffix in (f"{sec_id}.jpg",):
            path = settings.STORAGE_FACES / suffix
            if path.exists():
                path.unlink()
                logger.info("merge_people: removido %s", path)
```

- [ ] **Step 7: Rodar testes**

```bash
pytest tests/unit/test_person_service.py -v
```

Esperado: todos os testes PASSED.

- [ ] **Step 8: Commit**

```bash
git add app/services/person_service.py tests/unit/test_person_service.py
git commit -m "feat(person): suporte a múltiplos embeddings ArcFace por pessoa (até 5)"
```

---

## Task 6: `video_worker.py` — passar embedding ao `save_face_sample`

**Files:**
- Modify: `app/workers/video_worker.py`

O worker precisa passar o embedding do track para `save_face_sample` para que o multi-embedding funcione. Também remove `get_adaptive_params` que usava parâmetros dlib removidos.

- [ ] **Step 1: Atualizar `_process_track` em `video_worker.py`**

Na função `_process_track`, alterar a chamada de `save_face_sample`:

```python
    person_service.save_face_sample(
        db,
        person_id=person_id,
        appearance_id=appearance.id,
        face_crop=best_crop,
        embedding=mean_embedding,
    )
```

- [ ] **Step 2: Remover `get_adaptive_params`**

Deletar a função `get_adaptive_params` inteira (linhas que definem e retornam dict com `CNN_*` settings). O worker não usa mais parâmetros adaptativos de upsample — o InsightFace gerencia internamente.

- [ ] **Step 3: Verificar que worker ainda importa sem erro**

```bash
python -c "from app.workers.video_worker import process_video; print('OK')"
```

Esperado: `OK`

- [ ] **Step 4: Rodar testes de integração do worker**

```bash
pytest tests/integration/test_video_worker.py -v
```

Os mocks existentes mockam `face_service.extract_embeddings` diretamente — devem continuar funcionando. Se algum teste mocka `face_recognition` diretamente, atualizar para mockar `face_service.get_face_app`.

- [ ] **Step 5: Commit**

```bash
git add app/workers/video_worker.py
git commit -m "refactor(worker): passa embedding ArcFace ao save_face_sample; remove get_adaptive_params obsoleto"
```

---

## Task 7: `main.py` — migration + pre-warm InsightFace no lifespan

**Files:**
- Modify: `app/main.py`

- [ ] **Step 1: Adicionar import da migration**

No bloco de imports das migrations:

```python
from app.db.migrations.migration_insightface import run as migration_insightface
```

- [ ] **Step 2: Atualizar a função `lifespan`**

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    migration_insightface()
    init_db()
    migration_v1_13()
    migration_v1_20()
    migration_v1_30()
    migration_v1_35()
    migration_v1_40()
    from app.services import face_service
    face_service.get_face_app()   # pre-warm: carrega buffalo_l antes do primeiro vídeo
    ws_manager.set_loop(asyncio.get_event_loop())
    yield
```

> `migration_insightface()` **antes** de `init_db()` garante que embeddings incompatíveis sejam removidos antes de qualquer acesso.

- [ ] **Step 3: Verificar startup sem erro**

```bash
python -c "
import asyncio
from contextlib import asynccontextmanager
from app.main import app
print('import OK')
"
```

Esperado: `import OK` (InsightFace vai logar o download do modelo se for a primeira vez).

- [ ] **Step 4: Commit**

```bash
git add app/main.py
git commit -m "feat(main): adiciona migration_insightface e pre-warm InsightFace no lifespan"
```

---

## Task 8: Verificação final e changelog

- [ ] **Step 1: Rodar suíte completa**

```bash
pytest -v --tb=short 2>&1 | tail -20
```

Esperado: todos os testes PASSED. Se algum teste de integração ainda referencia `face_recognition` diretamente, substituir o mock:

```python
# ANTES:
with patch("face_recognition.face_locations", return_value=[...]):
    ...

# DEPOIS:
with patch("app.services.face_service.get_face_app") as mock_get:
    mock_app = MagicMock()
    mock_app.get.return_value = [make_mock_face(...)]
    mock_get.return_value = mock_app
    ...
```

- [ ] **Step 2: Criar fragmento de changelog**

Criar `changelog/changelog_v1.97-2026-06-08-insightface-retinaface-arcface.md`:

```markdown
## v1.97.0 — 2026-06-08

### Tipo da mudança
feat

### Arquivos alterados
- requirements.txt
- app/core/settings.py
- app/db/migrations/migration_insightface.py
- app/services/face_service.py
- app/services/person_service.py
- app/workers/video_worker.py
- app/main.py
- tests/unit/test_face_service.py
- tests/unit/test_person_service.py
- tests/unit/test_migration_insightface.py
- tests/unit/test_settings.py

### Impacto técnico/funcional
Substitui dlib/face_recognition por InsightFace buffalo_l (RetinaFace + ArcFace).
- RetinaFace detecta rostos pequenos, de perfil e em câmeras de segurança que o dlib CNN perdia.
- ArcFace 512-dim embeddings com distância coseno reduzem falsos positivos e negativos.
- ONNX Runtime com CoreML execution provider aproveita o M4 Neural Engine.
- Suporte a múltiplos embeddings por pessoa (até 5) melhora cobertura de pose/iluminação.
- Migration automática remove embeddings dlib 128-dim incompatíveis no startup.
- FACE_RECOGNITION_TOLERANCE muda de 0.6 (euclidiana) para 0.4 (coseno).
```

- [ ] **Step 3: Commit final**

```bash
git add changelog/changelog_v1.97-2026-06-08-insightface-retinaface-arcface.md
git commit -m "feat(face): migra para InsightFace RetinaFace+ArcFace — melhoria de acurácia (v1.97.0)"
git push
```
