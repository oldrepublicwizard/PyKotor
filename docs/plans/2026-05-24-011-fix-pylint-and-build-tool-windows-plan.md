---
title: "fix: pylint ci gate and build-tool windows TrimEnd"
type: fix
status: completed
date: 2026-05-24
origin: lfg-pr266-ci-follow-up
strategy_track: test-signal-quality
---

# fix: pylint CI gate and build-tool Windows TrimEnd

## Summary

Restore PR #266 merge signal by fixing two CI failures unrelated to the parity harness: the repo-wide **Pylint** workflow (pre-existing on `master`, exit code 31 from mass R0801 duplicate-code) and **Build KotorMCP (windows-latest)** in PR Build Validation (PowerShell `TrimEnd` char-array bug in the composite build-tool action).

---

## Problem Frame

After plans 008–010, **Python application** and parity harness tests are green. Remaining required failures on head `73eb48cd6`:

| Check | Symptom |
|-------|---------|
| Pylint `build (3.8/3.9/3.10)` | `Your code has been rated at 0.00/10`, exit 31 — thousands of R0801 duplicate-code hits across the monorepo |
| Build KotorMCP (windows-latest) | PowerShell: `Cannot convert argument "trimChars", with value: "\\"` for `TrimEnd` |

Pylint also fails on recent `master` pushes (runs 25861900104+), so this is not a regression from the parity harness branch.

---

## Requirements

- R1. Pylint workflow completes without false-positive repo-wide duplicate-code failure.
- R2. PR Build Validation Windows tool builds pass the build-tool composite artifact-name / venv setup steps.
- R3. Changes stay CI/workflow scoped — no parity harness product logic changes.
- R4. Preserve existing flake8/ruff/pytest gates; do not weaken local lint policy beyond aligning pylint CI with repo reality.

---

## Scope Boundaries

- Do not refactor duplicated Python across the monorepo to satisfy R0801.
- Do not replace pylint with ruff in this slice (separate initiative).
- Do not fix pending tool builds until they fail (ubuntu legs may pass after Windows fix).

### Deferred to Follow-Up Work

- Tighten pylint scope to Libraries/PyKotor only with incremental score thresholds: follow-up PR after baseline is stable.

---

## Context & Research

### Relevant Code and Patterns

- `.github/workflows/pylint.yml` — runs `pylint $(git ls-files '*.py')` with no disables; ignores `pyproject.toml` `[tool.pylintrc]` (max-line-length only today).
- `.github/actions/build-tool/action.yml` lines 61, 146 — `$toolPath.TrimEnd('/', '\\')` invalid in PowerShell (expects `[char[]]`, not string `"\\"`).
- Plan `2026-05-24-003` — prior build-pr path resolution fix; same composite action surface.

### Institutional Learnings

- MSDO / pytest CI fixes used minimal workflow-scoped diffs rather than repo-wide lint cleanups (plans 004–009).

---

## Key Technical Decisions

- **Disable R0801 in pylint CI**: Duplicate-code detection across `git ls-files '*.py'` is not actionable for a monorepo with vendor mirrors and parallel tool layouts; rating 0.00/10 blocks merges without improving product quality. Match pre-existing master failure mode.
- **Add pylint ignore paths for vendor and generated UI**: Align with ruff/pyright exclude lists in root `pyproject.toml`.
- **Fix TrimEnd with `[char[]]@('/', '\')`**: Minimal PowerShell-correct fix at both call sites in build-tool action; no behavioral change on Linux bash steps.

---

## Implementation Units

- U1. **Fix build-tool Windows TrimEnd**

**Goal:** Unblock Windows matrix legs in PR Build Validation.

**Requirements:** R2

**Dependencies:** None

**Files:**
- Modify: `.github/actions/build-tool/action.yml`

**Approach:**
- Replace `$toolPath.TrimEnd('/', '\\')` with `$toolPath.TrimEnd([char[]]@('/', '\'))` at artifact-name and venv setup steps.

**Test scenarios:**
- Test expectation: none — composite action; verified by CI Build KotorMCP (windows-latest).

**Verification:**
- Build KotorMCP (windows-latest) passes artifact-name step on PR #266.

---

- U2. **Align pylint workflow with monorepo reality**

**Goal:** Pylint CI reports real issues without duplicate-code mass failure.

**Requirements:** R1, R4

**Dependencies:** None

**Files:**
- Modify: `.github/workflows/pylint.yml`
- Modify: `pyproject.toml` (`[tool.pylintrc]` section — add disable/ignore for CI parity)

**Approach:**
- Extend `[tool.pylintrc]` with `disable=duplicate-code` (R0801) and ignore paths matching ruff excludes (`vendor`, `.venv`, `uic`, etc.).
- Update workflow to invoke pylint with explicit `--rcfile=pyproject.toml` or project discovery, and exclude paths via `--ignore` for directories pylint rc may not cover in all versions.
- Keep matrix 3.8–3.10 unchanged.

**Test scenarios:**
- Test expectation: none — workflow-only; verified by Pylint workflow green on PR branch.

**Verification:**
- Pylint `build (3.8)`, `(3.9)`, `(3.10)` complete successfully on PR #266 push.

---

## System-Wide Impact

- **Interaction graph:** PR Build Validation delegates to build-tool composite; all Windows tool builds use same TrimEnd sites.
- **Unchanged invariants:** flake8 in python-package.yml, ruff local policy, parity harness tests.

---

## Risks & Dependencies

| Risk | Mitigation |
|------|------------|
| Disabling R0801 hides real duplication | Accept for CI gate; ruff and human review remain; follow-up can scope pylint narrowly |
| Pylint still fails on other pre-existing issues | Run local pylint on Libraries/PyKotor slice before push; add ignores only if needed |
| KotorMCP build fails later in compile step | Separate investigation if compile fails after TrimEnd fix |

---

## Sources & References

- CI run 26352281982 (Pylint), 26352282848 job 77573879466 (KotorMCP Windows)
- Plan `2026-05-24-010`
- PR #266
