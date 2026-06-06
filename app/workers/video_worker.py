import logging
from pathlib import Path

import cv2
import numpy as np
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.settings import settings
from app.models.video import Video, VideoStatus
from app.services import face_service, frame_service, person_service, appearance_service

logger = logging.getLogger(__name__)


def _get_session_factory(engine):
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


def process_video(video_id: int, video_path: Path, _engine=None) -> None:
    # _engine permite injeção em testes sem patch de create_engine
    _owns_engine = _engine is None
    engine = _engine if _engine is not None else create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False},
    )
    Session = _get_session_factory(engine)
    db = Session()

    try:
        video = db.get(Video, video_id)
        video.status = VideoStatus.PROCESSANDO
        db.commit()

        person_counter = db.query(Video).count()  # heurística simples para índice inicial

        for segundo, frame in frame_service.extract_frames(video_path):
            embeddings = face_service.extract_embeddings(frame)

            for embedding in embeddings:
                known = person_service.get_all_embeddings(db)
                person_id, distance = face_service.find_matching_person(embedding, known)

                if person_id is None:
                    person_counter += 1
                    # Recorte da face (frame inteiro por simplificação; Sprint 3 pode refinar)
                    face_crop = frame
                    person_service.save_new_person(db, embedding, face_crop, person_index=person_counter)
                else:
                    appearance_service.upsert_appearance(
                        db,
                        person_id=person_id,
                        video_id=video_id,
                        timestamp=float(segundo),
                        confidence=distance,
                    )

        video = db.get(Video, video_id)
        video.status = VideoStatus.CONCLUIDO
        db.commit()

    except Exception:
        logger.exception("Erro ao processar vídeo id=%s", video_id)
        try:
            video = db.get(Video, video_id)
            video.status = VideoStatus.ERRO
            db.commit()
        except Exception:
            logger.exception("Falha ao atualizar status para Erro")
    finally:
        db.close()
        if _owns_engine:
            engine.dispose()
