import subprocess
import json
import logging
from pathlib import Path
from app.core.settings import settings
from app.core.ffmpeg_check import FFMPEG_AVAILABLE

logger = logging.getLogger(__name__)

CONVERTIBLE_FORMATS = {".ts", ".mkv", ".mov"}
NATIVE_FORMATS = {".mp4", ".avi"}


def needs_conversion(file_path: Path) -> bool:
    """Verifica se arquivo precisa ser convertido para MP4."""
    return file_path.suffix.lower() in CONVERTIBLE_FORMATS


def convert_to_mp4(
    input_path: Path,
    output_dir: Path | None = None
) -> Path:
    """Converte vídeo para MP4 via ffmpeg."""
    if not FFMPEG_AVAILABLE:
        raise RuntimeError(
            f"ffmpeg não disponível. Instale para converter {input_path.suffix}."
        )

    if output_dir is None:
        output_dir = input_path.parent

    output_path = output_dir / (input_path.stem + "_converted.mp4")

    cmd = [
        settings.FFMPEG_PATH,
        "-i", str(input_path),
        "-c:v", "copy",
        "-c:a", "copy",
        "-y",
        str(output_path)
    ]

    logger.info(f"Convertendo {input_path.name} → {output_path.name}")

    result = subprocess.run(
        cmd,
        capture_output=True,
        timeout=3600
    )

    if result.returncode != 0:
        error = result.stderr.decode()
        logger.error(f"Erro na conversão: {error}")
        raise subprocess.CalledProcessError(
            result.returncode, cmd, result.stdout, result.stderr
        )

    logger.info(f"Conversão OK: {output_path.name}")
    return output_path


def get_video_duration_seconds(file_path: Path) -> float | None:
    """Retorna duração do vídeo em segundos via ffprobe."""
    if not FFMPEG_AVAILABLE:
        return None

    ffprobe = settings.FFMPEG_PATH.replace("ffmpeg", "ffprobe")

    cmd = [
        ffprobe,
        "-v", "quiet",
        "-print_format", "json",
        "-show_format",
        str(file_path)
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, timeout=30)
        if result.returncode == 0:
            data = json.loads(result.stdout.decode())
            duration = float(data.get("format", {}).get("duration", 0))
            return duration if duration > 0 else None
    except Exception as e:
        logger.warning(f"ffprobe falhou: {e}")
    return None


def _recover_raw_h264_stream(input_path: Path, output_h264_path: Path) -> bool:
    try:
        with open(input_path, "rb") as f_in:
            header = f_in.read(1024)
            idx = header.find(b"mdat")
            if idx == -1:
                logger.error("recovery: box mdat não encontrado no cabeçalho")
                return False
            f_in.seek(idx + 4)
            
            with open(output_h264_path, "wb") as f_out:
                count = 0
                while True:
                    len_bytes = f_in.read(4)
                    if not len_bytes or len(len_bytes) < 4:
                        break
                    length = int.from_bytes(len_bytes, byteorder="big")
                    if length == 0 or length > 50000000:
                        break
                    nal_data = f_in.read(length)
                    if len(nal_data) < length:
                        break
                    f_out.write(b"\x00\x00\x00\x01" + nal_data)
                    count += 1
                logger.info(f"recovery: extraídos {count} NAL units para formato Annex B")
                return count > 0
    except Exception as e:
        logger.error(f"recovery: erro ao analisar avcC: {e}")
        return False


def repair_mp4_moov(input_path: Path) -> Path:
    """
    Reescreve o arquivo MP4 com moov atom no início (faststart).
    Necessário para arquivos de câmera de segurança que gravam
    o moov atom no final do arquivo.

    Retorna o path do arquivo reparado.
    Lança RuntimeError se ffmpeg não disponível.
    Lança subprocess.CalledProcessError se reparo falhar.
    """
    if not FFMPEG_AVAILABLE:
        raise RuntimeError("ffmpeg necessário para reparar arquivo MP4.")

    output_path = input_path.parent / (
        input_path.stem + "_faststart.mp4"
    )

    cmd = [
        settings.FFMPEG_PATH,
        "-i", str(input_path),
        "-c", "copy",
        "-movflags", "faststart",
        "-y",
        str(output_path)
    ]

    logger.info(f"Reparando moov atom: {input_path.name}")

    result = subprocess.run(
        cmd,
        capture_output=True,
        timeout=3600
    )

    if result.returncode != 0:
        error = result.stderr.decode()
        logger.error(f"Erro ao reparar: {error}")
        
        if "moov atom not found" in error:
            temp_h264 = input_path.parent / (input_path.stem + "_temp.h264")
            temp_mp4 = input_path.parent / (input_path.stem + "_temp.mp4")
            logger.info(f"Tentando recuperar stream raw H264 de {input_path.name}...")
            if _recover_raw_h264_stream(input_path, temp_h264):
                mux_cmd = [
                    settings.FFMPEG_PATH,
                    "-y",
                    "-f", "h264",
                    "-i", str(temp_h264),
                    "-c", "copy",
                    "-movflags", "faststart",
                    str(temp_mp4)
                ]
                mux_result = subprocess.run(mux_cmd, capture_output=True, timeout=3600)
                if mux_result.returncode == 0:
                    if temp_h264.exists():
                        temp_h264.unlink()
                    input_path.unlink()
                    temp_mp4.rename(input_path)
                    logger.info(f"Recuperação bem-sucedida: {input_path.name}")
                    return input_path
                else:
                    logger.error(f"Erro ao remuxar stream recuperada: {mux_result.stderr.decode()}")
            
            if temp_h264.exists():
                temp_h264.unlink()
            if temp_mp4.exists():
                temp_mp4.unlink()

        raise subprocess.CalledProcessError(
            result.returncode, cmd, result.stdout, result.stderr
        )

    # Substituir o original pelo reparado
    input_path.unlink()
    output_path.rename(input_path)

    logger.info(f"Reparo concluído: {input_path.name}")
    return input_path


def can_opencv_read(file_path: Path) -> bool:
    """
    Verifica se o OpenCV consegue abrir o arquivo de vídeo.
    Retorna False se o arquivo estiver corrompido ou
    com moov atom no final.
    """
    import cv2
    cap = cv2.VideoCapture(str(file_path))
    readable = cap.isOpened()
    frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    cap.release()
    # Frame count <= 0 indica arquivo ilegível mesmo se isOpened()
    return readable and frame_count > 0

