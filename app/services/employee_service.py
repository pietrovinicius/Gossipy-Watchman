from uuid import uuid4
from pathlib import Path
import numpy as np
import cv2
import face_recognition
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.models import Employee, Person
from app.schemas.employee import EmployeeCreate, EmployeeUpdate
from app.core.settings import settings


def register_employee(
    db: Session,
    name: str,
    registration: str,
    department: str | None,
    role: str | None,
    notes: str | None,
    photo_bytes: bytes,
    photo_filename: str,
) -> Employee:
    """Register new employee with face detection and embedding extraction."""
    # 1. Check registration unique
    existing = db.query(Employee).filter_by(registration=registration).first()
    if existing:
        raise HTTPException(status_code=409, detail="Matrícula já cadastrada")

    # 2. Detect faces in photo
    nparr = np.frombuffer(photo_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    rgb_frame = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    face_locations = face_recognition.face_locations(rgb_frame, model="cnn")
    if len(face_locations) == 0:
        raise HTTPException(status_code=422, detail="Nenhum rosto detectado na foto")
    if len(face_locations) > 1:
        raise HTTPException(status_code=422, detail="Foto contém múltiplos rostos")

    # 3. Extract embedding
    embeddings = face_recognition.face_encodings(rgb_frame, face_locations)
    embedding = embeddings[0]  # First (only) face

    # 4. Save photo
    settings.STORAGE_EMPLOYEES.mkdir(parents=True, exist_ok=True)
    file_id = str(uuid4())
    photo_path = settings.STORAGE_EMPLOYEES / f"{file_id}.jpg"
    cv2.imwrite(str(photo_path), img)

    # 5. Save embedding
    embedding_path = settings.STORAGE_EMPLOYEES / f"{file_id}_embedding.npy"
    np.save(str(embedding_path), embedding)

    # 6. Create Person
    person = Person(
        name=name,
        category="Funcionário",
        profile_image_path=str(photo_path),
    )
    db.add(person)
    db.flush()

    # 7. Create Employee
    employee = Employee(
        name=name,
        registration=registration,
        department=department,
        role=role,
        notes=notes,
        photo_path=str(photo_path),
        embedding_path=str(embedding_path),
        person_id=person.id,
        active=1,
    )
    db.add(employee)
    db.commit()
    db.refresh(employee)

    return employee


def list_employees(
    db: Session,
    active_only: bool = True,
    skip: int = 0,
    limit: int = 50,
) -> list[Employee]:
    """List employees with optional filtering."""
    query = db.query(Employee)
    if active_only:
        query = query.filter(Employee.active == 1)
    return query.offset(skip).limit(limit).all()


def get_employee_by_id(db: Session, employee_id: int) -> Employee | None:
    """Get employee by ID."""
    return db.query(Employee).filter_by(id=employee_id).first()


def get_employee_by_registration(db: Session, registration: str) -> Employee | None:
    """Get employee by registration."""
    return db.query(Employee).filter_by(registration=registration).first()


def update_employee(
    db: Session,
    employee_id: int,
    data: EmployeeUpdate,
) -> Employee | None:
    """Update employee fields."""
    employee = db.query(Employee).filter_by(id=employee_id).first()
    if not employee:
        return None

    if data.name is not None:
        employee.name = data.name
    if data.department is not None:
        employee.department = data.department
    if data.role is not None:
        employee.role = data.role
    if data.notes is not None:
        employee.notes = data.notes
    if data.active is not None:
        employee.active = 1 if data.active else 0

    db.commit()
    db.refresh(employee)
    return employee


def deactivate_employee(db: Session, employee_id: int) -> Employee | None:
    """Soft delete employee."""
    employee = db.query(Employee).filter_by(id=employee_id).first()
    if not employee:
        return None

    employee.active = 0
    db.commit()
    db.refresh(employee)

    return employee
