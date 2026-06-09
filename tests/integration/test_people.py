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
async def test_get_person_frames_returns_primary_photo(client, auth_headers, test_engine, tmp_path):
    from unittest.mock import patch

    pid = seed_person(test_engine, "Com Frames")

    Session = sessionmaker(bind=test_engine)
    session = Session()
    person = session.get(Person, pid)
    person.profile_image_path = str(tmp_path / f"{pid}.jpg")
    session.commit()
    session.close()

    (tmp_path / f"{pid}.jpg").write_bytes(b"x")
    (tmp_path / f"{pid}_sample_5.jpg").write_bytes(b"x")

    with patch("app.services.person_service.settings") as mock_settings:
        mock_settings.STORAGE_FACES = tmp_path
        response = await client.get(f"/api/v1/people/{pid}/frames", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    filenames = {item["filename"] for item in data}
    assert filenames == {f"{pid}.jpg", f"{pid}_sample_5.jpg"}
    primary = [item for item in data if item["is_primary"]]
    assert len(primary) == 1
    assert primary[0]["filename"] == f"{pid}.jpg"
    assert primary[0]["url"].endswith(f"/faces/{pid}.jpg")


@pytest.mark.asyncio
async def test_get_person_frames_not_found(client, auth_headers):
    response = await client.get("/api/v1/people/9999/frames", headers=auth_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_patch_primary_photo_updates_profile_image(client, auth_headers, test_engine, tmp_path):
    from unittest.mock import patch

    pid = seed_person(test_engine, "Foto Principal")
    (tmp_path / f"{pid}_sample_8.jpg").write_bytes(b"nova-foto")

    with patch("app.services.person_service.settings") as mock_settings:
        mock_settings.STORAGE_FACES = tmp_path
        response = await client.patch(
            f"/api/v1/people/{pid}/primary-photo",
            json={"filename": f"{pid}_sample_8.jpg"},
            headers=auth_headers,
        )

    assert response.status_code == 200
    data = response.json()
    # profile_image_path aponta diretamente para o sample (sem cópia para {pid}.jpg)
    assert data["profile_image_path"] == str(tmp_path / f"{pid}_sample_8.jpg")


@pytest.mark.asyncio
async def test_patch_primary_photo_path_traversal_returns_400(client, auth_headers, test_engine, tmp_path):
    from unittest.mock import patch

    pid = seed_person(test_engine, "Path Traversal")

    with patch("app.services.person_service.settings") as mock_settings:
        mock_settings.STORAGE_FACES = tmp_path
        response = await client.patch(
            f"/api/v1/people/{pid}/primary-photo",
            json={"filename": "../../etc/passwd"},
            headers=auth_headers,
        )

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_patch_primary_photo_missing_file_returns_404(client, auth_headers, test_engine, tmp_path):
    from unittest.mock import patch

    pid = seed_person(test_engine, "Sem Arquivo")

    with patch("app.services.person_service.settings") as mock_settings:
        mock_settings.STORAGE_FACES = tmp_path
        response = await client.patch(
            f"/api/v1/people/{pid}/primary-photo",
            json={"filename": f"{pid}_sample_404.jpg"},
            headers=auth_headers,
        )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_patch_primary_photo_other_persons_file_returns_403(client, auth_headers, test_engine, tmp_path):
    from unittest.mock import patch

    p1 = seed_person(test_engine, "Dono")
    p2 = seed_person(test_engine, "Outro")
    (tmp_path / f"{p2}_sample_1.jpg").write_bytes(b"x")

    with patch("app.services.person_service.settings") as mock_settings:
        mock_settings.STORAGE_FACES = tmp_path
        response = await client.patch(
            f"/api/v1/people/{p1}/primary-photo",
            json={"filename": f"{p2}_sample_1.jpg"},
            headers=auth_headers,
        )

    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_person_quality_returns_correct_structure(client, auth_headers, test_engine):
    pid = seed_person(test_engine, "Qualidade")
    response = await client.get(f"/api/v1/people/{pid}/quality", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert set(data.keys()) == {
        "avg_confidence", "sample_count", "quality_score",
        "quality_level", "color", "recommendation",
    }
    assert data["sample_count"] == 0
    assert data["quality_level"] == "insuficiente"


@pytest.mark.asyncio
async def test_get_person_quality_not_found(client, auth_headers):
    response = await client.get("/api/v1/people/9999/quality", headers=auth_headers)
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


# ── soft delete / restore ─────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_delete_person_without_token_returns_401(client, test_engine):
    pid = seed_person(test_engine, "Sem Token")
    response = await client.delete(f"/api/v1/people/{pid}")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_delete_person_returns_200_with_deleted_at(client, auth_headers, test_engine):
    pid = seed_person(test_engine, "Para Excluir")
    response = await client.delete(f"/api/v1/people/{pid}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == pid
    assert data["deleted_at"] is not None


@pytest.mark.asyncio
async def test_delete_person_unknown_id_returns_404(client, auth_headers):
    response = await client.delete("/api/v1/people/9999", headers=auth_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_people_excludes_deleted_by_default(client, auth_headers, test_engine):
    p1 = seed_person(test_engine, "Ativo")
    p2 = seed_person(test_engine, "Removido")
    await client.delete(f"/api/v1/people/{p2}", headers=auth_headers)

    response = await client.get("/api/v1/people", headers=auth_headers)
    ids = [item["id"] for item in response.json()]
    assert p1 in ids
    assert p2 not in ids


@pytest.mark.asyncio
async def test_list_people_include_deleted_true_returns_all(client, auth_headers, test_engine):
    p1 = seed_person(test_engine, "Ativo")
    p2 = seed_person(test_engine, "Removido")
    await client.delete(f"/api/v1/people/{p2}", headers=auth_headers)

    response = await client.get("/api/v1/people?include_deleted=true", headers=auth_headers)
    ids = [item["id"] for item in response.json()]
    assert p1 in ids
    assert p2 in ids


@pytest.mark.asyncio
async def test_restore_person_resets_deleted_at(client, auth_headers, test_engine):
    pid = seed_person(test_engine, "Para Restaurar")
    await client.delete(f"/api/v1/people/{pid}", headers=auth_headers)

    response = await client.post(f"/api/v1/people/{pid}/restore", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["deleted_at"] is None


# ── reset-name ────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_reset_person_name_returns_desconhecido_pattern(client, auth_headers, test_engine):
    pid = seed_person(test_engine, "Fulano da Silva")
    response = await client.post(f"/api/v1/people/{pid}/reset-name", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == f"Desconhecido #{pid}"


@pytest.mark.asyncio
async def test_reset_person_name_unknown_id_returns_404(client, auth_headers):
    response = await client.post("/api/v1/people/9999/reset-name", headers=auth_headers)
    assert response.status_code == 404
