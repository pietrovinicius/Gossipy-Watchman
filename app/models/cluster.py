from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class ClusterGroup(Base):
    __tablename__ = "cluster_groups"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    status: Mapped[str] = mapped_column(String(20), default="Pendente", nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True, default=None
    )

    suggestions: Mapped[list["ClusterSuggestion"]] = relationship(
        "ClusterSuggestion",
        back_populates="group",
        cascade="all, delete-orphan",
    )


class ClusterSuggestion(Base):
    __tablename__ = "cluster_suggestions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    group_id: Mapped[int] = mapped_column(
        ForeignKey("cluster_groups.id"), nullable=False
    )
    person_id: Mapped[int] = mapped_column(
        ForeignKey("people.id"), nullable=False
    )
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True, default=None
    )

    group: Mapped[ClusterGroup] = relationship(
        "ClusterGroup", back_populates="suggestions"
    )
    person: Mapped["Person"] = relationship("Person")
