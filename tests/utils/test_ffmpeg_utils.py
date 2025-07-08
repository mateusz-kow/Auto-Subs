import subprocess

import pytest

from src.utils.ffmpeg_utils import _adjust_path, get_video_duration, get_video_with_subtitles


def test_adjust_path_for_ffmpeg():
    """Test that paths are correctly formatted for the ffmpeg command line."""
    # On Windows, this would be C:\... and should be converted
    test_path = "/path/to/my file.mp4"
    # Assuming the CWD for the command is TEMP_DIR, it should become relative
    # For this test, we can simplify and assume cwd is `/path/to`
    adjusted = _adjust_path(test_path, cwd="/path/to")
    assert adjusted == "my file.mp4"

    # Test backslash replacement
    win_path = "C:\\Users\\Test\\video.mp4"
    adjusted_win = _adjust_path(win_path, cwd="C:\\Users\\Test")
    assert adjusted_win == "video.mp4"


def test_get_video_with_subtitles(mocker):
    """Test that the ffmpeg command for burning subtitles is constructed correctly."""
    mock_run = mocker.patch("subprocess.run")
    video_in = "input.mp4"
    subs_in = "subs.ass"
    video_out = "output.mp4"

    get_video_with_subtitles(video_in, subs_in, video_out)

    mock_run.assert_called_once()
    args, kwargs = mock_run.call_args
    cmd_list = args[0]

    assert "ffmpeg" in cmd_list
    assert "-i" in cmd_list
    assert _adjust_path(video_in) in cmd_list
    assert f"ass={_adjust_path(subs_in)}" in cmd_list[cmd_list.index("-vf") + 1]
    assert _adjust_path(video_out) in cmd_list


def test_get_video_duration(mocker):
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


def test_get_video_duration_raises_error(mocker):
    """Test that a RuntimeError is raised if ffprobe fails."""
    mocker.patch(
        "subprocess.run",
        side_effect=subprocess.CalledProcessError(1, "cmd"),
    )

    with pytest.raises(RuntimeError, match="Failed to retrieve video duration"):
        get_video_duration("non_existent_video.mp4")
