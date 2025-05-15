import subprocess
import os
import uuid
import logging
from typing import Optional
from src.utils.constants import TEMP_DIR

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def get_video_with_subtitles(video_path: str, ass_path: str, output_path: str = None) -> str:
    """
    Adds ASS subtitles to a video and saves the output.

    Args:
        video_path (str): Path to the input video file.
        ass_path (str): Path to the ASS subtitle file.
        output_path (str): Path where the output video will be saved.

    Returns:
        str: Absolute path to the output video file.

    Raises:
        RuntimeError: If ffmpeg processing fails.
    """
    try:
        if not output_path:
            output_path = os.path.join(TEMP_DIR, f"{uuid.uuid4()}_preview.mp4")

        cmd = [
            "ffmpeg", "-y", "-i", adjust_path(video_path),
            "-vf", f"ass={adjust_path(ass_path)}",
            "-c:a", "copy",
            adjust_path(output_path)
        ]
        logger.info(f"Running command: {' '.join(cmd)}")
        subprocess.run(cmd, check=True, cwd=TEMP_DIR)
        return os.path.abspath(output_path)
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to embed subtitles: {e}")
        raise RuntimeError(f"FFmpeg subtitle processing failed: {e}") from e


def get_preview_image(video_path: str, ass_path: str, output_path: Optional[str] = None, timestamp: float = 0.0) -> str:
    """
    Generates a preview image from a video at a given timestamp with ASS subtitles.

    Args:
        video_path (str): Path to the video file.
        ass_path (str): Path to the ASS subtitle file.
        output_path (Optional[str]): Optional path for saving the image.
        timestamp (float): Time (in seconds) from which to capture the frame.

    Returns:
        str: Absolute path to the preview image.
    """
    try:
        if not output_path:
            output_path = os.path.join(TEMP_DIR, f"{uuid.uuid4()}_preview.jpg")

        cmd = [
            "ffmpeg", "-y",
            "-ss", str(timestamp),
            "-i", adjust_path(video_path),
            "-vf", f"ass={adjust_path(ass_path)}",
            "-vframes", "1",
            "-q:v", "2",
            adjust_path(output_path)
        ]
        logger.info(f"Generating preview image with command: {' '.join(cmd)}")
        subprocess.run(cmd, check=True, cwd=TEMP_DIR)
        return os.path.abspath(output_path)
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to generate preview image: {e}")
        raise RuntimeError(f"FFmpeg preview image generation failed: {e}") from e


def adjust_path(path: str, cwd: str = TEMP_DIR) -> str:
    """
    Adjusts the provided path relative to the given `cwd` directory and normalizes path separators.

    Args:
        path (str): Input file path that needs to be adjusted.
        cwd (str): The current working directory (defaults to TEMP_DIR).

    Returns:
        str: The path relative to `cwd`, with normalized forward slashes.

    """
    abs_path = os.path.abspath(path)
    relative_path = os.path.relpath(abs_path, cwd)
    return relative_path.replace('\\', '/')
