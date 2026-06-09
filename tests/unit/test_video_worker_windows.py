import threading
from unittest.mock import MagicMock, patch, call


def test_process_video_calls_gc_collect_in_finally():
    """process_video deve chamar gc.collect() no bloco finally para liberar memória ONNX."""
    from app.workers import video_worker

    mock_engine = MagicMock()
    mock_session_cls = MagicMock()
    mock_db = MagicMock()
    mock_session_cls.return_value = mock_db

    mock_video = MagicMock()
    mock_db.get.return_value = mock_video

    with patch("app.workers.video_worker._get_session_factory", return_value=mock_session_cls):
        with patch("app.workers.video_worker.cv2") as mock_cv2:
            mock_cap = MagicMock()
            mock_cap.isOpened.return_value = False
            mock_cv2.VideoCapture.return_value = mock_cap
            with patch("app.workers.video_worker.gc") as mock_gc:
                video_worker.process_video(1, MagicMock(), _engine=mock_engine)
                mock_gc.collect.assert_called()


def test_processing_semaphore_exists_at_module_level():
    """_PROCESSING_SEMAPHORE deve existir como Semaphore(1) no módulo."""
    import threading
    from app.workers import video_worker

    assert hasattr(video_worker, "_PROCESSING_SEMAPHORE")
    assert isinstance(video_worker._PROCESSING_SEMAPHORE, threading.Semaphore)


def test_process_video_acquires_semaphore():
    """process_video deve adquirir e liberar _PROCESSING_SEMAPHORE."""
    from app.workers import video_worker

    mock_engine = MagicMock()
    mock_session_cls = MagicMock()
    mock_db = MagicMock()
    mock_session_cls.return_value = mock_db
    mock_db.get.return_value = MagicMock()

    acquire_calls = []
    release_calls = []

    original_acquire = video_worker._PROCESSING_SEMAPHORE.acquire
    original_release = video_worker._PROCESSING_SEMAPHORE.release

    def tracking_acquire(*args, **kwargs):
        acquire_calls.append(1)
        return original_acquire(*args, **kwargs)

    def tracking_release():
        release_calls.append(1)
        return original_release()

    with patch("app.workers.video_worker._get_session_factory", return_value=mock_session_cls):
        with patch("app.workers.video_worker.cv2") as mock_cv2:
            mock_cap = MagicMock()
            mock_cap.isOpened.return_value = False
            mock_cv2.VideoCapture.return_value = mock_cap
            with patch("app.workers.video_worker.gc"):
                with patch.object(video_worker._PROCESSING_SEMAPHORE, "acquire", side_effect=tracking_acquire):
                    with patch.object(video_worker._PROCESSING_SEMAPHORE, "release", side_effect=tracking_release):
                        video_worker.process_video(1, MagicMock(), _engine=mock_engine)

    assert len(acquire_calls) >= 1
    assert len(release_calls) >= 1
