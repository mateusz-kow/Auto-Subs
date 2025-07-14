import json
import os
import subprocess
import uuid
from logging import getLogger
from pathlib import Path
from typing import Optional, Union

from src.utils.constants import TEMP_DIR

logger = getLogger(__name__)


def get_video_with_subtitles(
    video_path: Union[str, Path],
    ass_path: Union[str, Path],
    output_path: Optional[Union[str, Path]] = None,
) -> Path:
    """
    Adds ASS subtitles to a video and saves the output.

    Args:
        video_path (Union[str, Path]): Path to the input video file.
        ass_path (Union[str, Path]): Path to the ASS subtitle file.
        output_path (Optional[Union[str, Path]]): Path where the output video will be saved.

    Returns:
        Path: Absolute path to the output video file.

    Raises:
        RuntimeError: If ffmpeg processing fails.
    """
    try:
        output_path = Path(output_path) if output_path else Path(TEMP_DIR) / f"{uuid.uuid4()}_preview.mp4"

        video_path = Path(video_path)
        ass_path = Path(ass_path)

        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            _adjust_path(video_path),
            "-vf",
            f"ass={_adjust_path(ass_path)}",
            "-c:a",
            "copy",
            _adjust_path(output_path),
        ]
        logger.info(f"Running command: {' '.join(cmd)}")
        subprocess.run(cmd, check=True, cwd=TEMP_DIR)
        return output_path.resolve()
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to embed subtitles: {e}")
        raise RuntimeError(f"FFmpeg subtitle processing failed: {e}") from e


def get_preview_image(
    video_path: Union[str, Path],
    ass_path: Union[str, Path],
    output_path: Optional[Union[str, Path]] = None,
    timestamp: float = 0.0,
) -> Path:
    """
    Generates a preview image from a video at a given timestamp with ASS subtitles.

    Args:
        video_path (Union[str, Path]): Path to the video file.
        ass_path (Union[str, Path]): Path to the ASS subtitle file.
        output_path (Optional[Union[str, Path]]): Optional path for saving the image.
        timestamp (float): Time (in seconds) from which to capture the frame.

    Returns:
        Path: Absolute path to the preview image.
    """
    try:
        output_path = Path(output_path) if output_path else Path(TEMP_DIR) / f"{uuid.uuid4()}_preview.jpg"

        video_path = Path(video_path)
        ass_path = Path(ass_path)

        cmd = [
            "ffmpeg",
            "-y",
            "-ss",
            str(timestamp),
            "-i",
            _adjust_path(video_path),
            "-vf",
            f"ass={_adjust_path(ass_path)}",
            "-vframes",
            "1",
            "-q:v",
            "2",
            _adjust_path(output_path),
        ]
        logger.info(f"Generating preview image with command: {' '.join(cmd)}")
        subprocess.run(cmd, check=True, cwd=TEMP_DIR)
        return output_path.resolve()
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to generate preview image: {e}")
        raise RuntimeError(f"FFmpeg preview image generation failed: {e}") from e


def get_video_duration(video_path: Union[str, Path]) -> float:
    """
    Retrieves the duration of a video file using ffmpeg.

    Args:
        video_path (Union[str, Path]): Path to the video file.

    Returns:
        float: Duration of the video in seconds.

    Raises:
        RuntimeError: If ffmpeg fails to retrieve the video duration.
    """
    try:
        video_path = Path(video_path)
        cmd = [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "json",
            _adjust_path(video_path),
        ]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            cwd=TEMP_DIR,
        )
        duration_info = json.loads(result.stdout)
        return float(duration_info["format"]["duration"])
    except (subprocess.CalledProcessError, KeyError, ValueError) as e:
        logger.error(f"Failed to retrieve video duration: {e}")
        raise RuntimeError(f"Failed to retrieve video duration: {e}") from e


def _adjust_path(path: Union[str, Path], cwd: Union[str, Path] = TEMP_DIR) -> str:
    """
    Adjusts the provided path relative to the given `cwd` directory and normalizes path separators.

    Args:
        path (Union[str, Path]): Input file path that needs to be adjusted.
        cwd (Union[str, Path]): The current working directory (defaults to TEMP_DIR).

    Returns:
        str: The path relative to `cwd`, with normalized forward slashes.

    """
    path = Path(path).resolve()
    cwd = Path(cwd).resolve()
    relative_path = os.path.relpath(path, cwd)
    return relative_path.replace("\\", "/")
