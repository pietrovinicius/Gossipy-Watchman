import numpy as np
import pytest
from unittest.mock import patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Base, Person
from app.models.cluster import ClusterGroup, ClusterSuggestion
from app.services.cluster_service import run_clusterization, get_clusters


def _l2(v: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(v)
    return v / n if n > 0 else v


def _make_l2_emb(seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    v = rng.standard_normal(512).astype(np.float32)
    return _l2(v)


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


# ── 1: Agrupamento de desconhecidos com distância coseno < 0.4 ────────────────
def test_dbscan_clustering_groups_correctly(db_session):
    p1 = Person(name="Desconhecido #1", category="Desconhecido")
    p2 = Person(name="Desconhecido #2", category="Desconhecido")
    p3 = Person(name="Desconhecido #3", category="Desconhecido")
    p4 = Person(name="Desconhecido #4", category="Desconhecido")
    db_session.add_all([p1, p2, p3, p4])
    db_session.commit()

    # Grupo 1: emb_a e emb_b próximos (coseno dist ≈ 0.05)
    emb_a = np.zeros(512, dtype=np.float32); emb_a[0] = 1.0
    emb_b = np.zeros(512, dtype=np.float32); emb_b[0] = 0.95; emb_b[1] = float(np.sqrt(1 - 0.95**2))
    emb_b = _l2(emb_b)

    # Grupo 2: emb_c e emb_d próximos (coseno dist ≈ 0.05), ortogonais ao grupo 1
    emb_c = np.zeros(512, dtype=np.float32); emb_c[2] = 1.0
    emb_d = np.zeros(512, dtype=np.float32); emb_d[2] = 0.95; emb_d[3] = float(np.sqrt(1 - 0.95**2))
    emb_d = _l2(emb_d)

    # Verificar separação entre grupos (coseno dist deve ser > 0.4)
    assert float(1.0 - np.dot(emb_a, emb_c)) > 0.4

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

    # p1 e p2 próximos (coseno dist ≈ 0.05); p3 (Funcionário) também próximo mas ignorado
    emb_a = np.zeros(512, dtype=np.float32); emb_a[0] = 1.0
    emb_b = np.zeros(512, dtype=np.float32); emb_b[0] = 0.95; emb_b[1] = float(np.sqrt(1 - 0.95**2))
    emb_b = _l2(emb_b)
    emb_c = emb_a.copy()  # idêntico ao p1, mas é Funcionário

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


# ── 3: Embeddings ortogonais (coseno dist = 1.0 > threshold) → sem grupo ─────
def test_clustering_identifies_noise_as_single_profiles(db_session):
    p1 = Person(name="Desconhecido #1", category="Desconhecido")
    p2 = Person(name="Desconhecido #2", category="Desconhecido")
    db_session.add_all([p1, p2])
    db_session.commit()

    # Ortogonais → coseno dist = 1.0 >> threshold 0.4 → sem agrupamento
    emb_a = np.zeros(512, dtype=np.float32); emb_a[0] = 1.0
    emb_b = np.zeros(512, dtype=np.float32); emb_b[1] = 1.0

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


# ── Task 2: clusterização deve usar distância coseno, não Euclidiana ──────────

def test_clusterizacao_usa_distancia_coseno_nao_euclidiana(db_session):
    """Dois embeddings L2-normalizados com coseno dist < threshold (0.4) mas
    Euclidiana > threshold (0.4) devem ser agrupados com métrica coseno.

    emb_a = [1, 0, 0, ...]
    emb_b ≈ [0.9, sqrt(0.19), 0, ...] → coseno dist ≈ 0.1 < 0.4 ✓
                                       → Euclidiana ≈ 0.447 > 0.4 ✗ (código antigo falharia)
    """
    p1 = Person(name="Desconhecido #1", category="Desconhecido")
    p2 = Person(name="Desconhecido #2", category="Desconhecido")
    db_session.add_all([p1, p2])
    db_session.commit()

    emb_a = np.zeros(512, dtype=np.float32)
    emb_a[0] = 1.0  # L2-normalizado

    emb_b = np.zeros(512, dtype=np.float32)
    emb_b[0] = 0.9
    emb_b[1] = float(np.sqrt(1.0 - 0.81))  # sqrt(0.19) → L2 norm = 1
    emb_b = _l2(emb_b)

    cosine_dist = float(1.0 - np.dot(emb_a, emb_b))
    euclidean_dist = float(np.linalg.norm(emb_a - emb_b))
    assert cosine_dist < 0.4, f"pré-condição: coseno {cosine_dist:.4f} deve ser < 0.4"
    assert euclidean_dist > 0.4, f"pré-condição: Euclidiana {euclidean_dist:.4f} deve ser > 0.4"

    mock_embeddings = [(p1.id, emb_a), (p2.id, emb_b)]
    with patch("app.services.cluster_service.person_service.get_all_embeddings",
               return_value=mock_embeddings):
        run_clusterization(db_session)

    groups = db_session.query(ClusterGroup).filter(ClusterGroup.deleted_at.is_(None)).all()
    assert len(groups) == 1, (
        f"Esperado 1 grupo (coseno dist={cosine_dist:.4f} < 0.4), "
        f"obtido {len(groups)} — provavelmente usando Euclidiana ({euclidean_dist:.4f} > 0.4)"
    )


def test_clusterizacao_nao_agrupa_embeddings_coseno_acima_threshold(db_session):
    """Dois embeddings com coseno dist > 0.4 NÃO devem ser agrupados."""
    p1 = Person(name="Desconhecido #1", category="Desconhecido")
    p2 = Person(name="Desconhecido #2", category="Desconhecido")
    db_session.add_all([p1, p2])
    db_session.commit()

    emb_a = np.zeros(512, dtype=np.float32); emb_a[0] = 1.0
    emb_b = np.zeros(512, dtype=np.float32); emb_b[1] = 1.0  # ortogonal → coseno dist = 1.0

    cosine_dist = float(1.0 - np.dot(emb_a, emb_b))
    assert cosine_dist > 0.4

    mock_embeddings = [(p1.id, emb_a), (p2.id, emb_b)]
    with patch("app.services.cluster_service.person_service.get_all_embeddings",
               return_value=mock_embeddings):
        run_clusterization(db_session)

    groups = db_session.query(ClusterGroup).filter(ClusterGroup.deleted_at.is_(None)).all()
    assert len(groups) == 0
