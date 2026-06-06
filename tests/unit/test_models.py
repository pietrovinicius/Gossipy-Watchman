import enum

import sqlalchemy as sa
from sqlalchemy import inspect


def get_columns(model_class) -> dict:
    mapper = inspect(model_class)
    return {col.key: col for col in mapper.column_attrs}


def get_relationships(model_class) -> set:
    mapper = inspect(model_class)
    return {rel.key for rel in mapper.relationships}


# ── Person ──────────────────────────────────────────────────────────────────

def test_person_table_name():
    from app.models.person import Person
    assert Person.__tablename__ == "people"


def test_person_has_required_columns():
    from app.models.person import Person
    cols = get_columns(Person)
    assert "id" in cols
    assert "name" in cols
    assert "profile_image_path" in cols
    assert "created_at" in cols


def test_person_id_is_primary_key():
    from app.models.person import Person
    col = sa.inspect(Person).mapper.column_attrs["id"].columns[0]
    assert col.primary_key is True


def test_person_created_at_has_default():
    from app.models.person import Person
    col = sa.inspect(Person).mapper.column_attrs["created_at"].columns[0]
    assert col.default is not None or col.server_default is not None


# ── Video ────────────────────────────────────────────────────────────────────

def test_video_table_name():
    from app.models.video import Video
    assert Video.__tablename__ == "videos"


def test_video_has_required_columns():
    from app.models.video import Video
    cols = get_columns(Video)
    assert "id" in cols
    assert "file_name" in cols
    assert "file_path" in cols
    assert "status" in cols
    assert "uploaded_at" in cols


def test_video_status_enum_values():
    from app.models.video import VideoStatus
    values = {e.value for e in VideoStatus}
    assert values == {"Pendente", "Processando", "Concluído", "Erro"}


def test_video_status_is_enum_type():
    from app.models.video import VideoStatus
    assert issubclass(VideoStatus, enum.Enum)


# ── Appearance ───────────────────────────────────────────────────────────────

def test_appearance_table_name():
    from app.models.appearance import Appearance
    assert Appearance.__tablename__ == "appearances"


def test_appearance_has_required_columns():
    from app.models.appearance import Appearance
    cols = get_columns(Appearance)
    assert "id" in cols
    assert "person_id" in cols
    assert "video_id" in cols
    assert "timestamp_start" in cols
    assert "timestamp_end" in cols
    assert "confidence" in cols


def test_appearance_has_foreign_keys():
    from app.models.appearance import Appearance
    fk_targets = {
        fk.target_fullname
        for col in sa.inspect(Appearance).mapper.local_table.columns
        for fk in col.foreign_keys
    }
    assert "people.id" in fk_targets
    assert "videos.id" in fk_targets


# ── __init__ exports ─────────────────────────────────────────────────────────

def test_models_init_exports_all():
    from app.models import Person, Video, Appearance
    assert Person is not None
    assert Video is not None
    assert Appearance is not None
