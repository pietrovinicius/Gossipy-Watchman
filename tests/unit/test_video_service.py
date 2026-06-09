import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.models import Base
from app.models.video import VideoStatus


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


def test_create_video_record_status_pendente(db):
    from app.services.video_service import create_video_record
    video = create_video_record(db, "clip.mp4", "storage/videos/clip.mp4")
    assert video.id is not None
    assert video.status == VideoStatus.PENDENTE
    assert video.file_name == "clip.mp4"


def test_get_video_by_id_returns_none_for_missing(db):
    from app.services.video_service import get_video_by_id
    result = get_video_by_id(db, 9999)
    assert result is None


def test_get_video_by_id_returns_video(db):
    from app.services.video_service import create_video_record, get_video_by_id
    created = create_video_record(db, "a.mp4", "storage/videos/a.mp4")
    found = get_video_by_id(db, created.id)
    assert found is not None
    assert found.id == created.id


def test_list_videos_empty(db):
    from app.services.video_service import list_videos
    result = list_videos(db)
    assert result == []


def test_list_videos_respects_limit(db):
    from app.services.video_service import create_video_record, list_videos
    for i in range(5):
        create_video_record(db, f"v{i}.mp4", f"storage/videos/v{i}.mp4")
    result = list_videos(db, skip=0, limit=3)
    assert len(result) == 3


def test_list_videos_respects_skip(db):
    from app.services.video_service import create_video_record, list_videos
    for i in range(4):
        create_video_record(db, f"v{i}.mp4", f"storage/videos/v{i}.mp4")
    result = list_videos(db, skip=2, limit=10)
    assert len(result) == 2


def test_update_video_status_changes_correctly(db):
    from app.services.video_service import create_video_record, update_video_status
    video = create_video_record(db, "b.mp4", "storage/videos/b.mp4")
    updated = update_video_status(db, video.id, VideoStatus.CONCLUIDO)
    assert updated is not None
    assert updated.status == VideoStatus.CONCLUIDO


def test_update_video_status_returns_none_for_missing(db):
    from app.services.video_service import update_video_status
    result = update_video_status(db, 9999, VideoStatus.ERRO)
    assert result is None


# ── get_video_detail ─────────────────────────────────────────────────────────

def _make_person(db, name="Fulano", category="Visitante", profile_image_path="fulano.jpg"):
    from app.models.person import Person
    person = Person(name=name, category=category, profile_image_path=profile_image_path)
    db.add(person)
    db.commit()
    db.refresh(person)
    return person


def _make_appearance(db, person_id, video_id, start, end, confidence=0.3):
    from app.models.appearance import Appearance
    appearance = Appearance(
        person_id=person_id,
        video_id=video_id,
        timestamp_start=start,
        timestamp_end=end,
        confidence=confidence,
    )
    db.add(appearance)
    db.commit()
    db.refresh(appearance)
    return appearance


def test_get_video_detail_returns_none_for_missing_video(db):
    from app.services.video_service import get_video_detail
    assert get_video_detail(db, 9999) is None


def test_get_video_detail_returns_dict_with_expected_keys(db):
    from app.services.video_service import create_video_record, get_video_detail
    video = create_video_record(db, "v.mp4", "storage/videos/v.mp4")
    detail = get_video_detail(db, video.id)
    assert detail is not None
    assert set(detail.keys()) == {"video", "people", "summary"}
    assert detail["video"]["id"] == video.id


def test_get_video_detail_video_without_appearances(db):
    from app.services.video_service import create_video_record, get_video_detail
    video = create_video_record(db, "v.mp4", "storage/videos/v.mp4")
    detail = get_video_detail(db, video.id)
    assert detail["people"] == []
    assert detail["summary"]["total_people"] == 0
    assert detail["summary"]["total_appearances"] == 0
    assert detail["summary"]["duration_covered"] == 0
    assert detail["summary"]["processing_status"] == video.status.value


def test_get_video_detail_orders_people_by_first_seen_at_asc(db):
    from app.services.video_service import create_video_record, get_video_detail
    video = create_video_record(db, "v.mp4", "storage/videos/v.mp4")
    person_a = _make_person(db, name="A")
    person_b = _make_person(db, name="B")
    _make_appearance(db, person_b.id, video.id, start=5.0, end=6.0)
    _make_appearance(db, person_a.id, video.id, start=1.0, end=2.0)

    detail = get_video_detail(db, video.id)
    names = [p["person_name"] for p in detail["people"]]
    assert names == ["A", "B"]


def test_get_video_detail_total_seconds_ignores_open_ended_appearances(db):
    from app.services.video_service import create_video_record, get_video_detail
    video = create_video_record(db, "v.mp4", "storage/videos/v.mp4")
    person = _make_person(db)
    _make_appearance(db, person.id, video.id, start=1.0, end=3.0)
    _make_appearance(db, person.id, video.id, start=10.0, end=None)

    detail = get_video_detail(db, video.id)
    p = detail["people"][0]
    assert p["total_seconds"] == 2.0
    assert p["appearance_count"] == 2
    assert p["first_seen_at"] == 1.0
    assert p["last_seen_at"] == 10.0


def test_get_video_detail_appearance_count_scoped_to_video(db):
    from app.services.video_service import create_video_record, get_video_detail
    video1 = create_video_record(db, "v1.mp4", "storage/videos/v1.mp4")
    video2 = create_video_record(db, "v2.mp4", "storage/videos/v2.mp4")
    person = _make_person(db)
    _make_appearance(db, person.id, video1.id, start=1.0, end=2.0)
    _make_appearance(db, person.id, video2.id, start=1.0, end=2.0)
    _make_appearance(db, person.id, video2.id, start=3.0, end=4.0)

    detail = get_video_detail(db, video1.id)
    assert len(detail["people"]) == 1
    assert detail["people"][0]["appearance_count"] == 1


def test_get_video_detail_summary_counts_distinct_people(db):
    from app.services.video_service import create_video_record, get_video_detail
    video = create_video_record(db, "v.mp4", "storage/videos/v.mp4")
    person_a = _make_person(db, name="A")
    person_b = _make_person(db, name="B")
    _make_appearance(db, person_a.id, video.id, start=1.0, end=2.0)
    _make_appearance(db, person_a.id, video.id, start=3.0, end=4.0)
    _make_appearance(db, person_b.id, video.id, start=5.0, end=6.0)

    detail = get_video_detail(db, video.id)
    assert detail["summary"]["total_people"] == 2
    assert detail["summary"]["total_appearances"] == 3
    assert detail["summary"]["duration_covered"] == 3.0


# ── soft delete / restore / reprocess ─────────────────────────────────────────

def test_soft_delete_video_sets_deleted_at(db):
    from app.services.video_service import create_video_record, soft_delete_video

    video = create_video_record(db, "clip.mp4", "storage/videos/clip.mp4")
    result = soft_delete_video(db, video.id)

    assert result is not None
    assert result.deleted_at is not None


def test_soft_delete_video_returns_none_for_unknown_id(db):
    from app.services.video_service import soft_delete_video

    assert soft_delete_video(db, 9999) is None


def test_soft_delete_video_is_idempotent(db):
    from app.services.video_service import create_video_record, soft_delete_video

    video = create_video_record(db, "clip.mp4", "storage/videos/clip.mp4")
    first = soft_delete_video(db, video.id)
    second = soft_delete_video(db, video.id)

    assert first.deleted_at == second.deleted_at


def test_restore_video_clears_deleted_at(db):
    from app.services.video_service import create_video_record, soft_delete_video, restore_video

    video = create_video_record(db, "clip.mp4", "storage/videos/clip.mp4")
    soft_delete_video(db, video.id)
    restored = restore_video(db, video.id)

    assert restored is not None
    assert restored.deleted_at is None


def test_list_videos_excludes_deleted_by_default(db):
    from app.services.video_service import create_video_record, soft_delete_video, list_videos

    v1 = create_video_record(db, "ativo.mp4", "storage/videos/ativo.mp4")
    v2 = create_video_record(db, "removido.mp4", "storage/videos/removido.mp4")
    soft_delete_video(db, v2.id)

    ids = [v.id for v in list_videos(db)]
    assert v1.id in ids
    assert v2.id not in ids


def test_list_videos_include_deleted_returns_all(db):
    from app.services.video_service import create_video_record, soft_delete_video, list_videos

    v1 = create_video_record(db, "ativo.mp4", "storage/videos/ativo.mp4")
    v2 = create_video_record(db, "removido.mp4", "storage/videos/removido.mp4")
    soft_delete_video(db, v2.id)

    ids = [v.id for v in list_videos(db, include_deleted=True)]
    assert v1.id in ids
    assert v2.id in ids


def test_list_videos_filters_by_status(db):
    from app.services.video_service import create_video_record, update_video_status, list_videos

    v1 = create_video_record(db, "a.mp4", "storage/videos/a.mp4")
    v2 = create_video_record(db, "b.mp4", "storage/videos/b.mp4")
    update_video_status(db, v2.id, VideoStatus.CONCLUIDO)

    result = list_videos(db, status_filter=VideoStatus.CONCLUIDO.value)

    ids = [v.id for v in result]
    assert v2.id in ids
    assert v1.id not in ids


def test_reprocess_video_resets_status_to_pendente(db, tmp_path):
    from app.services.video_service import create_video_record, update_video_status, reprocess_video

    file_path = tmp_path / "clip.mp4"
    file_path.write_bytes(b"x")
    video = create_video_record(db, "clip.mp4", str(file_path))
    update_video_status(db, video.id, VideoStatus.ERRO)

    result = reprocess_video(db, video.id)

    assert result is not None
    assert result.status == VideoStatus.PENDENTE


def test_reprocess_video_raises_409_when_file_missing(db):
    from fastapi import HTTPException
    from app.services.video_service import create_video_record, reprocess_video

    video = create_video_record(db, "clip.mp4", "storage/videos/inexistente_xyz.mp4")

    with pytest.raises(HTTPException) as exc:
        reprocess_video(db, video.id)
    assert exc.value.status_code == 409


def test_reprocess_video_returns_none_for_unknown_id(db):
    from app.services.video_service import reprocess_video

    assert reprocess_video(db, 9999) is None


# ── update_file_name ─────────────────────────────────────────────────────────

def test_update_file_name_persists_new_name(db):
    from app.services.video_service import create_video_record, update_file_name
    video = create_video_record(db, "original.dav", "storage/videos/abc.dav")
    updated = update_file_name(db, video.id, "original_converted.mp4")
    assert updated is not None
    assert updated.file_name == "original_converted.mp4"


def test_update_file_name_returns_none_for_unknown_id(db):
    from app.services.video_service import update_file_name
    assert update_file_name(db, 9999, "x.mp4") is None


# ── search_videos ────────────────────────────────────────────────────────────

def test_search_videos_without_filters_returns_all(db):
    from app.services.video_service import create_video_record, search_videos

    v1 = create_video_record(db, "clip1.mp4", "storage/videos/clip1.mp4")
    v2 = create_video_record(db, "clip2.mp4", "storage/videos/clip2.mp4")

    result = search_videos(db)

    assert result["total"] == 2
    assert len(result["items"]) == 2


def test_search_videos_includes_thumbnail_path(db):
    from app.services.video_service import create_video_record, search_videos

    v1 = create_video_record(db, "clip1.mp4", "storage/videos/clip1.mp4")
    v1.thumbnail_path = "storage/videos/1_thumbnail.jpg"
    db.commit()

    result = search_videos(db)

    assert result["items"][0]["thumbnail_path"] == "storage/videos/1_thumbnail.jpg"


def test_search_videos_with_query_filters_by_name(db):
    from app.services.video_service import create_video_record, search_videos

    v1 = create_video_record(db, "aniversario_2024.mp4", "storage/videos/aniversario_2024.mp4")
    v2 = create_video_record(db, "reuniao.mp4", "storage/videos/reuniao.mp4")

    result = search_videos(db, query="aniversario")

    assert result["total"] == 1
    assert result["items"][0]["id"] == v1.id


def test_search_videos_with_status_filter(db):
    from app.services.video_service import create_video_record, update_video_status, search_videos

    v1 = create_video_record(db, "a.mp4", "storage/videos/a.mp4")
    v2 = create_video_record(db, "b.mp4", "storage/videos/b.mp4")
    update_video_status(db, v2.id, VideoStatus.CONCLUIDO)

    result = search_videos(db, status_filter=VideoStatus.CONCLUIDO.value)

    assert result["total"] == 1
    assert result["items"][0]["id"] == v2.id


def test_search_videos_sort_by_people_desc(db):
    from app.services.video_service import create_video_record, search_videos

    v1 = create_video_record(db, "v1.mp4", "storage/videos/v1.mp4")
    v2 = create_video_record(db, "v2.mp4", "storage/videos/v2.mp4")

    person_a = _make_person(db, name="A")
    person_b = _make_person(db, name="B")
    person_c = _make_person(db, name="C")

    # v1: 3 pessoas
    _make_appearance(db, person_a.id, v1.id, start=1.0, end=2.0)
    _make_appearance(db, person_b.id, v1.id, start=3.0, end=4.0)
    _make_appearance(db, person_c.id, v1.id, start=5.0, end=6.0)

    # v2: 1 pessoa
    _make_appearance(db, person_a.id, v2.id, start=1.0, end=2.0)

    result = search_videos(db, sort_by="people_desc")

    assert result["items"][0]["id"] == v1.id
    assert result["items"][1]["id"] == v2.id


def test_search_videos_pagination_page_2(db):
    from app.services.video_service import create_video_record, search_videos

    for i in range(15):
        create_video_record(db, f"v{i}.mp4", f"storage/videos/v{i}.mp4")

    result = search_videos(db, page=2, page_size=5)

    assert result["page"] == 2
    assert len(result["items"]) == 5
    assert result["has_prev"] is True
    assert result["has_next"] is True


def test_search_videos_total_pages_calculated_correctly(db):
    from app.services.video_service import create_video_record, search_videos

    for i in range(27):
        create_video_record(db, f"v{i}.mp4", f"storage/videos/v{i}.mp4")

    result = search_videos(db, page_size=12)

    assert result["total"] == 27
    assert result["total_pages"] == 3


def test_search_videos_has_next_true_when_more_pages(db):
    from app.services.video_service import create_video_record, search_videos

    for i in range(15):
        create_video_record(db, f"v{i}.mp4", f"storage/videos/v{i}.mp4")

    result = search_videos(db, page=1, page_size=5)

    assert result["has_next"] is True
    assert result["has_prev"] is False


def test_search_videos_people_previews_limited_to_4(db):
    from app.services.video_service import create_video_record, search_videos

    video = create_video_record(db, "v.mp4", "storage/videos/v.mp4")

    for i in range(6):
        person = _make_person(db, name=f"Person{i}")
        _make_appearance(db, person.id, video.id, start=float(i), end=float(i+1))

    result = search_videos(db)

    assert result["items"][0]["people_count"] == 6
    assert len(result["items"][0]["people_previews"]) == 4


def test_search_videos_excludes_deleted_by_default(db):
    from app.services.video_service import create_video_record, soft_delete_video, search_videos

    v1 = create_video_record(db, "ativo.mp4", "storage/videos/ativo.mp4")
    v2 = create_video_record(db, "deletado.mp4", "storage/videos/deletado.mp4")
    soft_delete_video(db, v2.id)

    result = search_videos(db)

    assert result["total"] == 1
    assert result["items"][0]["id"] == v1.id


# ── soft_delete_video: limpeza de arquivos físicos ────────────────────────────

def test_soft_delete_video_remove_arquivo_fisico(db, tmp_path):
    """soft_delete_video deve apagar o arquivo de vídeo do disco."""
    from app.services.video_service import create_video_record, soft_delete_video

    video_file = tmp_path / "clip.mp4"
    video_file.write_bytes(b"video-content")

    video = create_video_record(db, "clip.mp4", str(video_file))
    soft_delete_video(db, video.id)

    assert not video_file.exists(), "arquivo de vídeo deve ser removido do disco ao deletar"
    assert video.deleted_at is not None, "DB record deve estar soft-deleted"


def test_soft_delete_video_remove_thumbnail_se_existir(db, tmp_path):
    """soft_delete_video deve apagar o thumbnail do disco se existir."""
    from app.services.video_service import create_video_record, soft_delete_video
    from app.models.video import Video

    video_file = tmp_path / "clip.mp4"
    video_file.write_bytes(b"video")
    thumb_file = tmp_path / "clip_thumb.jpg"
    thumb_file.write_bytes(b"thumb")

    video = create_video_record(db, "clip.mp4", str(video_file))
    # Setar thumbnail manualmente
    db.get(Video, video.id).thumbnail_path = str(thumb_file)
    db.commit()

    soft_delete_video(db, video.id)

    assert not thumb_file.exists(), "thumbnail deve ser removido junto com o vídeo"


def test_soft_delete_video_nao_falha_sem_arquivo_em_disco(db):
    """soft_delete_video não deve lançar exceção se arquivo físico não existir."""
    from app.services.video_service import create_video_record, soft_delete_video

    video = create_video_record(db, "fantasma.mp4", "/tmp/nao_existe_nunca.mp4")
    result = soft_delete_video(db, video.id)

    assert result is not None
    assert result.deleted_at is not None
