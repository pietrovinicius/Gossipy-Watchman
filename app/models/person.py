from datetime import datetime, timezone
from enum import Enum as PyEnum

from sqlalchemy import String, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class PersonCategory(PyEnum):
    funcionario = "Funcionário"
    visitante = "Visitante"
    desconhecido = "Desconhecido"
    monitorado = "Monitorado"


class Person(Base):
    __tablename__ = "people"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    profile_image_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(
        String(20),
        default=PersonCategory.desconhecido.value,
        nullable=False,
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True, default=None
    )

    employee: Mapped["Employee | None"] = relationship("Employee", back_populates="person", uselist=False)
