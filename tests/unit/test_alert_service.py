import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.models import Base, Alert, Person, Video, VideoStatus


@pytest.fixture
def db():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    engine.dispose()


@pytest.fixture
def person_and_video(db):
    p = Person(name="Teste", profile_image_path="faces/1.jpg")
    db.add(p)
    v = Video(file_name="video.mp4", file_path="storage/videos/video.mp4", status=VideoStatus.CONCLUIDO)
    db.add(v)
    db.commit()
    return p, v


def test_create_alert_persiste_com_campos_corretos(db, person_and_video):
    from app.services.alert_service import create_alert
    p, v = person_and_video
    alert = create_alert(db, person_id=p.id, video_id=v.id,
                         timestamp_in_video=5.0, message="Alerta teste")
    assert alert.id is not None
    assert alert.person_id == p.id
    assert alert.video_id == v.id
    assert alert.timestamp_in_video == 5.0
    assert alert.message == "Alerta teste"
    assert alert.seen is False


def test_list_alerts_retorna_vazio_quando_banco_vazio(db):
    from app.services.alert_service import list_alerts
    result = list_alerts(db)
    assert result == []


def test_list_alerts_unseen_only_filtra_corretamente(db, person_and_video):
    from app.services.alert_service import create_alert, list_alerts, mark_alerts_seen
    p, v = person_and_video
    a1 = create_alert(db, p.id, v.id, 1.0, "msg1")
    a2 = create_alert(db, p.id, v.id, 2.0, "msg2")
    mark_alerts_seen(db, [a1.id])

    unseen = list_alerts(db, unseen_only=True)
    assert len(unseen) == 1
    assert unseen[0].id == a2.id


def test_list_alerts_ordena_por_created_at_desc(db, person_and_video):
    from app.services.alert_service import create_alert, list_alerts
    p, v = person_and_video
    a1 = create_alert(db, p.id, v.id, 1.0, "primeiro")
    a2 = create_alert(db, p.id, v.id, 2.0, "segundo")
    result = list_alerts(db)
    # mais recente primeiro
    assert result[0].id == a2.id
    assert result[1].id == a1.id


def test_mark_alerts_seen_atualiza_ids_corretos(db, person_and_video):
    from app.services.alert_service import create_alert, mark_alerts_seen
    p, v = person_and_video
    a1 = create_alert(db, p.id, v.id, 1.0, "msg1")
    a2 = create_alert(db, p.id, v.id, 2.0, "msg2")
    updated = mark_alerts_seen(db, [a1.id])
    db.refresh(a1)
    db.refresh(a2)
    assert updated == 1
    assert a1.seen is True
    assert a2.seen is False


def test_get_unseen_count_retorna_zero_quando_tudo_visto(db, person_and_video):
    from app.services.alert_service import create_alert, mark_alerts_seen, get_unseen_count
    p, v = person_and_video
    a = create_alert(db, p.id, v.id, 1.0, "msg")
    mark_alerts_seen(db, [a.id])
    assert get_unseen_count(db) == 0
