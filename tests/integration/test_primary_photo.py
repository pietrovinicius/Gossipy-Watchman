import pytest
from pathlib import Path
from sqlalchemy.orm import sessionmaker
from app.models.person import Person
from app.core.settings import settings


def seed_person_with_frame(engine, name: str = "Teste") -> tuple[int, str]:
    """Cria pessoa + frame de teste no storage."""
    Session = sessionmaker(bind=engine)
    session = Session()

    # Cria pessoa
    person = Person(name=name, profile_image_path=None)
    session.add(person)
    session.commit()
    session.refresh(person)
    pid = person.id
    session.close()

    # Cria frame de teste (arquivo dummy)
    settings.STORAGE_FACES.mkdir(parents=True, exist_ok=True)
    frame_filename = f"{pid}_sample_001.jpg"
    frame_path = settings.STORAGE_FACES / frame_filename

    # Cria arquivo dummy (1x1 pixel JPEG)
    jpeg_bytes = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00\x0b\x08\x00\x01\x00\x01\x01\x11\x00\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xc4\x00\xb5\x10\x00\x02\x01\x03\x03\x02\x04\x03\x05\x05\x04\x04\x00\x00\x01}\x01\x02\x03\x00\x04\x11\x05\x12!1A\x06\x13Qa\x07"q\x142\x81\x91\xa1\x08#B\xb1\xc1\x15R\xd1\xf0$3br\x82\t\n\x16\x17\x18\x19\x1a%&\'()*456789:CDEFGHIJSTUVWXYZcdefghijstuvwxyz\x83\x84\x85\x86\x87\x88\x89\x8a\x92\x93\x94\x95\x96\x97\x98\x99\x9a\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xff\xda\x00\x08\x01\x01\x00\x00?\x00\xfb\xd3\xff\xd9'
    frame_path.write_bytes(jpeg_bytes)

    return pid, frame_filename


@pytest.mark.asyncio
async def test_set_primary_photo_updates_profile_image_path(client, auth_headers, test_engine):
    """RED: Teste que o endpoint PATCH /people/{id}/primary-photo funciona."""
    pid, frame_filename = seed_person_with_frame(test_engine, "Teste Primary Photo")

    # Chama endpoint para definir como principal
    response = await client.patch(
        f"/api/v1/people/{pid}/primary-photo",
        json={"filename": frame_filename},
        headers=auth_headers,
    )

    # Verifica resposta
    assert response.status_code == 200
    data = response.json()

    # Verifica se profile_image_path foi atualizado
    assert data["id"] == pid
    assert data["profile_image_path"] is not None
    assert str(pid) in data["profile_image_path"]
    assert data["profile_image_path"].endswith(f"{pid}.jpg")


@pytest.mark.asyncio
async def test_set_primary_photo_not_found(client, auth_headers):
    """RED: 404 quando pessoa não existe."""
    response = await client.patch(
        "/api/v1/people/9999/primary-photo",
        json={"filename": "any.jpg"},
        headers=auth_headers,
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_set_primary_photo_invalid_filename(client, auth_headers, test_engine):
    """RED: 400 quando filename contém path traversal."""
    pid, _ = seed_person_with_frame(test_engine, "Teste Security")

    response = await client.patch(
        f"/api/v1/people/{pid}/primary-photo",
        json={"filename": "../../../etc/passwd"},
        headers=auth_headers,
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_set_primary_photo_file_not_found(client, auth_headers, test_engine):
    """RED: 404 quando arquivo não existe."""
    pid, _ = seed_person_with_frame(test_engine, "Teste Not Found")

    response = await client.patch(
        f"/api/v1/people/{pid}/primary-photo",
        json={"filename": "nao_existe.jpg"},
        headers=auth_headers,
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_set_primary_photo_wrong_owner(client, auth_headers, test_engine):
    """RED: 403 quando frame pertence a outra pessoa."""
    pid1, frame1 = seed_person_with_frame(test_engine, "Pessoa 1")
    pid2, _ = seed_person_with_frame(test_engine, "Pessoa 2")

    # Tenta definir frame de pid1 como principal em pid2
    response = await client.patch(
        f"/api/v1/people/{pid2}/primary-photo",
        json={"filename": frame1},
        headers=auth_headers,
    )
    assert response.status_code == 403
