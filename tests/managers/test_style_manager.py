# tests/managers/test_style_manager.py
import json
from pathlib import Path
from unittest.mock import Mock

import pytest
from pytest_mock import MockerFixture

from src.config import DEFAULT_STYLE
from src.managers.style_manager import StyleManager
from src.utils.QThrottler import QThrottler


@pytest.fixture
def style_manager(mocker: MockerFixture) -> StyleManager:
    """
    Fixture to provide a StyleManager instance where the QThrottler
    is mocked to execute immediately (synchronously).
    """
    mocker.patch.object(QThrottler, "call", side_effect=lambda func, *args, **kwargs: func(*args, **kwargs))
    return StyleManager()


def test_initialization(style_manager: StyleManager) -> None:
    """Test that the StyleManager initializes with the default style."""
    assert style_manager.style == DEFAULT_STYLE


def test_from_dict_updates_style_and_notifies(style_manager: StyleManager, mocker: MockerFixture) -> None:
    """Test that updating from a dictionary changes the style and calls listeners."""
    mock_listener_obj = Mock(spec=["on_style_changed"])
    style_manager.register_listener(mock_listener_obj)

    new_style_changes = {"font_size": 50, "primary_color": "&H0000FF00"}
    style_manager.from_dict(new_style_changes)

    assert style_manager.style["font_size"] == 50
    assert style_manager.style["primary_color"] == "&H0000FF00"
    mock_listener_obj.on_style_changed.assert_called_once_with(style_manager.style)


def test_from_dict_does_not_notify_on_same_style(style_manager: StyleManager, mocker: MockerFixture) -> None:
    """Test that listeners are not called if the style is identical."""
    mock_listener_obj = Mock(spec=["on_style_changed"])
    style_manager.register_listener(mock_listener_obj)

    style_manager.from_dict(style_manager.style.copy())

    mock_listener_obj.on_style_changed.assert_not_called()


def test_reset_to_default(style_manager: StyleManager, mocker: MockerFixture) -> None:
    """Test resetting the style to its default values."""
    mock_listener_obj = Mock(spec=["on_style_changed", "on_style_loaded"])
    style_manager.register_listener(mock_listener_obj)

    style_manager.from_dict({"font_size": 99})
    assert style_manager.style["font_size"] == 99
    mock_listener_obj.on_style_changed.assert_called_once()
    mock_listener_obj.on_style_loaded.assert_not_called()

    style_manager.reset_to_default()
    assert style_manager.style == DEFAULT_STYLE
    assert mock_listener_obj.on_style_changed.call_count == 2
    mock_listener_obj.on_style_loaded.assert_called_once()


def test_save_and_load_style(style_manager: StyleManager, tmp_path: Path, mocker: MockerFixture) -> None:
    """Test that a style can be saved to a file and loaded back correctly."""
    mock_listener_obj = Mock(spec=["on_style_changed", "on_style_loaded"])
    style_manager.register_listener(mock_listener_obj)

    # 1. Modify the style
    modified_style = style_manager.style.copy()
    modified_style["font"] = "Test Font"
    modified_style["shadow"] = 5
    style_manager.from_dict(modified_style)

    # 2. Save the style to a temporary file
    file_path = tmp_path / "test_style.json"
    style_manager.save_to_file(file_path)
    assert file_path.exists()

    # 3. Reset the manager to default
    style_manager.reset_to_default()
    assert style_manager.style["font"] != "Test Font"

    # 4. Load the style from the file
    style_manager.load_from_file(file_path)

    # 5. Assert the style is restored
    assert style_manager.style["font"] == "Test Font"
    assert style_manager.style["shadow"] == 5
    # mock_listener_obj.on_style_loaded.assert_called_once()


def test_load_merges_with_default(style_manager: StyleManager, tmp_path: Path) -> None:
    """Test that loading a partial style file correctly merges with default values."""
    partial_style = {"font": "PartialFont", "font_size": 123}
    file_path = tmp_path / "partial_style.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(partial_style, f)

    style_manager.load_from_file(file_path)

    # Check that loaded values are present
    assert style_manager.style["font"] == "PartialFont"
    assert style_manager.style["font_size"] == 123
    # Check that a default value is still there
    assert style_manager.style["alignment"] == DEFAULT_STYLE["alignment"]
