#!/usr/bin/env python3
"""Shared discovery helpers for Python tools under Tools/."""

from __future__ import annotations

import argparse
import json
import re

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    import tomllib
except ImportError:
    try:
        import tomli as tomllib  # type: ignore[import-not-found,no-redef]
    except ImportError as exc:  # pragma: no cover - environment guard
        raise SystemExit("tomllib (or tomli on Python <3.11) is required") from exc


LIBRARY_SOURCE_PATHS = [
    "Libraries/PyKotor/src",
    "Libraries/bioware-kaitai-formats/src",
]
LIBRARY_TEST_PATHS = [
    "Libraries/PyKotor/tests",
]
VERSION_KEY_PATTERNS = {
    '"currentVersion":': "currentVersion",
    "CURRENT_VERSION =": "CURRENT_VERSION",
    "__version__ =": "__version__",
}


def _strip_py_suffix(path_str: str) -> str:
    s = str(path_str)
    return s[:-3] if s.endswith(".py") else s


@dataclass(frozen=True)
class ToolMetadata:
    directory: str
    relative_path: str
    project_name: str
    build_name: str
    package_name: str
    entrypoint: str
    module_name: str
    src_path: str
    tests_path: Optional[str]
    requirements_path: Optional[str]
    requires_qt: bool
    qt_api: Optional[str]
    console: Optional[bool]
    windowed: Optional[bool]
    version_file: Optional[str]
    version_key: Optional[str]
    release_tag_suffix: Optional[str]
    script_names: List[str]
    min_python: str
    validate_py38: bool

    @property
    def is_cli(self) -> bool:
        return not bool(self.windowed) or bool(self.console)

    def to_dict(self) -> Dict[str, Any]:
        payload = asdict(self)
        payload["is_cli"] = self.is_cli
        return payload


def read_pyproject(pyproject_path: Path) -> Dict[str, Any]:
    if not pyproject_path.exists():
        return {}
    with pyproject_path.open("rb") as handle:
        return tomllib.load(handle)


def _module_target_to_entrypoint(module_target: str) -> str:
    module_name = module_target.split(":", 1)[0]
    return module_name.replace(".", "/") + ".py"


def _entrypoint_from_scripts(project_table: Dict[str, Any]) -> Tuple[Optional[str], List[str]]:
    scripts = project_table.get("scripts", {})
    if not scripts:
        return None, []
    script_names = sorted(str(name) for name in scripts)
    first_target = scripts[script_names[0]]
    return _module_target_to_entrypoint(str(first_target)), script_names


def _discover_entrypoint(src_dir: Path) -> Optional[str]:
    for candidate in sorted(src_dir.rglob("__main__.py")):
        return candidate.relative_to(src_dir).as_posix()
    return None


def _detect_qt(
    project_table: Dict[str, Any], tool_table: Dict[str, Any]
) -> Tuple[bool, Optional[str]]:
    qt_api: Optional[str] = None
    requires_qt = False
    for dependency in project_table.get("dependencies", []):
        dep_lower = str(dependency).lower()
        if "pyqt5" in dep_lower:
            requires_qt = True
            qt_api = qt_api or "PyQt5"
        elif "pyqt6" in dep_lower:
            requires_qt = True
            qt_api = qt_api or "PyQt6"
        elif "pyside2" in dep_lower:
            requires_qt = True
            qt_api = qt_api or "PySide2"
        elif "pyside6" in dep_lower:
            requires_qt = True
            qt_api = qt_api or "PySide6"
        elif "qtpy" in dep_lower:
            requires_qt = True

    dep_table = tool_table.get("dependencies", {})
    configured_qt = dep_table.get("qt-api")
    if configured_qt:
        requires_qt = True
        qt_api = str(configured_qt)

    pyinstaller_table = tool_table.get("pyinstaller", {})
    pyinstaller_qt = pyinstaller_table.get("qt-api")
    if pyinstaller_qt:
        requires_qt = True
        qt_api = str(pyinstaller_qt)

    return requires_qt, qt_api


def _discover_package_name(entrypoint: str, src_dir: Path) -> str:
    entry_path = Path(entrypoint)
    if len(entry_path.parts) > 1:
        return entry_path.parts[0]

    for package_dir in sorted(src_dir.iterdir()):
        if package_dir.is_dir() and (package_dir / "__init__.py").exists():
            return package_dir.name
    raise ValueError(f"Unable to infer package name from src directory: {src_dir}")


def _infer_version_info(
    tool_root: Path,
    package_name: str,
    tool_config: Dict[str, Any],
) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    custom = tool_config.get("pykotor-tool", {})
    version_file = custom.get("version-file")
    version_key = custom.get("version-key")
    tag_suffix = custom.get("release-tag-suffix")

    if version_file and version_key:
        return str(version_file), str(version_key), str(tag_suffix) if tag_suffix else None

    candidate_paths = [
        tool_root / "src" / package_name / "config" / "config_info.py",
        tool_root / "src" / package_name / "config.py",
        tool_root / "src" / package_name / "__main__.py",
        tool_root / "src" / package_name / "__init__.py",
    ]
    for candidate in candidate_paths:
        if not candidate.exists():
            continue
        text = candidate.read_text(encoding="utf-8")
        for pattern, inferred_key in VERSION_KEY_PATTERNS.items():
            if pattern in text:
                relative = candidate.relative_to(tool_root).as_posix()
                return relative, inferred_key, str(tag_suffix) if tag_suffix else None

    return None, None, str(tag_suffix) if tag_suffix else None


def _parse_min_python(requires_python: Optional[str]) -> Tuple[int, int]:
    if not requires_python:
        return (3, 8)
    match = re.search(r">=\s*(\d+)\.(\d+)", requires_python)
    if match:
        return (int(match.group(1)), int(match.group(2)))
    return (3, 8)


def _validate_py38(min_python: Tuple[int, int]) -> bool:
    return min_python <= (3, 8)


def discover_tools(repo_root: Optional[Path] = None) -> List[ToolMetadata]:
    repo_root = repo_root or Path(__file__).resolve().parent
    tools_dir = repo_root / "Tools"
    if not tools_dir.exists():
        return []

    discovered: List[ToolMetadata] = []
    for tool_root in sorted(path for path in tools_dir.iterdir() if path.is_dir()):
        if tool_root.name.startswith("."):
            continue

        pyproject = read_pyproject(tool_root / "pyproject.toml")
        src_dir = tool_root / "src"
        if not pyproject or not src_dir.exists():
            continue

        project_table = pyproject.get("project", {})
        tool_table = pyproject.get("tool", {})
        pyinstaller_table = tool_table.get("pyinstaller", {})
        entrypoint = pyinstaller_table.get("entrypoint")
        script_names: List[str] = []
        if not entrypoint:
            entrypoint, script_names = _entrypoint_from_scripts(project_table)
        if not entrypoint:
            entrypoint = _discover_entrypoint(src_dir)
        if not entrypoint:
            continue

        package_name = _discover_package_name(str(entrypoint), src_dir)
        project_name = str(project_table.get("name") or tool_root.name.lower())
        build_name = str(pyinstaller_table.get("name") or project_name)
        module_name = _strip_py_suffix(str(entrypoint)).replace("/", ".")
        requires_qt, qt_api = _detect_qt(project_table, tool_table)
        tests_dir = tool_root / "tests"
        requirements_file = tool_root / "requirements.txt"
        version_file, version_key, tag_suffix = _infer_version_info(
            tool_root, package_name, tool_table
        )
        requires_python = project_table.get("requires-python")
        min_py = _parse_min_python(
            str(requires_python) if requires_python is not None else None
        )
        min_python = f"{min_py[0]}.{min_py[1]}"
        validate_py38 = _validate_py38(min_py)

        discovered.append(
            ToolMetadata(
                directory=tool_root.name,
                relative_path=tool_root.relative_to(repo_root).as_posix(),
                project_name=project_name,
                build_name=build_name,
                package_name=package_name,
                entrypoint=str(entrypoint),
                module_name=module_name,
                src_path=(tool_root / "src").relative_to(repo_root).as_posix(),
                tests_path=tests_dir.relative_to(repo_root).as_posix()
                if tests_dir.exists()
                else None,
                requirements_path=(
                    requirements_file.relative_to(repo_root).as_posix()
                    if requirements_file.exists()
                    else None
                ),
                requires_qt=requires_qt,
                qt_api=qt_api,
                console=pyinstaller_table.get("console"),
                windowed=pyinstaller_table.get("windowed"),
                version_file=version_file,
                version_key=version_key,
                release_tag_suffix=tag_suffix or build_name,
                script_names=script_names,
                min_python=min_python,
                validate_py38=validate_py38,
            )
        )

    return discovered


def resolve_tool(selector: str, repo_root: Optional[Path] = None) -> ToolMetadata:
    normalized = selector.replace("\\", "/").rstrip("/").lower()
    for tool in discover_tools(repo_root):
        candidates = {
            tool.directory.lower(),
            tool.project_name.lower(),
            tool.build_name.lower(),
            tool.package_name.lower(),
            tool.relative_path.lower(),
        }
        if normalized in candidates:
            return tool
    raise KeyError(selector)


def _emit_list(tools: List[ToolMetadata], format_name: str) -> None:
    payload = [tool.to_dict() for tool in tools]
    if format_name == "json":
        print(json.dumps(payload, indent=2))
        return
    print(f"tools_matrix={json.dumps(payload)}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Discover Python tools under Tools/")
    parser.add_argument("--tool", help="Return metadata for one tool selector")
    parser.add_argument("--format", choices=["json", "github"], default="json")
    parser.add_argument("--cli-only", action="store_true", help="Only emit non-windowed tools")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent
    if args.tool:
        try:
            tool = resolve_tool(args.tool, repo_root)
        except KeyError as exc:
            raise SystemExit(f"Unknown tool selector: {args.tool}") from exc
        print(json.dumps(tool.to_dict(), indent=2))
        return

    tools = discover_tools(repo_root)
    if args.cli_only:
        tools = [tool for tool in tools if tool.is_cli]
    _emit_list(tools, args.format)


if __name__ == "__main__":
    main()
