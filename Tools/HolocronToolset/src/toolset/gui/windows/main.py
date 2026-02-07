"""Professional SDK-style main window for Holocron Toolset.

Designed to match industry-standard game development toolsets like Unity, UE5, and Stride.
Features a three-panel layout: Project Browser | Asset Viewer | Inspector.
"""

from __future__ import annotations

import os
import sys

from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, cast

import qtpy

from qtpy import QtCore, QtWidgets
from qtpy.QtCore import QFileSystemWatcher, QModelIndex, QObject, QPoint, QCoreApplication, QSortFilterProxyModel, QTimer, Qt, Signal, Slot
from qtpy.QtGui import (
    QCloseEvent,
    QDragEnterEvent,
    QDropEvent,
    QKeyEvent,
    QMouseEvent,
    QPalette,
    QPixmap,
    QShowEvent,
)
from qtpy.QtWidgets import (
    QAbstractItemView,
    QAction,
    QApplication,
    QButtonGroup,
    QFileDialog,
    QHeaderView,
    QMainWindow,
    QMessageBox,
    QStyle,
)

from pykotor.extract.file import FileResource
from pykotor.resource.type import ResourceType
from toolset.data.installation import HTInstallation
from toolset.gui.common.filters import NoScrollEventFilter
from toolset.gui.common.localization import set_language, translate as tr, translate_format as trf
from toolset.gui.dialogs.async_loader import AsyncLoader
from toolset.gui.dialogs.theme_selector import ThemeSelectorDialog
from toolset.gui.widgets.settings.installations import GlobalSettings
from toolset.gui.widgets.kotor_filesystem_model import (
    CategoryItem,
    DirItem,
    InstallationItem,
    KotorFileSystemModel,
    ResourceItem,
    TreeItem,
)
from toolset.utils.window import open_resource_editor
from utility.gui.qt.widgets.itemviews.listview import RobustListView
from utility.gui.qt.widgets.itemviews.tableview import RobustTableView
from utility.gui.qt.widgets.itemviews.treeview import RobustTreeView
from loggerplus import RobustLogger
from toolset.gui.common.style.theme_manager import ThemeManager
from toolset.gui.windows.update_manager import UpdateManager

if TYPE_CHECKING:
    from toolset.gui.common.localization import ToolsetLanguage


class AssetFilterProxyModel(QSortFilterProxyModel):
    """Proxy model providing advanced search filters for assets."""

    def __init__(self, parent: QObject | None = None):
        super().__init__(parent)
        self._query: str = ""
        self._filters: dict[str, object] = {
            "ext": set(),
            "type": set(),
            "name": "",
            "path": "",
            "tokens": [],
        }

        if hasattr(self, "setRecursiveFilteringEnabled"):
            self.setRecursiveFilteringEnabled(True)

    def set_search(self, text: str) -> None:
        """Set the search query and update filters."""
        self._query = text.strip()
        self._filters = self._parse_query(self._query)
        self.invalidateFilter()

    def _parse_query(self, text: str) -> dict[str, object]:
        filters: dict[str, object] = {
            "ext": set(),
            "type": set(),
            "name": "",
            "path": "",
            "tokens": [],
        }

        if not text:
            return filters

        tokens = text.split()
        for token in tokens:
            if ":" in token:
                key, value = token.split(":", 1)
                key = key.lower().strip()
                value = value.strip()
                if key in {"ext", "type"}:
                    values = {v.strip().lower() for v in value.split(",") if v.strip()}
                    filters[key] = values
                elif key in {"name", "path"}:
                    filters[key] = value.lower()
                else:
                    filters["tokens"].append(token.lower())
            else:
                filters["tokens"].append(token.lower())

        return filters

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:  # noqa: N802
        source_model = self.sourceModel()
        if source_model is None:
            return False

        index = source_model.index(source_row, 0, source_parent)
        if not index.isValid():
            return False

        item = source_model.itemFromIndex(index)
        if item is None:
            return False

        if self._matches_item(item):
            return True

        if source_model.hasChildren(index):
            for i in range(source_model.rowCount(index)):
                if self.filterAcceptsRow(i, index):
                    return True

        return False

    def _matches_item(self, item: TreeItem) -> bool:
        name = str(item.data()).lower() if hasattr(item, "data") else str(item).lower()
        path = str(getattr(item, "path", "")).lower()

        ext_filter = cast(set[str], self._filters.get("ext", set()))
        type_filter = cast(set[str], self._filters.get("type", set()))
        name_filter = cast(str, self._filters.get("name", ""))
        path_filter = cast(str, self._filters.get("path", ""))
        tokens = cast(list[str], self._filters.get("tokens", []))

        ext = ""
        category = ""
        if isinstance(item, ResourceItem):
            ext = item.resource.restype().extension.lower()
            category = str(item.resource.restype().category).lower()

        if ext_filter and ext not in ext_filter:
            return False

        if type_filter and category not in type_filter and ext not in type_filter:
            return False

        if name_filter and name_filter not in name:
            return False

        if path_filter and path_filter not in path:
            return False

        for token in tokens:
            if token not in name and token not in path and token not in ext:
                return False

        return True


class ToolWindow(QMainWindow):
    """Main window for Holocron Toolset - Professional SDK-style interface."""

    # Signals
    sig_installation_changed: Signal = Signal(HTInstallation)
    sig_installations_updated: Signal = Signal(list)

    def __init__(self):
        """Initialize the main window."""
        super().__init__()

        # Core application state
        self.active: HTInstallation | None = None
        self.installations: dict[str, HTInstallation] = {}
        self.settings: GlobalSettings = GlobalSettings()
        self.update_manager: UpdateManager = UpdateManager(silent=True)

        # Theme and styling
        q_style: QStyle | None = self.style()
        assert q_style is not None, "Window style was somehow None"
        self.original_style: str = q_style.objectName()
        self.original_palette: QPalette = self.palette()
        self.theme_manager: ThemeManager = ThemeManager(self.original_style)
        self.theme_manager._apply_theme_and_style(
            self.settings.selectedTheme,
            self.settings.selectedStyle
        )

        # UI state
        self._mouse_move_pos: QPoint | None = None
        self._theme_dialog: ThemeSelectorDialog | None = None
        self._language_actions: dict[int, QAction] = {}

        # File system watcher for auto-detecting changes
        self._file_watcher: QFileSystemWatcher = QFileSystemWatcher(self)
        self._pending_changes: dict[str, list[str]] = {"modules": [], "override": []}
        self._last_watcher_update: datetime = datetime.now(tz=timezone.utc).astimezone()
        self._watcher_debounce_timer: QTimer = QTimer(self)
        self._watcher_debounce_timer.setSingleShot(True)
        self._watcher_debounce_timer.setInterval(500)
        self._watcher_debounce_timer.timeout.connect(self._process_pending_file_changes)

        # Initialize UI
        RobustLogger().debug("Initializing ToolWindow UI...")
        self._initUi()
        self._setup_signals()

        # Load settings and setup
        self.reload_settings()
        self.unset_installation()

    def _initUi(self):
        """Initialize the UI from the compiled .ui file."""
        from toolset.uic.qtpy.windows.main import Ui_MainWindow

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Replace standard views with Robust versions
        self._setup_robust_views()

        # Initialize the file system model
        self.fs_model = KotorFileSystemModel(self)
        self.fs_proxy = AssetFilterProxyModel(self)
        self.fs_proxy.setSourceModel(self.fs_model)
        
        # Connect model signals
        self.fs_model.address_changed.connect(lambda: self._update_breadcrumb(QModelIndex()))

        # Set model to views
        self.ui.projectTree.setModel(self.fs_model)
        self.ui.assetTreeView.setModel(self.fs_proxy)
        self.ui.assetListView.setModel(self.fs_proxy)
        self.ui.assetGridView.setModel(self.fs_proxy)
        self.ui.assetTableView.setModel(self.fs_proxy)

        # Configure project tree
        self._setup_project_tree()

        # Configure view mode buttons
        self._setup_view_mode_buttons()

        # Setup event filter to prevent scroll wheel interaction with controls
        self._no_scroll_filter = NoScrollEventFilter(self)
        self._no_scroll_filter.setup_filter(parent_widget=self)

        # Debug reload support
        if os.getenv("HOLOCRON_DEBUG_RELOAD") is not None:
            debug_action = self.ui.menubar.addAction("Debug Reload")
            if debug_action:
                from toolset.utils.misc import debug_reload_pymodules
                debug_action.triggered.connect(debug_reload_pymodules)

        # Set window icon
        app = cast(QApplication, QApplication.instance())
        self.setWindowIcon(app.windowIcon())

        # Initial panel sizes (25% | 50% | 25%)
        total_width = 1600
        self.ui.mainSplitter.setSizes([
            int(total_width * 0.25),  # Left panel
            int(total_width * 0.50),  # Center panel
            int(total_width * 0.25),  # Right panel
        ])
        
        # Setup status bar
        self._setup_status_bar()

    def _setup_robust_views(self):
        """Replace standard Qt views with Robust versions."""
        # Replace projectTree
        old_tree = self.ui.projectTree
        robust_tree = RobustTreeView(self.ui.leftPanel, use_columns=True)
        self.ui.leftPanelLayout.replaceWidget(old_tree, robust_tree)
        old_tree.deleteLater()
        self.ui.projectTree = robust_tree

        # Replace assetTreeView
        old_asset_tree = self.ui.assetTreeView
        robust_asset_tree = RobustTreeView(self.ui.treeViewPage, use_columns=True)
        self.ui.treeViewLayout.replaceWidget(old_asset_tree, robust_asset_tree)
        old_asset_tree.deleteLater()
        self.ui.assetTreeView = robust_asset_tree

        # Replace assetListView
        old_list = self.ui.assetListView
        robust_list = RobustListView(self.ui.listViewPage)
        self.ui.listViewLayout.replaceWidget(old_list, robust_list)
        old_list.deleteLater()
        self.ui.assetListView = robust_list

        # Replace assetGridView
        old_grid = self.ui.assetGridView
        robust_grid = RobustListView(self.ui.gridViewPage)
        robust_grid.setViewMode(robust_grid.ViewMode.IconMode)
        robust_grid.setIconSize(QtCore.QSize(128, 128))
        robust_grid.setGridSize(QtCore.QSize(140, 140))
        robust_grid.setResizeMode(robust_grid.ResizeMode.Adjust)
        robust_grid.setUniformItemSizes(True)
        self.ui.gridViewLayout.replaceWidget(old_grid, robust_grid)
        old_grid.deleteLater()
        self.ui.assetGridView = robust_grid

        # Replace assetTableView
        old_table = self.ui.assetTableView
        robust_table = RobustTableView(self.ui.tableViewPage)
        self.ui.tableViewLayout.replaceWidget(old_table, robust_table)
        old_table.deleteLater()
        self.ui.assetTableView = robust_table

    def _setup_project_tree(self):
        """Configure the project tree view."""
        header = self.ui.projectTree.header()
        if header is not None:
            header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
            header.setStretchLastSection(True)

        self.ui.projectTree.setUniformRowHeights(True)
        self.ui.projectTree.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.ui.projectTree.setSortingEnabled(True)
        self.ui.projectTree.sortByColumn(0, Qt.SortOrder.AscendingOrder)

        # Hide non-essential columns (keep Name + Path)
        for col in range(2, self.fs_model.columnCount()):
            self.ui.projectTree.setColumnHidden(col, True)

    def _setup_view_mode_buttons(self):
        """Configure view mode toggle buttons."""
        self._view_mode_group = QButtonGroup(self)
        self._view_mode_group.setExclusive(True)
        self._view_mode_group.addButton(self.ui.btnViewTree, 0)
        self._view_mode_group.addButton(self.ui.btnViewList, 1)
        self._view_mode_group.addButton(self.ui.btnViewGrid, 2)
        self._view_mode_group.addButton(self.ui.btnViewTable, 3)

        def set_view(index: int):
            self.ui.viewStack.setCurrentIndex(index)
            self._sync_asset_views()

        self.ui.btnViewTree.clicked.connect(lambda *args: set_view(0))
        self.ui.btnViewList.clicked.connect(lambda *args: set_view(1))
        self.ui.btnViewGrid.clicked.connect(lambda *args: set_view(2))
        self.ui.btnViewTable.clicked.connect(lambda *args: set_view(3))

        # Default to tree view
        self.ui.viewStack.setCurrentIndex(0)

    def _setup_signals(self):
        """Set up all signal connections."""
        self._setup_project_tree_signals()
        self._setup_asset_view_signals()
        self._setup_action_button_signals()
        self._setup_menu_signals()
        self._setup_toolbar_signals()
        self._setup_keyboard_shortcuts()
        self._setup_context_menus()

    def _setup_project_tree_signals(self):
        """Set up project tree signals."""
        selection_model = self.ui.projectTree.selectionModel()
        if selection_model is not None:
            selection_model.currentChanged.connect(self._on_project_selection_changed)

        self.ui.projectTree.doubleClicked.connect(self._on_project_item_activated)
        self.ui.projectTree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.ui.projectTree.customContextMenuRequested.connect(self._show_project_context_menu)

    def _setup_asset_view_signals(self):
        """Set up asset view signals."""
        self.ui.assetTreeView.doubleClicked.connect(self._on_asset_item_activated)
        self.ui.assetListView.doubleClicked.connect(self._on_asset_item_activated)
        self.ui.assetGridView.doubleClicked.connect(self._on_asset_item_activated)
        self.ui.assetTableView.doubleClicked.connect(self._on_asset_item_activated)

        # Sync selection changes from all asset views
        tree_selection = self.ui.assetTreeView.selectionModel()
        if tree_selection is not None:
            tree_selection.currentChanged.connect(self._sync_asset_views)
            tree_selection.currentChanged.connect(self._update_inspector_panel)
            tree_selection.selectionChanged.connect(lambda: self._update_status_bar())
        
        list_selection = self.ui.assetListView.selectionModel()
        if list_selection is not None:
            list_selection.currentChanged.connect(self._update_inspector_panel)
            list_selection.selectionChanged.connect(lambda: self._update_status_bar())
        
        grid_selection = self.ui.assetGridView.selectionModel()
        if grid_selection is not None:
            grid_selection.currentChanged.connect(self._update_inspector_panel)
            grid_selection.selectionChanged.connect(lambda: self._update_status_bar())
        
        table_selection = self.ui.assetTableView.selectionModel()
        if table_selection is not None:
            table_selection.currentChanged.connect(self._update_inspector_panel)
            table_selection.selectionChanged.connect(lambda: self._update_status_bar())
        
        # Setup context menus for asset views
        for view in [self.ui.assetTreeView, self.ui.assetListView, self.ui.assetGridView, self.ui.assetTableView]:
            view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            view.customContextMenuRequested.connect(self._show_asset_context_menu)
            view.setAcceptDrops(True)
            view.setDragEnabled(True)
            view.setDropIndicatorShown(True)
            view.setDragDropMode(QAbstractItemView.DragDropMode.DropOnly)
            view.installEventFilter(self)
            view.viewport().installEventFilter(self)

    def _setup_action_button_signals(self):
        """Set up action button signals."""
        self.ui.btnOpen.clicked.connect(self._open_selected_assets)
        self.ui.btnExtract.clicked.connect(self._extract_selected_assets)
        self.ui.btnDuplicate.clicked.connect(self._duplicate_selected_assets)
        self.ui.btnDelete.clicked.connect(self._delete_selected_assets)

    def _setup_toolbar_signals(self):
        """Set up toolbar button signals."""
        self.ui.btnCollapseAll.clicked.connect(self.ui.projectTree.collapseAll)
        self.ui.btnExpandAll.clicked.connect(self.ui.projectTree.expandAll)
        self.ui.btnRefresh.clicked.connect(self._refresh_current_installation)
        self.ui.searchBox.textChanged.connect(self._filter_assets)

    def _setup_keyboard_shortcuts(self):
        """Set up keyboard shortcuts."""
        from qtpy.QtGui import QKeySequence
        from qtpy.QtWidgets import QShortcut
        
        # File operations
        QShortcut(QKeySequence("Ctrl+O"), self).activated.connect(self.open_from_file)
        QShortcut(QKeySequence("Ctrl+S"), self).activated.connect(self._save_current_asset)
        QShortcut(QKeySequence("Ctrl+W"), self).activated.connect(self.close)
        
        # Edit operations
        QShortcut(QKeySequence("Ctrl+C"), self).activated.connect(self._copy_selected_assets)
        QShortcut(QKeySequence("Ctrl+X"), self).activated.connect(self._cut_selected_assets)
        QShortcut(QKeySequence("Ctrl+V"), self).activated.connect(self._paste_assets)
        QShortcut(QKeySequence("Delete"), self).activated.connect(self._delete_selected_assets)
        QShortcut(QKeySequence("Ctrl+D"), self).activated.connect(self._duplicate_selected_assets)
        
        # Navigation
        QShortcut(QKeySequence("F5"), self).activated.connect(self._refresh_current_installation)
        QShortcut(QKeySequence("Ctrl+F"), self).activated.connect(self._focus_search)
        QShortcut(QKeySequence("Ctrl+Shift+F"), self).activated.connect(self.open_file_search_dialog)
        
        # View operations
        QShortcut(QKeySequence("Ctrl+1"), self).activated.connect(lambda: self.ui.viewStack.setCurrentIndex(0))
        QShortcut(QKeySequence("Ctrl+2"), self).activated.connect(lambda: self.ui.viewStack.setCurrentIndex(1))
        QShortcut(QKeySequence("Ctrl+3"), self).activated.connect(lambda: self.ui.viewStack.setCurrentIndex(2))
        QShortcut(QKeySequence("Ctrl+4"), self).activated.connect(lambda: self.ui.viewStack.setCurrentIndex(3))
        
        # Quick actions
        QShortcut(QKeySequence("Return"), self).activated.connect(self._open_selected_assets)
        QShortcut(QKeySequence("Ctrl+E"), self).activated.connect(self._extract_selected_assets)
        QShortcut(QKeySequence("Space"), self).activated.connect(self._quick_preview)
        QShortcut(QKeySequence("Ctrl+Shift+P"), self).activated.connect(self._show_command_palette)
        
        # Bookmarks
        QShortcut(QKeySequence("Ctrl+B"), self).activated.connect(self._toggle_bookmark)
        QShortcut(QKeySequence("Ctrl+Shift+B"), self).activated.connect(self._show_bookmarks)
        
        # Batch operations
        QShortcut(QKeySequence("Ctrl+Shift+O"), self).activated.connect(self._show_batch_operations)

    def _setup_context_menus(self):
        """Set up context menu policies."""
        # Context menus are set up per-widget in their signal setup methods
        pass

    def _setup_status_bar(self):
        """Set up the status bar."""
        self._status_label = QtWidgets.QLabel("Ready")
        self._selection_label = QtWidgets.QLabel("No selection")
        self._progress_bar = QtWidgets.QProgressBar()
        self._progress_bar.setMaximumWidth(200)
        self._progress_bar.setVisible(False)
        
        status_bar = self.statusBar()
        if status_bar:
            status_bar.addWidget(self._status_label, 1)
            status_bar.addPermanentWidget(self._selection_label)
            status_bar.addPermanentWidget(self._progress_bar)
        
        # Update status on selection change
        self._update_status_bar()

    def _setup_menu_signals(self):
        """Set up menu action signals."""
        # File menu
        self.ui.openAction.triggered.connect(self.open_from_file)
        self.ui.actionSettings.triggered.connect(self.open_settings_dialog)
        self.ui.actionExit.triggered.connect(lambda *args: self.close())

        # New resource actions
        self.ui.actionNewTLK.triggered.connect(lambda: self._new_resource("TLK"))
        self.ui.actionNewDLG.triggered.connect(lambda: self._new_resource("DLG"))
        self.ui.actionNewNSS.triggered.connect(lambda: self._new_resource("NSS"))
        self.ui.actionNewUTC.triggered.connect(lambda: self._new_resource("UTC"))
        self.ui.actionNewUTP.triggered.connect(lambda: self._new_resource("UTP"))
        self.ui.actionNewUTD.triggered.connect(lambda: self._new_resource("UTD"))
        self.ui.actionNewUTI.triggered.connect(lambda: self._new_resource("UTI"))
        self.ui.actionNewUTT.triggered.connect(lambda: self._new_resource("UTT"))
        self.ui.actionNewUTM.triggered.connect(lambda: self._new_resource("UTM"))
        self.ui.actionNewUTW.triggered.connect(lambda: self._new_resource("UTW"))
        self.ui.actionNewUTE.triggered.connect(lambda: self._new_resource("UTE"))
        self.ui.actionNewUTS.triggered.connect(lambda: self._new_resource("UTS"))
        self.ui.actionNewGFF.triggered.connect(lambda: self._new_resource("GFF"))
        self.ui.actionNewERF.triggered.connect(lambda: self._new_resource("ERF"))
        self.ui.actionNewTXT.triggered.connect(lambda: self._new_resource("TXT"))
        self.ui.actionNewSSF.triggered.connect(lambda: self._new_resource("SSF"))

        # Tools menu
        self.ui.actionModuleDesigner.triggered.connect(self.open_module_designer)
        self.ui.actionEditTLK.triggered.connect(self.open_active_talktable)
        self.ui.actionEditJRL.triggered.connect(self.open_active_journal)
        self.ui.actionFileSearch.triggered.connect(self.open_file_search_dialog)
        self.ui.actionIndoorMapBuilder.triggered.connect(self.open_indoor_map_builder)
        self.ui.actionKotorDiff.triggered.connect(self.open_kotordiff)
        self.ui.actionTSLPatchDataEditor.triggered.connect(self.open_tslpatchdata_editor)
        self.ui.actionCloneModule.triggered.connect(self.open_clone_module_dialog)

        # Help menu
        self.ui.actionInstructions.triggered.connect(self.open_instructions_window)
        self.ui.actionHelpUpdates.triggered.connect(self.update_manager.check_for_updates)
        self.ui.actionHelpAbout.triggered.connect(self.open_about_dialog)

        # Discord links
        from toolset.utils.misc import open_link
        self.ui.actionDiscordDeadlyStream.triggered.connect(
            lambda: open_link("https://discord.com/invite/bRWyshn")
        )
        self.ui.actionDiscordKotOR.triggered.connect(
            lambda: open_link("http://discord.gg/kotor")
        )
        self.ui.actionDiscordHolocronToolset.triggered.connect(
            lambda: open_link("https://discord.gg/3ME278a9tQ")
        )

        # Theme menu
        if self.ui.menuTheme is not None:
            self.ui.menuTheme.clear()
            theme_action = QAction(tr("Theme..."), self)
            theme_action.triggered.connect(self._open_theme_dialog)
            self.ui.menuTheme.addAction(theme_action)

        # Recent files menu
        self.ui.menuRecentFiles.aboutToShow.connect(self.populate_recent_files_menu)

        # Language menu
        self._setup_language_menu()

    def _setup_language_menu(self):
        """Set up the language menu with all available languages."""
        from toolset.gui.common.localization import ToolsetLanguage

        current_language_id = self.settings.selectedLanguage
        try:
            current_language = ToolsetLanguage(current_language_id)
        except ValueError:
            current_language = ToolsetLanguage.ENGLISH

        set_language(current_language)

        for language in ToolsetLanguage:
            def make_language_handler(lang=language):
                def change_language(*args):
                    set_language(lang)
                    self.settings.selectedLanguage = lang.value
                    self._update_language_menu_checkmarks(lang)
                    self.apply_translations()
                return change_language

            display_name = language.get_display_name()
            language_action = self.ui.menuLanguage.addAction(display_name)
            if language_action:
                language_action.setCheckable(True)
                language_action.triggered.connect(make_language_handler())
                self._language_actions[language.value] = language_action

                if language == current_language:
                    language_action.setChecked(True)

        self.apply_translations()

    def _update_language_menu_checkmarks(self, language: "ToolsetLanguage"):
        """Update checkmarks in the language menu."""
        for action in self._language_actions.values():
            action.setChecked(False)

        if language.value in self._language_actions:
            self._language_actions[language.value].setChecked(True)

    def apply_translations(self):
        """Apply translations to all UI strings."""
        # Translate menus
        self.ui.menuFile.setTitle(tr("File"))
        self.ui.menuEdit.setTitle(tr("Edit"))
        self.ui.menuView.setTitle(tr("View"))
        self.ui.menuTools.setTitle(tr("Tools"))
        self.ui.menuTheme.setTitle(tr("Theme"))
        self.ui.menuLanguage.setTitle(tr("Language"))
        self.ui.menuHelp.setTitle(tr("Help"))
        self.ui.menuNew.setTitle(tr("New"))
        self.ui.menuRecentFiles.setTitle(tr("Recent Files"))
        self.ui.menuDiscord.setTitle(tr("Discord"))

        # Translate actions
        self.ui.actionExit.setText(tr("Exit"))
        self.ui.actionSettings.setText(tr("Settings"))
        self.ui.actionHelpAbout.setText(tr("About"))
        self.ui.actionInstructions.setText(tr("Instructions"))
        self.ui.actionHelpUpdates.setText(tr("Check For Updates"))

        # Update window title
        self.setWindowTitle(f"{tr('Holocron Toolset')} ({qtpy.API_NAME})")

    # ========== Project Tree Handlers ==========

    @Slot(QModelIndex, QModelIndex)
    def _on_project_selection_changed(
        self,
        current: QModelIndex,
        previous: QModelIndex,
    ):
        """Handle selection change in the project tree."""
        if not current.isValid():
            return

        item = self.fs_model.itemFromIndex(current)
        RobustLogger().debug(f"Project selection changed: {item.__class__.__name__}")

        # If installation item, load it
        if isinstance(item, InstallationItem):
            self._load_installation_from_item(item)
        
        # Update asset views to show selected item
        self._sync_asset_views_to_index(current)

    @Slot(QModelIndex)
    def _on_project_item_activated(self, index: QModelIndex):
        """Handle double-click on project tree item."""
        if not index.isValid():
            return

        item = self.fs_model.itemFromIndex(index)
        
        # If resource, open it
        if isinstance(item, ResourceItem):
            self._open_resources([item.resource])
        
        # If directory or category, expand and navigate
        elif isinstance(item, (DirItem, CategoryItem)):
            self.ui.projectTree.setExpanded(index, not self.ui.projectTree.isExpanded(index))
            self._sync_asset_views_to_index(index)

    def _load_installation_from_item(self, item: InstallationItem):
        """Load an installation from an InstallationItem."""
        if self.active is not None and self.active.name == item.name:
            return

        name = item.name
        path = str(item.path)
        tsl = item.tsl

        # Validate path
        if not path or not Path(path).exists():
            QMessageBox.warning(
                self,
                tr("Installation Not Found"),
                trf("Installation path '{path}' does not exist.", path=path)
            )
            return

        # Get or create installation
        if name in self.installations:
            self.active = self.installations[name]
        else:
            def create_installation() -> HTInstallation:
                return HTInstallation(Path(path), name, tsl=tsl)

            loader = AsyncLoader(
                self,
                tr("Loading installation..."),
                create_installation,
                tr("Failed to load installation"),
            )
            if not loader.exec():
                return

            self.active = loader.value
            self.installations[name] = self.active

        # Setup file watcher for this installation
        self._setup_file_watcher(self.active)

        # Update UI
        self.update_menus()
        self.sig_installation_changed.emit(self.active)

    # ========== Asset View Handlers ==========

    @Slot(QModelIndex)
    def _on_asset_item_activated(self, index: QModelIndex):
        """Handle double-click on asset view item."""
        if not index.isValid():
            return

        source_index = self._map_to_source_index(index)
        item = self.fs_model.itemFromIndex(source_index)
        
        if isinstance(item, ResourceItem):
            self._open_resources([item.resource])
        elif isinstance(item, (DirItem, CategoryItem)):
            # Navigate into directory in asset views
            self._sync_asset_views_to_index(index)

    def _sync_asset_views(self):
        """Sync all asset views to the current selection in assetTreeView."""
        current_index = self.ui.assetTreeView.currentIndex()
        self._sync_asset_views_to_index(current_index)

    def _sync_asset_views_to_index(self, index: QModelIndex):
        """Sync all asset views to a specific index."""
        if not index.isValid():
            root_index = QModelIndex()
        else:
            root_index = index

        self.ui.assetListView.setRootIndex(root_index)
        self.ui.assetGridView.setRootIndex(root_index)
        self.ui.assetTableView.setRootIndex(root_index)

        # Update breadcrumb
        self._update_breadcrumb(index)

    def _update_breadcrumb(self, index: QModelIndex):
        """Update the breadcrumb label with the current path."""
        if not index.isValid():
            self.ui.breadcrumbLabel.setText("Path: /")
            return

        path_parts = []
        current = self._map_to_source_index(index)
        while current.isValid():
            item = self.fs_model.itemFromIndex(current)
            if item:
                path_parts.insert(0, str(item.data()))
            current = current.parent()

        breadcrumb = " > ".join(path_parts)
        self.ui.breadcrumbLabel.setText(f"Path: {breadcrumb}")

    @Slot(QModelIndex, QModelIndex)
    def _update_inspector_panel(self, current: QModelIndex, previous: QModelIndex | None = None):
        """Update the inspector panel based on the current selection."""
        if not current.isValid():
            # Clear inspector
            self.ui.assetName.setText("")
            self.ui.assetType.setText("")
            self.ui.assetSize.setText("")
            self.ui.assetPath.setText("")
            self.ui.previewLabel.setText(tr("No Preview Available"))
            return
        
        source_index = self._map_to_source_index(current)
        item = self.fs_model.itemFromIndex(source_index)
        
        if isinstance(item, ResourceItem):
            resource = item.resource
            
            # Update asset info
            self.ui.assetName.setText(resource.resname())
            self.ui.assetType.setText(resource.restype().extension.upper())
            
            # Get size
            try:
                data = resource.data()
                size_bytes = len(data) if data else 0
                size_kb = size_bytes / 1024
                if size_kb < 1:
                    size_str = f"{size_bytes} B"
                elif size_kb < 1024:
                    size_str = f"{size_kb:.2f} KB"
                else:
                    size_str = f"{size_kb / 1024:.2f} MB"
                self.ui.assetSize.setText(size_str)
            except Exception:
                self.ui.assetSize.setText(tr("Unknown"))
            
            # Update path
            source = resource.source()
            if source:
                self.ui.assetPath.setText(str(source))
            else:
                self.ui.assetPath.setText(tr("N/A"))
            
            # Update preview
            self._update_preview(resource)
        
        elif isinstance(item, (DirItem, CategoryItem)):
            # Show directory info
            self.ui.assetName.setText(str(item.data()))
            self.ui.assetType.setText(tr("Directory"))
            self.ui.assetSize.setText(tr("N/A"))
            self.ui.assetPath.setText(str(item.path) if hasattr(item, "path") else "")
            self.ui.previewLabel.setText(tr("No Preview Available"))
        
        else:
            # Clear for other item types
            self.ui.assetName.setText("")
            self.ui.assetType.setText("")
            self.ui.assetSize.setText("")
            self.ui.assetPath.setText("")
            self.ui.previewLabel.setText(tr("No Preview Available"))

    def _update_preview(self, resource: FileResource):
        """Update the preview for a resource."""
        try:
            restype = resource.restype()
            
            # Check if it's a TGA or TPC image
            if restype.extension.lower() in ("tga", "tpc"):
                from pykotor.resource.formats.tpc import TPC
                
                data = resource.data()
                if not data:
                    self.ui.previewLabel.setText(tr("No Data"))
                    return
                
                # Try to load as TPC
                if restype.extension.lower() == "tpc":
                    tpc = TPC.from_bytes(data)
                    # Convert to QPixmap for display
                    from PIL import Image
                    from io import BytesIO
                    
                    # Get image data from TPC
                    width, height = tpc.width, tpc.height
                    rgba_data = tpc.convert(TPC.TPCTextureFormat.RGBA)
                    
                    # Create PIL image
                    img = Image.frombytes("RGBA", (width, height), rgba_data)
                    
                    # Convert to QPixmap
                    img_byte_arr = BytesIO()
                    img.save(img_byte_arr, format='PNG')
                    img_byte_arr.seek(0)
                    
                    from qtpy.QtGui import QPixmap
                    pixmap = QPixmap()
                    pixmap.loadFromData(img_byte_arr.read())
                    
                    # Scale to fit preview area (max 256x256)
                    if pixmap.width() > 256 or pixmap.height() > 256:
                        pixmap = pixmap.scaled(256, 256, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                    
                    self.ui.previewLabel.setPixmap(pixmap)
                else:
                    # TGA format - try to load directly
                    from qtpy.QtGui import QPixmap
                    pixmap = QPixmap()
                    if pixmap.loadFromData(data):
                        if pixmap.width() > 256 or pixmap.height() > 256:
                            pixmap = pixmap.scaled(256, 256, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                        self.ui.previewLabel.setPixmap(pixmap)
                    else:
                        self.ui.previewLabel.setText(tr("Failed to load image"))
            else:
                # No preview available for this type
                self.ui.previewLabel.setText(tr("No Preview Available"))
                
        except Exception as e:
            RobustLogger().exception(f"Failed to generate preview: {e}")
            self.ui.previewLabel.setText(tr("Preview Error"))

    # ========== Action Handlers ==========

    def _open_selected_assets(self):
        """Open the selected assets in their respective editors."""
        resources = self._get_selected_resources()
        if resources:
            self._open_resources(resources)

    def _extract_selected_assets(self):
        """Extract the selected assets to disk."""
        resources = self._get_selected_resources()
        if not resources:
            return

        # Choose destination directory
        dest_dir = QFileDialog.getExistingDirectory(
            self,
            tr("Select Extraction Destination"),
            str(Path.home()),
            QFileDialog.Option.ShowDirsOnly
        )
        
        if not dest_dir:
            return
        
        dest_path = Path(dest_dir)
        
        # Extract each resource
        success_count = 0
        fail_count = 0
        
        for resource in resources:
            try:
                filename = f"{resource.resname()}.{resource.restype().extension}"
                output_path = dest_path / filename
                
                # Get resource data
                data = resource.data()
                if data:
                    output_path.write_bytes(data)
                    success_count += 1
                else:
                    fail_count += 1
                    RobustLogger().warning(f"Failed to extract {filename}: no data")
            except Exception as e:
                fail_count += 1
                RobustLogger().exception(f"Failed to extract {resource.resname()}: {e}")
        
        # Show results
        if fail_count == 0:
            QMessageBox.information(
                self,
                tr("Extraction Complete"),
                trf("Successfully extracted {count} file(s) to {path}", count=success_count, path=dest_dir)
            )
        else:
            QMessageBox.warning(
                self,
                tr("Extraction Completed With Errors"),
                trf("Extracted {success} file(s), failed {fail} file(s)", success=success_count, fail=fail_count)
            )

    def _duplicate_selected_assets(self):
        """Duplicate the selected assets."""
        resources = self._get_selected_resources()
        if not resources:
            return

        if not self.active:
            QMessageBox.warning(
                self,
                tr("No Installation"),
                tr("Please select an installation first.")
            )
            return

        # Ask for confirmation
        reply = QMessageBox.question(
            self,
            tr("Duplicate Assets"),
            trf("Duplicate {count} selected asset(s)?", count=len(resources)),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        # Duplicate each resource to the Override folder
        success_count = 0
        fail_count = 0
        
        override_path = self.active.override_path()
        if not override_path.exists():
            override_path.mkdir(parents=True, exist_ok=True)
        
        for resource in resources:
            try:
                data = resource.data()
                if not data:
                    fail_count += 1
                    continue
                
                # Check if file already exists in override
                filename = f"{resource.resname()}.{resource.restype().extension}"
                target_path = override_path / filename
                
                if target_path.exists():
                    # Ask to overwrite
                    reply = QMessageBox.question(
                        self,
                        tr("File Exists"),
                        trf("File {filename} already exists in Override. Overwrite?", filename=filename),
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                    )
                    if reply != QMessageBox.StandardButton.Yes:
                        continue
                
                # Write the file
                target_path.write_bytes(data)
                success_count += 1
                
            except Exception as e:
                fail_count += 1
                RobustLogger().exception(f"Failed to duplicate {resource.resname()}: {e}")
        
        # Refresh the installation to show new files
        self._refresh_current_installation()
        
        # Show results
        if fail_count == 0:
            QMessageBox.information(
                self,
                tr("Duplication Complete"),
                trf("Successfully duplicated {count} file(s) to Override", count=success_count)
            )
        else:
            QMessageBox.warning(
                self,
                tr("Duplication Completed With Errors"),
                trf("Duplicated {success} file(s), failed {fail} file(s)", success=success_count, fail=fail_count)
            )

    def _delete_selected_assets(self):
        """Delete the selected assets."""
        resources = self._get_selected_resources()
        if not resources:
            return

        # Ask for confirmation
        reply = QMessageBox.warning(
            self,
            tr("Delete Assets"),
            trf("Permanently delete {count} selected asset(s)?\\n\\nThis action cannot be undone!", count=len(resources)),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        # Only allow deletion from Override folder for safety
        success_count = 0
        fail_count = 0
        skipped_count = 0
        
        for resource in resources:
            try:
                source = resource.source()
                if not source:
                    skipped_count += 1
                    continue
                
                source_path = Path(source)
                
                # Check if file is in Override
                if not self.active:
                    skipped_count += 1
                    continue
                
                override_path = self.active.override_path()
                try:
                    if source_path.relative_to(override_path):
                        # File is in Override, safe to delete
                        source_path.unlink()
                        success_count += 1
                    else:
                        # File is not in Override
                        skipped_count += 1
                except ValueError:
                    # Not relative to Override
                    skipped_count += 1
                    
            except Exception as e:
                fail_count += 1
                RobustLogger().exception(f"Failed to delete {resource.resname()}: {e}")
        
        # Refresh the installation
        if success_count > 0:
            self._refresh_current_installation()
        
        # Show results
        message_parts = []
        if success_count > 0:
            message_parts.append(trf("Deleted {count} file(s)", count=success_count))
        if fail_count > 0:
            message_parts.append(trf("Failed to delete {count} file(s)", count=fail_count))
        if skipped_count > 0:
            message_parts.append(trf("Skipped {count} file(s) (not in Override)", count=skipped_count))
        
        if fail_count > 0:
            QMessageBox.warning(
                self,
                tr("Delete Completed With Errors"),
                "\\n".join(message_parts)
            )
        else:
            QMessageBox.information(
                self,
                tr("Delete Complete"),
                "\\n".join(message_parts)
            )

    def _map_to_source_index(self, index: QModelIndex) -> QModelIndex:
        """Map a proxy index to the source model index if needed."""
        model = index.model()
        if isinstance(model, QSortFilterProxyModel):
            return model.mapToSource(index)
        return index

    def _navigate_to_resource(self, resource_id: str) -> bool:
        """Navigate to and select a resource by its ID (filename.extension).
        
        Args:
            resource_id: Resource identifier in format "resname.ext"
            
        Returns:
            True if resource was found and selected, False otherwise
        """
        if not self.active:
            return False
        
        # Find the resource in the installation
        try:
            # Parse resource ID (e.g., "texture.tpc" -> resname="texture", ext="tpc")
            if "." not in resource_id:
                return False
            
            resname, ext = resource_id.rsplit(".", 1)
            res_type = ResourceType.from_extension(ext)
            if not res_type:
                return False
            
            # Try to get the resource from the installation
            resource = self.active.resource(resname, res_type)
            if not resource:
                return False
            
            # Find the resource in the model
            def find_resource_index(parent_index: QModelIndex) -> QModelIndex | None:
                """Recursively search for resource in the model."""
                row_count = self.fs_model.rowCount(parent_index)
                for row in range(row_count):
                    index = self.fs_model.index(row, 0, parent_index)
                    item = self.fs_model.itemFromIndex(index)
                    
                    if isinstance(item, ResourceItem):
                        item_resource = item.resource
                        if (item_resource.resname() == resname and 
                            item_resource.restype() == res_type):
                            return index
                    
                    # Search children recursively
                    child_index = find_resource_index(index)
                    if child_index is not None:
                        return child_index
                
                return None
            
            # Start search from root
            source_index = find_resource_index(QModelIndex())
            if not source_index:
                return False
            
            # Map to proxy index if using proxy model
            current_view_index = self.ui.viewStack.currentIndex()
            views = [
                self.ui.assetTreeView,
                self.ui.assetListView,
                self.ui.assetGridView,
                self.ui.assetTableView,
            ]
            
            if current_view_index >= len(views):
                return False
            
            view = views[current_view_index]
            model = view.model()
            
            # Map source index to proxy if needed
            if isinstance(model, QSortFilterProxyModel):
                proxy_index = model.mapFromSource(source_index)
                if not proxy_index.isValid():
                    return False
                target_index = proxy_index
            else:
                target_index = source_index
            
            # Select and scroll to the resource
            selection_model = view.selectionModel()
            if selection_model:
                selection_model.clearSelection()
                selection_model.select(target_index, selection_model.SelectionFlag.Select | selection_model.SelectionFlag.Rows)
                selection_model.setCurrentIndex(target_index, selection_model.SelectionFlag.Current)
                view.scrollTo(target_index, QAbstractItemView.ScrollHint.PositionAtCenter)
            
            return True
            
        except Exception as e:
            from loggerplus import RobustLogger
            RobustLogger().exception(f"Failed to navigate to resource {resource_id}: {e}")
            return False

    def _get_selected_resources(self) -> list[FileResource]:
        """Get the currently selected resources from the active view."""
        current_view_index = self.ui.viewStack.currentIndex()
        views = [
            self.ui.assetTreeView,
            self.ui.assetListView,
            self.ui.assetGridView,
            self.ui.assetTableView,
        ]
        
        if current_view_index >= len(views):
            return []

        view = views[current_view_index]
        selection_model = view.selectionModel()
        if not selection_model:
            return []

        resources = []
        for index in selection_model.selectedIndexes():
            source_index = self._map_to_source_index(index)
            item = self.fs_model.itemFromIndex(source_index)
            if isinstance(item, ResourceItem):
                resources.append(item.resource)

        return resources

    def _open_resources(self, resources: list[FileResource]):
        """Open resources in their respective editors."""
        if not self.active:
            return

        for resource in resources:
            open_resource_editor(resource, self.active, self)

    # ========== Toolbar Handlers ==========

    def _refresh_current_installation(self):
        """Refresh the current installation."""
        if not self.active:
            return

        # Find the InstallationItem in the model
        for i in range(self.fs_model.rowCount()):
            index = self.fs_model.index(i, 0)
            item = self.fs_model.itemFromIndex(index)
            
            if isinstance(item, InstallationItem) and item.name == self.active.name:
                # Clear and reload the installation's children
                item.clear()
                item.loadChildren()
                
                # Refresh the view
                self.fs_model.layoutChanged.emit()
                
                QMessageBox.information(
                    self,
                    tr("Refresh Complete"),
                    trf("Refreshed installation: {name}", name=self.active.name)
                )
                break

    def _filter_assets(self, text: str):
        """Filter assets based on search text."""
        self.fs_proxy.set_search(text)

    def _focus_search(self):
        """Focus the search box."""
        self.ui.searchBox.setFocus()
        self.ui.searchBox.selectAll()

    # ========== Context Menus ==========

    @Slot(QPoint)
    def _show_project_context_menu(self, pos: QPoint):
        """Show context menu for project tree."""
        index = self.ui.projectTree.indexAt(pos)
        if not index.isValid():
            return
        
        item = self.fs_model.itemFromIndex(index)
        menu = QtWidgets.QMenu(self)
        
        if isinstance(item, InstallationItem):
            menu.addAction(tr("Refresh Installation"), self._refresh_current_installation)
            menu.addAction(tr("Set as Active"), lambda: self._load_installation_from_item(item))
            menu.addSeparator()
            menu.addAction(tr("Properties"), lambda: self._show_installation_properties(item))
        
        elif isinstance(item, CategoryItem):
            menu.addAction(tr("Refresh Category"), self._refresh_current_installation)
            menu.addAction(tr("Expand All"), lambda: self.ui.projectTree.expandRecursively(index))
            menu.addAction(tr("Collapse All"), lambda: self.ui.projectTree.collapse(index))
        
        elif isinstance(item, ResourceItem):
            menu.addAction(tr("Open"), self._open_selected_assets)
            menu.addAction(tr("Extract..."), self._extract_selected_assets)
            menu.addSeparator()
            menu.addAction(tr("Copy"), self._copy_selected_assets)
            menu.addAction(tr("Duplicate to Override"), self._duplicate_selected_assets)
            menu.addSeparator()
            menu.addAction(tr("Delete"), self._delete_selected_assets)
            menu.addSeparator()
            menu.addAction(tr("Show in Explorer"), lambda: self._show_in_explorer(item.resource))
            menu.addAction(tr("Copy Path"), lambda: self._copy_path_to_clipboard(item.resource))
            menu.addSeparator()
            menu.addAction(tr("Add to Favorites"), lambda: self._add_to_favorites(item.resource))
        
        global_pos = self.ui.projectTree.viewport().mapToGlobal(pos)
        menu.exec(global_pos)

    @Slot(QPoint)
    def _show_asset_context_menu(self, pos: QPoint):
        """Show context menu for asset views."""
        # Determine which view triggered the menu
        sender_widget = self.sender()
        if not isinstance(sender_widget, QtWidgets.QAbstractItemView):
            return
        
        index = sender_widget.indexAt(pos)
        if not index.isValid():
            return

        source_index = self._map_to_source_index(index)
        item = self.fs_model.itemFromIndex(source_index)
        menu = QtWidgets.QMenu(self)
        
        if isinstance(item, ResourceItem):
            # File operations
            menu.addAction(tr("Open"), self._open_selected_assets)
            menu.addAction(tr("Open With..."), self._open_with_dialog)
            menu.addSeparator()
            
            # Edit operations
            menu.addAction(tr("Copy"), self._copy_selected_assets)
            menu.addAction(tr("Cut"), self._cut_selected_assets)
            if self._clipboard_has_assets():
                menu.addAction(tr("Paste"), self._paste_assets)
            menu.addSeparator()
            
            # Asset operations
            menu.addAction(tr("Extract..."), self._extract_selected_assets)
            menu.addAction(tr("Duplicate to Override"), self._duplicate_selected_assets)
            menu.addAction(tr("Delete"), self._delete_selected_assets)
            menu.addSeparator()
            
            # Batch operations (show if multiple selected)
            if len(self._get_selected_resources()) > 1:
                menu.addAction(tr("Batch Operations..."), self._show_batch_operations)
                menu.addSeparator()
            
            # Utilities
            menu.addAction(tr("Rename..."), self._rename_selected_asset)
            menu.addAction(tr("Show Dependencies"), lambda: self._show_dependencies(item.resource))
            menu.addAction(tr("Find References"), lambda: self._find_references(item.resource))
            menu.addSeparator()
            
            # System operations
            menu.addAction(tr("Show in Explorer"), lambda: self._show_in_explorer(item.resource))
            menu.addAction(tr("Copy Path"), lambda: self._copy_path_to_clipboard(item.resource))
            menu.addSeparator()
            
            # Favorites
            menu.addAction(tr("Add to Favorites"), lambda: self._add_to_favorites(item.resource))
        
        elif isinstance(item, (DirItem, CategoryItem)):
            menu.addAction(tr("New Resource..."), self._show_new_resource_dialog)
            menu.addSeparator()
            menu.addAction(tr("Refresh"), self._refresh_current_installation)
            menu.addAction(tr("Expand All"), lambda: sender_widget.expandRecursively(index) if hasattr(sender_widget, 'expandRecursively') else None)
            menu.addAction(tr("Collapse All"), lambda: sender_widget.collapse(index) if hasattr(sender_widget, 'collapse') else None)
        
        global_pos = sender_widget.viewport().mapToGlobal(pos)
        menu.exec(global_pos)

    # ========== New Resource Handlers ==========

    def _show_new_resource_dialog(self):
        """Show dialog to create a new resource."""
        if not self.active:
            QMessageBox.warning(
                self,
                tr("No Installation"),
                tr("Please select an installation first.")
            )
            return
        
        from qtpy.QtWidgets import QDialog, QVBoxLayout, QLabel, QListWidget, QPushButton, QHBoxLayout, QListWidgetItem, QInputDialog
        from qtpy.QtCore import Qt
        
        dialog = QDialog(self)
        dialog.setWindowTitle(tr("Create New Resource"))
        dialog.setWindowFlags(dialog.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        dialog.resize(500, 400)
        
        layout = QVBoxLayout(dialog)
        
        # Instructions
        instructions = QLabel(tr("Select resource type to create:"))
        layout.addWidget(instructions)
        
        # Resource type list
        type_list = QListWidget()
        
        # Define available resource types with descriptions
        resource_types = [
            ("2DA", "2DA Table", tr("Table data file")),
            ("TXT", "Text File", tr("Plain text file")),
            ("TXI", "Texture Info", tr("Texture information file")),
            ("NSS", "Script Source", tr("NWScript source code")),
            ("UTC", "Creature", tr("Creature template")),
            ("UTP", "Placeable", tr("Placeable object template")),
            ("UTD", "Door", tr("Door template")),
            ("UTI", "Item", tr("Item template")),
            ("UTE", "Encounter", tr("Encounter template")),
            ("UTM", "Merchant", tr("Merchant template")),
            ("UTS", "Sound", tr("Sound template")),
            ("UTT", "Trigger", tr("Trigger template")),
            ("UTW", "Waypoint", tr("Waypoint template")),
            ("DLG", "Dialog", tr("Conversation file")),
            ("JRL", "Journal", tr("Journal entry")),
        ]
        
        for ext, type_name, description in resource_types:
            item = QListWidgetItem(f"{type_name} (.{ext})\n{description}")
            item.setData(Qt.ItemDataRole.UserRole, ext)
            type_list.addItem(item)
        
        type_list.setCurrentRow(0)
        layout.addWidget(type_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        create_button = QPushButton(tr("Create"))
        cancel_button = QPushButton(tr("Cancel"))
        
        button_layout.addWidget(create_button)
        button_layout.addStretch()
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        
        # Create button action
        def create_resource():
            current_row = type_list.currentRow()
            if current_row < 0:
                return
            
            ext = resource_types[current_row][0]
            type_name = resource_types[current_row][1]
            
            # Ask for resource name
            name, ok = QInputDialog.getText(
                self,
                tr("Resource Name"),
                trf("Enter name for new {type}:", type=type_name),
                text=f"new_{ext.lower()}"
            )
            
            if not ok or not name:
                return
            
            # Remove extension if user added it
            if name.endswith(f".{ext.lower()}"):
                name = name[:-len(ext)-1]
            
            dialog.accept()
            self._create_new_resource(name, ext)
        
        create_button.clicked.connect(create_resource)
        cancel_button.clicked.connect(dialog.reject)
        type_list.itemDoubleClicked.connect(create_resource)
        
        dialog.exec_()

    def _create_new_resource(self, resname: str, restype_ext: str):
        """Create a new resource with the given name and type.
        
        Args:
            resname: Resource name (without extension)
            restype_ext: Resource type extension (e.g., "2DA", "NSS", "UTC")
        """
        try:
            from pykotor.resource.type import ResourceType
            
            # Get resource type from extension
            restype = ResourceType.from_extension(restype_ext)
            if not restype:
                QMessageBox.warning(
                    self,
                    tr("Invalid Type"),
                    trf("Unknown resource type: {type}", type=restype_ext)
                )
                return
            
            # Get Override path
            override_path = self.active.override_path()
            if not override_path.exists():
                override_path.mkdir(parents=True, exist_ok=True)
            
            # Build file path
            filename = f"{resname}.{restype_ext.lower()}"
            target_path = override_path / filename
            
            # Check if file already exists
            if target_path.exists():
                reply = QMessageBox.question(
                    self,
                    tr("File Exists"),
                    trf("File {filename} already exists. Overwrite?", filename=filename),
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                if reply != QMessageBox.StandardButton.Yes:
                    return
            
            # Create empty/template resource based on type
            if restype_ext == "2DA":
                # Create minimal 2DA file
                data = b"2DA V2.b\n\n           \n0          \n"
            elif restype_ext in {"TXT", "TXI", "NSS"}:
                # Create empty text file
                data = b""
            elif restype_ext in {"UTC", "UTP", "UTD", "UTI", "UTE", "UTM", "UTS", "UTT", "UTW", "DLG", "JRL"}:
                # Create minimal GFF structure
                # This is a basic GFF header - editors will properly initialize it
                from pykotor.resource.generics.gff import GFF, GFFFieldType
                gff = GFF()
                gff.root.add_field("TemplateResRef", GFFFieldType.ResRef, resname[:16])
                data = bytes(gff.write_gff())
            else:
                # For other types, create empty file
                data = b""
            
            # Write file
            target_path.write_bytes(data)
            
            # Refresh installation
            self._refresh_current_installation()
            
            # Show success and offer to open
            reply = QMessageBox.question(
                self,
                tr("Resource Created"),
                trf("Created {filename}. Open it now?", filename=filename),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # Open the newly created resource
                resource = self.active.resource(resname, restype)
                if resource:
                    from toolset.utils.window import open_resource_editor
                    open_resource_editor(resource, self.active, self)
            
            self._update_status_bar(trf("Created {filename}", filename=filename))
            
        except Exception as e:
            from loggerplus import RobustLogger
            RobustLogger().exception(f"Failed to create resource {resname}.{restype_ext}: {e}")
            QMessageBox.critical(
                self,
                tr("Creation Error"),
                trf("Failed to create resource: {error}", error=str(e))
            )

    def _new_resource(self, resource_type: str):
        """Create a new resource of the specified type."""
        # This is called from menu items - redirect to the dialog
        self._show_new_resource_dialog()

    # ========== Menu Handlers ==========

    def open_from_file(self):
        """Open a resource from a file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            tr("Open File"),
            str(Path.home()),
            "All Files (*.*)"
        )
        
        if not file_path:
            return
        
        path = Path(file_path)
        if not path.exists():
            return
        
        # Create a FileResource from the path
        resource = FileResource.from_path(path)
        if self.active:
            open_resource_editor(resource, self.active, self)
        else:
            QMessageBox.warning(
                self,
                tr("No Installation"),
                tr("Please select a game installation first.")
            )

    def open_settings_dialog(self):
        """Open the settings dialog."""
        from toolset.gui.dialogs.settings import SettingsDialog
        
        dialog = SettingsDialog(self)
        if dialog.exec():
            # Settings were saved, reload them
            self.reload_settings()

    def open_module_designer(self):
        """Open the module designer."""
        if not self.active:
            QMessageBox.warning(
                self,
                tr("No Installation"),
                tr("Please select a game installation first.")
            )
            return
        
        from toolset.gui.windows.module_designer import ModuleDesigner
        designer = ModuleDesigner(None, self.active, self)
        designer.show()

    def open_active_talktable(self):
        """Open the active installation's talk table."""
        if not self.active:
            QMessageBox.warning(
                self,
                tr("No Installation"),
                tr("Please select a game installation first.")
            )
            return
        
        from toolset.gui.editors.tlk import TLKEditor
        editor = TLKEditor(self, self.active)
        editor.load(self.active.path / "dialog.tlk")
        editor.show()

    def open_active_journal(self):
        """Open the active installation's journal."""
        if not self.active:
            QMessageBox.warning(
                self,
                tr("No Installation"),
                tr("Please select a game installation first.")
            )
            return
        
        # Load journal.jrl from active installation
        jrl_resource = self.active.resource("journal", ResourceType.JRL)
        if jrl_resource:
            open_resource_editor(jrl_resource, self.active, self)
        else:
            QMessageBox.warning(
                self,
                tr("Journal Not Found"),
                tr("Could not find journal.jrl in the active installation.")
            )

    def open_file_search_dialog(self):
        """Open the file search dialog."""
        if not self.active:
            QMessageBox.warning(
                self,
                tr("No Installation"),
                tr("Please select a game installation first.")
            )
            return
        
        from toolset.gui.dialogs.search import FileSearchDialog
        dialog = FileSearchDialog(self, [self.active])
        dialog.show()

    def open_indoor_map_builder(self):
        """Open the indoor map builder."""
        if not self.active:
            QMessageBox.warning(
                self,
                tr("No Installation"),
                tr("Please select a game installation first.")
            )
            return
        
        from toolset.gui.windows.indoor_builder import IndoorMapBuilder
        builder = IndoorMapBuilder(None, self.active)
        builder.show()

    def open_kotordiff(self):
        """Open KotorDiff."""
        import subprocess
        import shutil
        
        # Try to find kotordiff executable
        kotordiff_path = shutil.which("kotordiff")
        if kotordiff_path:
            subprocess.Popen([kotordiff_path])
        else:
            QMessageBox.information(
                self,
                tr("KotorDiff"),
                tr("KotorDiff executable not found in PATH.")
            )

    def open_tslpatchdata_editor(self):
        """Open the TSLPatchData editor."""
        from toolset.gui.editors.tsl_patchdata import TSLPatchDataEditor
        
        editor = TSLPatchDataEditor(self)
        editor.show()

    def open_clone_module_dialog(self):
        """Open the clone module dialog."""
        if not self.active:
            QMessageBox.warning(
                self,
                tr("No Installation"),
                tr("Please select a game installation first.")
            )
            return
        
        from toolset.gui.dialogs.clone_module import CloneModuleDialog
        dialog = CloneModuleDialog(self, self.active)
        dialog.exec()

    def open_instructions_window(self):
        """Open the instructions window."""
        from toolset.gui.dialogs.instructions import InstructionsDialog
        dialog = InstructionsDialog(self)
        dialog.exec()

    def open_about_dialog(self):
        """Open the about dialog."""
        from toolset.gui.dialogs.about import AboutDialog
        dialog = AboutDialog(self)
        dialog.exec()

    def populate_recent_files_menu(self):
        """Populate the recent files menu."""
        self.ui.menuRecentFiles.clear()
        
        # Get recent files from settings
        recent_files = self.settings.recentFiles if hasattr(self.settings, 'recentFiles') else []
        
        if not recent_files:
            no_files_action = self.ui.menuRecentFiles.addAction(tr("No Recent Files"))
            if no_files_action:
                no_files_action.setEnabled(False)
            return
        
        # Add recent files as menu items
        for file_path_str in recent_files[:10]:  # Limit to 10 most recent
            file_path = Path(file_path_str)
            if not file_path.exists():
                continue
            
            action = self.ui.menuRecentFiles.addAction(file_path.name)
            if action:
                def make_handler(path=file_path):
                    def open_recent():
                        resource = FileResource.from_path(path)
                        if self.active:
                            open_resource_editor(resource, self.active, self)
                        else:
                            QMessageBox.warning(
                                self,
                                tr("No Installation"),
                                tr("Please select a game installation first.")
                            )
                    return open_recent
                
                action.triggered.connect(make_handler())
                action.setToolTip(str(file_path))

    def update_menus(self):
        """Update menu states based on current installation."""
        has_installation = self.active is not None
        
        # Enable/disable actions based on installation state
        self.ui.actionNewDLG.setEnabled(has_installation)
        self.ui.actionNewNSS.setEnabled(has_installation)
        self.ui.actionNewUTC.setEnabled(has_installation)
        self.ui.actionNewUTP.setEnabled(has_installation)
        self.ui.actionNewUTD.setEnabled(has_installation)
        self.ui.actionNewUTI.setEnabled(has_installation)
        self.ui.actionNewUTT.setEnabled(has_installation)
        self.ui.actionNewUTM.setEnabled(has_installation)
        self.ui.actionNewUTW.setEnabled(has_installation)
        self.ui.actionNewUTE.setEnabled(has_installation)
        self.ui.actionNewUTS.setEnabled(has_installation)
        
        self.ui.actionEditTLK.setEnabled(has_installation)
        self.ui.actionEditJRL.setEnabled(has_installation)
        self.ui.actionFileSearch.setEnabled(has_installation)
        self.ui.actionModuleDesigner.setEnabled(has_installation)
        self.ui.actionIndoorMapBuilder.setEnabled(has_installation)
        self.ui.actionCloneModule.setEnabled(has_installation)

    @Slot(bool)
    def _open_theme_dialog(self, checked: bool = False):
        """Open the theme selector dialog."""
        if self._theme_dialog is None or not self._theme_dialog.isVisible():
            current_theme = self.settings.selectedTheme or "sourcegraph-dark"
            current_style = self.settings.selectedStyle or "Fusion"
            available_themes = sorted(set(self.theme_manager.get_available_themes()))
            available_styles = list(self.theme_manager.get_default_styles())

            self._theme_dialog = ThemeSelectorDialog(
                parent=self,
                available_themes=available_themes,
                available_styles=available_styles,
                current_theme=current_theme,
                current_style=current_style,
            )

            self._theme_dialog.theme_changed.connect(self._on_theme_changed)
            self._theme_dialog.style_changed.connect(self._on_style_changed)
            self._theme_dialog.show()
        else:
            self._theme_dialog.raise_()
            self._theme_dialog.activateWindow()

    def _on_theme_changed(self, theme_name: str):
        """Handle theme change from dialog."""
        self.theme_manager.change_theme(theme_name)
        self.settings.selectedTheme = theme_name
        if self._theme_dialog and self._theme_dialog.isVisible():
            self._theme_dialog.update_current_selection(theme_name=theme_name, style_name=None)

    def _on_style_changed(self, style_name: str):
        """Handle style change from dialog."""
        self.theme_manager.change_style(style_name)
        self.settings.selectedStyle = style_name
        if self._theme_dialog and self._theme_dialog.isVisible():
            self._theme_dialog.update_current_selection(theme_name=None, style_name=style_name)

    def reload_settings(self):
        """Reload settings from disk."""
        # Load installations from settings and set them in the model
        installations = self.settings.installations()
        self.fs_model.set_installations(installations)

    def unset_installation(self):
        """Unset the active installation."""
        self.active = None
        self.update_menus()

    # ========== SDK Feature Implementations ==========

    def _save_current_asset(self):
        """Save the currently active asset."""
        from toolset.utils.window import TOOLSET_WINDOWS
        from toolset.gui.editor import Editor
        
        # Find all open editor windows
        open_editors = [w for w in TOOLSET_WINDOWS if isinstance(w, Editor)]
        
        if not open_editors:
            QMessageBox.information(
                self,
                tr("No Editor"),
                tr("No editor windows are currently open.")
            )
            return
        
        # If only one editor is open, save it
        if len(open_editors) == 1:
            self._save_editor(open_editors[0])
            return
        
        # Multiple editors open - show selection dialog
        from qtpy.QtWidgets import QDialog, QVBoxLayout, QLabel, QListWidget, QPushButton, QHBoxLayout, QListWidgetItem
        from qtpy.QtCore import Qt
        
        dialog = QDialog(self)
        dialog.setWindowTitle(tr("Save Editor"))
        dialog.setWindowFlags(dialog.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        dialog.resize(500, 300)
        
        layout = QVBoxLayout(dialog)
        
        # Instructions
        instructions = QLabel(tr("Multiple editors are open. Select which one to save:"))
        layout.addWidget(instructions)
        
        # Editor list
        editor_list = QListWidget()
        for editor in open_editors:
            # Get editor title or file path
            title = editor.windowTitle() if hasattr(editor, 'windowTitle') else "Unknown Editor"
            if hasattr(editor, '_filepath') and editor._filepath:
                title = f"{title} - {editor._filepath}"
            
            item = QListWidgetItem(title)
            item.setData(Qt.ItemDataRole.UserRole, editor)
            editor_list.addItem(item)
        
        editor_list.setCurrentRow(0)
        layout.addWidget(editor_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        save_button = QPushButton(tr("Save"))
        save_all_button = QPushButton(tr("Save All"))
        cancel_button = QPushButton(tr("Cancel"))
        
        button_layout.addWidget(save_button)
        button_layout.addWidget(save_all_button)
        button_layout.addStretch()
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        
        # Button actions
        def save_selected():
            current_row = editor_list.currentRow()
            if current_row >= 0 and current_row < len(open_editors):
                editor = open_editors[current_row]
                self._save_editor(editor)
                dialog.accept()
        
        def save_all():
            success_count = 0
            fail_count = 0
            for editor in open_editors:
                if self._save_editor(editor, show_messages=False):
                    success_count += 1
                else:
                    fail_count += 1
            
            # Show summary
            if fail_count == 0:
                QMessageBox.information(
                    self,
                    tr("Save All Complete"),
                    trf("Successfully saved {count} editor(s).", count=success_count)
                )
            else:
                QMessageBox.warning(
                    self,
                    tr("Save All Complete"),
                    trf("Saved {success}, failed {fail}", success=success_count, fail=fail_count)
                )
            
            dialog.accept()
        
        save_button.clicked.connect(save_selected)
        save_all_button.clicked.connect(save_all)
        cancel_button.clicked.connect(dialog.reject)
        editor_list.itemDoubleClicked.connect(save_selected)
        
        dialog.exec_()

    def _save_editor(self, editor, show_messages: bool = True) -> bool:
        """Save an editor's content back to the installation.
        
        Args:
            editor: The editor window to save
            show_messages: Whether to show success/error messages
            
        Returns:
            True if save succeeded, False otherwise
        """
        try:
            # Check if editor has save method
            if not hasattr(editor, 'save') and not hasattr(editor, 'build'):
                if show_messages:
                    QMessageBox.warning(
                        self,
                        tr("Cannot Save"),
                        tr("This editor does not support saving.")
                    )
                return False
            
            # Try to save using editor's save method if available
            if hasattr(editor, 'save'):
                editor.save()
                if show_messages:
                    self._update_status_bar(tr("Editor saved successfully"))
                return True
            
            # Alternative: use build method and save to installation
            if hasattr(editor, 'build') and hasattr(editor, '_filepath'):
                data = editor.build()
                filepath = Path(editor._filepath)
                
                # If file is in Override, save it there
                if not self.active:
                    if show_messages:
                        QMessageBox.warning(
                            self,
                            tr("No Installation"),
                            tr("No active installation to save to.")
                        )
                    return False
                
                override_path = self.active.override_path()
                
                # Check if file should be saved to Override
                try:
                    filepath.relative_to(override_path)
                    # File is in Override, safe to save
                    filepath.write_bytes(data)
                    
                    # Refresh installation
                    self._refresh_current_installation()
                    
                    if show_messages:
                        self._update_status_bar(trf("Saved {filename}", filename=filepath.name))
                    return True
                except ValueError:
                    # Not in Override - save to Override instead
                    new_filepath = override_path / filepath.name
                    new_filepath.write_bytes(data)
                    
                    # Refresh installation
                    self._refresh_current_installation()
                    
                    if show_messages:
                        QMessageBox.information(
                            self,
                            tr("Saved to Override"),
                            trf("Saved {filename} to Override folder", filename=filepath.name)
                        )
                    return True
            
            if show_messages:
                QMessageBox.warning(
                    self,
                    tr("Cannot Save"),
                    tr("This editor does not support the required save methods.")
                )
            return False
            
        except Exception as e:
            from loggerplus import RobustLogger
            RobustLogger().exception(f"Failed to save editor: {e}")
            if show_messages:
                QMessageBox.critical(
                    self,
                    tr("Save Error"),
                    trf("Failed to save: {error}", error=str(e))
                )
            return False

    def _copy_selected_assets(self):
        """Copy selected assets to clipboard."""
        resources = self._get_selected_resources()
        if not resources:
            return
        
        # Store resources in internal clipboard
        if not hasattr(self, '_clipboard'):
            self._clipboard = {}
        self._clipboard['resources'] = resources
        self._clipboard['operation'] = 'copy'
        
        self._update_status_bar(f"Copied {len(resources)} asset(s)")

    def _cut_selected_assets(self):
        """Cut selected assets to clipboard."""
        resources = self._get_selected_resources()
        if not resources:
            return
        
        # Store resources in internal clipboard
        if not hasattr(self, '_clipboard'):
            self._clipboard = {}
        self._clipboard['resources'] = resources
        self._clipboard['operation'] = 'cut'
        
        self._update_status_bar(f"Cut {len(resources)} asset(s)")

    def _paste_assets(self):
        """Paste assets from clipboard."""
        if not hasattr(self, '_clipboard') or 'resources' not in self._clipboard:
            return
        
        operation = self._clipboard.get('operation', 'copy')
        
        if operation == 'copy':
            # Duplicate to current location
            self._duplicate_selected_assets()
        elif operation == 'cut':
            # Move to current location
            resources = self._clipboard['resources']
            if self._move_resources(resources):
                # Clear clipboard after successful move
                self._clipboard.clear()

    def _move_resources(self, resources: list[FileResource]) -> bool:
        """Move resources to Override folder.
        
        Args:
            resources: List of resources to move
            
        Returns:
            True if any resources were moved successfully, False otherwise
        """
        if not resources:
            return False
        
        if not self.active:
            QMessageBox.warning(
                self,
                tr("No Installation"),
                tr("Please select an installation first.")
            )
            return False
        
        override_path = self.active.override_path()
        if not override_path.exists():
            override_path.mkdir(parents=True, exist_ok=True)
        
        success_count = 0
        fail_count = 0
        skipped_count = 0
        
        for resource in resources:
            try:
                # Get source path
                source = resource.source()
                if not source:
                    skipped_count += 1
                    continue
                
                source_path = Path(source)
                
                # Validate source is in Override folder (can only move from Override)
                try:
                    source_path.relative_to(override_path)
                except ValueError:
                    # Not in Override - skip
                    skipped_count += 1
                    continue
                
                # Build target path (might be same as source if already in Override root)
                filename = f"{resource.resname()}.{resource.restype().extension}"
                target_path = override_path / filename
                
                # Skip if source and target are the same
                if source_path.resolve() == target_path.resolve():
                    skipped_count += 1
                    continue
                
                # Check for collision
                if target_path.exists() and target_path.resolve() != source_path.resolve():
                    reply = QMessageBox.question(
                        self,
                        tr("File Exists"),
                        trf("File {filename} already exists. Overwrite?", filename=filename),
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                        QMessageBox.StandardButton.No
                    )
                    if reply != QMessageBox.StandardButton.Yes:
                        skipped_count += 1
                        continue
                    # Remove existing file before move
                    target_path.unlink()
                
                # Execute move
                import shutil
                shutil.move(str(source_path), str(target_path))
                success_count += 1
                
            except Exception as e:
                fail_count += 1
                from loggerplus import RobustLogger
                RobustLogger().exception(f"Failed to move {resource.resname()}: {e}")
        
        # Refresh the installation if any moves succeeded
        if success_count > 0:
            self._refresh_current_installation()
        
        # Show results
        message_parts = []
        if success_count > 0:
            message_parts.append(trf("Moved {count} file(s)", count=success_count))
        if fail_count > 0:
            message_parts.append(trf("Failed to move {count} file(s)", count=fail_count))
        if skipped_count > 0:
            message_parts.append(trf("Skipped {count} file(s)", count=skipped_count))
        
        if message_parts:
            self._update_status_bar("; ".join(message_parts))
        
        return success_count > 0

    def _clipboard_has_assets(self) -> bool:
        """Check if clipboard has assets."""
        return hasattr(self, '_clipboard') and 'resources' in self._clipboard

    def _rename_selected_asset(self):
        """Rename the selected asset."""
        resources = self._get_selected_resources()
        if len(resources) != 1:
            QMessageBox.warning(
                self,
                tr("Rename"),
                tr("Please select exactly one asset to rename.")
            )
            return
        
        resource = resources[0]
        old_name = resource.resname()
        
        from qtpy.QtWidgets import QInputDialog
        new_name, ok = QInputDialog.getText(
            self,
            tr("Rename Asset"),
            tr("New name:"),
            text=old_name
        )
        
        if ok and new_name and new_name != old_name:
            # Validate and execute rename
            try:
                # Get source path
                source = resource.source()
                if not source:
                    QMessageBox.warning(
                        self,
                        tr("Rename"),
                        tr("Cannot rename: Resource has no source path.")
                    )
                    return
                
                source_path = Path(source)
                
                # Check if file is in Override (only allow rename in Override)
                if not self.active:
                    QMessageBox.warning(
                        self,
                        tr("Rename"),
                        tr("No active installation.")
                    )
                    return
                
                override_path = self.active.override_path()
                try:
                    source_path.relative_to(override_path)
                except ValueError:
                    # Not in Override
                    QMessageBox.warning(
                        self,
                        tr("Rename"),
                        tr("Can only rename files in Override folder.")
                    )
                    return
                
                # Preserve file extension
                extension = resource.restype().extension
                if not new_name.endswith(f".{extension}"):
                    new_name = f"{new_name}.{extension}"
                
                # Build new path
                new_path = source_path.parent / new_name
                
                # Check for duplicate
                if new_path.exists():
                    reply = QMessageBox.question(
                        self,
                        tr("Rename"),
                        trf("A file named '{name}' already exists. Overwrite?", name=new_name),
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                        QMessageBox.StandardButton.No
                    )
                    if reply != QMessageBox.StandardButton.Yes:
                        return
                
                # Execute rename
                import shutil
                shutil.move(str(source_path), str(new_path))
                
                # Refresh the installation
                self._refresh_current_installation()
                
                # Show success message
                self._update_status_bar(trf("Renamed {old} to {new}", old=old_name, new=new_name.rsplit('.', 1)[0]))
                
            except Exception as e:
                from loggerplus import RobustLogger
                RobustLogger().exception(f"Failed to rename {old_name}: {e}")
                QMessageBox.critical(
                    self,
                    tr("Rename Error"),
                    trf("Failed to rename: {error}", error=str(e))
                )

    def _show_in_explorer(self, resource: FileResource):
        """Show resource in system file explorer."""
        import subprocess
        import platform
        
        source = resource.source()
        if not source:
            return
        
        path = Path(source)
        if not path.exists():
            return
        
        system = platform.system()
        try:
            if system == "Windows":
                subprocess.run(["explorer", "/select,", str(path)])
            elif system == "Darwin":  # macOS
                subprocess.run(["open", "-R", str(path)])
            else:  # Linux
                subprocess.run(["xdg-open", str(path.parent)])
        except Exception as e:
            RobustLogger().exception(f"Failed to show in explorer: {e}")

    def _copy_path_to_clipboard(self, resource: FileResource):
        """Copy resource path to clipboard."""
        source = resource.source()
        if source:
            clipboard = QApplication.clipboard()
            if clipboard:
                clipboard.setText(str(source))
                self._update_status_bar("Path copied to clipboard")

    def _add_to_favorites(self, resource: FileResource):
        """Add resource to favorites."""
        if not hasattr(self.settings, 'favorites'):
            self.settings.favorites = []
        
        resource_id = f"{resource.resname()}.{resource.restype().extension}"
        if resource_id not in self.settings.favorites:
            self.settings.favorites.append(resource_id)
            self._update_status_bar(f"Added {resource_id} to favorites")

    def _toggle_bookmark(self):
        """Toggle bookmark for current selection."""
        resources = self._get_selected_resources()
        if len(resources) == 1:
            self._add_to_favorites(resources[0])

    def _show_bookmarks(self):
        """Show bookmarks/favorites dialog with management."""
        from qtpy.QtWidgets import QDialog, QVBoxLayout, QListWidget, QPushButton, QHBoxLayout
        from qtpy.QtCore import Qt
        
        dialog = QDialog(self)
        dialog.setWindowTitle(tr("Favorites"))
        dialog.setWindowFlags(dialog.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        dialog.resize(500, 400)
        
        layout = QVBoxLayout(dialog)
        
        # Favorites list
        favorites_list = QListWidget()
        layout.addWidget(favorites_list)
        
        # Load favorites from settings
        if not hasattr(self.settings, 'favorites'):
            self.settings.favorites = []
        
        for favorite in self.settings.favorites:
            favorites_list.addItem(favorite)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        goto_button = QPushButton(tr("Go To"))
        remove_button = QPushButton(tr("Remove"))
        clear_button = QPushButton(tr("Clear All"))
        close_button = QPushButton(tr("Close"))
        
        button_layout.addWidget(goto_button)
        button_layout.addWidget(remove_button)
        button_layout.addWidget(clear_button)
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
        
        # Button actions
        def goto_favorite():
            current_item = favorites_list.currentItem()
            if current_item:
                favorite_id = current_item.text()
                if self._navigate_to_resource(favorite_id):
                    self._update_status_bar(trf("Navigated to: {resource}", resource=favorite_id))
                    dialog.accept()
                else:
                    self._update_status_bar(trf("Could not find favorite: {resource}", resource=favorite_id))
        
        def remove_favorite():
            current_row = favorites_list.currentRow()
            if current_row >= 0:
                item = favorites_list.takeItem(current_row)
                self.settings.favorites.remove(item.text())
        
        def clear_all():
            favorites_list.clear()
            self.settings.favorites.clear()
        
        goto_button.clicked.connect(goto_favorite)
        remove_button.clicked.connect(remove_favorite)
        clear_button.clicked.connect(clear_all)
        close_button.clicked.connect(dialog.accept)
        
        # Double-click to go to favorite
        favorites_list.itemDoubleClicked.connect(goto_favorite)
        
        dialog.exec_()

    def _show_dependencies(self, resource: FileResource):
        """Show dependencies for a resource."""
        from qtpy.QtWidgets import QDialog, QVBoxLayout, QTreeWidget, QTreeWidgetItem, QPushButton, QHBoxLayout
        from qtpy.QtCore import Qt

        dialog = QDialog(self)
        dialog.setWindowTitle(trf("Dependencies: {name}", name=resource.resname()))
        dialog.setWindowFlags(dialog.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        dialog.resize(600, 450)

        layout = QVBoxLayout(dialog)

        tree = QTreeWidget()
        tree.setHeaderLabels([tr("Dependency"), tr("Type")])
        layout.addWidget(tree)

        root_label = f"{resource.resname()}.{resource.restype().extension}"
        root_item = QTreeWidgetItem([root_label, tr("Resource")])
        tree.addTopLevelItem(root_item)

        dependencies_found = False
        restype = resource.restype()

        if restype in {ResourceType.MDL, ResourceType.MDX}:
            data = resource.data()
            if data:
                from pykotor.tools.model import iterate_textures, iterate_lightmaps

                textures = sorted(set(iterate_textures(data)))
                lightmaps = sorted(set(iterate_lightmaps(data)))

                if textures:
                    dependencies_found = True
                    tex_item = QTreeWidgetItem([tr("Textures"), tr("Category")])
                    for tex in textures:
                        tex_child = QTreeWidgetItem([tex, tr("Texture")])
                        tex_item.addChild(tex_child)
                    root_item.addChild(tex_item)

                if lightmaps:
                    dependencies_found = True
                    lm_item = QTreeWidgetItem([tr("Lightmaps"), tr("Category")])
                    for lm in lightmaps:
                        lm_child = QTreeWidgetItem([lm, tr("Lightmap")])
                        lm_item.addChild(lm_child)
                    root_item.addChild(lm_item)

        if not dependencies_found:
            QTreeWidgetItem([tr("No dependencies found"), tr("Info")], root_item)

        tree.expandAll()

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        close_button = QPushButton(tr("Close"))
        close_button.clicked.connect(dialog.accept)
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)

        dialog.exec_()

    def _find_references(self, resource: FileResource):
        """Find references to a resource."""
        if self.active is None:
            QMessageBox.warning(
                self,
                tr("Find References"),
                tr("Please select an installation first.")
            )
            return

        from qtpy.QtWidgets import QDialog
        from toolset.gui.dialogs.async_loader import AsyncLoader
        from toolset.gui.dialogs.reference_search_options import ReferenceSearchOptions
        from toolset.gui.dialogs.search import FileResults
        from toolset.utils.window import add_window
        from pykotor.tools.reference_finder import find_resref_references, ReferenceSearchResult

        resref = resource.resname()

        options_dialog = ReferenceSearchOptions(self)
        if options_dialog.exec() != QDialog.DialogCode.Accepted:
            return

        partial_match = options_dialog.get_partial_match()
        case_sensitive = options_dialog.get_case_sensitive()
        file_pattern = options_dialog.get_file_pattern()
        file_types = options_dialog.get_file_types()

        search_ncs = resource.restype() in {ResourceType.NSS, ResourceType.NCS}

        def search_fn() -> list[ReferenceSearchResult]:
            return find_resref_references(
                self.active,
                resref,
                search_ncs=search_ncs,
                partial_match=partial_match,
                case_sensitive=case_sensitive,
                file_pattern=file_pattern,
                file_types=file_types,
            )

        loader = AsyncLoader(
            self,
            trf("Searching for references to '{name}'...", name=resref),
            search_fn,
            error_title=tr("An unexpected error occurred searching for references."),
            start_immediately=False,
        )
        loader.setModal(False)
        loader.show()

        def handle_search_completed(results_list: list[ReferenceSearchResult]):
            if not results_list:
                QMessageBox(
                    QMessageBox.Icon.Information,
                    tr("No references found"),
                    trf("No references found for '{name}'", name=resref),
                    parent=self,
                ).exec()
                return

            results_dialog = FileResults(self, results_list, self.active)
            results_dialog.show()
            results_dialog.activateWindow()
            results_dialog.setWindowTitle(trf("{count} reference(s) found for '{name}'", count=len(results_list), name=resref))
            add_window(results_dialog)

        loader.optional_finish_hook.connect(handle_search_completed)
        loader.start_worker()
        add_window(loader)

    def _quick_preview(self):
        """Show quick preview of selected asset in popup dialog."""
        resources = self._get_selected_resources()
        if len(resources) != 1:
            return
        
        resource = resources[0]
        
        # Create quick preview dialog
        from qtpy.QtWidgets import QDialog, QVBoxLayout, QLabel
        from qtpy.QtCore import Qt
        
        dialog = QDialog(self)
        dialog.setWindowTitle(trf("Quick Preview: {name}", name=resource.resname()))
        dialog.setWindowFlags(dialog.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        dialog.resize(400, 300)
        
        layout = QVBoxLayout(dialog)
        
        # Asset info
        info_label = QLabel()
        info_text = f"""
<b>Name:</b> {resource.resname()}<br>
<b>Type:</b> {resource.restype().extension.upper()} ({resource.restype().category})<br>
<b>Size:</b> {self._format_size(resource.size())}<br>
<b>Path:</b> {resource.source() or 'N/A'}
"""
        info_label.setText(info_text)
        info_label.setTextFormat(Qt.RichText)
        layout.addWidget(info_label)
        
        # Preview image if available
        if resource.restype().extension.lower() in ('tpc', 'tga'):
            try:
                preview_label = QLabel()
                preview_label.setAlignment(Qt.AlignCenter)
                
                # Load and scale image
                from PIL import Image
                import io
                
                data = resource.data()
                if data:
                    if resource.restype().extension.lower() == 'tpc':
                        from pykotor.resource.formats.tpc import read_tpc, TPCTextureFormat
                        tpc = read_tpc(data)
                        if tpc.convert(TPCTextureFormat.RGB):
                            img = Image.frombytes("RGB", (tpc.width, tpc.height), bytes(tpc.get().data))
                        else:
                            img = Image.frombytes("RGBA", (tpc.width, tpc.height), bytes(tpc.get().data))
                    else:  # TGA
                        img = Image.open(io.BytesIO(data))
                    
                    # Scale to fit dialog
                    img.thumbnail((350, 200), Image.Resampling.LANCZOS)
                    
                    # Convert to QPixmap
                    img_bytes = io.BytesIO()
                    img.save(img_bytes, format='PNG')
                    img_bytes.seek(0)
                    
                    pixmap = QPixmap()
                    pixmap.loadFromData(img_bytes.getvalue())
                    preview_label.setPixmap(pixmap)
                    
                layout.addWidget(preview_label)
            except Exception as e:
                RobustLogger().exception(f"Failed to generate preview: {e}")
        
        dialog.exec_()
    
    def _format_size(self, size_bytes: int) -> str:
        """Format byte size into human-readable string."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"

    def _show_command_palette(self):
        """Show command palette for quick actions (SDK-style)."""
        from qtpy.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QListWidget, QListWidgetItem
        from qtpy.QtCore import Qt
        
        dialog = QDialog(self)
        dialog.setWindowTitle(tr("Command Palette"))
        dialog.setWindowFlags(dialog.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        dialog.resize(600, 400)
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Search input
        search_input = QLineEdit()
        search_input.setPlaceholderText(tr("Type a command..."))
        search_input.setStyleSheet("padding: 8px; font-size: 14px; border: none; border-bottom: 1px solid #ccc;")
        layout.addWidget(search_input)
        
        # Command list
        command_list = QListWidget()
        command_list.setStyleSheet("border: none; font-size: 12px;")
        layout.addWidget(command_list)
        
        # Define all available commands
        commands = [
            ("File: Open Selected", self._open_selected_assets),
            ("File: Open With...", self._open_with_dialog),
            ("File: Save Editor", self._save_current_asset),
            ("File: Extract Selected", self._extract_selected_assets),
            ("File: Duplicate to Override", self._duplicate_selected_assets),
            ("File: Delete Selected", self._delete_selected_assets),
            ("File: New Resource", self._show_new_resource_dialog),
            ("Edit: Copy", self._copy_selected_assets),
            ("Edit: Cut", self._cut_selected_assets),
            ("Edit: Paste", self._paste_assets),
            ("Edit: Rename", self._rename_selected_asset),
            ("View: Refresh", self._refresh_current_installation),
            ("View: Tree Mode", lambda: self.ui.treeViewButton.click()),
            ("View: List Mode", lambda: self.ui.listViewButton.click()),
            ("View: Grid Mode", lambda: self.ui.gridViewButton.click()),
            ("View: Table Mode", lambda: self.ui.tableViewButton.click()),
            ("Search: Focus Search Box", self._focus_search),
            ("Search: Clear Search", lambda: self.ui.searchBox.clear()),
            ("Navigate: Show in Explorer", lambda: self._show_in_explorer(self._get_selected_resources()[0]) if self._get_selected_resources() else None),
            ("Navigate: Copy Path", lambda: self._copy_path_to_clipboard(self._get_selected_resources()[0]) if self._get_selected_resources() else None),
            ("Tools: Show Dependencies", lambda: self._show_dependencies(self._get_selected_resources()[0]) if self._get_selected_resources() else None),
            ("Tools: Find References", lambda: self._find_references(self._get_selected_resources()[0]) if self._get_selected_resources() else None),
            ("Tools: Quick Preview", self._quick_preview),
            ("Tools: Batch Operations", self._show_batch_operations),
            ("Favorites: Add to Favorites", lambda: self._add_to_favorites(self._get_selected_resources()[0]) if self._get_selected_resources() else None),
            ("Favorites: Show Favorites", self._show_bookmarks),
        ]
        
        # Populate initial list
        for cmd_name, cmd_func in commands:
            item = QListWidgetItem(cmd_name)
            item.setData(Qt.UserRole, cmd_func)
            command_list.addItem(item)
        
        # Filter commands on search
        def filter_commands():
            query = search_input.text().lower()
            for i in range(command_list.count()):
                item = command_list.item(i)
                item.setHidden(query not in item.text().lower())
        
        search_input.textChanged.connect(filter_commands)
        
        # Execute command on Enter or double-click
        def execute_command():
            current_item = command_list.currentItem()
            if current_item:
                cmd_func = current_item.data(Qt.UserRole)
                if cmd_func:
                    dialog.accept()
                    try:
                        cmd_func()
                    except Exception as e:
                        RobustLogger().exception(f"Command failed: {e}")
        
        search_input.returnPressed.connect(execute_command)
        command_list.itemDoubleClicked.connect(execute_command)
        
        # Auto-select first visible item when typing
        def auto_select_first():
            for i in range(command_list.count()):
                item = command_list.item(i)
                if not item.isHidden():
                    command_list.setCurrentItem(item)
                    break
        
        search_input.textChanged.connect(auto_select_first)
        
        # Focus search input
        search_input.setFocus()
        
        dialog.exec_()

    def _get_editor_options_for_resource(self, resource: FileResource) -> list[tuple[str, str, bool]]:
        """Get available editor options for a resource type.
        
        Returns:
            List of tuples (editor_name, description, is_specialized)
        """
        restype = resource.restype()
        options = []
        
        # GFF-based resources can use both GFF Editor and specialized editors
        gff_based_types = {
            ResourceType.DLG, ResourceType.UTC, ResourceType.BTC, ResourceType.BIC,
            ResourceType.UTP, ResourceType.BTP, ResourceType.UTD, ResourceType.BTD,
            ResourceType.IFO, ResourceType.UTS, ResourceType.UTT, ResourceType.BTT,
            ResourceType.UTM, ResourceType.BTM, ResourceType.UTW, ResourceType.UTE,
            ResourceType.BTE, ResourceType.UTI, ResourceType.BTI, ResourceType.JRL,
            ResourceType.ARE, ResourceType.GIT, ResourceType.PTH
        }
        
        if restype.target_type() in gff_based_types:
            # These resources have both generic GFF editor and specialized editor
            options.append((tr("Generic GFF Editor"), tr("Universal GFF structure editor"), False))
            
            # Add specialized editor names
            if restype.target_type() is ResourceType.DLG:
                options.append((tr("Dialog Editor"), tr("Specialized conversation editor"), True))
            elif restype.target_type() in {ResourceType.UTC, ResourceType.BTC, ResourceType.BIC}:
                options.append((tr("Creature Editor"), tr("Specialized creature editor"), True))
            elif restype.target_type() in {ResourceType.UTP, ResourceType.BTP}:
                options.append((tr("Placeable Editor"), tr("Specialized placeable editor"), True))
            elif restype.target_type() in {ResourceType.UTD, ResourceType.BTD}:
                options.append((tr("Door Editor"), tr("Specialized door editor"), True))
            elif restype.target_type() is ResourceType.IFO:
                options.append((tr("Module Editor"), tr("Specialized module information editor"), True))
            elif restype.target_type() is ResourceType.UTS:
                options.append((tr("Sound Editor"), tr("Specialized sound editor"), True))
            elif restype.target_type() in {ResourceType.UTT, ResourceType.BTT}:
                options.append((tr("Trigger Editor"), tr("Specialized trigger editor"), True))
            elif restype.target_type() in {ResourceType.UTM, ResourceType.BTM}:
                options.append((tr("Merchant Editor"), tr("Specialized merchant editor"), True))
            elif restype.target_type() is ResourceType.UTW:
                options.append((tr("Waypoint Editor"), tr("Specialized waypoint editor"), True))
            elif restype.target_type() in {ResourceType.UTE, ResourceType.BTE}:
                options.append((tr("Encounter Editor"), tr("Specialized encounter editor"), True))
            elif restype.target_type() in {ResourceType.UTI, ResourceType.BTI}:
                options.append((tr("Item Editor"), tr("Specialized item editor"), True))
            elif restype.target_type() is ResourceType.JRL:
                options.append((tr("Journal Editor"), tr("Specialized journal editor"), True))
            elif restype.target_type() is ResourceType.ARE:
                options.append((tr("Area Editor"), tr("Specialized area editor"), True))
            elif restype.target_type() is ResourceType.GIT:
                options.append((tr("Instance Editor"), tr("Specialized instance editor"), True))
            elif restype.target_type() is ResourceType.PTH:
                options.append((tr("Path Editor"), tr("Specialized path editor"), True))
        
        # Non-GFF resources with single editor
        elif restype.target_type() is ResourceType.TwoDA:
            options.append((tr("2DA Editor"), tr("Table editor for 2DA files"), False))
        elif restype.target_type() is ResourceType.SSF:
            options.append((tr("SSF Editor"), tr("Sound set editor"), False))
        elif restype.target_type() is ResourceType.TLK:
            options.append((tr("TLK Editor"), tr("Talk table editor"), False))
        elif restype.target_type() is ResourceType.LTR:
            options.append((tr("LTR Editor"), tr("Letter combo editor"), False))
        elif restype.target_type() is ResourceType.LIP:
            options.append((tr("LIP Editor"), tr("Lip sync editor"), False))
        elif restype.category == "Walkmeshes":
            options.append((tr("Walkmesh Editor"), tr("BWM walkmesh editor"), False))
        elif restype.category in {"Images", "Textures"} and restype is not ResourceType.TXI:
            options.append((tr("Texture Editor"), tr("Image and texture editor"), False))
        elif restype is ResourceType.NSS:
            options.append((tr("Script Editor"), tr("NWScript source editor"), False))
        elif restype is ResourceType.NCS:
            options.append((tr("Script Editor"), tr("Decompiled NWScript editor"), False))
        elif restype in {ResourceType.MDL, ResourceType.MDX}:
            options.append((tr("Model Editor"), tr("3D model editor"), False))
        elif restype in {ResourceType.ERF, ResourceType.MOD, ResourceType.SAV, ResourceType.RIM}:
            options.append((tr("Archive Editor"), tr("ERF/MOD/RIM archive editor"), False))
        elif restype in {ResourceType.TXT, ResourceType.TXI}:
            options.append((tr("Text Editor"), tr("Plain text editor"), False))
        elif restype is ResourceType.WAV:
            options.append((tr("Audio Player"), tr("WAV audio player"), False))
        
        return options

    def _open_with_dialog(self):
        """Show open with dialog for selected asset."""
        resources = self._get_selected_resources()
        if len(resources) != 1:
            QMessageBox.warning(
                self,
                tr("Open With"),
                tr("Please select exactly one asset.")
            )
            return
        
        resource = resources[0]
        options = self._get_editor_options_for_resource(resource)
        
        if not options:
            QMessageBox.information(
                self,
                tr("Open With"),
                tr("No editors available for this resource type.")
            )
            return
        
        # Create dialog
        from qtpy.QtWidgets import QDialog, QVBoxLayout, QLabel, QListWidget, QPushButton, QHBoxLayout, QListWidgetItem
        from qtpy.QtCore import Qt
        
        dialog = QDialog(self)
        dialog.setWindowTitle(tr("Open With"))
        dialog.setWindowFlags(dialog.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        dialog.resize(500, 300)
        
        layout = QVBoxLayout(dialog)
        
        # Resource info
        resource_label = QLabel(trf("Select editor for: {name}.{ext}", 
                                    name=resource.resname(), 
                                    ext=resource.restype().extension))
        layout.addWidget(resource_label)
        
        # Editor list
        editor_list = QListWidget()
        for editor_name, description, is_specialized in options:
            item = QListWidgetItem(f"{editor_name}\n{description}")
            item.setData(Qt.ItemDataRole.UserRole, is_specialized)
            editor_list.addItem(item)
        
        if editor_list.count() > 0:
            editor_list.setCurrentRow(0)
        
        layout.addWidget(editor_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        open_button = QPushButton(tr("Open"))
        cancel_button = QPushButton(tr("Cancel"))
        
        button_layout.addWidget(open_button)
        button_layout.addStretch()
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        
        # Button actions
        def open_selected():
            current_row = editor_list.currentRow()
            if current_row >= 0:
                _, _, is_specialized = options[current_row]
                
                # Open with the selected editor option
                try:
                    if not self.active:
                        QMessageBox.warning(
                            self,
                            tr("No Installation"),
                            tr("Please select an installation first.")
                        )
                        return
                    
                    # Use the global open_resource_editor with gff_specialized flag
                    from toolset.utils.window import open_resource_editor
                    open_resource_editor(resource, self.active, self, gff_specialized=is_specialized)
                    
                    self._update_status_bar(trf("Opened {name} in editor", name=resource.resname()))
                    dialog.accept()
                    
                except Exception as e:
                    from loggerplus import RobustLogger
                    RobustLogger().exception(f"Failed to open resource in editor: {e}")
                    QMessageBox.critical(
                        self,
                        tr("Open Error"),
                        trf("Failed to open resource: {error}", error=str(e))
                    )
        
        open_button.clicked.connect(open_selected)
        cancel_button.clicked.connect(dialog.reject)
        editor_list.itemDoubleClicked.connect(open_selected)
        
        dialog.exec_()

    def _show_installation_properties(self, item: InstallationItem):
        """Show properties dialog for installation with detailed info."""
        from qtpy.QtWidgets import QDialog, QVBoxLayout, QLabel, QTabWidget, QWidget, QFormLayout, QPushButton, QHBoxLayout, QTextEdit
        from qtpy.QtCore import Qt
        
        dialog = QDialog(self)
        dialog.setWindowTitle(trf("Properties: {name}", name=item.name))
        dialog.setWindowFlags(dialog.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        dialog.resize(600, 500)
        
        layout = QVBoxLayout(dialog)
        
        # Tabs for different property categories
        tabs = QTabWidget()
        layout.addWidget(tabs)
        
        # General tab
        general_tab = QWidget()
        general_layout = QFormLayout(general_tab)
        
        general_layout.addRow(tr("Name:"), QLabel(item.name))
        general_layout.addRow(tr("Path:"), QLabel(str(item.path)))
        general_layout.addRow(tr("Game:"), QLabel("Star Wars: Knights of the Old Republic II - The Sith Lords" if item.tsl else "Star Wars: Knights of the Old Republic"))
        
        # Calculate total files
        total_files = 0
        for category in ['Core', 'Modules', 'Override', 'Textures', 'Saves']:
            if hasattr(item.installation, category.lower()):
                location = getattr(item.installation, category.lower())()
                if location:
                    total_files += len(list(location))
        
        general_layout.addRow(tr("Total Files:"), QLabel(str(total_files)))
        general_layout.addRow(tr("Active:"), QLabel(tr("Yes") if self.active == item.installation else tr("No")))
        
        tabs.addTab(general_tab, tr("General"))
        
        # Paths tab
        paths_tab = QWidget()
        paths_layout = QFormLayout(paths_tab)
        
        if hasattr(item.installation, 'core'):
            paths_layout.addRow(tr("Core:"), QLabel(str(item.installation.core().path()) if item.installation.core() else tr("N/A")))
        if hasattr(item.installation, 'modules'):
            paths_layout.addRow(tr("Modules:"), QLabel(str(item.installation.modules().path()) if item.installation.modules() else tr("N/A")))
        if hasattr(item.installation, 'override'):
            paths_layout.addRow(tr("Override:"), QLabel(str(item.installation.override().path()) if item.installation.override() else tr("N/A")))
        if hasattr(item.installation, 'texturepacks'):
            paths_layout.addRow(tr("Textures:"), QLabel(str(item.installation.texturepacks().path()) if item.installation.texturepacks() else tr("N/A")))
        if hasattr(item.installation, 'saves'):
            paths_layout.addRow(tr("Saves:"), QLabel(str(item.installation.saves().path()) if item.installation.saves() else tr("N/A")))
        
        tabs.addTab(paths_tab, tr("Paths"))
        
        # Statistics tab
        stats_tab = QWidget()
        stats_layout = QFormLayout(stats_tab)
        
        # Calculate file counts per category
        for category in ['Core', 'Modules', 'Override', 'Textures', 'Saves']:
            if hasattr(item.installation, category.lower()):
                location = getattr(item.installation, category.lower())()
                if location:
                    count = len(list(location))
                    stats_layout.addRow(trf("{category} Files:", category=category), QLabel(str(count)))
        
        tabs.addTab(stats_tab, tr("Statistics"))
        
        # Info tab
        info_tab = QWidget()
        info_layout = QVBoxLayout(info_tab)
        
        info_text = QTextEdit()
        info_text.setReadOnly(True)
        info_text.setPlainText(
            f"Installation: {item.name}\\n"
            f"Path: {item.path}\\n"
            f"Game: {'TSL' if item.tsl else 'K1'}\\n"
            f"\\nThis installation contains game resources from the specified path.\\n"
            f"You can browse, extract, and modify these resources using the toolset."
        )
        info_layout.addWidget(info_text)
        
        tabs.addTab(info_tab, tr("Info"))
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        close_button = QPushButton(tr("Close"))
        close_button.clicked.connect(dialog.accept)
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
        
        dialog.exec_()

    def _show_batch_operations(self):
        """Show batch operations dialog for processing multiple assets."""
        from qtpy.QtWidgets import (
            QDialog, QVBoxLayout, QLabel, QListWidget, QPushButton, 
            QHBoxLayout, QComboBox, QProgressDialog
        )
        from qtpy.QtCore import Qt
        
        resources = self._get_selected_resources()
        if not resources:
            QMessageBox.warning(
                self,
                tr("Batch Operations"),
                tr("No assets selected. Please select one or more assets to perform batch operations.")
            )
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle(trf("Batch Operations ({count} assets)", count=len(resources)))
        dialog.setWindowFlags(dialog.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        dialog.resize(600, 400)
        
        layout = QVBoxLayout(dialog)
        
        # Operation selection
        operation_label = QLabel(tr("Select Operation:"))
        layout.addWidget(operation_label)
        
        operation_combo = QComboBox()
        operation_combo.addItems([
            tr("Extract All"),
            tr("Duplicate All to Override"),
            tr("Delete All"),
            tr("Rename with Pattern"),
            tr("Convert Format"),
            tr("Export to Directory"),
        ])
        layout.addWidget(operation_combo)
        
        # Asset list
        asset_list_label = QLabel(tr("Selected Assets:"))
        layout.addWidget(asset_list_label)
        
        asset_list = QListWidget()
        for resource in resources:
            asset_list.addItem(f"{resource.resname()}.{resource.restype().extension}")
        layout.addWidget(asset_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        execute_button = QPushButton(tr("Execute"))
        cancel_button = QPushButton(tr("Cancel"))
        
        button_layout.addWidget(execute_button)
        button_layout.addStretch()
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        
        # Execute batch operation
        def execute_batch():
            operation = operation_combo.currentText()
            success_count = 0
            fail_count = 0
            skipped_count = 0
            dest_path = None
            
            # For Extract All, ask for destination directory upfront
            if tr("Extract All") in operation:
                dest_dir = QFileDialog.getExistingDirectory(
                    self,
                    tr("Select Extraction Destination"),
                    str(Path.home()),
                    QFileDialog.Option.ShowDirsOnly
                )
                if not dest_dir:
                    return
                dest_path = Path(dest_dir)
            
            # For Delete All, ask for confirmation upfront
            if tr("Delete All") in operation:
                reply = QMessageBox.question(
                    self,
                    tr("Delete Assets"),
                    trf("Are you sure you want to delete {count} asset(s)?", count=len(resources)),
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                if reply != QMessageBox.StandardButton.Yes:
                    return
            
            # For Rename with Pattern, show pattern dialog
            find_pattern = None
            replace_pattern = None
            rename_pairs = []
            if tr("Rename with Pattern") in operation:
                from qtpy.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QFormLayout
                pattern_dialog = QDialog(self)
                pattern_dialog.setWindowTitle(tr("Rename Pattern"))
                pattern_dialog.setWindowFlags(pattern_dialog.windowFlags() & ~Qt.WindowContextHelpButtonHint)
                pattern_dialog.resize(500, 200)
                
                pattern_layout = QVBoxLayout(pattern_dialog)
                form_layout = QFormLayout()
                
                find_input = QLineEdit()
                find_input.setPlaceholderText("e.g., old_*.tpc")
                replace_input = QLineEdit()
                replace_input.setPlaceholderText("e.g., new_*.tpc")
                
                form_layout.addRow(tr("Find pattern (use * for wildcard):"), find_input)
                form_layout.addRow(tr("Replace pattern (use * for match):"), replace_input)
                pattern_layout.addLayout(form_layout)
                
                preview_label = QLabel(tr("Preview: (enter patterns to see preview)"))
                pattern_layout.addWidget(preview_label)
                
                button_layout = QHBoxLayout()
                ok_button = QPushButton(tr("OK"))
                cancel_button = QPushButton(tr("Cancel"))
                button_layout.addWidget(ok_button)
                button_layout.addWidget(cancel_button)
                pattern_layout.addLayout(button_layout)
                
                ok_button.clicked.connect(pattern_dialog.accept)
                cancel_button.clicked.connect(pattern_dialog.reject)
                
                # Update preview on text change
                def update_preview():
                    find = find_input.text()
                    replace = replace_input.text()
                    if find and replace:
                        import re
                        import fnmatch
                        pattern_regex = fnmatch.translate(find)
                        matches = 0
                        for res in resources:
                            resname = res.resname()
                            if re.match(pattern_regex, resname):
                                matches += 1
                        preview_label.setText(trf("Preview: {count} file(s) will be renamed", count=matches))
                    else:
                        preview_label.setText(tr("Preview: (enter patterns to see preview)"))
                
                find_input.textChanged.connect(update_preview)
                replace_input.textChanged.connect(update_preview)
                
                if pattern_dialog.exec_() != QDialog.DialogCode.Accepted:
                    return
                
                find_pattern = find_input.text()
                replace_pattern = replace_input.text()
                
                if not find_pattern or not replace_pattern:
                    QMessageBox.warning(self, tr("Invalid Pattern"), tr("Both find and replace patterns are required."))
                    return
                
                # Build rename pairs
                import re
                import fnmatch
                pattern_regex = fnmatch.translate(find_pattern)
                for resource in resources:
                    resname = resource.resname()
                    match = re.match(pattern_regex, resname)
                    if match:
                        # Extract the wildcard content
                        if '*' in find_pattern:
                            wildcard_content = resname[find_pattern.index('*'):len(resname)-len(find_pattern)+find_pattern.index('*')+1]
                            new_name = replace_pattern.replace('*', wildcard_content, 1)
                        else:
                            new_name = replace_pattern
                        rename_pairs.append((resource, new_name))
                
                if not rename_pairs:
                    QMessageBox.information(self, tr("No Matches"), tr("No files match the pattern."))
                    return
                
                # Validate no collisions in new names
                new_names = [pair[1] for pair in rename_pairs]
                if len(new_names) != len(set(new_names)):
                    QMessageBox.warning(self, tr("Collision Detected"), tr("Pattern would create duplicate names."))
                    return
            
            # Create progress dialog
            progress = QProgressDialog(
                trf("Processing {count} assets...", count=len(resources)),
                tr("Cancel"),
                0,
                len(resources),
                self
            )
            progress.setWindowModality(Qt.WindowModal)
            progress.setWindowTitle(tr("Batch Operation"))
            
            try:
                override_path = None
                if tr("Duplicate All to Override") in operation:
                    if not self.active:
                        QMessageBox.warning(self, tr("No Installation"), tr("Please select an installation first."))
                        return
                    override_path = self.active.override_path()
                    if not override_path.exists():
                        override_path.mkdir(parents=True, exist_ok=True)
                
                for i, resource in enumerate(resources):
                    if progress.wasCanceled():
                        break
                    
                    progress.setValue(i)
                    progress.setLabelText(
                        trf("Processing {name} ({current}/{total})",
                            name=resource.resname(),
                            current=i + 1,
                            total=len(resources))
                    )
                    
                    # Execute operation based on selection
                    if tr("Extract All") in operation:
                        try:
                            filename = f"{resource.resname()}.{resource.restype().extension}"
                            output_path = dest_path / filename
                            data = resource.data()
                            if data:
                                output_path.write_bytes(data)
                                success_count += 1
                            else:
                                fail_count += 1
                        except Exception as e:
                            fail_count += 1
                            RobustLogger().exception(f"Failed to extract {resource.resname()}: {e}")
                    
                    elif tr("Duplicate All to Override") in operation:
                        try:
                            data = resource.data()
                            if not data:
                                fail_count += 1
                                continue
                            
                            filename = f"{resource.resname()}.{resource.restype().extension}"
                            target_path = override_path / filename
                            
                            if target_path.exists():
                                # Skip existing files in batch mode
                                skipped_count += 1
                                continue
                            
                            target_path.write_bytes(data)
                            success_count += 1
                        except Exception as e:
                            fail_count += 1
                            RobustLogger().exception(f"Failed to duplicate {resource.resname()}: {e}")
                    
                    elif tr("Delete All") in operation:
                        try:
                            source = resource.source()
                            if not source:
                                skipped_count += 1
                                continue
                            
                            source_path = Path(source)
                            
                            # Only delete from Override folder
                            if not self.active:
                                skipped_count += 1
                                continue
                            
                            override_path_check = self.active.override_path()
                            try:
                                source_path.relative_to(override_path_check)
                                source_path.unlink()
                                success_count += 1
                            except ValueError:
                                skipped_count += 1
                        except Exception as e:
                            fail_count += 1
                            RobustLogger().exception(f"Failed to delete {resource.resname()}: {e}")
                    
                    elif tr("Rename with Pattern") in operation:
                        # Find this resource in rename_pairs
                        for res, new_name in rename_pairs:
                            if res == resource:
                                try:
                                    source = resource.source()
                                    if not source:
                                        skipped_count += 1
                                        break
                                    
                                    source_path = Path(source)
                                    
                                    # Only rename in Override folder
                                    if not self.active:
                                        skipped_count += 1
                                        break
                                    
                                    override_path_check = self.active.override_path()
                                    try:
                                        source_path.relative_to(override_path_check)
                                    except ValueError:
                                        skipped_count += 1
                                        break
                                    
                                    # Build new path
                                    extension = resource.restype().extension
                                    if not new_name.endswith(f".{extension}"):
                                        new_name_full = f"{new_name}.{extension}"
                                    else:
                                        new_name_full = new_name
                                    
                                    new_path = source_path.parent / new_name_full
                                    
                                    # Check for collision
                                    if new_path.exists() and new_path.resolve() != source_path.resolve():
                                        skipped_count += 1
                                        break
                                    
                                    # Execute rename
                                    import shutil
                                    shutil.move(str(source_path), str(new_path))
                                    success_count += 1
                                    
                                except Exception as e:
                                    fail_count += 1
                                    RobustLogger().exception(f"Failed to rename {resource.resname()}: {e}")
                                break
                    
                    # Process UI events to keep dialog responsive
                    QApplication.processEvents()
                
                progress.setValue(len(resources))
                
                # Refresh installation if any operations succeeded
                if success_count > 0 and (tr("Duplicate All to Override") in operation or tr("Delete All") in operation or tr("Rename with Pattern") in operation):
                    self._refresh_current_installation()
                
                # Show results
                if not progress.wasCanceled():
                    message_parts = []
                    if success_count > 0:
                        message_parts.append(trf("Success: {count}", count=success_count))
                    if fail_count > 0:
                        message_parts.append(trf("Failed: {count}", count=fail_count))
                    if skipped_count > 0:
                        message_parts.append(trf("Skipped: {count}", count=skipped_count))
                    
                    result_message = ", ".join(message_parts) if message_parts else tr("No operations performed")
                    
                    QMessageBox.information(
                        self,
                        tr("Batch Operation Complete"),
                        result_message
                    )
                    dialog.accept()
                
            except Exception as e:
                RobustLogger().exception(f"Batch operation failed: {e}")
                QMessageBox.critical(
                    self,
                    tr("Batch Operation Failed"),
                    trf("Error: {error}", error=str(e))
                )
        
        execute_button.clicked.connect(execute_batch)
        cancel_button.clicked.connect(dialog.reject)
        
        dialog.exec_()

    def _update_status_bar(self, message: str | None = None):
        """Update status bar with current state."""
        if not hasattr(self, '_status_label'):
            return
        
        if message:
            self._status_label.setText(message)
        
        # Update selection count
        resources = self._get_selected_resources()
        if resources:
            count_text = trf("{count} item(s) selected", count=len(resources))
            
            # Add favorite indicator if single resource is selected and is in favorites
            if len(resources) == 1:
                if not hasattr(self.settings, 'favorites'):
                    self.settings.favorites = []
                
                resource = resources[0]
                resource_id = f"{resource.resname()}.{resource.restype().extension}"
                if resource_id in self.settings.favorites:
                    count_text += " ★"  # Add star indicator
            
            self._selection_label.setText(count_text)
        else:
            self._selection_label.setText(tr("No selection"))

    def _get_drop_target_dir(self, view: QAbstractItemView, pos: QPoint | None) -> Path | None:
        """Resolve the target directory for a drop operation."""
        if pos is not None:
            index = view.indexAt(pos)
            if index.isValid():
                source_index = self._map_to_source_index(index)
                item = self.fs_model.itemFromIndex(source_index)
                if isinstance(item, ResourceItem):
                    item = item.parent
                if isinstance(item, (DirItem, CategoryItem, InstallationItem)):
                    return Path(item.path)

        if self.active and self.active.override():
            return Path(self.active.override().path())
        return None

    def _import_external_files(self, urls: list[QtCore.QUrl], target_dir: Path | None) -> bool:
        """Import external files into the target directory."""
        if target_dir is None or not target_dir.exists():
            return False

        import shutil

        def unique_target(path: Path) -> Path:
            if not path.exists():
                return path
            stem = path.stem
            suffix = path.suffix
            counter = 1
            while True:
                candidate = path.with_name(f"{stem}_{counter}{suffix}")
                if not candidate.exists():
                    return candidate
                counter += 1

        imported_any = False
        for url in urls:
            src = Path(url.toLocalFile())
            if not src.exists():
                continue

            if src.is_dir():
                dst = unique_target(target_dir / src.name)
                shutil.copytree(src, dst, dirs_exist_ok=True)
                imported_any = True
            else:
                dst = unique_target(target_dir / src.name)
                shutil.copy2(src, dst)
                imported_any = True

        if imported_any:
            self._update_status_bar(trf("Imported files to {path}", path=str(target_dir)))
            self._refresh_current_installation()
        return imported_any

    # ========== File System Watcher ==========

    def _setup_file_watcher(self, installation: HTInstallation):
        """Set up file system watcher for an installation."""
        # Clear existing watches
        watched_paths = self._file_watcher.directories() + self._file_watcher.files()
        if watched_paths:
            self._file_watcher.removePaths(watched_paths)
        
        # Watch modules and override directories
        modules_path = installation.module_path()
        override_path = installation.override_path()
        
        paths_to_watch = []
        if modules_path.exists():
            paths_to_watch.append(str(modules_path))
        if override_path.exists():
            paths_to_watch.append(str(override_path))
        
        if paths_to_watch:
            self._file_watcher.addPaths(paths_to_watch)
            self._file_watcher.directoryChanged.connect(self._on_directory_changed)

    def _on_directory_changed(self, path: str):
        """Handle directory change event."""
        # Debounce changes
        path_obj = Path(path)
        
        if not self.active:
            return
        
        # Determine which category changed
        if path_obj == self.active.module_path():
            category = "modules"
        elif path_obj == self.active.override_path():
            category = "override"
        else:
            return
        
        # Add to pending changes
        if path not in self._pending_changes[category]:
            self._pending_changes[category].append(path)
        
        # Restart debounce timer
        self._watcher_debounce_timer.start()

    def _process_pending_file_changes(self):
        """Process pending file system changes."""
        if not self.active:
            return
        
        # Check if there are any pending changes
        has_changes = any(self._pending_changes.values())
        if not has_changes:
            return
        
        # Refresh the affected categories
        for category, paths in self._pending_changes.items():
            if paths:
                RobustLogger().debug(f"Processing file changes in {category}: {len(paths)} path(s)")
        
        # Clear pending changes
        self._pending_changes = {"modules": [], "override": []}
        
        # Refresh the current installation
        self._refresh_current_installation()

    # ========== Events ==========

    def showEvent(self, event: QShowEvent | None = None):
        """Called when the window is shown."""
        super().showEvent(event)

    def closeEvent(self, e: QCloseEvent | None):
        """Called when the window is closed."""
        instance = QCoreApplication.instance()
        if instance is None:
            sys.exit()
        else:
            instance.quit()

    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle mouse move events."""
        if event.buttons() == Qt.MouseButton.LeftButton:
            if self._mouse_move_pos is None:
                return
            globalPos = (
                event.globalPos()
                if qtpy.QT5
                else event.globalPosition().toPoint()
            )
            self.move(self.mapFromGlobal(self.mapToGlobal(self.pos()) + (globalPos - self._mouse_move_pos)))
            self._mouse_move_pos = globalPos

    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press events."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._mouse_move_pos = (
                event.globalPos()
                if qtpy.QT5
                else event.globalPosition().toPoint()
            )

    def mouseReleaseEvent(self, event: QMouseEvent):
        """Handle mouse release events."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._mouse_move_pos = None

    def keyPressEvent(self, event: QKeyEvent):
        """Handle key press events."""
        super().keyPressEvent(event)

    def eventFilter(self, obj: QObject, event: QtCore.QEvent) -> bool:
        """Handle drag-and-drop events for asset views."""
        views = {
            self.ui.assetTreeView,
            self.ui.assetListView,
            self.ui.assetGridView,
            self.ui.assetTableView,
        }

        view = None
        for candidate in views:
            if obj is candidate or obj is candidate.viewport():
                view = candidate
                break

        if view is not None:
            if event.type() == QtCore.QEvent.Type.DragEnter:
                drag_event = cast(QDragEnterEvent, event)
                mime_data = drag_event.mimeData()
                if mime_data and mime_data.hasUrls():
                    pos = getattr(drag_event, "position", None)
                    point = pos.toPoint() if pos is not None else drag_event.pos()
                    target_dir = self._get_drop_target_dir(view, point)
                    if target_dir is not None:
                        drag_event.acceptProposedAction()
                        return True

            if event.type() == QtCore.QEvent.Type.Drop:
                drop_event = cast(QDropEvent, event)
                mime_data = drop_event.mimeData()
                if mime_data and mime_data.hasUrls():
                    pos = getattr(drop_event, "position", None)
                    point = pos.toPoint() if pos is not None else drop_event.pos()
                    target_dir = self._get_drop_target_dir(view, point)
                    if self._import_external_files(mime_data.urls(), target_dir):
                        drop_event.acceptProposedAction()
                        return True

        return super().eventFilter(obj, event)

    def dragEnterEvent(self, e: QDragEnterEvent | None):
        """Handle drag enter events."""
        if e is None:
            return
        
        mime_data = e.mimeData()
        if mime_data and mime_data.hasUrls():
            e.acceptProposedAction()

    def dropEvent(self, e: QDropEvent | None):
        """Handle drop events."""
        if e is None:
            return

        mime_data = e.mimeData()
        if not mime_data or not mime_data.hasUrls():
            return

        target_dir = self._get_drop_target_dir(self.ui.assetTreeView, None)
        if self._import_external_files(mime_data.urls(), target_dir):
            e.acceptProposedAction()
