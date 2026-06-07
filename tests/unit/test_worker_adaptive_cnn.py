import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from app.workers.video_worker import get_adaptive_params


def test_adaptive_params_short_video():
    """Vídeo < 10min → modo preciso."""
    with patch('app.workers.video_worker.get_video_duration_seconds') as mock_dur:
        mock_dur.return_value = 300.0

        params = get_adaptive_params(Path("short.mp4"))

        assert params['upsample'] == 2
        assert params['fps_sample'] == 2
        assert 'preciso' in params['mode'].lower()


def test_adaptive_params_medium_video():
    """Vídeo 10-60min → modo equilibrado."""
    with patch('app.workers.video_worker.get_video_duration_seconds') as mock_dur:
        mock_dur.return_value = 1800.0

        params = get_adaptive_params(Path("medium.mp4"))

        assert params['upsample'] == 1
        assert params['fps_sample'] == 2
        assert 'equilibrado' in params['mode'].lower()


def test_adaptive_params_long_video():
    """Vídeo > 60min → modo eficiente."""
    with patch('app.workers.video_worker.get_video_duration_seconds') as mock_dur:
        mock_dur.return_value = 7200.0

        params = get_adaptive_params(Path("long.mp4"))

        assert params['upsample'] == 1
        assert params['fps_sample'] == 1
        assert 'eficiente' in params['mode'].lower()


def test_adaptive_params_no_duration():
    """Sem ffprobe → parâmetros padrão."""
    with patch('app.workers.video_worker.get_video_duration_seconds') as mock_dur:
        mock_dur.return_value = None

        params = get_adaptive_params(Path("unknown.mp4"))

        assert params['duration'] is None
        assert 'padrão' in params['mode'].lower()


def test_adaptive_params_dict_structure():
    """get_adaptive_params retorna dict com campos obrigatórios."""
    with patch('app.workers.video_worker.get_video_duration_seconds') as mock_dur:
        mock_dur.return_value = 600.0

        params = get_adaptive_params(Path("test.mp4"))

        assert 'model' in params
        assert 'upsample' in params
        assert 'fps_sample' in params
        assert 'duration' in params
        assert 'mode' in params
