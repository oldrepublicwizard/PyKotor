"""Reusable standalone installation/folder-path toolbar for editor windows."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Callable, ClassVar

from qtpy.QtCore import Signal  # pyright: ignore[reportPrivateImportUsage]
from qtpy.QtWidgets import (
    QButtonGroup,
    QComboBox,
    QDialog,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
    QWidget,
)

from loggerplus import RobustLogger
from toolset.data.installation import HTInstallation
from toolset.gui.dialogs.asyncloader import AsyncLoader
from toolset.gui.widgets.settings.installations import GlobalSettings, InstallationsWidget
from toolset.uic.qtpy.widgets.installation_toolbar import Ui_Form

if TYPE_CHECKING:
    pass


@dataclass(frozen=True)
class FolderPathSpec:
    key: str
    label: str
    tooltip: str
    required: bool = False


def open_manage_installations_dialog(
    parent: QWidget,
    *,
    on_save: Callable[[], None] | None = None,
) -> None:
    """Open the shared Manage Installations dialog. Call on_save after user accepts."""
    from toolset.uic.qtpy.dialogs.manage_installations import Ui_Dialog

    dialog = QDialog(parent)
    dialog.setWindowTitle("Manage Installations")
    ui = Ui_Dialog()
    ui.setupUi(dialog)
    widget = InstallationsWidget(ui.installationsWidgetPlaceholder)
    layout = QVBoxLayout(ui.installationsWidgetPlaceholder)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.addWidget(widget)
    ui.buttonBox.accepted.connect(dialog.accept)
    ui.buttonBox.rejected.connect(dialog.reject)
    if dialog.exec() == QDialog.DialogCode.Accepted:
        widget.save()
        if on_save is not None:
            on_save()


class InstallationToolbar(QWidget, Ui_Form):
    """Reusable installation/folder-path strip; layout from installation_toolbar.ui."""

    installation_changed = Signal(object)  # HTInstallation | None
    folder_paths_changed = Signal(object)  # dict[str, Path | None]

    # Set by setupUi(self) from Ui_Form
    installationCombo: QComboBox
    reloadBtn: QPushButton
    manageBtn: QPushButton
    modeFullRadio: QRadioButton
    modeFolderRadio: QRadioButton
    pathsWidget: QWidget
    pathsLayout: QFormLayout

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        folder_path_specs: list[FolderPathSpec] | None = None,
        requires_installation: bool = False,
    ):
        super().__init__(parent)
        self._log = RobustLogger()
        self._specs: list[FolderPathSpec] = folder_path_specs or []
        self._requires_installation: bool = requires_installation
        self._settings = GlobalSettings()
        self._installation_cache: dict[str, HTInstallation] = {}
        self._override_installation: HTInstallation | None = None
        self._folder_edits: dict[str, QLineEdit] = {}
        self._saved_installations: dict[str, dict[str, str | bool]] = {}
        self._in_update = False

        self.setupUi(self)
        self.mode_group = QButtonGroup(self)
        self.mode_group.addButton(self.modeFullRadio)
        self.mode_group.addButton(self.modeFolderRadio)

        if not self._specs:
            self.modeFullRadio.setChecked(True)
            self.modeFolderRadio.hide()
            self.modeFullRadio.hide()
            self.pathsWidget.hide()
        elif self._requires_installation:
            self.modeFullRadio.setChecked(True)
            self.modeFolderRadio.setEnabled(False)
            self.modeFolderRadio.setToolTip("This window requires a full installation.")
            self.pathsWidget.hide()
        else:
            self.modeFullRadio.setChecked(True)
            self.pathsWidget.hide()

        for spec in self._specs:
            row = QWidget(self.pathsWidget)
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(4)
            edit = QLineEdit(row)
            edit.setPlaceholderText("Optional folder path..." if not spec.required else "Required folder path...")
            edit.setToolTip(spec.tooltip)
            browse = QPushButton("Browse...", row)
            browse.clicked.connect(lambda _=False, key=spec.key: self._browse_for_path(key))
            edit.textChanged.connect(self._emit_current_state)
            row_layout.addWidget(edit, 1)
            row_layout.addWidget(browse)
            self._folder_edits[spec.key] = edit
            self.pathsLayout.addRow(f"{spec.label}:", row)

        self.installationCombo.currentIndexChanged.connect(self._on_installation_selection_changed)
        self.reloadBtn.clicked.connect(self.reload_installations)
        self.manageBtn.clicked.connect(self._open_installations_settings)
        self.mode_group.buttonToggled.connect(self._on_mode_changed)

        self.reload_installations()
        self._emit_current_state()

    @property
    def installation_combo(self):
        """Backward-compatible alias for installationCombo (e.g. indoor_builder sync)."""
        return self.installationCombo

    def set_override_installation(self, installation: HTInstallation | None) -> None:
        """Set an installation passed from CLI (e.g. --game-path). Shows in combo and emits so the window uses it."""
        self._override_installation = installation
        self.reload_installations()
        if installation is not None:
            self._installation_cache["__override__"] = installation
        # reload_installations() already called _emit_current_state(), which emits the selected installation

    def reload_installations(self) -> None:
        current_key = self.installationCombo.currentData()
        self._saved_installations = {name: {"path": config.path, "tsl": config.tsl, "name": name} for name, config in self._settings.installations().items()}
        self._in_update = True
        try:
            self.installationCombo.clear()
            if self._override_installation is not None:
                path_str = str(self._override_installation.path())
                self.installationCombo.addItem(f"Current: {path_str}", "__override__")
                self._installation_cache["__override__"] = self._override_installation
            self.installationCombo.addItem("(None)", None)
            for name, config in sorted(self._saved_installations.items()):
                self.installationCombo.addItem(f"{name} ({config['path']})", name)
            if current_key is not None:
                idx = self.installationCombo.findData(current_key)
                if idx >= 0:
                    self.installationCombo.setCurrentIndex(idx)
            elif self._override_installation is not None:
                self.installationCombo.setCurrentIndex(0)
        finally:
            self._in_update = False
        self._emit_current_state()

    def _browse_for_path(self, key: str) -> None:
        directory = QFileDialog.getExistingDirectory(self, "Select Folder")
        if directory:
            self._folder_edits[key].setText(directory)

    def _open_installations_settings(self) -> None:
        open_manage_installations_dialog(self, on_save=self.reload_installations)

    def _on_installation_selection_changed(self, _index: int) -> None:
        if self._in_update:
            return
        use_paths = self.modeFolderRadio.isChecked() and bool(self._specs) and not self._requires_installation
        if use_paths:
            self._emit_current_state()
            return
        selected_name = self.installationCombo.currentData()
        if selected_name == "__override__":
            self.installation_changed.emit(self._installation_cache.get("__override__"))
            self.folder_paths_changed.emit({})
            return
        if selected_name is None:
            self.installation_changed.emit(None)
            self.folder_paths_changed.emit({})
            return
        cache_key = str(selected_name)
        if cache_key in self._installation_cache:
            self.installation_changed.emit(self._installation_cache[cache_key])
            self.folder_paths_changed.emit({})
            return
        config = self._saved_installations.get(cache_key)
        if config is None:
            self.installation_changed.emit(None)
            self.folder_paths_changed.emit({})
            return
        # Cache miss: load installation in background and show AsyncLoader
        parent_window = self.window()
        if parent_window is None:
            parent_window = self

        def task() -> HTInstallation | None:
            try:
                inst = HTInstallation(
                    str(config["path"]),
                    str(config["name"]),
                    tsl=bool(config.get("tsl")),
                )
                return inst
            except Exception as exc:  # noqa: BLE001
                self._log.exception("Failed to create installation '%s': %s", cache_key, exc)
                raise

        loader = AsyncLoader(
            parent_window,
            "Loading installation...",
            task,
            error_title="Invalid Installation",
            start_immediately=True,
            initial_message="Loading installation... Please wait.",
        )

        def on_finish(inst: HTInstallation | None) -> None:
            if inst is not None:
                self._installation_cache[cache_key] = inst
            self.installation_changed.emit(inst)
            self.folder_paths_changed.emit({})

        loader.optional_finish_hook.connect(on_finish)
        prev_index = self.installationCombo.currentIndex()
        loader.exec()
        if loader.dialog_result_code() != QDialog.DialogCode.Accepted:
            self._in_update = True
            try:
                self.installationCombo.setCurrentIndex(prev_index)
            finally:
                self._in_update = False
            self.installation_changed.emit(self._get_selected_installation())
            self.folder_paths_changed.emit({})

    def _on_mode_changed(self, _button, checked: bool) -> None:
        if not checked:
            return
        use_paths = self.modeFolderRadio.isChecked() and bool(self._specs) and not self._requires_installation
        self.pathsWidget.setVisible(use_paths)
        self._emit_current_state()

    def _get_selected_installation(self) -> HTInstallation | None:
        selected_name = self.installationCombo.currentData()
        if selected_name is None:
            return None
        if selected_name == "__override__":
            return self._installation_cache.get("__override__")

        cache_key = str(selected_name)
        if cache_key in self._installation_cache:
            return self._installation_cache[cache_key]

        config = self._saved_installations.get(cache_key)
        if config is None:
            return None
        try:
            installation = HTInstallation(
                str(config["path"]),
                str(config["name"]),
                tsl=bool(config.get("tsl")),
            )
            self._installation_cache[cache_key] = installation
            return installation
        except Exception as exc:  # noqa: BLE001
            self._log.exception("Failed to create installation '%s': %s", cache_key, exc)
            QMessageBox.warning(self, "Invalid Installation", f"Could not load installation '{cache_key}'.")
            return None

    def get_folder_paths(self) -> dict[str, Path | None]:
        result: dict[str, Path | None] = {}
        for spec in self._specs:
            raw = self._folder_edits[spec.key].text().strip()
            result[spec.key] = Path(raw) if raw else None
        return result

    def _emit_current_state(self) -> None:
        use_paths = self.modeFolderRadio.isChecked() and bool(self._specs) and not self._requires_installation
        selected_installation = None if use_paths else self._get_selected_installation()
        self.installation_changed.emit(selected_installation)
        self.folder_paths_changed.emit(self.get_folder_paths() if use_paths else {})


class StandaloneWindowMixin:
    STANDALONE_FOLDER_PATHS: ClassVar[list[FolderPathSpec]] = []
    STANDALONE_REQUIRES_INSTALLATION: ClassVar[bool] = False

    _installation_toolbar: InstallationToolbar | None = None
    _standalone_folder_paths: dict[str, Path | None]

    def enable_standalone_mode(self) -> None:
        if self._installation_toolbar is not None:
            return
        if not hasattr(self, "centralWidget"):
            return
        main_window = self
        if not isinstance(main_window, QWidget):  # runtime safety for pyright/mixin
            return
        central = getattr(main_window, "centralWidget")()
        if central is None:
            return

        self._standalone_folder_paths = {}
        self._installation_toolbar = InstallationToolbar(
            main_window,
            folder_path_specs=list(self.STANDALONE_FOLDER_PATHS),
            requires_installation=self.STANDALONE_REQUIRES_INSTALLATION,
        )
        self._installation_toolbar.installation_changed.connect(self._handle_installation_changed)
        self._installation_toolbar.folder_paths_changed.connect(self._handle_folder_paths_changed)

        container = QWidget(main_window)
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._installation_toolbar)
        layout.addWidget(central, 1)
        getattr(main_window, "setCentralWidget")(container)

    def set_installation(self, installation: HTInstallation | None) -> None:
        setattr(self, "_installation", installation)
        self._on_installation_changed(installation)

    def _handle_installation_changed(self, installation: HTInstallation | None) -> None:
        setattr(self, "_installation", installation)
        self._on_installation_changed(installation)

    def _handle_folder_paths_changed(self, paths: dict[str, Path | None]) -> None:
        self._standalone_folder_paths = paths
        self._on_folder_paths_changed(paths)

    def _on_installation_changed(self, installation: HTInstallation | None) -> None:  # noqa: ARG002
        """Override in subclasses that need runtime installation switching."""

    def _on_folder_paths_changed(self, paths: dict[str, Path | None]) -> None:  # noqa: ARG002
        """Override in subclasses that support folder-path mode."""
