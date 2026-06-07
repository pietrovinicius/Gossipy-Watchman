import pytest
from unittest.mock import patch, MagicMock
from app.core.ffmpeg_check import check_ffmpeg, get_ffmpeg_status


def test_check_ffmpeg_returns_true_when_available():
    """ffmpeg disponível no PATH."""
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=b'ffmpeg version 6.0.1'
        )
        result = check_ffmpeg()
        assert result is True


def test_check_ffmpeg_returns_false_when_not_found():
    """ffmpeg não encontrado."""
    with patch('subprocess.run') as mock_run:
        mock_run.side_effect = FileNotFoundError()
        result = check_ffmpeg()
        assert result is False


def test_check_ffmpeg_returns_false_on_timeout():
    """ffmpeg timeout."""
    import subprocess
    with patch('subprocess.run') as mock_run:
        mock_run.side_effect = subprocess.TimeoutExpired('ffmpeg', 10)
        result = check_ffmpeg()
        assert result is False


def test_check_ffmpeg_returns_false_on_error():
    """ffmpeg retorna erro (returncode != 0)."""
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = MagicMock(returncode=1)
        result = check_ffmpeg()
        assert result is False


def test_get_ffmpeg_status_returns_dict_with_available_true():
    """get_ffmpeg_status retorna dict com available=True."""
    with patch('app.core.ffmpeg_check.FFMPEG_AVAILABLE', True):
        status = get_ffmpeg_status()
        assert status['available'] is True
        assert 'path' in status
        assert 'message' in status
        assert 'disponível' in status['message'].lower()


def test_get_ffmpeg_status_returns_dict_with_available_false():
    """get_ffmpeg_status retorna dict com available=False."""
    with patch('app.core.ffmpeg_check.FFMPEG_AVAILABLE', False):
        status = get_ffmpeg_status()
        assert status['available'] is False
        assert 'não encontrado' in status['message'].lower()
