from fastapi import APIRouter, Depends, UploadFile, File, Query, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import Employee
from app.schemas.employee import EmployeeCreate, EmployeeUpdate, EmployeeResponse
from app.services.employee_service import (
    register_employee,
    list_employees,
    get_employee_by_id,
    update_employee,
    deactivate_employee,
)
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/employees", tags=["employees"])

ALLOWED_PHOTO_EXTENSIONS = {".jpg", ".jpeg", ".png"}
MAX_PHOTO_SIZE_MB = 10


def validate_photo_file(filename: str, size: int) -> None:
    """Validate uploaded photo file."""
    ext = filename[filename.rfind(".") :].lower()
    if ext not in ALLOWED_PHOTO_EXTENSIONS:
        raise HTTPException(
            status_code=422, detail=f"Formato não suportado: {ext}"
        )
    if size > MAX_PHOTO_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail=f"Arquivo maior que {MAX_PHOTO_SIZE_MB}MB",
        )


@router.post("", response_model=EmployeeResponse, status_code=201)
async def create_employee(
    name: str,
    registration: str,
    department: str | None = None,
    role: str | None = None,
    notes: str | None = None,
    photo: UploadFile = File(...),
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
) -> EmployeeResponse:
    """Register new employee with photo."""
    validate_photo_file(photo.filename or "", photo.size or 0)

    photo_bytes = await photo.read()

    employee = register_employee(
        db=db,
        name=name,
        registration=registration,
        department=department,
        role=role,
        notes=notes,
        photo_bytes=photo_bytes,
        photo_filename=photo.filename or "photo.jpg",
    )

    return EmployeeResponse.model_validate(employee)


@router.get("", response_model=list[EmployeeResponse])
def list_all_employees(
    active_only: bool = Query(True),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
) -> list[EmployeeResponse]:
    """List employees."""
    employees = list_employees(db, active_only=active_only, skip=skip, limit=limit)
    return [EmployeeResponse.model_validate(e) for e in employees]


@router.get("/{employee_id}", response_model=EmployeeResponse)
def get_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
) -> EmployeeResponse:
    """Get employee by ID."""
    employee = get_employee_by_id(db, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Funcionário não encontrado")
    return EmployeeResponse.model_validate(employee)


@router.patch("/{employee_id}", response_model=EmployeeResponse)
def update_emp(
    employee_id: int,
    data: EmployeeUpdate,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
) -> EmployeeResponse:
    """Update employee."""
    employee = update_employee(db, employee_id, data)
    if not employee:
        raise HTTPException(status_code=404, detail="Funcionário não encontrado")
    return EmployeeResponse.model_validate(employee)


@router.delete("/{employee_id}", response_model=EmployeeResponse)
def delete_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_user),
) -> EmployeeResponse:
    """Deactivate employee (soft delete)."""
    employee = deactivate_employee(db, employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Funcionário não encontrado")
    return EmployeeResponse.model_validate(employee)
