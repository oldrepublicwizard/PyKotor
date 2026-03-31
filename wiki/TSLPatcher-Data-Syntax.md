# TSLPatcher Data Syntax

TSLPatcher’s `changes.ini` can patch 2DA tables and TLK string databases alongside GFF edits. The sections below document the `[2DAList]` and `[TLKList]` directive syntax that HoloPatcher and TSLPatcher both support.

## Contents

- [2DAList Syntax — Two-Dimensional Array Modifications](#2dalist-syntax)
- [TLKList Syntax — Talk Table Modifications](#tlklist-syntax)

---

<a id="2dalist-syntax"></a>

# TSLPatcher 2DAList Syntax - Complete Guide

This guide explains how to modify [2DA files](2DA-File-Format) using TSLPatcher syntax. For the complete [2DA file](2DA-File-Format) format specification, see [2DA File Format](2DA-File-Format). For general TSLPatcher information, see [TSLPatcher's Official Readme](TSLPatcher's-Official-Readme). For HoloPatcher-specific information, see [HoloPatcher README for Mod Developers](HoloPatcher#mod-developers).

## Overview

The `[2DAList]` section in TSLPatcher's `changes.ini` enables you to modify 2DA (Two-Dimensional array) files used throughout KotOR and TSL. [2DA files](2DA-File-Format) are tabular data structures that store game information such as appearances, classes, feats, items, spells, and more. You can change existing rows, add new rows, copy rows, and add columns using various targeting methods and value types.

The `[2DAList]` section is processed **after** `[TLKList]` but **before** `[GFFList]` in HoloPatcher, meaning you can use `StrRef#` tokens from [TLKList](TSLPatcher-Data-Syntax#tlklist-syntax), and any `2DAMEMORY#` tokens you create will be available to [GFFList](TSLPatcher-GFF-Syntax#gfflist-syntax) and other sections.

## Table of Contents

- [Quick Start](#quick-start)
- [Cheatsheet](#cheatsheet)
- [Basic Structure](#basic-structure)
- [Processing Order](#processing-order)
- [File-Level Configuration](#file-level-configuration)
- [Modification Types](#modification-types)
  - [ChangeRow - Modify Existing Row](#changerow---modify-existing-row)
  - [AddRow - Add New Row](#addrow---add-new-row)
  - [CopyRow - Copy and Conditionally Add Row](#copyrow---copy-and-conditionally-add-row)
  - [AddColumn - Add New Column](#addcolumn---add-new-column)
- [Target Types](#target-types)
- [Cell Values and RowValue Types](#cell-values-and-rowvalue-types)
- [Memory Token System](#memory-token-system)
- [Special Functions](#special-functions)
- [Examples](#examples)
- [Common Pitfalls and Troubleshooting](#common-pitfalls-and-troubleshooting)
- [Integration with Other Sections](#integration-with-other-sections)

## Quick Start

<!-- markdownlint-disable MD029 -->
1. Add your [2DA file](2DA-File-Format) under `[2DAList]`:

```ini
[2DAList]
Table0=appearance.2da
```

2. Create a section named exactly like that file:

```ini
[appearance.2da]
ChangeRow0=modify_appearance
```

3. Create the modification section to change a row:

```ini
[modify_appearance]
RowIndex=5
label=CUSTOM_APPEARANCE
modeltype=1
```

4. Store values for later use with `2DAMEMORY#` tokens:

```ini
[modify_appearance]
RowIndex=5
label=CUSTOM_APPEARANCE
2DAMEMORY10=RowIndex
2DAMEMORY11=label
```

5. Use tokens from TLKList or other [2DA](2DA-File-Format) modifications:

```ini
[add_new_appearance]
label=MY_NEW_APPEARANCE
name=StrRef50
appearance=2DAMEMORY10
```
<!-- markdownlint-enable MD029 -->

## Cheatsheet

- **Modification types**: `ChangeRow#`, `AddRow#`, `CopyRow#`, `AddColumn#`
- **Row targeting**:
  - `RowIndex=#` --> Target by numeric row index (0-based)
  - `RowLabel=label` --> Target by row label (first column value)
  - `LabelIndex=value` --> Find row where "label" column equals value
- **Cell values**:
  - `ColumnName=value` --> Set cell to constant string
  - `ColumnName=[StrRef](Audio-and-Localization-Formats#string-references-strref)#` --> Use [TLK](Audio-and-Localization-Formats#tlk) stringref token
  - `ColumnName=2DAMEMORY#` --> Use [2DA](2DA-File-Format) memory token
  - `ColumnName=high()` --> Maximum value in that column
  - `ColumnName=RowIndex` --> Current row's index
  - `ColumnName=RowLabel` --> Current row's label
  - `ColumnName=RowCell('column')` --> value from another cell
  - `ColumnName=****` --> Empty string
- **Memory storage**:
  - `2DAMEMORY#=RowIndex` --> Store row index
  - `2DAMEMORY#=RowLabel` --> Store row label
  - `2DAMEMORY#=ColumnName` --> Store cell value from that column
  - `[StrRef](Audio-and-Localization-Formats#string-references-strref)#=value` --> Store stringref for later use
- **Special row properties**:
  - `RowLabel=value` --> Set row label (for AddRow/CopyRow)
  - `NewRowLabel=value` --> Alternative name for RowLabel
  - `ExclusiveColumn=name` --> Check for existing row by column value (AddRow/CopyRow)

## Basic structure

```ini
[2DAList]
!DefaultDestination=override
!DefaultSourceFolder=.
Table0=appearance.2da
Replace0=classes.2da

[appearance.2da]
!Destination=override
!SourceFolder=.
!SourceFile=custom_appearance.2da
!ReplaceFile=0
!SaveAs=appearance.2da
ChangeRow0=modify_row_1
AddRow0=add_new_row
CopyRow0=copy_existing_row
AddColumn0=add_new_column

[modify_row_1]
RowIndex=5
label=CUSTOM_APPEARANCE
modeltype=1

[add_new_row]
ExclusiveColumn=label
RowLabel=10
label=NEW_APPEARANCE
name=StrRef100

[copy_existing_row]
RowLabel=1
ExclusiveColumn=label
NewRowLabel=9
label=COPIED_APPEARANCE

[add_new_column]
ColumnLabel=NewColumn
DefaultValue=0
I5=CustomValue
L1=AnotherValue
```

The `[2DAList]` section declares which [2DA files](2DA-File-Format) you want to modify. Each entry (like `Table0`, `Table1`, etc., or `Replace0`, `Replace1`, etc.) references another section with the same name as the filename.

**Syntax Notes:**

- Use `Table#` to add a new [2DA file](2DA-File-Format) modification (non-replacing)
- Use `Replace#` to replace an existing [2DA file](2DA-File-Format) before applying modifications
- The `#` is a sequential number starting from 0 (Table0, Table1, Table2, etc.)
- Numbers can be sequential, but gaps are allowed (Table0, Table2, Table5 is valid)
- Each file section contains modification entries (`ChangeRow#`, `AddRow#`, `CopyRow#`, `AddColumn#`)

## Processing Order

In **HoloPatcher**, the 2DAList runs in the following execution order:

1. **[InstallList]** - files are installed first
2. **[TLKList]** - [TLK](Audio-and-Localization-Formats#tlk) modifications (creates `StrRef#` tokens)
3. **[2DAList]** ← **You are here** - [2DA file](2DA-File-Format) modifications (creates `2DAMEMORY#` tokens)
4. **[GFFList]** - [GFF file](GFF-File-Format) modifications (can use `StrRef#` and `2DAMEMORY#` tokens)
5. **[CompileList]** - Script compilation (can use `[StrRef](Audio-and-Localization-Formats#string-references-strref)#` and `2DAMEMORY#` tokens)
6. **[HACKList]** - Binary hacking (can use `[StrRef](Audio-and-Localization-Formats#string-references-strref)#` and `2DAMEMORY#` tokens)
7. **[SSFList]** - Sound set modifications (can use `[StrRef](Audio-and-Localization-Formats#string-references-strref)#` and `2DAMEMORY#` tokens)

**Important:** Since 2DAList runs after TLKList, you can use `[StrRef](Audio-and-Localization-Formats#string-references-strref)#` tokens in your [2DA](2DA-File-Format) modifications. Any `2DAMEMORY#` tokens you create will be available to all subsequent sections (GFFList, CompileList, HACKList, SSFList).

## file-Level Configuration

### Top-Level Keys in [2DAList]

| [KEY](Container-Formats#key) | type | Default | Description |
|-----|------|---------|-------------|
| `!DefaultDestination` | string | `override` | Default destination for all [2DA files](2DA-File-Format) in this section |
| `!DefaultSourceFolder` | string | `.` | Default source folder for [2DA files](2DA-File-Format). Relative path from `mod_path` (typically the `tslpatchdata` folder, which is the parent directory of `changes.ini` and `namespaces.ini`). When `.`, refers to the `tslpatchdata` folder itself. Path resolution: `mod_path / !DefaultSourceFolder / filename` |

### file Section Configuration

Each [2DA file](2DA-File-Format) requires its own section (e.g., `[appearance.2da]`).

| Key | type | Default | Description |
|-----|------|---------|-------------|
| `!Destination` | string | Inherited from `!DefaultDestination` | Where to save the modified file (`override` or `path\to\file.mod`) |
| `!SourceFolder` | string | Inherited from `!DefaultSourceFolder` | Source folder for the [2DA file](2DA-File-Format). Relative path from `mod_path` (typically the tslpatchdata folder). When `.`, refers to the tslpatchdata folder itself. |
| `!SourceFile` | string | Same as section name | Alternative source filename (useful for multiple setup options using different source files) |
| `!ReplaceFile` | 0/1 | 0 | If `1`, overwrite existing file before applying modifications. If `0` (default), modify the existing file in place. |
| `!SaveAs` | string | Same as section name | Alternative filename to save as (useful for renaming files during installation) |
| `!OverrideType` | string | `warn` (HoloPatcher) / `ignore` (TSLPatcher) | How to handle existing files in Override when destination is an [ERF](Container-Formats#erf) or [RIM](Container-Formats#rim) container. Valid values: `ignore`, `warn`, `rename` |

**Destination values:**

- `override` or empty: Save to the Override folder
- `Modules\module.mod`: Insert into a [MOD](Container-Formats#erf), [ERF](Container-Formats#erf), or [RIM](Container-Formats#rim) container (use backslashes for path separators)
- Container paths must be relative to the game folder root

**Syntax Notes:**

- `!DefaultSourceFolder` and `!SourceFolder` default to `.` which refers to the `tslpatchdata` folder itself
- When specifying paths, use backslashes (`\`) as path separators (TSLPatcher style), though forward slashes (`/`) are also accepted and normalized
- Path resolution: `mod_path / !SourceFolder / !SourceFile` (or section name if `!SourceFile` is not set)

## Modification types

### ChangeRow - Modify Existing Row

**Syntax:** `ChangeRow#=section_name`

Changes an existing row in the [2DA file](2DA-File-Format). You must specify which row to modify using one of the target types (see [Target Types](#target-types)).

**Required Keys:**

- One of: `RowIndex`, `RowLabel`, or `LabelIndex` (to identify which row to modify)

**Optional Keys:**

- Any column name (to modify cell values)
- `2DAMEMORY#=value` (to store values in memory)
- `[StrRef](Audio-and-Localization-Formats#string-references-strref)#=value` (to store stringref values in memory)

**Example:**

```ini
[2DAList]
Table0=appearance.2da

[appearance.2da]
ChangeRow0=modify_appearance_5

[modify_appearance_5]
RowIndex=5
label=CUSTOM_APPEARANCE
modeltype=1
```

**Example with Memory Storage:**

```ini
[modify_appearance_5]
RowIndex=5
label=CUSTOM_APPEARANCE
modeltype=1
2DAMEMORY10=RowIndex      ; Store row index (5) in memory token 10
2DAMEMORY11=RowLabel      ; Store row label in memory token 11
2DAMEMORY12=modeltype     ; Store modeltype value in memory token 12
StrRef20=name             ; Store name stringref in TLK memory token 20
```

**Behavior:**

- If the target row is not found, a warning is logged and the modification is skipped
- Existing cell values are overwritten with new values
- Columns that are not specified remain unchanged
- Memory tokens are evaluated and stored after cell modifications are applied

### AddRow - Add New Row

**Syntax:** `AddRow#=section_name`

Adds a new row to the [2DA file](2DA-File-Format). If `ExclusiveColumn` is specified and a row with that value already exists, the existing row is modified instead of adding a new one.

**Required Keys:**

- None (empty section creates a row with default/empty values)

**Optional Keys:**

- `ExclusiveColumn=column_name` --> Check if a row with the same value in this column already exists; if so, modify it instead of adding
- `RowLabel=value` or `NewRowLabel=value` --> Set the row label (defaults to current row count if not specified)
- Any column name (to set cell values)
- `2DAMEMORY#=value` (to store values in memory)
- `[StrRef](Audio-and-Localization-Formats#string-references-strref)#=value` (to store stringref values in memory)

**Example:**

```ini
[appearance.2da]
AddRow0=add_new_appearance

[add_new_appearance]
ExclusiveColumn=label
RowLabel=100
label=MY_NEW_APPEARANCE
name=StrRef200
modeltype=2
```

**Example with Exclusive Column (Prevent Duplicates):**

```ini
[add_new_appearance]
ExclusiveColumn=label
label=MY_NEW_APPEARANCE
name=StrRef200
```

If a row with `label=MY_NEW_APPEARANCE` already exists, it will be modified. Otherwise, a new row will be added.

**Behavior:**

- New row is added with the specified cell values
- If `ExclusiveColumn` is specified and a matching row exists, that row is updated instead
- Row label defaults to the current row count (as a string) if `RowLabel`/`NewRowLabel` is not specified
- Memory tokens are evaluated and stored after the row is added/modified

### CopyRow - Copy and Conditionally Add Row

**Syntax:** `CopyRow#=section_name`

Copies an existing row (identified by a target) and optionally adds it as a new row or modifies an existing one if `ExclusiveColumn` matches.

**Required Keys:**

- One of: `RowIndex`, `RowLabel`, or `LabelIndex` (to identify the source row to copy)

**Optional Keys:**

- `ExclusiveColumn=column_name` --> If a row with the same value in this column already exists, modify that row instead of adding a new one
- `RowLabel=value` or `NewRowLabel=value` --> Set the new row's label (defaults to current row count if not specified)
- Any column name (to override cell values from the copied row)
- `2DAMEMORY#=value` (to store values in memory)
- `[StrRef](Audio-and-Localization-Formats#string-references-strref)#=value` (to store stringref values in memory)

**Example:**

```ini
[appearance.2da]
CopyRow0=copy_appearance_1

[copy_appearance_1]
RowLabel=1
ExclusiveColumn=label
NewRowLabel=50
label=COPIED_APPEARANCE
name=StrRef300
```

**Example - Copy and Modify:**

```ini
[copy_appearance_1]
RowIndex=5
ExclusiveColumn=label
label=MODIFIED_COPY
modeltype=3
```

**Behavior:**

- The source row (identified by target) is copied
- All cell values from the source row are preserved unless overridden
- If `ExclusiveColumn` is specified and a matching row exists, that existing row is updated
- If `ExclusiveColumn` is not specified or no match is found, a new row is added
- If the source row is not found, an error is raised
- Memory tokens are evaluated and stored after the row is copied/modified

### AddColumn - Add New Column

**Syntax:** `AddColumn#=section_name`

Adds a new column to the [2DA file](2DA-File-Format) with a default value for all rows. Specific rows can be given custom values using index or label-based inserts.

**Required Keys:**

- `ColumnLabel=column_name` --> The name of the new column
- `DefaultValue=value` --> Default value for all rows (use `****` for empty string)

**Optional Keys:**

- `I#=value` --> Set value for row at index `#` (e.g., `I5=CustomValue` sets row index 5)
- `Llabel=value` --> Set value for row with label `label` (e.g., `L1=CustomValue` sets row with label "1")
- `2DAMEMORY#=I#` or `2DAMEMORY#=Llabel` --> Store the cell value from the new column into memory token `#` after the column is created
  - Use `I#` format to reference by row index (e.g., `2DAMEMORY10=I5` stores the value from row index 5 in the new column)
  - Use `Llabel` format to reference by row label (e.g., `2DAMEMORY10=L1` stores the value from the row with label "1" in the new column)
  - Memory storage happens **after** the column is created and all insert values are applied

**Example:**

```ini
[appearance.2da]
AddColumn0=add_custom_column

[add_custom_column]
ColumnLabel=CustomColumn
DefaultValue=0
I5=SpecialValue
L1=AnotherValue
2DAMEMORY10=I5
```

**Example with Memory Storage:**

```ini
[add_custom_column]
ColumnLabel=NewProperty
DefaultValue=****
I0=ValueForRow0
I1=ValueForRow1
L5=ValueForLabel5
2DAMEMORY20=I0    ; Store value from row index 0 after column is created
2DAMEMORY21=L5    ; Store value from row label 5 after column is created
```

**Behavior:**

- New column is added to all rows
- All rows initially receive the `DefaultValue`
- Rows specified in `I#` or `Llabel` entries get their custom values
- If a row specified in `I#` doesn't exist, an error is raised
- If a row specified in `Llabel` doesn't exist, an error is raised
- **Memory Storage:** Memory tokens specified with `2DAMEMORY#=I#` or `2DAMEMORY#=Llabel` store the cell value from the new column **after** it's created and all insert values are applied
  - `2DAMEMORY#=I5` retrieves the cell value from row index 5 in the newly created column
  - `2DAMEMORY#=L1` retrieves the cell value from the row with label "1" in the newly created column
  - This allows you to capture values from the new column for use in later modifications

**Special value Syntax in AddColumn:**

For `I#` and `Llabel` values (the right side of the assignment), you can use:

- Constant strings: `I5=CustomValue`
- Token references: `I5=2DAMEMORY10`, `I5=StrRef20`
- Special functions (`high()`, `RowIndex`, `RowLabel`) are **not supported** in AddColumn (unlike ChangeRow/AddRow/CopyRow)

**Memory Storage Syntax:**

For memory storage (`2DAMEMORY#=`), you must use:

- `2DAMEMORY#=I#` - Store value from row at index `#` in the new column
- `2DAMEMORY#=Llabel` - Store value from row with label `label` in the new column

The `I#` and `Llabel` on the right side of `2DAMEMORY#=` refer to which row's value to store from the newly created column, not the value to insert.

## Target types

Target types identify which row to modify in ChangeRow and CopyRow operations. Only one target type can be specified per modification.

### RowIndex

**Syntax:** `RowIndex=integer`

Targets a row by its numeric index (0-based).

**Example:**

```ini
[modify_row]
RowIndex=5
label=MODIFIED
```

**Behavior:**

- Directly accesses the row at the specified index
- If the index is out of bounds, the row is not found and a warning is logged
- The value must be a valid integer
- **Dynamic targeting**: Can use `2DAMEMORY#` tokens for dynamic row selection (e.g., `RowIndex=2DAMEMORY10` will use the value stored in token 10)

### RowLabel

**Syntax:** `RowLabel=label_string`

Targets a row by its label (the value in the first column, typically named "label").

**Example:**

```ini
[modify_row]
RowLabel=1
label=MODIFIED
```

**Behavior:**

- Searches for a row where the row label matches the specified value
- Uses string comparison (case-sensitive)
- If no matching row is found, a warning is logged
- **Dynamic targeting**: RowLabel can accept token references for dynamic row selection:
  - `RowLabel=2DAMEMORY10` - Uses the value stored in [2DA](2DA-File-Format) memory token 10
  - `RowLabel=StrRef20` - Uses the stringref value from [TLK](Audio-and-Localization-Formats#tlk) memory token 20 (converted to string)
- This allows you to dynamically determine which row to modify based on previously stored values

### LabelIndex

**Syntax:** `LabelIndex=value`

Targets a row by searching the "label" column for a matching value. This is different from `RowLabel` because it searches within a specific column named "label" rather than using the row's label value.

**Example:**

```ini
[modify_row]
LabelIndex=MY_APPEARANCE
label=MODIFIED
```

**Behavior:**

- Requires the [2DA](2DA-File-Format) to have a column named "label"
- Searches all rows for a cell in the "label" column that matches the specified value
- If the "label" column doesn't exist, an error is raised
- If no matching row is found, a warning is logged
- **Dynamic targeting**: LabelIndex can accept token references for dynamic row selection:
  - `LabelIndex=2DAMEMORY10` - Uses the value stored in [2DA](2DA-File-Format) memory token 10
  - `LabelIndex=StrRef20` - Uses the stringref value from [TLK](Audio-and-Localization-Formats#tlk) memory token 20 (converted to string)
- This allows you to dynamically search for rows based on previously stored values

**Note:** `RowLabel` and `LabelIndex` may seem similar, but they operate differently:

- `RowLabel` uses the row's label value (first column's value)
- `LabelIndex` searches within a column named "label" for a matching value

## Cell values and RowValue types

When setting cell values in ChangeRow, AddRow, and CopyRow, you can use various value types. Each cell value is parsed as a `RowValue` type based on the syntax.

### Constant string values

**Syntax:** `ColumnName=any_string`

The simplest value type - a literal string that will be placed in the cell.

**Example:**

```ini
label=CUSTOM_APPEARANCE
modeltype=1
description=This is a custom appearance
```

### Empty string

**Syntax:** `ColumnName=****`

Use `****` to set a cell to an empty string.

**Example:**

```ini
comment=****
notes=****
```

### Token References

#### [StrRef](Audio-and-Localization-Formats#string-references-strref) Tokens

**Syntax:** `ColumnName=[StrRef](Audio-and-Localization-Formats#string-references-strref)#`

References a stringref token created in the `[TLKList]` section. The token number is extracted and the value is looked up from [TLK](Audio-and-Localization-Formats#tlk) memory.

**Example:**

```ini
name=StrRef50
description=StrRef100
```

**Behavior:**

- Token must be defined in `[TLKList]` before use
- value stored in the token is used as the cell value
- If token is not found, an error is raised

#### 2DAMEMORY Token References(#2damemory-token-references)

**Syntax:** `ColumnName=2DAMEMORY#`

References a [2DA](2DA-File-Format) memory token created in a previous 2DAList modification. The token number is extracted and the value is looked up from [2DA](2DA-File-Format) memory.

**Example:**

```ini
appearance=2DAMEMORY10
model=2DAMEMORY5
```

**Behavior:**

- Token must be defined earlier in the same or a previous [2DA file](2DA-File-Format) modification
- value stored in the token (as a string) is used as the cell value
- If token is not found, an error is raised
- **Important:** `!FieldPath` tokens (used in GFFList) cannot be used here - only string values are supported
- The token value is looked up from `memory.memory_2da[token_id]` at runtime
- If the token contains a `PureWindowsPath` (from GFFList `!FieldPath`), a `TypeError` will be raised

### Special Functions

#### high() - Maximum value

**Syntax:** `ColumnName=high()` or `ColumnName=high(column_name)`

Returns the maximum value from a column or the maximum row label.

**Without Column Name:**

```ini
RowLabel=high()    ; Maximum row label (used when setting row label)
forcehostile=high()  ; Maximum value in the "forcehostile" column
```

**With Column Name:**

```ini
forcehostile=high(modeltype)  ; Maximum value from "modeltype" column
```

**Behavior:**

- `high()` without column name in `RowLabel` context returns the maximum row label
- `high()` without column name in a cell context returns the maximum value from that cell's column
- `high(column)` returns the maximum value from the specified column
- values are compared as integers if possible, otherwise as strings
- Only works in ChangeRow, AddRow, and CopyRow (not in AddColumn)

#### RowIndex - Current Row index

**Syntax:** `ColumnName=RowIndex`

Returns the numeric index of the current row as a string.

**Example:**

```ini
index_value=RowIndex
```

**Behavior:**

- Returns the row index (0-based) as a string
- Only works in ChangeRow, AddRow, and CopyRow cell values
- Cannot be used as a target (use `RowIndex=#` for targeting)

#### RowLabel - Current Row Label

**Syntax:** `ColumnName=RowLabel`

Returns the label of the current row (value in the first column).

**Example:**

```ini
label_copy=RowLabel
```

**Behavior:**

- Returns the row's label value as a string
- Only works in ChangeRow, AddRow, and CopyRow cell values
- Cannot be used as a target (use `RowLabel=value` for targeting)

#### RowCell - value from Another Cell

**Syntax:** `ColumnName=RowCell('column_name')`

**Note:** This syntax is not directly supported in the INI format. In practice, you would reference a column name directly to get its value, or use `2DAMEMORY#` tokens. The `RowCell` type exists internally but is primarily used for memory storage operations.

**For Memory Storage:**

```ini
2DAMEMORY10=modeltype  ; Stores value from "modeltype" column (this internally uses RowCell)
```

## Memory Token System

The memory token system allows you to store values from [2DA](2DA-File-Format) modifications for use in other sections or later modifications.

### 2DAMEMORY Tokens

**Syntax:** `2DAMEMORY#=value_source`

Stores a value in [2DA](2DA-File-Format) memory at token `#`. The token number can be any non-negative integer (typically starting from 0 or 1).

**Available value Sources:**

| value Source | Description | Example | Internal type |
|--------------|-------------|---------|---------------|
| `RowIndex` | Store the row's numeric index (0-based) as string | `2DAMEMORY10=RowIndex` | `RowValueRowIndex()` |
| `RowLabel` | Store the row's label value (first column) | `2DAMEMORY11=RowLabel` | `RowValueRowLabel()` |
| `ColumnName` | Store the value from a specific column in the current row | `2DAMEMORY12=modeltype` | `RowValueRowCell(column)` |
| `StrRef#` | Store the stringref value from a [TLK](Audio-and-Localization-Formats#tlk) token (converted to string) | `2DAMEMORY13=StrRef50` | `RowValueTLKMemory(token_id)` |
| `2DAMEMORY#` | Copy value from another [2DA](2DA-File-Format) token | `2DAMEMORY14=2DAMEMORY10` | References existing token |

**Note:** The internal types listed above are runtime evaluation objects that compute values when the modification is applied. They are **only used for storage operations** (left side of `2DAMEMORY#=`), not for cell value assignments (right side of `ColumnName=`).

**Example - Storing Multiple values:**

```ini
[modify_appearance]
RowIndex=5
label=CUSTOM_APPEARANCE
modeltype=1
2DAMEMORY10=RowIndex      ; Stores "5"
2DAMEMORY11=RowLabel      ; Stores "CUSTOM_APPEARANCE" or row label value
2DAMEMORY12=modeltype     ; Stores "1"
```

**Example - Using Stored values:**

```ini
[add_new_appearance]
label=ANOTHER_APPEARANCE
modeltype=2DAMEMORY12     ; Use stored modeltype value
appearance=2DAMEMORY10    ; Use stored row index
```

**Behavior:**

- Tokens are stored as strings in [2DA](2DA-File-Format) memory (`memory.memory_2da[token_id]`)
- **Evaluation Order:** Memory storage operations (`2DAMEMORY#=...`) are evaluated **after** all cell modifications are applied within the same modification section
- This means you cannot use a token in a cell value (`ColumnName=2DAMEMORY#`) and create it (`2DAMEMORY#=...`) in the same section - create tokens in earlier modifications
- Tokens are available to all subsequent sections (GFFList, CompileList, HACKList, SSFList)
- Tokens persist across multiple [2DA file](2DA-File-Format) modifications within the same `[2DAList]` section
- If a token is referenced before being set, a `KeyError` is raised: `"2DAMEMORY{id} was not defined before use"`
- **Storage type:** values are stored as `str` type (or `PureWindowsPath` for GFFList `!FieldPath`, but those cannot be used in 2DAList)

### [StrRef](Audio-and-Localization-Formats#string-references-strref) Tokens ([TLK](Audio-and-Localization-Formats#tlk) Memory)

**Syntax:** `[StrRef](Audio-and-Localization-Formats#string-references-strref)#=value_source`

Stores a stringref value in [TLK](Audio-and-Localization-Formats#tlk) memory at token `#`. These tokens are primarily created in `[TLKList]`, but can also be set here.

**Available value Sources:**

| value Source | Description | Example |
|--------------|-------------|---------|
| `ColumnName` | Store the stringref from a specific column (value must be convertible to integer) | `StrRef20=name` |
| `StrRef#` | Copy stringref value from another [TLK](Audio-and-Localization-Formats#tlk) token | `StrRef21=StrRef20` |
| `2DAMEMORY#` | Store stringref from a [2DA](2DA-File-Format) token (value must be convertible to integer) | `StrRef22=2DAMEMORY10` |

**Example:**

```ini
[modify_appearance]
RowIndex=5
name=12345
StrRef30=name          ; Store stringref 12345 in token 30
StrRef31=StrRef30      ; Copy token 30 to token 31
```

**Behavior:**

- values are stored as integers in [TLK](Audio-and-Localization-Formats#tlk) memory
- The source value must be convertible to an integer (stringrefs are integers)
- Tokens are available to all subsequent sections
- [StrRef](Audio-and-Localization-Formats#string-references-strref) tokens are primarily used in GFFList for localized string fields

### Token Usage in Other Sections

Once created, `2DAMEMORY#` and `StrRef#` tokens can be used in:

1. **Later [2DA](2DA-File-Format) modifications** - Use in ChangeRow, AddRow, CopyRow, or AddColumn
2. **GFFList** - Use in field values, field paths, or TypeId fields
3. **CompileList** - Use as preprocessor tokens in [NSS](NSS-File-Format) scripts (`#2DAMEMORY#` and `#StrRef#`)
4. **HACKList** - Use in binary patch values
5. **SSFList** - Use for sound stringref assignments

**Example Cross-Section Usage:**

```ini
[2DAList]
Table0=appearance.2da

[appearance.2da]
AddRow0=new_appearance

[new_appearance]
RowLabel=100
label=MY_APPEARANCE
2DAMEMORY10=RowIndex

[GFFList]
File0=item.uti

[item.uti]
ModelVariation=2DAMEMORY10  ; Use the stored row index
```

## Examples

### Example 1: Modify Existing Appearance

```ini
[2DAList]
Table0=appearance.2da

[appearance.2da]
ChangeRow0=modify_human_male

[modify_human_male]
RowLabel=1
label=HUMAN_MALE
modeltype=1
2DAMEMORY10=RowIndex
```

### Example 1a: Dynamic Row Targeting with Tokens

```ini
[2DAList]
Table0=appearance.2da

[appearance.2da]
AddRow0=store_row_index

[store_row_index]
RowLabel=100
label=MY_APPEARANCE
2DAMEMORY10=RowIndex    ; Store the new row's index

[appearance.2da]
ChangeRow0=modify_using_token

[modify_using_token]
RowIndex=2DAMEMORY10    ; Dynamically target the row we just created
label=MODIFIED_APPEARANCE
modeltype=2
```

This demonstrates how you can store a row index in one modification and use it to target that row in a later modification.

### Example 2: Add New Appearance with Exclusive Check

```ini
[2DAList]
Table0=appearance.2da

[appearance.2da]
AddRow0=add_custom_appearance

[add_custom_appearance]
ExclusiveColumn=label
RowLabel=100
label=CUSTOM_APPEARANCE
name=StrRef500
modeltype=2
```

### Example 3: Copy Row and Modify

```ini
[2DAList]
Table0=appearance.2da

[appearance.2da]
CopyRow0=copy_and_modify

[copy_and_modify]
RowIndex=5
ExclusiveColumn=label
label=MODIFIED_COPY
modeltype=3
2DAMEMORY20=RowIndex
```

### Example 4: Add Column with Custom values

```ini
[2DAList]
Table0=appearance.2da

[appearance.2da]
AddColumn0=add_custom_property

[add_custom_property]
ColumnLabel=CustomProperty
DefaultValue=0
I5=100
L1=200
2DAMEMORY30=I5
```

### Example 5: Complex Multi-Row Modification

```ini
[2DAList]
Table0=appearance.2da

[appearance.2da]
ChangeRow0=modify_row_1
ChangeRow1=modify_row_2
AddRow0=add_new_row
CopyRow0=copy_row
AddColumn0=add_column

[modify_row_1]
RowIndex=1
label=MODIFIED_1
2DAMEMORY10=RowIndex

[modify_row_2]
RowLabel=2
label=MODIFIED_2
appearance=2DAMEMORY10

[add_new_row]
ExclusiveColumn=label
RowLabel=50
label=NEW_APPEARANCE
name=StrRef1000

[copy_row]
RowIndex=1
ExclusiveColumn=label
label=COPIED_APPEARANCE
modeltype=2DAMEMORY10

[add_column]
ColumnLabel=NewColumn
DefaultValue=****
I1=Value1
I2=Value2
L50=Value3
2DAMEMORY40=I1
```

### Example 6: Using Tokens from TLKList

```ini
[TLKList]
StrRef1000=Hello World

[2DAList]
Table0=appearance.2da

[appearance.2da]
AddRow0=new_appearance

[new_appearance]
RowLabel=100
label=MY_APPEARANCE
name=StrRef1000    ; Use token from TLKList
```

### Example 7: Cross-file Token Usage

```ini
[2DAList]
Table0=appearance.2da
Table1=classes.2da

[appearance.2da]
AddRow0=store_appearance

[store_appearance]
RowLabel=100
label=MY_APPEARANCE
2DAMEMORY10=RowIndex

[classes.2da]
ChangeRow0=use_appearance

[use_appearance]
RowIndex=5
appearance=2DAMEMORY10  ; Use token from previous file modification
```

## Common Pitfalls and Troubleshooting

### Row Not Found Errors

**Problem:** "The source row was not found during the search"

**Solutions:**

- Verify the target row exists (check RowIndex is within bounds, RowLabel matches exactly, or LabelIndex value exists in "label" column)
- Ensure case-sensitivity: `RowLabel=MyLabel` will not match `mylabel`
- Check that the [2DA file](2DA-File-Format) has been loaded correctly
- Verify `!SourceFile` is correct if using a custom source file

**Example Fix:**

```ini
; Before (may fail if row doesn't exist)
[modify_row]
RowIndex=999
label=MODIFIED

; After (check row exists first, or use safer targeting)
[modify_row]
RowLabel=1
label=MODIFIED
```

### Token Not Defined Errors

**Problem:** "2DAMEMORY# was not defined before use" or "[StrRef](Audio-and-Localization-Formats#string-references-strref)# was not defined before use"

**Solutions:**

- Ensure the token is created **before** it's used
- For 2DAMEMORY tokens: Create in an earlier modification in the same file or previous file
- For [StrRef](Audio-and-Localization-Formats#string-references-strref) tokens: Ensure they're created in `[TLKList]` or earlier in `[2DAList]`
- Check token numbers match exactly (no typos)

**Example Fix:**

```ini
; Wrong - token used before creation
[add_row]
label=NEW
appearance=2DAMEMORY10
2DAMEMORY10=RowIndex    ; Too late!

; Correct - token created first
[add_row]
label=NEW
2DAMEMORY10=RowIndex     ; Create first
appearance=2DAMEMORY10   ; Use after creation
```

**Note:** Within the same modification section, memory storage operations (`2DAMEMORY#=...`) are evaluated **after** cell modifications (`ColumnName=...`), so you cannot use a token in a cell value and create it in the same section.

**Example of the problem:**

```ini
; This will FAIL - token used before it's created
[add_row]
label=NEW
appearance=2DAMEMORY10    ; Tries to use token 10 (not yet created)
2DAMEMORY10=RowIndex      ; Creates token 10 (too late!)
```

**Solution:** Create tokens in earlier modifications, then use them in later ones.

### Invalid Column Names

**Problem:** Column doesn't exist in the [2DA file](2DA-File-Format)

**Solutions:**

- Verify column names match exactly (case-sensitive)
- Use AddColumn to add the column first if it doesn't exist
- Check the source [2DA file](2DA-File-Format) to see available columns

### ExclusiveColumn Behavior

**Problem:** Unexpected row modification instead of adding new row (or vice versa)

**Solutions:**

- Understand that `ExclusiveColumn` checks if a row with the same value exists
- If match found: existing row is modified
- If no match: new row is added
- Ensure the column specified in `ExclusiveColumn` is included in the cell modifications

**Example:**

```ini
; This will modify existing row if label="MY_APPEARANCE" exists
[add_row]
ExclusiveColumn=label
label=MY_APPEARANCE
name=StrRef100
```

### AddColumn Memory Storage Syntax

**Problem:** Incorrect syntax for storing values from new column

**Solutions:**

- Use `I#` format for row index: `2DAMEMORY#=I5` (stores value from row index 5 in the new column)
- Use `Llabel` format for row label: `2DAMEMORY#=L1` (stores value from row with label "1" in the new column)
- Memory is stored **after** the column is created and all insert values (`I#=` and `Llabel=`) are applied
- Cannot use other RowValue types (like `RowIndex`, `RowLabel`, `ColumnName`, etc.) directly in AddColumn memory storage - only `I#` and `Llabel` formats are supported
- The `I#` or `Llabel` syntax tells the patcher to retrieve the cell value from that specific row in the newly created column

**Example:**

```ini
[add_column]
ColumnLabel=NewColumn
DefaultValue=0
I5=Value
2DAMEMORY10=I5    ; Correct - stores value from row index 5
2DAMEMORY11=RowIndex  ; Wrong - RowIndex not supported in AddColumn memory storage
```

### Target type Confusion

**Problem:** Confusion between `RowLabel` and `LabelIndex`

**Solutions:**

- `RowLabel=value` --> Uses the row's label (first column value) to find the row
- `LabelIndex=value` --> Searches the "label" column for a matching value
- Use `RowLabel` when you know the row label value
- Use `LabelIndex` when you need to search within a column named "label"

### Empty string vs Missing values

**Problem:** Confusion about `****` vs omitted keys

**Solutions:**

- `****` explicitly sets a cell to an empty string
- Omitting a column [KEY](Container-Formats#key) leaves the cell unchanged (in ChangeRow/CopyRow) or empty (in AddRow)
- Use `****` when you want to explicitly clear a value

### Special Functions Not Working

**Problem:** `high()`, `RowIndex`, `RowLabel` not working as expected

**Solutions:**

- Special functions only work in ChangeRow, AddRow, and CopyRow cell values
- They do **not** work in AddColumn inserts or default values
- `high()` without column name uses the current column context
- Check syntax: `high()` not `high`, `RowIndex` not `Rowindex`

## Integration with Other Sections

### Using [StrRef](Audio-and-Localization-Formats#string-references-strref) Tokens from TLKList

Since `[2DAList]` runs after `[TLKList]`, you can use `StrRef#` tokens in your [2DA](2DA-File-Format) modifications:

```ini
[TLKList]
StrRef500=Custom Appearance Name

[2DAList]
Table0=appearance.2da

[appearance.2da]
AddRow0=new_appearance

[new_appearance]
RowLabel=100
label=CUSTOM_APPEARANCE
name=StrRef500
```

### Creating 2DAMEMORY Tokens for GFFList

Any `2DAMEMORY#` tokens you create in `[2DAList]` are available in `[GFFList]`:

```ini
[2DAList]
Table0=appearance.2da

[appearance.2da]
AddRow0=store_appearance_id

[store_appearance_id]
RowLabel=100
label=MY_APPEARANCE
2DAMEMORY10=RowIndex

[GFFList]
File0=item.uti

[item.uti]
ModelVariation=2DAMEMORY10  ; Use stored row index
```

### Using 2DAMEMORY Tokens in CompileList

In `[CompileList]`, you can use `2DAMEMORY#` tokens as preprocessor tokens in [NSS](NSS-File-Format) scripts:

```ini
[2DAList]
Table0=appearance.2da

[appearance.2da]
AddRow0=store_id

[store_id]
RowLabel=100
2DAMEMORY10=RowIndex

[CompileList]
File0=script.nss

[script.nss]
; In script.nss:
; ChangeObjectAppearance(OBJECT_SELF, #2DAMEMORY10#);
```

### Using 2DAMEMORY Tokens in HACKList

In `[HACKList]`, you can use `2DAMEMORY#` tokens for binary patch values:

```ini
[2DAList]
Table0=appearance.2da

[appearance.2da]
AddRow0=store_id

[store_id]
RowLabel=100
2DAMEMORY10=RowIndex

[HACKList]
File0=script.ncs

[script.ncs]
40=2DAMEMORY10  ; Modify offset 40 (hex 0x28) with stored value
```

### Using 2DAMEMORY Tokens in SSFList

In `[SSFList]`, you can use `2DAMEMORY#` tokens for sound stringref assignments:

```ini
[2DAList]
Table0=appearance.2da

[appearance.2da]
AddRow0=store_id

[store_id]
RowLabel=100
2DAMEMORY10=RowIndex

[SSFList]
File0=soundset.ssf

[soundset.ssf]
Battlecry 1=2DAMEMORY10  ; Use stored value as stringref
```

## Processing Order and Execution

### Modification Order Within a file

Modifications within a single [2DA file](2DA-File-Format) are processed in the order they appear in the file section:

```ini
[appearance.2da]
ChangeRow0=modify_first
ChangeRow1=modify_second
AddRow0=add_new
CopyRow0=copy_existing
AddColumn0=add_column
```

Processing order:

1. All `ChangeRow#` modifications (in order)
2. All `AddRow#` modifications (in order)
3. All `CopyRow#` modifications (in order)
4. All `AddColumn#` modifications (in order)

**Important:** Since AddColumn runs last, columns added by AddColumn cannot be used in earlier ChangeRow/AddRow/CopyRow modifications within the same file. However, tokens created in earlier modifications are available for AddColumn.

### Cross-file Token Availability

Tokens created in earlier files are available to later files:

```ini
[2DAList]
Table0=appearance.2da
Table1=classes.2da

[appearance.2da]
AddRow0=create_token
[create_token]
RowLabel=100
2DAMEMORY10=RowIndex

[classes.2da]
ChangeRow0=use_token
[use_token]
RowIndex=5
appearance=2DAMEMORY10  ; Token from previous file is available
```

## Advanced Patterns

### Pattern 1: Conditional Row Creation

Use `ExclusiveColumn` to prevent duplicate rows:

```ini
[add_appearance]
ExclusiveColumn=label
label=MY_APPEARANCE
name=StrRef100
```

This will modify existing row if `label=MY_APPEARANCE` exists, otherwise add a new row.

### Pattern 2: Storing Multiple values from One Row

```ini
[modify_appearance]
RowIndex=5
2DAMEMORY10=RowIndex
2DAMEMORY11=RowLabel
2DAMEMORY12=modeltype
2DAMEMORY13=name
```

Store multiple values for use in other sections.

### Pattern 3: Incremental Row Labels

Use `high()` to automatically assign the next available row label:

```ini
[add_appearance]
RowLabel=high()
label=NEW_APPEARANCE
```

### Pattern 4: Copy and Modify Pattern

Copy an existing row, modify some values, and store the new row index:

```ini
[copy_modify]
RowIndex=1
ExclusiveColumn=label
label=MODIFIED_COPY
modeltype=3
2DAMEMORY10=RowIndex
```

## Summary

The `[2DAList]` section provides powerful tools for modifying [2DA files](2DA-File-Format):

- **ChangeRow**: Modify existing rows by index, label, or label column
- **AddRow**: Add new rows with optional duplicate checking
- **CopyRow**: Copy existing rows with modifications
- **AddColumn**: Add new columns with default and custom values
- **Memory Tokens**: Store values for cross-file and cross-section use
- **Token Integration**: Use [StrRef](Audio-and-Localization-Formats#string-references-strref) tokens from TLKList and provide 2DAMEMORY tokens to other sections

[KEY](Container-Formats#key) points to remember:

1. Tokens are evaluated after cell modifications within the same section
2. Tokens persist across multiple files in the same `[2DAList]` section
3. `ExclusiveColumn` provides smart duplicate prevention
4. Special functions (`high()`, `RowIndex`, `RowLabel`) only work in ChangeRow/AddRow/CopyRow
5. AddColumn runs last within a file, so new columns can't be used in earlier modifications
6. All memory tokens are available to subsequent sections (GFFList, CompileList, HACKList, SSFList)

### See also

- [2DA-File-Format](2DA-File-Format) -- 2DA structure and columns
- [TSLPatcher TLKList Syntax](TSLPatcher-Data-Syntax#tlklist-syntax) -- Creating [StrRef](Audio-and-Localization-Formats#string-references-strref) tokens
- [TSLPatcher GFFList Syntax](TSLPatcher-GFF-Syntax#gfflist-syntax) -- Using 2DAMEMORY tokens in [GFF files](GFF-File-Format)
- [TSLPatcher HACKList Syntax](TSLPatcher-Install-and-Hack-Syntax#hacklist-syntax) -- Using tokens in binary patches
- [TSLPatcher SSFList Syntax](TSLPatcher-GFF-Syntax#ssflist-syntax) -- Using tokens in sound sets
- [Community sources and archives](Home#community-sources-and-archives) -- DeadlyStream, LucasForums for 2DA modding examples
- [TSLPatcher's Official Readme](TSLPatcher's-Official-Readme) -- CompileList and overview


---

<a id="tlklist-syntax"></a>

# TSLPatcher TLKList Syntax Documentation

This guide explains how to modify [TLK files](Audio-and-Localization-Formats#tlk) using TSLPatcher syntax. For the complete [TLK file](Audio-and-Localization-Formats#tlk) format specification, see [TLK File Format](Audio-and-Localization-Formats#tlk). For general TSLPatcher information, see [TSLPatcher's Official Readme](TSLPatcher's-Official-Readme). For HoloPatcher-specific information, see [HoloPatcher README for Mod Developers](HoloPatcher#mod-developers).

## Overview

The `[TLKList]` section in TSLPatcher's changes.ini file enables you to modify TLK ([Talk Table](Audio-and-Localization-Formats#tlk)) files used throughout KotOR. [TLK files](Audio-and-Localization-Formats#tlk) store all in-game text strings and their associated voiceover sound references. The most important [TLK file](Audio-and-Localization-Formats#tlk) is [`dialog.tlk`](Audio-and-Localization-Formats#tlk), which contains all dialog, item descriptions, conversations, and other text displayed in the game.

TSLPatcher was designed by Stoffe with an **append-only philosophy** for [TLK](Audio-and-Localization-Formats#tlk) modifications. This design maximizes mod compatibility by non-destructively adding new entries to the end of [`dialog.tlk`](Audio-and-Localization-Formats#tlk), allowing multiple mods to safely coexist without conflicts.

## Benefits of [TLK](Audio-and-Localization-Formats#tlk) Modification

TSLPatcher's [TLK](Audio-and-Localization-Formats#tlk) modification system provides several [KEY](Container-Formats#key) advantages:

- **Avoid distributing large files**: The [`dialog.tlk`](Audio-and-Localization-Formats#tlk) file is approximately 10 MB. Instead of distributing the entire modified file, TSLPatcher allows you to add only your new entries, significantly reducing mod file size.

- **Memory system integration**: TSLPatcher keeps StrRefs of newly added entries in memory, allowing you to insert those StrRefs as needed into:
  - [2DA](2DA-File-Format) tables
  - [GFF files](GFF-File-Format)
  For example, if you add the name of a new force power to [`dialog.tlk`](Audio-and-Localization-Formats#tlk), TSLPatcher can memorize the [StrRef](Audio-and-Localization-Formats#string-references-strref) the name string ended up as, and insert that value into the "name" column in `spells.2da`.

- **Cross-section token usage**: [StrRef](Audio-and-Localization-Formats#string-references-strref) tokens created in `[TLKList]` can be used throughout other sections:
  - In `[2DAList]` to assign stringrefs to [2DA](2DA-File-Format) cells
  - In `[GFFList]` to assign stringrefs to [GFF](GFF-File-Format) fields (including ExoLocString fields)
  - In `[CompileList]` scripts where `#StrRef#` tokens are replaced during compilation
  - In `[SSFList]` to assign stringrefs to soundset entries

## Glossary

- **TLK ([Talk Table](Audio-and-Localization-Formats#tlk))**: Binary file format storing text strings and voiceover references. The primary file is [`dialog.tlk`](Audio-and-Localization-Formats#tlk).

- **StringRef ([StrRef](Audio-and-Localization-Formats#string-references-strref))**: Short for "string Reference", this is a numeric identifier/index for an entry in a [TLK file](Audio-and-Localization-Formats#tlk). StringRefs start at 0 and increment sequentially. Example: StringRef 12345 refers to the 12346th entry in a [TLK file](Audio-and-Localization-Formats#tlk). The [StrRef](Audio-and-Localization-Formats#string-references-strref) is the identifier number that the game engine uses to retrieve text strings from [`dialog.tlk`](Audio-and-Localization-Formats#tlk).

- **[KEY](Container-Formats#key)**: The left side of the `=` symbol in an INI entry (e.g., `StrRef0`, `AppendFile0`)

- **value**: The right side of the `=` symbol in an INI entry. In `[TLKList]`, values specify the index into [TLK](Audio-and-Localization-Formats#tlk) source files to read from.

- **Token**: A placeholder like `StrRef0` or `StrRef1` that gets replaced with an actual StringRef during patching.

- **Append**: Non-destructive operation that adds new entries to the end of [`dialog.tlk`](Audio-and-Localization-Formats#tlk). This is TSLPatcher's primary and recommended method.

- **Replace**: Destructive operation that overwrites existing entries in [`dialog.tlk`](Audio-and-Localization-Formats#tlk). **Should ONLY be used for fixing grammar, spelling, or typographical errors in existing game content.** See [Replace Functionality Warning](#replace-functionality-warning) for details.

- **append.tlk**: Default source file containing new strings to append. Created using TalkEd.exe (see [Creating TLK Files](#creating-tlk-files)). Located in `tslpatchdata` folder.

- **appendf.tlk**: Feminine/non-English localized version of `append.tlk`. Used exclusively for KotOR1 Polish localization. Must have exactly the same number of entries as `append.tlk`. See [Localized Versions](#localized-versions) for details.

- **dialog.tlk**: The game's main [TLK file](Audio-and-Localization-Formats#tlk) containing all in-game text (typically ~10 MB). Modified files are written to the game's root directory (not override folder). TSLPatcher allows you to add new entries without distributing the entire large file.

## Table of Contents

- [Glossary](#glossary)
- [Benefits of TLK Modification](#benefits-of-tlk-modification)
- [Replace Functionality Warning](#replace-functionality-warning)
- [Creating TLK Files](#creating-tlk-files)
- [Basic Structure](#basic-structure)
- [Configuration Keys](#configuration-keys)
- [Entry Syntax](#entry-syntax)
  - [How Token Creation Works](#how-token-creation-works)
  - [StrRef Entries](#strref-entries)
  - [AppendFile Syntax](#appendfile-syntax)
- [Localized Versions](#localized-versions)
- [Memory System](#memory-system)
- [Processing Order](#processing-order)
- [File Structure](#basic-structure)
- [Complete Examples](#complete-examples)
- [Common Use Cases](#common-use-cases)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)
- [Reference](#reference)

## Replace Functionality Warning

⚠️ **CRITICAL: Replace functionality should ONLY be used for fixing grammar, spelling, or typographical errors in existing game content.**

TSLPatcher was designed by Stoffe to be **append-only** for [TLK](Audio-and-Localization-Formats#tlk) modifications. The original TSLPatcher exclusively appended new entries to the end of [`dialog.tlk`](Audio-and-Localization-Formats#tlk) and never replaced existing entries. This design was intentional to maximize mod compatibility:

### Why Replace Should Be Avoided for New Content

- **Breaks mod compatibility**: If two mods replace the same stringref, they conflict irreconcilably
- **Destroys vanilla content**: Replaces original game text permanently, making it impossible to restore
- **Prevents mod stacking**: Can't safely use multiple mods that replace different entries simultaneously
- **Defeats TSLPatcher's design**: The tool was specifically designed for non-destructive appending to avoid conflicts

### Why Append Works Better

- **Non-destructive**: Appending preserves all existing game text, preventing conflicts between mods
- **Dynamic indexing**: Uses tokens (`[StrRef](Audio-and-Localization-Formats#string-references-strref)#`) to handle variable stringref assignments without hard-coding indices
- **Mod stacking**: Multiple mods can safely add entries without interfering with each other
- **Compatibility**: Avoids the need to distribute full [`dialog.tlk`](Audio-and-Localization-Formats#tlk) files (10+ MB), reducing mod size

### Acceptable Uses of Replace

- ✅ Fixing typos in base game text (e.g., "teh" --> "the")
- ✅ Correcting grammar mistakes in vanilla content
- ✅ Fixing broken or corrupted entries
- ✅ Community patch projects (like K1CP) that systematically fix errors

### When NOT to Use Replace

- ❌ Adding new content (use AppendFile or [StrRef](Audio-and-Localization-Formats#string-references-strref) syntax instead)
- ❌ Modifying existing text for flavor/preference
- ❌ Any scenario where append would work

**For all new content, always use the append-based syntaxes described in [Entry Syntax](#entry-syntax).**

## Creating [TLK](Audio-and-Localization-Formats#tlk) files

To use custom [dialog.tlk](Audio-and-Localization-Formats#tlk) entries in your mod, you must create source [TLK files](Audio-and-Localization-Formats#tlk) containing your new strings:

### Using TalkEd.exe

1. **Create a new [TLK file](Audio-and-Localization-Formats#tlk)**: Use TalkEd.exe (a [TLK](Audio-and-Localization-Formats#tlk) editor tool) to create a new [TLK file](Audio-and-Localization-Formats#tlk)
2. **Add your entries**: Add all your new text strings and voiceover sound references to this file
3. **Save as append.tlk**: Name the file exactly `append.tlk` (case-sensitive)
4. **Place in tslpatchdata**: Save `append.tlk` in the `tslpatchdata` folder

### Localized Versions (KotOR1 Polish only)

If you are using a non-English version of KotOR1 that has a `dialogf.tlk` file (Polish localization), you must also:

1. **Create appendf.tlk**: Create a new file with the feminine form of your strings
2. **Name it appendf.tlk**: Must be named exactly `appendf.tlk` (case-sensitive)
3. **Match entry count**: **`appendf.tlk` must have exactly the same number of entries as `append.tlk`**
4. **Matching indices**: Each index in `appendf.tlk` should correspond to the same index in `append.tlk`
5. **Handle missing forms**: If a string has no specific feminine form, put the same text in both files

**Important**: The entry count must match exactly. If `append.tlk` has 100 entries, `appendf.tlk` must also have exactly 100 entries, even if some are identical between the two files.

### Using ChangeEdit (Optional)

The ChangeEdit application provides a user-friendly [GUI](GFF-File-Format#gui-graphical-user-interface) interface for configuring [TLK](Audio-and-Localization-Formats#tlk) entries without manually editing the INI file:

1. **Open append.tlk**: In ChangeEdit, navigate to the "[TLK](Audio-and-Localization-Formats#tlk) Entries" section in the tree view
2. **Load file**: Press the "Open append.tlk file..." button on top of the right list
3. **View entries**: This lists all your custom text entries in the list to the right
4. **Select entries**: Select an entry you wish TSLPatcher to add to [`dialog.tlk`](Audio-and-Localization-Formats#tlk)
5. **Add to list**: Press the left arrow icon (←) to add the entry to the list on the left
6. **Token creation**: Take note of the value in the left column, which should look like `StrRef0` for the first entry, with an incrementing number (`StrRef1`, `StrRef2`, etc.) for each subsequent entry
7. **Use tokens**: This token (e.g., `StrRef0`) is what you'll use in other sections to assign the resulting [StrRef](Audio-and-Localization-Formats#string-references-strref) value:
   - [2DA](2DA-File-Format) cells (`[2DAList]`)
   - [GFF](GFF-File-Format) fields (`[GFFList]`)

**Manual Editing**: While ChangeEdit provides a [GUI](GFF-File-Format#gui-graphical-user-interface) interface, you can also edit the `changes.ini` file directly with any text editor (Notepad, VS Code, etc.). The INI format is plain text and human-readable.

**Important**: When using ChangeEdit, always verify the generated INI entries match your expectations, especially for token names and entry indices.

## Basic structure

```ini
[TLKList]
!DefaultDestination=.
!DefaultSourceFolder=.
!SourceFile=append.tlk
!SourceFileF=appendf.tlk

; Append new entries
StrRef0=0
StrRef1=1

; Append from custom file (Useful if you have a LOT of TLK entries and want to organize within multiple [TLK files](Audio-and-Localization-Formats#tlk))
AppendFile0=custom_entries.tlk

[custom_entries.tlk]
0=10
1=11
```

**[KEY](Container-Formats#key) Points:**

- All examples use **append** operations - the recommended approach
- values specify which [StrRef](Audio-and-Localization-Formats#string-references-strref) indices to read from source files

## Configuration Keys

### `!DefaultDestination`

- **type**: String (path)
- **Default**: `.` (kotor game installation path root)
- **Description**: Default destination folder for [TLK files](Audio-and-Localization-Formats#tlk) when not overridden
- **Example**: `!DefaultDestination=override`

### `!DefaultSourceFolder`

- **type**: String (path)
- **Default**: `.` (tslpatchdata folder)
- **Description**: Default folder to search for [TLK](Audio-and-Localization-Formats#tlk) source files (e.g., `append.tlk`). This is a relative path from `mod_path`, which is typically the `tslpatchdata` folder (the parent directory of the `changes.ini` file). The default value `.` refers to the `tslpatchdata` folder itself.
- **Path Resolution**: files are resolved as `mod_path / !DefaultSourceFolder / filename`. When `mod_path = "C:/Mod/tslpatchdata"`:
  - `!DefaultSourceFolder=.` resolves to e.g. `"C:/Mod/tslpatchdata"`
  - `!DefaultSourceFolder=tlk_files` resolves to e.g. `"C:/Mod/tslpatchdata/tlk_files"`
- **Example**: `!DefaultSourceFolder=.` (default, refers to tslpatchdata folder)

### `!SourceFile`

- **type**: String (filename)
- **Default**: `append.tlk`
- **Description**: Name of the [TLK file](Audio-and-Localization-Formats#tlk) to use when appending entries via [StrRef](Audio-and-Localization-Formats#string-references-strref) syntax
- **Example**: `!SourceFile=my_strings.tlk`

### `!SourceFileF`

- **type**: String (filename)
- **Default**: `appendf.tlk`
- **Description**: Name of the [TLK file](Audio-and-Localization-Formats#tlk) to use for feminine/non-English localized versions (exclusively KotOR1 Polish)
- **Version Added**: 1.2.8b6
- **Note**: Must have exactly the same number of entries as `!SourceFile`. Each index in `appendf.tlk` maps directly to the same index in `append.tlk`. If a string has no specific feminine form, put the same text in both files.
- **Example**: `!SourceFileF=my_strings_f.tlk`

### Unsupported Keys

The following keys are **NOT** supported in `[TLKList]`:

- `!ReplaceFile` - Not applicable to [TLK files](Audio-and-Localization-Formats#tlk)
- `!OverrideType` - Not applicable to [TLK files](Audio-and-Localization-Formats#tlk)

## Entry Syntax

The `[TLKList]` section supports two primary entry syntax patterns, both using **append** operations:

1. **[StrRef](Audio-and-Localization-Formats#string-references-strref) Entries** - Append from the default source file (`append.tlk`)
2. **AppendFile Syntax** - Append from custom [TLK files](Audio-and-Localization-Formats#tlk) with flexible mappings

### How Token Creation Works

**Important**: Tokens are created from the **value** (the number on the right side of `=`). For `StrRef<number>=<number>` entries, the number in the [KEY](Container-Formats#key) and value must match, and this matching number determines the token name.

- `StrRef0=0` creates token `StrRef0` (reads index 0 from `append.tlk`)
- `StrRef5=5` creates token `StrRef5` (reads index 5 from `append.tlk`)
- For AppendFile subsections, `10=10` creates token `StrRef10` (reads index 10 from the source [TLK](Audio-and-Localization-Formats#tlk))

The token name `[StrRef](Audio-and-Localization-Formats#string-references-strref)<number>` is created from the matching number, and this token stores the new stringref that gets appended to [`dialog.tlk`](Audio-and-Localization-Formats#tlk) for use in other sections.

### [StrRef](Audio-and-Localization-Formats#string-references-strref) Entries

**Purpose**: Append new entries to [`dialog.tlk`](Audio-and-Localization-Formats#tlk) from the default source file (`append.tlk`)

**Syntax**:

```ini
StrRef<number>=<number>
```

**Parameters**:

- `<number>` - The index into `append.tlk` (or `!SourceFile`) to read from. This number must match in both the [KEY](Container-Formats#key) and value.

**Behavior**:

- Appends a new entry to the end of [`dialog.tlk`](Audio-and-Localization-Formats#tlk) (non-destructive)
- Reads text and sound from `append.tlk` at the specified index
- The new entry receives the next available stringref automatically
- Creates token `StrRef<number>` from the matching number (see [How Token Creation Works](#how-token-creation-works))
- Stores that new stringref in memory for use in other sections via the token

**Examples**:

```ini
[TLKList]
StrRef0=0  ; Reads index 0 from append.tlk, creates token StrRef0
StrRef1=1  ; Reads index 1 from append.tlk, creates token StrRef1
StrRef2=2  ; Reads index 2 from append.tlk, creates token StrRef2
```

### AppendFile Syntax

**Purpose**: Add entries from a custom [TLK file](Audio-and-Localization-Formats#tlk) using index mappings

**Syntax**:

```ini
AppendFile<anything>=<tlk_filename>
```

**Parameters**:

- `<tlk_filename>` - Name of a [TLK file](Audio-and-Localization-Formats#tlk) in the source folder OR name of a subsection in the INI

**Behavior**:

- Creates a **new section** `[<tlk_filename>]` if the file doesn't exist in source
- Maps entries from the source [TLK](Audio-and-Localization-Formats#tlk) to [`dialog.tlk`](Audio-and-Localization-Formats#tlk) using the subsection mappings
- All entries are **added** (not replaced) to [`dialog.tlk`](Audio-and-Localization-Formats#tlk)
- For AppendFile, entries are appended and tokens are created from the mapping values

**Subsection Syntax**:

```ini
[<tlk_filename>]
<token_identifier>=<source_index>
StrRef<token_identifier>=StrRef<source_index>  ; Alternative explicit syntax
```

**Subsection Parameters**:

- `<source_index>` - The index into the source [TLK file](Audio-and-Localization-Formats#tlk) to read from. Token `StrRef{source_index}` is created from this value. The number in the [KEY](Container-Formats#key) should match the number in the value for clarity.

**Examples**:

```ini
[TLKList]
AppendFile0=planets.tlk  ; Creates subsection [planets.tlk] for mappings

[planets.tlk]
10=10  ; Reads index 10, creates token StrRef10
11=11  ; Reads index 11, creates token StrRef11
12=12  ; Reads index 12, creates token StrRef12 (alternative: StrRef12=StrRef12)
```

**Important Notes**:

- The `<anything>` in `AppendFile<anything>` is arbitrary and ignored
- The subsection `[planets.tlk]` can define mappings using numeric indices or `[StrRef](Audio-and-Localization-Formats#string-references-strref)` syntax

## Localized Versions

### KotOR1 Polish Localization

KotOR1 Polish edition uses both [`dialog.tlk`](Audio-and-Localization-Formats#tlk) and `dialogf.tlk` files. If your mod supports this localization:

1. **Create both files**: Create `append.tlk` (masculine/standard) and `appendf.tlk` (feminine/localized)
2. **Match entry counts**: Both files must have exactly the same number of entries
3. **Map indices**: Entry at index 0 in `append.tlk` corresponds to index 0 in `appendf.tlk`
4. **Handle duplicates**: If a string doesn't have a feminine form, use the same text in both files

### Configuration

```ini
[TLKList]
!SourceFile=append.tlk
!SourceFileF=appendf.tlk
StrRef0=0
StrRef1=1
```

When TSLPatcher processes entries, it automatically uses `appendf.tlk` when the target game has `dialogf.tlk` present.

### Non-English Localization Notes

- **KotOR2**: Does not use `dialogf.tlk` - only [`dialog.tlk`](Audio-and-Localization-Formats#tlk) is used
- **Other Languages**: Currently only KotOR1 Polish uses the dual-[TLK](Audio-and-Localization-Formats#tlk) system
- **Entry Matching**: The strict requirement for matching entry counts ensures proper localization mapping

## Memory System

When [TLK](Audio-and-Localization-Formats#tlk) entries are **added** via append operations, TSLPatcher stores them in memory for use in other patch sections.

### Memory Storage

```python
# After append operation (StrRef or AppendFile)
memory.memory_str[token_identifier] = new_stringref
```

**Behavior**:

- For **append** operations: Stores the new stringref that was added, mapped to the token identifier (see [How Token Creation Works](#how-token-creation-works))
- For **replace** operations: Memory is not typically stored (no need since stringref is static)

### Token Creation from values

Tokens are created from the matching number in both the [KEY](Container-Formats#key) and value. See [How Token Creation Works](#how-token-creation-works) for details. After processing, tokens are available for use in other sections like `[2DAList]`, `[GFFList]`, and `[CompileList]`.

### Using [TLK](Audio-and-Localization-Formats#tlk) Memory in Other Sections

**In [2DA files](2DA-File-Format)**:

```ini
[TLKList]
StrRef0=0  ; Creates token StrRef0

[2DAList]
Table0=spells.2da

[spells.2da]
AddRow0=new_spell
2DAMEMORY0=StrRef0  ; Store stringref in 2DA memory for cross-file use

[new_spell]
name=StrRef0  ; Token gets replaced with actual stringref
```

**In [GFF files](GFF-File-Format)**:

```ini
[TLKList]
StrRef0=0  ; Creates token StrRef0

[GFFList]
File0=item.uti

[item.uti]
LocalizedName=StrRef0  ; Token gets replaced with actual stringref
```

**In [NSS](NSS-File-Format) Scripts (CompileList)**:

```c
// Script compilation will replace #StrRef# tokens
void main() {
    // #StrRef0# token gets replaced with actual stringref during compilation
    SendMessageToPC(GetFirstPC(), #StrRef0#);
}
```

## Processing Order

### TSLPatcher Execution Order

In **TSLPatcher v1.2.8 and later**, the TLKList section is processed **first** in the patching pipeline (before InstallList):

```text
TSLPatcher Execution Order (v1.2.8+):
1. [TLKList]         - Add TLK entries (append operations)
2. [InstallList]     - Copy files to installation
3. [2DAList]         - Add/Modify 2DA entries
4. [GFFList]         - Add/Modify GFF entries
5. [CompileList]     - Compile NSS scripts (replaces #StrRef# tokens)
6. [SSFList]         - Modify soundset files
```

**Note**: In TSLPatcher v1.2.8b0 (2006-08-06), the processing order was changed so that [TLK](Audio-and-Localization-Formats#tlk) Appending happens before Install List. According to the official change log, this allows [MOD](Container-Formats#erf), [ERF](Container-Formats#erf), or [RIM](Container-Formats#rim) files to be placed in their proper locations before later sections run, so modified files can be saved into those container files. Those later sections include:

- [GFF](GFF-File-Format) patching
- Script compilation

**Older TSLPatcher versions** (before 1.2.8) processed InstallList before TLKList.

### HoloPatcher Execution Order

**HoloPatcher** (a modern Python drop-in replacement for TSLPatcher) uses a **different execution order**:

```text
HoloPatcher Execution Order:
1. [InstallList]     - Copy files to installation
2. [TLKList]         - Add TLK entries (append operations) ← HERE
3. [2DAList]         - Add/Modify 2DA entries
4. [GFFList]         - Add/Modify GFF entries
5. [CompileList]     - Compile NSS scripts (replaces #StrRef# tokens)
6. [HACKList]        - Patch [NCS files](NCS-File-Format)
7. [SSFList]         - Modify soundset files
```

**Important Compatibility Note**: This is a **backwards-compatible discrepancy** between TSLPatcher and HoloPatcher. HoloPatcher processes InstallList before TLKList to allow users to install a base [`dialog.tlk`](Audio-and-Localization-Formats#tlk) file (or other files) via InstallList, which can then be modified by [TLK](Audio-and-Localization-Formats#tlk) appending operations. This order provides greater flexibility for mod workflows.

### Analysis: Order Comparison

**TSLPatcher's reasoning** (TLKList --> InstallList):

- Allows [MOD](Container-Formats#erf), [ERF](Container-Formats#erf), and [RIM](Container-Formats#rim) files to be placed before sections that save into them ([GFF](GFF-File-Format) and Compile)

**HoloPatcher's reasoning** (InstallList --> TLKList):

- ✅ **More flexible**: Users can install a custom base [`dialog.tlk`](Audio-and-Localization-Formats#tlk) file via InstallList, then [TLK](Audio-and-Localization-Formats#tlk) appending modifies it
- ✅ **Better for testing**: Allows installing known-good [TLK files](Audio-and-Localization-Formats#tlk) before appending new entries
- ✅ **Preserves dependencies**: [TLK](Audio-and-Localization-Formats#tlk) entries are still processed before sections that reference them:
  - [2DA](2DA-File-Format)
  - [GFF](GFF-File-Format)
  - Compile
  - [SSF](Audio-and-Localization-Formats#ssf)
- ✅ **More intuitive**: file installation happens first, then modifications are applied

**Critical Timing** (applies to both TSLPatcher and HoloPatcher):

- [TLK](Audio-and-Localization-Formats#tlk) entries are added to the destination target [`dialog.tlk`](Audio-and-Localization-Formats#tlk) **before** these modifications run:

  - [2DA](2DA-File-Format)
  - [GFF](GFF-File-Format)
- This ensures stringrefs/[TLK](Audio-and-Localization-Formats#tlk) entries are available when referenced by other sections
- Script compilation happens **after** [TLK](Audio-and-Localization-Formats#tlk) processing, so `#[StrRef](Audio-and-Localization-Formats#string-references-strref)#` tokens can be resolved
- Tokens are substituted after [TLK](Audio-and-Localization-Formats#tlk) entries have been appended in:

  - [2DA](2DA-File-Format)
  - [GFF](GFF-File-Format)
  - Script files

## file structure

### [TLK](Audio-and-Localization-Formats#tlk) file format

A [TLK file](Audio-and-Localization-Formats#tlk) is a binary format containing:

- **header**: file type (`TLK`), version (`V3.0`), language ID, string count, entries offset
- **Entry headers**: flags, sound ResRef (16 bytes), volume/pitch variance (unused), text offset, text length, sound length (unused)
- **Text data**: Actual string content stored at the specified offsets

**[TLK](Audio-and-Localization-Formats#tlk) Entry structure**:

```python
class TLKEntry:
    text: str              # The display text (UTF-8 or cp1252 encoding)
    voiceover: ResRef      # Sound file ResRef (max 16 characters)
    sound_length: float    # Unused by KotOR (present in format but ignored)
```

**string Length Limitations**:

- **TSLPatcher v1.2.8b6 and later**: Can handle [TLK](Audio-and-Localization-Formats#tlk) entries with strings of **any size** (no practical limit)
- **Earlier versions**: Had a bug that prevented proper handling of strings longer than 4096 characters
- If you encounter issues with long strings, ensure you're using TSLPatcher v1.2.8b6 or later. HoloPatcher does **NOT** have this bug.

### KotOR [TLK](Audio-and-Localization-Formats#tlk) files

**Standard files**:

- [`dialog.tlk`](Audio-and-Localization-Formats#tlk) - Main English dialog (always present in game directory)

**Localized Versions** (exclusively KotOR1 Polish):

- `dialogf.tlk` - Feminine/non-English localized version
- Must match the number of entries in [`dialog.tlk`](Audio-and-Localization-Formats#tlk) exactly

**Entry indices**:

- StringRefs start at 0 and increment sequentially
- Valid entries: 0 to (total_entries - 1)
- Reference entries as integers throughout the game and mod files

## Complete Examples

### Example 1: Simple Append with [StrRef](Audio-and-Localization-Formats#string-references-strref)

Add new string entries from `append.tlk` to [`dialog.tlk`](Audio-and-Localization-Formats#tlk):

```ini
[TLKList]
StrRef0=0
StrRef1=1
StrRef2=2
```

**files**: `tslpatchdata/append.tlk` contains entries 0, 1, 2 with your custom text

**Result**: Each entry from `append.tlk` is appended to [`dialog.tlk`](Audio-and-Localization-Formats#tlk) and assigned the next available stringref (e.g., 123456, 123457, 123458). These new stringrefs are stored in memory as tokens `StrRef0`, `StrRef1`, `StrRef2` for use in other sections.

### Example 2: Append with Custom file

Add entries from a custom [TLK file](Audio-and-Localization-Formats#tlk) using index mappings:

```ini
[TLKList]
AppendFile0=planets.tlk

[planets.tlk]
0=10   ; Reads index 10, creates token StrRef10
1=11   ; Reads index 11, creates token StrRef11
2=12   ; Reads index 12, creates token StrRef12
```

**files**: `tslpatchdata/planets.tlk` contains entries at indices 10, 11, 12, etc.

**Result**: Each entry from `planets.tlk` is appended to [`dialog.tlk`](Audio-and-Localization-Formats#tlk) and tokens `StrRef10`, `StrRef11`, `StrRef12` are created (from the values, not the keys).

### Example 3: Combined Append Operations

Use multiple append methods together:

```ini
[TLKList]
!SourceFile=append.tlk
StrRef0=0
StrRef1=1
AppendFile0=items.tlk

[items.tlk]
0=100   ; Creates token StrRef100
1=101   ; Creates token StrRef101
```

**files**: `tslpatchdata/append.tlk` (entries 0, 1), `tslpatchdata/items.tlk` (entries 100, 101)

**Processing Order**: Entries are processed sequentially, creating tokens `StrRef0`, `StrRef1`, `StrRef100`, `StrRef101`.

### Example 4: Localized Version (Polish KotOR1)

Support for feminine/localized versions:

```ini
[TLKList]
!SourceFile=append.tlk
!SourceFileF=appendf.tlk
StrRef0=0
StrRef1=1
StrRef2=2
```

**files**:

- `append.tlk` (masculine/English) - Contains 3 entries (indices 0, 1, 2)
- `appendf.tlk` (feminine/Polish) - Must have exactly 3 entries (indices 0, 1, 2)

**Requirements**:

- Both files must have **exactly the same number of entries**
- Entry at index 0 in `append.tlk` maps to index 0 in `appendf.tlk`
- If a string has no feminine form, use the same text in both files
- TSLPatcher automatically uses `appendf.tlk` when the target game has `dialogf.tlk` present

## Common Use Cases

### Adding New Dialog for NPCs

**Scenario**: Add custom lines for a new NPC

**Solution**:

```ini
[TLKList]
StrRef0=0  ; Greeting line
StrRef1=1  ; Quest offer
StrRef2=2  ; Refusal response

[GFFList]
File0=my_npc.dlg

[my_npc.dlg]
; Reference tokens StrRef0, StrRef1, StrRef2 in dialog entries
```

### Adding Item Descriptions

**Scenario**: Add descriptions for new items

**Solution**:

```ini
[TLKList]
AppendFile0=items.tlk

[items.tlk]
0=10  ; Item name --> token StrRef10
1=11  ; Item description --> token StrRef11
2=12  ; Another item name --> token StrRef12
3=13  ; Another item description --> token StrRef13

[GFFList]
File0=new_item.uti

[new_item.uti]
LocalizedName=StrRef10
DescIdentified=StrRef11
```

### Translating Mod Content

**Scenario**: Create English and non-English versions

**Solution**:

```ini
[TLKList]
!SourceFile=append_en.tlk
!SourceFileF=append_de.tlk
StrRef0=0
StrRef1=1
StrRef2=2
```

**files**: Both `append_en.tlk` (English) and `append_de.tlk` (German) must match entry count exactly. TSLPatcher uses the appropriate file based on game localization.

## Troubleshooting

### Error: "Invalid syntax found in [TLKList]"

**Cause**: Unrecognized [KEY](Container-Formats#key) format

**Solutions**:

- Check for typos in [KEY](Container-Formats#key) names
- Ensure you're using one of the supported syntaxes: `[StrRef](Audio-and-Localization-Formats#string-references-strref)<key>=<value>` or `AppendFile<key>=<value>`
- Verify the [KEY](Container-Formats#key) matches the expected pattern

**Correct Syntaxes**:

```ini
; StrRef syntax: Key can be anything, value must be numeric
StrRef0=0
StrRef1=1

; AppendFile syntax: Key starts with "AppendFile", value is filename
AppendFile0=file.tlk
AppendFile1=another.tlk
```

### Error: "Could not parse '[KEY](Container-Formats#key)=value' in [TLKList]"

**Cause**: Invalid numeric values or malformed entries

**Solutions**:

- Ensure values are valid integers for [StrRef](Audio-and-Localization-Formats#string-references-strref) mappings and for AppendFile mappings
- Check that numeric keys can be parsed as integers if using numeric format
- Verify no extra spaces or invalid characters

**Correct**:

```ini
StrRef0=0
StrRef123=123
```

**Incorrect**:

```ini
StrRef0=abc  ; Value must be numeric
StrRef=0  ; Missing numeric part in key
```

### Error: "Section [filename] not found"

**Cause**: Referenced [TLK file](Audio-and-Localization-Formats#tlk) or subsection doesn't exist

**Solutions**:

- Create the subsection in the INI if using internal mappings:

  ```ini
  AppendFile0=myfile.tlk
  [myfile.tlk]  ; Must create this subsection
  0=1
  ```

- Or ensure the file exists in the source folder if using external [TLK files](Audio-and-Localization-Formats#tlk)
- Check `!DefaultSourceFolder` path is correct

### Error: "Cannot replace nonexistent stringref in [dialog.tlk](Audio-and-Localization-Formats#tlk)"

**Cause**: Trying to replace an entry that doesn't exist (if using replace functionality)

**Solutions**:

- For new content, use append syntax (`[StrRef](Audio-and-Localization-Formats#string-references-strref)` or `AppendFile`) instead of replace
- Verify the stringref number is correct if you must use replace for error fixing
- Remember: **Always use append for new content** - see [Replace Functionality Warning](#replace-functionality-warning)

**Adding New** (use this):

```ini
StrRef0=0  ; Appends new entry, creates token StrRef0
```

### Issue: Entries Not Appearing

**Cause**: Multiple possible issues

**Solutions**:

- Check file paths: `!DefaultSourceFolder` and file locations
- Verify [TLK file](Audio-and-Localization-Formats#tlk) format: must be valid binary [TLK](Audio-and-Localization-Formats#tlk)
- Check file encoding: should be UTF-8 or cp1252
- Ensure the file is in the tslpatchdata folder (or specified source folder)
- Review the log for processing errors
- Verify keys and values are correctly formatted

### Issue: Wrong Token Created

**Cause**: Confusion about token creation from keys vs values

**Solutions**:

- See [How Token Creation Works](#how-token-creation-works) - tokens are created from the **value** (matching number)
- `StrRef0=0` creates token `StrRef0`
- `StrRef5=5` creates token `StrRef5`

### Issue: Memory Tokens Not Working

**Cause**: Token not created or not accessible in other sections

**Solutions**:

- Verify the stringref was actually added (check logs)
- Ensure you're using the correct token name (created from matching number)
- Check memory is being used in the correct execution order
- Tokens are only created for **append** operations, not replace operations

**Example**:

```ini
[TLKList]
StrRef0=0  ; Creates token StrRef0

[2DAList]
Table0=spells.2da

[spells.2da]
name=StrRef0  ; Use the token
```

### Issue: files with Many Entries

**Best Practice**: Use AppendFile with subsections for clarity and organization

**Good** (Organized by content type):

```ini
[TLKList]
AppendFile0=items.tlk
AppendFile1=npcs.tlk

[items.tlk]
0=100   ; Token: StrRef100 - Item name
1=101   ; Token: StrRef101 - Item description
; ... many more entries

[npcs.tlk]
0=200   ; Token: StrRef200 - NPC greeting
1=201   ; Token: StrRef201 - NPC dialogue
; ... many more entries
```

**Less Ideal** (but still works for small mods):

```ini
[TLKList]
StrRef0=0
StrRef1=1
StrRef2=2
; ... 200 more lines becomes hard to manage
```

### Issue: Write-Protected [dialog.tlk](Audio-and-Localization-Formats#tlk)

**Cause**: Some systems have [`dialog.tlk`](Audio-and-Localization-Formats#tlk) set to read-only or write-protected

**Solutions**:

- Check file permissions on [`dialog.tlk`](Audio-and-Localization-Formats#tlk) in the game directory
- Run TSLPatcher with administrator privileges if needed
- Ensure the game is not running when installing mods
- Check if antivirus software is blocking file modification

**Note**: TSLPatcher v1.2.8b8 fixed a bug where installation would stop when [`dialog.tlk`](Audio-and-Localization-Formats#tlk) was write-protected. If using an older version, ensure the file is writable.

## Best Practices

### 1. Organization

- Group related entries in separate [TLK files](Audio-and-Localization-Formats#tlk)
- Use descriptive file names: `npcs.tlk`, `items.tlk`, `planets.tlk`
- Keep the main INI clean with AppendFile/[StrRef](Audio-and-Localization-Formats#string-references-strref) references
- Document which tokens correspond to which content

### 2. Token Management

- See [How Token Creation Works](#how-token-creation-works) for token creation details
- Use consistent numbering to create predictable token names
- Document token usage in comments when helpful:

  ```ini
  StrRef0=0  ; NPC greeting
  ```

### 3. Compatibility

- **Always use append for new content** - this is TSLPatcher's design
- Never use replace functionality except for fixing existing errors (see [Replace Functionality Warning](#replace-functionality-warning))
- Document which stringrefs are custom vs modified
- Use descriptive token names by choosing appropriate numbers

### 4. Testing

- Verify all [TLK files](Audio-and-Localization-Formats#tlk) are valid before packaging
- Check stringref assignments in logs
- Test with multiple mods installed to check compatibility
- Use `KotorDiff` to compare before/after [`dialog.tlk`](Audio-and-Localization-Formats#tlk)
- Verify tokens are correctly created and accessible

### 5. file Management

- **Create with TalkEd.exe**: Use TalkEd.exe to create and edit your source [TLK](Audio-and-Localization-Formats#tlk) files (see [Creating TLK Files](#creating-tlk-files))
- **Keep source [TLK files](Audio-and-Localization-Formats#tlk) readable**: Use JSON export for debugging if your [TLK](Audio-and-Localization-Formats#tlk) editor supports it
- **Maintain consistent naming**: Always use `append.tlk` and `appendf.tlk` (or set `!SourceFile`/`!SourceFileF` if using custom names)
- **Version control**: Keep [TLK files](Audio-and-Localization-Formats#tlk) separately from other mod files for easier management
- **Match entry counts**: If using localized versions, ensure `append.tlk` and `appendf.tlk` have **exactly the same number of entries**
- **file size considerations**: The [`dialog.tlk`](Audio-and-Localization-Formats#tlk) file is ~10 MB, but you only need to distribute small `append.tlk` files with your mod

### 6. Localization

- **KotOR1 Polish only**: The dual-[TLK](Audio-and-Localization-Formats#tlk) system ([`dialog.tlk`](Audio-and-Localization-Formats#tlk) + `dialogf.tlk`) is exclusively for KotOR1 Polish localization
- **Maintain parallel files**: If supporting Polish, maintain both `append.tlk` and `appendf.tlk`
- **Exact entry matching**: Entry counts must match exactly between `append.tlk` and `appendf.tlk`
- **Map indices**: Each index must correspond between the two files (index 0 --> index 0, index 1 --> index 1, etc.)
- **Handle duplicates**: If a string has no feminine form, use the same text in both files
- **Use configuration keys**: Set `!SourceFileF` to specify the feminine version filename
- **Documentation**: Document language support in your mod's README
- **KotOR2/TSL**: Does not use `dialogf.tlk` - only create `append.tlk` for KotOR2 mods

### 7. Key/value Clarity

- Keys appear on the left side of `=`, values on the right
- For `[StrRef](Audio-and-Localization-Formats#string-references-strref)<number>=<number>`, numbers must match for proper token creation
- Use consistent numbering for readability

## Reference

### Supported Entry Patterns

| Pattern | Syntax | Purpose | Replacement |
|---------|--------|---------|-------------|
| [StrRef](Audio-and-Localization-Formats#string-references-strref) | `[StrRef](Audio-and-Localization-Formats#string-references-strref)<number>=<number>` | Append from default file | No |
| AppendFile | `AppendFile<anything>=<filename>` | Append from custom file | No |

### Memory System Reference

```python
# After StrRef append
# StrRef0=0 --> Creates token StrRef0
# Memory: memory.memory_str[0] = new_stringref (from dialog.tlk append)

# After AppendFile append
# Subsection: 10=10 --> Creates token StrRef10
# Memory: memory.memory_str[10] = new_stringref (from dialog.tlk append)
```

**[KEY](Container-Formats#key) Points**:

- See [How Token Creation Works](#how-token-creation-works) for token lifecycle
- See [Memory System](#memory-system) for StrRef retention
- Tokens are available for use in these sections:
  - `[2DAList]`
  - `[GFFList]`
  - `[CompileList]`

### Processing Flow

1. Parse [TLKList] section
2. Load source [TLK files](Audio-and-Localization-Formats#tlk) from `!SourceFile`/`!SourceFileF` e.g. `!SourceFile=append.tlk`
3. For each [StrRef](Audio-and-Localization-Formats#string-references-strref) entry:
   - Parse: *[KEY](Container-Formats#key)* (ignored), *value* (source index)
   - Load entry from source file at *value* index
   - Append to dialog.tlk (gets new stringref)
   - Create token [StrRef](Audio-and-Localization-Formats#string-references-strref){value} from *value* to store the new stringref
4. For each AppendFile entry:
   - Parse: Key (part after the word 'append' is ignored), *value* (filename) e.g. `AppendFile0=some_append_contents.tlk`
   - Parse subsection [filename] mappings
   - For each mapping:
     - Parse: *[KEY](Container-Formats#key)* (ignored), *value* (source index)
     - Load entry from referenced file at *value* index
     - Append to dialog.tlk (gets new stringref)
     - Create token [StrRef](Audio-and-Localization-Formats#string-references-strref){value} from *value* to store the new stringref
5. Tokens are now available for substitution in:
   - [2DAList] sections (2DAMEMORY#=[StrRef](Audio-and-Localization-Formats#string-references-strref)#)
   - [GFFList] sections (FieldName=[StrRef](Audio-and-Localization-Formats#string-references-strref)#)
   - [CompileList] scripts (#[StrRef](Audio-and-Localization-Formats#string-references-strref)# tokens)

### Token Substitution Examples

**In [2DA files](2DA-File-Format)**: `name=StrRef0` (token gets replaced with actual stringref)

**In [GFF files](GFF-File-Format)**: `LocalizedName=StrRef0` (token gets replaced with actual stringref)

**In [NSS](NSS-File-Format) scripts**: `SendMessageToPC(GetFirstPC(), #StrRef0#);` (token gets replaced during compilation)

### Version History Notes

**TSLPatcher v1.2.8b6 (2006-10-03)**:

- Added optional `!SourceFile` and `!SourceFileF` keys to the `[TLKList]` section
- If present, these can be used to set an alternative name of the [TLK file](Audio-and-Localization-Formats#tlk) to use
- If left out, default values are `append.tlk` and `appendf.tlk` as before
- **Fixed bug**: Previously couldn't handle [TLK](Audio-and-Localization-Formats#tlk) entries with strings longer than 4096 characters - now supports strings of any size

**TSLPatcher v1.2.8b0 (2006-08-06)**:

- Changed processing order: [TLK](Audio-and-Localization-Formats#tlk) Appending now happens before Install List
- This allows [MOD](Container-Formats#erf), [ERF](Container-Formats#erf), or [RIM](Container-Formats#rim) files to be placed before [GFF](GFF-File-Format) and script compilation sections run

**TSLPatcher v1.2.8b8 (2006-12-02)**:

- Fixed bug that caused TSLPatcher to stop installation into games where the [`dialog.tlk`](Audio-and-Localization-Formats#tlk) file was write-protected

### See also

- [TLK-File-Format](Audio-and-Localization-Formats#tlk) -- Talk table structure and StrRef
- [TSLPatcher's Official Readme](TSLPatcher's-Official-Readme) -- General TSLPatcher and ChangeEdit
- [TSLPatcher 2DAList Syntax](TSLPatcher-Data-Syntax#2dalist-syntax)
  - Merge rows in [2DA](2DA-File-Format) tables
  - Pipe memorized [StrRef](Audio-and-Localization-Formats#string-references-strref) tokens into those cells
- [TSLPatcher GFFList Syntax](TSLPatcher-GFF-Syntax#gfflist-syntax) -- Modify [GFF](GFF-File-Format) with StrRef tokens
- [TSLPatcher SSFList Syntax](TSLPatcher-GFF-Syntax#ssflist-syntax) -- Modify soundset files with StrRef tokens
- [TSLPatcher InstallList Syntax](TSLPatcher-Install-and-Hack-Syntax#installlist-syntax) -- Install files and script compilation
- [HoloPatcher README for Mod Developers](HoloPatcher#mod-developers) -- PyKotor implementation
- [Community sources and archives](Home#community-sources-and-archives) -- DeadlyStream, LucasForums for TLK/StrRef modding


---
