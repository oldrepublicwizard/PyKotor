"""Generate NSS function documentation for wiki/NSS-File-Format.md stubs.

Reads KOTOR_FUNCTIONS and TSL_FUNCTIONS from scriptdefs.py, categorizes them,
and outputs wiki-formatted markdown blocks for each category section.

Usage:
    uv run helper_scripts/generate_nss_wiki.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

# Add pykotor to path
sys.path.insert(0, str(Path(__file__).parent.parent / "Libraries/PyKotor/src"))

from pykotor.common.scriptdefs import KOTOR_FUNCTIONS, TSL_FUNCTIONS
from pykotor.common.script import DataType, ScriptFunction, ScriptParam

# ─── Category assignment ──────────────────────────────────────────────────────
# Rules checked in ORDER - first match wins.
# Patterns are matched against the FULL function name using re.search().
# IMPORTANT: More specific rules MUST come before broader ones.

CATEGORY_RULES: list[tuple[str, str]] = [
    # ── Effects System ─────────────────────────────────────────────────────
    (r"^Effect", "Effects System"),

    # ── Item Properties ────────────────────────────────────────────────────
    (r"ItemProperty|^(Get|Add|Remove|Break|HasItem).*Property|^GetIsItemProperty", "Item Properties"),

    # ── Local Variables ────────────────────────────────────────────────────
    (r"^(Get|Set)Local(Boolean|Number|String|Object|Float)", "Local Variables"),

    # ── Global Variables ───────────────────────────────────────────────────
    (r"^(Get|Set)Global", "Global Variables"),

    # ── Sound and Music ────────────────────────────────────────────────────
    (r"^(Music|AmbientSound|PlaySound|SoundObject|SetSoundObject|GetSoundObject)", "Sound and Music Functions"),
    (r"BackgroundMusic|SoundObjectPlay|SoundObjectStop|SoundObjectSetVolume|SoundObjectSetPosition|SoundObjectGetState|^AmbientSound", "Sound and Music Functions"),

    # ── Alignment System ───────────────────────────────────────────────────
    (r"Alignment|GoodEvil|LawChaos|^AdjustAlignment|^GetAlignmentGoodEvil|^GetAlignmentLawChaos", "Alignment System"),
    (r"^GetIsEnemy|^GetIsFriend|^GetIsNeutral|^GetFactionEqual|^GetStandardFactionReputation|^SetStandardFactionReputation|^GetReputation|^SetReputation|FriendlyFireCheck|^GetIsFriend|^GetIsReactionType", "Alignment System"),

    # ── Class System ───────────────────────────────────────────────────────
    (r"^GetClassByPosition|^GetLevelByClass|^GetLevelByPosition|^GetHasSpell|^GetKnowsFeat|LevelUpHenchman|^GetTotalLevels|^GetSpellResistance|^GetLastSpellLevel|^GetSpellCastItem", "Class System"),

    # ── Abilities and Stats ────────────────────────────────────────────────
    (r"AbilityScore|AbilityModifier|^GetAbility|^SetAbility|HitPoints|ForcePoints|GetFortitude|GetWill|GetReflex|GetReflexAdjusted|Strength|Dexterity|Constitution|GetIntelligence|GetWisdom|GetCharisma|BaseAttackBonus|^GetCurrentHitPoints|^GetMaxHitPoints|^GetCurrentForcePoints|^GetMaxForcePoints", "Abilities and Stats"),

    # ── Skills and Feats ──────────────────────────────────────────────────
    (r"SkillRank|HasSkill|^GetSkill|^SetSkill|HasFeat|^GetHasFeat|^GetFeatX|FeatUsesRemaining|^GetLastSpell|^GetSpellFeatId|^SetFeatUsesRemaining", "Skills and Feats"),

    # ── Party Management ──────────────────────────────────────────────────
    (r"^(Add|Remove|Get|Set|Is|Show)Party|AvailableNPC|IsNPCPartyMember|IsObjectPartyMember|ShowPartySelection|SwitchPlayerCharacter", "Party Management"),

    # ── Player Character Functions ────────────────────────────────────────
    (r"^GetIsPC|^GetPCSpeaker|^SetPCSpeaker|^GetControlledCharacter|^SetCameraMode|^RewardXP|^RewardFeat|^RewardSkill|^GetPCName|PlayerRestrictMode|^GiveXPToCreature|^AwardLevelUpHenchman|^GetPCChatMessage|^SetPCChatMessage|^GetPCPublicCDKey|^SetPCSkinColor|^GetPlotFlag|^SetPlotFlag|^GetGender|^SetGender|^GetAge|^SetAge|^GetRace|^GetSubRace|^SetSubRace|^BootPC|^GetNumLevels", "Player Character Functions"),

    # ── Dialog and Conversation Functions ────────────────────────────────
    (r"^SpeakString|^SpeakUniqueTo|Conversation|^ActionStartConversation|IsInConversation|^PauseConversation|^ResumeConversation|^GetCurrentDialogString|Token(?:Integer|String|Float|Object|Boolean)|GetTokenPair|SetCustomToken|^GetPCSpeaker|^SetPCSpeaker|^GetFirstNPCInConversation|^GetLastConversationPlayed|^SetLastConversationPlayed", "Dialog and Conversation Functions"),

    # ── Combat Functions ──────────────────────────────────────────────────
    (r"^GetIsInCombat|^GetAttackTarget|^GetLastAttacker|^GetLastDamager|^GetLastKiller|^GetDamageDealers|^GetDamageDealtByType|^GetTotalDamageDealt|^CombatRoundStart|^ActionCombatRoundStart|^ActionAttack|CastSpell|^GetSpellId|^GetSpellTargetObject|^GetSpellTargetLocation|^GetSavingThrowCheckPenalty|^SetSavingThrowCheckPenalty|^GetLastSpellHarmful|^GetLastCastSpell|IsItemSizeGe|^GetWeaponRanged|^GetIsWeaponEffective|^GetNumWeapon|^GetLastHostileActor|^GetAoEObjectById|^ActionForceMoveToObject|^ActionForceMoveToLocation|^SetIsDestroyable|^GetIsDestroyable|^SetImmortal|^GetImmortal|^GetInvulnerable|^SetInvulnerable", "Combat Functions"),

    # ── Item Management ───────────────────────────────────────────────────
    # Match functions with "Item" in name (not followed by Property) + equip-related
    (r"(?!.*ItemProperty).*Item|^(Equip|Unequip)|CreateObject|^ActionPickUp|^ActionDropItem|^ActionGiveItem|^ActionTakeItem|^GetDroppableFlag|^SetDroppableFlag|^GetPickpocketable|^SetPickpocketable|^GetItemCursed|^SetItemCursed|^GetItemCharges|^SetItemCharges|^GetItemWeight|^GetIdentified|^SetIdentified|^GetStolenFlag|^SetStolenFlag", "Item Management"),

    # ── Module and Area Functions ────────────────────────────────────────
    (r"^GetArea\b|^GetModule|^JumpToArea|^ExploreAreaForPlayer|^GetAreaTransitionTarget|^SetAreaTransitionBMP|^GetAreaByTag|^GetObjectByArea|^SetAreaUnescapable|^GetAreaUnescapable|^GetTile|^GetFirstArea|^GetNextArea|^GetEntering|^GetExiting|^GetTransitionTarget|^SetTransitionTarget|^GetAreaSize|^GetEnteringObject|^GetExitingObject|^GetNearestObject.*Area|^SetWeather|^GetWeather|^GetTime|^SetTime|^GetCalendar|^SetCalendar|^GetHour|^GetMinute|^GetSecond|^GetMillisecond|^GetDay|^GetMonth|^GetYear", "Module and Area Functions"),

    # ── Object Query and Manipulation ─────────────────────────────────────
    (r"^GetObjectByTag|^GetNearestObject|^GetNearestCreature|^GetNearestEnemy|^DestroyObject|^CopyObject|^PlayAnimation|^ApplyEffectToObject|^ApplyEffectAtLocation|^RemoveEffect|^GetFirstEffect|^GetNextEffect|^GetEffectCreator|^GetEffectType|^GetIsObjectValid|^GetDistanceBetween|^GetDistanceToObject|^GetObjectType|^GetFacing|^SetFacing|^GetFacingFromLocation|^GetPosition|^SetPosition|^GetLocation|^SetLocation|^Location|^GetFirst(Creature|Door|Waypoint|Placeable|Trigger|Item)|^GetNext(Creature|Door|Waypoint|Placeable|Trigger|Item)|^CreateObject(?!.*OnObject)|^SpawnObject|^GetIs(Dead|PC|NPC|Alive|Enemy|Friend|Neutral|InCombat)|^GetTag|^GetName|^SetName|^GetObjectInArea", "Object Query and Manipulation"),

    # ── Actions (action-queue items) ──────────────────────────────────────
    (r"^Action|^ClearAllActions|^GetCurrentAction|^GetNumberOfActions|^AssignCommand|^DelayCommand", "Actions"),
]


def get_category(func: ScriptFunction) -> str:
    """Return the wiki category for this function."""
    name = func.name
    for pattern, category in CATEGORY_RULES:
        if re.search(pattern, name):
            return category
    return "Other Functions"



def get_routine_number(func: ScriptFunction) -> int | None:
    """Extract the routine number from the description string."""
    # Description typically starts with "// N: ..."
    desc = func.description or ""
    m = re.match(r"^//\s*(\d+)\s*:", desc.strip())
    if m:
        return int(m.group(1))
    return None


def get_param_type_name(dtype: DataType) -> str:
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


def format_signature(func: ScriptFunction) -> str:
    """Return the function signature like: FuncName(type param1, type param2=default)"""
    params = []
    for p in func.params:
        ptype = get_param_type_name(p.datatype)
        if p.default is not None:
            params.append(f"{ptype} {p.name}={p.default}")
        else:
            params.append(f"{ptype} {p.name}")
    rtype = get_param_type_name(func.returntype)
    sig = f"{rtype} {func.name}({', '.join(params)})"
    return sig


def format_function_doc(func: ScriptFunction, routine_num: int | None) -> str:
    """Format a function entry in wiki-doc format."""
    name_lower = func.name.lower()
    lines: list[str] = []

    # anchor
    lines.append(f'<a id="{name_lower}"></a>')
    lines.append("")

    # heading
    param_names = []
    for p in func.params:
        if p.default is not None:
            param_names.append(f"{p.name}={p.default}")
        else:
            param_names.append(p.name)
    heading_params = ", ".join(param_names)
    if routine_num is not None:
        lines.append(f"#### `{func.name}({heading_params})` - Routine {routine_num}")
    else:
        lines.append(f"#### `{func.name}({heading_params})`")
    lines.append("")

    # Parse description
    desc = (func.description or "").strip()
    # Remove trailing function signature line (last line usually repeats the signature)
    desc_lines = desc.splitlines()
    # Strip leading "// N: " comment prefix lines
    cleaned: list[str] = []
    for dl in desc_lines:
        dl_stripped = dl.strip()
        if dl_stripped.startswith("//"):
            # Remove leading comment markers
            content = re.sub(r"^//\s*\d+:\s*", "", dl_stripped, count=1)
            content = re.sub(r"^//\s*", "", content)
            content = content.rstrip()
            cleaned.append(content)
        else:
            # This is likely the function signature line - skip it
            pass

    # Remove last line if it looks like the function signature itself
    if cleaned and re.match(r"^[a-z_].*\(.*\)\s*;?\s*$", cleaned[-1], re.IGNORECASE):
        cleaned.pop()

    # Format description
    desc_text = "\n".join(cleaned).strip()
    if desc_text:
        lines.append(f"{desc_text}")
        lines.append("")

    # Parameters
    if func.params:
        lines.append("**Parameters:**")
        lines.append("")
        for p in func.params:
            ptype = get_param_type_name(p.datatype)
            default_str = f" (default: `{p.default}`)" if p.default is not None else ""
            lines.append(f"- `{p.name}`: `{ptype}`{default_str}")
        lines.append("")

    # Return type
    rtype = get_param_type_name(func.returntype)
    if rtype != "void":
        lines.append(f"**Returns:** `{rtype}`")
        lines.append("")

    return "\n".join(lines)


def build_category_map(
    functions: list[ScriptFunction],
) -> dict[str, list[tuple[int | None, ScriptFunction]]]:
    """Returns {category: [(routine_num, func), ...]} sorted by routine_num."""
    category_map: dict[str, list[tuple[int | None, ScriptFunction]]] = {}
    for func in functions:
        cat = get_category(func)
        n = get_routine_number(func)
        category_map.setdefault(cat, []).append((n, func))
    # Sort each category by routine number
    for cat in category_map:
        category_map[cat].sort(key=lambda x: (x[0] is None, x[0] or 0))
    return category_map


def main() -> None:
    from pykotor.common.scriptdefs import KOTOR_FUNCTIONS, TSL_FUNCTIONS

    kotor_map = build_category_map(list(KOTOR_FUNCTIONS))
    tsl_map = build_category_map(list(TSL_FUNCTIONS))

    # Find functions that are TSL-specific (not in KOTOR)
    kotor_names = {f.name for f in KOTOR_FUNCTIONS}
    tsl_only = [f for f in TSL_FUNCTIONS if f.name not in kotor_names]
    tsl_only_map = build_category_map(tsl_only)

    SECTIONS_ORDER = [
        "Abilities and Stats",
        "Actions",
        "Alignment System",
        "Class System",
        "Combat Functions",
        "Dialog and Conversation Functions",
        "Effects System",
        "Global Variables",
        "Item Management",
        "Item Properties",
        "Local Variables",
        "Module and Area Functions",
        "Object Query and Manipulation",
        "Other Functions",
        "Party Management",
        "Player Character Functions",
        "Skills and Feats",
        "Sound and Music Functions",
    ]

    print("=" * 80)
    print("SHARED FUNCTIONS (K1 & TSL) — fill-in content for stub sections")
    print("=" * 80)
    print()

    for section in SECTIONS_ORDER:
        entries = kotor_map.get(section, [])
        if not entries:
            print(f"### {section}")
            print()
            print(f"*No functions matched for {section}*")
            print()
            continue
        print(f"### {section}")
        print()
        for n, func in entries:
            print(format_function_doc(func, n))
        print()

    print()
    print("=" * 80)
    print("TSL-ONLY FUNCTIONS — fill-in content for TSL stub sections")
    print("=" * 80)
    print()

    for section in SECTIONS_ORDER:
        entries = tsl_only_map.get(section, [])
        if not entries:
            continue
        print(f"### {section}")
        print()
        for n, func in entries:
            print(format_function_doc(func, n))
        print()


if __name__ == "__main__":
    main()
