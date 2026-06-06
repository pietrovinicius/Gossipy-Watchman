from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./gossipy.db"
    STORAGE_VIDEOS: Path = Path("storage/videos")
    STORAGE_FACES: Path = Path("storage/faces")
    FACE_RECOGNITION_TOLERANCE: float = 0.6
    FRAMES_PER_SECOND_SAMPLE: int = 1
    APP_NAME: str = "Gossipy Watchman"
    APP_VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
