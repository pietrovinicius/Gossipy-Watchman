import csv
import io
from datetime import datetime, timezone

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Base, Person
from app.models.appearance import Appearance
from app.models.video import Video, VideoStatus


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    engine.dispose()


def _make_video(db, name="v.mp4"):
    v = Video(
        file_name=name,
        file_path=f"storage/videos/{name}",
        status=VideoStatus.CONCLUIDO,
        uploaded_at=datetime(2026, 6, 1, tzinfo=timezone.utc),
    )
    db.add(v)
    db.commit()
    db.refresh(v)
    return v


def _make_person(db, name="João"):
    p = Person(name=name, category="Funcionário")
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


def _make_appearance(db, person_id, video_id, start=0.0, end=5.0, confidence=0.3):
    a = Appearance(
        person_id=person_id,
        video_id=video_id,
        timestamp_start=start,
        timestamp_end=end,
        confidence=confidence,
    )
    db.add(a)
    db.commit()
    return a


# ── testes ──────────────────────────────────────────────────────────────────

def test_empty_db_generates_csv_with_header_only(db_session):
    from app.services.export_service import generate_timeline_csv

    csv_str = generate_timeline_csv(db_session)
    lines = csv_str.strip().splitlines()
    # primeiras 3 linhas = comentários de auditoria
    assert lines[0].startswith("# Gossipy Watchman")
    assert lines[1].startswith("# Gerado em:")
    assert lines[2].startswith("# Total de registros: 0")
    # 4ª linha = header CSV
    assert "pessoa_id" in lines[3]


def test_audit_comment_is_first_line(db_session):
    from app.services.export_service import generate_timeline_csv

    csv_str = generate_timeline_csv(db_session)
    assert csv_str.startswith("# Gossipy Watchman")


def test_header_contains_all_9_columns(db_session):
    from app.services.export_service import generate_timeline_csv

    csv_str = generate_timeline_csv(db_session)
    # extrair linha de header (4ª linha, índice 3)
    header_line = csv_str.strip().splitlines()[3]
    reader = csv.reader([header_line])
    cols = next(reader)
    expected = {
        "pessoa_id", "pessoa_nome", "pessoa_categoria",
        "video_id", "video_arquivo",
        "entrada_segundos", "saida_segundos", "duracao_segundos", "confianca",
    }
    assert expected == set(cols)


def test_filter_by_person_id(db_session):
    from app.services.export_service import generate_timeline_csv

    v = _make_video(db_session)
    p1 = _make_person(db_session, "João")
    p2 = _make_person(db_session, "Maria")
    _make_appearance(db_session, p1.id, v.id)
    _make_appearance(db_session, p2.id, v.id)

    csv_str = generate_timeline_csv(db_session, person_id=p1.id)
    data_lines = [l for l in csv_str.splitlines() if not l.startswith("#") and l.strip() and "pessoa_id" not in l]
    assert len(data_lines) == 1
    assert "João" in csv_str
    assert "Maria" not in csv_str


def test_filter_by_video_id(db_session):
    from app.services.export_service import generate_timeline_csv

    v1 = _make_video(db_session, "v1.mp4")
    v2 = _make_video(db_session, "v2.mp4")
    p = _make_person(db_session)
    _make_appearance(db_session, p.id, v1.id)
    _make_appearance(db_session, p.id, v2.id)

    csv_str = generate_timeline_csv(db_session, video_id=v1.id)
    data_lines = [l for l in csv_str.splitlines() if not l.startswith("#") and l.strip() and "pessoa_id" not in l]
    assert len(data_lines) == 1
    assert "v1.mp4" in csv_str
    assert "v2.mp4" not in csv_str


def test_no_filter_returns_all_appearances(db_session):
    from app.services.export_service import generate_timeline_csv

    v = _make_video(db_session)
    p1 = _make_person(db_session, "João")
    p2 = _make_person(db_session, "Maria")
    _make_appearance(db_session, p1.id, v.id, start=0.0, end=3.0)
    _make_appearance(db_session, p2.id, v.id, start=5.0, end=8.0)

    csv_str = generate_timeline_csv(db_session)
    data_lines = [l for l in csv_str.splitlines() if not l.startswith("#") and l.strip() and "pessoa_id" not in l]
    assert len(data_lines) == 2


def test_duracao_calculada_corretamente(db_session):
    from app.services.export_service import generate_timeline_csv

    v = _make_video(db_session)
    p = _make_person(db_session)
    _make_appearance(db_session, p.id, v.id, start=2.0, end=7.5, confidence=0.3)

    csv_str = generate_timeline_csv(db_session)
    # parsear dados
    reader = csv.DictReader(
        [l for l in csv_str.splitlines() if not l.startswith("#")]
    )
    row = next(reader)
    assert float(row["duracao_segundos"]) == pytest.approx(5.5)


def test_duracao_vazia_quando_timestamp_end_none(db_session):
    from app.services.export_service import generate_timeline_csv

    v = _make_video(db_session)
    p = _make_person(db_session)
    a = Appearance(person_id=p.id, video_id=v.id, timestamp_start=1.0, timestamp_end=None, confidence=0.4)
    db_session.add(a)
    db_session.commit()

    csv_str = generate_timeline_csv(db_session)
    reader = csv.DictReader(
        [l for l in csv_str.splitlines() if not l.startswith("#")]
    )
    row = next(reader)
    assert row["duracao_segundos"] == ""
    assert row["saida_segundos"] == ""
