"""Dedicated merge-to-TSLPatcher workflow for resource patches based on a game installation."""

from __future__ import annotations

import copy
import logging
import tempfile

from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path
from typing import TYPE_CHECKING, Any, TypeVar

from pykotor.common.language import LocalizedString
from pykotor.common.misc import ResRef
from pykotor.diff_tool.app import DiffConfig
from pykotor.extract.capsule import Capsule
from pykotor.extract.file import ResourceIdentifier
from pykotor.extract.installation import Installation, SearchLocation
from pykotor.resource.generics.dlg import DLG, bytes_dlg, read_dlg
from pykotor.resource.generics.dlg.links import DLGLink
from pykotor.resource.generics.dlg.nodes import DLGEntry, DLGNode, DLGReply
from pykotor.resource.generics.dlg.stunts import DLGStunt
from pykotor.resource.type import ResourceType
from pykotor.tools.finder import canonical_search_order

if TYPE_CHECKING:
    from collections.abc import Callable, Mapping, Sequence


class MergeConflictError(RuntimeError):
    """Raised when two modded resources cannot be safely merged."""


TNode = TypeVar("TNode", bound=DLGNode)


@dataclass(frozen=True)
class _ResolvedResource:
    identifier: ResourceIdentifier
    filepath: Path
    data: bytes


@dataclass(frozen=True)
class _SequenceAlignment:
    base_to_variant: dict[int, int]
    added_variant_indices: list[int]
    removed_base_indices: list[int]


def _normalize_merge_conflict_policy(policy: str | None) -> str:
    if policy in {"mod-a", "mod-b", "fail"}:
        return policy
    return "mod-a"


def run_merge_tslpatcher_workflow(
    config: DiffConfig,
    run_application: Callable[[DiffConfig], int],
) -> int:
    global _merge_conflict_policy

    if config.tslpatchdata_path is None:
        raise MergeConflictError("--merge-tslpatcher requires --tslpatchdata.")
    if not config.merge_modded_paths or len(config.merge_modded_paths) != 2:  # noqa: PLR2004
        raise MergeConflictError("Exactly two modified resource paths are required.")
    if config.merge_installation_path is None or config.merge_resource_name is None:
        raise MergeConflictError("--merge-tslpatcher requires both --merge-installation and --merge-resource.")

    installation = Installation(config.merge_installation_path)
    resolved_base = _resolve_base_resource(
        installation,
        config.merge_resource_name,
        config.merge_resource_type,
        config.merge_module_root,
    )

    resource_type = resolved_base.identifier.restype
    if resource_type != ResourceType.DLG:
        raise MergeConflictError(f"Only DLG merge-to-TSLPatcher is currently implemented. Resolved type: {resource_type.extension}")

    mod_path_a, mod_path_b = config.merge_modded_paths
    if not mod_path_a.is_file() or not mod_path_b.is_file():
        raise MergeConflictError("Both --merge-path inputs must be files.")

    base_dlg = read_dlg(resolved_base.data)
    mod_a_dlg = read_dlg(mod_path_a)
    mod_b_dlg = read_dlg(mod_path_b)
    _merge_conflict_policy = _normalize_merge_conflict_policy(config.merge_conflict_policy)
    _merge_conflicts.clear()
    merged_dlg = _merge_dlg_three_way(base_dlg, mod_a_dlg, mod_b_dlg)

    if _merge_conflicts:
        chosen_label = "mod_a" if _merge_conflict_policy == "mod-a" else "mod_b"
        _merge_logger.warning("=== Merge completed with %d conflict(s) (%s values used) ===", len(_merge_conflicts), chosen_label)
        for conflict in _merge_conflicts:
            _merge_logger.warning("  - %s", conflict)

    with tempfile.TemporaryDirectory(prefix="kotordiff-merge-") as temp_dir_str:
        temp_dir = Path(temp_dir_str)
        base_dir = temp_dir / "base"
        merged_dir = temp_dir / "merged"
        base_dir.mkdir(parents=True, exist_ok=True)
        merged_dir.mkdir(parents=True, exist_ok=True)

        resource_filename = f"{resolved_base.identifier.resname}.{resolved_base.identifier.restype.extension}"
        base_file_path = base_dir / resource_filename
        merged_file_path = merged_dir / resource_filename
        base_file_path.write_bytes(resolved_base.data)
        merged_file_path.write_bytes(bytes_dlg(merged_dlg, game=installation.game(), file_format=ResourceType.DLG))

        diff_config = DiffConfig(
            paths=[base_file_path, merged_file_path],
            tslpatchdata_path=config.tslpatchdata_path,
            ini_filename=config.ini_filename,
            output_log_path=config.output_log_path,
            log_level=config.log_level,
            output_mode=config.output_mode,
            use_colors=config.use_colors,
            compare_hashes=config.compare_hashes,
            use_profiler=config.use_profiler,
            filters=config.filters,
            logging_enabled=config.logging_enabled,
            use_incremental_writer=True,
        )
        return run_application(diff_config)


def _resolve_base_resource(
    installation: Installation,
    resource_name: str,
    explicit_type: ResourceType | None,
    module_root: str | None,
) -> _ResolvedResource:
    resource_name = resource_name.strip()
    suffix = Path(resource_name).suffix.lstrip(".")
    restype = explicit_type or (ResourceType.from_extension(suffix) if suffix else ResourceType.INVALID)
    if restype.is_invalid:
        raise MergeConflictError("Could not determine resource type for --merge-resource. Include an extension or pass --merge-resource-type.")

    resname = Path(resource_name).stem if suffix else resource_name
    query = ResourceIdentifier(resname, restype)

    direct_override_path = installation.override_path() / f"{resname}.{restype.extension}"
    if direct_override_path.is_file():
        return _ResolvedResource(query, direct_override_path, direct_override_path.read_bytes())

    if module_root:
        modules_dir = installation.module_path()
        direct_module_candidates = [
            modules_dir / module_root,
            modules_dir / f"{module_root}.mod",
            modules_dir / f"{module_root}.rim",
            modules_dir / f"{module_root}_s.rim",
        ]
        for candidate in direct_module_candidates:
            if candidate.is_file():
                resource = Capsule(candidate).resource(resname, restype)
                if resource is not None:
                    return _ResolvedResource(query, candidate, resource)

    search_order = [
        location
        for location in canonical_search_order()
        if location in {SearchLocation.OVERRIDE, SearchLocation.MODULES, SearchLocation.CHITIN}
    ]
    locations = installation.locations([query], order=search_order, module_root=module_root).get(query, [])
    if not locations:
        raise MergeConflictError(f"Unable to resolve {resname}.{restype.extension} from installation {installation.path()}.")
    if len(locations) > 1:
        location_list = "\n".join(str(location.filepath) for location in locations)
        raise MergeConflictError(f"Base resource resolution for {resname}.{restype.extension} is ambiguous. Narrow it with --merge-module.\n{location_list}")

    resource = installation.resource(
        resname,
        restype,
        order=search_order,
        module_root=module_root,
    )
    if resource is None:
        raise MergeConflictError(f"Resolved location for {resname}.{restype.extension} but failed to read it.")

    return _ResolvedResource(query, resource.filepath, resource.data)


def _merge_dlg_three_way(base: DLG, mod_a: DLG, mod_b: DLG) -> DLG:
    base_entries = base.all_entries(as_sorted=True)
    base_replies = base.all_replies(as_sorted=True)
    mod_a_entries = mod_a.all_entries(as_sorted=True)
    mod_a_replies = mod_a.all_replies(as_sorted=True)
    mod_b_entries = mod_b.all_entries(as_sorted=True)
    mod_b_replies = mod_b.all_replies(as_sorted=True)

    entry_align_a = _align_node_sequence(base_entries, mod_a_entries)
    entry_align_b = _align_node_sequence(base_entries, mod_b_entries)
    reply_align_a = _align_node_sequence(base_replies, mod_a_replies)
    reply_align_b = _align_node_sequence(base_replies, mod_b_replies)

    if entry_align_a.removed_base_indices or entry_align_b.removed_base_indices:
        _merge_logger.warning("EntryList removals detected; removed entries will be excluded from the merge.")
    if reply_align_a.removed_base_indices or reply_align_b.removed_base_indices:
        _merge_logger.warning("ReplyList removals detected; removed replies will be excluded from the merge.")

    merged = DLG()
    for field_name, base_value in base.__dict__.items():
        if field_name == "starters":
            continue
        setattr(
            merged,
            field_name,
            _merge_value(
                base_value,
                getattr(mod_a, field_name),
                getattr(mod_b, field_name),
                f"DLG.{field_name}",
            ),
        )

    entry_keys, entry_key_by_base, entry_key_by_a, entry_key_by_b = _build_node_keys(
        base_entries,
        mod_a_entries,
        mod_b_entries,
        entry_align_a,
        entry_align_b,
        prefix="entry",
    )
    reply_keys, reply_key_by_base, reply_key_by_a, reply_key_by_b = _build_node_keys(
        base_replies,
        mod_a_replies,
        mod_b_replies,
        reply_align_a,
        reply_align_b,
        prefix="reply",
    )

    entry_node_map = _build_merged_nodes(
        DLGEntry,
        entry_keys,
        base_entries,
        mod_a_entries,
        mod_b_entries,
        entry_key_by_base,
        entry_key_by_a,
        entry_key_by_b,
        label="EntryList",
    )
    reply_node_map = _build_merged_nodes(
        DLGReply,
        reply_keys,
        base_replies,
        mod_a_replies,
        mod_b_replies,
        reply_key_by_base,
        reply_key_by_a,
        reply_key_by_b,
        label="ReplyList",
    )

    for index, key in enumerate(entry_keys):
        entry_node_map[key].list_index = index
    for index, key in enumerate(reply_keys):
        reply_node_map[key].list_index = index

    _merge_links_for_nodes(
        base_entries,
        mod_a_entries,
        mod_b_entries,
        entry_key_by_base,
        entry_key_by_a,
        entry_key_by_b,
        reply_key_by_base,
        reply_key_by_a,
        reply_key_by_b,
        entry_node_map,
        reply_node_map,
        label="EntryList",
    )
    _merge_links_for_nodes(
        base_replies,
        mod_a_replies,
        mod_b_replies,
        reply_key_by_base,
        reply_key_by_a,
        reply_key_by_b,
        entry_key_by_base,
        entry_key_by_a,
        entry_key_by_b,
        reply_node_map,
        entry_node_map,
        label="ReplyList",
    )

    merged.starters = _merge_link_sequence(
        base.starters,
        mod_a.starters,
        mod_b.starters,
        entry_key_by_base,
        entry_key_by_a,
        entry_key_by_b,
        entry_node_map,
        label="StartingList",
        parent_label="DLG",
    )

    merged.next_node_id = max(
        merged.next_node_id,
        max((node.node_id for node in [*entry_node_map.values(), *reply_node_map.values()]), default=0) + 1,
    )
    return merged


def _align_node_sequence(
    base_nodes: Sequence[TNode],
    variant_nodes: Sequence[TNode],
) -> _SequenceAlignment:
    base_keys = [_node_identity(node) for node in base_nodes]
    variant_keys = [_node_identity(node) for node in variant_nodes]
    matcher = SequenceMatcher(a=base_keys, b=variant_keys, autojunk=False)

    base_to_variant: dict[int, int] = {}
    added_variant_indices: list[int] = []
    removed_base_indices: list[int] = []

    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            for offset in range(i2 - i1):
                base_to_variant[i1 + offset] = j1 + offset
            continue

        if tag == "replace":
            nested_matcher = SequenceMatcher(
                a=base_keys[i1:i2],
                b=variant_keys[j1:j2],
                autojunk=False,
            )
            matched_base_indices: set[int] = set()
            matched_variant_indices: set[int] = set()
            for nested_tag, nested_i1, nested_i2, nested_j1, nested_j2 in nested_matcher.get_opcodes():
                if nested_tag != "equal":
                    continue
                for offset in range(nested_i2 - nested_i1):
                    base_index = i1 + nested_i1 + offset
                    variant_index = j1 + nested_j1 + offset
                    base_to_variant[base_index] = variant_index
                    matched_base_indices.add(base_index)
                    matched_variant_indices.add(variant_index)

            added_variant_indices.extend(
                variant_index for variant_index in range(j1, j2) if variant_index not in matched_variant_indices
            )
            removed_base_indices.extend(
                base_index for base_index in range(i1, i2) if base_index not in matched_base_indices
            )
            continue

        if tag == "insert":
            added_variant_indices.extend(range(j1, j2))
            continue

        if tag == "delete":
            removed_base_indices.extend(range(i1, i2))

    return _SequenceAlignment(base_to_variant, added_variant_indices, removed_base_indices)


def _build_node_keys(
    base_nodes: Sequence[TNode],
    mod_a_nodes: Sequence[TNode],
    mod_b_nodes: Sequence[TNode],
    align_a: _SequenceAlignment,
    align_b: _SequenceAlignment,
    *,
    prefix: str,
) -> tuple[list[str], dict[int, str], dict[int, str], dict[int, str]]:
    ordered_keys = [f"{prefix}:base:{index}" for index in range(len(base_nodes))]
    key_by_base = {index: key for index, key in enumerate(ordered_keys)}
    key_by_a = {variant_index: key_by_base[base_index] for base_index, variant_index in align_a.base_to_variant.items()}
    key_by_b = {variant_index: key_by_base[base_index] for base_index, variant_index in align_b.base_to_variant.items()}

    exact_additions_a: dict[tuple[Any, ...], str] = {}
    for variant_index in align_a.added_variant_indices:
        key = f"{prefix}:a:{variant_index}"
        ordered_keys.append(key)
        key_by_a[variant_index] = key
        exact_additions_a[_node_exact_signature(mod_a_nodes[variant_index])] = key

    for variant_index in align_b.added_variant_indices:
        signature = _node_exact_signature(mod_b_nodes[variant_index])
        existing_key = exact_additions_a.get(signature)
        if existing_key is not None:
            key_by_b[variant_index] = existing_key
            continue
        key = f"{prefix}:b:{variant_index}"
        ordered_keys.append(key)
        key_by_b[variant_index] = key

    return ordered_keys, key_by_base, key_by_a, key_by_b


def _build_merged_nodes(
    node_cls: type[TNode],
    ordered_keys: Sequence[str],
    base_nodes: Sequence[TNode],
    mod_a_nodes: Sequence[TNode],
    mod_b_nodes: Sequence[TNode],
    key_by_base: dict[int, str],
    key_by_a: dict[int, str],
    key_by_b: dict[int, str],
    *,
    label: str,
) -> dict[str, TNode]:
    inverse_base = {value: key for key, value in key_by_base.items()}
    inverse_a = {value: key for key, value in key_by_a.items()}
    inverse_b = {value: key for key, value in key_by_b.items()}
    merged_nodes: dict[str, TNode] = {}

    for key in ordered_keys:
        base_node = base_nodes[inverse_base[key]] if key in inverse_base else None
        mod_a_node = mod_a_nodes[inverse_a[key]] if key in inverse_a else None
        mod_b_node = mod_b_nodes[inverse_b[key]] if key in inverse_b else None

        if base_node is None and mod_a_node is not None and mod_b_node is None:
            merged_nodes[key] = _clone_node(mod_a_node)
            continue
        if base_node is None and mod_b_node is not None and mod_a_node is None:
            merged_nodes[key] = _clone_node(mod_b_node)
            continue
        if base_node is None and mod_a_node is not None and mod_b_node is not None:
            merged_nodes[key] = _merge_node_fields(None, mod_a_node, mod_b_node, f"{label}[{key}]")
            continue
        if base_node is None:
            raise MergeConflictError(f"Internal merge error while building {label}: {key}")

        merged_nodes[key] = _merge_node_fields(
            base_node,
            mod_a_node or base_node,
            mod_b_node or base_node,
            f"{label}[{key}]",
        )

    return merged_nodes


def _merge_node_fields(
    base_node: TNode | None,
    mod_a_node: TNode,
    mod_b_node: TNode,
    context: str,
) -> TNode:
    merged = mod_a_node.__class__()
    all_fields = set(mod_a_node.__dict__.keys()) | set(mod_b_node.__dict__.keys())
    if base_node is not None:
        all_fields |= set(base_node.__dict__.keys())

    for field_name in all_fields:
        if field_name in {"links", "list_index", "_hash_cache"}:
            continue
        base_value = getattr(base_node, field_name) if base_node is not None else None
        merged_value = _merge_value(
            base_value,
            getattr(mod_a_node, field_name),
            getattr(mod_b_node, field_name),
            f"{context}.{field_name}",
        )
        setattr(merged, field_name, merged_value)
    merged.links = []
    merged.list_index = -1
    return merged


def _merge_links_for_nodes(
    base_nodes: Sequence[TNode],
    mod_a_nodes: Sequence[TNode],
    mod_b_nodes: Sequence[TNode],
    key_by_base: dict[int, str],
    key_by_a: dict[int, str],
    key_by_b: dict[int, str],
    target_key_by_base: dict[int, str],
    target_key_by_a: dict[int, str],
    target_key_by_b: dict[int, str],
    merged_source_nodes: dict[str, TNode],
    merged_target_nodes: Mapping[str, DLGNode],
    *,
    label: str,
) -> None:
    inverse_base = {value: key for key, value in key_by_base.items()}
    inverse_a = {value: key for key, value in key_by_a.items()}
    inverse_b = {value: key for key, value in key_by_b.items()}

    for key, merged_node in merged_source_nodes.items():
        base_node = base_nodes[inverse_base[key]] if key in inverse_base else None
        mod_a_node = mod_a_nodes[inverse_a[key]] if key in inverse_a else None
        mod_b_node = mod_b_nodes[inverse_b[key]] if key in inverse_b else None
        merged_node.links = _merge_link_sequence(
            base_node.links if base_node is not None else [],
            mod_a_node.links if mod_a_node is not None else [],
            mod_b_node.links if mod_b_node is not None else [],
            target_key_by_base,
            target_key_by_a,
            target_key_by_b,
            merged_target_nodes,
            label=("RepliesList" if label == "EntryList" else "EntriesList"),
            parent_label=f"{label}[{key}]",
        )


def _merge_link_sequence(
    base_links: Sequence[DLGLink],
    mod_a_links: Sequence[DLGLink],
    mod_b_links: Sequence[DLGLink],
    target_key_by_base: dict[int, str],
    target_key_by_a: dict[int, str],
    target_key_by_b: dict[int, str],
    merged_target_nodes: Mapping[str, DLGNode],
    *,
    label: str,
    parent_label: str,
) -> list[DLGLink]:
    base_map, base_order = _index_links(base_links, target_key_by_base, f"{parent_label}.{label}.base")
    mod_a_map, mod_a_order = _index_links(mod_a_links, target_key_by_a, f"{parent_label}.{label}.mod_a")
    mod_b_map, mod_b_order = _index_links(mod_b_links, target_key_by_b, f"{parent_label}.{label}.mod_b")

    ordered_keys = [*base_order, *[key for key in mod_a_order if key not in base_map], *[key for key in mod_b_order if key not in base_map and key not in mod_a_map]]
    merged_links: list[DLGLink] = []
    for target_key in ordered_keys:
        if target_key not in merged_target_nodes:
            _merge_logger.warning(
                "%s.%s: link target %s no longer exists in merged dialog, skipping.", parent_label, label, target_key
            )
            continue
        base_link = base_map.get(target_key)
        mod_a_link = mod_a_map.get(target_key)
        mod_b_link = mod_b_map.get(target_key)

        if base_link is not None and mod_a_link is None and mod_b_link is None:
            continue
        if base_link is not None and (mod_a_link is None or mod_b_link is None):
            merged_link = _resolve_link_presence_conflict(
                mod_a_link,
                mod_b_link,
                merged_target_nodes[target_key],
                f"{parent_label}.{label}[{target_key}]",
            )
            if merged_link is None:
                continue
        elif base_link is None and mod_a_link is not None and mod_b_link is None:
            merged_link = _clone_link(mod_a_link, merged_target_nodes[target_key])
        elif base_link is None and mod_b_link is not None and mod_a_link is None:
            merged_link = _clone_link(mod_b_link, merged_target_nodes[target_key])
        elif base_link is None and mod_a_link is not None and mod_b_link is not None:
            merged_link = _merge_link_fields(
                None,
                mod_a_link,
                mod_b_link,
                merged_target_nodes[target_key],
                f"{parent_label}.{label}[{target_key}]",
            )
        elif base_link is not None and mod_a_link is not None and mod_b_link is not None:
            merged_link = _merge_link_fields(
                base_link,
                mod_a_link,
                mod_b_link,
                merged_target_nodes[target_key],
                f"{parent_label}.{label}[{target_key}]",
            )
        else:
            raise MergeConflictError(f"Internal link merge error at {parent_label}.{label}[{target_key}]")

        merged_link.list_index = len(merged_links)
        merged_links.append(merged_link)

    return merged_links


def _index_links(
    links: Sequence[DLGLink],
    target_key_map: dict[int, str],
    context: str,
) -> tuple[dict[str, DLGLink], list[str]]:
    result: dict[str, DLGLink] = {}
    ordered_keys: list[str] = []
    for link in links:
        target_key = target_key_map.get(link.node.list_index)
        if target_key is None:
            _merge_logger.warning(
                "%s: link references node at list_index %d that could not be mapped; skipping.",
                context, link.node.list_index
            )
            continue
        if target_key in result:
            _merge_logger.warning(
                "%s: duplicate link to target %s; keeping first occurrence.", context, target_key
            )
            continue
        result[target_key] = link
        ordered_keys.append(target_key)
    return result, ordered_keys


def _clone_node(node: TNode) -> TNode:
    cloned = copy.deepcopy(node)
    cloned.links = []
    return cloned


def _clone_link(link: DLGLink, target_node: DLGNode) -> DLGLink:
    cloned = DLGLink(target_node)
    for field_name, value in link.__dict__.items():
        if field_name in {"node", "list_index", "_hash_cache"}:
            continue
        setattr(cloned, field_name, copy.deepcopy(value))
    return cloned


def _merge_link_fields(
    base_link: DLGLink | None,
    mod_a_link: DLGLink,
    mod_b_link: DLGLink,
    target_node: DLGNode,
    context: str,
) -> DLGLink:
    merged = DLGLink(target_node)
    fields = set(mod_a_link.__dict__.keys()) | set(mod_b_link.__dict__.keys())
    if base_link is not None:
        fields |= set(base_link.__dict__.keys())
    for field_name in fields:
        if field_name in {"node", "list_index", "_hash_cache"}:
            continue
        base_value = getattr(base_link, field_name) if base_link is not None else None
        setattr(
            merged,
            field_name,
            _merge_value(base_value, getattr(mod_a_link, field_name), getattr(mod_b_link, field_name), f"{context}.{field_name}"),
        )
    return merged


_merge_logger = logging.getLogger(__name__)

# Track conflict warnings for summary output
_merge_conflicts: list[str] = []
_merge_conflict_policy = "mod-a"


def _preferred_conflict_label() -> str:
    return "mod_a" if _merge_conflict_policy != "mod-b" else "mod_b"


def _raise_or_record_conflict(context: str, message: str) -> None:
    if _merge_conflict_policy == "fail":
        raise MergeConflictError(message)
    _merge_logger.warning(message)
    _merge_conflicts.append(context)


def _resolve_link_presence_conflict(
    mod_a_link: DLGLink | None,
    mod_b_link: DLGLink | None,
    target_node: DLGNode,
    context: str,
) -> DLGLink | None:
    chosen_link = mod_a_link if _merge_conflict_policy != "mod-b" else mod_b_link
    preferred_label = _preferred_conflict_label()
    if chosen_link is None:
        _raise_or_record_conflict(
            f"{context} (link removed)",
            f"CONFLICT at {context}: one mod removed this link while the other kept it. Removing link per {preferred_label} policy.",
        )
        return None

    _raise_or_record_conflict(
        context,
        f"CONFLICT at {context}: one mod removed this link while the other kept it. Using {preferred_label} value.",
    )
    return _clone_link(chosen_link, target_node)


def _merge_value(base_value: Any, mod_a_value: Any, mod_b_value: Any, context: str) -> Any:
    if _values_equal(mod_a_value, base_value) and _values_equal(mod_b_value, base_value):
        return copy.deepcopy(base_value if base_value is not None else mod_a_value)
    if _values_equal(mod_a_value, mod_b_value):
        return copy.deepcopy(mod_a_value)
    if _values_equal(mod_b_value, base_value):
        return copy.deepcopy(mod_a_value)
    if _values_equal(mod_a_value, base_value):
        return copy.deepcopy(mod_b_value)
    # Try list-level merge when all three are lists
    if isinstance(base_value, list) and isinstance(mod_a_value, list) and isinstance(mod_b_value, list):
        return _merge_list_values(base_value, mod_a_value, mod_b_value, context)
    preferred_value = mod_a_value if _merge_conflict_policy != "mod-b" else mod_b_value
    preferred_label = _preferred_conflict_label()
    _raise_or_record_conflict(
        context,
        f"CONFLICT at {context}: both mods changed this field differently. Using {preferred_label} value.",
    )
    return copy.deepcopy(preferred_value)


def _merge_list_values(base_list: list, mod_a_list: list, mod_b_list: list, context: str) -> list:
    """Merge two modified lists against a common base using signature-based matching.

    Strategy: take the union of both mod additions, keep items present in both,
    remove items that either mod removed (from base), and preserve order.
    """
    base_sigs = [_signature(item) for item in base_list]
    a_sigs = [_signature(item) for item in mod_a_list]
    b_sigs = [_signature(item) for item in mod_b_list]

    base_set = set(base_sigs)
    a_set = set(a_sigs)
    b_set = set(b_sigs)

    # Items removed by mod A or mod B from the base
    removed_by_a = base_set - a_set
    removed_by_b = base_set - b_set

    # Start with mod_a's list, then append new items from mod_b
    merged: list = []
    seen_sigs: set = set()
    for item in mod_a_list:
        sig = _signature(item)
        if sig in removed_by_b:
            continue  # mod_b removed this from base, honor the removal
        if sig not in seen_sigs:
            merged.append(copy.deepcopy(item))
            seen_sigs.add(sig)
    for item in mod_b_list:
        sig = _signature(item)
        if sig in removed_by_a:
            continue  # mod_a removed this from base, honor the removal
        if sig not in seen_sigs:
            merged.append(copy.deepcopy(item))
            seen_sigs.add(sig)
    return merged


def _values_equal(left: Any, right: Any) -> bool:
    """Check equality, treating None as equivalent to zero/empty defaults for GFF fields."""
    if left is None and right is None:
        return True
    if left is None or right is None:
        non_none = right if left is None else left
        if isinstance(non_none, (int, float)) and non_none == 0:
            return True
        if isinstance(non_none, str) and non_none == "":
            return True
        if isinstance(non_none, list) and len(non_none) == 0:
            return True
        if isinstance(non_none, ResRef) and str(non_none) == "":
            return True
        return False
    return _signature(left) == _signature(right)


def _node_identity(node: DLGNode) -> tuple[Any, ...]:
    if node.node_id:
        return (node.__class__.__name__, "node_id", node.node_id)
    vo_resref = str(getattr(node, "vo_resref", ResRef("")))
    if vo_resref:
        if isinstance(node, DLGEntry):
            return (node.__class__.__name__, node.speaker, node.listener, "vo_resref", vo_resref)
        return (node.__class__.__name__, node.listener, "vo_resref", vo_resref)
    text_key = _localized_key(node.text)
    if isinstance(node, DLGEntry):
        return (node.__class__.__name__, node.speaker, node.listener, text_key)
    return (node.__class__.__name__, node.listener, text_key)


def _node_exact_signature(node: DLGNode) -> tuple[Any, ...]:
    items: list[tuple[str, Any]] = []
    for field_name, value in sorted(node.__dict__.items()):
        if field_name in {"links", "list_index", "_hash_cache"}:
            continue
        items.append((field_name, _signature(value)))
    return tuple(items)


def _localized_key(value: LocalizedString) -> tuple[int, tuple[tuple[int, str], ...]]:
    substrings = tuple(
        sorted(
            (language, text)
            for language, text in value.to_dict()["substrings"].items()
            if text != ""
        )
    )
    return (value.stringref, substrings)


_SIGNATURE_EXCLUDE_KEYS = frozenset({"_hash_cache"})


def _signature(value: Any) -> Any:
    if isinstance(value, LocalizedString):
        return ("loc", _localized_key(value))
    if isinstance(value, ResRef):
        return ("resref", str(value))
    if isinstance(value, DLGStunt):
        return ("stunt", tuple(sorted((k, v) for k, v in value.to_dict().items() if k not in _SIGNATURE_EXCLUDE_KEYS)))
    if hasattr(value, "to_dict") and callable(value.to_dict):
        data = value.to_dict()
        if isinstance(data, dict):
            return tuple((key, _signature(item)) for key, item in sorted(data.items()) if key not in _SIGNATURE_EXCLUDE_KEYS)
    if isinstance(value, list):
        return tuple(_signature(item) for item in value)
    if isinstance(value, tuple):
        return tuple(_signature(item) for item in value)
    if isinstance(value, dict):
        return tuple((key, _signature(item)) for key, item in sorted(value.items()) if key not in _SIGNATURE_EXCLUDE_KEYS)
    return value
