import pytest
from sqlalchemy.orm import sessionmaker

from app.models.person import Person


def seed_person(engine, name: str = "Desconhecido #1") -> int:
    Session = sessionmaker(bind=engine)
    session = Session()
    person = Person(name=name, profile_image_path=None)
    session.add(person)
    session.commit()
    session.refresh(person)
    pid = person.id
    session.close()
    return pid


@pytest.mark.asyncio
async def test_list_people_empty(client):
    response = await client.get("/api/v1/people")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_get_person_returns_correct(client, test_engine):
    pid = seed_person(test_engine, "João")
    response = await client.get(f"/api/v1/people/{pid}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == pid
    assert data["name"] == "João"


@pytest.mark.asyncio
async def test_get_person_not_found(client):
    response = await client.get("/api/v1/people/9999")
    assert response.status_code == 404
    assert "não encontrada" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_patch_person_updates_name(client, test_engine):
    pid = seed_person(test_engine, "Desconhecido #1")
    response = await client.patch(
        f"/api/v1/people/{pid}",
        json={"name": "Maria Silva"},
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Maria Silva"


@pytest.mark.asyncio
async def test_patch_person_not_found(client):
    response = await client.patch(
        "/api/v1/people/9999",
        json={"name": "Teste"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_patch_person_empty_name_returns_422(client, test_engine):
    pid = seed_person(test_engine)
    response = await client.patch(
        f"/api/v1/people/{pid}",
        json={"name": ""},
    )
    assert response.status_code == 422
