"""Tests for actions_executor with strict type checking.

Tests verify that dynamic FileOperations attribute access works correctly.
"""

from __future__ import annotations

import pathlib
import sys
import tempfile
from multiprocessing import Queue

# Setup paths
THIS_FILE = pathlib.Path(__file__).resolve()
REPO_ROOT = THIS_FILE.parents[5]
PYKOTOR_SRC = REPO_ROOT / "Libraries" / "PyKotor" / "src"
UTILITY_SRC = REPO_ROOT / "Libraries" / "Utility" / "src"

for path in (PYKOTOR_SRC, UTILITY_SRC):
    as_posix = path.as_posix()
    if as_posix not in sys.path:
        sys.path.insert(0, as_posix)


from utility.gui.qt.common.expensive_functions import FileOperations
from utility.gui.qt.common.tasks.actions_executor import FileActionsExecutor


class TestActionsExecutorStrictTyping:
    """Test FileActionsExecutor with strict type checking (getattr for dynamic lookup)."""

    def test_execute_task_with_existing_operation(self):
        """Test that existing FileOperations methods are accessed via getattr."""
        progress_queue: Queue = Queue()

        class _Ctl:
            value = False

        pause_flag = _Ctl()
        cancel_flag = _Ctl()
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / "test.txt"
            result = FileActionsExecutor._execute_task(
                "create_file",
                None,
                [path],
                "content",
                progress_queue=progress_queue,
                pause_flag=pause_flag,
                cancel_flag=cancel_flag,
            )
            assert path.read_text() == "content"
            assert result is not None

    def test_execute_task_with_nonexistent_operation(self):
        """Test that nonexistent operations return None gracefully."""
        result = FileActionsExecutor._execute_task("nonexistent_operation_xyz", None)

        # Should return None when operation doesn't exist
        assert result is None

    def test_file_operations_has_attributes(self):
        """Test that FileOperations class has operation attributes."""
        # Verify FileOperations has some expected attributes
        # This is a legitimate use of getattr for dynamic lookup
        assert hasattr(FileOperations, "create_file") or hasattr(FileOperations, "read_file")

    def test_execute_task_uses_getattr_not_object_getattribute(self):
        """Test that _execute_task uses getattr (not object.__getattribute__)."""
        # This test verifies the implementation uses getattr
        # We can't directly test the implementation, but we can verify behavior
        result = FileActionsExecutor._execute_task("invalid_op_12345", None)

        # Should handle gracefully (return None) using getattr with default
        assert result is None
