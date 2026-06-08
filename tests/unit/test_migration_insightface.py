import numpy as np
import pytest
from pathlib import Path


def test_migration_deletes_128dim_npy(tmp_path):
    npy = tmp_path / "1_embedding.npy"
    np.save(str(npy), np.zeros(128))

    from app.db.migrations.migration_insightface import run
    run(storage_dir=tmp_path)

    assert not npy.exists()


def test_migration_preserves_512dim_npy(tmp_path):
    npy = tmp_path / "1_embedding_0.npy"
    np.save(str(npy), np.zeros(512))

    from app.db.migrations.migration_insightface import run
    run(storage_dir=tmp_path)

    assert npy.exists()


def test_migration_preserves_jpg(tmp_path):
    jpg = tmp_path / "1.jpg"
    jpg.write_bytes(b"\xff\xd8\xff")

    from app.db.migrations.migration_insightface import run
    run(storage_dir=tmp_path)

    assert jpg.exists()


def test_migration_idempotent(tmp_path):
    npy = tmp_path / "1_embedding.npy"
    np.save(str(npy), np.zeros(128))

    from app.db.migrations.migration_insightface import run
    run(storage_dir=tmp_path)
    run(storage_dir=tmp_path)


def test_migration_handles_missing_directory(tmp_path):
    from app.db.migrations.migration_insightface import run
    run(storage_dir=tmp_path / "nonexistent")


def test_migration_deletes_old_single_embedding_npy(tmp_path):
    npy = tmp_path / "42_embedding.npy"
    np.save(str(npy), np.zeros(128))

    from app.db.migrations.migration_insightface import run
    run(storage_dir=tmp_path)

    assert not npy.exists()
