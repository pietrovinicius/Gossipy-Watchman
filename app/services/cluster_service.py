import logging
from datetime import datetime
import numpy as np
from sqlalchemy.orm import Session, joinedload

from app.core.settings import settings
from app.models.person import Person
from app.models.cluster import ClusterGroup, ClusterSuggestion
from app.services import person_service

logger = logging.getLogger(__name__)


def run_clusterization(db: Session) -> None:
    # 1. Desativa sugestões pendentes anteriores
    db.query(ClusterGroup).filter(
        ClusterGroup.status == "Pendente",
        ClusterGroup.deleted_at.is_(None)
    ).update({"deleted_at": datetime.utcnow()}, synchronize_session=False)

    db.query(ClusterSuggestion).filter(
        ClusterSuggestion.deleted_at.is_(None)
    ).update({"deleted_at": datetime.utcnow()}, synchronize_session=False)
    db.commit()

    # 2. Carrega todas as pessoas ativas da categoria "Desconhecido"
    eligible_people = db.query(Person).filter(
        Person.category == "Desconhecido",
        Person.deleted_at.is_(None)
    ).all()
    eligible_ids = {p.id for p in eligible_people}

    # 3. Carrega embeddings de todas as pessoas
    all_embeddings = person_service.get_all_embeddings(db)

    # 4. Filtra embeddings elegíveis
    active_embeddings = [(pid, emb) for pid, emb in all_embeddings if pid in eligible_ids]

    n = len(active_embeddings)
    if n < 2:
        logger.info("run_clusterization: perfis elegíveis insuficientes (%s) para clusterização", n)
        return

    # 5. Calcula distâncias coseno entre todos os pares.
    # ArcFace embeddings são L2-normalizados → coseno = 1 - dot(a, b)
    tol = settings.FACE_RECOGNITION_TOLERANCE
    pairwise: dict[tuple[int, int], float] = {}
    for i in range(n):
        for j in range(i + 1, n):
            d = float(1.0 - np.dot(active_embeddings[i][1], active_embeddings[j][1]))
            pairwise[(i, j)] = d

    # 6. Clusterização por complete linkage:
    # Um cluster só absorve um novo nó/cluster se a distância MÁXIMA entre todos os
    # pares inter-cluster for < threshold (evita encadeamento A≈B≈C quando A≇C).
    clusters: list[set[int]] = [{i} for i in range(n)]
    sorted_pairs = sorted(pairwise.items(), key=lambda kv: kv[1])

    changed = True
    while changed:
        changed = False
        for (i, j), d in sorted_pairs:
            if d >= tol:
                break
            ci = next((idx for idx, c in enumerate(clusters) if i in c), None)
            cj = next((idx for idx, c in enumerate(clusters) if j in c), None)
            if ci is None or cj is None or ci == cj:
                continue
            # Distância complete linkage = máxima distância entre os dois clusters
            max_d = max(
                pairwise[(min(a, b), max(a, b))]
                for a in clusters[ci]
                for b in clusters[cj]
            )
            if max_d < tol:
                clusters[ci] = clusters[ci] | clusters[cj]
                del clusters[cj]
                changed = True
                break  # reiniciar após merge (índices mudaram)

    components = [list(c) for c in clusters]

    # 7. Persiste os grupos encontrados com tamanho >= 2
    for comp in components:
        if len(comp) >= 2:
            pids = [active_embeddings[idx][0] for idx in comp]
            pids.sort()  # O menor ID (mais antigo) será sugerido como principal

            group = ClusterGroup(status="Pendente")
            db.add(group)
            db.flush()  # Obtém o group.id

            for i, pid in enumerate(pids):
                sug = ClusterSuggestion(
                    group_id=group.id,
                    person_id=pid,
                    is_primary=(i == 0)
                )
                db.add(sug)
            
            logger.info("run_clusterization: grupo %s criado com %s integrantes", group.id, len(pids))

    db.commit()


def get_clusters(db: Session) -> list[ClusterGroup]:
    # Retorna grupos pendentes carregando as sugestões ativas
    return (
        db.query(ClusterGroup)
        .options(joinedload(ClusterGroup.suggestions).joinedload(ClusterSuggestion.person))
        .filter(
            ClusterGroup.status == "Pendente",
            ClusterGroup.deleted_at.is_(None)
        )
        .all()
    )
