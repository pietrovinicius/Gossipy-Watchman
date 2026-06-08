import io
import os
import numpy as np
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.session import get_db
from app.models import Base, Person
from app.services.auth_service import create_access_token


@pytest.fixture
def client_with_db():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)

    def override_get_db():
        db = Session()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    token = create_access_token({"sub": "testuser"})
    client = TestClient(app)
    yield client, Session, token
    app.dependency_overrides.clear()
    engine.dispose()


def _fake_jpeg() -> bytes:
    return b"\xff\xd8\xff\xe0" + b"\x00" * 100


def test_search_sem_auth_retorna_401(client_with_db):
    client, _, _ = client_with_db
    response = client.post(
        "/api/v1/search/by-face",
        files={"file": ("face.jpg", _fake_jpeg(), "image/jpeg")},
    )
    assert response.status_code == 401


def test_search_imagem_sem_face_retorna_lista_vazia(client_with_db):
    client, _, token = client_with_db
    headers = {"Authorization": f"Bearer {token}"}
    with patch("app.services.face_service.extract_embeddings", return_value=[]):
        response = client.post(
            "/api/v1/search/by-face",
            files={"file": ("face.jpg", _fake_jpeg(), "image/jpeg")},
            headers=headers,
        )
    assert response.status_code == 200
    body = response.json()
    assert body["results"] == []
    assert "query_time_ms" in body


def test_search_retorna_resultados_com_campos_corretos(client_with_db):
    client, Session, token = client_with_db
    db = Session()
    p = Person(name="Alice", profile_image_path="faces/1.jpg")
    db.add(p)
    db.commit()
    person_id = p.id
    db.close()

    emb = np.array([0.1] * 128)
    query_emb = np.array([0.11] * 128)
    fake_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    headers = {"Authorization": f"Bearer {token}"}

    with patch("app.services.search_service.cv2.imdecode", return_value=fake_frame), \
         patch("app.services.search_service.cv2.cvtColor", return_value=fake_frame), \
         patch("app.services.face_service.extract_embeddings", return_value=[(query_emb, (0, 100, 100, 0))]), \
         patch("app.services.search_service.person_service.get_all_embeddings",
               return_value=[(person_id, emb)]):

        response = client.post(
            "/api/v1/search/by-face",
            files={"file": ("face.jpg", _fake_jpeg(), "image/jpeg")},
            headers=headers,
        )

    assert response.status_code == 200
    body = response.json()
    assert len(body["results"]) == 1
    r = body["results"][0]
    assert r["person_id"] == person_id
    assert r["person_name"] == "Alice"
    assert "distance" in r
    assert "confidence_pct" in r


def test_search_tipo_invalido_retorna_422(client_with_db):
    client, _, token = client_with_db
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post(
        "/api/v1/search/by-face",
        files={"file": ("doc.pdf", b"%PDF-1.4", "application/pdf")},
        headers=headers,
    )
    assert response.status_code == 422
