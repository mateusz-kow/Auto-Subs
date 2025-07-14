import json
from pathlib import Path

import pytest
from pytest_mock import MockerFixture

from src.managers.StyleManager import DEFAULT_STYLE, StyleManager
from src.utils.QThrottler import QThrottler


@pytest.fixture
def style_manager(mocker: MockerFixture) -> StyleManager:
    """
    Fixture to provide a StyleManager instance where the QThrottler
    is mocked to execute immediately (synchronously).
    """
    # Mock QThrottler to bypass its timing logic for tests.
    # Its `call` method will now immediately execute the given function.
    mocker.patch.object(QThrottler, "call", side_effect=lambda func, *args, **kwargs: func(*args, **kwargs))
    return StyleManager()


def test_initialization(style_manager: StyleManager) -> None:
    """Test that the StyleManager initializes with the default style."""
    assert style_manager.style == DEFAULT_STYLE


def test_from_dict_updates_style_and_notifies(style_manager: StyleManager, mocker: MockerFixture) -> None:
    """Test that updating from a dictionary changes the style and calls listeners."""
    # We need a fresh mock for the listener itself in each test
    mock_listener = mocker.MagicMock()
    style_manager.add_style_listener(mock_listener)

    new_style_changes = {"font_size": 50, "primary_color": "&H0000FF00"}
    style_manager.from_dict(new_style_changes)

    assert style_manager.style["font_size"] == 50
    assert style_manager.style["primary_color"] == "&H0000FF00"
    mock_listener.assert_called_once()


def test_from_dict_does_not_notify_on_same_style(style_manager: StyleManager, mocker: MockerFixture) -> None:
    """Test that listeners are not called if the style is identical."""
    mock_listener = mocker.MagicMock()
    style_manager.add_style_listener(mock_listener)

    # Call with a copy of the current style
    style_manager.from_dict(style_manager.style.copy())

    mock_listener.assert_not_called()


def test_reset_to_default(style_manager: StyleManager, mocker: MockerFixture) -> None:
    """Test resetting the style to its default values."""
    mock_listener = mocker.MagicMock()
    style_manager.add_style_listener(mock_listener)

    # First, change the style
    style_manager.from_dict({"font_size": 99})
    assert style_manager.style["font_size"] == 99
    mock_listener.assert_called_once()  # Called from the change

    # Now, reset it
    style_manager.reset_to_default()
    assert style_manager.style == DEFAULT_STYLE
    # With the mocked QThrottler, this call is now immediate
    assert mock_listener.call_count == 2  # Called again from the reset


def test_save_and_load_style(style_manager: StyleManager, tmp_path: Path, mocker: MockerFixture) -> None:
    """Test that a style can be saved to a file and loaded back correctly."""
    mock_loaded_listener = mocker.MagicMock()
    style_manager.add_style_loaded_listener(mock_loaded_listener)

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
    mock_loaded_listener.assert_called_once()


def test_load_merges_with_default(style_manager: StyleManager, tmp_path: Path) -> None:
    """Test that loading a partial style file correctly merges with default values."""
    partial_style = {"font": "PartialFont", "font_size": 123}
    file_path = tmp_path / "partial_style.json"
    with open(file_path, "w") as f:
        json.dump(partial_style, f)

    style_manager.load_from_file(file_path)

    # Check that loaded values are present
    assert style_manager.style["font"] == "PartialFont"
    assert style_manager.style["font_size"] == 123
    # Check that a default value is still there
    assert style_manager.style["alignment"] == DEFAULT_STYLE["alignment"]
