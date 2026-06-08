from pathlib import Path
from unittest.mock import patch, MagicMock
import numpy as np
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.models import Base
from app.models.person import Person, PersonCategory
from app.models.video import Video, VideoStatus


@pytest.fixture(autouse=True)
def mock_can_opencv_read():
    with patch("app.services.conversion_service.can_opencv_read", return_value=True) as mock:
        yield mock


@pytest.fixture(autouse=True)
def disable_motion_gating_by_default():
    from app.core.settings import settings
    original = settings.MOTION_GATING_ENABLED
    settings.MOTION_GATING_ENABLED = False
    yield
    settings.MOTION_GATING_ENABLED = original



@pytest.fixture
def db_engine():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,  # uma conexão única compartilhada entre sessions
    )
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture
def video_in_db(db_engine):
    Session = sessionmaker(bind=db_engine)
    session = Session()
    video = Video(
        file_name="test.mp4",
        file_path="storage/videos/test.mp4",
        status=VideoStatus.PENDENTE,
    )
    session.add(video)
    session.commit()
    session.refresh(video)
    video_id = video.id
    session.close()
    return db_engine, video_id


def get_video_status(engine, video_id: int) -> VideoStatus:
    Session = sessionmaker(bind=engine)
    session = Session()
    video = session.get(Video, video_id)
    status = video.status
    session.close()
    return status


def _make_monitored_person(engine) -> int:
    Session = sessionmaker(bind=engine)
    session = Session()
    p = Person(name="Suspeito", profile_image_path="faces/99.jpg",
               category=PersonCategory.monitorado.value)
    session.add(p)
    session.commit()
    pid = p.id
    session.close()
    return pid


# Frames próximos o bastante para formarem um único track (gap <= FACE_TRACK_GAP_TOLERANCE)
# e em quantidade >= FACE_TRACK_MIN_SAMPLES para o track não ser descartado.
TRACK_FRAMES = [(0, "f0"), (1, "f1")]


def _frame_iter(fake_frame):
    return iter([(seg, fake_frame) for seg, _ in TRACK_FRAMES])


# ── status transitions ────────────────────────────────────────────────────────

def test_status_changes_to_processando_then_concluido(video_in_db):
    from app.workers.video_worker import process_video

    engine, video_id = video_in_db

    with patch("app.workers.video_worker.frame_service.extract_frames", return_value=iter([])), \
         patch("app.workers.video_worker.person_service.get_all_embeddings", return_value=[]):
        process_video(video_id, Path("video.mp4"), _engine=engine)

    assert get_video_status(engine, video_id) == VideoStatus.CONCLUIDO


def test_status_changes_to_erro_on_exception(video_in_db):
    from app.workers.video_worker import process_video

    engine, video_id = video_in_db

    with patch("app.workers.video_worker.frame_service.extract_frames",
               side_effect=RuntimeError("boom")):
        process_video(video_id, Path("video.mp4"), _engine=engine)

    assert get_video_status(engine, video_id) == VideoStatus.ERRO


# ── track novo → save_new_person ──────────────────────────────────────────────

def test_new_track_calls_save_new_person(video_in_db):
    from app.workers.video_worker import process_video

    engine, video_id = video_in_db
    embedding = np.random.rand(128)
    fake_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    location = (0, 120, 120, 0)

    with patch("app.workers.video_worker.frame_service.extract_frames",
               return_value=_frame_iter(fake_frame)), \
         patch("app.workers.video_worker.face_service.extract_embeddings",
               return_value=[(embedding, location, 0.95)]), \
         patch("app.workers.video_worker.person_service.get_all_embeddings",
               return_value=[]), \
         patch("app.workers.video_worker.face_service.find_matching_person",
               return_value=(None, None)), \
         patch("app.workers.video_worker.person_service.save_new_person") as mock_save:
        mock_save.return_value = MagicMock(id=99)
        process_video(video_id, Path("video.mp4"), _engine=engine)

    mock_save.assert_called_once()


def test_short_track_is_discarded_and_does_not_create_person(video_in_db):
    """Track com menos amostras que FACE_TRACK_MIN_SAMPLES é descartado —
    não deve gerar pessoa nem aparição."""
    from app.workers.video_worker import process_video

    engine, video_id = video_in_db
    embedding = np.random.rand(128)
    fake_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    location = (0, 120, 120, 0)

    with patch("app.workers.video_worker.frame_service.extract_frames",
               return_value=iter([(0, fake_frame)])), \
         patch("app.workers.video_worker.face_service.extract_embeddings",
               return_value=[(embedding, location, 0.95)]), \
         patch("app.workers.video_worker.person_service.get_all_embeddings",
               return_value=[]), \
         patch("app.workers.video_worker.face_service.find_matching_person") as mock_match, \
         patch("app.workers.video_worker.person_service.save_new_person") as mock_save:
        process_video(video_id, Path("video.mp4"), _engine=engine)

    mock_match.assert_not_called()
    mock_save.assert_not_called()


# ── track conhecido → upsert_appearance ───────────────────────────────────────

def test_known_track_calls_upsert_appearance(video_in_db):
    from app.workers.video_worker import process_video

    engine, video_id = video_in_db
    embedding = np.random.rand(128)
    fake_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    location = (0, 120, 120, 0)

    with patch("app.workers.video_worker.frame_service.extract_frames",
               return_value=_frame_iter(fake_frame)), \
         patch("app.workers.video_worker.face_service.extract_embeddings",
               return_value=[(embedding, location, 0.95)]), \
         patch("app.workers.video_worker.person_service.get_all_embeddings",
               return_value=[(7, embedding)]), \
         patch("app.workers.video_worker.face_service.find_matching_person",
               return_value=(7, 0.3)), \
         patch("app.workers.video_worker.appearance_service.upsert_appearance") as mock_upsert:
        mock_upsert.return_value = MagicMock()
        process_video(video_id, Path("video.mp4"), _engine=engine)

    mock_upsert.assert_called_once()
    args, kwargs = mock_upsert.call_args
    person_id_arg = kwargs.get("person_id") or args[1]
    assert person_id_arg == 7


def test_matching_uses_track_mean_embedding(video_in_db):
    """find_matching_person deve receber o embedding médio do track,
    não o embedding de um frame isolado."""
    from app.workers.video_worker import process_video

    engine, video_id = video_in_db
    rng = np.random.default_rng(7)
    emb1 = rng.random(512).astype(np.float32)
    emb2 = rng.random(512).astype(np.float32)
    fake_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    location = (0, 120, 120, 0)

    with patch("app.workers.video_worker.frame_service.extract_frames",
               return_value=_frame_iter(fake_frame)), \
         patch("app.workers.video_worker.face_service.extract_embeddings",
               side_effect=[[(emb1, location, 0.95)], [(emb2, location, 0.95)]]), \
         patch("app.workers.video_worker.person_service.get_all_embeddings",
               return_value=[]), \
         patch("app.workers.video_worker.face_service.find_matching_person",
               return_value=(None, None)) as mock_match, \
         patch("app.workers.video_worker.person_service.save_new_person",
               return_value=MagicMock(id=99)):
        process_video(video_id, Path("video.mp4"), _engine=engine)

    mock_match.assert_called_once()
    used_embedding = mock_match.call_args[0][0]
    raw_mean = np.mean([emb1, emb2], axis=0).astype(np.float32)
    expected_mean = raw_mean / np.linalg.norm(raw_mean)
    assert np.allclose(used_embedding, expected_mean)


# ── watchlist: alertas para Monitorado ───────────────────────────────────────

def test_monitorado_dispara_create_alert(video_in_db):
    from app.workers.video_worker import process_video

    engine, video_id = video_in_db
    person_id = _make_monitored_person(engine)
    embedding = np.random.rand(128)
    fake_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    location = (0, 120, 120, 0)

    with patch("app.workers.video_worker.frame_service.extract_frames",
               return_value=_frame_iter(fake_frame)), \
         patch("app.workers.video_worker.face_service.extract_embeddings",
               return_value=[(embedding, location, 0.95)]), \
         patch("app.workers.video_worker.person_service.get_all_embeddings",
               return_value=[(person_id, embedding)]), \
         patch("app.workers.video_worker.face_service.find_matching_person",
               return_value=(person_id, 0.25)), \
         patch("app.workers.video_worker.appearance_service.upsert_appearance",
               return_value=MagicMock()), \
         patch("app.workers.video_worker.alert_service.create_alert") as mock_alert:
        mock_alert.return_value = MagicMock(id=1)
        process_video(video_id, Path("video.mp4"), _engine=engine)

    mock_alert.assert_called_once()
    kwargs = mock_alert.call_args.kwargs
    assert kwargs["person_id"] == person_id
    assert kwargs["video_id"] == video_id


def test_funcionario_nao_dispara_alerta(video_in_db):
    from app.workers.video_worker import process_video

    engine, video_id = video_in_db
    Session = sessionmaker(bind=engine)
    session = Session()
    p = Person(name="Func", profile_image_path="faces/2.jpg",
               category=PersonCategory.funcionario.value)
    session.add(p)
    session.commit()
    person_id = p.id
    session.close()

    embedding = np.random.rand(128)
    fake_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    location = (0, 120, 120, 0)

    with patch("app.workers.video_worker.frame_service.extract_frames",
               return_value=_frame_iter(fake_frame)), \
         patch("app.workers.video_worker.face_service.extract_embeddings",
               return_value=[(embedding, location, 0.95)]), \
         patch("app.workers.video_worker.person_service.get_all_embeddings",
               return_value=[(person_id, embedding)]), \
         patch("app.workers.video_worker.face_service.find_matching_person",
               return_value=(person_id, 0.25)), \
         patch("app.workers.video_worker.appearance_service.upsert_appearance",
               return_value=MagicMock()), \
         patch("app.workers.video_worker.alert_service.create_alert") as mock_alert:
        process_video(video_id, Path("video.mp4"), _engine=engine)

    mock_alert.assert_not_called()


def test_alerta_criado_apenas_uma_vez_por_pessoa_por_video(video_in_db):
    """2 tracks da mesma pessoa monitorada (gap > tolerância entre eles)
    → apenas 1 alerta no vídeo todo."""
    from app.workers.video_worker import process_video

    engine, video_id = video_in_db
    person_id = _make_monitored_person(engine)
    embedding = np.random.rand(128)
    fake_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    location = (0, 120, 120, 0)

    # track 1: segundos 0,1 — track 2: segundos 10,11 (gap=9s > FACE_TRACK_GAP_TOLERANCE)
    frames = iter([(0, fake_frame), (1, fake_frame), (10, fake_frame), (11, fake_frame)])

    with patch("app.workers.video_worker.frame_service.extract_frames",
               return_value=frames), \
         patch("app.workers.video_worker.face_service.extract_embeddings",
               return_value=[(embedding, location, 0.95)]), \
         patch("app.workers.video_worker.person_service.get_all_embeddings",
               return_value=[(person_id, embedding)]), \
         patch("app.workers.video_worker.face_service.find_matching_person",
               return_value=(person_id, 0.25)), \
         patch("app.workers.video_worker.appearance_service.upsert_appearance",
               return_value=MagicMock()), \
         patch("app.workers.video_worker.alert_service.create_alert") as mock_alert:
        mock_alert.return_value = MagicMock(id=1)
        process_video(video_id, Path("video.mp4"), _engine=engine)

    assert mock_alert.call_count == 1


def test_motion_gating_disabled_processes_all_frames(video_in_db):
    from app.workers.video_worker import process_video
    from app.core.settings import settings
    
    engine, video_id = video_in_db
    frame1 = np.zeros((100, 100, 3), dtype=np.uint8)
    frame2 = np.zeros((100, 100, 3), dtype=np.uint8) # Idêntico
    
    frames = [(0, frame1), (1, frame2)]
    
    with patch("app.workers.video_worker.frame_service.extract_frames", return_value=iter(frames)), \
         patch("app.workers.video_worker.face_service.extract_embeddings", return_value=[]) as mock_extract, \
         patch("app.workers.video_worker.settings", MagicMock(MOTION_GATING_ENABLED=False, DATABASE_URL=settings.DATABASE_URL)):
        
        process_video(video_id, Path("video.mp4"), _engine=engine)
        
    assert mock_extract.call_count == 2


def test_motion_gating_enabled_skips_static_frames(video_in_db):
    from app.workers.video_worker import process_video
    from app.core.settings import settings
    
    engine, video_id = video_in_db
    frame1 = np.zeros((100, 100, 3), dtype=np.uint8)
    frame2 = np.zeros((100, 100, 3), dtype=np.uint8) # Idêntico
    
    frames = [(0, frame1), (1, frame2)]
    
    with patch("app.workers.video_worker.frame_service.extract_frames", return_value=iter(frames)), \
         patch("app.workers.video_worker.face_service.extract_embeddings", return_value=[]) as mock_extract, \
         patch("app.workers.video_worker.settings", MagicMock(
             MOTION_GATING_ENABLED=True,
             MOTION_GATING_THRESHOLD=25,
             MOTION_GATING_AREA_RATIO=0.005,
             MOTION_GATING_FORCE_INTERVAL=999,
             DATABASE_URL=settings.DATABASE_URL,
             STORAGE_VIDEOS=settings.STORAGE_VIDEOS
         )):

        process_video(video_id, Path("video.mp4"), _engine=engine)

    assert mock_extract.call_count == 1


def test_motion_gating_enabled_processes_moving_frames(video_in_db):
    from app.workers.video_worker import process_video
    from app.core.settings import settings
    
    engine, video_id = video_in_db
    frame1 = np.zeros((100, 100, 3), dtype=np.uint8)
    frame2 = np.zeros((100, 100, 3), dtype=np.uint8)
    frame2[40:60, 40:60] = 255 # Movimento bem acima de 0.5% (20*20 = 400 pixels = 4%)
    
    frames = [(0, frame1), (1, frame2)]
    
    with patch("app.workers.video_worker.frame_service.extract_frames", return_value=iter(frames)), \
         patch("app.workers.video_worker.face_service.extract_embeddings", return_value=[]) as mock_extract, \
         patch("app.workers.video_worker.settings", MagicMock(
             MOTION_GATING_ENABLED=True,
             MOTION_GATING_THRESHOLD=25,
             MOTION_GATING_AREA_RATIO=0.005,
             MOTION_GATING_FORCE_INTERVAL=999,
             DATABASE_URL=settings.DATABASE_URL,
             STORAGE_VIDEOS=settings.STORAGE_VIDEOS
         )):

        process_video(video_id, Path("video.mp4"), _engine=engine)

    assert mock_extract.call_count == 2



# ── Task 1: person_counter usa contagem de pessoas ────────────────────────────

def test_person_counter_usa_contagem_de_pessoas(db_engine):
    """Nova pessoa deve receber índice baseado em Person.count, não Video.count."""
    from app.workers.video_worker import process_video
    from sqlalchemy.orm import sessionmaker as SM

    S = SM(bind=db_engine)
    s = S()

    # 3 pessoas existentes
    for i in range(3):
        s.add(Person(name=f"Existente {i}", profile_image_path=f"faces/{i}.jpg"))

    # 7 vídeos — o índice NÃO deve ser baseado neles
    for _ in range(7):
        s.add(Video(file_name="x.mp4", file_path="storage/videos/x.mp4",
                    status=VideoStatus.PENDENTE))

    # vídeo alvo
    target = Video(file_name="test.mp4", file_path="storage/videos/test.mp4",
                   status=VideoStatus.PENDENTE)
    s.add(target)
    s.commit()
    video_id = target.id
    s.close()

    emb = np.zeros(512, dtype=np.float32); emb[0] = 1.0
    fake_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    location = (0, 120, 120, 0)

    with patch("app.workers.video_worker.frame_service.extract_frames",
               return_value=_frame_iter(fake_frame)), \
         patch("app.workers.video_worker.face_service.extract_embeddings",
               return_value=[(emb, location, 0.95)]), \
         patch("app.workers.video_worker.person_service.get_all_embeddings",
               return_value=[]), \
         patch("app.workers.video_worker.face_service.find_matching_person",
               return_value=(None, None)), \
         patch("app.workers.video_worker.person_service.save_new_person") as mock_save:
        mock_save.return_value = MagicMock(id=99)
        process_video(video_id, Path("video.mp4"), _engine=db_engine)

    mock_save.assert_called_once()
    _, kwargs = mock_save.call_args
    person_index = kwargs.get("person_index") or mock_save.call_args[0][3]
    # 3 pessoas → próxima deve ser #4, não #8 (que seria Video.count)
    assert person_index == 4, f"Esperado 4 (Person.count+1), recebido {person_index}"


# ── Task 2: get_all_embeddings chamado 1x por vídeo ──────────────────────────

def test_get_all_embeddings_chamado_uma_vez_por_video(video_in_db):
    """get_all_embeddings deve ser chamado 1x por vídeo, não por track."""
    from app.workers.video_worker import process_video

    engine, video_id = video_in_db
    emb = np.zeros(512, dtype=np.float32); emb[0] = 1.0
    fake_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    location = (0, 120, 120, 0)

    # 3 tracks distintos (gaps > FACE_TRACK_GAP_TOLERANCE)
    frames_3_tracks = iter([
        (0, fake_frame), (1, fake_frame),   # track 1
        (10, fake_frame), (11, fake_frame),  # track 2 (gap=9s > tolerance=2s)
        (20, fake_frame), (21, fake_frame),  # track 3
    ])

    with patch("app.workers.video_worker.frame_service.extract_frames",
               return_value=frames_3_tracks), \
         patch("app.workers.video_worker.face_service.extract_embeddings",
               return_value=[(emb, location, 0.95)]), \
         patch("app.workers.video_worker.face_service.find_matching_person",
               return_value=(None, None)), \
         patch("app.workers.video_worker.person_service.save_new_person",
               return_value=MagicMock(id=99)), \
         patch("app.workers.video_worker.person_service.get_all_embeddings") as mock_get_embs:
        mock_get_embs.return_value = []
        process_video(video_id, Path("video.mp4"), _engine=engine)

    assert mock_get_embs.call_count == 1, (
        f"get_all_embeddings chamado {mock_get_embs.call_count}x — devia ser 1x por vídeo"
    )


# ── Task 4: Motion Gating força detecção periódica ────────────────────────────

def test_motion_gating_forca_deteccao_periodica(video_in_db):
    """Mesmo sem movimento, detecção deve rodar a cada MOTION_GATING_FORCE_INTERVAL segundos."""
    from app.workers.video_worker import process_video
    from app.core.settings import settings

    engine, video_id = video_in_db
    settings.MOTION_GATING_ENABLED = True

    fake_frame = np.zeros((480, 640, 3), dtype=np.uint8)

    # 12 frames de 0..11s — todos estáticos (has_motion retorna False)
    all_frames = iter([(s, fake_frame) for s in range(12)])

    with patch("app.workers.video_worker.frame_service.extract_frames",
               return_value=all_frames), \
         patch("app.workers.video_worker.frame_service.has_motion",
               return_value=(False, 0.0)), \
         patch("app.workers.video_worker.person_service.get_all_embeddings",
               return_value=[]), \
         patch("app.workers.video_worker.face_service.extract_embeddings",
               return_value=[]) as mock_extract:
        process_video(video_id, Path("video.mp4"), _engine=engine)

    settings.MOTION_GATING_ENABLED = False

    # Com FORCE_INTERVAL=5 e 12s de vídeo, detecção forçada em 0, 5, 10 → ≥3 chamadas
    assert mock_extract.call_count >= 3, (
        f"Detecção forçada esperada ≥3x em 12s com interval=5, recebido {mock_extract.call_count}"
    )
