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
    assert settings.FRAMES_PER_SECOND_SAMPLE == 2
    assert isinstance(settings.FRAMES_PER_SECOND_SAMPLE, int)


def test_app_name_default():
    from app.core.settings import settings
    assert settings.APP_NAME == "Gossipy Watchman"


def test_api_v1_prefix_default():
    from app.core.settings import settings
    assert settings.API_V1_PREFIX == "/api/v1"


# ── Novos testes Sprint 5 ────────────────────────────────────────────────────

def test_jwt_secret_key_exists():
    from app.core.settings import settings
    assert isinstance(settings.JWT_SECRET_KEY, str)
    assert len(settings.JWT_SECRET_KEY) > 0


def test_jwt_algorithm_default():
    from app.core.settings import settings
    assert settings.JWT_ALGORITHM == "HS256"


def test_jwt_expire_minutes_default():
    from app.core.settings import settings
    assert settings.JWT_EXPIRE_MINUTES == 60
    assert isinstance(settings.JWT_EXPIRE_MINUTES, int)


def test_admin_username_default():
    from app.core.settings import settings
    assert settings.ADMIN_USERNAME == "admin"


def test_max_upload_size_mb_default():
    from app.core.settings import settings
    assert settings.MAX_UPLOAD_SIZE_MB == 5120


def test_max_upload_size_bytes_calculated():
    from app.core.settings import settings
    assert settings.MAX_UPLOAD_SIZE_BYTES == settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024


def test_docs_enabled_default():
    from app.core.settings import settings
    assert isinstance(settings.DOCS_ENABLED, bool)
    assert settings.DOCS_ENABLED is True


# ── Novos testes Sprint — detecção facial CNN ───────────────────────────────

def test_face_detection_model_default():
    from app.core.settings import settings
    assert settings.FACE_DETECTION_MODEL == "cnn"


def test_face_upsample_default():
    from app.core.settings import settings
    assert settings.FACE_UPSAMPLE == 1
    assert isinstance(settings.FACE_UPSAMPLE, int)


def test_face_detection_model_accepts_hog():
    from app.core.settings import Settings
    s = Settings(FACE_DETECTION_MODEL="hog")
    assert s.FACE_DETECTION_MODEL == "hog"
