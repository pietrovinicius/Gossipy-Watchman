import os
from pathlib import Path

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Banco
    DATABASE_URL: str = "sqlite:///./gossipy.db"

    # Storage
    STORAGE_VIDEOS: Path = Path("storage/videos")
    STORAGE_FACES: Path = Path("storage/faces")
    STORAGE_EMPLOYEES: Path = Path("storage/employees")

    # Visão computacional
    FACE_RECOGNITION_TOLERANCE: float = 0.4  # distância coseno ArcFace
    FRAMES_PER_SECOND_SAMPLE: int = 2

    # InsightFace
    INSIGHTFACE_MODEL: str = "buffalo_l"
    INSIGHTFACE_DET_SIZE: int = 1024
    INSIGHTFACE_DET_SCORE: float = 0.45
    FACE_MAX_EMBEDDINGS_PER_PERSON: int = 5
    FACE_MAX_SAMPLES_PER_PERSON: int = 10
    INSIGHTFACE_HIGH_RES_THRESHOLD: int = 1920  # escala frames acima deste valor

    # Qualidade de frame
    FACE_MIN_SIZE_PX: int = 40
    FACE_BLUR_THRESHOLD: float = 40.0

    # Agregação por aparição contínua (track)
    FACE_TRACK_GAP_TOLERANCE: float = 2.0
    FACE_TRACK_MIN_SAMPLES: int = 1
    FACE_TRACK_IOU_THRESHOLD: float = 0.3

    # k-NN voting
    FACE_KNN_K: int = 3

    # Filtro de pose facial — câmera CCTV de teto/parede gera pitch 35–50°
    FACE_MAX_YAW_DEG: float = 65.0
    FACE_MAX_PITCH_DEG: float = 55.0

    # Motion Gating
    MOTION_GATING_ENABLED: bool = True
    MOTION_GATING_THRESHOLD: int = 15
    MOTION_GATING_AREA_RATIO: float = 0.001
    MOTION_GATING_FORCE_INTERVAL: int = 5  # forçar detecção a cada N segundos

    # App
    APP_NAME: str = "Gossipy Watchman"
    APP_VERSION: str = "2.12.0"
    API_V1_PREFIX: str = "/api/v1"
    DOCS_ENABLED: bool = True

    # JWT — fallback para testes; produção deve setar no .env
    JWT_SECRET_KEY: str = Field(
        default=os.getenv(
            "JWT_SECRET_KEY",
            "test-secret-key-nao-usar-em-producao",
        )
    )
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60

    # Admin
    ADMIN_USERNAME: str = "admin"
    ADMIN_PASSWORD_HASH: str = ""

    # Upload
    MAX_UPLOAD_SIZE_MB: int = 5120
    MAX_UPLOAD_SIZE_BYTES: int = 0

    # ffmpeg
    FFMPEG_PATH: str = "ffmpeg"

    @model_validator(mode="after")
    def _compute_derived(self) -> "Settings":
        self.MAX_UPLOAD_SIZE_BYTES = self.MAX_UPLOAD_SIZE_MB * 1024 * 1024
        return self


settings = Settings()
