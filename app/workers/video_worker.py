import asyncio
import logging
from pathlib import Path

import cv2
import numpy as np
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.settings import settings
from app.core.ws_manager import ws_manager
from app.models.person import Person, PersonCategory
from app.models.video import Video, VideoStatus
from app.services import alert_service, face_service, frame_service, person_service, appearance_service

logger = logging.getLogger(__name__)


def _broadcast_sync(video_id: int, payload: dict) -> None:
    loop = ws_manager._loop
    if loop is None or not loop.is_running():
        return
    fut = asyncio.run_coroutine_threadsafe(ws_manager.broadcast(video_id, payload), loop)
    try:
        fut.result(timeout=2)
    except Exception:
        logger.warning("_broadcast_sync timeout/erro para video_id=%s", video_id)


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
        _broadcast_sync(video_id, {"event": "status", "status": "Processando", "video_id": video_id})

        person_counter = db.query(Video).count()  # heurística simples para índice inicial
        alerted_in_this_video: set[int] = set()

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
                    person = db.get(Person, person_id)
                    if person and person.category == PersonCategory.monitorado.value:
                        if person_id not in alerted_in_this_video:
                            alerted_in_this_video.add(person_id)
                            alert = alert_service.create_alert(
                                db=db,
                                person_id=person_id,
                                video_id=video_id,
                                timestamp_in_video=float(segundo),
                                message=f"Pessoa monitorada detectada: {person.name}",
                            )
                            _broadcast_sync(video_id, {
                                "event": "watchlist_alert",
                                "video_id": video_id,
                                "person_id": person_id,
                                "person_name": person.name,
                                "alert_id": alert.id,
                                "timestamp_in_video": float(segundo),
                                "message": f"ALERTA: {person.name} detectado",
                                "severity": "high",
                            })

            _broadcast_sync(video_id, {"event": "frame", "second": segundo, "video_id": video_id})

        video = db.get(Video, video_id)
        video.status = VideoStatus.CONCLUIDO
        db.commit()
        _broadcast_sync(video_id, {"event": "status", "status": "Concluído", "video_id": video_id})

    except Exception:
        logger.exception("Erro ao processar vídeo id=%s", video_id)
        try:
            video = db.get(Video, video_id)
            video.status = VideoStatus.ERRO
            db.commit()
            _broadcast_sync(video_id, {"event": "status", "status": "Erro", "video_id": video_id})
        except Exception:
            logger.exception("Falha ao atualizar status para Erro")
    finally:
        db.close()
        if _owns_engine:
            engine.dispose()
