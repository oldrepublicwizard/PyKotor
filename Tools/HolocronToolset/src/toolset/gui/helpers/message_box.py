"""Common QMessageBox helper functions for consistent UI messaging."""

from __future__ import annotations

from typing import TYPE_CHECKING

from qtpy.QtWidgets import QMessageBox

if TYPE_CHECKING:
    from qtpy.QtWidgets import QWidget


def show_info_message(
    title: str,
    text: str,
    parent: QWidget | None = None,
) -> None:
    """Show an informational message box."""
    QMessageBox(
        QMessageBox.Icon.Information,
        title,
        text,
        QMessageBox.StandardButton.Ok,
        parent,
    ).exec()


def show_warning_message(
    title: str,
    text: str,
    parent: QWidget | None = None,
) -> None:
    """Show a warning message box."""
    QMessageBox(
        QMessageBox.Icon.Warning,
        title,
        text,
        QMessageBox.StandardButton.Ok,
        parent,
    ).exec()


def show_error_message(
    title: str,
    text: str,
    parent: QWidget | None = None,
) -> None:
    """Show an error message box."""
    QMessageBox(
        QMessageBox.Icon.Critical,
        title,
        text,
        QMessageBox.StandardButton.Ok,
        parent,
    ).exec()