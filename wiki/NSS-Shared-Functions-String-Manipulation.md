# String Manipulation

Part of the [NSS File Format Documentation](NSS-File-Format).

**Category:** Shared Functions (K1 & TSL)

This document provides detailed documentation for NWScript string manipulation functions. These functions allow scripts to work with text data, extract substrings, search within strings, convert case, and perform type conversions.

## Implementation cross-reference

String routines are registered with the script VM like other NWScript calls; **routine IDs** on this page follow `nwscript.nss` (K1/TSL). They are used heavily with [TLK](TLK-File-Format) entries and dialog-related APIs on [NSS-Shared-Functions-Dialog-and-Conversation-Functions](NSS-Shared-Functions-Dialog-and-Conversation-Functions).

- **PyKotor:** NSS → NCS — [`resource/formats/ncs/compiler/`](https://github.com/OldRepublicDevs/PyKotor/tree/master/Libraries/PyKotor/src/pykotor/resource/formats/ncs/compiler); routine metadata — [`scriptdefs.py` L3706+ (`GetStringLength`)](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/common/scriptdefs.py#L3706), [L3713+ (`GetStringUpperCase`)](https://github.com/OldRepublicDevs/PyKotor/blob/master/Libraries/PyKotor/src/pykotor/common/scriptdefs.py#L3713) (first K1 block; search the same file for other `GetString*` / `String*` symbols).

- **reone:** [`main.cpp`](https://github.com/modawan/reone/blob/master/src/libs/game/script/routine/impl/main.cpp) — [`GetStringLength` L547+](https://github.com/modawan/reone/blob/master/src/libs/game/script/routine/impl/main.cpp#L547), [`GetStringUpperCase` L557+](https://github.com/modawan/reone/blob/master/src/libs/game/script/routine/impl/main.cpp#L557); K1 `insert` — [`GetStringLength` L6916](https://github.com/modawan/reone/blob/master/src/libs/game/script/routine/impl/main.cpp#L6916), [`GetStringUpperCase` L6917](https://github.com/modawan/reone/blob/master/src/libs/game/script/routine/impl/main.cpp#L6917) (TSL second block [L7472](https://github.com/modawan/reone/blob/master/src/libs/game/script/routine/impl/main.cpp#L7472) / [L7473](https://github.com/modawan/reone/blob/master/src/libs/game/script/routine/impl/main.cpp#L7473)).

- **KotOR.js:** [`NWScriptDefK1.ts`](https://github.com/KobaltBlu/KotOR.js/blob/master/src/nwscript/NWScriptDefK1.ts) — [`GetStringLength` L899](https://github.com/KobaltBlu/KotOR.js/blob/master/src/nwscript/NWScriptDefK1.ts#L899), [`GetStringUpperCase` L908](https://github.com/KobaltBlu/KotOR.js/blob/master/src/nwscript/NWScriptDefK1.ts#L908).

- **Kotor.NET:** NCS bytecode layout — [`NCS.cs` L9+](https://github.com/NickHugi/Kotor.NET/blob/master/Kotor.NET/Formats/KotorNCS/NCS.cs#L9).

---

## String Manipulation Fundamentals

### Understanding Strings in NWScript

Strings in NWScript are:

- **Immutable** - String functions return new strings rather than modifying originals
- **Case-Sensitive** - String comparisons are case-sensitive by default
- **Indexed from 0** - String positions start at 0 (first character is at position 0)

### String Operations

String functions are used for:

- Text processing and parsing
- Building dynamic dialogue strings
- Extracting data from strings
- Formatting output
- Type conversions

---

## String Length and Validation

### GetStringLength

**Routine:** 59

#### Function Signature

```c
int GetStringLength(string sString);
```

#### Description

Gets the length (number of characters) of a string.

#### Parameters

- `sString`: String to measure

#### Returns

- Length of the string (number of characters)
- `-1` on error

#### Usage Examples

```c
// Get string length
string sText = "Hello World";
int nLength = GetStringLength(sText); // Returns 11
```

```c
// Check if string is empty
string sInput = GetGlobalString("PlayerInput");
if (GetStringLength(sInput) == 0) {
    // String is empty
}
```

**Pattern: Validate String**

```c
// Validate non-empty string
string sName = GetGlobalString("PlayerName");
if (GetStringLength(sName) > 0) {
    // String has content
    SpeakString("Welcome, " + sName + "!", TALKVOLUME_TALK);
}
```

---

## Case Conversion Functions

### GetStringUpperCase

**Routine:** 60

#### Function Signature

```c
string GetStringUpperCase(string sString);
```

#### Description

Converts all characters in a string to uppercase.

#### Parameters

- `sString`: String to convert

#### Returns

- Uppercase version of the string
- Empty string ("") on error

#### Usage Examples

```c
// Convert to uppercase
string sText = "hello world";
string sUpper = GetStringUpperCase(sText); // Returns "HELLO WORLD"
```

```c
// Case-insensitive comparison
string sInput = "Yes";
string sUpper = GetStringUpperCase(sInput);
if (sUpper == "YES") {
    // Match regardless of original case
}
```

---

### GetStringLowerCase

**Routine:** 61

#### Function Signature

```c
string GetStringLowerCase(string sString);
```

#### Description

Converts all characters in a string to lowercase.

#### Parameters

- `sString`: String to convert

#### Returns

- Lowercase version of the string
- Empty string ("") on error

#### Usage Examples

```c
// Convert to lowercase
string sText = "HELLO WORLD";
string sLower = GetStringLowerCase(sText); // Returns "hello world"
```

**Pattern: Case-Insensitive Comparison**

```c
// Compare strings ignoring case
string sInput = "Yes";
string sLower = GetStringLowerCase(sInput);
if (sLower == "yes") {
    // Match found
}
```

---

## Substring Functions

### GetSubString

**Routine:** 65

#### Function Signature

```c
string GetSubString(string sString, int nStart, int nCount);
```

#### Description

Extracts a substring from a string, starting at a specific position and taking a specified number of characters.

#### Parameters

- `sString`: Source string
- `nStart`: Starting position (0-based index)
- `nCount`: Number of characters to extract

#### Returns

- Substring extracted from the source string
- Empty string ("") on error or if indices are invalid

#### Usage Examples

```c
// Extract substring
string sText = "Hello World";
string sSub = GetSubString(sText, 0, 5); // Returns "Hello"
```

```c
// Extract middle portion
string sText = "Hello World";
string sSub = GetSubString(sText, 6, 5); // Returns "World"
```

**Pattern: Extract Prefix**

```c
// Extract first N characters
string sTag = "npc_merchant_01";
string sPrefix = GetSubString(sTag, 0, 4); // Returns "npc_"
```

**Pattern: Parse String Data**

```c
// Extract data from formatted string
string sData = "Item:123:Description";
string sItem = GetSubString(sData, 5, 3); // Extract "123"
```

#### Notes

- String indices start at 0
- `nStart` must be within string bounds
- `nCount` cannot exceed remaining characters
- Returns empty string if indices are invalid

---

### GetStringLeft

**Routine:** 63

#### Function Signature

```c
string GetStringLeft(string sString, int nCount);
```

#### Description

Gets the first `nCount` characters from the left (beginning) of a string.

#### Parameters

- `sString`: Source string
- `nCount`: Number of characters to extract from the left

#### Returns

- Left portion of the string
- Empty string ("") if `nCount` is 0 or negative, or if string is empty

#### Usage Examples

```c
// Get left portion
string sText = "Hello World";
string sLeft = GetStringLeft(sText, 5); // Returns "Hello"
```

```c
// Extract prefix
string sTag = "npc_merchant";
string sPrefix = GetStringLeft(sTag, 4); // Returns "npc_"
```

**Pattern: Check String Prefix**

```c
// Check if string starts with prefix
string sTag = "npc_merchant";
string sPrefix = GetStringLeft(sTag, 4);
if (sPrefix == "npc_") {
    // Tag starts with "npc_"
}
```

---

### GetStringRight

**Routine:** 62

#### Function Signature

```c
string GetStringRight(string sString, int nCount);
```

#### Description

Gets the last `nCount` characters from the right (end) of a string.

#### Parameters

- `sString`: Source string
- `nCount`: Number of characters to extract from the right

#### Returns

- Right portion of the string
- Empty string ("") if `nCount` is 0 or negative, or if string is empty

#### Usage Examples

```c
// Get right portion
string sText = "Hello World";
string sRight = GetStringRight(sText, 5); // Returns "World"
```

```c
// Extract suffix
string sTag = "item_sword_01";
string sSuffix = GetStringRight(sTag, 2); // Returns "01"
```

**Pattern: Extract File Extension**

```c
// Extract extension from filename
string sFile = "script.nss";
string sExt = GetStringRight(sFile, 3); // Returns "nss"
```

---

## String Search Functions

### FindSubString

**Routine:** 66

#### Function Signature

```c
int FindSubString(string sString, string sSubString);
```

#### Description

Finds the position of a substring within a string. Returns the index of the first occurrence.

#### Parameters

- `sString`: String to search in
- `sSubString`: Substring to search for

#### Returns

- Position (0-based index) of the first occurrence of the substring
- `-1` if substring is not found or on error

#### Usage Examples

```c
// Find substring
string sText = "Hello World";
int nPos = FindSubString(sText, "World"); // Returns 6
```

```c
// Check if substring exists
string sTag = "npc_merchant_01";
int nPos = FindSubString(sTag, "merchant");
if (nPos >= 0) {
    // Substring found
}
```

**Pattern: Check if String Contains Substring**

```c
// Check if string contains specific text
string sName = GetName(GetFirstPC());
if (FindSubString(sName, "Revan") >= 0) {
    // Name contains "Revan"
}
```

**Pattern: Extract After Substring**

```c
// Extract text after a marker
string sData = "Item:123:Description";
int nPos = FindSubString(sData, ":");
if (nPos >= 0) {
    string sAfter = GetSubString(sData, nPos + 1, GetStringLength(sData) - nPos - 1);
    // sAfter = "123:Description"
}
```

#### Notes

- Returns -1 if substring not found
- Search is case-sensitive
- Returns position of first occurrence only

---

## String Insertion Functions

### InsertString

**Routine:** 64

#### Function Signature

```c
string InsertString(string sDestination, string sString, int nPosition);
```

#### Description

Inserts a string into another string at a specified position.

#### Parameters

- `sDestination`: Destination string to insert into
- `sString`: String to insert
- `nPosition`: Position (0-based index) where to insert

#### Returns

- New string with the insertion
- Empty string ("") on error or if position is invalid

#### Usage Examples

```c
// Insert string
string sText = "Hello World";
string sNew = InsertString(sText, "Beautiful ", 6); // Returns "Hello Beautiful World"
```

```c
// Insert at beginning
string sText = "World";
string sNew = InsertString(sText, "Hello ", 0); // Returns "Hello World"
```

**Pattern: Build Dynamic String**

```c
// Build string by inserting parts
string sMessage = "Welcome!";
string sName = GetName(GetFirstPC());
string sFinal = InsertString(sMessage, sName + " ", 8); // "Welcome [Name]!"
```

#### Notes

- Position must be within string bounds (0 to length)
- Insertion happens before the character at the position
- Original strings are not modified (strings are immutable)

---

## Type Conversion Functions

### StringToInt

**Routine:** 232

#### Function Signature

```c
int StringToInt(string sString);
```

#### Description

Converts a string to an integer. Parses the numeric value from the string.

#### Parameters

- `sString`: String containing a number

#### Returns

- Integer value parsed from the string
- `0` if string is not a valid number or on error

#### Usage Examples

```c
// Convert string to int
string sNumber = "123";
int nValue = StringToInt(sNumber); // Returns 123
```

```c
// Parse number from formatted string
string sData = "Level:15";
int nPos = FindSubString(sData, ":");
if (nPos >= 0) {
    string sLevel = GetSubString(sData, nPos + 1, GetStringLength(sData) - nPos - 1);
    int nLevel = StringToInt(sLevel); // Returns 15
}
```

**Pattern: Parse Numeric Data**

```c
// Extract and convert number
string sGlobal = GetGlobalString("QuestProgress");
int nProgress = StringToInt(sGlobal);
if (nProgress > 0) {
    // Valid progress value
}
```

#### Notes

- Returns 0 for invalid strings
- Only parses integer portion (stops at first non-digit)
- Negative numbers are supported if string starts with "-"

---

### IntToString

**Routine:** 92

#### Function Signature

```c
string IntToString(int nInteger);
```

#### Description

Converts an integer to a string representation.

#### Parameters

- `nInteger`: Integer to convert

#### Returns

- String representation of the integer

#### Usage Examples

```c
// Convert int to string
int nLevel = 15;
string sLevel = IntToString(nLevel); // Returns "15"
```

**Pattern: Build Dynamic Messages**

```c
// Include numbers in messages
int nHP = GetCurrentHitPoints(GetFirstPC());
int nMaxHP = GetMaxHitPoints(GetFirstPC());
string sMessage = "HP: " + IntToString(nHP) + "/" + IntToString(nMaxHP);
SpeakString(sMessage, TALKVOLUME_TALK);
```

**Pattern: Format Quest Progress**

```c
// Format progress string
int nProgress = GetGlobalNumber("QuestProgress");
string sProgress = "Progress: " + IntToString(nProgress) + "%";
```

---

### StringToFloat

**Routine:** 233

#### Function Signature

```c
float StringToFloat(string sString);
```

#### Description

Converts a string to a float. Parses the numeric value from the string.

#### Parameters

- `sString`: String containing a number (can include decimal point)

#### Returns

- Float value parsed from the string
- `0.0` if string is not a valid number or on error

#### Usage Examples

```c
// Convert string to float
string sNumber = "123.45";
float fValue = StringToFloat(sNumber); // Returns 123.45
```

```c
// Parse float from string
string sData = "Distance:12.5";
int nPos = FindSubString(sData, ":");
if (nPos >= 0) {
    string sDist = GetSubString(sData, nPos + 1, GetStringLength(sData) - nPos - 1);
    float fDist = StringToFloat(sDist); // Returns 12.5
}
```

---

### FloatToString

**Routine:** 3

#### Function Signature

```c
string FloatToString(float fFloat, int nWidth = 0, int nDecimals = 0);
```

#### Description

Converts a float to a string representation with optional formatting.

#### Parameters

- `fFloat`: Float to convert
- `nWidth`: Minimum width of the string (pads with spaces if needed, 0 = no padding)
- `nDecimals`: Number of decimal places (0 = no decimals)

#### Returns

- String representation of the float

#### Usage Examples

```c
// Convert float to string
float fValue = 123.456;
string sValue = FloatToString(fValue); // Returns "123.456"
```

```c
// Format with decimals
float fValue = 123.456;
string sValue = FloatToString(fValue, 0, 2); // Returns "123.46" (rounded)
```

**Pattern: Format Distance**

```c
// Format distance with 1 decimal
float fDist = GetDistanceBetween(OBJECT_SELF, oTarget);
string sDist = FloatToString(fDist, 0, 1);
SpeakString("Distance: " + sDist + " meters", TALKVOLUME_TALK);
```

---

## Common Patterns and Best Practices

### Pattern: Parse Formatted String

```c
// Parse "Key:Value" format
string sData = "Level:15";
int nPos = FindSubString(sData, ":");
if (nPos >= 0) {
    string sKey = GetStringLeft(sData, nPos); // "Level"
    string sValue = GetSubString(sData, nPos + 1, GetStringLength(sData) - nPos - 1); // "15"
    int nLevel = StringToInt(sValue);
}
```

### Pattern: Case-Insensitive Comparison

```c
// Compare strings ignoring case
string sInput = "Yes";
string sLower = GetStringLowerCase(sInput);
if (sLower == "yes" || sLower == "y") {
    // Match found
}
```

### Pattern: Extract File Extension

```c
// Get file extension
string sFile = "script.nss";
int nPos = FindSubString(sFile, ".");
if (nPos >= 0) {
    string sExt = GetStringRight(sFile, GetStringLength(sFile) - nPos - 1); // "nss"
}
```

### Pattern: Build Dynamic Dialogue

```c
// Build dynamic message with variables
string sName = GetName(GetFirstPC());
int nLevel = GetHitDice(GetFirstPC());
string sMessage = "Welcome, " + sName + "! You are level " + IntToString(nLevel) + ".";
SpeakString(sMessage, TALKVOLUME_TALK);
```

### Pattern: Validate String Format

```c
// Check if string matches expected format
string sTag = "npc_merchant_01";
string sPrefix = GetStringLeft(sTag, 4);
if (sPrefix == "npc_") {
    // Valid NPC tag format
    string sSuffix = GetStringRight(sTag, 2);
    int nID = StringToInt(sSuffix);
}
```

### Best Practices

1. **Check String Length**: Use `GetStringLength()` to validate strings before operations
2. **Validate Indices**: Ensure substring indices are within bounds before extraction
3. **Handle -1 Returns**: `FindSubString()` returns -1 if not found - always check
4. **Case Sensitivity**: Remember string comparisons are case-sensitive
5. **Type Conversion**: Validate strings before converting to numbers
6. **String Immutability**: String functions return new strings - assign results to variables

---

## Related Functions

- String concatenation uses `+` operator: `string sResult = s1 + s2;`
- String comparison uses `==` operator: `if (s1 == s2)`
- `GetName()` - Get object name as string (see [Object Query](NSS-Shared-Functions-Object-Query-and-Manipulation))
- `GetTag()` - Get object tag as string (see [Object Query](NSS-Shared-Functions-Object-Query-and-Manipulation))

---

## Additional Notes

### String Indexing

- Strings are **0-indexed** (first character is at position 0)
- `GetSubString(s, 0, 1)` gets the first character
- `GetSubString(s, n, 1)` gets the character at position n
- Last character is at position `GetStringLength(s) - 1`

### String Immutability

Strings in NWScript are immutable:

- Functions return new strings
- Original strings are never modified
- Always assign results: `sNew = GetStringUpperCase(sOld);`

### Type Conversion Notes

- **StringToInt**: Returns 0 for invalid strings, stops at first non-digit
- **StringToFloat**: Returns 0.0 for invalid strings, supports decimal notation
- **IntToString**: Always succeeds (any int can be converted)
- **FloatToString**: Formatting parameters are optional

### Common String Operations

**Concatenation:**

```c
string s1 = "Hello";
string s2 = "World";
string s3 = s1 + " " + s2; // "Hello World"
```

**Comparison:**

```c
if (s1 == s2) {
    // Strings are equal (case-sensitive)
}
```

**Empty String Check:**

```c
if (GetStringLength(s) == 0) {
    // String is empty
}
```
