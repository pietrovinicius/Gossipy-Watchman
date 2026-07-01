from pathlib import Path


def test_database_url_default():
    from app.core.settings import settings
    assert settings.DATABASE_URL == "sqlite:///./gossipy.db"


def test_storage_videos_is_path():
    from app.core.settings import settings
    assert isinstance(settings.STORAGE_VIDEOS, Path)
    assert settings.STORAGE_VIDEOS.as_posix() == "storage/videos"


def test_storage_faces_is_path():
    from app.core.settings import settings
    assert isinstance(settings.STORAGE_FACES, Path)
    assert settings.STORAGE_FACES.as_posix() == "storage/faces"


def test_face_recognition_tolerance_default():
    from app.core.settings import Settings
    s = Settings(_env_file=None)
    assert s.FACE_RECOGNITION_TOLERANCE == 0.4
    assert isinstance(s.FACE_RECOGNITION_TOLERANCE, float)


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


# ── Testes InsightFace ────────────────────────────────────────────────────────

def test_insightface_model_default():
    from app.core.settings import settings
    assert settings.INSIGHTFACE_MODEL == "buffalo_l"


def test_insightface_det_size_default():
    from app.core.settings import settings
    assert settings.INSIGHTFACE_DET_SIZE == 640


def test_insightface_det_score_default():
    from app.core.settings import settings
    assert settings.INSIGHTFACE_DET_SCORE == 0.7


def test_face_max_embeddings_per_person_default():
    from app.core.settings import settings
    assert settings.FACE_MAX_EMBEDDINGS_PER_PERSON == 5


def test_insightface_providers_default_cpu_only():
    """Providers padrão devem ser CPU-only para compatibilidade Windows."""
    from app.core.settings import Settings
    s = Settings(_env_file=None)
    assert s.INSIGHTFACE_PROVIDERS == ["CPUExecutionProvider"]


def test_insightface_det_size_code_default_is_640():
    """Default no código deve ser 640 (seguro para 16GB RAM)."""
    from app.core.settings import Settings
    s = Settings(_env_file=None)
    assert s.INSIGHTFACE_DET_SIZE == 640


def test_face_recognition_tolerance_cosine():
    from app.core.settings import settings
    assert settings.FACE_RECOGNITION_TOLERANCE == 0.4
