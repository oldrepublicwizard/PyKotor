# GFF Diff Semantics and Reva Engine Research

## GFF Diff Output (Canonical, Industry-Standard)

The diff tool produces **canonical output** that clearly distinguishes:

| Category | Meaning | Example |
|----------|---------|---------|
| **MODIFIED** | Same logical entry, different fields (field-level diff shown) | Creature ResRef match, GuaranteedCount added |
| **ADDED** | Entry present only in new file | New creature in CreatureList |
| **REMOVED** | Entry present only in old file | Creature removed |
| **REORDERED** | Same entry, different index, no field changes | List reorder |
| **Summary** | `X modified, Y added, Z removed, W reordered` | Per-list totals |

When the **only** differences are ignorable (e.g., optional K2 field with default value, string whitespace/CRLF), the files report **MATCHES** with no spurious output.

## GFF List Semantic Identity Matching

When comparing GFF lists, the diff tool uses **semantic identity** for known list types to avoid false "added + removed" reports. For example, UTE `CreatureList` entries with the same creature (ResRef, CR, Appearance, SingleSpawn) but different optional fields (e.g., GuaranteedCount in K2) are matched by identity; if the only diff is ignorable, they are treated as **identical**.

### Registry: `_GFF_LIST_SEMANTIC_REGISTRY`

Located in `gff_data.py`. Maps `(GFFContent, list_field_name)` → `GFFListSemanticConfig`:

| GFF Type | List Field   | Identity Fields                         | Default When Absent   | Ignorable When Value |
|----------|--------------|-----------------------------------------|------------------------|----------------------|
| UTE      | CreatureList | ResRef, CR, SingleSpawn                 | GuaranteedCount: 0, Appearance: 0 | GuaranteedCount: 0   |

### Registry: `_GFF_IGNORABLE_FIELD_VALUES`

Maps `GFFContent` → `{field_name: {value1, value2, ...}}`. Fields added/removed with these values are not reported (engine default when absent).

| GFF Type | Field            | Ignorable Values | Engine Note                    |
|----------|------------------|------------------|--------------------------------|
| UTE      | GuaranteedCount  | {0}              | K2-only; engine reads 0 when absent |

### Adding New Semantic Configs

```python
_GFF_LIST_SEMANTIC_REGISTRY[(GFFContent.UTC, "ItemList")] = GFFListSemanticConfig(
    identity_fields=("InventoryRes", "ItemStackSize"),
    default_when_absent={"Repos_Pos": 0},
    ignorable_when_value={"Repos_Pos": 0},
)
```

### Adding Ignorable Fields

```python
_GFF_IGNORABLE_FIELD_VALUES[GFFContent.UTE]["GuaranteedCount"] = {0}
```

## String Normalization

GFF string fields are normalized before comparison to avoid false positives from:

- CRLF vs LF line endings
- Trailing whitespace per line and overall

See `_normalize_string_for_compare()` in `gff_data.py`.

Confirmed executable-derived generic-field findings are centralized in `wiki/reverse_engineering_findings.md`.

## Default and Ignorable Fields

When `ignore_default_changes=True` (default for GFF diff):

- Fields added with default values (0, empty, -1, or values in `_GFF_IGNORABLE_FIELD_VALUES`) are not reported
- String fields are normalized (CRLF, trailing whitespace) before comparison
- Semantic config `default_when_absent` is used for **identity matching** so same-identity entries are correctly paired
