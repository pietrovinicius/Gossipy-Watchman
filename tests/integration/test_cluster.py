import pytest
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch

from app.models.person import Person
# Esses imports devem falhar na fase RED pois os models de cluster ainda não existem
from app.models.cluster import ClusterGroup, ClusterSuggestion


def seed_person(engine, name: str = "Desconhecido #1", category: str = "Desconhecido") -> int:
    Session = sessionmaker(bind=engine)
    session = Session()
    person = Person(name=name, profile_image_path=None, category=category)
    session.add(person)
    session.commit()
    session.refresh(person)
    pid = person.id
    session.close()
    return pid


def seed_cluster_group(engine, person_ids: list[int]) -> int:
    Session = sessionmaker(bind=engine)
    session = Session()
    group = ClusterGroup(status="Pendente")
    session.add(group)
    session.commit()
    session.refresh(group)
    
    for i, pid in enumerate(person_ids):
        sug = ClusterSuggestion(
            group_id=group.id,
            person_id=pid,
            is_primary=(i == 0)  # primeiro é sugerido como principal
        )
        session.add(sug)
    session.commit()
    gid = group.id
    session.close()
    return gid


# ── 1: POST /api/v1/people/clusterize exige autenticação e retorna 202 ────────
@pytest.mark.asyncio
async def test_post_clusterize_endpoint_triggers_background_task(client, auth_headers):
    # Sem autenticação → deve retornar 401
    response_no_auth = await client.post("/api/v1/people/clusterize")
    assert response_no_auth.status_code == 401

    # Com autenticação → deve retornar 202 (Accepted)
    with patch("app.api.v1.people.BackgroundTasks.add_task") as mock_add_task:
        response = await client.post("/api/v1/people/clusterize", headers=auth_headers)
        assert response.status_code == 202
        data = response.json()
        assert "task_id" in data
        assert "status" in data
        assert data["status"] == "iniciado"


# ── 2: GET /api/v1/people/clusters retorna as sugestões pendentes do banco ─────
@pytest.mark.asyncio
async def test_get_clusters_endpoint_returns_pending_suggestions(client, auth_headers, test_engine):
    # Sem autenticação → deve retornar 401
    response_no_auth = await client.get("/api/v1/people/clusters")
    assert response_no_auth.status_code == 401

    # Cadastra dados de teste
    p1 = seed_person(test_engine, "Desconhecido #1")
    p2 = seed_person(test_engine, "Desconhecido #2")
    seed_cluster_group(test_engine, [p1, p2])

    response = await client.get("/api/v1/people/clusters", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    
    assert len(data) == 1
    group_data = data[0]
    assert group_data["status"] == "Pendente"
    assert len(group_data["suggestions"]) == 2
    
    # Verifica estrutura das sugestões
    sug_ids = {s["person_id"] for s in group_data["suggestions"]}
    assert sug_ids == {p1, p2}
    
    primary = next(s for s in group_data["suggestions"] if s["is_primary"])
    assert primary["person_id"] == p1


# ── 3: Mesclar via POST /api/v1/people/merge atualiza o status do grupo para 'Aceito' ──
@pytest.mark.asyncio
async def test_resolve_cluster_suggestion_via_merge(client, auth_headers, test_engine):
    p1 = seed_person(test_engine, "Principal")
    p2 = seed_person(test_engine, "Secundário")
    gid = seed_cluster_group(test_engine, [p1, p2])

    # Executa a mesclagem
    merge_response = await client.post(
        "/api/v1/people/merge",
        json={"primary_id": p1, "secondary_ids": [p2]},
        headers=auth_headers,
    )
    assert merge_response.status_code == 200

    # Verifica se o status do cluster_group mudou para 'Aceito'
    Session = sessionmaker(bind=test_engine)
    session = Session()
    group = session.get(ClusterGroup, gid)
    assert group.status == "Aceito"
    session.close()
