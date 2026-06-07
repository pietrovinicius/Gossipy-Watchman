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

    # Visão computacional
    FACE_RECOGNITION_TOLERANCE: float = 0.6
    FRAMES_PER_SECOND_SAMPLE: int = 1
    FACE_DETECTION_MODEL: str = "cnn"
    FACE_UPSAMPLE: int = 1

    # App
    APP_NAME: str = "Gossipy Watchman"
    APP_VERSION: str = "1.7.0"
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
    MAX_UPLOAD_SIZE_MB: int = 500
    MAX_UPLOAD_SIZE_BYTES: int = 0

    @model_validator(mode="after")
    def _compute_derived(self) -> "Settings":
        self.MAX_UPLOAD_SIZE_BYTES = self.MAX_UPLOAD_SIZE_MB * 1024 * 1024
        return self


settings = Settings()
