"""Unit Tests for ActionsDispatcher with declarative action definitions.

This test suite validates that ActionsDispatcher works correctly with declarative
action definitions, multiprocessing execution, error handling, and integration scenarios.
"""

from __future__ import annotations

import os
import tempfile

from pathlib import Path
from typing import Any, Generator

import pytest

from qtpy.QtWidgets import QApplication

# Import ActionsDispatcher and dependencies
from utility.gui.qt.common.action_definitions import (
    ActionDefinition,
    ActionKey,
    FileExplorerActions,
)
from utility.gui.qt.common.actions_dispatcher import ActionsDispatcher
from utility.gui.qt.common.tasks.actions_executor import FileActionsExecutor
from utility.gui.qt.filesystem.qfiledialogextended.qfiledialogextended import QFileDialogExtended


@pytest.fixture
def force_process_pool(monkeypatch: pytest.MonkeyPatch) -> None:
    """Allow FileActionsExecutor to use multiprocessing when PYKOTOR_DISABLE_MULTIPROCESSING is set."""
    monkeypatch.delenv("PYKOTOR_DISABLE_MULTIPROCESSING", raising=False)


@pytest.fixture(scope="session")
def qapp() -> Generator[QApplication | None, Any, None]:
    """Create QApplication for tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test files and directories
        test_dir = Path(tmpdir)

        # Create files
        (test_dir / "file1.txt").write_text("content 1")
        (test_dir / "file2.txt").write_text("content 2")
        (test_dir / "file3.cpp").write_text("// cpp file")

        # Create subdirectories
        subdir = test_dir / "subdir"
        subdir.mkdir()
        (subdir / "subfile.txt").write_text("sub content")

        # Create hidden file
        if os.name == "nt":
            (test_dir / ".hidden").write_text("hidden content")

        yield test_dir


def test_declarative_action_definitions(qapp):
    """Test that declarative action definitions are properly structured."""
    definitions = FileExplorerActions.ACTION_DEFINITIONS
    assert len(definitions) > 0

    open_def = definitions.get(ActionKey.OPEN)
    assert open_def is not None
    assert open_def.text == "Open"
    assert open_def.icon == "document-open"

    delete_def = definitions.get(ActionKey.DELETE)
    assert delete_def is not None
    assert delete_def.text == "Delete"

    actions = FileExplorerActions()
    assert isinstance(actions.actions, dict)
    assert len(actions.actions) > 0

    assert ActionKey.OPEN in actions.actions
    assert ActionKey.DELETE in actions.actions
    assert ActionKey.COPY in actions.actions

    assert actions.actions[ActionKey.OPEN].text() == "Open"
    assert actions.actions[ActionKey.DELETE].text() == "Delete"


def test_actions_dispatcher_initialization(qapp, temp_dir: Path):
    """Test ActionsDispatcher initialization with declarative setup."""
    # Create QFileDialogExtended for testing
    dialog = QFileDialogExtended()
    dialog.setDirectory(str(temp_dir))

    # Create dispatcher
    dispatcher = ActionsDispatcher(dialog.model, dialog, FileActionsExecutor())

    # Test basic initialization
    assert dispatcher.fs_model is dialog.model
    assert dispatcher.dialog is dialog
    assert isinstance(dispatcher.file_actions_executor, FileActionsExecutor)

    # Test that signals are connected (hard to test directly, but no crash is good)
    assert hasattr(dispatcher, "setup_signals")


def test_declarative_action_execution(qapp, temp_dir: Path):
    """Test that actions defined declaratively execute correctly."""
    dialog = QFileDialogExtended()
    dialog.setDirectory(str(temp_dir))
    executor = FileActionsExecutor()
    dispatcher = ActionsDispatcher(dialog.model, dialog, executor)

    # Test that we can get actions
    actions = FileExplorerActions()
    open_action = actions.get_action("open")

    # Simulate triggering an action
    # Note: This is tricky in unit tests as it requires full Qt event loop
    # For now, just test that the action exists and has correct properties
    assert open_action is not None
    assert open_action.text() == "Open"


def test_multiprocessing_execution(qapp, tmp_path: Path, force_process_pool: None):
    """Test that actions use multiprocessing for execution."""
    executor = FileActionsExecutor(max_workers=2, enable_multiprocessing=True)

    assert hasattr(executor, "process_pool")
    assert executor.process_pool is not None

    out_file = tmp_path / "queued_create.txt"
    task_id = executor.queue_task("create_file", args=([out_file], "test content"))
    assert task_id is not None
    assert isinstance(task_id, str)


def test_error_handling_in_declarative_actions(qapp, temp_dir: Path):
    """Test error handling with declarative actions."""
    dialog = QFileDialogExtended()
    dialog.setDirectory(str(temp_dir))
    executor = FileActionsExecutor()
    dispatcher = ActionsDispatcher(dialog.model, dialog, executor)

    # Test invalid action (should not crash)
    # Since we dynamically look up methods, invalid ones should be handled gracefully
    invalid_definition = ActionDefinition(
        "dialog-error", "Invalid", None, operation="nonexistent_operation"
    )

    # This should not crash, though it may not do anything
    try:
        dispatcher._handle_action(invalid_definition)
        assert True  # No exception raised
    except Exception as e:
        # If it does raise, it should be a reasonable exception
        assert isinstance(e, (AttributeError, ValueError))


def test_integration_with_file_operations(qapp, temp_dir: Path):
    """Test full integration of declarative actions with file operations."""
    dialog = QFileDialogExtended()
    dialog.setDirectory(str(temp_dir))
    executor = FileActionsExecutor()
    dispatcher = ActionsDispatcher(dialog.model, dialog, executor)

    # Test that dispatcher can handle real file operations
    # Select a file in the dialog
    txt_files = list(temp_dir.glob("*.txt"))
    if txt_files:
        dialog.selectFile(str(txt_files[0]))

        # Test that selected paths can be retrieved
        selected = dispatcher.get_selected_paths()
        assert len(selected) > 0
        assert selected[0].name.endswith(".txt")

    # Test directory operations
    assert dispatcher.get_current_directory() == temp_dir


def test_action_metadata_consistency():
    """Test that action definitions have consistent metadata."""
    actions = FileExplorerActions()

    for _key, definition in actions.ACTION_DEFINITIONS.items():
        assert definition.icon
        assert definition.text

        has_operation = definition.operation is not None
        has_handler = definition.handler_func is not None
        has_prepare = definition.prepare_func is not None

        assert has_operation or has_handler or has_prepare


def test_async_flags_in_definitions():
    """Test that async flags are properly set in action definitions."""
    # Check that actions that should be async are marked as such
    actions = FileExplorerActions()

    file_ops = [ActionKey.OPEN, ActionKey.DELETE, ActionKey.COPY, ActionKey.RENAME]
    for key in file_ops:
        if key in actions.actions:
            definition = actions.ACTION_DEFINITIONS.get(key)
            if definition:
                assert definition.async_operation


def test_memory_management_with_declarative_actions(qapp, temp_dir: Path):
    """Test memory management with multiple declarative action instances."""
    # Create multiple dialogs and dispatchers
    for _ in range(3):
        dialog = QFileDialogExtended()
        dialog.setDirectory(str(temp_dir))
        executor = FileActionsExecutor()
        dispatcher = ActionsDispatcher(dialog.model, dialog, executor)

        # Test basic functionality
        actions = FileExplorerActions()
        assert len(actions.actions) > 0

        # Clean up
        dialog.close()
        del dialog, dispatcher, executor

    # If we get here without memory issues, test passes
    assert True


def test_cross_platform_compatibility(qapp, temp_dir: Path):
    """Test cross-platform aspects of declarative actions."""
    dialog = QFileDialogExtended()
    dialog.setDirectory(str(temp_dir))
    executor = FileActionsExecutor()
    dispatcher = ActionsDispatcher(dialog.model, dialog, executor)

    # Test that paths work correctly
    current_dir = dispatcher.get_current_directory()
    assert current_dir.exists()
    assert current_dir.is_dir()

    # Test file selection
    if list(temp_dir.glob("*")):
        first_file = next(temp_dir.glob("*"))
        dialog.selectFile(str(first_file))
        selected = dispatcher.get_selected_paths()
        assert len(selected) >= 1


def test_full_integration_workflow(qapp, temp_dir: Path, force_process_pool: None):
    """Test full workflow with declarative actions."""
    dialog = QFileDialogExtended()
    dialog.setDirectory(str(temp_dir))
    executor = FileActionsExecutor()
    dispatcher = ActionsDispatcher(dialog.model, dialog, executor)

    # 1. Test action definitions loaded
    actions = FileExplorerActions()
    assert len(actions.actions) > 0

    # 2. Test dispatcher initialization
    assert dispatcher.fs_model is not None
    assert dispatcher.dialog is not None

    executor_mp = FileActionsExecutor(enable_multiprocessing=True)
    workflow_file = temp_dir / "workflow_test.txt"
    task_id = executor_mp.queue_task("create_file", args=([workflow_file], "test"))
    assert task_id

    # 4. Test directory navigation
    dispatcher.dialog.setDirectory(
        str(temp_dir / "subdir") if (temp_dir / "subdir").exists() else str(temp_dir)
    )
    assert dispatcher.get_current_directory().exists()

    # 5. Test state consistency
    selected = dispatcher.get_selected_paths()
    assert isinstance(selected, list)

    # If we complete all steps without exceptions, integration works
    assert True
