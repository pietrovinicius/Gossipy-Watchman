import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
import subprocess
from app.services.conversion_service import (
    needs_conversion, convert_to_mp4, get_video_duration_seconds,
    can_opencv_read, repair_mp4_moov
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


def test_needs_conversion_true_for_dav():
    assert needs_conversion(Path("video.dav")) is True


def test_native_formats_does_not_include_dav():
    from app.services.conversion_service import NATIVE_FORMATS
    assert ".dav" not in NATIVE_FORMATS


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


# ── can_opencv_read ───────────────────────────────────────────────────────────

def test_can_opencv_read_false_when_not_opened():
    from app.services.conversion_service import can_opencv_read
    with patch("cv2.VideoCapture") as mock_vc:
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = False
        mock_vc.return_value = mock_cap
        
        result = can_opencv_read(Path("video.mp4"))
        assert result is False
        mock_cap.release.assert_called_once()


def test_can_opencv_read_false_when_frame_count_zero_or_less():
    from app.services.conversion_service import can_opencv_read
    import cv2
    with patch("cv2.VideoCapture") as mock_vc:
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.get.return_value = 0  # frame_count <= 0
        mock_vc.return_value = mock_cap
        
        result = can_opencv_read(Path("video.mp4"))
        assert result is False
        mock_cap.get.assert_called_once_with(cv2.CAP_PROP_FRAME_COUNT)
        mock_cap.release.assert_called_once()


def test_can_opencv_read_true_for_valid_video():
    from app.services.conversion_service import can_opencv_read
    import cv2
    with patch("cv2.VideoCapture") as mock_vc:
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.get.return_value = 100  # frame_count > 0
        mock_vc.return_value = mock_cap
        
        result = can_opencv_read(Path("video.mp4"))
        assert result is True
        mock_cap.get.assert_called_once_with(cv2.CAP_PROP_FRAME_COUNT)
        mock_cap.release.assert_called_once()


# ── repair_mp4_moov ───────────────────────────────────────────────────────────

def test_repair_mp4_moov_calls_ffmpeg_with_faststart_flags(tmp_path):
    from app.services.conversion_service import repair_mp4_moov
    
    test_file = tmp_path / "video.mp4"
    test_file.write_bytes(b"fake video")
    
    with patch("app.services.conversion_service.FFMPEG_AVAILABLE", True):
        with patch("app.services.conversion_service.subprocess.run") as mock_run:
            def side_effect(cmd, **kwargs):
                output_path_str = cmd[-1]
                Path(output_path_str).write_bytes(b"repaired video")
                return MagicMock(returncode=0)
                
            mock_run.side_effect = side_effect
            
            result = repair_mp4_moov(test_file)
            
            assert mock_run.called
            call_args = mock_run.call_args[0][0]
            assert "-movflags" in call_args
            assert "faststart" in call_args
            assert "-c" in call_args
            assert "copy" in call_args
            assert result == test_file


def test_repair_mp4_moov_replaces_original_file(tmp_path):
    from app.services.conversion_service import repair_mp4_moov
    
    test_file = tmp_path / "video.mp4"
    test_file.write_bytes(b"original")
    
    with patch("app.services.conversion_service.FFMPEG_AVAILABLE", True):
        with patch("app.services.conversion_service.subprocess.run") as mock_run:
            def side_effect(cmd, **kwargs):
                output_path_str = cmd[-1]
                Path(output_path_str).write_bytes(b"repaired")
                return MagicMock(returncode=0)
            mock_run.side_effect = side_effect
            
            result = repair_mp4_moov(test_file)
            
            assert result.exists()
            assert result.read_bytes() == b"repaired"
            temp_file = tmp_path / "video_faststart.mp4"
            assert not temp_file.exists()


def test_repair_mp4_moov_raises_runtime_error_if_ffmpeg_unavailable(tmp_path):
    from app.services.conversion_service import repair_mp4_moov
    test_file = tmp_path / "video.mp4"
    
    with patch("app.services.conversion_service.FFMPEG_AVAILABLE", False):
        with pytest.raises(RuntimeError) as exc:
            repair_mp4_moov(test_file)
        assert "ffmpeg necessário" in str(exc.value)


def test_repair_mp4_moov_raises_called_process_error_if_ffmpeg_fails(tmp_path):
    from app.services.conversion_service import repair_mp4_moov
    test_file = tmp_path / "video.mp4"
    test_file.write_bytes(b"fake")
    
    with patch("app.services.conversion_service.FFMPEG_AVAILABLE", True):
        with patch("app.services.conversion_service.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(
                returncode=1,
                stderr=b"ffmpeg failure"
            )
            with pytest.raises(subprocess.CalledProcessError):
                repair_mp4_moov(test_file)


def test_repair_mp4_moov_falls_back_to_h264_recovery_on_missing_moov(tmp_path):
    from app.services.conversion_service import repair_mp4_moov
    
    test_file = tmp_path / "video.mp4"
    content = b"fakeheader_mdat" + b"\x00\x00\x00\x04\x67\x00\x00\x00" + b"\x00\x00\x00\x04\x68\x00\x00\x00"
    test_file.write_bytes(content)
    
    with patch("app.services.conversion_service.FFMPEG_AVAILABLE", True):
        with patch("app.services.conversion_service.subprocess.run") as mock_run, \
             patch("app.services.conversion_service.subprocess.Popen") as mock_popen:
             
            mock_run.return_value = MagicMock(returncode=1, stderr=b"moov atom not found")
            
            mock_process = MagicMock()
            mock_popen.return_value = mock_process
            
            def side_effect(*args, **kwargs):
                # Escrever o arquivo de saída temporário esperado
                temp_mp4 = tmp_path / "video_temp.mp4"
                temp_mp4.write_bytes(b"recovered mp4")
                return 0
            mock_process.wait.side_effect = side_effect
            
            result = repair_mp4_moov(test_file)
            assert result == test_file
            assert test_file.read_bytes() == b"recovered mp4"


def test_detect_codec_from_first_nal_hevc(tmp_path):
    from app.services.conversion_service import _detect_codec_from_first_nal
    test_file = tmp_path / "hevc_video.mp4"
    # mdat seguido de NAL de 4 bytes com first_byte 0x40 (hevc_type = 32 VPS)
    content = b"fakeheader_mdat" + b"\x00\x00\x00\x04\x40\x00\x00\x00"
    test_file.write_bytes(content)
    assert _detect_codec_from_first_nal(test_file) == "hevc"


def test_detect_codec_from_first_nal_h264(tmp_path):
    from app.services.conversion_service import _detect_codec_from_first_nal
    test_file = tmp_path / "h264_video.mp4"
    # mdat seguido de NAL de 4 bytes com first_byte 0x67 (h264_type = 7 SPS)
    content = b"fakeheader_mdat" + b"\x00\x00\x00\x04\x67\x00\x00\x00"
    test_file.write_bytes(content)
    assert _detect_codec_from_first_nal(test_file) == "h264"


def test_repair_mp4_moov_falls_back_to_hevc_recovery_on_missing_moov(tmp_path):
    from app.services.conversion_service import repair_mp4_moov
    
    test_file = tmp_path / "video.mp4"
    # hevc_type = 32 (VPS)
    content = b"fakeheader_mdat" + b"\x00\x00\x00\x04\x40\x00\x00\x00"
    test_file.write_bytes(content)
    
    with patch("app.services.conversion_service.FFMPEG_AVAILABLE", True):
        with patch("app.services.conversion_service.subprocess.run") as mock_run, \
             patch("app.services.conversion_service.subprocess.Popen") as mock_popen:
             
            mock_run.return_value = MagicMock(returncode=1, stderr=b"moov atom not found")
            
            mock_process = MagicMock()
            mock_popen.return_value = mock_process
            
            def side_effect(*args, **kwargs):
                temp_mp4 = tmp_path / "video_temp.mp4"
                temp_mp4.write_bytes(b"recovered hevc mp4")
                return 0
            mock_process.wait.side_effect = side_effect
            
            result = repair_mp4_moov(test_file)
            assert result == test_file
            assert test_file.read_bytes() == b"recovered hevc mp4"
            
            # Verificar se popen foi chamado com -f hevc
            assert mock_popen.called
            called_args = mock_popen.call_args[0][0]
            idx_f = called_args.index("-f")
            assert called_args[idx_f + 1] == "hevc"




