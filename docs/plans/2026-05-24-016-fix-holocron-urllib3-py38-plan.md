---
title: "fix: holocron toolset urllib3/requests pins for python 3.8 ci"
type: fix
status: completed
date: 2026-05-24
origin: lfg-pr266-follow-up
strategy_track: test-signal-quality
---

# fix: HolocronToolset urllib3/requests pins for Python 3.8 CI

## Summary

Plan 015 confirmed tomli-into-venv fix (`847a06e20`) — KotorDiff Windows passed. HolocronToolset Windows failed because `urllib3>=2.6.3` is unavailable on Python 3.8 (max 2.2.3). Split urllib3 and requests pins in the HolocronToolset submodule `requirements.txt` to match repo Py3.8/3.9+ convention.

---

## Requirements

- R1. HolocronToolset PR Build Validation (windows-latest, Python 3.8) passes deps dry-run.
- R2. Python 3.9+ still resolves urllib3>=2.6.3 and requests>=2.32.4.
- R3. No product code changes.

---

## Implementation Units

- U1. Update `Tools/HolocronToolset/requirements.txt` with version-split pins.
- U2. Commit submodule + PyKotor gitlink; re-run CI on PR #266.

**Verification:** PR Build Validation HolocronToolset (windows-latest) green.
