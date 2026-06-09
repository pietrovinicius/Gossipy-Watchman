import time
from pathlib import Path
from unittest.mock import MagicMock, patch, call


def test_safe_unlink_deletes_file(tmp_path):
    from app.core.path_utils import safe_unlink

    f = tmp_path / "test.mp4"
    f.write_bytes(b"data")
    safe_unlink(f)
    assert not f.exists()


def test_safe_unlink_missing_ok_true(tmp_path):
    from app.core.path_utils import safe_unlink

    f = tmp_path / "nonexistent.mp4"
    safe_unlink(f, missing_ok=True)  # deve não lançar


def test_safe_unlink_missing_ok_false_raises(tmp_path):
    import pytest
    from app.core.path_utils import safe_unlink

    f = tmp_path / "nonexistent.mp4"
    with pytest.raises(FileNotFoundError):
        safe_unlink(f, missing_ok=False)


def test_safe_unlink_retries_on_permission_error(tmp_path):
    from app.core.path_utils import safe_unlink

    f = tmp_path / "locked.mp4"
    f.write_bytes(b"data")

    call_count = 0

    original_unlink = Path.unlink

    def flaky_unlink(self, missing_ok=False):
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise PermissionError("file locked")
        original_unlink(self, missing_ok=missing_ok)

    with patch.object(Path, "unlink", flaky_unlink):
        with patch("time.sleep"):
            safe_unlink(f, retries=3)

    assert call_count == 3


def test_safe_unlink_raises_after_max_retries(tmp_path):
    import pytest
    from app.core.path_utils import safe_unlink

    f = tmp_path / "locked.mp4"
    f.write_bytes(b"data")

    with patch.object(Path, "unlink", side_effect=PermissionError("always locked")):
        with patch("time.sleep"):
            with pytest.raises(PermissionError):
                safe_unlink(f, retries=3)
