import time
from pathlib import Path


def safe_unlink(path: Path, missing_ok: bool = True, retries: int = 3, delay: float = 0.2) -> None:
    """Remove arquivo com retry em PermissionError (Windows file locking)."""
    for attempt in range(retries):
        try:
            path.unlink(missing_ok=missing_ok)
            return
        except PermissionError:
            if attempt == retries - 1:
                raise
            time.sleep(delay)
        except FileNotFoundError:
            if not missing_ok:
                raise
            return
