"""Export all resources from a KotOR installation to JSON files."""

from __future__ import annotations

import base64
import json
import shutil

from pathlib import Path
from typing import TYPE_CHECKING, Iterator

from pykotor.common.misc import Game
from pykotor.cli.commands.format_convert import resource_data_to_json_bytes
from pykotor.cli.commands.get_cmd import _resolve_installation_path
from pykotor.extract.file import FileResource, clear_file_data_cache
from pykotor.extract.installation import Installation
from pykotor.tools.path import get_kotor_paths_from_default

if TYPE_CHECKING:
    from argparse import Namespace

    from loggerplus import RobustLogger as Logger


def _parse_game_arg(game_str: str | None) -> Game | None:
    if not game_str or not game_str.strip():
        return None

    normalized = game_str.strip().lower()
    if normalized in {"k1", "kotor", "kotor1"}:
        return Game.K1
    if normalized in {"k2", "tsl", "kotor2"}:
        return Game.K2
    return None


def _iter_stream_resources(installation: Installation) -> Iterator[FileResource]:
    for path_getter in (
        installation.streammusic_path,
        installation.streamsounds_path,
        installation.streamvoice_path,
    ):
        try:
            folder_path = path_getter()
        except Exception:
            continue
        if not folder_path.exists():
            continue
        for file_path in folder_path.rglob("*"):
            if file_path.is_file():
                yield FileResource.from_path(file_path)


def _iter_all_installation_resources(installation: Installation, logger: Logger) -> Iterator[FileResource]:
    seen: set[tuple[str, int, int, str, str]] = set()

    def add(resource: FileResource) -> FileResource | None:
        key = (
            str(resource.filepath()),
            resource.offset(),
            resource.size(),
            resource.resname().lower(),
            resource.restype().extension.lower() if resource.restype().extension else resource.restype().name.lower(),
        )
        if key in seen:
            return None
        seen.add(key)
        return resource

    root_tlk = installation.path() / "dialog.tlk"
    if root_tlk.is_file():
        resource = add(FileResource.from_path(root_tlk))
        if resource is not None:
            yield resource
    root_tlk_f = installation.path() / "dialogf.tlk"
    if root_tlk_f.is_file():
        resource = add(FileResource.from_path(root_tlk_f))
        if resource is not None:
            yield resource

    try:
        for resource in installation.override_resources():
            deduped = add(resource)
            if deduped is not None:
                yield deduped
    except Exception as exc:
        logger.warning("Skipping override resources: %s: %s", exc.__class__.__name__, exc)

    try:
        for module_name in installation.modules_list():
            for resource in installation.module_resources(module_name):
                deduped = add(resource)
                if deduped is not None:
                    yield deduped
    except Exception as exc:
        logger.warning("Skipping module resources: %s: %s", exc.__class__.__name__, exc)

    try:
        for lip_name in installation.lips_list():
            for resource in installation.lip_resources(lip_name):
                deduped = add(resource)
                if deduped is not None:
                    yield deduped
    except Exception as exc:
        logger.warning("Skipping lip resources: %s: %s", exc.__class__.__name__, exc)

    try:
        for texturepack_name in installation.texturepacks_list():
            for resource in installation.texturepack_resources(texturepack_name):
                deduped = add(resource)
                if deduped is not None:
                    yield deduped
    except Exception as exc:
        logger.warning("Skipping texturepack resources: %s: %s", exc.__class__.__name__, exc)

    try:
        for resource in installation.core_resources():
            deduped = add(resource)
            if deduped is not None:
                yield deduped
    except Exception as exc:
        logger.warning("Skipping core resources: %s: %s", exc.__class__.__name__, exc)

    try:
        for resource in _iter_stream_resources(installation):
            deduped = add(resource)
            if deduped is not None:
                yield deduped
    except Exception as exc:
        logger.warning("Skipping stream resources: %s: %s", exc.__class__.__name__, exc)


def _resource_output_path(output_root: Path, installation_path: Path, resource: FileResource) -> Path:
    filepath = Path(resource.filepath())
    try:
        relative_source = filepath.relative_to(installation_path)
    except ValueError:
        relative_source = Path(filepath.name)

    target_path = relative_source / resource.filename() if (resource.inside_capsule or resource.inside_bif) else relative_source
    return output_root / target_path.with_suffix(f"{target_path.suffix}.json" if target_path.suffix else ".json")


def _build_fallback_payload(installation_path: Path, resource: FileResource, data: bytes) -> bytes:
    filepath = Path(resource.filepath())
    try:
        relative_source = filepath.relative_to(installation_path)
    except ValueError:
        relative_source = Path(filepath.name)

    payload = {
        "resource": resource.filename(),
        "resname": resource.resname(),
        "restype": resource.restype().name,
        "extension": resource.restype().extension,
        "source_path": relative_source.as_posix(),
        "container_path": relative_source.as_posix() if (resource.inside_capsule or resource.inside_bif) else None,
        "offset": resource.offset(),
        "size": len(data),
        "encoding": "base64",
        "data_base64": base64.b64encode(data).decode("ascii"),
    }
    return json.dumps(payload, separators=(",", ":")).encode("utf-8") + b"\n"


def _export_installation_to_json(installation_path: Path, output_root: Path, logger: Logger) -> int:
    output_root.mkdir(parents=True, exist_ok=True)

    try:
        installation = Installation(installation_path)
    except Exception:
        logger.exception("Invalid installation path: %s", installation_path)
        return 1

    logger.info("Exporting resources from %s to %s", installation_path, output_root)

    supported_count = 0
    fallback_count = 0
    error_count = 0
    processed_count = 0

    created_directories: set[Path] = set()
    for index, resource in enumerate(_iter_all_installation_resources(installation, logger), start=1):
        processed_count = index
        destination = _resource_output_path(output_root, Path(installation_path), resource)
        destination_parent = destination.parent
        if destination_parent not in created_directories:
            destination_parent.mkdir(parents=True, exist_ok=True)
            created_directories.add(destination_parent)

        try:
            data = resource.data()
            try:
                json_bytes = resource_data_to_json_bytes(data, resource.restype())
                supported_count += 1
            except ValueError:
                json_bytes = _build_fallback_payload(Path(installation_path), resource, data)
                fallback_count += 1
            destination.write_bytes(json_bytes)
        except Exception as exc:
            error_count += 1
            error_payload = {
                "resource": resource.filename(),
                "source_path": str(resource.filepath()),
                "error": f"{exc.__class__.__name__}: {exc}",
            }
            destination.write_text(json.dumps(error_payload, separators=(",", ":")) + "\n", encoding="utf-8")

        if index % 500 == 0:
            logger.info(
                "Processed %s resources (%s supported, %s fallback, %s errors)",
                index,
                supported_count,
                fallback_count,
                error_count,
            )
        if index % 1000 == 0:
            clear_file_data_cache()

    clear_file_data_cache()
    logger.info(
        "Processed %s resources (%s supported, %s fallback, %s errors)",
        processed_count,
        supported_count,
        fallback_count,
        error_count,
    )

    logger.info(
        "Installation export complete: %s supported JSON, %s fallback JSON, %s error JSON",
        supported_count,
        fallback_count,
        error_count,
    )
    return 0 if error_count == 0 else 2


def cmd_installation_to_json(args: Namespace, logger: Logger) -> int:
    output_root = Path(getattr(args, "output", "installation-json")).resolve()
    clean_output = bool(getattr(args, "clean", False))

    if getattr(args, "all_detected", False):
        explicit_path = getattr(args, "path", None) or getattr(args, "installation", None)
        if explicit_path:
            logger.error("--all-detected cannot be combined with --path.")
            return 1

        game_arg = getattr(args, "game", None)
        game_filter = _parse_game_arg(game_arg)
        if game_arg and game_filter is None:
            logger.error("Unknown game '%s'. Use k1 or k2.", game_arg)
            return 1

        discovered = get_kotor_paths_from_default()
        install_targets = [
            (game, index, Path(path))
            for game, game_paths in discovered.items()
            if game_filter in (None, game)
            for index, path in enumerate(game_paths)
        ]
        if not install_targets:
            logger.error("No default installations were found%s.", f" for {game_filter.name}" if game_filter else "")
            return 1

        if clean_output and output_root.exists():
            shutil.rmtree(output_root)
        output_root.mkdir(parents=True, exist_ok=True)

        exit_codes: list[int] = []
        for game, index, installation_path in install_targets:
            install_output_root = output_root / game.name.lower() / str(index)
            logger.info(
                "Exporting auto-detected %s installation [%s] from %s to %s",
                game.name,
                index,
                installation_path,
                install_output_root,
            )
            exit_codes.append(_export_installation_to_json(installation_path, install_output_root, logger))

        if any(code == 1 for code in exit_codes):
            return 1
        if any(code == 2 for code in exit_codes):
            return 2
        return 0

    installation_path = _resolve_installation_path(args, logger)
    if installation_path is None:
        return 1

    if clean_output and output_root.exists():
        shutil.rmtree(output_root)
    return _export_installation_to_json(Path(installation_path), output_root, logger)