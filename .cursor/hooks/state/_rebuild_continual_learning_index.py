"""Rebuild continual-learning-index.json from all agent-transcripts *.jsonl on disk."""

from __future__ import annotations

import datetime as dt
import json

from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]  # PyKotor repo root
TRANSCRIPTS = Path(r"C:\Users\boden\.cursor\projects\c-GitHub-PyKotor\agent-transcripts")
OUT = Path(__file__).resolve().parent / "continual-learning-index.json"


def main() -> None:
    now = dt.datetime.now(dt.timezone.utc)
    stamp = now.strftime("%Y-%m-%dT%H:%M:%S.") + f"{now.microsecond:06d}Z"
    transcripts: dict[str, dict[str, int | str]] = {}
    for p in sorted(TRANSCRIPTS.rglob("*.jsonl")):
        try:
            mtime_ms = int(p.stat().st_mtime * 1000)
        except OSError:
            continue
        transcripts[str(p.resolve())] = {"mtimeMs": mtime_ms, "lastProcessedAt": stamp}
    OUT.write_text(
        json.dumps({"version": 1, "transcripts": transcripts}, indent=2), encoding="utf-8"
    )
    print("entries", len(transcripts))


if __name__ == "__main__":
    main()
