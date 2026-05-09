"""JSON read/write for GFF (toolset interchange format)."""

from __future__ import annotations

import json

from typing import TYPE_CHECKING

from pykotor.resource.formats._base import BiowareEncoder
from pykotor.resource.formats.gff.gff_data import GFF
from pykotor.resource.type import ResourceWriter, autoclose

if TYPE_CHECKING:
    from pykotor.resource.type import TARGET_TYPES


class GFFJSONWriter(ResourceWriter):
    """Writes GFF data as JSON using :class:`BiowareEncoder` and :meth:`GFF.__json__`.

    Output matches :func:`pykotor.resource.formats.gff.gff_auto.write_gff` with
    ``file_format=ToolsetFormat.GFF_JSON`` (indent=4, UTF-8).
    """

    def __init__(
        self,
        gff: GFF,
        target: TARGET_TYPES,
    ):
        super().__init__(target)
        self._gff: GFF = gff

    @autoclose
    def write(self, *, auto_close: bool = True):  # noqa: FBT001, FBT002, ARG002  # pyright: ignore[reportUnusedParameters]
        json_dump = json.dumps(self._gff, cls=BiowareEncoder, indent=4)
        self._writer.write_bytes(json_dump.encode("utf-8"))
