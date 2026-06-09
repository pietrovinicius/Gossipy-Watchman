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


def _parse_csv(csv_str: str) -> list[dict]:
    data_lines = [l for l in csv_str.splitlines() if not l.startswith("#")]
    reader = csv.DictReader(data_lines, delimiter=";")
    return list(reader)


# ── Estrutura geral ──────────────────────────────────────────────────────────

def test_empty_db_generates_csv_with_header_only(db_session):
    from app.services.export_service import generate_timeline_csv

    csv_str = generate_timeline_csv(db_session)
    lines = csv_str.strip().splitlines()
    assert lines[0].startswith("# Gossipy Watchman")
    assert lines[1].startswith("# Gerado em:")
    assert lines[2].startswith("# Total de registros: 0")
    assert "pessoa_id" in lines[3]


def test_audit_comment_is_first_line(db_session):
    from app.services.export_service import generate_timeline_csv

    csv_str = generate_timeline_csv(db_session)
    assert csv_str.startswith("# Gossipy Watchman")


def test_delimiter_is_semicolon(db_session):
    from app.services.export_service import generate_timeline_csv

    csv_str = generate_timeline_csv(db_session)
    header_line = csv_str.strip().splitlines()[3]
    assert ";" in header_line
    assert "pessoa_id" in header_line


def test_header_contains_all_20_columns(db_session):
    from app.services.export_service import generate_timeline_csv

    csv_str = generate_timeline_csv(db_session)
    header_line = csv_str.strip().splitlines()[3]
    reader = csv.reader([header_line], delimiter=";")
    cols = set(next(reader))
    expected = {
        "pessoa_id", "pessoa_nome", "pessoa_categoria",
        "aparicao_num",
        "inicio_s", "inicio_formatado",
        "fim_s", "fim_formatado",
        "presente_por_s", "presente_por_formatado",
        "primeira_vez_s", "primeira_vez_formatado",
        "ultima_vez_s", "ultima_vez_formatado",
        "total_aparicoes_no_video", "total_presente_no_video_s",
        "confianca",
        "video_id", "video_arquivo", "video_data_upload",
    }
    assert expected == cols


# ── Filtros ──────────────────────────────────────────────────────────────────

def test_filter_by_person_id(db_session):
    from app.services.export_service import generate_timeline_csv

    v = _make_video(db_session)
    p1 = _make_person(db_session, "João")
    p2 = _make_person(db_session, "Maria")
    _make_appearance(db_session, p1.id, v.id)
    _make_appearance(db_session, p2.id, v.id)

    csv_str = generate_timeline_csv(db_session, person_id=p1.id)
    rows = _parse_csv(csv_str)
    assert len(rows) == 1
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
    rows = _parse_csv(csv_str)
    assert len(rows) == 1
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
    rows = _parse_csv(csv_str)
    assert len(rows) == 2


# ── Campos de tempo ──────────────────────────────────────────────────────────

def test_inicio_e_fim_em_segundos(db_session):
    from app.services.export_service import generate_timeline_csv

    v = _make_video(db_session)
    p = _make_person(db_session)
    _make_appearance(db_session, p.id, v.id, start=2.0, end=7.5)

    rows = _parse_csv(generate_timeline_csv(db_session))
    row = rows[0]
    assert float(row["inicio_s"]) == pytest.approx(2.0)
    assert float(row["fim_s"]) == pytest.approx(7.5)


def test_presente_por_calculado(db_session):
    from app.services.export_service import generate_timeline_csv

    v = _make_video(db_session)
    p = _make_person(db_session)
    _make_appearance(db_session, p.id, v.id, start=2.0, end=7.5)

    rows = _parse_csv(generate_timeline_csv(db_session))
    assert float(rows[0]["presente_por_s"]) == pytest.approx(5.5)


def test_presente_por_vazio_quando_fim_none(db_session):
    from app.services.export_service import generate_timeline_csv

    v = _make_video(db_session)
    p = _make_person(db_session)
    a = Appearance(person_id=p.id, video_id=v.id, timestamp_start=1.0, timestamp_end=None, confidence=0.4)
    db_session.add(a)
    db_session.commit()

    rows = _parse_csv(generate_timeline_csv(db_session))
    assert rows[0]["fim_s"] == ""
    assert rows[0]["presente_por_s"] == ""


def test_inicio_formatado_mm_ss(db_session):
    from app.services.export_service import generate_timeline_csv

    v = _make_video(db_session)
    p = _make_person(db_session)
    _make_appearance(db_session, p.id, v.id, start=125.0, end=130.0)

    rows = _parse_csv(generate_timeline_csv(db_session))
    assert rows[0]["inicio_formatado"] == "02:05"
    assert rows[0]["fim_formatado"] == "02:10"
    assert rows[0]["presente_por_formatado"] == "00:05"


# ── Agregados por pessoa ─────────────────────────────────────────────────────

def test_primeira_vez_e_ultima_vez(db_session):
    from app.services.export_service import generate_timeline_csv

    v = _make_video(db_session)
    p = _make_person(db_session)
    _make_appearance(db_session, p.id, v.id, start=5.0, end=10.0)
    _make_appearance(db_session, p.id, v.id, start=20.0, end=30.0)

    rows = _parse_csv(generate_timeline_csv(db_session))
    # primeira_vez = menor timestamp_start = 5.0
    # ultima_vez = maior timestamp_end = 30.0
    for row in rows:
        assert float(row["primeira_vez_s"]) == pytest.approx(5.0)
        assert float(row["ultima_vez_s"]) == pytest.approx(30.0)


def test_total_aparicoes_no_video(db_session):
    from app.services.export_service import generate_timeline_csv

    v = _make_video(db_session)
    p = _make_person(db_session)
    _make_appearance(db_session, p.id, v.id, start=0.0, end=5.0)
    _make_appearance(db_session, p.id, v.id, start=10.0, end=15.0)
    _make_appearance(db_session, p.id, v.id, start=20.0, end=25.0)

    rows = _parse_csv(generate_timeline_csv(db_session))
    assert len(rows) == 3
    for row in rows:
        assert int(row["total_aparicoes_no_video"]) == 3


def test_total_presente_no_video(db_session):
    from app.services.export_service import generate_timeline_csv

    v = _make_video(db_session)
    p = _make_person(db_session)
    _make_appearance(db_session, p.id, v.id, start=0.0, end=5.0)   # 5s
    _make_appearance(db_session, p.id, v.id, start=10.0, end=13.0)  # 3s

    rows = _parse_csv(generate_timeline_csv(db_session))
    for row in rows:
        assert float(row["total_presente_no_video_s"]) == pytest.approx(8.0)


def test_aparicao_num_incrementa_por_pessoa_e_video(db_session):
    from app.services.export_service import generate_timeline_csv

    v = _make_video(db_session)
    p = _make_person(db_session)
    _make_appearance(db_session, p.id, v.id, start=0.0, end=5.0)
    _make_appearance(db_session, p.id, v.id, start=10.0, end=15.0)

    rows = _parse_csv(generate_timeline_csv(db_session))
    nums = [int(r["aparicao_num"]) for r in rows]
    assert nums == [1, 2]


# ── Metadados do vídeo ───────────────────────────────────────────────────────

def test_video_data_upload_formatada(db_session):
    from app.services.export_service import generate_timeline_csv

    v = _make_video(db_session)
    p = _make_person(db_session)
    _make_appearance(db_session, p.id, v.id)

    rows = _parse_csv(generate_timeline_csv(db_session))
    # uploaded_at = 2026-06-01 UTC → "01/06/2026 00:00:00"
    assert rows[0]["video_data_upload"] == "01/06/2026 00:00:00"


def test_video_arquivo_e_id_presentes(db_session):
    from app.services.export_service import generate_timeline_csv

    v = _make_video(db_session, "camera01.mp4")
    p = _make_person(db_session)
    _make_appearance(db_session, p.id, v.id)

    rows = _parse_csv(generate_timeline_csv(db_session))
    assert rows[0]["video_arquivo"] == "camera01.mp4"
    assert int(rows[0]["video_id"]) == v.id


# ── _fmt_ss unitário ─────────────────────────────────────────────────────────

def test_fmt_ss_zero():
    from app.services.export_service import _fmt_ss
    assert _fmt_ss(0) == "00:00"


def test_fmt_ss_one_minute():
    from app.services.export_service import _fmt_ss
    assert _fmt_ss(60) == "01:00"


def test_fmt_ss_none():
    from app.services.export_service import _fmt_ss
    assert _fmt_ss(None) == ""


def test_fmt_ss_125():
    from app.services.export_service import _fmt_ss
    assert _fmt_ss(125) == "02:05"
