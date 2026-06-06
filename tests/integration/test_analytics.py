import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.session import get_db
from app.models import Base
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
    yield client, token
    app.dependency_overrides.clear()
    engine.dispose()


def test_analytics_overview_sem_auth_retorna_401(client_with_db):
    client, _ = client_with_db
    response = client.get("/api/v1/analytics/overview")
    assert response.status_code == 401


def test_analytics_overview_retorna_campos_esperados(client_with_db):
    client, token = client_with_db
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/v1/analytics/overview", headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert "total_videos" in body
    assert "total_people" in body
    assert "total_appearances" in body
