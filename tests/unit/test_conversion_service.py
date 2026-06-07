import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
import subprocess
from app.services.conversion_service import (
    needs_conversion, convert_to_mp4, get_video_duration_seconds
)


def test_needs_conversion_true_for_ts():
    assert needs_conversion(Path("video.ts")) is True


def test_needs_conversion_true_for_mkv():
    assert needs_conversion(Path("video.mkv")) is True


def test_needs_conversion_true_for_mov():
    assert needs_conversion(Path("video.mov")) is True


def test_needs_conversion_false_for_mp4():
    assert needs_conversion(Path("video.mp4")) is False


def test_needs_conversion_false_for_avi():
    assert needs_conversion(Path("video.avi")) is False


def test_convert_to_mp4_raises_runtime_error_if_ffmpeg_unavailable():
    with patch('app.services.conversion_service.FFMPEG_AVAILABLE', False):
        with pytest.raises(RuntimeError):
            convert_to_mp4(Path("video.ts"))


def test_convert_to_mp4_calls_subprocess_with_correct_args(tmp_path):
    test_file = tmp_path / "video.ts"
    test_file.write_bytes(b"fake video")

    with patch('app.services.conversion_service.FFMPEG_AVAILABLE', True):
        with patch('app.services.conversion_service.subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            with patch('app.services.conversion_service.Path.stat'):
                result = convert_to_mp4(test_file, tmp_path)

            assert mock_run.called
            call_args = mock_run.call_args[0][0]
            assert "-i" in call_args
            assert str(test_file) in call_args
            assert "_converted.mp4" in str(result)


def test_convert_to_mp4_raises_called_process_error_on_failure(tmp_path):
    test_file = tmp_path / "video.ts"
    test_file.write_bytes(b"fake")

    with patch('app.services.conversion_service.FFMPEG_AVAILABLE', True):
        with patch('app.services.conversion_service.subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(
                returncode=1,
                stderr=b"conversion failed"
            )
            with pytest.raises(subprocess.CalledProcessError):
                convert_to_mp4(test_file, tmp_path)


def test_get_video_duration_seconds_returns_float(tmp_path):
    test_file = tmp_path / "video.mp4"
    test_file.write_bytes(b"fake")

    with patch('app.services.conversion_service.FFMPEG_AVAILABLE', True):
        with patch('app.services.conversion_service.subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout=b'{"format": {"duration": "120.5"}}'
            )
            result = get_video_duration_seconds(test_file)
            assert isinstance(result, float)
            assert result == 120.5


def test_get_video_duration_seconds_returns_none_if_unavailable(tmp_path):
    test_file = tmp_path / "video.mp4"
    test_file.write_bytes(b"fake")

    with patch('app.services.conversion_service.FFMPEG_AVAILABLE', False):
        result = get_video_duration_seconds(test_file)
        assert result is None


def test_get_video_duration_seconds_returns_none_on_error(tmp_path):
    test_file = tmp_path / "video.mp4"
    test_file.write_bytes(b"fake")

    with patch('app.services.conversion_service.FFMPEG_AVAILABLE', True):
        with patch('app.services.conversion_service.subprocess.run') as mock_run:
            mock_run.side_effect = Exception("ffprobe error")
            result = get_video_duration_seconds(test_file)
            assert result is None
