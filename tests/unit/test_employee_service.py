import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.schemas.employee import EmployeeCreate, EmployeeUpdate
from app.models import Employee, Person


@pytest.fixture
def mock_db():
    return MagicMock(spec=Session)


@pytest.fixture
def photo_bytes():
    return b"fake_jpeg_data"


def _make_mock_face(embedding=None):
    import numpy as np
    face = MagicMock()
    face.embedding = embedding if embedding is not None else (
        lambda v: v / __import__('numpy').linalg.norm(v)
    )(__import__('numpy').ones(512, dtype=__import__('numpy').float32))
    return face


def _patch_face_app(faces: list):
    mock_app = MagicMock()
    mock_app.get.return_value = faces
    return patch("app.services.employee_service.get_face_app", return_value=mock_app)


class TestRegisterEmployee:

    @patch("app.services.employee_service.cv2")
    @patch("app.services.employee_service.uuid4")
    @patch("app.services.employee_service.np.save")
    def test_register_employee_creates_employee_and_person(
        self, mock_np_save, mock_uuid, mock_cv2, mock_db, photo_bytes
    ):
        from app.services.employee_service import register_employee

        mock_uuid.return_value = "test-uuid"
        mock_cv2.imdecode.return_value = MagicMock()

        mock_db.query.return_value.filter_by.return_value.first.return_value = None

        with _patch_face_app([_make_mock_face()]):
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

    @patch("app.services.employee_service.face_recognition_unused", create=True)
    def test_register_employee_fails_duplicate_registration(
        self, _unused, mock_db, photo_bytes
    ):
        from app.services.employee_service import register_employee
        from fastapi import HTTPException

        existing = MagicMock()
        mock_db.query.return_value.filter_by.return_value.first.return_value = existing

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
    def test_register_employee_fails_no_face_detected(
        self, mock_cv2, mock_db, photo_bytes
    ):
        from app.services.employee_service import register_employee
        from fastapi import HTTPException

        mock_cv2.imdecode.return_value = MagicMock()
        mock_db.query.return_value.filter_by.return_value.first.return_value = None

        with _patch_face_app([]):
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
    def test_register_employee_fails_multiple_faces(
        self, mock_cv2, mock_db, photo_bytes
    ):
        from app.services.employee_service import register_employee
        from fastapi import HTTPException

        mock_cv2.imdecode.return_value = MagicMock()
        mock_db.query.return_value.filter_by.return_value.first.return_value = None

        with _patch_face_app([_make_mock_face(), _make_mock_face()]):
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

    def test_list_employees_active_only(self, mock_db):
        from app.services.employee_service import list_employees

        mock_employees = [MagicMock(id=1, active=1), MagicMock(id=2, active=1)]
        mock_db.query.return_value.filter.return_value.offset.return_value.limit.return_value.all.return_value = (
            mock_employees
        )

        result = list_employees(mock_db, active_only=True)

        assert len(result) == 2
        assert mock_db.query.return_value.filter.called

    def test_list_employees_pagination(self, mock_db):
        from app.services.employee_service import list_employees

        mock_db.query.return_value.filter.return_value.offset.return_value.limit.return_value.all.return_value = []

        list_employees(mock_db, skip=10, limit=5)

        assert mock_db.query.return_value.filter.return_value.offset.called


class TestGetEmployee:

    def test_get_employee_by_id(self, mock_db):
        from app.services.employee_service import get_employee_by_id

        mock_employee = MagicMock(id=1, name="Alice")
        mock_db.query.return_value.filter_by.return_value.first.return_value = mock_employee

        result = get_employee_by_id(mock_db, 1)

        assert result is not None
        assert result.id == 1

    def test_get_employee_by_registration(self, mock_db):
        from app.services.employee_service import get_employee_by_registration

        mock_employee = MagicMock(registration="MAT001", name="Alice")
        mock_db.query.return_value.filter_by.return_value.first.return_value = mock_employee

        result = get_employee_by_registration(mock_db, "MAT001")

        assert result is not None
        assert result.registration == "MAT001"


class TestUpdateEmployee:

    def test_update_employee(self, mock_db):
        from app.services.employee_service import update_employee

        mock_employee = MagicMock(id=1, name="Alice", department="TI")
        mock_db.query.return_value.filter_by.return_value.first.return_value = mock_employee

        update_data = EmployeeUpdate(name="Alice Updated", department="RH")
        result = update_employee(mock_db, 1, update_data)

        assert result is not None
        assert mock_db.commit.called


class TestDeactivateEmployee:

    def test_deactivate_employee(self, mock_db):
        from app.services.employee_service import deactivate_employee

        mock_employee = MagicMock(id=1, active=1, person_id=5)
        mock_db.query.return_value.filter_by.return_value.first.return_value = mock_employee

        result = deactivate_employee(mock_db, 1)

        assert result is not None
        assert mock_db.commit.called


class TestPromotePersonToEmployee:

    def test_promote_creates_employee_linked_to_person(self, mock_db):
        from app.services.employee_service import promote_person_to_employee

        mock_person = MagicMock(id=5, name="Ana", profile_image_path="storage/faces/ana.jpg", employee=None)

        call_count = {"n": 0}

        def query_side_effect(model):
            call_count["n"] += 1
            m = MagicMock()
            if call_count["n"] == 1:
                # Person lookup
                m.filter_by.return_value.first.return_value = mock_person
            else:
                # Employee registration duplicate check
                m.filter_by.return_value.first.return_value = None
            return m

        mock_db.query.side_effect = query_side_effect

        result = promote_person_to_employee(mock_db, 5, "MAT100", "RH", "Analista", None)

        assert result is not None
        assert mock_db.add.called
        assert mock_db.commit.called

    def test_promote_person_not_found_raises_404(self, mock_db):
        from app.services.employee_service import promote_person_to_employee
        from fastapi import HTTPException

        mock_db.query.return_value.filter_by.return_value.first.return_value = None

        with pytest.raises(HTTPException) as exc:
            promote_person_to_employee(mock_db, 99, "MAT100", None, None, None)

        assert exc.value.status_code == 404

    def test_promote_already_employee_raises_409(self, mock_db):
        from app.services.employee_service import promote_person_to_employee
        from fastapi import HTTPException

        mock_person = MagicMock(id=5, name="Ana", employee=MagicMock())
        mock_db.query.return_value.filter_by.return_value.first.return_value = mock_person

        with pytest.raises(HTTPException) as exc:
            promote_person_to_employee(mock_db, 5, "MAT100", None, None, None)

        assert exc.value.status_code == 409
        assert "já é funcionária" in exc.value.detail

    def test_promote_duplicate_registration_raises_409(self, mock_db):
        from app.services.employee_service import promote_person_to_employee
        from fastapi import HTTPException

        mock_person = MagicMock(id=5, name="Ana", employee=None)
        existing_emp = MagicMock(registration="MAT100")

        call_count = {"n": 0}

        def query_side_effect(model):
            call_count["n"] += 1
            m = MagicMock()
            if call_count["n"] == 1:
                m.filter_by.return_value.first.return_value = mock_person
            else:
                m.filter_by.return_value.first.return_value = existing_emp
            return m

        mock_db.query.side_effect = query_side_effect

        with pytest.raises(HTTPException) as exc:
            promote_person_to_employee(mock_db, 5, "MAT100", None, None, None)

        assert exc.value.status_code == 409
        assert "Matrícula" in exc.value.detail
