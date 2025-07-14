import subprocess
from pathlib import Path

import pytest
from pytest_mock import MockerFixture

from src.utils.ffmpeg_utils import get_video_duration, get_video_with_subtitles


def test_get_video_with_subtitles(mocker: MockerFixture) -> None:
    """Test that the ffmpeg command for burning subtitles is constructed correctly."""
    mock_run = mocker.patch("subprocess.run")
    video_in = Path("input.mp4")
    subs_in = Path("subs.ass")
    video_out = Path("output.mp4")

    get_video_with_subtitles(video_in, subs_in, video_out)

    mock_run.assert_called_once()
    args, kwargs = mock_run.call_args
    cmd_list = args[0]

    assert "ffmpeg" in cmd_list
    assert "-i" in cmd_list


def test_get_video_duration(mocker: MockerFixture) -> None:
    """Test that video duration is correctly parsed from ffprobe output."""
    json_output = '{"format": {"duration": "123.45"}}'
    mock_run = mocker.patch("subprocess.run")
    # Configure the mock to return a completed process with the sample JSON output
    mock_run.return_value = subprocess.CompletedProcess(args=[], returncode=0, stdout=json_output, stderr="")

    duration = get_video_duration("fake_video.mp4")

    assert duration == 123.45
    mock_run.assert_called_once()
    cmd_list = mock_run.call_args[0][0]
    assert "ffprobe" in cmd_list
    assert "format=duration" in cmd_list


def test_get_video_duration_raises_error(mocker: MockerFixture) -> None:
    """Test that a RuntimeError is raised if ffprobe fails."""
    mocker.patch(
        "subprocess.run",
        side_effect=subprocess.CalledProcessError(1, "cmd"),
    )

    with pytest.raises(RuntimeError, match="Failed to retrieve video duration"):
        get_video_duration("non_existent_video.mp4")
