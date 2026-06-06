import enum
from datetime import datetime, timezone

from sqlalchemy import String, DateTime, Enum
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class VideoStatus(str, enum.Enum):
    PENDENTE = "Pendente"
    PROCESSANDO = "Processando"
    CONCLUIDO = "Concluído"
    ERRO = "Erro"


class Video(Base):
    __tablename__ = "videos"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(512), nullable=False)
    status: Mapped[VideoStatus] = mapped_column(
        Enum(VideoStatus, values_callable=lambda obj: [e.value for e in obj]),
        default=VideoStatus.PENDENTE,
        nullable=False,
    )
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
