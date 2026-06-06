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
async def test_list_people_empty(client, auth_headers):
    response = await client.get("/api/v1/people", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_get_person_returns_correct(client, auth_headers, test_engine):
    pid = seed_person(test_engine, "João")
    response = await client.get(f"/api/v1/people/{pid}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == pid
    assert data["name"] == "João"


@pytest.mark.asyncio
async def test_get_person_not_found(client, auth_headers):
    response = await client.get("/api/v1/people/9999", headers=auth_headers)
    assert response.status_code == 404
    assert "não encontrada" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_patch_person_updates_name(client, auth_headers, test_engine):
    pid = seed_person(test_engine, "Desconhecido #1")
    response = await client.patch(
        f"/api/v1/people/{pid}",
        json={"name": "Maria Silva"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Maria Silva"


@pytest.mark.asyncio
async def test_patch_person_not_found(client, auth_headers):
    response = await client.patch(
        "/api/v1/people/9999",
        json={"name": "Teste"},
        headers=auth_headers,
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_patch_person_empty_name_returns_422(client, auth_headers, test_engine):
    pid = seed_person(test_engine)
    response = await client.patch(
        f"/api/v1/people/{pid}",
        json={"name": ""},
        headers=auth_headers,
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_patch_person_updates_notes_and_category(client, auth_headers, test_engine):
    pid = seed_person(test_engine, "Funcionário Teste")
    response = await client.patch(
        f"/api/v1/people/{pid}",
        json={"notes": "Trabalha no turno da manhã", "category": "Funcionário"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["notes"] == "Trabalha no turno da manhã"
    assert data["category"] == "Funcionário"


@pytest.mark.asyncio
async def test_get_person_stats_returns_correct_structure(client, auth_headers, test_engine):
    pid = seed_person(test_engine, "Pessoa Stats")
    response = await client.get(f"/api/v1/people/{pid}/stats", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "video_count" in data
    assert "total_seconds" in data
    assert "first_seen" in data
    assert "last_seen" in data
    assert data["video_count"] == 0
    assert data["total_seconds"] == 0.0


@pytest.mark.asyncio
async def test_get_person_stats_not_found(client, auth_headers):
    response = await client.get("/api/v1/people/9999/stats", headers=auth_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_merge_people_returns_primary(client, auth_headers, test_engine):
    p1_id = seed_person(test_engine, "Principal")
    p2_id = seed_person(test_engine, "Secundário")
    response = await client.post(
        "/api/v1/people/merge",
        json={"primary_id": p1_id, "secondary_ids": [p2_id]},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == p1_id
    assert data["name"] == "Principal"


@pytest.mark.asyncio
async def test_merge_people_secondary_not_found(client, auth_headers, test_engine):
    p1_id = seed_person(test_engine, "Principal")
    response = await client.post(
        "/api/v1/people/merge",
        json={"primary_id": p1_id, "secondary_ids": [9999]},
        headers=auth_headers,
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_merge_people_self_merge_returns_422(client, auth_headers, test_engine):
    pid = seed_person(test_engine, "Auto Merge")
    response = await client.post(
        "/api/v1/people/merge",
        json={"primary_id": pid, "secondary_ids": [pid]},
        headers=auth_headers,
    )
    assert response.status_code == 422
