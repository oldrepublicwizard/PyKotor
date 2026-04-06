"""Apply NSS stub replacements to wiki/NSS-File-Format.md.

Reads KOTOR_FUNCTIONS, TSL_FUNCTIONS, KOTOR_CONSTANTS, TSL_CONSTANTS from
scriptdefs.py and replaces every stub section with generated documentation.

Usage:
    uv run helper_scripts/apply_nss_stubs.py [--dry-run]
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import TYPE_CHECKING

REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT / "Libraries/PyKotor/src"))
sys.path.insert(0, str(REPO_ROOT / "Libraries/Utility/src"))

from pykotor.common.script import DataType, ScriptConstant, ScriptFunction, ScriptParam
from pykotor.common.scriptdefs import KOTOR_CONSTANTS, KOTOR_FUNCTIONS, TSL_CONSTANTS, TSL_FUNCTIONS

# ─── TYPE NAME LOOKUP ─────────────────────────────────────────────────────────

def dtype_name(dtype: DataType) -> str:
    return {
        DataType.INT: "int",
        DataType.FLOAT: "float",
        DataType.STRING: "string",
        DataType.OBJECT: "object",
        DataType.VOID: "void",
        DataType.ACTION: "action",
        DataType.VECTOR: "vector",
        DataType.LOCATION: "location",
        DataType.TALENT: "talent",
        DataType.EFFECT: "effect",
        DataType.EVENT: "event",
        DataType.ITEMPROPERTY: "itemproperty",
    }.get(dtype, str(dtype).split(".")[-1].lower())


# ─── FUNCTION CATEGORIZATION ──────────────────────────────────────────────────

FUNC_CATEGORY_RULES: list[tuple[str, str]] = [
    (r"^Effect", "Effects System"),
    (r"ItemProperty|^(Get|Add|Remove|Break|HasItem).*Property|^GetIsItemProperty", "Item Properties"),
    (r"^(Get|Set)Local(Boolean|Number|String|Object|Float)", "Local Variables"),
    (r"^(Get|Set)Global", "Global Variables"),
    (r"^(Music|AmbientSound|PlaySound|SoundObject|SetSoundObject|GetSoundObject)", "Sound and Music Functions"),
    (r"BackgroundMusic|SoundObjectPlay|SoundObjectStop|SoundObjectSetVolume|SoundObjectSetPosition|SoundObjectGetState", "Sound and Music Functions"),
    (r"Alignment|GoodEvil|LawChaos|^AdjustAlignment", "Alignment System"),
    (r"^GetIsEnemy|^GetIsFriend|^GetIsNeutral|^GetFactionEqual|^GetStandardFactionReputation|^SetStandardFactionReputation|^GetReputation|^SetReputation|FriendlyFireCheck|^GetIsReactionType", "Alignment System"),
    (r"^GetClassByPosition|^GetLevelByClass|^GetLevelByPosition|^GetHasSpell|^GetKnowsFeat|LevelUpHenchman|^GetTotalLevels|^GetSpellResistance|^GetLastSpellLevel|^GetSpellCastItem", "Class System"),
    (r"AbilityScore|AbilityModifier|^GetAbility|^SetAbility|HitPoints|ForcePoints|GetFortitude|GetWill|GetReflex|GetReflexAdjusted|Strength|Dexterity|Constitution|GetIntelligence|GetWisdom|GetCharisma|BaseAttackBonus|^GetCurrentHitPoints|^GetMaxHitPoints|^GetCurrentForcePoints|^GetMaxForcePoints", "Abilities and Stats"),
    (r"SkillRank|HasSkill|^GetSkill|^SetSkill|HasFeat|^GetHasFeat|^GetFeatX|FeatUsesRemaining|^GetLastSpell|^GetSpellFeatId|^SetFeatUsesRemaining", "Skills and Feats"),
    (r"^(Add|Remove|Get|Set|Is|Show)Party|AvailableNPC|IsNPCPartyMember|IsObjectPartyMember|ShowPartySelection|SwitchPlayerCharacter", "Party Management"),
    (r"^GetIsPC|^GetPCSpeaker|^SetPCSpeaker|^GetControlledCharacter|^SetCameraMode|^RewardXP|^RewardFeat|^RewardSkill|^GetPCName|PlayerRestrictMode|^GiveXPToCreature|^AwardLevelUpHenchman|^GetPCChatMessage|^SetPCChatMessage|^GetPCPublicCDKey|^SetPCSkinColor|^GetPlotFlag|^SetPlotFlag|^GetGender|^SetGender|^GetAge|^SetAge|^GetRace|^GetSubRace|^SetSubRace|^BootPC|^GetNumLevels", "Player Character Functions"),
    (r"^SpeakString|^SpeakUniqueTo|Conversation|^ActionStartConversation|IsInConversation|^PauseConversation|^ResumeConversation|^GetCurrentDialogString|Token(?:Integer|String|Float|Object|Boolean)|GetTokenPair|SetCustomToken|^GetFirstNPCInConversation|^GetLastConversationPlayed|^SetLastConversationPlayed", "Dialog and Conversation Functions"),
    (r"^GetIsInCombat|^GetAttackTarget|^GetLastAttacker|^GetLastDamager|^GetLastKiller|^GetDamageDealers|^GetDamageDealtByType|^GetTotalDamageDealt|^CombatRoundStart|^ActionCombatRoundStart|^ActionAttack|CastSpell|^GetSpellId|^GetSpellTargetObject|^GetSpellTargetLocation|^GetSavingThrowCheckPenalty|^SetSavingThrowCheckPenalty|^GetLastSpellHarmful|^GetLastCastSpell|IsItemSizeGe|^GetWeaponRanged|^GetIsWeaponEffective|^GetNumWeapon|^GetLastHostileActor|^GetAoEObjectById|^ActionForceMoveToObject|^ActionForceMoveToLocation|^SetIsDestroyable|^GetIsDestroyable|^SetImmortal|^GetImmortal|^GetInvulnerable|^SetInvulnerable", "Combat Functions"),
    (r"(?!.*ItemProperty).*Item|^(Equip|Unequip)|CreateObject|^ActionPickUp|^ActionDropItem|^ActionGiveItem|^ActionTakeItem|^GetDroppableFlag|^SetDroppableFlag|^GetPickpocketable|^SetPickpocketable|^GetItemCursed|^SetItemCursed|^GetItemCharges|^SetItemCharges|^GetItemWeight|^GetIdentified|^SetIdentified|^GetStolenFlag|^SetStolenFlag", "Item Management"),
    (r"^GetArea\b|^GetModule|^JumpToArea|^ExploreAreaForPlayer|^GetAreaTransitionTarget|^SetAreaTransitionBMP|^GetAreaByTag|^GetObjectByArea|^SetAreaUnescapable|^GetAreaUnescapable|^GetTile|^GetFirstArea|^GetNextArea|^GetEntering|^GetExiting|^GetTransitionTarget|^SetTransitionTarget|^GetAreaSize|^GetEnteringObject|^GetExitingObject|^SetWeather|^GetWeather|^GetTime|^SetTime|^GetCalendar|^SetCalendar|^GetHour|^GetMinute|^GetSecond|^GetMillisecond|^GetDay|^GetMonth|^GetYear", "Module and Area Functions"),
    (r"^GetObjectByTag|^GetNearestObject|^GetNearestCreature|^GetNearestEnemy|^DestroyObject|^CopyObject|^PlayAnimation|^ApplyEffectToObject|^ApplyEffectAtLocation|^RemoveEffect|^GetFirstEffect|^GetNextEffect|^GetEffectCreator|^GetEffectType|^GetIsObjectValid|^GetDistanceBetween|^GetDistanceToObject|^GetObjectType|^GetFacing|^SetFacing|^GetFacingFromLocation|^GetPosition|^SetPosition|^GetLocation|^SetLocation|^Location\b|^GetFirst(Creature|Door|Waypoint|Placeable|Trigger|Item)|^GetNext(Creature|Door|Waypoint|Placeable|Trigger|Item)|^CreateObject(?!.*OnObject)|^SpawnObject|^GetTag|^GetName|^SetName|^GetObjectInArea", "Object Query and Manipulation"),
    (r"^Action|^ClearAllActions|^GetCurrentAction|^GetNumberOfActions|^AssignCommand|^DelayCommand", "Actions"),
]


def categorize_function(func: ScriptFunction) -> str:
    for pattern, cat in FUNC_CATEGORY_RULES:
        if re.search(pattern, func.name):
            return cat
    return "Other Functions"


def get_routine_num(func: ScriptFunction) -> int | None:
    m = re.match(r"^//\s*(\d+)\s*:", (func.description or "").strip())
    return int(m.group(1)) if m else None


def format_func_doc(func: ScriptFunction) -> str:
    name_lower = func.name.lower()
    lines: list[str] = []

    lines.append(f'<a id="{name_lower}"></a>')
    lines.append("")

    param_names = []
    for p in func.params:
        if p.default is not None:
            param_names.append(f"{p.name}={p.default}")
        else:
            param_names.append(p.name)
    heading_params = ", ".join(param_names)
    n = get_routine_num(func)
    if n is not None:
        lines.append(f"#### `{func.name}({heading_params})` - Routine {n}")
    else:
        lines.append(f"#### `{func.name}({heading_params})`")
    lines.append("")

    # Parse description: strip "//" comment lines
    desc = (func.description or "").strip()
    desc_lines = desc.splitlines()
    cleaned: list[str] = []
    for dl in desc_lines:
        ds = dl.strip()
        if ds.startswith("//"):
            # Strip leading "// N: " or "// "
            content = re.sub(r"^//\s*\d+:\s*", "", ds, count=1)
            content = re.sub(r"^//\s*", "", content).rstrip()
            cleaned.append(content)
    # Drop last line if it looks like a function signature
    if cleaned and re.match(r"^[A-Za-z_][A-Za-z0-9_]*\s*\(.*\)\s*;?\s*$", cleaned[-1]):
        cleaned.pop()
    desc_text = "\n".join(cleaned).strip()
    if desc_text:
        lines.append(desc_text)
        lines.append("")

    if func.params:
        lines.append("**Parameters:**")
        lines.append("")
        for p in func.params:
            pt = dtype_name(p.datatype)
            default_str = f" (default: `{p.default}`)" if p.default is not None else ""
            lines.append(f"- `{p.name}`: `{pt}`{default_str}")
        lines.append("")

    rtype = dtype_name(func.returntype)
    if rtype != "void":
        lines.append(f"**Returns:** `{rtype}`")
        lines.append("")

    return "\n".join(lines)


def build_func_section_content(funcs: list[ScriptFunction]) -> str:
    if not funcs:
        return "*No functions in this category.*\n"
    sorted_funcs = sorted(funcs, key=lambda f: (get_routine_num(f) is None, get_routine_num(f) or 0))
    parts = [format_func_doc(f) for f in sorted_funcs]
    return "\n".join(parts) + "\n"


# ─── CONSTANT CATEGORIZATION ──────────────────────────────────────────────────

CONST_CATEGORY_RULES: list[tuple[str, str]] = [
    (r"^ABILITY_", "Ability Constants"),
    (r"^ALIGNMENT_", "Alignment Constants"),
    (r"^CLASS_TYPE_", "Class type Constants"),
    (r"^INVENTORY_SLOT_", "Inventory Constants"),
    (r"^NPC_", "NPC Constants"),
    (r"^OBJECT_TYPE_", "Object type Constants"),
    (r"^PLANET_", "Planet Constants"),
    (r"^VFX_", "Visual Effects (VFX)"),
]


def categorize_constant(c: ScriptConstant) -> str:
    for pattern, cat in CONST_CATEGORY_RULES:
        if re.match(pattern, c.name):
            return cat
    return "Other Constants"


def build_const_section_content(consts: list[ScriptConstant]) -> str:
    if not consts:
        return "*No constants in this category.*\n"
    lines = [
        "| Constant | Type | Value |",
        "|----------|------|-------|",
    ]
    for c in consts:
        val = c.value
        if isinstance(val, float):
            val_str = f"`{val}`"
        elif isinstance(val, str):
            val_str = f'`"{val}"`'
        else:
            val_str = f"`{val}`"
        lines.append(f"| `{c.name}` | `{dtype_name(c.datatype)}` | {val_str} |")
    return "\n".join(lines) + "\n"


# ─── BUILD ALL SECTION CONTENT ────────────────────────────────────────────────

# H2 heading → context key
H2_TO_CONTEXT: dict[str, str] = {
    "## Shared Functions (K1 & TSL)": "shared_functions",
    "## K1-Only Functions": "k1_only_functions",
    "## TSL-Only Functions": "tsl_only_functions",
    "## Shared Constants (K1 & TSL)": "shared_constants",
    "## K1-Only Constants": "k1_only_constants",
    "## TSL-Only Constants": "tsl_only_constants",
}

CONST_CONTEXTS = {"shared_constants", "k1_only_constants", "tsl_only_constants"}

# These H3 sections already have documented content — do NOT replace
SKIP_H3_NAMES: set[str] = {"Party Management"}

ALL_FUNC_SECTIONS = [
    "Abilities and Stats", "Actions", "Alignment System", "Class System",
    "Combat Functions", "Dialog and Conversation Functions", "Effects System",
    "Global Variables", "Item Management", "Item Properties", "Local Variables",
    "Module and Area Functions", "Object Query and Manipulation", "Other Functions",
    "Party Management", "Player Character Functions", "Skills and Feats",
    "Sound and Music Functions",
]

ALL_CONST_SECTIONS = [
    "Ability Constants", "Alignment Constants", "Class type Constants",
    "Inventory Constants", "NPC Constants", "Object type Constants",
    "Other Constants", "Planet Constants", "Visual Effects (VFX)",
]


def build_all_section_content() -> dict[tuple[str, str], str]:
    kotor_names = {f.name for f in KOTOR_FUNCTIONS}
    tsl_names = {f.name for f in TSL_FUNCTIONS}
    kotor_const_names = {c.name for c in KOTOR_CONSTANTS}

    # Function sets
    shared_funcs = list(KOTOR_FUNCTIONS)
    k1_only_funcs = [f for f in KOTOR_FUNCTIONS if f.name not in tsl_names]
    tsl_only_funcs = [f for f in TSL_FUNCTIONS if f.name not in kotor_names]

    # Constant sets
    shared_consts = list(KOTOR_CONSTANTS)
    k1_only_consts = [c for c in KOTOR_CONSTANTS if c.name not in {c2.name for c2 in TSL_CONSTANTS}]
    tsl_only_consts = [c for c in TSL_CONSTANTS if c.name not in kotor_const_names]

    def cat_funcs(funcs: list[ScriptFunction]) -> dict[str, list[ScriptFunction]]:
        result: dict[str, list[ScriptFunction]] = {}
        for f in funcs:
            result.setdefault(categorize_function(f), []).append(f)
        return result

    def cat_consts(consts: list[ScriptConstant]) -> dict[str, list[ScriptConstant]]:
        result: dict[str, list[ScriptConstant]] = {}
        for c in consts:
            result.setdefault(categorize_constant(c), []).append(c)
        return result

    shared_fb = cat_funcs(shared_funcs)
    k1_fb = cat_funcs(k1_only_funcs)
    tsl_fb = cat_funcs(tsl_only_funcs)
    shared_cb = cat_consts(shared_consts)
    k1_cb = cat_consts(k1_only_consts)
    tsl_cb = cat_consts(tsl_only_consts)

    content: dict[tuple[str, str], str] = {}

    for sec in ALL_FUNC_SECTIONS:
        content[("shared_functions", sec)] = build_func_section_content(shared_fb.get(sec, []))
        content[("k1_only_functions", sec)] = build_func_section_content(k1_fb.get(sec, []))
        content[("tsl_only_functions", sec)] = build_func_section_content(tsl_fb.get(sec, []))

    for sec in ALL_CONST_SECTIONS:
        content[("shared_constants", sec)] = build_const_section_content(shared_cb.get(sec, []))
        content[("k1_only_constants", sec)] = build_const_section_content(k1_cb.get(sec, []))
        content[("tsl_only_constants", sec)] = build_const_section_content(tsl_cb.get(sec, []))

    return content


# ─── STUB DETECTION ───────────────────────────────────────────────────────────

_STUB_FUNC_PATTERNS = [
    re.compile(r"See \[.*?\]\(NSS-File-Format#.*?\) for detailed documentation\."),
    re.compile(r"Shared combat routines:"),
    re.compile(r"Shared routines: \[NSS-Shared-Functions"),
]


def is_stub(h3_body: str, context: str) -> bool:
    """Return True if this H3 section body is a stub that needs replacement."""
    stripped = h3_body.strip()
    if context in CONST_CONTEXTS:
        # Constants: stub if no markdown table exists
        return "|" not in stripped
    # Functions: stub if contains a known stub pattern
    return any(pat.search(stripped) for pat in _STUB_FUNC_PATTERNS)


# ─── FILE PATCHING ────────────────────────────────────────────────────────────

def patch_markdown(content: str, section_content: dict[tuple[str, str], str]) -> tuple[str, int]:
    """
    Patch all stub sections in the markdown.
    Returns (patched_content, count_of_replacements).
    """
    replacements = 0

    # Split by H2 headings (keeping the heading)
    h2_parts = re.split(r"^(## .+)$", content, flags=re.MULTILINE)
    # h2_parts = [preamble, h2_heading, body, h2_heading, body, ...]

    result_parts: list[str] = [h2_parts[0]]  # preamble before first ##

    for idx in range(1, len(h2_parts), 2):
        h2_heading = h2_parts[idx]
        h2_body = h2_parts[idx + 1] if idx + 1 < len(h2_parts) else ""

        ctx = H2_TO_CONTEXT.get(h2_heading.strip())
        result_parts.append(h2_heading)

        if not ctx:
            # Not a section we process; keep as-is
            result_parts.append(h2_body)
            continue

        # Split H2 body by H3 headings
        h3_parts = re.split(r"^(### .+)$", h2_body, flags=re.MULTILINE)
        # h3_parts = [preamble, h3_heading, body, ...]

        result_h3: list[str] = [h3_parts[0]]  # text before first H3

        for jdx in range(1, len(h3_parts), 2):
            h3_heading = h3_parts[jdx]
            h3_body = h3_parts[jdx + 1] if jdx + 1 < len(h3_parts) else ""

            h3_name = h3_heading.strip()[4:].strip()  # strip "### "

            if h3_name not in SKIP_H3_NAMES and is_stub(h3_body, ctx):
                key = (ctx, h3_name)
                replacement = section_content.get(key)
                if replacement is not None:
                    result_h3.append(h3_heading)
                    result_h3.append("\n\n")
                    result_h3.append(replacement.strip())
                    result_h3.append("\n")
                    replacements += 1
                    continue

            result_h3.append(h3_heading)
            result_h3.append(h3_body)

        result_parts.append("".join(result_h3))

    return "".join(result_parts), replacements


# ─── MAIN ─────────────────────────────────────────────────────────────────────

WIKI_PATHS = [
    REPO_ROOT / "wiki" / "NSS-File-Format.md",
    REPO_ROOT / "Tools" / "HolocronToolset" / "src" / "toolset" / "help" / "wiki" / "NSS-File-Format.md",
]


def main() -> None:
    dry_run = "--dry-run" in sys.argv
    show_stats = "--stats" in sys.argv

    print("Building section content from scriptdefs.py...")
    section_content = build_all_section_content()

    if show_stats:
        print("\nSection content sizes:")
        for (ctx, sec), content in sorted(section_content.items()):
            lines = content.count("\n")
            print(f"  [{ctx}] {sec}: {lines} lines")
        print()

    for wiki_path in WIKI_PATHS:
        if not wiki_path.exists():
            print(f"  SKIP (not found): {wiki_path}")
            continue

        original = wiki_path.read_text(encoding="utf-8")
        patched, count = patch_markdown(original, section_content)

        if dry_run:
            print(f"  DRY-RUN {wiki_path}: would replace {count} stub section(s)")
            print(f"  Original size: {len(original):,} bytes / {original.count(chr(10)):,} lines")
            print(f"  Patched size:  {len(patched):,} bytes / {patched.count(chr(10)):,} lines")
        else:
            wiki_path.write_text(patched, encoding="utf-8")
            print(f"  WROTE {wiki_path}")
            print(f"  Replaced {count} stub section(s)")
            print(f"  {len(patched):,} bytes / {patched.count(chr(10)):,} lines")


if __name__ == "__main__":
    main()
