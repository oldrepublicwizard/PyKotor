# Assembly / Binary → Code Transpile Parity Skill

## When to use

Use this skill when you need to **decompile, disassemble, or transpile** binary/assembly code (e.g. from game executables or RE tooling) into a high-level language (C/C++, Python, etc.) with **exhaustive, 1:1 parity** and **no placeholders or simplifications**. The skill uses **subagents** with different instructions to produce multiple implementations and then **compare them** for accuracy and completeness.

**Triggers:**
- "decompile assembly to Python/C/C++"
- "transpile disassembly to code with parity"
- "1:1 implementation from binary / reverse engineering"
- "ensure parity between disassembly and high-level code"
- "exhaustive implementation from agdec / Ghidra / get-function"

## Prerequisites

- **MCP (agdec-http)** must be available for disassembly (e.g. `get-function`, `list-functions`, `search-everything`). Ensure a Ghidra project has the target binary loaded before calling tools.
- **Program path** (e.g. `/K1/k1_win_gog_swkotor.exe`, `/TSL/k2_win_gog_aspyr_swkotor2.exe`) must be known for `get-function` and related calls.

## Workflow

### 1. Gather Disassembly (no placeholders)

- Call **get-function** for every function that is part of the target behavior (entry points and all callees to a chosen depth, e.g. 2–3).
- Record **full disassembly** and any decompiler output. If the decompiler returns "Fallback decompilation (decompiler unavailable)", treat **disassembly as the source of truth** and derive control flow, data flow, and constants from it.
- For each function: list **call sites, constants, and branches** (jump targets, error paths, success paths). Document **offsets and struct fields** (e.g. `[this+0x100c8]`) from the binary.
- Build a **single source-of-truth doc** (e.g. `SAVE_LOAD_ENGINE_BEHAVIOR.md` or a RE report) that enumerates every step and branch with zero omissions.

### 2. Subagent A: Primary language (e.g. Python)

- Launch a **subagent** with instructions to:
  - Read the disassembly and the behavior doc.
  - Produce **exhaustive** high-level code in the **primary language** (e.g. Python) that implements **every branch, every call, and every constant** from the disassembly.
  - **Forbidden:** placeholders (e.g. `# TODO`), "simplified" logic, or skipping error paths. If an engine calls GetDirectorySize and compares to `[this+0x100c8]`, the code must either implement that check or accept a parameter for the required value and document the mapping.
  - Output: a single implementation (file or module) plus a short list of "assumptions" (e.g. "required_bytes from [this+0x100c8] passed in as parameter").

### 3. Subagent B: Alternate language or same language, different instructions

- Launch a **second subagent** with instructions to:
  - Use the **same** disassembly and behavior doc.
  - Produce **exhaustive** code in an **alternate language** (e.g. C or C++) **or** the same language but written from a different angle (e.g. "implement from a data-flow perspective" vs "implement from a control-flow perspective").
  - Same rules: no placeholders, no simplifications; every branch and constant must appear.

### 4. Parity comparison

- **Compare** the two implementations:
  - Same **sequence of operations** (order of steps).
  - Same **branches** (error path, success path, conditional skip e.g. "skip screenshot if path == alias").
  - Same **constants** (magic numbers, offsets, thresholds).
  - Same **API surface** (functions called; parameters; return values).
- Produce a **parity report**: list items that match, and any **discrepancy** (e.g. one impl has a check the other misses). Resolve discrepancies by re-reading the disassembly and updating one or both implementations until parity is achieved.

### 5. Final deliverable

- **Exhaustive code** in the requested language(s), with:
  - No omissions: every step from the behavior doc is present.
  - No placeholders: no "TODO" or "simplified"; use parameters or documented assumptions where the runtime context (e.g. `this`, global addresses) is not available.
  - **Comments** that cite binary addresses and offsets (e.g. "K1 SaveGame @ 004b58a0"; "[EDI+0x100c8]").
- A short **verification** section: how to confirm behavior (e.g. unit tests, golden SAV roundtrip, or manual checklist against the behavior doc).

## Subagent prompt templates

**Primary (e.g. Python):**
"You are implementing [FEATURE] from binary disassembly. Source of truth: [BEHAVIOR_DOC] and get-function disassembly for [FUNCTIONS]. Produce exhaustive [LANGUAGE] code: every branch, every constant, every error path. No placeholders, no TODOs, no simplifications. Cite binary addresses in comments. If the binary uses [this+OFFSET] or globals, use a parameter or documented constant."

**Alternate (e.g. C or second pass):**
"Same as primary but implement in [ALT_LANGUAGE] (or same language from a control-flow-first perspective). Same rules: exhaustive, no placeholders. Every step in [BEHAVIOR_DOC] must appear."

**Parity checker:**
"Compare IMPL_A and IMPL_B. List: (1) steps present in both, (2) steps only in A, (3) steps only in B, (4) constants/branches that differ. Flag any discrepancy as a parity failure and cite the disassembly line that decides the correct behavior."

## Integration with agdec-http

- **get-function**: primary source for disassembly and decompilation. Use `program_path` and function address (e.g. `004b58a0`).
- **list-functions** / **search-symbols**: to find all related symbols (e.g. SaveGame, LoadGame, GetFreeDiskSpace).
- **list-cross-references**: to ensure no caller or callee is missed when building the behavior doc.

Wiki and user-facing docs remain **conceptual**; do not put raw RE dumps or tool names in end-user-facing markdown. Keep addresses and offsets in code comments and internal RE reports.

## Success criteria

- Disassembly fully reflected in at least one high-level implementation.
- Two implementations (from two subagents) compared; parity report shows no unresolved discrepancies.
- Deliverable is **exhaustive and complete** with **zero omissions, placeholders, or simplifications** relative to the agreed behavior doc.
