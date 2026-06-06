import pytest
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

    app_obj = upsert_appearance(session, person_id, video_id, timestamp=5.0, confidence=0.3)

    assert app_obj.id is not None
    assert app_obj.timestamp_start == 5.0
    assert app_obj.timestamp_end is None
    assert app_obj.confidence == 0.3


def test_continuous_appearance_extends_timestamp_end(db_session):
    from app.services.appearance_service import upsert_appearance
    session, person_id, video_id = db_session

    upsert_appearance(session, person_id, video_id, timestamp=5.0, confidence=0.3)
    app_obj = upsert_appearance(session, person_id, video_id, timestamp=6.5, confidence=0.25)

    appearances = session.query(Appearance).all()
    assert len(appearances) == 1
    assert app_obj.timestamp_end == 6.5


def test_gap_creates_new_record(db_session):
    from app.services.appearance_service import upsert_appearance
    session, person_id, video_id = db_session

    upsert_appearance(session, person_id, video_id, timestamp=5.0, confidence=0.3)
    # gap de 10s — acima da tolerância de 2s
    app_obj2 = upsert_appearance(session, person_id, video_id, timestamp=17.0, confidence=0.4)

    appearances = session.query(Appearance).all()
    assert len(appearances) == 2
    assert app_obj2.timestamp_start == 17.0


def test_confidence_updated_if_better(db_session):
    from app.services.appearance_service import upsert_appearance
    session, person_id, video_id = db_session

    upsert_appearance(session, person_id, video_id, timestamp=5.0, confidence=0.5)
    app_obj = upsert_appearance(session, person_id, video_id, timestamp=6.0, confidence=0.2)

    assert app_obj.confidence == pytest.approx(0.2)


def test_confidence_not_downgraded(db_session):
    from app.services.appearance_service import upsert_appearance
    session, person_id, video_id = db_session

    upsert_appearance(session, person_id, video_id, timestamp=5.0, confidence=0.2)
    app_obj = upsert_appearance(session, person_id, video_id, timestamp=6.0, confidence=0.5)

    assert app_obj.confidence == pytest.approx(0.2)
