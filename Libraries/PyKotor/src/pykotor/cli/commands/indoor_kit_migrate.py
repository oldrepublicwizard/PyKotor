"""CLI: migrate indoor kit JSON v1 to format_version 2 (tile templates)."""

from __future__ import annotations

import json

from pathlib import Path

from pykotor.tools.indoor_kit_migrate import migrate_kit_json_v1_to_v2

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from argparse import Namespace

    from loggerplus import RobustLogger


def cmd_indoor_kit_migrate_v1_to_v2(args: Namespace, logger: RobustLogger) -> int:
    """Read a v1 kit JSON, write a v2 JSON (lossy: all components become floor templates)."""
    input_path = Path(args.input)
    output_path = Path(args.output)
    if not input_path.is_file():
        logger.error("Input file not found: %s", input_path)
        return 1
    try:
        doc = json.loads(input_path.read_text(encoding="utf-8"))
        v2 = migrate_kit_json_v1_to_v2(doc)
    except ValueError as e:
        logger.error("%s", e)
        return 1
    except json.JSONDecodeError as e:
        logger.error("Invalid JSON: %s", e)
        return 1

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(v2, indent=2) + "\n", encoding="utf-8")
    logger.info("Wrote v2 kit JSON to %s", output_path)
    return 0
