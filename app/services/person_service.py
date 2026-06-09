import logging
import shutil
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.settings import settings
from app.models.appearance import Appearance
from app.models.person import Person

logger = logging.getLogger(__name__)


def get_all_embeddings(db: Session) -> list[tuple[int, np.ndarray]]:
    people = db.query(Person).all()
    result: list[tuple[int, np.ndarray]] = []
    for person in people:
        npy_files = sorted(settings.STORAGE_FACES.glob(f"{person.id}_embedding_*.npy"))
        if not npy_files:
            logger.warning("Nenhum embedding encontrado para pessoa id=%s", person.id)
            continue
        for npy_path in npy_files:
            try:
                embedding = np.load(str(npy_path))
                if embedding.shape != (512,):
                    logger.warning(
                        "Embedding com shape inesperado %s ignorado: %s",
                        embedding.shape,
                        npy_path.name,
                    )
                    continue
                result.append((person.id, embedding))
            except Exception:
                logger.warning("Falha ao carregar %s", npy_path, exc_info=True)
    logger.info("[EMBEDDINGS TOTAIS] carregados=%d", len(result))
    return result


def save_new_person(
    db: Session,
    embedding: np.ndarray,
    face_crop: np.ndarray,
    person_index: int,
) -> Person:
    logger.debug(
        f"[SAVE NEW PERSON] embedding_entrada shape={embedding.shape} "
        f"dtype={embedding.dtype} norm={np.linalg.norm(embedding):.4f}"
    )
    person = Person(name=f"Desconhecido #{person_index}")
    db.add(person)
    db.commit()
    db.refresh(person)

    jpg_path = settings.STORAGE_FACES / f"{person.id}.jpg"
    npy_path = settings.STORAGE_FACES / f"{person.id}_embedding_0.npy"

    cv2.imwrite(str(jpg_path), face_crop)
    np.save(str(npy_path), embedding.astype(np.float32))

    logger.info(
        f"[SAVE NEW PERSON] person_id={person.id} name={person.name} "
        f"embedding_salvo shape={embedding.shape} dtype={embedding.dtype} "
        f"npy_path={npy_path}"
    )

    person.profile_image_path = str(jpg_path)
    db.commit()

    return person


def save_face_sample(
    db: Session,
    person_id: int,
    appearance_id: int,
    face_crop: np.ndarray,
    embedding: np.ndarray | None = None,
) -> str | None:
    """Salva recorte facial como amostra adicional. Se embedding ArcFace fornecido
    e o total for menor que FACE_MAX_EMBEDDINGS_PER_PERSON, grava embedding adicional.

    Nunca propaga exceção: falhas de I/O são logadas e retornam None.
    """
    try:
        existing = list(settings.STORAGE_FACES.glob(f"{person_id}_sample_*.jpg"))
        if len(existing) >= settings.FACE_MAX_SAMPLES_PER_PERSON:
            return None

        sample_path = settings.STORAGE_FACES / f"{person_id}_sample_{appearance_id}.jpg"
        cv2.imwrite(str(sample_path), face_crop)

        if embedding is not None:
            existing_embs = list(
                settings.STORAGE_FACES.glob(f"{person_id}_embedding_*.npy")
            )
            if len(existing_embs) < settings.FACE_MAX_EMBEDDINGS_PER_PERSON:
                idx = len(existing_embs)
                emb_path = settings.STORAGE_FACES / f"{person_id}_embedding_{idx}.npy"
                np.save(str(emb_path), embedding.astype(np.float32))
                logger.debug(
                    "Embedding adicional salvo: %s (total=%d)", emb_path.name, idx + 1
                )

        return str(sample_path)
    except Exception:
        logger.warning("Falha ao salvar amostra facial para pessoa id=%s", person_id, exc_info=True)
        return None


def list_face_samples(db: Session, person_id: int) -> list[dict]:
    """Lista arquivos de imagem facial da pessoa (foto principal + amostras), marcando a principal."""
    person = db.get(Person, person_id)
    primary_filename = (
        Path(person.profile_image_path).name
        if person and person.profile_image_path
        else None
    )
    logger.debug(
        f"[LIST_SAMPLES] person_id={person_id} "
        f"profile_image_path={person.profile_image_path if person else None} "
        f"primary_filename={primary_filename}"
    )

    files = sorted(settings.STORAGE_FACES.glob(f"{person_id}.jpg")) + sorted(
        settings.STORAGE_FACES.glob(f"{person_id}_sample_*.jpg")
    )

    result = [
        {"filename": f.name, "is_primary": f.name == primary_filename}
        for f in files
    ]
    logger.debug(f"[LIST_SAMPLES] result={result}")
    return result


def _is_safe_face_filename(filename: str) -> bool:
    return ".." not in filename and "/" not in filename and "\\" not in filename


def delete_face_frame(db: Session, person_id: int, filename: str) -> None:
    """Deleta arquivo de frame facial da pessoa.

    Validações: path traversal + ownership. Não permite deletar foto principal.
    """
    if not _is_safe_face_filename(filename):
        raise HTTPException(status_code=400, detail="Nome de arquivo inválido")

    # Validar ownership
    owner_prefix = f"{person_id}_"
    if filename != f"{person_id}.jpg" and not filename.startswith(owner_prefix):
        raise HTTPException(status_code=403, detail="Arquivo não pertence a esta pessoa")

    # Não permitir deletar foto principal
    if filename == f"{person_id}.jpg":
        raise HTTPException(status_code=400, detail="Não é possível deletar a foto principal")

    frame_path = settings.STORAGE_FACES / filename
    if not frame_path.exists():
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")

    frame_path.unlink()
    logger.info(f"Frame deletado: {filename} (person_id={person_id})")


def set_primary_photo(db: Session, person_id: int, source_filename: str) -> Person:
    """Define uma amostra facial existente como foto principal da pessoa.

    Cadeia de validação: 400 (caminho inseguro) → 404 (arquivo inexistente)
    → 403 (arquivo pertence a outra pessoa). Copia preservando o original
    (shutil.copy2) para {person_id}.jpg.
    """
    logger.info(f"[SET_PRIMARY] iniciando: person_id={person_id} source_filename={source_filename}")

    if not _is_safe_face_filename(source_filename):
        raise HTTPException(status_code=400, detail="Nome de arquivo inválido")

    source_path = settings.STORAGE_FACES / source_filename
    if not source_path.exists():
        raise HTTPException(status_code=404, detail="Arquivo não encontrado")

    owner_prefix = f"{person_id}_"
    if source_filename != f"{person_id}.jpg" and not source_filename.startswith(owner_prefix):
        raise HTTPException(status_code=403, detail="Arquivo não pertence a esta pessoa")

    person = db.get(Person, person_id)
    if person is None:
        raise HTTPException(status_code=404, detail="Pessoa não encontrada")

    primary_path = settings.STORAGE_FACES / f"{person_id}.jpg"
    shutil.copy2(str(source_path), str(primary_path))
    logger.info(f"[SET_PRIMARY] arquivo copiado: {source_path} → {primary_path}")

    person.profile_image_path = str(primary_path)
    db.commit()
    logger.info(f"[SET_PRIMARY] DB commitado: profile_image_path={person.profile_image_path}")

    db.refresh(person)
    logger.info(f"[SET_PRIMARY] pessoa refreshada do DB: profile_image_path={person.profile_image_path}")

    return person


def list_people(
    db: Session, skip: int = 0, limit: int = 50, include_deleted: bool = False
) -> list[Person]:
    query = db.query(Person)
    if not include_deleted:
        query = query.filter(Person.deleted_at.is_(None))
    return (
        query
        .order_by(Person.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_person_by_id(db: Session, person_id: int) -> Person | None:
    return db.get(Person, person_id)


def soft_delete_person(db: Session, person_id: int) -> Person | None:
    person = db.get(Person, person_id)
    if person is None:
        return None
    if person.deleted_at is None:
        person.deleted_at = datetime.utcnow()
        db.commit()
        db.refresh(person)
    return person


def restore_person(db: Session, person_id: int) -> Person | None:
    person = db.get(Person, person_id)
    if person is None:
        return None
    person.deleted_at = None
    db.commit()
    db.refresh(person)
    return person


def reset_person_name(db: Session, person_id: int) -> Person | None:
    person = db.get(Person, person_id)
    if person is None:
        return None
    person.name = f"Desconhecido #{person.id}"
    db.commit()
    db.refresh(person)
    return person


def update_person_name(db: Session, person_id: int, name: str) -> Person | None:
    person = db.get(Person, person_id)
    if person is None:
        return None
    person.name = name
    db.commit()
    db.refresh(person)
    return person


def update_person_details(
    db: Session,
    person_id: int,
    name: str | None,
    notes: str | None,
    category: str | None,
) -> Person | None:
    person = db.get(Person, person_id)
    if person is None:
        return None
    if name is not None:
        person.name = name
    if notes is not None:
        person.notes = notes
    if category is not None:
        person.category = category
    db.commit()
    db.refresh(person)
    return person


def get_person_stats(db: Session, person_id: int) -> dict:
    appearances = (
        db.query(Appearance).filter(Appearance.person_id == person_id).all()
    )
    if not appearances:
        return {
            "video_count": 0,
            "total_seconds": 0.0,
            "first_seen": None,
            "last_seen": None,
        }

    video_ids = {a.video_id for a in appearances}
    total_seconds = sum(
        (a.timestamp_end - a.timestamp_start)
        for a in appearances
        if a.timestamp_end is not None
    )

    # first_seen / last_seen via video.uploaded_at
    from app.models.video import Video

    videos = (
        db.query(Video)
        .filter(Video.id.in_(video_ids))
        .order_by(Video.uploaded_at)
        .all()
    )
    first_seen: datetime | None = videos[0].uploaded_at if videos else None
    last_seen: datetime | None = videos[-1].uploaded_at if videos else None

    return {
        "video_count": len(video_ids),
        "total_seconds": round(total_seconds, 3),
        "first_seen": first_seen,
        "last_seen": last_seen,
    }


_QUALITY_BANDS = (
    # (limite mínimo de score, nível, cor, recomendação)
    # Calibrado para distância coseno ArcFace (threshold=0.4 → score≈60%)
    # score = (1 - avg_cosine_distance) * 100
    (90.0, "excelente", "green", "Perfil com amostras de alta confiança. Nenhuma ação necessária."),
    (80.0, "bom", "green", "Perfil com boa confiança. Considere adicionar mais amostras em ângulos variados para reforçar."),
    (70.0, "regular", "yellow", "Confiança mediana nas identificações. Recomenda-se revisar e definir uma foto principal mais nítida."),
    (60.0, "insuficiente", "yellow", "Confiança baixa nas identificações. Adicione amostras mais nítidas e revise possíveis confusões com outras pessoas."),
    (float("-inf"), "fraco", "red", "Confiança muito baixa. Recomenda-se revisar manualmente e considerar recadastrar esta pessoa."),
)


def get_profile_quality(db: Session, person_id: int) -> dict:
    """Avalia a qualidade do perfil a partir da confiança média dos reconhecimentos.

    confidence é distância coseno ArcFace (menor = mais confiante, threshold=0.4).
    quality_score = (1 - avg_confidence) * 100 cresce conforme a confiança aumenta.
    """
    person = db.get(Person, person_id)
    if person is None:
        raise HTTPException(status_code=404, detail="Pessoa não encontrada")

    appearances = db.query(Appearance).filter(Appearance.person_id == person_id).all()
    sample_count = len(appearances)

    if sample_count == 0:
        avg_confidence = 0.0
        quality_score = 0.0
    else:
        avg_confidence = round(sum(a.confidence for a in appearances) / sample_count, 4)
        quality_score = round((1 - avg_confidence) * 100, 1)

    for min_score, level, color, recommendation in _QUALITY_BANDS:
        if sample_count > 0 and quality_score > min_score:
            quality_level, quality_color, quality_recommendation = level, color, recommendation
            break
    else:
        quality_level, quality_color, quality_recommendation = (
            "insuficiente", "red", "Sem amostras suficientes para avaliar a qualidade do perfil. Aguarde novos reconhecimentos ou adicione fotos manualmente."
        )

    return {
        "avg_confidence": avg_confidence,
        "sample_count": sample_count,
        "quality_score": quality_score,
        "quality_level": quality_level,
        "color": quality_color,
        "recommendation": quality_recommendation,
    }


def merge_people(
    db: Session,
    primary_id: int,
    secondary_ids: list[int],
) -> Person:
    if primary_id in secondary_ids:
        raise HTTPException(status_code=400, detail="primary_id não pode estar em secondary_ids")

    primary = db.get(Person, primary_id)
    if primary is None:
        raise HTTPException(status_code=404, detail=f"Pessoa {primary_id} não encontrada")

    for sec_id in secondary_ids:
        secondary = db.get(Person, sec_id)
        if secondary is None:
            raise HTTPException(status_code=404, detail=f"Pessoa {sec_id} não encontrada")

        # reassociate appearances
        db.query(Appearance).filter(Appearance.person_id == sec_id).update(
            {"person_id": primary_id}
        )

        # copia embeddings do secundário para o primário (até o limite) antes de deletar
        primary_embs = sorted(settings.STORAGE_FACES.glob(f"{primary_id}_embedding_*.npy"))
        cap = settings.FACE_MAX_EMBEDDINGS_PER_PERSON
        for src in sorted(settings.STORAGE_FACES.glob(f"{sec_id}_embedding_*.npy")):
            if len(primary_embs) < cap:
                dst = settings.STORAGE_FACES / f"{primary_id}_embedding_{len(primary_embs)}.npy"
                shutil.copy2(src, dst)
                primary_embs.append(dst)
                logger.info("merge_people: copiado %s → %s", src.name, dst.name)
            src.unlink(missing_ok=True)
            logger.info("merge_people: removido %s", src)
        jpg_path = settings.STORAGE_FACES / f"{sec_id}.jpg"
        if jpg_path.exists():
            jpg_path.unlink()
            logger.info("merge_people: removido %s", jpg_path)

        db.delete(secondary)

    # Resolve cluster suggestions containing secondary_ids
    from app.models.cluster import ClusterGroup, ClusterSuggestion
    suggestions = db.query(ClusterSuggestion).filter(
        ClusterSuggestion.person_id.in_(secondary_ids),
        ClusterSuggestion.deleted_at.is_(None)
    ).all()
    for sug in suggestions:
        group = db.get(ClusterGroup, sug.group_id)
        if group and group.status == "Pendente":
            group.status = "Aceito"
            logger.info("merge_people: cluster_group %s resolvido como Aceito", group.id)

    db.commit()
    db.refresh(primary)
    return primary
