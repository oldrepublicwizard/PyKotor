"""JSON read/write for SSF (sound sets); used for tooling and round-trip."""

from __future__ import annotations

import json

from typing import TYPE_CHECKING, Any

from pykotor.resource.formats.ssf.ssf_data import SSF, SSFSound
from pykotor.resource.type import ResourceReader, ResourceWriter, autoclose
from pykotor.tools.encoding import decode_bytes_with_fallbacks

if TYPE_CHECKING:
    from pykotor.resource.type import SOURCE_TYPES, TARGET_TYPES


class SSFJSONReader(ResourceReader):
    """Reads SSF files from JSON format."""

    def __init__(
        self,
        source: SOURCE_TYPES,
        offset: int = 0,
        size: int = 0,
    ):
        super().__init__(source, offset, size)
        self._json: dict[str, Any] = {}
        self._ssf: SSF | None = None

    @autoclose
    def load(self, *, auto_close: bool = True) -> SSF:  # noqa: FBT001, FBT002, ARG002
        self._ssf = SSF()
        raw = self._reader.read_all()
        self._json = json.loads(decode_bytes_with_fallbacks(raw))

        sounds = self._json.get("sounds")
        if not isinstance(sounds, list):
            msg = "The JSON file that was loaded was not a valid SSF."
            raise ValueError(msg)

        for sound_entry in sounds:
            sound = SSFSound(int(sound_entry["id"]))
            stringref = int(sound_entry["strref"])
            self._ssf.set_data(sound, stringref)

        return self._ssf


class SSFJSONWriter(ResourceWriter):
    def __init__(
        self,
        ssf: SSF,
        target: TARGET_TYPES,
    ):
        super().__init__(target)
        self._ssf: SSF = ssf
        self._json: dict[str, list[dict[str, str]]] = {"sounds": []}

    @autoclose
    def write(self, *, auto_close: bool = True):  # noqa: FBT001, FBT002, ARG002  # pyright: ignore[reportUnusedParameters]
        for sound_name, sound in SSFSound.__members__.items():
            self._json["sounds"].append(
                {
                    "id": str(sound.value),
                    "label": sound_name,
                    "strref": str(self._ssf.get(sound)),
                }
            )

        json_dump = json.dumps(self._json, indent=4)
        self._writer.write_bytes(json_dump.encode())