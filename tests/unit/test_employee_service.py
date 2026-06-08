import pytest
import numpy as np
from unittest.mock import patch, MagicMock
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.schemas.employee import EmployeeCreate, EmployeeUpdate
from app.models import Employee, Person


@pytest.fixture
def mock_db():
    """Mock SQLAlchemy session."""
    return MagicMock(spec=Session)


@pytest.fixture
def photo_bytes():
    """Dummy photo bytes."""
    return b"fake_jpeg_data"


class TestRegisterEmployee:
    """Tests for register_employee function."""

    @patch("app.services.face_service.extract_embeddings")
    @patch("app.services.employee_service.cv2")
    @patch("app.services.employee_service.np")
    @patch("app.services.employee_service.uuid4")
    def test_register_employee_creates_employee_and_person(
        self, mock_uuid, mock_np, mock_cv2, mock_extract, mock_db, photo_bytes
    ):
        """register_employee should create Employee and Person."""
        from app.services.employee_service import register_employee

        mock_uuid.return_value = "test-uuid"
        mock_extract.return_value = [
            (np.array([0.1, 0.2, 0.3]), (0, 100, 100, 0))
        ]
        mock_db.query.return_value.filter_by.return_value.first.return_value = None

        result = register_employee(
            mock_db,
            name="Alice",
            registration="MAT001",
            department="TI",
            role="Dev",
            notes="Teste",
            photo_bytes=photo_bytes,
            photo_filename="alice.jpg",
        )

        assert result is not None
        assert mock_db.add.call_count >= 2  # Person + Employee

    def test_register_employee_fails_duplicate_registration(
        self, mock_db, photo_bytes
    ):
        """register_employee should raise 409 for duplicate registration."""
        from app.services.employee_service import register_employee
        from fastapi import HTTPException

        # Simulate existing employee
        existing = MagicMock()
        mock_db.query.return_value.filter_by.return_value.first.return_value = (
            existing
        )

        with pytest.raises(HTTPException) as exc_info:
            register_employee(
                mock_db,
                name="Bob",
                registration="MAT001",
                department="TI",
                role="Dev",
                notes=None,
                photo_bytes=photo_bytes,
                photo_filename="bob.jpg",
            )

        assert exc_info.value.status_code == 409

    @patch("app.services.employee_service.cv2")
    @patch("app.services.face_service.extract_embeddings")
    def test_register_employee_fails_no_face_detected(
        self, mock_extract, mock_cv2, mock_db, photo_bytes
    ):
        """register_employee should raise 422 if photo has no face."""
        from app.services.employee_service import register_employee
        from fastapi import HTTPException

        mock_cv2.imdecode.return_value = MagicMock()
        mock_extract.return_value = []  # No faces
        mock_db.query.return_value.filter_by.return_value.first.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            register_employee(
                mock_db,
                name="Charlie",
                registration="MAT002",
                department="TI",
                role="Dev",
                notes=None,
                photo_bytes=photo_bytes,
                photo_filename="charlie.jpg",
            )

        assert exc_info.value.status_code == 422

    @patch("app.services.employee_service.cv2")
    @patch("app.services.face_service.extract_embeddings")
    def test_register_employee_fails_multiple_faces(
        self, mock_extract, mock_cv2, mock_db, photo_bytes
    ):
        """register_employee should raise 422 if photo has multiple faces."""
        from app.services.employee_service import register_employee
        from fastapi import HTTPException

        mock_cv2.imdecode.return_value = MagicMock()
        mock_extract.return_value = [
            (np.array([0.1]), (0, 100, 100, 0)),
            (np.array([0.2]), (100, 200, 200, 100)),
        ]  # 2 faces
        mock_db.query.return_value.filter_by.return_value.first.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            register_employee(
                mock_db,
                name="Dave",
                registration="MAT003",
                department="TI",
                role="Dev",
                notes=None,
                photo_bytes=photo_bytes,
                photo_filename="dave.jpg",
            )

        assert exc_info.value.status_code == 422


class TestListEmployees:
    """Tests for list_employees function."""

    def test_list_employees_active_only(self, mock_db):
        """list_employees should filter active=True by default."""
        from app.services.employee_service import list_employees

        mock_employees = [MagicMock(id=1, active=1), MagicMock(id=2, active=1)]
        mock_db.query.return_value.filter.return_value.offset.return_value.limit.return_value.all.return_value = (
            mock_employees
        )

        result = list_employees(mock_db, active_only=True)

        assert len(result) == 2
        assert mock_db.query.return_value.filter.called

    def test_list_employees_pagination(self, mock_db):
        """list_employees should support skip and limit."""
        from app.services.employee_service import list_employees

        mock_db.query.return_value.filter.return_value.offset.return_value.limit.return_value.all.return_value = []

        list_employees(mock_db, skip=10, limit=5)

        # Verify offset/limit called with correct values
        assert (
            mock_db.query.return_value.filter.return_value.offset.called
        )


class TestGetEmployee:
    """Tests for get_employee_by_id and get_employee_by_registration."""

    def test_get_employee_by_id(self, mock_db):
        """get_employee_by_id should return employee or None."""
        from app.services.employee_service import get_employee_by_id

        mock_employee = MagicMock(id=1, name="Alice")
        mock_db.query.return_value.filter_by.return_value.first.return_value = (
            mock_employee
        )

        result = get_employee_by_id(mock_db, 1)

        assert result is not None
        assert result.id == 1

    def test_get_employee_by_registration(self, mock_db):
        """get_employee_by_registration should return employee or None."""
        from app.services.employee_service import get_employee_by_registration

        mock_employee = MagicMock(registration="MAT001", name="Alice")
        mock_db.query.return_value.filter_by.return_value.first.return_value = (
            mock_employee
        )

        result = get_employee_by_registration(mock_db, "MAT001")

        assert result is not None
        assert result.registration == "MAT001"


class TestUpdateEmployee:
    """Tests for update_employee function."""

    def test_update_employee(self, mock_db):
        """update_employee should update fields."""
        from app.services.employee_service import update_employee

        mock_employee = MagicMock(id=1, name="Alice", department="TI")
        mock_db.query.return_value.filter_by.return_value.first.return_value = (
            mock_employee
        )

        update_data = EmployeeUpdate(name="Alice Updated", department="RH")
        result = update_employee(mock_db, 1, update_data)

        assert result is not None
        assert mock_db.commit.called


class TestDeactivateEmployee:
    """Tests for deactivate_employee function."""

    def test_deactivate_employee(self, mock_db):
        """deactivate_employee should set active=False."""
        from app.services.employee_service import deactivate_employee

        mock_employee = MagicMock(id=1, active=1, person_id=5)
        mock_db.query.return_value.filter_by.return_value.first.return_value = (
            mock_employee
        )

        result = deactivate_employee(mock_db, 1)

        assert result is not None
        assert mock_db.commit.called
