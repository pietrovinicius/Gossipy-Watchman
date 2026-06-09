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

    # 5. Calcula distâncias coseno e monta o grafo de adjacência (Single Linkage / Connected Components)
    # ArcFace embeddings são L2-normalizados → coseno = 1 - dot(a, b)
    adj = {i: [] for i in range(n)}
    for i in range(n):
        for j in range(i + 1, n):
            dist = float(1.0 - np.dot(active_embeddings[i][1], active_embeddings[j][1]))
            if dist < settings.FACE_RECOGNITION_TOLERANCE:
                adj[i].append(j)
                adj[j].append(i)

    # 6. Busca por componentes conectados (DBSCAN simplificado sem densidade de ruído)
    visited = [False] * n
    components = []
    for i in range(n):
        if not visited[i]:
            comp = []
            queue = [i]
            visited[i] = True
            while queue:
                curr = queue.pop(0)
                comp.append(curr)
                for neighbor in adj[curr]:
                    if not visited[neighbor]:
                        visited[neighbor] = True
                        queue.append(neighbor)
            components.append(comp)

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
