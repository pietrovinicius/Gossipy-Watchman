import numpy as np
import pytest
from unittest.mock import patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Base, Person
# Esses imports devem falhar na fase RED pois as tabelas/arquivos de serviço ainda não existem
from app.models.cluster import ClusterGroup, ClusterSuggestion
from app.services.cluster_service import run_clusterization, get_clusters


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    
    # Criar também as tabelas de clusters sugeridas que ainda não estão no Base real
    # Mas como Base.metadata.create_all cria tudo que está importado e registrado na metadata,
    # se ClusterGroup e ClusterSuggestion herdarem de Base, create_all vai criá-las.
    # Para garantir o RED caso os imports quebrem de cara, o pytest levantará ImportError/AttributeError.
    
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    engine.dispose()


# ── 1: Agrupamento de desconhecidos com distância euclidiana < 0.6 ────────────
def test_dbscan_clustering_groups_correctly(db_session):
    # Cadastra 4 pessoas desconhecidas no banco
    p1 = Person(name="Desconhecido #1", category="Desconhecido")
    p2 = Person(name="Desconhecido #2", category="Desconhecido")
    p3 = Person(name="Desconhecido #3", category="Desconhecido")
    p4 = Person(name="Desconhecido #4", category="Desconhecido")
    db_session.add_all([p1, p2, p3, p4])
    db_session.commit()

    # Mocks de embeddings
    # A e B serão próximos (distância ~0.14)
    # C e D serão próximos (distância ~0.14)
    # A/B e C/D serão distantes (distância > 1.0)
    emb_a = np.zeros(128)
    emb_b = np.zeros(128)
    emb_b[0] = 0.1
    
    emb_c = np.ones(128)
    emb_d = np.ones(128)
    emb_d[0] = 0.9

    # Mockamos a função que carrega os embeddings do disco
    mock_embeddings = [
        (p1.id, emb_a),
        (p2.id, emb_b),
        (p3.id, emb_c),
        (p4.id, emb_d),
    ]

    with patch("app.services.cluster_service.person_service.get_all_embeddings", return_value=mock_embeddings):
        run_clusterization(db_session)

    # Verifica se os grupos foram criados no banco
    groups = db_session.query(ClusterGroup).filter(ClusterGroup.deleted_at.is_(None)).all()
    assert len(groups) == 2

    # Verifica se os membros do cluster estão associados corretamente
    suggestions = db_session.query(ClusterSuggestion).filter(ClusterSuggestion.deleted_at.is_(None)).all()
    assert len(suggestions) == 4

    # Agrupa por group_id
    group_map = {}
    for sug in suggestions:
        group_map.setdefault(sug.group_id, []).append(sug.person_id)

    # Devem ter dois grupos com tamanho 2 cada
    sizes = [len(members) for members in group_map.values()]
    assert sizes == [2, 2]

    # Verifica se A (p1) e B (p2) estão no mesmo grupo
    group_1_id = suggestions[0].group_id
    p1_group_id = next(s.group_id for s in suggestions if s.person_id == p1.id)
    p2_group_id = next(s.group_id for s in suggestions if s.person_id == p2.id)
    p3_group_id = next(s.group_id for s in suggestions if s.person_id == p3.id)
    p4_group_id = next(s.group_id for s in suggestions if s.person_id == p4.id)

    assert p1_group_id == p2_group_id
    assert p3_group_id == p4_group_id
    assert p1_group_id != p3_group_id


# ── 2: Ignorar perfis conhecidos (Funcionário, Visitante, Monitorado) ─────────
def test_clustering_ignores_known_profiles(db_session):
    p1 = Person(name="Desconhecido #1", category="Desconhecido")
    p2 = Person(name="Desconhecido #2", category="Desconhecido")
    p3 = Person(name="Funcionário #1", category="Funcionário")
    db_session.add_all([p1, p2, p3])
    db_session.commit()

    emb_a = np.zeros(128)
    emb_b = np.zeros(128)
    emb_b[0] = 0.1
    emb_c = np.zeros(128)
    emb_c[0] = 0.05

    # Mock com todos os 3 perfis
    mock_embeddings = [
        (p1.id, emb_a),
        (p2.id, emb_b),
        (p3.id, emb_c),
    ]

    with patch("app.services.cluster_service.person_service.get_all_embeddings", return_value=mock_embeddings):
        run_clusterization(db_session)

    # O grupo sugerido deve conter apenas p1 e p2. p3 (Funcionário) deve ser ignorado.
    groups = db_session.query(ClusterGroup).filter(ClusterGroup.deleted_at.is_(None)).all()
    assert len(groups) == 1

    suggestions = db_session.query(ClusterSuggestion).filter(ClusterSuggestion.deleted_at.is_(None)).all()
    person_ids = {s.person_id for s in suggestions}
    assert p1.id in person_ids
    assert p2.id in person_ids
    assert p3.id not in person_ids


# ── 3: Identificar ruído (distância > 0.6) e não criar grupos no banco ────────
def test_clustering_identifies_noise_as_single_profiles(db_session):
    p1 = Person(name="Desconhecido #1", category="Desconhecido")
    p2 = Person(name="Desconhecido #2", category="Desconhecido")
    db_session.add_all([p1, p2])
    db_session.commit()

    # Distância Euclidiana = 1.0 (maior que o threshold de 0.6)
    emb_a = np.zeros(128)
    emb_b = np.ones(128) / np.sqrt(128)

    mock_embeddings = [
        (p1.id, emb_a),
        (p2.id, emb_b),
    ]

    with patch("app.services.cluster_service.person_service.get_all_embeddings", return_value=mock_embeddings):
        run_clusterization(db_session)

    # Não deve criar nenhum cluster group ativo
    groups = db_session.query(ClusterGroup).filter(ClusterGroup.deleted_at.is_(None)).all()
    assert len(groups) == 0

    suggestions = db_session.query(ClusterSuggestion).filter(ClusterSuggestion.deleted_at.is_(None)).all()
    assert len(suggestions) == 0
