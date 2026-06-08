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

_CV2_PATCH = {
    "cv2_imdecode": patch("app.services.search_service.cv2.imdecode", return_value=FAKE_FRAME),
    "cv2_cvtColor": patch("app.services.search_service.cv2.cvtColor", return_value=FAKE_RGB),
}


def _mock_cv2():
    return (
        patch("app.services.search_service.cv2.imdecode", return_value=FAKE_FRAME),
        patch("app.services.search_service.cv2.cvtColor", return_value=FAKE_RGB),
    )


def test_imagem_sem_face_retorna_lista_vazia(db):
    from app.services.search_service import search_by_face
    p1, p2 = _mock_cv2()
    with p1, p2, patch("app.services.search_service.face_recognition") as mock_fr:
        mock_fr.face_locations.return_value = []
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
    query_emb = np.array([0.15] * 128)

    cv1, cv2p = _mock_cv2()
    with cv1, cv2p, \
         patch("app.services.search_service.face_recognition") as mock_fr, \
         patch("app.services.search_service.person_service.get_all_embeddings",
               return_value=[(p1.id, emb1), (p2.id, emb2)]):
        mock_fr.face_locations.return_value = [(0, 100, 100, 0)]
        mock_fr.face_encodings.return_value = [query_emb]
        distances = np.array([0.2, 0.8])
        mock_fr.face_distance.return_value = distances

        result = search_by_face(db, b"fake", tolerance=1.0)

    assert len(result) == 2
    assert result[0]["distance"] <= result[1]["distance"]


def test_resultados_acima_do_tolerance_excluidos(db):
    from app.services.search_service import search_by_face
    p = Person(name="Alice", profile_image_path="faces/1.jpg")
    db.add(p)
    db.commit()

    emb = np.array([0.1] * 128)
    query_emb = np.array([0.9] * 128)

    cv1, cv2p = _mock_cv2()
    with cv1, cv2p, \
         patch("app.services.search_service.face_recognition") as mock_fr, \
         patch("app.services.search_service.person_service.get_all_embeddings",
               return_value=[(p.id, emb)]):
        mock_fr.face_locations.return_value = [(0, 100, 100, 0)]
        mock_fr.face_encodings.return_value = [query_emb]
        mock_fr.face_distance.return_value = np.array([0.8])

        result = search_by_face(db, b"fake", tolerance=0.6)

    assert result == []


def test_confidence_pct_calculado_corretamente(db):
    from app.services.search_service import search_by_face
    p = Person(name="Alice", profile_image_path="faces/1.jpg")
    db.add(p)
    db.commit()

    emb = np.array([0.1] * 128)
    query_emb = np.array([0.2] * 128)

    cv1, cv2p = _mock_cv2()
    with cv1, cv2p, \
         patch("app.services.search_service.face_recognition") as mock_fr, \
         patch("app.services.search_service.person_service.get_all_embeddings",
               return_value=[(p.id, emb)]):
        mock_fr.face_locations.return_value = [(0, 100, 100, 0)]
        mock_fr.face_encodings.return_value = [query_emb]
        mock_fr.face_distance.return_value = np.array([0.3])

        result = search_by_face(db, b"fake", tolerance=1.0)

    assert result[0]["confidence_pct"] == 70  # int((1 - 0.3) * 100)


def test_top_k_limita_numero_de_resultados(db):
    from app.services.search_service import search_by_face
    people = [Person(name=f"P{i}", profile_image_path=f"faces/{i}.jpg") for i in range(6)]
    db.add_all(people)
    db.commit()

    embs = [(p.id, np.random.rand(128)) for p in people]
    query_emb = np.random.rand(128)
    distances = np.linspace(0.1, 0.5, len(people))

    cv1, cv2p = _mock_cv2()
    with cv1, cv2p, \
         patch("app.services.search_service.face_recognition") as mock_fr, \
         patch("app.services.search_service.person_service.get_all_embeddings",
               return_value=embs):
        mock_fr.face_locations.return_value = [(0, 100, 100, 0)]
        mock_fr.face_encodings.return_value = [query_emb]
        mock_fr.face_distance.return_value = distances

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
    locs = [(0, 10, 10, 0), (0, 100, 100, 0)]

    cv1, cv2p = _mock_cv2()
    with cv1, cv2p, \
         patch("app.services.search_service.face_recognition") as mock_fr, \
         patch("app.services.search_service.person_service.get_all_embeddings",
               return_value=[(p.id, emb)]):
        mock_fr.face_locations.return_value = locs
        mock_fr.face_encodings.return_value = [small_emb, big_emb]
        mock_fr.face_distance.return_value = np.array([0.05])

        result = search_by_face(db, b"fake", tolerance=1.0)

    assert len(result) == 1
    assert result[0]["distance"] == pytest.approx(0.05)
