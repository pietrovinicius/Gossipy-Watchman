from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.models.base import Base


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    registration = Column(String(100), nullable=False, unique=True, index=True)
    department = Column(String(100))
    role = Column(String(100))
    photo_path = Column(String(500))
    embedding_path = Column(String(500))
    person_id = Column(Integer, ForeignKey("people.id"))
    active = Column(Integer, nullable=False, default=1)
    notes = Column(Text)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    person = relationship("Person", back_populates="employee")

    def __repr__(self) -> str:
        return f"<Employee(id={self.id}, name='{self.name}', registration='{self.registration}')>"
