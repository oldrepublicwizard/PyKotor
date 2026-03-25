# Archived UTE / UTECreature class docstrings

## `UTE`

```
Stores encounter data.

UTE files are GFF-based format files that store encounter definitions including
creature spawn lists, difficulty, respawn settings, and script hooks.

Root fields cover spawn limits, faction, reset/respawn flags, script hooks, and a
``CreatureList`` of template ResRefs with CR and spawn flags. It has been observed that
KotOR II adds ``GuaranteedCount`` per creature row; KotOR I does not use that field when
loading encounters. Loader symbols/addresses are migrated to
``wiki/reverse_engineering_findings.md``.

Note: UTE uses ``GFFContent.UTE``.

Attributes:
----------
    resref: "TemplateResRef" field. The resource reference for this encounter template.
        Reference: https://github.com/th3w1zard1/Kotor.NET/tree/master/UTE.cs:15 (TemplateResRef property)

    tag: "Tag" field. Tag identifier for this encounter.
        Reference: https://github.com/th3w1zard1/Kotor.NET/tree/master/UTE.cs:13 (Tag property)

    comment: "Comment" field. Developer comment.
        Reference: https://github.com/th3w1zard1/Kotor.NET/tree/master/UTE.cs:33 (Comment property)

    active: "Active" field. Whether encounter is active.
        Reference: https://github.com/th3w1zard1/Kotor.NET/tree/master/UTE.cs:16 (Active property)

    difficulty_id: "DifficultyIndex" field. Difficulty index identifier.
        Reference: https://github.com/th3w1zard1/Kotor.NET/tree/master/UTE.cs:18 (DifficultyIndex property)

    faction_id: "Faction" field. Faction identifier.
        Reference: https://github.com/th3w1zard1/Kotor.NET/tree/master/UTE.cs:19 (Faction property)

    max_creatures: "MaxCreatures" field. Maximum number of creatures to spawn.
        Reference: https://github.com/th3w1zard1/Kotor.NET/tree/master/UTE.cs:20 (MaxCreatures property)

    player_only: "PlayerOnly" field. Whether encounter only triggers for player.
        Reference: https://github.com/th3w1zard1/Kotor.NET/tree/master/UTE.cs:21 (PlayerOnly property)

    rec_creatures: "RecCreatures" field. Recommended number of creatures.
        Reference: https://github.com/th3w1zard1/Kotor.NET/tree/master/UTE.cs:22 (RecCreatures property)

    reset: "Reset" field. Whether encounter resets after completion.
        Reference: https://github.com/th3w1zard1/Kotor.NET/tree/master/UTE.cs:23 (Reset property)

    reset_time: "ResetTime" field. Time in seconds before reset.
        Reference: https://github.com/th3w1zard1/Kotor.NET/tree/master/UTE.cs:24 (ResetTime property)

    respawns: "Respawns" field. Number of times encounter can respawn.
        Reference: https://github.com/th3w1zard1/Kotor.NET/tree/master/UTE.cs:25 (Respawns property)

    single_shot: "SpawnOption" field. Whether encounter spawns only once.
        Reference: https://github.com/th3w1zard1/Kotor.NET/tree/master/UTE.cs:26 (SpawnOption property)

    on_entered: "OnEntered" field. Script to run when encounter area is entered.
        Reference: https://github.com/th3w1zard1/Kotor.NET/tree/master/UTE.cs:27 (OnEntered property)

    on_exit: "OnExit" field. Script to run when leaving encounter area.
        Reference: https://github.com/th3w1zard1/Kotor.NET/tree/master/UTE.cs:28 (OnExit property)

    on_exhausted: "OnExhausted" field. Script to run when encounter is exhausted.
        Reference: https://github.com/th3w1zard1/Kotor.NET/tree/master/UTE.cs:29 (OnExhausted property)

    on_heartbeat: "OnHeartbeat" field. Script to run on heartbeat.
        Reference: https://github.com/th3w1zard1/Kotor.NET/tree/master/UTE.cs:30 (OnHeartbeat property)

    on_user_defined: "OnUserDefined" field. Script to run on user-defined event.
        Reference: https://github.com/th3w1zard1/Kotor.NET/tree/master/UTE.cs:31 (OnUserDefined property)

    creatures: List of UTECreature objects representing spawnable creatures.
        Reference: https://github.com/th3w1zard1/Kotor.NET/tree/master/UTE.cs:34 (Creatures property)

    palette_id: "PaletteID" field. Palette identifier. Used in toolset only.
        Reference: https://github.com/th3w1zard1/Kotor.NET/tree/master/UTE.cs:32 (PaletteID property)

    name: "LocalizedName" field. Localized name. Not used by the game engine.
        Reference: https://github.com/th3w1zard1/Kotor.NET/tree/master/UTE.cs:14 (LocalizedName property)

    unused_difficulty: "Difficulty" field. Difficulty value. Not used by the game engine.
        Reference: https://github.com/th3w1zard1/Kotor.NET/tree/master/UTE.cs:17 (Difficulty property)
```

## `UTECreature`

```
Stores data for a creature that can be spawned by an encounter.

Each ``CreatureList`` row stores template ResRef, CR, ``SingleSpawn``, optional
``GuaranteedCount`` (TSL), and toolset ``Appearance`` (not used by KotOR I encounter load).
Binary-level notes are migrated to ``wiki/reverse_engineering_findings.md``.

Attributes:
----------
    appearance_id: "Appearance" field. Appearance type identifier for this creature.
        Reference: https://github.com/th3w1zard1/Kotor.NET/tree/master/UTE.cs:39 (Appearance property)

    challenge_rating: "CR" field. Challenge rating value.
        Reference: https://github.com/th3w1zard1/Kotor.NET/tree/master/UTE.cs:40 (CR property)

    resref: "ResRef" field. Resource reference to creature template (UTC file).
        Reference: https://github.com/th3w1zard1/Kotor.NET/tree/master/UTE.cs:41 (ResRef property)

    single_spawn: "SingleSpawn" field. Whether this creature spawns only once.
        Reference: https://github.com/th3w1zard1/Kotor.NET/tree/master/UTE.cs:42 (SingleSpawn property)

    guaranteed_count: "GuaranteedCount" field. Guaranteed spawn count. KotOR 2 only.
        Reference: https://github.com/th3w1zard1/Kotor.NET/tree/master/UTE.cs:43 (GuaranteedCount property)
```

