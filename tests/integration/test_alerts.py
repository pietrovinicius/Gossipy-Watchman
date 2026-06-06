import pytest


@pytest.mark.asyncio
async def test_get_alerts_sem_token_retorna_401(client):
    res = await client.get("/api/v1/alerts")
    assert res.status_code == 401


@pytest.mark.asyncio
async def test_get_alerts_retorna_lista_vazia(client, auth_headers):
    res = await client.get("/api/v1/alerts", headers=auth_headers)
    assert res.status_code == 200
    assert res.json() == []


@pytest.mark.asyncio
async def test_get_alerts_count_retorna_zero(client, auth_headers):
    res = await client.get("/api/v1/alerts/count", headers=auth_headers)
    assert res.status_code == 200
    assert res.json() == {"unseen": 0}


@pytest.mark.asyncio
async def test_patch_alerts_seen_atualiza_registros(client, auth_headers, db_session):
    from app.services.alert_service import create_alert
    from app.models import Person, Video, VideoStatus

    p = Person(name="Mon", profile_image_path="faces/1.jpg")
    db_session.add(p)
    v = Video(file_name="v.mp4", file_path="s/v.mp4", status=VideoStatus.CONCLUIDO)
    db_session.add(v)
    db_session.commit()

    alert = create_alert(db_session, p.id, v.id, 3.0, "teste")

    res = await client.patch(
        "/api/v1/alerts/seen",
        json={"alert_ids": [alert.id]},
        headers=auth_headers,
    )
    assert res.status_code == 200
    assert res.json()["updated"] == 1
