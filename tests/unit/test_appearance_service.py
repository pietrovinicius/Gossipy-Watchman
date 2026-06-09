import pytest
from datetime import datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Base, Appearance
from app.models.video import VideoStatus
from app.models.person import Person
from app.models.video import Video


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    person = Person(name="Desconhecido #1")
    video = Video(file_name="test.mp4", file_path="storage/videos/test.mp4", status=VideoStatus.PROCESSANDO)
    session.add_all([person, video])
    session.commit()
    session.refresh(person)
    session.refresh(video)

    yield session, person.id, video.id
    session.close()
    engine.dispose()


def test_first_appearance_creates_new_record(db_session):
    from app.services.appearance_service import upsert_appearance
    session, person_id, video_id = db_session

    app_obj = upsert_appearance(session, person_id, video_id,
                                timestamp_start=5.0, timestamp_end=5.0, confidence=0.3)

    assert app_obj.id is not None
    assert app_obj.timestamp_start == 5.0
    assert app_obj.timestamp_end == pytest.approx(5.0)
    assert app_obj.confidence == 0.3


def test_continuous_appearance_extends_timestamp_end(db_session):
    from app.services.appearance_service import upsert_appearance
    session, person_id, video_id = db_session

    upsert_appearance(session, person_id, video_id, timestamp_start=5.0, timestamp_end=5.0, confidence=0.3)
    app_obj = upsert_appearance(session, person_id, video_id, timestamp_start=6.5, timestamp_end=6.5, confidence=0.25)

    appearances = session.query(Appearance).all()
    assert len(appearances) == 1
    assert app_obj.timestamp_end == pytest.approx(6.5)


def test_gap_creates_new_record(db_session):
    from app.services.appearance_service import upsert_appearance
    session, person_id, video_id = db_session

    upsert_appearance(session, person_id, video_id, timestamp_start=5.0, timestamp_end=5.0, confidence=0.3)
    # gap de 10s — acima da tolerância de 2s
    app_obj2 = upsert_appearance(session, person_id, video_id, timestamp_start=17.0, timestamp_end=17.0, confidence=0.4)

    appearances = session.query(Appearance).all()
    assert len(appearances) == 2
    assert app_obj2.timestamp_start == 17.0


def test_confidence_updated_if_better(db_session):
    from app.services.appearance_service import upsert_appearance
    session, person_id, video_id = db_session

    upsert_appearance(session, person_id, video_id, timestamp_start=5.0, timestamp_end=5.0, confidence=0.5)
    app_obj = upsert_appearance(session, person_id, video_id, timestamp_start=6.0, timestamp_end=6.0, confidence=0.2)

    assert app_obj.confidence == pytest.approx(0.2)


def test_confidence_not_downgraded(db_session):
    from app.services.appearance_service import upsert_appearance
    session, person_id, video_id = db_session

    upsert_appearance(session, person_id, video_id, timestamp_start=5.0, timestamp_end=5.0, confidence=0.2)
    app_obj = upsert_appearance(session, person_id, video_id, timestamp_start=6.0, timestamp_end=6.0, confidence=0.5)

    assert app_obj.confidence == pytest.approx(0.2)


# ── Task 6: gap tolerance deve vir de settings, não hardcoded ─────────────────

def test_upsert_usa_gap_tolerance_de_settings(db_session):
    """Aparição a 8s deve ser estendida quando gap_tolerance=10s via settings."""
    from unittest.mock import patch
    from app.services.appearance_service import upsert_appearance
    from app.models import Appearance
    session, person_id, video_id = db_session

    with patch("app.services.appearance_service.settings") as mock_s:
        mock_s.FACE_TRACK_GAP_TOLERANCE = 10.0
        upsert_appearance(session, person_id, video_id, timestamp_start=0.0, timestamp_end=0.0, confidence=0.1)
        app2 = upsert_appearance(session, person_id, video_id, timestamp_start=8.0, timestamp_end=8.0, confidence=0.2)

    appearances = session.query(Appearance).filter(
        Appearance.person_id == person_id,
        Appearance.video_id == video_id,
    ).all()
    assert len(appearances) == 1, (
        "8s deve ser dentro do gap de 10s → mesma aparição estendida; "
        "se 2 registros, gap_tolerance está hardcoded em 2.0"
    )
    assert app2.timestamp_end == pytest.approx(8.0)


def test_upsert_cria_nova_aparicao_quando_gap_settings_excedido(db_session):
    """Aparição a 15s deve criar novo registro quando gap_tolerance=10s."""
    from unittest.mock import patch
    from app.services.appearance_service import upsert_appearance
    from app.models import Appearance
    session, person_id, video_id = db_session

    with patch("app.services.appearance_service.settings") as mock_s:
        mock_s.FACE_TRACK_GAP_TOLERANCE = 10.0
        app1 = upsert_appearance(session, person_id, video_id, timestamp_start=0.0, timestamp_end=0.0, confidence=0.1)
        app2 = upsert_appearance(session, person_id, video_id, timestamp_start=15.0, timestamp_end=15.0, confidence=0.2)

    assert app1.id != app2.id


# ── Task 1 V3: timestamp_end deve refletir track.last_seen ────────────────────

def test_upsert_grava_timestamp_end_correto(db_session):
    """timestamp_end deve refletir fim real do track, não start."""
    from app.services.appearance_service import upsert_appearance
    session, person_id, video_id = db_session

    app = upsert_appearance(
        session, person_id, video_id,
        timestamp_start=5.0, timestamp_end=12.0, confidence=0.2,
    )
    assert app.timestamp_start == pytest.approx(5.0)
    assert app.timestamp_end == pytest.approx(12.0)


def test_upsert_estende_para_cobrir_dois_tracks_proximos(db_session):
    """Dois tracks separados por gap < tolerance devem ser mesclados."""
    from app.services.appearance_service import upsert_appearance
    from app.models import Appearance
    session, person_id, video_id = db_session

    # track 1: 0→8s
    upsert_appearance(session, person_id, video_id,
                      timestamp_start=0.0, timestamp_end=8.0, confidence=0.2)
    # track 2: 9→15s (gap=1s < tolerance=2s → deve mesclar)
    upsert_appearance(session, person_id, video_id,
                      timestamp_start=9.0, timestamp_end=15.0, confidence=0.3)

    appearances = session.query(Appearance).filter(
        Appearance.person_id == person_id, Appearance.video_id == video_id
    ).all()
    assert len(appearances) == 1
    assert appearances[0].timestamp_end == pytest.approx(15.0)


def test_upsert_cria_novo_registro_quando_gap_excedido_novo(db_session):
    """Dois tracks separados por gap > tolerance → dois registros distintos."""
    from app.services.appearance_service import upsert_appearance
    from app.models import Appearance
    session, person_id, video_id = db_session

    upsert_appearance(session, person_id, video_id,
                      timestamp_start=0.0, timestamp_end=5.0, confidence=0.2)
    upsert_appearance(session, person_id, video_id,
                      timestamp_start=10.0, timestamp_end=15.0, confidence=0.3)

    appearances = session.query(Appearance).filter(
        Appearance.person_id == person_id, Appearance.video_id == video_id
    ).all()
    assert len(appearances) == 2


# ── add_manual_appearance ─────────────────────────────────────────────────────

@pytest.fixture
def db_session_full():
    """Fixture com vídeo CONCLUIDO para testes de add_manual_appearance."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    person = Person(name="Pessoa Manual")
    video = Video(
        file_name="v.mp4",
        file_path="storage/videos/v.mp4",
        status=VideoStatus.CONCLUIDO,
        uploaded_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )
    session.add_all([person, video])
    session.commit()
    session.refresh(person)
    session.refresh(video)

    yield session, person.id, video.id
    session.close()
    engine.dispose()


def test_add_manual_appearance_cria_nova_aparicao(db_session_full):
    """add_manual_appearance deve criar Appearance com os dados fornecidos."""
    from app.services.appearance_service import add_manual_appearance

    session, person_id, video_id = db_session_full
    app_obj = add_manual_appearance(
        session, video_id=video_id, person_id=person_id,
        timestamp_start=5.0, timestamp_end=10.0, confidence=0.0,
    )

    assert app_obj.id is not None
    assert app_obj.person_id == person_id
    assert app_obj.video_id == video_id
    assert app_obj.timestamp_start == pytest.approx(5.0)
    assert app_obj.timestamp_end == pytest.approx(10.0)
    assert app_obj.confidence == pytest.approx(0.0)


def test_add_manual_appearance_video_nao_encontrado(db_session_full):
    """add_manual_appearance deve lançar 404 quando vídeo não existe."""
    from fastapi import HTTPException
    from app.services.appearance_service import add_manual_appearance

    session, person_id, _ = db_session_full
    with pytest.raises(HTTPException) as exc:
        add_manual_appearance(
            session, video_id=9999, person_id=person_id,
            timestamp_start=0.0, timestamp_end=1.0, confidence=0.0,
        )
    assert exc.value.status_code == 404


def test_add_manual_appearance_pessoa_nao_encontrada(db_session_full):
    """add_manual_appearance deve lançar 404 quando pessoa não existe."""
    from fastapi import HTTPException
    from app.services.appearance_service import add_manual_appearance

    session, _, video_id = db_session_full
    with pytest.raises(HTTPException) as exc:
        add_manual_appearance(
            session, video_id=video_id, person_id=9999,
            timestamp_start=0.0, timestamp_end=1.0, confidence=0.0,
        )
    assert exc.value.status_code == 404
