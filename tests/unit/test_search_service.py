import numpy as np
import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.models import Base, Person
from app.core.settings import settings


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


FAKE_EMBEDDING = np.array([0.1] * 128, dtype=np.float64)
FAKE_FRAME = np.zeros((480, 640, 3), dtype=np.uint8)
FAKE_RGB = np.zeros((480, 640, 3), dtype=np.uint8)


def _mock_cv2():
    return (
        patch("app.services.search_service.cv2.imdecode", return_value=FAKE_FRAME),
        patch("app.services.search_service.cv2.cvtColor", return_value=FAKE_RGB),
    )


def test_imagem_sem_face_retorna_lista_vazia(db):
    from app.services.search_service import search_by_face
    p1, p2 = _mock_cv2()
    with p1, p2, patch("app.services.face_service.extract_embeddings", return_value=[]):
        result = search_by_face(db, b"fake_image_bytes")
    assert result == []


def test_imagem_com_face_retorna_resultados_por_distancia_asc(db):
    from app.services.search_service import search_by_face
    p1 = Person(name="Alice", profile_image_path="faces/1.jpg")
    p2 = Person(name="Bob", profile_image_path="faces/2.jpg")
    db.add_all([p1, p2])
    db.commit()

    emb1 = np.array([0.1] * 128)
    emb2 = np.array([0.9] * 128)
    query_emb = np.array([0.3] * 128)  # dist1 = sqrt(128 * 0.2^2) ≈ 2.26, dist2 = sqrt(128 * 0.6^2) ≈ 6.78

    cv1, cv2p = _mock_cv2()
    with cv1, cv2p, \
         patch("app.services.face_service.extract_embeddings", return_value=[(query_emb, (0, 100, 100, 0))]), \
         patch("app.services.search_service.person_service.get_all_embeddings",
               return_value=[(p1.id, emb1), (p2.id, emb2)]):

        result = search_by_face(db, b"fake", tolerance=10.0)

    assert len(result) == 2
    assert result[0]["distance"] <= result[1]["distance"]
    assert result[0]["person_id"] == p1.id


def test_resultados_acima_do_tolerance_excluidos(db):
    from app.services.search_service import search_by_face
    p = Person(name="Alice", profile_image_path="faces/1.jpg")
    db.add(p)
    db.commit()

    emb = np.array([0.1] * 128)
    query_emb = np.array([0.9] * 128)

    cv1, cv2p = _mock_cv2()
    with cv1, cv2p, \
         patch("app.services.face_service.extract_embeddings", return_value=[(query_emb, (0, 100, 100, 0))]), \
         patch("app.services.search_service.person_service.get_all_embeddings",
               return_value=[(p.id, emb)]):

        result = search_by_face(db, b"fake", tolerance=1.0)

    assert result == []


def test_confidence_pct_calculado_corretamente(db):
    from app.services.search_service import search_by_face
    p = Person(name="Alice", profile_image_path="faces/1.jpg")
    db.add(p)
    db.commit()

    emb = np.array([0.1] * 128)
    query_emb = np.array([0.1] * 128)  # dist = 0.0

    cv1, cv2p = _mock_cv2()
    with cv1, cv2p, \
         patch("app.services.face_service.extract_embeddings", return_value=[(query_emb, (0, 100, 100, 0))]), \
         patch("app.services.search_service.person_service.get_all_embeddings",
               return_value=[(p.id, emb)]):

        result = search_by_face(db, b"fake", tolerance=1.0)

    assert result[0]["confidence_pct"] == 100  # 1.0 - 0.0 * 100 = 100


def test_top_k_limita_numero_de_resultados(db):
    from app.services.search_service import search_by_face
    people = [Person(name=f"P{i}", profile_image_path=f"faces/{i}.jpg") for i in range(6)]
    db.add_all(people)
    db.commit()

    # Todos com o mesmo embedding
    embs = [(p.id, np.array([0.1] * 128)) for p in people]
    query_emb = np.array([0.1] * 128)

    cv1, cv2p = _mock_cv2()
    with cv1, cv2p, \
         patch("app.services.face_service.extract_embeddings", return_value=[(query_emb, (0, 100, 100, 0))]), \
         patch("app.services.search_service.person_service.get_all_embeddings",
               return_value=embs):

        result = search_by_face(db, b"fake", top_k=3, tolerance=1.0)

    assert len(result) == 3


def test_multiplas_faces_usa_maior_area(db):
    from app.services.search_service import search_by_face
    p = Person(name="Alice", profile_image_path="faces/1.jpg")
    db.add(p)
    db.commit()

    emb = np.array([0.1] * 128)
    small_emb = np.array([0.5] * 128)
    big_emb = np.array([0.1] * 128)

    # face_locations: (top, right, bottom, left) — área = (bottom-top)*(right-left)
    # face pequena: 10x10=100, face grande: 100x100=10000
    loc_small = (0, 10, 10, 0)
    loc_big = (0, 100, 100, 0)

    cv1, cv2p = _mock_cv2()
    with cv1, cv2p, \
         patch("app.services.face_service.extract_embeddings", return_value=[(small_emb, loc_small), (big_emb, loc_big)]), \
         patch("app.services.search_service.person_service.get_all_embeddings",
               return_value=[(p.id, emb)]):

        result = search_by_face(db, b"fake", tolerance=1.0)

    assert len(result) == 1
    # Deve usar big_emb (distancia 0.0)
    assert result[0]["distance"] == pytest.approx(0.0)
