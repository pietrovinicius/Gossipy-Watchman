"""Testes do video_worker.py após migração para InsightFace.

get_adaptive_params foi removido — funcionalidade de calibração CNN não se aplica
ao pipeline InsightFace/RetinaFace. Este arquivo testa o comportamento de
_process_track, especialmente que mean_embedding é passado a save_face_sample.
"""
import numpy as np
import pytest
from unittest.mock import patch, MagicMock, call


def _make_track(person_counter_offset: int = 0):
    """Retorna mock de FaceTrack."""
    import numpy as np
    track = MagicMock()
    track.start_time = 1.0
    track.last_seen = 5.0
    track.sample_count = 3
    emb = np.zeros(512, dtype=np.float32)
    emb[0] = 1.0
    track.mean_embedding.return_value = emb
    track.get_best_crop.return_value = np.zeros((80, 80, 3), dtype=np.uint8)
    return track


def test_process_track_passes_embedding_to_save_face_sample():
    """_process_track deve passar mean_embedding ao save_face_sample."""
    from app.workers.video_worker import _process_track

    mock_db = MagicMock()
    track = _make_track()
    mean_emb = track.mean_embedding()

    appearance_mock = MagicMock()
    appearance_mock.id = 42

    with patch("app.workers.video_worker.person_service.get_all_embeddings",
               return_value=[(1, mean_emb)]), \
         patch("app.workers.video_worker.face_service.find_matching_person",
               return_value=(1, 0.05)), \
         patch("app.workers.video_worker.appearance_service.upsert_appearance",
               return_value=appearance_mock), \
         patch("app.workers.video_worker.person_service.save_face_sample") as mock_save_sample, \
         patch("app.workers.video_worker.db") if False else MagicMock():  # skip
        mock_db.get.return_value = None  # no alert (person not "monitorado")
        _process_track(mock_db, video_id=1, track=track,
                       person_counter=0, alerted_in_this_video=set())

    mock_save_sample.assert_called_once()
    _, kwargs = mock_save_sample.call_args
    # embedding keyword arg deve estar presente
    assert "embedding" in kwargs
    np.testing.assert_array_equal(kwargs["embedding"], mean_emb)


def test_process_track_creates_new_person_when_no_match():
    """_process_track deve criar nova pessoa quando sem match."""
    from app.workers.video_worker import _process_track

    mock_db = MagicMock()
    track = _make_track()
    mean_emb = track.mean_embedding()

    with patch("app.workers.video_worker.person_service.get_all_embeddings",
               return_value=[]), \
         patch("app.workers.video_worker.face_service.find_matching_person",
               return_value=(None, None)), \
         patch("app.workers.video_worker.person_service.save_new_person") as mock_save_new:
        new_counter = _process_track(mock_db, video_id=1, track=track,
                                     person_counter=5, alerted_in_this_video=set())

    assert new_counter == 6
    mock_save_new.assert_called_once()


def test_get_adaptive_params_does_not_exist():
    """get_adaptive_params foi removido — não deve existir no módulo."""
    import app.workers.video_worker as ww
    assert not hasattr(ww, "get_adaptive_params"), (
        "get_adaptive_params deve ter sido removido após migração para InsightFace"
    )
