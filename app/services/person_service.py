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
        npy_path = settings.STORAGE_FACES / f"{person.id}_embedding.npy"
        if not npy_path.exists():
            logger.warning("Embedding não encontrado para pessoa id=%s: %s", person.id, npy_path)
            continue
        embedding = np.load(str(npy_path))
        result.append((person.id, embedding))
    return result


def save_new_person(
    db: Session,
    embedding: np.ndarray,
    face_crop: np.ndarray,
    person_index: int,
) -> Person:
    person = Person(name=f"Desconhecido #{person_index}")
    db.add(person)
    db.commit()
    db.refresh(person)

    jpg_path = settings.STORAGE_FACES / f"{person.id}.jpg"
    npy_path = settings.STORAGE_FACES / f"{person.id}_embedding.npy"

    cv2.imwrite(str(jpg_path), face_crop)
    np.save(str(npy_path), embedding)

    person.profile_image_path = str(jpg_path)
    db.commit()

    return person


MAX_FACE_SAMPLES = 10


def save_face_sample(
    db: Session,
    person_id: int,
    appearance_id: int,
    face_crop: np.ndarray,
) -> str | None:
    """Salva recorte facial como amostra adicional da pessoa, até MAX_FACE_SAMPLES por pessoa.

    Nunca propaga exceção: falhas de I/O são logadas e retornam None,
    pois a amostra é um complemento opcional ao fluxo principal do worker.
    """
    try:
        existing = list(settings.STORAGE_FACES.glob(f"{person_id}_sample_*.jpg"))
        if len(existing) >= MAX_FACE_SAMPLES:
            return None

        sample_path = settings.STORAGE_FACES / f"{person_id}_sample_{appearance_id}.jpg"
        cv2.imwrite(str(sample_path), face_crop)
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

    files = sorted(settings.STORAGE_FACES.glob(f"{person_id}.jpg")) + sorted(
        settings.STORAGE_FACES.glob(f"{person_id}_sample_*.jpg")
    )

    return [
        {"filename": f.name, "is_primary": f.name == primary_filename}
        for f in files
    ]


def _is_safe_face_filename(filename: str) -> bool:
    return ".." not in filename and "/" not in filename and "\\" not in filename


def set_primary_photo(db: Session, person_id: int, source_filename: str) -> Person:
    """Define uma amostra facial existente como foto principal da pessoa.

    Cadeia de validação: 400 (caminho inseguro) → 404 (arquivo inexistente)
    → 403 (arquivo pertence a outra pessoa). Copia preservando o original
    (shutil.copy2) para {person_id}.jpg.
    """
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

    person.profile_image_path = str(primary_path)
    db.commit()
    db.refresh(person)
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
    (60.0, "excelente", "green", "Perfil com amostras de alta confiança. Nenhuma ação necessária."),
    (48.0, "bom", "green", "Perfil com boa confiança. Considere adicionar mais amostras em ângulos variados para reforçar."),
    (44.0, "regular", "yellow", "Confiança mediana nas identificações. Recomenda-se revisar e definir uma foto principal mais nítida."),
    (40.0, "insuficiente", "yellow", "Confiança baixa nas identificações. Adicione amostras mais nítidas e revise possíveis confusões com outras pessoas."),
    (float("-inf"), "fraco", "red", "Confiança muito baixa. Recomenda-se revisar manualmente e considerar recadastrar esta pessoa."),
)


def get_profile_quality(db: Session, person_id: int) -> dict:
    """Avalia a qualidade do perfil a partir da confiança média dos reconhecimentos.

    confidence é distância euclidiana (menor = mais confiante), portanto
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

        # remove .npy and .jpg files for secondary
        for suffix in (f"{sec_id}_embedding.npy", f"{sec_id}.jpg"):
            path = settings.STORAGE_FACES / suffix
            if path.exists():
                path.unlink()
                logger.info("merge_people: removido %s", path)

        db.delete(secondary)

    db.commit()
    db.refresh(primary)
    return primary
