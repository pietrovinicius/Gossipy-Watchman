from pathlib import Path


def test_database_url_default():
    from app.core.settings import settings
    assert settings.DATABASE_URL == "sqlite:///./gossipy.db"


def test_storage_videos_is_path():
    from app.core.settings import settings
    assert isinstance(settings.STORAGE_VIDEOS, Path)
    assert str(settings.STORAGE_VIDEOS) == "storage/videos"


def test_storage_faces_is_path():
    from app.core.settings import settings
    assert isinstance(settings.STORAGE_FACES, Path)
    assert str(settings.STORAGE_FACES) == "storage/faces"


def test_face_recognition_tolerance_default():
    from app.core.settings import settings
    assert settings.FACE_RECOGNITION_TOLERANCE == 0.6
    assert isinstance(settings.FACE_RECOGNITION_TOLERANCE, float)


def test_frames_per_second_sample_default():
    from app.core.settings import settings
    assert settings.FRAMES_PER_SECOND_SAMPLE == 1
    assert isinstance(settings.FRAMES_PER_SECOND_SAMPLE, int)


def test_app_name_default():
    from app.core.settings import settings
    assert settings.APP_NAME == "Gossipy Watchman"


def test_api_v1_prefix_default():
    from app.core.settings import settings
    assert settings.API_V1_PREFIX == "/api/v1"
