import numpy as np
import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.models import Base, Person


@pytest.fixture
def db():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    engine.dispose()


def _l2(v: np.ndarray) -> np.ndarray:
    return (v / np.linalg.norm(v)).astype(np.float32)


def make_face(bbox: list[float], embedding: np.ndarray):
    face = MagicMock()
    face.bbox = np.array(bbox, dtype=np.float32)
    face.embedding = _l2(embedding)
    return face


FAKE_FRAME = np.zeros((480, 640, 3), dtype=np.uint8)


def _patch_imdecode(frame=FAKE_FRAME):
    return patch("app.services.search_service.cv2.imdecode", return_value=frame)


def _patch_face_app(faces: list):
    mock_app = MagicMock()
    mock_app.get.return_value = faces
    return patch("app.services.search_service.get_face_app", return_value=mock_app)


def test_imagem_sem_face_retorna_lista_vazia(db):
    from app.services.search_service import search_by_face

    with _patch_imdecode(), _patch_face_app([]):
        result = search_by_face(db, b"fake_image_bytes")

    assert result == []


def test_imagem_invalida_retorna_lista_vazia(db):
    from app.services.search_service import search_by_face

    with _patch_imdecode(None):
        result = search_by_face(db, b"bad_bytes")

    assert result == []


def test_imagem_com_face_retorna_resultados_por_distancia_asc(db):
    from app.services.search_service import search_by_face

    p1 = Person(name="Alice", profile_image_path="faces/1.jpg")
    p2 = Person(name="Bob", profile_image_path="faces/2.jpg")
    db.add_all([p1, p2])
    db.commit()

    # query ≈ [1,0,...], emb1 closer, emb2 further
    query_raw = np.zeros(512, dtype=np.float32); query_raw[0] = 1.0
    emb1 = _l2(np.full(512, 0.99)); emb1[0] += 0.1; emb1 = _l2(emb1)
    emb2 = _l2(np.full(512, 0.1))  # more orthogonal

    face = make_face([0, 0, 120, 120], query_raw)

    with _patch_imdecode(), _patch_face_app([face]), \
         patch("app.services.search_service.person_service.get_all_embeddings",
               return_value=[(p1.id, emb1), (p2.id, emb2)]):
        result = search_by_face(db, b"fake", tolerance=1.0)

    assert len(result) == 2
    assert result[0]["distance"] <= result[1]["distance"]


def test_resultados_acima_do_tolerance_excluidos(db):
    from app.services.search_service import search_by_face

    p = Person(name="Alice", profile_image_path="faces/1.jpg")
    db.add(p)
    db.commit()

    query_raw = np.zeros(512, dtype=np.float32); query_raw[0] = 1.0
    # orthogonal → cosine dist = 1.0
    known_emb = np.zeros(512, dtype=np.float32); known_emb[1] = 1.0

    face = make_face([0, 0, 120, 120], query_raw)

    with _patch_imdecode(), _patch_face_app([face]), \
         patch("app.services.search_service.person_service.get_all_embeddings",
               return_value=[(p.id, known_emb)]):
        result = search_by_face(db, b"fake", tolerance=0.4)

    assert result == []


def test_confidence_pct_calculado_corretamente(db):
    from app.services.search_service import search_by_face

    p = Person(name="Alice", profile_image_path="faces/1.jpg")
    db.add(p)
    db.commit()

    # cosine dist = 0.3 → confidence_pct = 70
    # query=[1,0,...], known=[0.7, sqrt(0.51), 0,...] → ||known||=1, dot=0.7, dist=0.3
    query_raw = np.zeros(512, dtype=np.float32); query_raw[0] = 1.0
    known_raw = np.zeros(512, dtype=np.float32)
    known_raw[0] = 0.7; known_raw[1] = (1 - 0.49) ** 0.5
    known_emb = _l2(known_raw)

    face = make_face([0, 0, 120, 120], query_raw)

    with _patch_imdecode(), _patch_face_app([face]), \
         patch("app.services.search_service.person_service.get_all_embeddings",
               return_value=[(p.id, known_emb)]):
        result = search_by_face(db, b"fake", tolerance=1.0)

    # int((1 - cosine_dist) * 100) ≈ 70; allow ±1 for float32 precision
    assert abs(result[0]["confidence_pct"] - 70) <= 1


def test_top_k_limita_numero_de_resultados(db):
    from app.services.search_service import search_by_face

    people = [Person(name=f"P{i}", profile_image_path=f"faces/{i}.jpg") for i in range(6)]
    db.add_all(people)
    db.commit()

    query_raw = np.zeros(512, dtype=np.float32); query_raw[0] = 1.0
    face = make_face([0, 0, 120, 120], query_raw)

    rng = np.random.default_rng(0)
    embs = [(p.id, _l2(rng.random(512).astype(np.float32))) for p in people]

    with _patch_imdecode(), _patch_face_app([face]), \
         patch("app.services.search_service.person_service.get_all_embeddings",
               return_value=embs):
        result = search_by_face(db, b"fake", top_k=3, tolerance=1.0)

    assert len(result) == 3


def test_multiplas_faces_usa_maior_area(db):
    from app.services.search_service import search_by_face

    p = Person(name="Alice", profile_image_path="faces/1.jpg")
    db.add(p)
    db.commit()

    # small face: bbox 10x10, big face: 100x100
    small_raw = np.zeros(512, dtype=np.float32); small_raw[1] = 1.0  # orthogonal → dist=1.0
    big_raw = np.zeros(512, dtype=np.float32); big_raw[0] = 1.0      # identical → dist≈0

    known_emb = np.zeros(512, dtype=np.float32); known_emb[0] = 1.0  # matches big face

    face_small = make_face([0, 0, 10, 10], small_raw)
    face_big = make_face([0, 0, 100, 100], big_raw)

    with _patch_imdecode(), _patch_face_app([face_small, face_big]), \
         patch("app.services.search_service.person_service.get_all_embeddings",
               return_value=[(p.id, known_emb)]):
        result = search_by_face(db, b"fake", tolerance=0.1)

    # big face matches (dist≈0), small face would not (dist=1.0 > 0.1)
    assert len(result) == 1
    assert result[0]["distance"] == pytest.approx(0.0, abs=1e-5)
