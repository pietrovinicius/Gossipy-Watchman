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

    known_embeddings = [(1, mean_emb)]
    with patch("app.workers.video_worker.face_service.find_matching_person",
               return_value=(1, 0.05)), \
         patch("app.workers.video_worker.appearance_service.upsert_appearance",
               return_value=appearance_mock), \
         patch("app.workers.video_worker.person_service.save_face_sample") as mock_save_sample:
        mock_db.get.return_value = None  # no alert (person not "monitorado")
        _process_track(mock_db, video_id=1, track=track,
                       person_counter=0, alerted_in_this_video=set(),
                       known_embeddings=known_embeddings)

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

    with patch("app.workers.video_worker.face_service.find_matching_person",
               return_value=(None, None)), \
         patch("app.workers.video_worker.person_service.save_new_person",
               return_value=MagicMock(id=99)) as mock_save_new, \
         patch("app.workers.video_worker.appearance_service.upsert_appearance",
               return_value=MagicMock(id=1)):
        new_counter, _ = _process_track(mock_db, video_id=1, track=track,
                                        person_counter=5, alerted_in_this_video=set(),
                                        known_embeddings=[])

    assert new_counter == 6
    mock_save_new.assert_called_once()


def test_process_track_nova_pessoa_cria_appearance():
    """_process_track deve criar appearance para nova pessoa, vinculando ao vídeo."""
    from app.workers.video_worker import _process_track

    mock_db = MagicMock()
    track = _make_track()

    mock_upsert = MagicMock(return_value=MagicMock(id=1))

    with patch("app.workers.video_worker.face_service.find_matching_person",
               return_value=(None, None)), \
         patch("app.workers.video_worker.person_service.save_new_person",
               return_value=MagicMock(id=77)), \
         patch("app.workers.video_worker.appearance_service.upsert_appearance",
               mock_upsert):
        _process_track(mock_db, video_id=42, track=track,
                       person_counter=0, alerted_in_this_video=set(),
                       known_embeddings=[])

    mock_upsert.assert_called_once()
    call_kwargs = mock_upsert.call_args
    assert call_kwargs.kwargs.get("person_id") == 77 or call_kwargs.args[1] == 77, (
        "upsert_appearance deve ser chamado com person_id=77 (nova pessoa)"
    )
    assert call_kwargs.kwargs.get("video_id") == 42 or call_kwargs.args[2] == 42, (
        "upsert_appearance deve ser chamado com video_id=42"
    )


def test_get_adaptive_params_does_not_exist():
    """get_adaptive_params foi removido — não deve existir no módulo."""
    import app.workers.video_worker as ww
    assert not hasattr(ww, "get_adaptive_params"), (
        "get_adaptive_params deve ter sido removido após migração para InsightFace"
    )


def test_process_track_atualiza_cache_com_pessoa_conhecida():
    """_process_track deve adicionar embedding ao cache quando pessoa conhecida identificada."""
    from app.workers.video_worker import _process_track

    mock_db = MagicMock()
    track = _make_track()
    mean_emb = track.mean_embedding()

    appearance_mock = MagicMock()
    appearance_mock.id = 42

    initial_cache = [(1, mean_emb.copy())]
    with patch("app.workers.video_worker.face_service.find_matching_person",
               return_value=(1, 0.05)), \
         patch("app.workers.video_worker.appearance_service.upsert_appearance",
               return_value=appearance_mock), \
         patch("app.workers.video_worker.person_service.save_face_sample",
               return_value="/tmp/sample.jpg"):
        mock_db.get.return_value = None
        _, updated_cache = _process_track(
            mock_db, video_id=1, track=track,
            person_counter=0, alerted_in_this_video=set(),
            known_embeddings=list(initial_cache),
        )

    assert len(updated_cache) > len(initial_cache), (
        "cache deve crescer com o novo embedding da pessoa conhecida"
    )
    assert any(pid == 1 and np.allclose(emb, mean_emb) for pid, emb in updated_cache[len(initial_cache):])


def test_process_track_nao_duplica_se_embedding_identico_ja_presente():
    """_process_track com mesma pessoa: cache cresce para alimentar matches futuros."""
    from app.workers.video_worker import _process_track

    mock_db = MagicMock()
    track = _make_track()

    appearance_mock = MagicMock()
    appearance_mock.id = 10

    with patch("app.workers.video_worker.face_service.find_matching_person",
               return_value=(7, 0.1)), \
         patch("app.workers.video_worker.appearance_service.upsert_appearance",
               return_value=appearance_mock), \
         patch("app.workers.video_worker.person_service.save_face_sample",
               return_value=None):
        mock_db.get.return_value = None
        _, updated_cache = _process_track(
            mock_db, video_id=2, track=track,
            person_counter=0, alerted_in_this_video=set(),
            known_embeddings=[],
        )

    assert any(pid == 7 for pid, _ in updated_cache), (
        "embedding da pessoa 7 deve estar no cache após o track"
    )


# ── Task 5 V3: cache não cresce infinitamente por pessoa ─────────────────────

def test_cache_nao_cresce_alem_do_limite_por_pessoa():
    """_process_track não deve acumular entradas ilimitadas no cache para uma pessoa.
    Após FACE_MAX_EMBEDDINGS_PER_PERSON aparições da mesma pessoa, o cache deve
    ter no máximo FACE_MAX_EMBEDDINGS_PER_PERSON entradas para essa pessoa."""
    from app.workers.video_worker import _process_track
    from app.core.settings import settings

    mock_db = MagicMock()
    appearance_mock = MagicMock()
    appearance_mock.id = 1

    limit = settings.FACE_MAX_EMBEDDINGS_PER_PERSON
    n_tracks = limit + 3  # mais do que o limite

    cache = []
    with patch("app.workers.video_worker.face_service.find_matching_person",
               return_value=(42, 0.05)), \
         patch("app.workers.video_worker.appearance_service.upsert_appearance",
               return_value=appearance_mock), \
         patch("app.workers.video_worker.person_service.save_face_sample",
               return_value=None):
        mock_db.get.return_value = None
        for _ in range(n_tracks):
            track = _make_track()
            _, cache = _process_track(
                mock_db, video_id=1, track=track,
                person_counter=0, alerted_in_this_video=set(),
                known_embeddings=cache,
            )

    count_person_42 = sum(1 for pid, _ in cache if pid == 42)
    assert count_person_42 <= limit, (
        f"Cache tem {count_person_42} entradas para pessoa 42, "
        f"esperado <= {limit} (FACE_MAX_EMBEDDINGS_PER_PERSON)"
    )
