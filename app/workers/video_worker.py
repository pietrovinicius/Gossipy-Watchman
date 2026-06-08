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
from app.services.conversion_service import get_video_duration_seconds

logger = logging.getLogger(__name__)


def get_adaptive_params(video_path: Path) -> dict:
    """Retorna parâmetros CNN otimizados por duração."""
    duration = get_video_duration_seconds(video_path)

    if duration is None:
        return {
            "model": settings.FACE_DETECTION_MODEL,
            "upsample": settings.FACE_UPSAMPLE,
            "fps_sample": settings.FRAMES_PER_SECOND_SAMPLE,
            "duration": None,
            "mode": "padrão (ffprobe indisponível)"
        }

    if duration <= settings.CNN_ADAPTIVE_SHORT_MAX:
        mode = f"preciso (vídeo curto: {duration:.0f}s)"
        upsample = settings.CNN_SHORT_UPSAMPLE
        fps_sample = settings.CNN_SHORT_FPS_SAMPLE
    elif duration <= settings.CNN_ADAPTIVE_MEDIUM_MAX:
        mode = f"equilibrado (vídeo médio: {duration/60:.1f}min)"
        upsample = settings.CNN_MEDIUM_UPSAMPLE
        fps_sample = settings.CNN_MEDIUM_FPS_SAMPLE
    else:
        mode = f"eficiente (vídeo longo: {duration/3600:.1f}h)"
        upsample = settings.CNN_LONG_UPSAMPLE
        fps_sample = settings.CNN_LONG_FPS_SAMPLE

    return {
        "model": settings.FACE_DETECTION_MODEL,
        "upsample": upsample,
        "fps_sample": fps_sample,
        "duration": duration,
        "mode": mode
    }


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


def _process_track(
    db,
    video_id: int,
    track,
    person_counter: int,
    alerted_in_this_video: set[int],
) -> int:
    """Resolve a identidade de um track (aparição contínua) e persiste o
    resultado: pessoa nova ou aparição/alerta de pessoa conhecida.

    Retorna o `person_counter` atualizado.
    """
    mean_embedding = track.mean_embedding()
    best_crop = track.get_best_crop()

    known = person_service.get_all_embeddings(db)
    person_id, distance = face_service.find_matching_person(mean_embedding, known)

    if person_id is None:
        person_counter += 1
        logger.info(
            f"[WORKER] track={track.start_time:.1f}s-{track.last_seen:.1f}s "
            f"({track.sample_count} amostras) NOVA_PESSOA → Desconhecido #{person_counter}"
        )
        person_service.save_new_person(db, mean_embedding, best_crop, person_index=person_counter)
        return person_counter

    logger.info(
        f"[WORKER] track={track.start_time:.1f}s-{track.last_seen:.1f}s "
        f"({track.sample_count} amostras) PESSOA_CONHECIDA person_id={person_id} "
        f"distancia={distance:.4f}"
    )
    appearance = appearance_service.upsert_appearance(
        db,
        person_id=person_id,
        video_id=video_id,
        timestamp=float(track.start_time),
        confidence=distance,
    )
    person_service.save_face_sample(db, person_id, appearance.id, best_crop)

    person = db.get(Person, person_id)
    if person and person.category == PersonCategory.monitorado.value:
        if person_id not in alerted_in_this_video:
            alerted_in_this_video.add(person_id)
            alert = alert_service.create_alert(
                db=db,
                person_id=person_id,
                video_id=video_id,
                timestamp_in_video=float(track.start_time),
                message=f"Pessoa monitorada detectada: {person.name}",
            )
            _broadcast_sync(video_id, {
                "event": "watchlist_alert",
                "video_id": video_id,
                "person_id": person_id,
                "person_name": person.name,
                "alert_id": alert.id,
                "timestamp_in_video": float(track.start_time),
                "message": f"ALERTA: {person.name} detectado",
                "severity": "high",
            })

    return person_counter


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

        from app.services.conversion_service import (
            can_opencv_read, repair_mp4_moov
        )
        from app.services.video_service import update_video_status

        # Verificar se OpenCV consegue ler o arquivo
        if not can_opencv_read(video_path):
            logger.warning(
                f"[video_id={video_id}] OpenCV não consegue ler "
                f"{video_path.name} — tentando reparar moov atom"
            )
            _broadcast_sync(video_id, {
                "event": "converting",
                "video_id": video_id,
                "status": "Reparando",
                "message": "Reparando formato do vídeo (moov atom)..."
            })
            try:
                video_path = repair_mp4_moov(video_path)
                logger.info(
                    f"[video_id={video_id}] Reparo concluído: "
                    f"{video_path.name}"
                )
            except Exception as e:
                logger.error(
                    f"[video_id={video_id}] Falha no reparo: {e}"
                )
                update_video_status(db, video_id, VideoStatus.ERRO)
                _broadcast_sync(video_id, {
                    "event": "error",
                    "video_id": video_id,
                    "status": "Erro",
                    "message": (
                        "Não foi possível reparar o arquivo de vídeo. "
                        "Tente converter para MP4 com ffmpeg antes do upload."
                    )
                })
                return

        person_counter = db.query(Video).count()  # heurística simples para índice inicial
        alerted_in_this_video: set[int] = set()
        first_frame = True
        tracker = face_service.FaceTracker()

        for segundo, frame in frame_service.extract_frames(video_path):
            # Salvar primeiro frame como thumbnail
            if first_frame:
                try:
                    thumbnail_path = settings.STORAGE_VIDEOS / f"{video_id}_thumbnail.jpg"
                    cv2.imwrite(str(thumbnail_path), frame)
                    video.thumbnail_path = str(thumbnail_path)
                    db.commit()
                    logger.info(f"[WORKER] thumbnail salvo: {thumbnail_path}")
                except Exception:
                    logger.warning(f"[WORKER] falha ao salvar thumbnail para video_id={video_id}", exc_info=True)
                first_frame = False

            embeddings = face_service.extract_embeddings(frame)
            for embedding, location in embeddings:
                tracker.add_detection(embedding, location, frame, timestamp=float(segundo))

            _broadcast_sync(video_id, {"event": "frame", "second": segundo, "video_id": video_id})

        for track in tracker.flush():
            person_counter = _process_track(db, video_id, track, person_counter, alerted_in_this_video)

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
