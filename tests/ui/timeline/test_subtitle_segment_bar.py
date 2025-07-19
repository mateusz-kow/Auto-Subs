from pathlib import Path

import pytest
from PySide6.QtCore import QPointF, Qt
from PySide6.QtWidgets import QApplication
from pytest_mock import MockerFixture
from pytestqt.qtbot import QtBot

from src.subtitles.models import Subtitles, SubtitleSegment, SubtitleWord
from src.ui.subtitle_editor_app import SubtitleEditorApp
from src.ui.timeline.constants import TIME_SCALE_FACTOR
from src.ui.timeline.SubtitleSegmentBar import SubtitleSegmentBar


def find_segment_bar(app: SubtitleEditorApp, index: int) -> SubtitleSegmentBar | None:
    """Helper to find a SubtitleSegmentBar in the scene by its index."""
    for item in app.timeline_bar.segments_bar.scene().items():
        if isinstance(item, SubtitleSegmentBar) and item.index == index:
            return item
    return None


@pytest.fixture
def app_with_data(qtbot: QtBot, mocker: MockerFixture, tmp_path: Path) -> SubtitleEditorApp:
    """Fixture to provide a fully initialized app with video and subtitles loaded."""
    mocker.patch("src.managers.VideoManager.get_video_duration", return_value=10.0)
    mocker.patch("src.managers.TranscriptionManager.TranscriptionManager._load_model")
    mocker.patch("src.ui.MediaPlayer.MediaPlayer._initialize_mpv", return_value=True)
    mocker.patch("src.ui.SubtitleEditorApp.SubtitleEditorApp._render_subtitles_on_player")

    if not QApplication.instance():
        QApplication([])

    app = SubtitleEditorApp()
    qtbot.addWidget(app)
    app.show()

    video_path = tmp_path / "video.mp4"
    video_path.touch()
    app.video_manager.set_video_path(video_path)

    subtitles = Subtitles(
        [
            SubtitleSegment([SubtitleWord("First", 0.5, 1.5)]),
            SubtitleSegment([SubtitleWord("Second", 2.0, 4.0)]),
        ]
    )
    app.subtitles_manager.set_subtitles(subtitles)
    qtbot.wait_for_window_shown(app)

    qtbot.waitUntil(lambda: find_segment_bar(app, 1) is not None, timeout=1000)

    return app


def test_segment_resizing_integration(app_with_data: SubtitleEditorApp, qtbot: QtBot, mocker: MockerFixture) -> None:
    """Perform a full integration test of resizing a segment via UI events."""
    app = app_with_data
    segments_bar = app.timeline_bar.segments_bar
    segment_index = 1
    segment_item = find_segment_bar(app, segment_index)
    assert segment_item is not None

    # Spy on the manager's method
    resize_spy = mocker.spy(app.subtitles_manager, "resize_segment")

    # --- Simulate Drag ---
    # 1. Press on the right handle
    original_rect = segment_item.rect()
    start_pos = segment_item.mapToScene(QPointF(original_rect.right() - 1, original_rect.center().y()))
    qtbot.mousePress(
        segments_bar.viewport(),
        Qt.MouseButton.LeftButton,
        Qt.KeyboardModifier.NoModifier,
        segments_bar.mapFromScene(start_pos),
    )  # type: ignore[no-untyped-call]

    # 2. Drag to a new position (shorten the segment)
    new_x_in_seconds = 3.0
    drag_pos = QPointF(new_x_in_seconds * TIME_SCALE_FACTOR, start_pos.y())
    qtbot.mouseMove(segments_bar.viewport(), segments_bar.mapFromScene(drag_pos))  # type: ignore[no-untyped-call]

    # 3. Release the mouse
    qtbot.mouseRelease(
        segments_bar.viewport(),
        Qt.MouseButton.LeftButton,
        Qt.KeyboardModifier.NoModifier,
        segments_bar.mapFromScene(drag_pos),
    )  # type: ignore[no-untyped-call]

    # --- Assertions ---
    # Check that the manager method was called correctly
    resize_spy.assert_called_once()
    args, _ = resize_spy.call_args
    assert args[0] == segment_index  # segment_index
    assert args[1] == pytest.approx(2.0)  # new_start (unchanged)
    assert args[2] == pytest.approx(new_x_in_seconds)  # new_end

    # Check that the data model has been updated
    updated_segment = app.subtitles_manager.subtitles.segments[segment_index]
    assert updated_segment.start == pytest.approx(2.0)
    assert updated_segment.end == pytest.approx(3.0)
