================================================================================
SHARED FUNCTIONS (K1 & TSL) ù fill-in content for stub sections
================================================================================

### Abilities and Stats

<a id="getcurrenthitpoints"></a>

#### `GetCurrentHitPoints(oObject=0)` - Routine 49

Get the current hitpoints of oObject
* Return value on error: 0

**Parameters:**

- `oObject`: `object` (default: `0`)

**Returns:** `int`

<a id="getmaxhitpoints"></a>

#### `GetMaxHitPoints(oObject=0)` - Routine 50

Get the maximum hitpoints of oObject
* Return value on error: 0

**Parameters:**

- `oObject`: `object` (default: `0`)

**Returns:** `int`

<a id="getcurrentforcepoints"></a>

#### `GetCurrentForcePoints(oObject=0)` - Routine 55

returns the current force points for the creature

**Parameters:**

- `oObject`: `object` (default: `0`)

**Returns:** `int`

<a id="getmaxforcepoints"></a>

#### `GetMaxForcePoints(oObject=0)` - Routine 56

returns the Max force points for the creature

**Parameters:**

- `oObject`: `object` (default: `0`)

**Returns:** `int`

<a id="getabilityscore"></a>

#### `GetAbilityScore(oCreature, nAbilityType)` - Routine 139

Get the ability score of type nAbility for a creature (otherwise 0)
- oCreature: the creature whose ability score we wish to find out
- nAbilityType: ABILITY_*
Return value on error: 0

**Parameters:**

- `oCreature`: `object`
- `nAbilityType`: `int`

**Returns:** `int`

<a id="getreflexadjusteddamage"></a>

#### `GetReflexAdjustedDamage(nDamage, oTarget, nDC, nSaveType=0, oSaveVersus=0)` - Routine 299

Use this in spell scripts to get nDamage adjusted by oTarget's reflex and
evasion saves.
- nDamage
- oTarget
- nDC: Difficulty check
- nSaveType: SAVING_THROW_TYPE_*
- oSaveVersus

**Parameters:**

- `nDamage`: `int`
- `oTarget`: `object`
- `nDC`: `int`
- `nSaveType`: `int` (default: `0`)
- `oSaveVersus`: `object` (default: `0`)

**Returns:** `int`

<a id="getabilitymodifier"></a>

#### `GetAbilityModifier(nAbility, oCreature=0)` - Routine 331

Returns the ability modifier for the specified ability
Get oCreature's ability modifier for nAbility.
- nAbility: ABILITY_*
- oCreature

**Parameters:**

- `nAbility`: `int`
- `oCreature`: `object` (default: `0`)

**Returns:** `int`

<a id="getfortitudesavingthrow"></a>

#### `GetFortitudeSavingThrow(oTarget)` - Routine 491

Get oTarget's base fortitude saving throw value (this will only work for
creatures, doors, and placeables).
* Returns 0 if oTarget is invalid.

**Parameters:**

- `oTarget`: `object`

**Returns:** `int`

<a id="getwillsavingthrow"></a>

#### `GetWillSavingThrow(oTarget)` - Routine 492

Get oTarget's base will saving throw value (this will only work for creatures,
doors, and placeables).
* Returns 0 if oTarget is invalid.

**Parameters:**

- `oTarget`: `object`

**Returns:** `int`

<a id="getreflexsavingthrow"></a>

#### `GetReflexSavingThrow(oTarget)` - Routine 493

Get oTarget's base reflex saving throw value (this will only work for
creatures, doors, and placeables).
* Returns 0 if oTarget is invalid.

**Parameters:**

- `oTarget`: `object`

**Returns:** `int`

<a id="swmg_adjustfollowerhitpoints"></a>

#### `SWMG_AdjustFollowerHitPoints(oFollower, nHP, nAbsolute=0)` - Routine 590

adjusts a followers hit points, can specify the absolute value to set to
SWMG_AdjustFollowerHitPoints

**Parameters:**

- `oFollower`: `object`
- `nHP`: `int`
- `nAbsolute`: `int` (default: `0`)

**Returns:** `int`

<a id="swmg_setfollowerhitpoints"></a>

#### `SWMG_SetFollowerHitPoints(oFollower, nHP)` - Routine 604

SWMG_SetFollowerHitPoints

**Parameters:**

- `oFollower`: `object`
- `nHP`: `int`

<a id="swmg_gethitpoints"></a>

#### `SWMG_GetHitPoints(oFollower)` - Routine 616

SWMG_GetHitPoints

**Parameters:**

- `oFollower`: `object`

**Returns:** `int`

<a id="swmg_getmaxhitpoints"></a>

#### `SWMG_GetMaxHitPoints(oFollower)` - Routine 617

SWMG_GetMaxHitPoints

**Parameters:**

- `oFollower`: `object`

**Returns:** `int`

<a id="swmg_setmaxhitpoints"></a>

#### `SWMG_SetMaxHitPoints(oFollower, nMaxHP)` - Routine 618

SWMG_SetMaxHitPoints

**Parameters:**

- `oFollower`: `object`
- `nMaxHP`: `int`

<a id="setmaxhitpoints"></a>

#### `SetMaxHitPoints(oObject, nMaxHP)` - Routine 758

SetMaxHitPoints
Set the maximum hitpoints of oObject
The objects maximum AND current hitpoints will be nMaxHP after the function is called

**Parameters:**

- `oObject`: `object`
- `nMaxHP`: `int`


### Actions

<a id="assigncommand"></a>

#### `AssignCommand(oActionSubject, aActionToAssign)` - Routine 6

Assign aActionToAssign to oActionSubject.
* No return value, but if an error occurs, the log file will contain
"AssignCommand failed."
(If the object doesn't exist, nothing happens.)

**Parameters:**

- `oActionSubject`: `object`
- `aActionToAssign`: `action`

<a id="delaycommand"></a>

#### `DelayCommand(fSeconds, aActionToDelay)` - Routine 7

Delay aActionToDelay by fSeconds.
* No return value, but if an error occurs, the log file will contain
"DelayCommand failed.".

**Parameters:**

- `fSeconds`: `float`
- `aActionToDelay`: `action`

<a id="clearallactions"></a>

#### `ClearAllActions()` - Routine 9

Clear all the actions of the caller. (This will only work on Creatures)
* No return value, but if an error occurs, the log file will contain
"ClearAllActions failed.".

<a id="actionrandomwalk"></a>

#### `ActionRandomWalk()` - Routine 20

The action subject will generate a random location near its current location
and pathfind to it.  All commands will remove a RandomWalk() from the action
queue if there is one in place.
* No return value, but if an error occurs the log file will contain
"ActionRandomWalk failed."

<a id="actionmovetolocation"></a>

#### `ActionMoveToLocation(lDestination, bRun=0)` - Routine 21

The action subject will move to lDestination.
- lDestination: The object will move to this location.  If the location is
invalid or a path cannot be found to it, the command does nothing.
- bRun: If this is TRUE, the action subject will run rather than walk
* No return value, but if an error occurs the log file will contain
"MoveToPoint failed."

**Parameters:**

- `lDestination`: `location`
- `bRun`: `int` (default: `0`)

<a id="actionmovetoobject"></a>

#### `ActionMoveToObject(oMoveTo, bRun=0, fRange=1.0)` - Routine 22

Cause the action subject to move to a certain distance from oMoveTo.
If there is no path to oMoveTo, this command will do nothing.
- oMoveTo: This is the object we wish the action subject to move to
- bRun: If this is TRUE, the action subject will run rather than walk
- fRange: This is the desired distance between the action subject and oMoveTo
* No return value, but if an error occurs the log file will contain
"ActionMoveToObject failed."

**Parameters:**

- `oMoveTo`: `object`
- `bRun`: `int` (default: `0`)
- `fRange`: `float` (default: `1.0`)

<a id="actionmoveawayfromobject"></a>

#### `ActionMoveAwayFromObject(oFleeFrom, bRun=0, fMoveAwayRange=40.0)` - Routine 23

Cause the action subject to move to a certain distance away from oFleeFrom.
- oFleeFrom: This is the object we wish the action subject to move away from.
If oFleeFrom is not in the same area as the action subject, nothing will
happen.
- bRun: If this is TRUE, the action subject will run rather than walk
- fMoveAwayRange: This is the distance we wish the action subject to put
between themselves and oFleeFrom
* No return value, but if an error occurs the log file will contain
"ActionMoveAwayFromObject failed."

**Parameters:**

- `oFleeFrom`: `object`
- `bRun`: `int` (default: `0`)
- `fMoveAwayRange`: `float` (default: `40.0`)

<a id="actionspeakstring"></a>

#### `ActionSpeakString(sStringToSpeak, nTalkVolume=0)` - Routine 39

Add a speak action to the action subject.
- sStringToSpeak: String to be spoken
- nTalkVolume: TALKVOLUME_*

**Parameters:**

- `sStringToSpeak`: `string`
- `nTalkVolume`: `int` (default: `0`)

<a id="actionplayanimation"></a>

#### `ActionPlayAnimation(nAnimation, fSpeed=1.0, fDurationSeconds=0.0)` - Routine 40

Cause the action subject to play an animation
- nAnimation: ANIMATION_*
- fSpeed: Speed of the animation
- fDurationSeconds: Duration of the animation (this is not used for Fire and
Forget animations) If a time of -1.0f is specified for a looping animation
it will loop until the next animation is applied.

**Parameters:**

- `nAnimation`: `int`
- `fSpeed`: `float` (default: `1.0`)
- `fDurationSeconds`: `float` (default: `0.0`)

<a id="actionopendoor"></a>

#### `ActionOpenDoor(oDoor)` - Routine 43

Cause the action subject to open oDoor

**Parameters:**

- `oDoor`: `object`

<a id="actionclosedoor"></a>

#### `ActionCloseDoor(oDoor)` - Routine 44

Cause the action subject to close oDoor

**Parameters:**

- `oDoor`: `object`

<a id="actionforcefollowobject"></a>

#### `ActionForceFollowObject(oFollow, fFollowDistance=0.0)` - Routine 167

The action subject will follow oFollow until a ClearAllActions() is called.
- oFollow: this is the object to be followed
- fFollowDistance: follow distance in metres
* No return value

**Parameters:**

- `oFollow`: `object`
- `fFollowDistance`: `float` (default: `0.0`)

<a id="actionjumptoobject"></a>

#### `ActionJumpToObject(oToJumpTo, bWalkStraightLineToPoint=1)` - Routine 196

Jump to an object ID, or as near to it as possible.

**Parameters:**

- `oToJumpTo`: `object`
- `bWalkStraightLineToPoint`: `int` (default: `1`)

<a id="actionwait"></a>

#### `ActionWait(fSeconds)` - Routine 202

Do nothing for fSeconds seconds.

**Parameters:**

- `fSeconds`: `float`

<a id="actionjumptolocation"></a>

#### `ActionJumpToLocation(lLocation)` - Routine 214

The subject will jump to lLocation instantly (even between areas).
If lLocation is invalid, nothing will happen.

**Parameters:**

- `lLocation`: `location`

<a id="actionspeakstringbystrref"></a>

#### `ActionSpeakStringByStrRef(nStrRef, nTalkVolume=0)` - Routine 240

Causes the creature to speak a translated string.
- nStrRef: Reference of the string in the talk table
- nTalkVolume: TALKVOLUME_*

**Parameters:**

- `nStrRef`: `int`
- `nTalkVolume`: `int` (default: `0`)

<a id="actionusefeat"></a>

#### `ActionUseFeat(nFeat, oTarget)` - Routine 287

Use nFeat on oTarget.
- nFeat: FEAT_*
- oTarget

**Parameters:**

- `nFeat`: `int`
- `oTarget`: `object`

<a id="actionuseskill"></a>

#### `ActionUseSkill(nSkill, oTarget, nSubSkill=0, oItemUsed=1)` - Routine 288

Runs the action "UseSkill" on the current creature
Use nSkill on oTarget.
- nSkill: SKILL_*
- oTarget
- nSubSkill: SUBSKILL_*
- oItemUsed: Item to use in conjunction with the skill

**Parameters:**

- `nSkill`: `int`
- `oTarget`: `object`
- `nSubSkill`: `int` (default: `0`)
- `oItemUsed`: `object` (default: `1`)

<a id="actiondocommand"></a>

#### `ActionDoCommand(aActionToDo)` - Routine 294

Do aActionToDo.

**Parameters:**

- `aActionToDo`: `action`

<a id="actionusetalentonobject"></a>

#### `ActionUseTalentOnObject(tChosenTalent, oTarget)` - Routine 309

Use tChosenTalent on oTarget.

**Parameters:**

- `tChosenTalent`: `talent`
- `oTarget`: `object`

<a id="actionusetalentatlocation"></a>

#### `ActionUseTalentAtLocation(tChosenTalent, lTargetLocation)` - Routine 310

Use tChosenTalent at lTargetLocation.

**Parameters:**

- `tChosenTalent`: `talent`
- `lTargetLocation`: `location`

<a id="actioninteractobject"></a>

#### `ActionInteractObject(oPlaceable)` - Routine 329

Use oPlaceable.

**Parameters:**

- `oPlaceable`: `object`

<a id="actionmoveawayfromlocation"></a>

#### `ActionMoveAwayFromLocation(lMoveAwayFrom, bRun=0, fMoveAwayRange=40.0)` - Routine 360

Causes the action subject to move away from lMoveAwayFrom.

**Parameters:**

- `lMoveAwayFrom`: `location`
- `bRun`: `int` (default: `0`)
- `fMoveAwayRange`: `float` (default: `40.0`)

<a id="actionsurrendertoenemies"></a>

#### `ActionSurrenderToEnemies()` - Routine 379

<a id="actionequipmostdamagingmelee"></a>

#### `ActionEquipMostDamagingMelee(oVersus=1, bOffHand=0)` - Routine 399

The creature will equip the melee weapon in its possession that can do the
most damage. If no valid melee weapon is found, it will equip the most
damaging range weapon. This function should only ever be called in the
EndOfCombatRound scripts, because otherwise it would have to stop the combat
round to run simulation.
- oVersus: You can try to get the most damaging weapon against oVersus
- bOffHand

**Parameters:**

- `oVersus`: `object` (default: `1`)
- `bOffHand`: `int` (default: `0`)

<a id="actionequipmostdamagingranged"></a>

#### `ActionEquipMostDamagingRanged(oVersus=1)` - Routine 400

The creature will equip the range weapon in its possession that can do the
most damage.
If no valid range weapon can be found, it will equip the most damaging melee
weapon.
- oVersus: You can try to get the most damaging weapon against oVersus

**Parameters:**

- `oVersus`: `object` (default: `1`)

<a id="actionequipmosteffectivearmor"></a>

#### `ActionEquipMostEffectiveArmor()` - Routine 404

The creature will equip the armour in its possession that has the highest
armour class.

<a id="actionunlockobject"></a>

#### `ActionUnlockObject(oTarget)` - Routine 483

The action subject will unlock oTarget, which can be a door or a placeable
object.

**Parameters:**

- `oTarget`: `object`

<a id="actionlockobject"></a>

#### `ActionLockObject(oTarget)` - Routine 484

The action subject will lock oTarget, which can be a door or a placeable
object.

**Parameters:**

- `oTarget`: `object`

<a id="actioncastfakespellatobject"></a>

#### `ActionCastFakeSpellAtObject(nSpell, oTarget, nProjectilePathType=0)` - Routine 501

The action subject will fake casting a spell at oTarget; the conjure and cast
animations and visuals will occur, nothing else.
- nSpell
- oTarget
- nProjectilePathType: PROJECTILE_PATH_TYPE_*

**Parameters:**

- `nSpell`: `int`
- `oTarget`: `object`
- `nProjectilePathType`: `int` (default: `0`)

<a id="actioncastfakespellatlocation"></a>

#### `ActionCastFakeSpellAtLocation(nSpell, lTarget, nProjectilePathType=0)` - Routine 502

The action subject will fake casting a spell at lLocation; the conjure and
cast animations and visuals will occur, nothing else.
- nSpell
- lTarget
- nProjectilePathType: PROJECTILE_PATH_TYPE_*

**Parameters:**

- `nSpell`: `int`
- `lTarget`: `location`
- `nProjectilePathType`: `int` (default: `0`)

<a id="getcurrentaction"></a>

#### `GetCurrentAction(oObject=0)` - Routine 522

Get the current action (ACTION_*) that oObject is executing.

**Parameters:**

- `oObject`: `object` (default: `0`)

**Returns:** `int`

<a id="actionbarkstring"></a>

#### `ActionBarkString(strRef)`

700. ActionBarkString
this will cause a creature to bark the strRef from the talk table.

**Parameters:**

- `strRef`: `int`

<a id="actionfollowleader"></a>

#### `ActionFollowLeader()`

730. ActionFollowLeader
this action has a party member follow the leader.
DO NOT USE ON A CREATURE THAT IS NOT IN THE PARTY!!


### Alignment System

<a id="getgoodevilvalue"></a>

#### `GetGoodEvilValue(oCreature)` - Routine 125

Get an integer between 0 and 100 (inclusive) to represent oCreature's
Good/Evil alignment
(100=good, 0=evil)
* Return value if oCreature is not a valid creature: -1

**Parameters:**

- `oCreature`: `object`

**Returns:** `int`

<a id="getalignmentgoodevil"></a>

#### `GetAlignmentGoodEvil(oCreature)` - Routine 127

Return an ALIGNMENT_* constant to represent oCreature's good/evil alignment
* Return value if oCreature is not a valid creature: -1

**Parameters:**

- `oCreature`: `object`

**Returns:** `int`

<a id="getfactionequal"></a>

#### `GetFactionEqual(oFirstObject, oSecondObject=0)` - Routine 172

* Returns TRUE if the Faction Ids of the two objects are the same

**Parameters:**

- `oFirstObject`: `object`
- `oSecondObject`: `object` (default: `0`)

**Returns:** `int`

<a id="getfactionaveragegoodevilalignment"></a>

#### `GetFactionAverageGoodEvilAlignment(oFactionMember)` - Routine 187

Get an integer between 0 and 100 (inclusive) that represents the average
good/evil alignment of oFactionMember's faction.
* Return value on error: -1

**Parameters:**

- `oFactionMember`: `object`

**Returns:** `int`

<a id="adjustalignment"></a>

#### `AdjustAlignment(oSubject, nAlignment, nShift)` - Routine 201

Adjust the alignment of oSubject.
- oSubject
- nAlignment:
-> ALIGNMENT_LIGHT_SIDE/ALIGNMENT_DARK_SIDE: oSubject's
alignment will be shifted in the direction specified
-> ALIGNMENT_NEUTRAL: nShift is applied to oSubject's dark side/light side
alignment value in the direction which is towards neutrality.
e.g. If oSubject has an alignment value of 80 (i.e. light side)
then if nShift is 15, the alignment value will become (80-15)=65
Furthermore, the shift will at most take the alignment value to 50 and
not beyond.
e.g. If oSubject has an alignment value of 40 then if nShift is 15,
the aligment value will become 50
- nShift: this is the desired shift in alignment
* No return value

**Parameters:**

- `oSubject`: `object`
- `nAlignment`: `int`
- `nShift`: `int`

<a id="getreputation"></a>

#### `GetReputation(oSource, oTarget)` - Routine 208

Get an integer between 0 and 100 (inclusive) that represents how oSource
feels about oTarget.
-> 0-10 means oSource is hostile to oTarget
-> 11-89 means oSource is neutral to oTarget
-> 90-100 means oSource is friendly to oTarget
* Returns -1 if oSource or oTarget does not identify a valid object

**Parameters:**

- `oSource`: `object`
- `oTarget`: `object`

**Returns:** `int`

<a id="getisenemy"></a>

#### `GetIsEnemy(oTarget, oSource=0)` - Routine 235

* Returns TRUE if oSource considers oTarget as an enemy.

**Parameters:**

- `oTarget`: `object`
- `oSource`: `object` (default: `0`)

**Returns:** `int`

<a id="getisfriend"></a>

#### `GetIsFriend(oTarget, oSource=0)` - Routine 236

* Returns TRUE if oSource considers oTarget as a friend.

**Parameters:**

- `oTarget`: `object`
- `oSource`: `object` (default: `0`)

**Returns:** `int`

<a id="getisneutral"></a>

#### `GetIsNeutral(oTarget, oSource=0)` - Routine 237

* Returns TRUE if oSource considers oTarget as neutral.

**Parameters:**

- `oTarget`: `object`
- `oSource`: `object` (default: `0`)

**Returns:** `int`

<a id="versusalignmenteffect"></a>

#### `VersusAlignmentEffect(eEffect, nLawChaos=0, nGoodEvil=0)` - Routine 355

Set eEffect to be versus a specific alignment.
- eEffect
- nLawChaos: ALIGNMENT_LAWFUL/ALIGNMENT_CHAOTIC/ALIGNMENT_ALL
- nGoodEvil: ALIGNMENT_GOOD/ALIGNMENT_EVIL/ALIGNMENT_ALL

**Parameters:**

- `eEffect`: `effect`
- `nLawChaos`: `int` (default: `0`)
- `nGoodEvil`: `int` (default: `0`)

**Returns:** `effect`

<a id="setgoodevilvalue"></a>

#### `SetGoodEvilValue(oCreature, nAlignment)` - Routine 750

SetAlignmentGoodEvil
Set oCreature's alignment value

**Parameters:**

- `oCreature`: `object`
- `nAlignment`: `int`


### Class System

<a id="gethasspelleffect"></a>

#### `GetHasSpellEffect(nSpell, oObject=0)` - Routine 304

Determine if oObject has effects originating from nSpell.
- nSpell: SPELL_*
- oObject

**Parameters:**

- `nSpell`: `int`
- `oObject`: `object` (default: `0`)

**Returns:** `int`

<a id="getclassbyposition"></a>

#### `GetClassByPosition(nClassPosition, oCreature=0)` - Routine 341

A creature can have up to three classes.  This function determines the
creature's class (CLASS_TYPE_*) based on nClassPosition.
- nClassPosition: 1, 2 or 3
- oCreature
* Returns CLASS_TYPE_INVALID if the oCreature does not have a class in
nClassPosition (i.e. a single-class creature will only have a value in
nClassLocation=1) or if oCreature is not a valid creature.

**Parameters:**

- `nClassPosition`: `int`
- `oCreature`: `object` (default: `0`)

**Returns:** `int`

<a id="getlevelbyposition"></a>

#### `GetLevelByPosition(nClassPosition, oCreature=0)` - Routine 342

A creature can have up to three classes.  This function determines the
creature's class level based on nClass Position.
- nClassPosition: 1, 2 or 3
- oCreature
* Returns 0 if oCreature does not have a class in nClassPosition
(i.e. a single-class creature will only have a value in nClassLocation=1)
or if oCreature is not a valid creature.

**Parameters:**

- `nClassPosition`: `int`
- `oCreature`: `object` (default: `0`)

**Returns:** `int`

<a id="getlevelbyclass"></a>

#### `GetLevelByClass(nClassType, oCreature=0)` - Routine 343

Determine the levels that oCreature holds in nClassType.
- nClassType: CLASS_TYPE_*
- oCreature

**Parameters:**

- `nClassType`: `int`
- `oCreature`: `object` (default: `0`)

**Returns:** `int`

<a id="gethasspell"></a>

#### `GetHasSpell(nSpell, oCreature=0)` - Routine 377

Determine whether oCreature has nSpell memorised.
- nSpell: SPELL_*
- oCreature

**Parameters:**

- `nSpell`: `int`
- `oCreature`: `object` (default: `0`)

**Returns:** `int`

<a id="getspellcastitem"></a>

#### `GetSpellCastItem()` - Routine 438

Use this in a spell script to get the item used to cast the spell.

**Returns:** `object`


### Combat Functions

<a id="getlastattacker"></a>

#### `GetLastAttacker(oAttackee=0)` - Routine 36

Get the last attacker of oAttackee.  This should only be used ONLY in the
OnAttacked events for creatures, placeables and doors.
* Return value on error: OBJECT_INVALID

**Parameters:**

- `oAttackee`: `object` (default: `0`)

**Returns:** `object`

<a id="actionattack"></a>

#### `ActionAttack(oAttackee, bPassive=0)` - Routine 37

Attack oAttackee.
- bPassive: If this is TRUE, attack is in passive mode.

**Parameters:**

- `oAttackee`: `object`
- `bPassive`: `int` (default: `0`)

<a id="getspelltargetobject"></a>

#### `GetSpellTargetObject()` - Routine 47

Get the object at which the caller last cast a spell
* Return value on error: OBJECT_INVALID

**Returns:** `object`

<a id="actioncastspellatobject"></a>

#### `ActionCastSpellAtObject(nSpell, oTarget, nMetaMagic=0, bCheat=0, nDomainLevel=0, nProjectilePathType=0, bInstantSpell=0)` - Routine 48

This action casts a spell at oTarget.
- nSpell: SPELL_*
- oTarget: Target for the spell
- nMetamagic: METAMAGIC_*
- bCheat: If this is TRUE, then the executor of the action doesn't have to be
able to cast the spell.
- nDomainLevel: TBD - SS
- nProjectilePathType: PROJECTILE_PATH_TYPE_*
- bInstantSpell: If this is TRUE, the spell is cast immediately. This allows
the end-user to simulate a high-level magic-user having lots of advance
warning of impending trouble

**Parameters:**

- `nSpell`: `int`
- `oTarget`: `object`
- `nMetaMagic`: `int` (default: `0`)
- `bCheat`: `int` (default: `0`)
- `nDomainLevel`: `int` (default: `0`)
- `nProjectilePathType`: `int` (default: `0`)
- `bInstantSpell`: `int` (default: `0`)

<a id="getspelltargetlocation"></a>

#### `GetSpellTargetLocation()` - Routine 222

Get the location of the caller's last spell target.

**Returns:** `location`

<a id="actioncastspellatlocation"></a>

#### `ActionCastSpellAtLocation(nSpell, lTargetLocation, nMetaMagic=0, bCheat=0, nProjectilePathType=0, bInstantSpell=0)` - Routine 234

Cast spell nSpell at lTargetLocation.
- nSpell: SPELL_*
- lTargetLocation
- nMetaMagic: METAMAGIC_*
- bCheat: If this is TRUE, then the executor of the action doesn't have to be
able to cast the spell.
- nProjectilePathType: PROJECTILE_PATH_TYPE_*
- bInstantSpell: If this is TRUE, the spell is cast immediately; this allows
the end-user to simulate
a high-level magic user having lots of advance warning of impending trouble.

**Parameters:**

- `nSpell`: `int`
- `lTargetLocation`: `location`
- `nMetaMagic`: `int` (default: `0`)
- `bCheat`: `int` (default: `0`)
- `nProjectilePathType`: `int` (default: `0`)
- `bInstantSpell`: `int` (default: `0`)

<a id="getspellid"></a>

#### `GetSpellId()` - Routine 248

This is for use in a Spell script, it gets the ID of the spell that is being
cast (SPELL_*).

**Returns:** `int`

<a id="getattacktarget"></a>

#### `GetAttackTarget(oCreature=0)` - Routine 316

Get the attack target of oCreature.
This only works when oCreature is in combat.

**Parameters:**

- `oCreature`: `object` (default: `0`)

**Returns:** `object`

<a id="getisincombat"></a>

#### `GetIsInCombat(oCreature=0)` - Routine 320

* Returns TRUE if oCreature is in combat.

**Parameters:**

- `oCreature`: `object` (default: `0`)

**Returns:** `int`

<a id="setisdestroyable"></a>

#### `SetIsDestroyable(bDestroyable, bRaiseable=1, bSelectableWhenDead=0)` - Routine 323

Set the destroyable status of the caller.
- bDestroyable: If this is FALSE, the caller does not fade out on death, but
sticks around as a corpse.
- bRaiseable: If this is TRUE, the caller can be raised via resurrection.
- bSelectableWhenDead: If this is TRUE, the caller is selectable after death.

**Parameters:**

- `bDestroyable`: `int`
- `bRaiseable`: `int` (default: `1`)
- `bSelectableWhenDead`: `int` (default: `0`)

<a id="getdamagedealtbytype"></a>

#### `GetDamageDealtByType(nDamageType)` - Routine 344

Get the amount of damage of type nDamageType that has been dealt to the caller.
- nDamageType: DAMAGE_TYPE_*

**Parameters:**

- `nDamageType`: `int`

**Returns:** `int`

<a id="gettotaldamagedealt"></a>

#### `GetTotalDamageDealt()` - Routine 345

Get the total amount of damage that has been dealt to the caller.

**Returns:** `int`

<a id="getlastdamager"></a>

#### `GetLastDamager()` - Routine 346

Get the last object that damaged the caller.
* Returns OBJECT_INVALID if the caller is not a valid object.

**Returns:** `object`

<a id="actionforcemovetolocation"></a>

#### `ActionForceMoveToLocation(lDestination, bRun=0, fTimeout=30.0)` - Routine 382

Force the action subject to move to lDestination.

**Parameters:**

- `lDestination`: `location`
- `bRun`: `int` (default: `0`)
- `fTimeout`: `float` (default: `30.0`)

<a id="actionforcemovetoobject"></a>

#### `ActionForceMoveToObject(oMoveTo, bRun=0, fRange=1.0, fTimeout=30.0)` - Routine 383

Force the action subject to move to oMoveTo.

**Parameters:**

- `oMoveTo`: `object`
- `bRun`: `int` (default: `0`)
- `fRange`: `float` (default: `1.0`)
- `fTimeout`: `float` (default: `30.0`)

<a id="getisweaponeffective"></a>

#### `GetIsWeaponEffective(oVersus=1, bOffHand=0)` - Routine 422

* Returns TRUE if the weapon equipped is capable of damaging oVersus.

**Parameters:**

- `oVersus`: `object` (default: `1`)
- `bOffHand`: `int` (default: `0`)

**Returns:** `int`

<a id="getlastkiller"></a>

#### `GetLastKiller()` - Routine 437

Get the object that killed the caller.

**Returns:** `object`

<a id="getweaponranged"></a>

#### `GetWeaponRanged(oItem)` - Routine 511

* Returns TRUE if oItem is a ranged weapon.

**Parameters:**

- `oItem`: `object`

**Returns:** `int`

<a id="getlasthostileactor"></a>

#### `GetLastHostileActor(oVictim=0)` - Routine 556

Get the last object that was sent as a GetLastAttacker(), GetLastDamager(),
GetLastSpellCaster() (for a hostile spell), or GetLastDisturbed() (when a
creature is pickpocketed).
Note: Return values may only ever be:
1) A Creature
2) Plot Characters will never have this value set
3) Area of Effect Objects will return the AOE creator if they are registered
as this value, otherwise they will return INVALID_OBJECT_ID
4) Traps will not return the creature that set the trap.
5) This value will never be overwritten by another non-creature object.
6) This value will never be a dead/destroyed creature

**Parameters:**

- `oVictim`: `object` (default: `0`)

**Returns:** `object`


### Dialog and Conversation Functions

<a id="actionpauseconversation"></a>

#### `ActionPauseConversation()` - Routine 205

Pause the current conversation.

<a id="actionresumeconversation"></a>

#### `ActionResumeConversation()` - Routine 206

Resume a conversation after it has been paused.

<a id="speakstring"></a>

#### `SpeakString(sStringToSpeak, nTalkVolume=0)` - Routine 221

The caller will immediately speak sStringToSpeak (this is different from
ActionSpeakString)
- sStringToSpeak
- nTalkVolume: TALKVOLUME_*

**Parameters:**

- `sStringToSpeak`: `string`
- `nTalkVolume`: `int` (default: `0`)

<a id="beginconversation"></a>

#### `BeginConversation(sResRef=, oObjectToDialog=1)` - Routine 255

Use this in an OnDialog script to start up the dialog tree.
- sResRef: if this is not specified, the default dialog file will be used
- oObjectToDialog: if this is not specified the person that triggered the
event will be used

**Parameters:**

- `sResRef`: `string` (default: ``)
- `oObjectToDialog`: `object` (default: `1`)

**Returns:** `int`

<a id="setcustomtoken"></a>

#### `SetCustomToken(nCustomTokenNumber, sTokenValue)` - Routine 284

Set the value for a custom token.

**Parameters:**

- `nCustomTokenNumber`: `int`
- `sTokenValue`: `string`

<a id="eventconversation"></a>

#### `EventConversation()` - Routine 295

Conversation event.

**Returns:** `event`

<a id="speakonelinerconversation"></a>

#### `SpeakOneLinerConversation(sDialogResRef=, oTokenTarget=32767)` - Routine 417

Immediately speak a conversation one-liner.
- sDialogResRef
- oTokenTarget: This must be specified if there are creature-specific tokens
in the string.

**Parameters:**

- `sDialogResRef`: `string` (default: ``)
- `oTokenTarget`: `object` (default: `32767`)

<a id="getisinconversation"></a>

#### `GetIsInConversation(oObject)` - Routine 445

Determine whether oObject is in conversation.

**Parameters:**

- `oObject`: `object`

**Returns:** `int`

<a id="getlastconversation"></a>

#### `GetLastConversation()` - Routine 711

GetLastConversation
Gets the last conversation string.

**Returns:** `string`

<a id="actionstartconversation"></a>

#### `ActionStartConversation(oObjectToConverse, sDialogResRef=, bPrivateConversation=0, nConversationType=0, bIgnoreStartRange=0, sNameObjectToIgnore1=, sNameObjectToIgnore2=, sNameObjectToIgnore3=, sNameObjectToIgnore4=, sNameObjectToIgnore5=, sNameObjectToIgnore6=, bUseLeader=0)`

AMF: APRIL 28, 2003 - I HAVE CHANGED THIS FUNCTION AS PER DAN'S REQUEST
Starts a conversation with oObjectToConverseWith - this will cause their
OnDialog event to fire.
- oObjectToConverseWith
- sDialogResRef: If this is blank, the creature's own dialogue file will be used
- bPrivateConversation: If this is blank, the default is FALSE.
- nConversationType - If this is blank the default will be Cinematic, ie. a normal conversation type
other choices inclue: CONVERSATION_TYPE_COMPUTER
UPDATE:  nConversationType actually has no meaning anymore.  This has been replaced by a flag in the dialog editor.  However
for backwards compatability it has been left here.  So when using this command place CONVERSATION_TYPE_CINEMATIC in here. - DJF
- bIgnoreStartRange - If this is blank the default will be FALSE, ie. Start conversation ranges are in effect
Setting this to TRUE will cause creatures to start a conversation without requiring to close
the distance between the two object in dialog.
- sNameObjectToIgnore1-6 - Normally objects in the animation list of the dialog editor have to be available for animations on that node to work
these 6 strings are to indicate 6 objects that dont need to be available for things to proceed.  The string should be EXACTLY
the same as the string that it represents in the dialog editor.

**Parameters:**

- `oObjectToConverse`: `object`
- `sDialogResRef`: `string` (default: ``)
- `bPrivateConversation`: `int` (default: `0`)
- `nConversationType`: `int` (default: `0`)
- `bIgnoreStartRange`: `int` (default: `0`)
- `sNameObjectToIgnore1`: `string` (default: ``)
- `sNameObjectToIgnore2`: `string` (default: ``)
- `sNameObjectToIgnore3`: `string` (default: ``)
- `sNameObjectToIgnore4`: `string` (default: ``)
- `sNameObjectToIgnore5`: `string` (default: ``)
- `sNameObjectToIgnore6`: `string` (default: ``)
- `bUseLeader`: `int` (default: `0`)

<a id="getisconversationactive"></a>

#### `GetIsConversationActive()`

701. GetIsConversationActive
Checks to see if any conversations are currently taking place

**Returns:** `int`


### Effects System

<a id="effectassuredhit"></a>

#### `EffectAssuredHit()` - Routine 51

EffectAssuredHit
Create an Assured Hit effect, which guarantees that all attacks are successful

**Returns:** `effect`

<a id="effectheal"></a>

#### `EffectHeal(nDamageToHeal)` - Routine 78

Create a Heal effect. This should be applied as an instantaneous effect.
* Returns an effect of type EFFECT_TYPE_INVALIDEFFECT if nDamageToHeal < 0.

**Parameters:**

- `nDamageToHeal`: `int`

**Returns:** `effect`

<a id="effectdamage"></a>

#### `EffectDamage(nDamageAmount, nDamageType=8, nDamagePower=0)` - Routine 79

Create a Damage effect
- nDamageAmount: amount of damage to be dealt. This should be applied as an
instantaneous effect.
- nDamageType: DAMAGE_TYPE_*
- nDamagePower: DAMAGE_POWER_*

**Parameters:**

- `nDamageAmount`: `int`
- `nDamageType`: `int` (default: `8`)
- `nDamagePower`: `int` (default: `0`)

**Returns:** `effect`

<a id="effectabilityincrease"></a>

#### `EffectAbilityIncrease(nAbilityToIncrease, nModifyBy)` - Routine 80

Create an Ability Increase effect
- bAbilityToIncrease: ABILITY_*

**Parameters:**

- `nAbilityToIncrease`: `int`
- `nModifyBy`: `int`

**Returns:** `effect`

<a id="effectdamageresistance"></a>

#### `EffectDamageResistance(nDamageType, nAmount, nLimit=0)` - Routine 81

Create a Damage Resistance effect that removes the first nAmount points of
damage of type nDamageType, up to nLimit (or infinite if nLimit is 0)
- nDamageType: DAMAGE_TYPE_*
- nAmount
- nLimit

**Parameters:**

- `nDamageType`: `int`
- `nAmount`: `int`
- `nLimit`: `int` (default: `0`)

**Returns:** `effect`

<a id="effectresurrection"></a>

#### `EffectResurrection()` - Routine 82

Create a Resurrection effect. This should be applied as an instantaneous effect.

**Returns:** `effect`

<a id="effectacincrease"></a>

#### `EffectACIncrease(nValue, nModifyType=0, nDamageType=8199)` - Routine 115

Create an AC Increase effect
- nValue: size of AC increase
- nModifyType: AC_*_BONUS
- nDamageType: DAMAGE_TYPE_*
* Default value for nDamageType should only ever be used in this function prototype.

**Parameters:**

- `nValue`: `int`
- `nModifyType`: `int` (default: `0`)
- `nDamageType`: `int` (default: `8199`)

**Returns:** `effect`

<a id="effectsavingthrowincrease"></a>

#### `EffectSavingThrowIncrease(nSave, nValue, nSaveType=0)` - Routine 117

Create an AC Decrease effect
- nSave: SAVING_THROW_* (not SAVING_THROW_TYPE_*)
- nValue: size of AC decrease
- nSaveType: SAVING_THROW_TYPE_*

**Parameters:**

- `nSave`: `int`
- `nValue`: `int`
- `nSaveType`: `int` (default: `0`)

**Returns:** `effect`

<a id="effectattackincrease"></a>

#### `EffectAttackIncrease(nBonus, nModifierType=0)` - Routine 118

Create an Attack Increase effect
- nBonus: size of attack bonus
- nModifierType: ATTACK_BONUS_*

**Parameters:**

- `nBonus`: `int`
- `nModifierType`: `int` (default: `0`)

**Returns:** `effect`

<a id="effectdamagereduction"></a>

#### `EffectDamageReduction(nAmount, nDamagePower, nLimit=0)` - Routine 119

Create a Damage Reduction effect
- nAmount: amount of damage reduction
- nDamagePower: DAMAGE_POWER_*
- nLimit: How much damage the effect can absorb before disappearing.
Set to zero for infinite

**Parameters:**

- `nAmount`: `int`
- `nDamagePower`: `int`
- `nLimit`: `int` (default: `0`)

**Returns:** `effect`

<a id="effectdamageincrease"></a>

#### `EffectDamageIncrease(nBonus, nDamageType=8)` - Routine 120

Create a Damage Increase effect
- nBonus: DAMAGE_BONUS_*
- nDamageType: DAMAGE_TYPE_*

**Parameters:**

- `nBonus`: `int`
- `nDamageType`: `int` (default: `8`)

**Returns:** `effect`

<a id="effectentangle"></a>

#### `EffectEntangle()` - Routine 130

Create an Entangle effect
When applied, this effect will restrict the creature's movement and apply a
(-2) to all attacks and a -4 to AC.

**Returns:** `effect`

<a id="effectdeath"></a>

#### `EffectDeath(nSpectacularDeath=0, nDisplayFeedback=1)` - Routine 133

Create a Death effect
- nSpectacularDeath: if this is TRUE, the creature to which this effect is
applied will die in an extraordinary fashion
- nDisplayFeedback

**Parameters:**

- `nSpectacularDeath`: `int` (default: `0`)
- `nDisplayFeedback`: `int` (default: `1`)

**Returns:** `effect`

<a id="effectknockdown"></a>

#### `EffectKnockdown()` - Routine 134

Create a Knockdown effect
This effect knocks creatures off their feet, they will sit until the effect
is removed. This should be applied as a temporary effect with a 3 second
duration minimum (1 second to fall, 1 second sitting, 1 second to get up).

**Returns:** `effect`

<a id="effectparalyze"></a>

#### `EffectParalyze()` - Routine 148

Create a Paralyze effect

**Returns:** `effect`

<a id="effectspellimmunity"></a>

#### `EffectSpellImmunity(nImmunityToSpell=-1)` - Routine 149

Create a Spell Immunity effect.
There is a known bug with this function. There *must* be a parameter specified
when this is called (even if the desired parameter is SPELL_ALL_SPELLS),
otherwise an effect of type EFFECT_TYPE_INVALIDEFFECT will be returned.
- nImmunityToSpell: SPELL_*
* Returns an effect of type EFFECT_TYPE_INVALIDEFFECT if nImmunityToSpell is
invalid.

**Parameters:**

- `nImmunityToSpell`: `int` (default: `-1`)

**Returns:** `effect`

<a id="effectforcejump"></a>

#### `EffectForceJump(oTarget, nAdvanced=0)` - Routine 153

EffectForceJump
The effect required for force jumping

**Parameters:**

- `oTarget`: `object`
- `nAdvanced`: `int` (default: `0`)

**Returns:** `effect`

<a id="effectsleep"></a>

#### `EffectSleep()` - Routine 154

Create a Sleep effect

**Returns:** `effect`

<a id="effecttemporaryforcepoints"></a>

#### `EffectTemporaryForcePoints(nTempForce)` - Routine 156

**Parameters:**

- `nTempForce`: `int`

**Returns:** `effect`

<a id="effectconfused"></a>

#### `EffectConfused()` - Routine 157

Create a Confuse effect

**Returns:** `effect`

<a id="effectfrightened"></a>

#### `EffectFrightened()` - Routine 158

Create a Frighten effect

**Returns:** `effect`

<a id="effectchoke"></a>

#### `EffectChoke()` - Routine 159

Choke the bugger...

**Returns:** `effect`

<a id="effectstunned"></a>

#### `EffectStunned()` - Routine 161

Create a Stun effect

**Returns:** `effect`

<a id="effectregenerate"></a>

#### `EffectRegenerate(nAmount, fIntervalSeconds)` - Routine 164

Create a Regenerate effect.
- nAmount: amount of damage to be regenerated per time interval
- fIntervalSeconds: length of interval in seconds

**Parameters:**

- `nAmount`: `int`
- `fIntervalSeconds`: `float`

**Returns:** `effect`

<a id="effectmovementspeedincrease"></a>

#### `EffectMovementSpeedIncrease(nNewSpeedPercent)` - Routine 165

Create a Movement Speed Increase effect.
- nNewSpeedPercent: This works in a dodgy way so please read this notes carefully.
If you supply an integer under 100, 100 gets added to it to produce the final speed.
e.g. if you supply 50, then the resulting speed is 150% of the original speed.
If you supply 100 or above, then this is used directly as the resulting speed.
e.g. if you specify 100, then the resulting speed is 100% of the original speed that is,
it is unchanged.
However if you specify 200, then the resulting speed is double the original speed.

**Parameters:**

- `nNewSpeedPercent`: `int`

**Returns:** `effect`

<a id="effectareaofeffect"></a>

#### `EffectAreaOfEffect(nAreaEffectId, sOnEnterScript=, sHeartbeatScript=, sOnExitScript=)` - Routine 171

Create an Area Of Effect effect in the area of the creature it is applied to.
If the scripts are not specified, default ones will be used.

**Parameters:**

- `nAreaEffectId`: `int`
- `sOnEnterScript`: `string` (default: ``)
- `sHeartbeatScript`: `string` (default: ``)
- `sOnExitScript`: `string` (default: ``)

**Returns:** `effect`

<a id="effectvisualeffect"></a>

#### `EffectVisualEffect(nVisualEffectId, nMissEffect=0)` - Routine 180

* Create a Visual Effect that can be applied to an object.
- nVisualEffectId
- nMissEffect: if this is TRUE, a random vector near or past the target will
be generated, on which to play the effect

**Parameters:**

- `nVisualEffectId`: `int`
- `nMissEffect`: `int` (default: `0`)

**Returns:** `effect`

<a id="effectlinkeffects"></a>

#### `EffectLinkEffects(eChildEffect, eParentEffect)` - Routine 199

Link the two supplied effects, returning eChildEffect as a child of
eParentEffect.
Note: When applying linked effects if the target is immune to all valid
effects all other effects will be removed as well. This means that if you
apply a visual effect and a silence effect (in a link) and the target is
immune to the silence effect that the visual effect will get removed as well.
Visual Effects are not considered "valid" effects for the purposes of
determining if an effect will be removed or not and as such should never be
packaged *only* with other visual effects in a link.

**Parameters:**

- `eChildEffect`: `effect`
- `eParentEffect`: `effect`

**Returns:** `effect`

<a id="effectbeam"></a>

#### `EffectBeam(nBeamVisualEffect, oEffector, nBodyPart, bMissEffect=0)` - Routine 207

Create a Beam effect.
- nBeamVisualEffect: VFX_BEAM_*
- oEffector: the beam is emitted from this creature
- nBodyPart: BODY_NODE_*
- bMissEffect: If this is TRUE, the beam will fire to a random vector near or
past the target
* Returns an effect of type EFFECT_TYPE_INVALIDEFFECT if nBeamVisualEffect is
not valid.

**Parameters:**

- `nBeamVisualEffect`: `int`
- `oEffector`: `object`
- `nBodyPart`: `int`
- `bMissEffect`: `int` (default: `0`)

**Returns:** `effect`

<a id="effectforceresistanceincrease"></a>

#### `EffectForceResistanceIncrease(nValue)` - Routine 212

Create a Force Resistance Increase effect.
- nValue: size of Force Resistance increase

**Parameters:**

- `nValue`: `int`

**Returns:** `effect`

<a id="effectbodyfuel"></a>

#### `EffectBodyFuel()` - Routine 224

the effect of body fule.. convers HP -> FP i think

**Returns:** `effect`

<a id="effectpoison"></a>

#### `EffectPoison(nPoisonType)` - Routine 250

Create a Poison effect.
- nPoisonType: POISON_*

**Parameters:**

- `nPoisonType`: `int`

**Returns:** `effect`

<a id="effectassureddeflection"></a>

#### `EffectAssuredDeflection(nReturn=0)` - Routine 252

Assured Deflection
This effect ensures that all projectiles shot at a jedi will be deflected
without doing an opposed roll.  It takes an optional parameter to say whether
the deflected projectile will return to the attacker and cause damage

**Parameters:**

- `nReturn`: `int` (default: `0`)

**Returns:** `effect`

<a id="effectforcepushtargeted"></a>

#### `EffectForcePushTargeted(lCentre, nIgnoreTestDirectLine=0)` - Routine 269

EffectForcePushTargeted
This effect is exactly the same as force push, except it takes a location parameter that specifies
where the location of the force push is to be done from.  All orientations are also based on this location.
AMF:  The new ignore test direct line variable should be used with extreme caution
It overrides geometry checks for force pushes, so that the object that the effect is applied to
is guaranteed to move that far, ignoring collisions.  It is best used for cutscenes.

**Parameters:**

- `lCentre`: `location`
- `nIgnoreTestDirectLine`: `int` (default: `0`)

**Returns:** `effect`

<a id="effecthaste"></a>

#### `EffectHaste()` - Routine 270

Create a Haste effect.

**Returns:** `effect`

<a id="effectimmunity"></a>

#### `EffectImmunity(nImmunityType)` - Routine 273

Create an Immunity effect.
- nImmunityType: IMMUNITY_TYPE_*

**Parameters:**

- `nImmunityType`: `int`

**Returns:** `effect`

<a id="effectdamageimmunityincrease"></a>

#### `EffectDamageImmunityIncrease(nDamageType, nPercentImmunity)` - Routine 275

Creates a Damage Immunity Increase effect.
- nDamageType: DAMAGE_TYPE_*
- nPercentImmunity

**Parameters:**

- `nDamageType`: `int`
- `nPercentImmunity`: `int`

**Returns:** `effect`

<a id="effecttemporaryhitpoints"></a>

#### `EffectTemporaryHitpoints(nHitPoints)` - Routine 314

Create a Temporary Hitpoints effect.
- nHitPoints: a positive integer
* Returns an effect of type EFFECT_TYPE_INVALIDEFFECT if nHitPoints < 0.

**Parameters:**

- `nHitPoints`: `int`

**Returns:** `effect`

<a id="effectskillincrease"></a>

#### `EffectSkillIncrease(nSkill, nValue)` - Routine 351

Create a Skill Increase effect.
- nSkill: SKILL_*
- nValue
* Returns an effect of type EFFECT_TYPE_INVALIDEFFECT if nSkill is invalid.

**Parameters:**

- `nSkill`: `int`
- `nValue`: `int`

**Returns:** `effect`

<a id="effectdamageforcepoints"></a>

#### `EffectDamageForcePoints(nDamage)` - Routine 372

Damages the creatures force points

**Parameters:**

- `nDamage`: `int`

**Returns:** `effect`

<a id="effecthealforcepoints"></a>

#### `EffectHealForcePoints(nHeal)` - Routine 373

Heals the creatures force points

**Parameters:**

- `nHeal`: `int`

**Returns:** `effect`

<a id="effecthitpointchangewhendying"></a>

#### `EffectHitPointChangeWhenDying(fHitPointChangePerRound)` - Routine 387

Create a Hit Point Change When Dying effect.
- fHitPointChangePerRound: this can be positive or negative, but not zero.
* Returns an effect of type EFFECT_TYPE_INVALIDEFFECT if fHitPointChangePerRound is 0.

**Parameters:**

- `fHitPointChangePerRound`: `float`

**Returns:** `effect`

<a id="effectdroidstun"></a>

#### `EffectDroidStun()` - Routine 391

Stunn the droid

**Returns:** `effect`

<a id="effectforcepushed"></a>

#### `EffectForcePushed()` - Routine 392

Force push the creature...

**Returns:** `effect`

<a id="effectforceresisted"></a>

#### `EffectForceResisted(oSource)` - Routine 402

Effect that will play an animation and display a visual effect to indicate the
target has resisted a force power.

**Parameters:**

- `oSource`: `object`

**Returns:** `effect`

<a id="effectforcefizzle"></a>

#### `EffectForceFizzle()` - Routine 420

Effect that will display a visual effect on the specified object's hand to
indicate a force power has fizzled out.

**Returns:** `effect`

<a id="effectabilitydecrease"></a>

#### `EffectAbilityDecrease(nAbility, nModifyBy)` - Routine 446

Create an Ability Decrease effect.
- nAbility: ABILITY_*
- nModifyBy: This is the amount by which to decrement the ability

**Parameters:**

- `nAbility`: `int`
- `nModifyBy`: `int`

**Returns:** `effect`

<a id="effectattackdecrease"></a>

#### `EffectAttackDecrease(nPenalty, nModifierType=0)` - Routine 447

Create an Attack Decrease effect.
- nPenalty
- nModifierType: ATTACK_BONUS_*

**Parameters:**

- `nPenalty`: `int`
- `nModifierType`: `int` (default: `0`)

**Returns:** `effect`

<a id="effectdamagedecrease"></a>

#### `EffectDamageDecrease(nPenalty, nDamageType=8)` - Routine 448

Create a Damage Decrease effect.
- nPenalty
- nDamageType: DAMAGE_TYPE_*

**Parameters:**

- `nPenalty`: `int`
- `nDamageType`: `int` (default: `8`)

**Returns:** `effect`

<a id="effectdamageimmunitydecrease"></a>

#### `EffectDamageImmunityDecrease(nDamageType, nPercentImmunity)` - Routine 449

Create a Damage Immunity Decrease effect.
- nDamageType: DAMAGE_TYPE_*
- nPercentImmunity

**Parameters:**

- `nDamageType`: `int`
- `nPercentImmunity`: `int`

**Returns:** `effect`

<a id="effectacdecrease"></a>

#### `EffectACDecrease(nValue, nModifyType=0, nDamageType=8199)` - Routine 450

Create an AC Decrease effect.
- nValue
- nModifyType: AC_*
- nDamageType: DAMAGE_TYPE_*
* Default value for nDamageType should only ever be used in this function prototype.

**Parameters:**

- `nValue`: `int`
- `nModifyType`: `int` (default: `0`)
- `nDamageType`: `int` (default: `8199`)

**Returns:** `effect`

<a id="effectmovementspeeddecrease"></a>

#### `EffectMovementSpeedDecrease(nPercentChange)` - Routine 451

Create a Movement Speed Decrease effect.
- nPercentChange: This is expected to be a positive integer between 1 and 99 inclusive.
If a negative integer is supplied then a movement speed increase will result,
and if a number >= 100 is supplied then the effect is deleted.

**Parameters:**

- `nPercentChange`: `int`

**Returns:** `effect`

<a id="effectsavingthrowdecrease"></a>

#### `EffectSavingThrowDecrease(nSave, nValue, nSaveType=0)` - Routine 452

Create a Saving Throw Decrease effect.
- nSave
- nValue
- nSaveType: SAVING_THROW_TYPE_*

**Parameters:**

- `nSave`: `int`
- `nValue`: `int`
- `nSaveType`: `int` (default: `0`)

**Returns:** `effect`

<a id="effectskilldecrease"></a>

#### `EffectSkillDecrease(nSkill, nValue)` - Routine 453

Create a Skill Decrease effect.
* Returns an effect of type EFFECT_TYPE_INVALIDEFFECT if nSkill is invalid.

**Parameters:**

- `nSkill`: `int`
- `nValue`: `int`

**Returns:** `effect`

<a id="effectforceresistancedecrease"></a>

#### `EffectForceResistanceDecrease(nValue)` - Routine 454

Create a Force Resistance Decrease effect.

**Parameters:**

- `nValue`: `int`

**Returns:** `effect`

<a id="effectinvisibility"></a>

#### `EffectInvisibility(nInvisibilityType)` - Routine 457

Create an Invisibility effect.
- nInvisibilityType: INVISIBILITY_TYPE_*
* Returns an effect of type EFFECT_TYPE_INVALIDEFFECT if nInvisibilityType
is invalid.

**Parameters:**

- `nInvisibilityType`: `int`

**Returns:** `effect`

<a id="effectconcealment"></a>

#### `EffectConcealment(nPercentage)` - Routine 458

Create a Concealment effect.
- nPercentage: 1-100 inclusive
* Returns an effect of type EFFECT_TYPE_INVALIDEFFECT if nPercentage < 1 or
nPercentage > 100.

**Parameters:**

- `nPercentage`: `int`

**Returns:** `effect`

<a id="effectforceshield"></a>

#### `EffectForceShield(nShield)` - Routine 459

Create a Force Shield that has parameters from the guven index into the forceshields.2da

**Parameters:**

- `nShield`: `int`

**Returns:** `effect`

<a id="effectdispelmagicall"></a>

#### `EffectDispelMagicAll(nCasterLevel)` - Routine 460

Create a Dispel Magic All effect.

**Parameters:**

- `nCasterLevel`: `int`

**Returns:** `effect`

<a id="effectdisguise"></a>

#### `EffectDisguise(nDisguiseAppearance)` - Routine 463

Create a Disguise effect.
- * nDisguiseAppearance: DISGUISE_TYPE_*s

**Parameters:**

- `nDisguiseAppearance`: `int`

**Returns:** `effect`

<a id="effecttrueseeing"></a>

#### `EffectTrueSeeing()` - Routine 465

Create a True Seeing effect.

**Returns:** `effect`

<a id="effectseeinvisible"></a>

#### `EffectSeeInvisible()` - Routine 466

Create a See Invisible effect.

**Returns:** `effect`

<a id="effecttimestop"></a>

#### `EffectTimeStop()` - Routine 467

Create a Time Stop effect.

**Returns:** `effect`

<a id="effectblasterdeflectionincrease"></a>

#### `EffectBlasterDeflectionIncrease(nChange)` - Routine 469

Increase the blaster deflection rate, i think...

**Parameters:**

- `nChange`: `int`

**Returns:** `effect`

<a id="effectblasterdeflectiondecrease"></a>

#### `EffectBlasterDeflectionDecrease(nChange)` - Routine 470

decrease the blaster deflection rate

**Parameters:**

- `nChange`: `int`

**Returns:** `effect`

<a id="effecthorrified"></a>

#### `EffectHorrified()` - Routine 471

Make the creature horified. BOO!

**Returns:** `effect`

<a id="effectspelllevelabsorption"></a>

#### `EffectSpellLevelAbsorption(nMaxSpellLevelAbsorbed, nTotalSpellLevelsAbsorbed=0, nSpellSchool=0)` - Routine 472

Create a Spell Level Absorption effect.
- nMaxSpellLevelAbsorbed: maximum spell level that will be absorbed by the
effect
- nTotalSpellLevelsAbsorbed: maximum number of spell levels that will be
absorbed by the effect
- nSpellSchool: SPELL_SCHOOL_*
* Returns an effect of type EFFECT_TYPE_INVALIDEFFECT if:
nMaxSpellLevelAbsorbed is not between -1 and 9 inclusive, or nSpellSchool
is invalid.

**Parameters:**

- `nMaxSpellLevelAbsorbed`: `int`
- `nTotalSpellLevelsAbsorbed`: `int` (default: `0`)
- `nSpellSchool`: `int` (default: `0`)

**Returns:** `effect`

<a id="effectdispelmagicbest"></a>

#### `EffectDispelMagicBest(nCasterLevel)` - Routine 473

Create a Dispel Magic Best effect.

**Parameters:**

- `nCasterLevel`: `int`

**Returns:** `effect`

<a id="effectmisschance"></a>

#### `EffectMissChance(nPercentage)` - Routine 477

Create a Miss Chance effect.
- nPercentage: 1-100 inclusive
* Returns an effect of type EFFECT_TYPE_INVALIDEFFECT if nPercentage < 1 or
nPercentage > 100.

**Parameters:**

- `nPercentage`: `int`

**Returns:** `effect`

<a id="effectmodifyattacks"></a>

#### `EffectModifyAttacks(nAttacks)` - Routine 485

Create a Modify Attacks effect to add attacks.
- nAttacks: maximum is 5, even with the effect stacked
* Returns an effect of type EFFECT_TYPE_INVALIDEFFECT if nAttacks > 5.

**Parameters:**

- `nAttacks`: `int`

**Returns:** `effect`

<a id="effectdamageshield"></a>

#### `EffectDamageShield(nDamageAmount, nRandomAmount, nDamageType)` - Routine 487

Create a Damage Shield effect which does (nDamageAmount + nRandomAmount)
damage to any melee attacker on a successful attack of damage type nDamageType.
- nDamageAmount: an integer value
- nRandomAmount: DAMAGE_BONUS_*
- nDamageType: DAMAGE_TYPE_*

**Parameters:**

- `nDamageAmount`: `int`
- `nRandomAmount`: `int`
- `nDamageType`: `int`

**Returns:** `effect`

<a id="effectforcedrain"></a>

#### `EffectForceDrain(nDamage)` - Routine 675

EffectForceDrain
This command will reduce the force points of a creature.

**Parameters:**

- `nDamage`: `int`

**Returns:** `effect`

<a id="effectpsychicstatic"></a>

#### `EffectPsychicStatic()` - Routine 676

EffectTemporaryForcePoints

**Returns:** `effect`

<a id="effectcutscenehorrified"></a>

#### `EffectCutSceneHorrified()` - Routine 754

EffectCutSceneHorrified
Get a horrified effect for cutscene purposes (ie. this effect will ignore immunities).

**Returns:** `effect`

<a id="effectcutsceneparalyze"></a>

#### `EffectCutSceneParalyze()` - Routine 755

EffectCutSceneParalyze
Get a paralyze effect for cutscene purposes (ie. this effect will ignore immunities).

**Returns:** `effect`

<a id="effectcutscenestunned"></a>

#### `EffectCutSceneStunned()` - Routine 756

EffectCutSceneStunned
Get a stun effect for cutscene purposes (ie. this effect will ignore immunities).

**Returns:** `effect`

<a id="effectlightsaberthrow"></a>

#### `EffectLightsaberThrow(oTarget1, oTarget2=1, oTarget3=1, nAdvancedDamage=0)`

702. EffectLightsaberThrow
This function throws a lightsaber at a target
If multiple targets are specified, then the lightsaber travels to them
sequentially, returning to the first object specified
This effect is applied to an object, so an effector is not needed

**Parameters:**

- `oTarget1`: `object`
- `oTarget2`: `object` (default: `1`)
- `oTarget3`: `object` (default: `1`)
- `nAdvancedDamage`: `int` (default: `0`)

**Returns:** `effect`

<a id="effectwhirlwind"></a>

#### `EffectWhirlWind()`

703.
creates the effect of a whirl wind.

**Returns:** `effect`


### Global Variables

<a id="setglobalstring"></a>

#### `SetGlobalString(sIdentifier, sValue)` - Routine 160

Sets a global string with the specified identifier.  This is an EXTREMELY
restricted function - do not use without expilicit permission.
This means if you are not Preston.  Then go see him if you're even thinking
about using this.

**Parameters:**

- `sIdentifier`: `string`
- `sValue`: `string`

<a id="getglobalstring"></a>

#### `GetGlobalString(sIdentifier)` - Routine 194

Get a global string with the specified identifier
This is an EXTREMELY restricted function.  Use only with explicit permission.
This means if you are not Preston.  Then go see him if you're even thinking
about using this.

**Parameters:**

- `sIdentifier`: `string`

**Returns:** `string`

<a id="getglobalboolean"></a>

#### `GetGlobalBoolean(sIdentifier)` - Routine 578

GetGlobalBoolean
This function returns the value of a global boolean (TRUE or FALSE) scripting variable.

**Parameters:**

- `sIdentifier`: `string`

**Returns:** `int`

<a id="setglobalboolean"></a>

#### `SetGlobalBoolean(sIdentifier, nValue)` - Routine 579

SetGlobalBoolean
This function sets the value of a global boolean (TRUE or FALSE) scripting variable.

**Parameters:**

- `sIdentifier`: `string`
- `nValue`: `int`

<a id="getglobalnumber"></a>

#### `GetGlobalNumber(sIdentifier)` - Routine 580

GetGlobalNumber
This function returns the value of a global number (-128 to +127) scripting variable.

**Parameters:**

- `sIdentifier`: `string`

**Returns:** `int`

<a id="setglobalnumber"></a>

#### `SetGlobalNumber(sIdentifier, nValue)` - Routine 581

SetGlobalNumber
This function sets the value of a global number (-128 to +127) scripting variable.

**Parameters:**

- `sIdentifier`: `string`
- `nValue`: `int`

<a id="getgloballocation"></a>

#### `GetGlobalLocation(sIdentifier)` - Routine 692

GetGlobalLocation
This function returns the a global location scripting variable.

**Parameters:**

- `sIdentifier`: `string`

**Returns:** `location`

<a id="setgloballocation"></a>

#### `SetGlobalLocation(sIdentifier, lValue)` - Routine 693

SetGlobalLocation
This function sets the a global location scripting variable.

**Parameters:**

- `sIdentifier`: `string`
- `lValue`: `location`

<a id="setglobalfadein"></a>

#### `SetGlobalFadeIn(fWait=0.0, fLength=0.0, fR=0.0, fG=0.0, fB=0.0)`

719. SetGlobalFadeIn
Sets a Fade In that starts after fWait seconds and fades for fLength Seconds.
The Fade will be from a color specified by the RGB values fR, fG, and fB.
Note that fR, fG, and fB are normalized values.
The default values are an immediate cut in from black.

**Parameters:**

- `fWait`: `float` (default: `0.0`)
- `fLength`: `float` (default: `0.0`)
- `fR`: `float` (default: `0.0`)
- `fG`: `float` (default: `0.0`)
- `fB`: `float` (default: `0.0`)

<a id="setglobalfadeout"></a>

#### `SetGlobalFadeOut(fWait=0.0, fLength=0.0, fR=0.0, fG=0.0, fB=0.0)`

720. SetGlobalFadeOut
Sets a Fade Out that starts after fWait seconds and fades for fLength Seconds.
The Fade will be to a color specified by the RGB values fR, fG, and fB.
Note that fR, fG, and fB are normalized values.
The default values are an immediate cut to from black.

**Parameters:**

- `fWait`: `float` (default: `0.0`)
- `fLength`: `float` (default: `0.0`)
- `fR`: `float` (default: `0.0`)
- `fG`: `float` (default: `0.0`)
- `fB`: `float` (default: `0.0`)


### Item Management

<a id="getitempossessor"></a>

#### `GetItemPossessor(oItem)` - Routine 29

Get the possessor of oItem
* Return value on error: OBJECT_INVALID

**Parameters:**

- `oItem`: `object`

**Returns:** `object`

<a id="getitempossessedby"></a>

#### `GetItemPossessedBy(oCreature, sItemTag)` - Routine 30

Get the object possessed by oCreature with the tag sItemTag
* Return value on error: OBJECT_INVALID

**Parameters:**

- `oCreature`: `object`
- `sItemTag`: `string`

**Returns:** `object`

<a id="createitemonobject"></a>

#### `CreateItemOnObject(sItemTemplate, oTarget=0, nStackSize=1)` - Routine 31

Create an item with the template sItemTemplate in oTarget's inventory.
- nStackSize: This is the stack size of the item to be created
* Return value: The object that has been created.  On error, this returns
OBJECT_INVALID.

**Parameters:**

- `sItemTemplate`: `string`
- `oTarget`: `object` (default: `0`)
- `nStackSize`: `int` (default: `1`)

**Returns:** `object`

<a id="actionequipitem"></a>

#### `ActionEquipItem(oItem, nInventorySlot, bInstant=0)` - Routine 32

Equip oItem into nInventorySlot.
- nInventorySlot: INVENTORY_SLOT_*
* No return value, but if an error occurs the log file will contain
"ActionEquipItem failed."

**Parameters:**

- `oItem`: `object`
- `nInventorySlot`: `int`
- `bInstant`: `int` (default: `0`)

<a id="actionunequipitem"></a>

#### `ActionUnequipItem(oItem, bInstant=0)` - Routine 33

Unequip oItem from whatever slot it is currently in.

**Parameters:**

- `oItem`: `object`
- `bInstant`: `int` (default: `0`)

<a id="actionpickupitem"></a>

#### `ActionPickUpItem(oItem)` - Routine 34

Pick up oItem from the ground.
* No return value, but if an error occurs the log file will contain
"ActionPickUpItem failed."

**Parameters:**

- `oItem`: `object`

<a id="actionputdownitem"></a>

#### `ActionPutDownItem(oItem)` - Routine 35

Put down oItem on the ground.
* No return value, but if an error occurs the log file will contain
"ActionPutDownItem failed."

**Parameters:**

- `oItem`: `object`

<a id="getlastitemequipped"></a>

#### `GetLastItemEquipped()` - Routine 52

Returns the last item that was equipped by a creature.

**Returns:** `object`

<a id="actiongiveitem"></a>

#### `ActionGiveItem(oItem, oGiveTo)` - Routine 135

Give oItem to oGiveTo
If oItem is not a valid item, or oGiveTo is not a valid object, nothing will
happen.

**Parameters:**

- `oItem`: `object`
- `oGiveTo`: `object`

<a id="actiontakeitem"></a>

#### `ActionTakeItem(oItem, oTakeFrom)` - Routine 136

Take oItem from oTakeFrom
If oItem is not a valid item, or oTakeFrom is not a valid object, nothing
will happen.

**Parameters:**

- `oItem`: `object`
- `oTakeFrom`: `object`

<a id="getitemstacksize"></a>

#### `GetItemStackSize(oItem)` - Routine 138

Gets the stack size of an item.

**Parameters:**

- `oItem`: `object`

**Returns:** `int`

<a id="setitemstacksize"></a>

#### `SetItemStackSize(oItem, nStackSize)` - Routine 150

Set the stack size of an item.
NOTE: The stack size will be clamped to between 1 and the max stack size (as
specified in the base item).

**Parameters:**

- `oItem`: `object`
- `nStackSize`: `int`

<a id="getiteminslot"></a>

#### `GetItemInSlot(nInventorySlot, oCreature=0)` - Routine 155

Get the object which is in oCreature's specified inventory slot
- nInventorySlot: INVENTORY_SLOT_*
- oCreature
* Returns OBJECT_INVALID if oCreature is not a valid creature or there is no
item in nInventorySlot.

**Parameters:**

- `nInventorySlot`: `int`
- `oCreature`: `object` (default: `0`)

**Returns:** `object`

<a id="createobject"></a>

#### `CreateObject(nObjectType, sTemplate, lLocation, bUseAppearAnimation=0)` - Routine 243

Create an object of the specified type at lLocation.
- nObjectType: OBJECT_TYPE_ITEM, OBJECT_TYPE_CREATURE, OBJECT_TYPE_PLACEABLE,
OBJECT_TYPE_STORE
- sTemplate
- lLocation
- bUseAppearAnimation
Waypoints can now also be created using the CreateObject function.
nObjectType is: OBJECT_TYPE_WAYPOINT
sTemplate will be the tag of the waypoint
lLocation is where the waypoint will be placed
bUseAppearAnimation is ignored

**Parameters:**

- `nObjectType`: `int`
- `sTemplate`: `string`
- `lLocation`: `location`
- `bUseAppearAnimation`: `int` (default: `0`)

**Returns:** `object`

<a id="setitemnonequippable"></a>

#### `SetItemNonEquippable(oItem, bNonEquippable)` - Routine 266

Flag the specified item as being non-equippable or not.  Set bNonEquippable
to TRUE to prevent this item from being equipped, and FALSE to allow
the normal equipping checks to determine if the item can be equipped.
NOTE: This will do nothing if the object passed in is not an item.  Items that
are already equipped when this is called will not automatically be
unequipped.  These items will just be prevented from being re-equipped
should they be unequipped.

**Parameters:**

- `oItem`: `object`
- `bNonEquippable`: `int`

<a id="giveitem"></a>

#### `GiveItem(oItem, oGiveTo)` - Routine 271

Give oItem to oGiveTo (instant; for similar Action use ActionGiveItem)
If oItem is not a valid item, or oGiveTo is not a valid object, nothing will
happen.

**Parameters:**

- `oItem`: `object`
- `oGiveTo`: `object`

<a id="getmoduleitemacquired"></a>

#### `GetModuleItemAcquired()` - Routine 282

Use this in an OnItemAcquired script to get the item that was acquired.
* Returns OBJECT_INVALID if the module is not valid.

**Returns:** `object`

<a id="getmoduleitemacquiredfrom"></a>

#### `GetModuleItemAcquiredFrom()` - Routine 283

Use this in an OnItemAcquired script to get the creatre that previously
possessed the item.
* Returns OBJECT_INVALID if the item was picked up from the ground.

**Returns:** `object`

<a id="getmoduleitemlost"></a>

#### `GetModuleItemLost()` - Routine 292

Use this in an OnItemLost script to get the item that was lost/dropped.
* Returns OBJECT_INVALID if the module is not valid.

**Returns:** `object`

<a id="getmoduleitemlostby"></a>

#### `GetModuleItemLostBy()` - Routine 293

Use this in an OnItemLost script to get the creature that lost the item.
* Returns OBJECT_INVALID if the module is not valid.

**Returns:** `object`

<a id="getidentified"></a>

#### `GetIdentified(oItem)` - Routine 332

Determined whether oItem has been identified.

**Parameters:**

- `oItem`: `object`

**Returns:** `int`

<a id="setidentified"></a>

#### `SetIdentified(oItem, bIdentified)` - Routine 333

Set whether oItem has been identified.

**Parameters:**

- `oItem`: `object`
- `bIdentified`: `int`

<a id="getfirstitemininventory"></a>

#### `GetFirstItemInInventory(oTarget=0)` - Routine 339

Get the first item in oTarget's inventory (start to cycle through oTarget's
inventory).
* Returns OBJECT_INVALID if the caller is not a creature, item, placeable or store,
or if no item is found.

**Parameters:**

- `oTarget`: `object` (default: `0`)

**Returns:** `object`

<a id="getnextitemininventory"></a>

#### `GetNextItemInInventory(oTarget=0)` - Routine 340

Get the next item in oTarget's inventory (continue to cycle through oTarget's
inventory).
* Returns OBJECT_INVALID if the caller is not a creature, item, placeable or store,
or if no item is found.

**Parameters:**

- `oTarget`: `object` (default: `0`)

**Returns:** `object`

<a id="getinventorydisturbitem"></a>

#### `GetInventoryDisturbItem()` - Routine 353

get the item that caused the caller's OnInventoryDisturbed script to fire.
* Returns OBJECT_INVALID if the caller is not a valid object.

**Returns:** `object`

<a id="getbaseitemtype"></a>

#### `GetBaseItemType(oItem)` - Routine 397

Get the base item type (BASE_ITEM_*) of oItem.
* Returns BASE_ITEM_INVALID if oItem is an invalid item.

**Parameters:**

- `oItem`: `object`

**Returns:** `int`

<a id="getitemacvalue"></a>

#### `GetItemACValue(oItem)` - Routine 401

Get the Armour Class of oItem.
* Return 0 if the oItem is not a valid item, or if oItem has no armour value.

**Parameters:**

- `oItem`: `object`

**Returns:** `int`

<a id="eventactivateitem"></a>

#### `EventActivateItem(oItem, lTarget, oTarget=1)` - Routine 424

Activate oItem.

**Parameters:**

- `oItem`: `object`
- `lTarget`: `location`
- `oTarget`: `object` (default: `1`)

**Returns:** `event`

<a id="getitemactivated"></a>

#### `GetItemActivated()` - Routine 439

Use this in an OnItemActivated module script to get the item that was activated.

**Returns:** `object`

<a id="getitemactivator"></a>

#### `GetItemActivator()` - Routine 440

Use this in an OnItemActivated module script to get the creature that
activated the item.

**Returns:** `object`

<a id="getitemactivatedtargetlocation"></a>

#### `GetItemActivatedTargetLocation()` - Routine 441

Use this in an OnItemActivated module script to get the location of the item's
target.

**Returns:** `location`

<a id="getitemactivatedtarget"></a>

#### `GetItemActivatedTarget()` - Routine 442

Use this in an OnItemActivated module script to get the item's target.

**Returns:** `object`

<a id="getnumstackeditems"></a>

#### `GetNumStackedItems(oItem)` - Routine 475

Get the number of stacked items that oItem comprises.

**Parameters:**

- `oItem`: `object`

**Returns:** `int`

<a id="changeitemcost"></a>

#### `ChangeItemCost(sItem, fCostMultiplier)` - Routine 747

ChangeItemCost
Change the cost of an item

**Parameters:**

- `sItem`: `string`
- `fCostMultiplier`: `float`

<a id="createitemonfloor"></a>

#### `CreateItemOnFloor(sTemplate, lLocation, bUseAppearAnimation=0)`

766. CreateItemOnFloor
Should only be used for items that have been created on the ground, and will
be destroyed without ever being picked up or equipped.  Returns true if successful

**Parameters:**

- `sTemplate`: `string`
- `lLocation`: `location`
- `bUseAppearAnimation`: `int` (default: `0`)

**Returns:** `object`


### Item Properties

<a id="getitemhasitemproperty"></a>

#### `GetItemHasItemProperty(oItem, nProperty)` - Routine 398

Determines whether oItem has nProperty.
- oItem
- nProperty: ITEM_PROPERTY_*
* Returns FALSE if oItem is not a valid item, or if oItem does not have
nProperty.

**Parameters:**

- `oItem`: `object`
- `nProperty`: `int`

**Returns:** `int`


### Local Variables

<a id="getlocalboolean"></a>

#### `GetLocalBoolean(oObject, nIndex)`

679. GetLocalBoolean
This gets a boolean flag on an object
currently the index is a range between 0 and 63

**Parameters:**

- `oObject`: `object`
- `nIndex`: `int`

**Returns:** `int`

<a id="setlocalboolean"></a>

#### `SetLocalBoolean(oObject, nIndex, nValue)`

680. SetLocalBoolean
This sets a boolean flag on an object
currently the index is a range between 0 and 63

**Parameters:**

- `oObject`: `object`
- `nIndex`: `int`
- `nValue`: `int`

<a id="getlocalnumber"></a>

#### `GetLocalNumber(oObject, nIndex)`

681. GetLocalNumber
This gets a number on an object
currently the index is a range between 0 and 0

**Parameters:**

- `oObject`: `object`
- `nIndex`: `int`

**Returns:** `int`

<a id="setlocalnumber"></a>

#### `SetLocalNumber(oObject, nIndex, nValue)`

682. SetLocalNumber
This sets a number on an object
currently the index is a range between 0 and 0

**Parameters:**

- `oObject`: `object`
- `nIndex`: `int`
- `nValue`: `int`


### Module and Area Functions

<a id="settime"></a>

#### `SetTime(nHour, nMinute, nSecond, nMillisecond)` - Routine 12

Set the time to the time specified.
- nHour should be from 0 to 23 inclusive
- nMinute should be from 0 to 59 inclusive
- nSecond should be from 0 to 59 inclusive
- nMillisecond should be from 0 to 999 inclusive
1) Time can only be advanced forwards; attempting to set the time backwards
will result in the day advancing and then the time being set to that
specified, e.g. if the current hour is 15 and then the hour is set to 3,
the day will be advanced by 1 and the hour will be set to 3.
2) If values larger than the max hour, minute, second or millisecond are
specified, they will be wrapped around and the overflow will be used to
advance the next field, e.g. specifying 62 hours, 250 minutes, 10 seconds
and 10 milliseconds will result in the calendar day being advanced by 2
and the time being set to 18 hours, 10 minutes, 10 milliseconds.

**Parameters:**

- `nHour`: `int`
- `nMinute`: `int`
- `nSecond`: `int`
- `nMillisecond`: `int`

<a id="setareaunescapable"></a>

#### `SetAreaUnescapable(bUnescapable)` - Routine 14

Sets whether the current area is escapable or not
TRUE means you can not escape the area
FALSE means you can escape the area

**Parameters:**

- `bUnescapable`: `int`

<a id="getareaunescapable"></a>

#### `GetAreaUnescapable()` - Routine 15

Returns whether the current area is escapable or not
TRUE means you can not escape the area
FALSE means you can escape the area

**Returns:** `int`

<a id="gettimehour"></a>

#### `GetTimeHour()` - Routine 16

Get the current hour.

**Returns:** `int`

<a id="gettimeminute"></a>

#### `GetTimeMinute()` - Routine 17

Get the current minute

**Returns:** `int`

<a id="gettimesecond"></a>

#### `GetTimeSecond()` - Routine 18

Get the current second

**Returns:** `int`

<a id="gettimemillisecond"></a>

#### `GetTimeMillisecond()` - Routine 19

Get the current millisecond

**Returns:** `int`

<a id="getarea"></a>

#### `GetArea(oTarget)` - Routine 24

Get the area that oTarget is currently in
* Return value on error: OBJECT_INVALID

**Parameters:**

- `oTarget`: `object`

**Returns:** `object`

<a id="getenteringobject"></a>

#### `GetEnteringObject()` - Routine 25

The value returned by this function depends on the object type of the caller:
1) If the caller is a door or placeable it returns the object that last
triggered it.
2) If the caller is a trigger, area of effect, module, area or encounter it
returns the object that last entered it.
* Return value on error: OBJECT_INVALID

**Returns:** `object`

<a id="getexitingobject"></a>

#### `GetExitingObject()` - Routine 26

Get the object that last left the caller.  This function works on triggers,
areas of effect, modules, areas and encounters.
* Return value on error: OBJECT_INVALID

**Returns:** `object`

<a id="gettransitiontarget"></a>

#### `GetTransitionTarget(oTransition)` - Routine 198

Get the destination (a waypoint or a door) for a trigger or a door.
* Returns OBJECT_INVALID if oTransition is not a valid trigger or door.

**Parameters:**

- `oTransition`: `object`

**Returns:** `object`

<a id="setareatransitionbmp"></a>

#### `SetAreaTransitionBMP(nPredefinedAreaTransition, sCustomAreaTransitionBMP=)` - Routine 203

Set the transition bitmap of a player; this should only be called in area
transition scripts. This action should be run by the person "clicking" the
area transition via AssignCommand.
- nPredefinedAreaTransition:
-> To use a predefined area transition bitmap, use one of AREA_TRANSITION_*
-> To use a custom, user-defined area transition bitmap, use
AREA_TRANSITION_USER_DEFINED and specify the filename in the second
parameter
- sCustomAreaTransitionBMP: this is the filename of a custom, user-defined
area transition bitmap

**Parameters:**

- `nPredefinedAreaTransition`: `int`
- `sCustomAreaTransitionBMP`: `string` (default: ``)

<a id="getmodulefilename"></a>

#### `GetModuleFileName()` - Routine 210

Gets the actual file name of the current module

**Returns:** `string`

<a id="getmodule"></a>

#### `GetModule()` - Routine 242

Get the module.
* Return value on error: OBJECT_INVALID

**Returns:** `object`

<a id="exploreareaforplayer"></a>

#### `ExploreAreaForPlayer(oArea, oPlayer)` - Routine 403

Expose the entire map of oArea to oPlayer.

**Parameters:**

- `oArea`: `object`
- `oPlayer`: `object`

<a id="getmodulename"></a>

#### `GetModuleName()` - Routine 561

Get the module's name in the language of the server that's running it.
* If there is no entry for the language of the server, it will return an
empty string

**Returns:** `string`


### Object Query and Manipulation

<a id="setfacing"></a>

#### `SetFacing(fDirection)` - Routine 10

Cause the caller to face fDirection.
- fDirection is expressed as anticlockwise degrees from Due East.
DIRECTION_EAST, DIRECTION_NORTH, DIRECTION_WEST and DIRECTION_SOUTH are

**Parameters:**

- `fDirection`: `float`

<a id="getposition"></a>

#### `GetPosition(oTarget)` - Routine 27

Get the position of oTarget
* Return value on error: vector (0.0f, 0.0f, 0.0f)

**Parameters:**

- `oTarget`: `object`

**Returns:** `vector`

<a id="getfacing"></a>

#### `GetFacing(oTarget)` - Routine 28

Get the direction in which oTarget is facing, expressed as a float between
0.0f and 360.0f
* Return value on error: -1.0f

**Parameters:**

- `oTarget`: `object`

**Returns:** `float`

<a id="getnearestcreature"></a>

#### `GetNearestCreature(nFirstCriteriaType, nFirstCriteriaValue, oTarget=0, nNth=1, nSecondCriteriaType=-1, nSecondCriteriaValue=-1, nThirdCriteriaType=-1, nThirdCriteriaValue=-1)` - Routine 38

Get the creature nearest to oTarget, subject to all the criteria specified.
- nFirstCriteriaType: CREATURE_TYPE_*
- nFirstCriteriaValue:
-> CLASS_TYPE_* if nFirstCriteriaType was CREATURE_TYPE_CLASS
-> SPELL_* if nFirstCriteriaType was CREATURE_TYPE_DOES_NOT_HAVE_SPELL_EFFECT
or CREATURE_TYPE_HAS_SPELL_EFFECT
-> TRUE or FALSE if nFirstCriteriaType was CREATURE_TYPE_IS_ALIVE
-> PERCEPTION_* if nFirstCriteriaType was CREATURE_TYPE_PERCEPTION
-> PLAYER_CHAR_IS_PC or PLAYER_CHAR_NOT_PC if nFirstCriteriaType was
CREATURE_TYPE_PLAYER_CHAR
-> RACIAL_TYPE_* if nFirstCriteriaType was CREATURE_TYPE_RACIAL_TYPE
-> REPUTATION_TYPE_* if nFirstCriteriaType was CREATURE_TYPE_REPUTATION
For example, to get the nearest PC, use:
(CREATURE_TYPE_PLAYER_CHAR, PLAYER_CHAR_IS_PC)
- oTarget: We're trying to find the creature of the specified type that is
nearest to oTarget
- nNth: We don't have to find the first nearest: we can find the Nth nearest...
- nSecondCriteriaType: This is used in the same way as nFirstCriteriaType to
further specify the type of creature that we are looking for.
- nSecondCriteriaValue: This is used in the same way as nFirstCriteriaValue
to further specify the type of creature that we are looking for.
- nThirdCriteriaType: This is used in the same way as nFirstCriteriaType to
further specify the type of creature that we are looking for.
- nThirdCriteriaValue: This is used in the same way as nFirstCriteriaValue to
further specify the type of creature that we are looking for.
* Return value on error: OBJECT_INVALID

**Parameters:**

- `nFirstCriteriaType`: `int`
- `nFirstCriteriaValue`: `int`
- `oTarget`: `object` (default: `0`)
- `nNth`: `int` (default: `1`)
- `nSecondCriteriaType`: `int` (default: `-1`)
- `nSecondCriteriaValue`: `int` (default: `-1`)
- `nThirdCriteriaType`: `int` (default: `-1`)
- `nThirdCriteriaValue`: `int` (default: `-1`)

**Returns:** `object`

<a id="getdistancetoobject"></a>

#### `GetDistanceToObject(oObject)` - Routine 41

Get the distance from the caller to oObject in metres.
* Return value on error: -1.0f

**Parameters:**

- `oObject`: `object`

**Returns:** `float`

<a id="getisobjectvalid"></a>

#### `GetIsObjectValid(oObject)` - Routine 42

* Returns TRUE if oObject is a valid object.

**Parameters:**

- `oObject`: `object`

**Returns:** `int`

<a id="getfirsteffect"></a>

#### `GetFirstEffect(oCreature)` - Routine 85

Get the first in-game effect on oCreature.

**Parameters:**

- `oCreature`: `object`

**Returns:** `effect`

<a id="getnexteffect"></a>

#### `GetNextEffect(oCreature)` - Routine 86

Get the next in-game effect on oCreature.

**Parameters:**

- `oCreature`: `object`

**Returns:** `effect`

<a id="removeeffect"></a>

#### `RemoveEffect(oCreature, eEffect)` - Routine 87

Remove eEffect from oCreature.
* No return value

**Parameters:**

- `oCreature`: `object`
- `eEffect`: `effect`

<a id="geteffectcreator"></a>

#### `GetEffectCreator(eEffect)` - Routine 91

Get the object that created eEffect.
* Returns OBJECT_INVALID if eEffect is not a valid effect.

**Parameters:**

- `eEffect`: `effect`

**Returns:** `object`

<a id="getobjecttype"></a>

#### `GetObjectType(oTarget)` - Routine 106

Get the object type (OBJECT_TYPE_*) of oTarget
* Return value if oTarget is not a valid object: -1

**Parameters:**

- `oTarget`: `object`

**Returns:** `int`

<a id="getisdead"></a>

#### `GetIsDead(oCreature)` - Routine 140

* Returns TRUE if oCreature is a dead NPC, dead PC or a dying PC.

**Parameters:**

- `oCreature`: `object`

**Returns:** `int`

<a id="setfacingpoint"></a>

#### `SetFacingPoint(vTarget)` - Routine 143

Cause the caller to face vTarget

**Parameters:**

- `vTarget`: `vector`

<a id="getdistancebetween"></a>

#### `GetDistanceBetween(oObjectA, oObjectB)` - Routine 151

Get the distance in metres between oObjectA and oObjectB.
* Return value if either object is invalid: 0.0f

**Parameters:**

- `oObjectA`: `object`
- `oObjectB`: `object`

**Returns:** `float`

<a id="gettag"></a>

#### `GetTag(oObject)` - Routine 168

Get the Tag of oObject
* Return value if oObject is not a valid object: ""

**Parameters:**

- `oObject`: `object`

**Returns:** `string`

<a id="geteffecttype"></a>

#### `GetEffectType(eEffect)` - Routine 170

Get the effect type (EFFECT_TYPE_*) of eEffect.
* Return value if eEffect is invalid: EFFECT_INVALIDEFFECT

**Parameters:**

- `eEffect`: `effect`

**Returns:** `int`

<a id="getobjectbytag"></a>

#### `GetObjectByTag(sTag, nNth=0)` - Routine 200

Get the nNth object with the specified tag.
- sTag
- nNth: the nth object with this tag may be requested
* Returns OBJECT_INVALID if the object cannot be found.

**Parameters:**

- `sTag`: `string`
- `nNth`: `int` (default: `0`)

**Returns:** `object`

<a id="getlocation"></a>

#### `GetLocation(oObject)` - Routine 213

Get the location of oObject.

**Parameters:**

- `oObject`: `object`

**Returns:** `location`

<a id="location"></a>

#### `Location(vPosition, fOrientation)` - Routine 215

Create a location.

**Parameters:**

- `vPosition`: `vector`
- `fOrientation`: `float`

**Returns:** `location`

<a id="applyeffectatlocation"></a>

#### `ApplyEffectAtLocation(nDurationType, eEffect, lLocation, fDuration=0.0)` - Routine 216

Apply eEffect at lLocation.

**Parameters:**

- `nDurationType`: `int`
- `eEffect`: `effect`
- `lLocation`: `location`
- `fDuration`: `float` (default: `0.0`)

<a id="applyeffecttoobject"></a>

#### `ApplyEffectToObject(nDurationType, eEffect, oTarget, fDuration=0.0)` - Routine 220

Apply eEffect to oTarget.

**Parameters:**

- `nDurationType`: `int`
- `eEffect`: `effect`
- `oTarget`: `object`
- `fDuration`: `float` (default: `0.0`)

<a id="getpositionfromlocation"></a>

#### `GetPositionFromLocation(lLocation)` - Routine 223

Get the position vector from lLocation.

**Parameters:**

- `lLocation`: `location`

**Returns:** `vector`

<a id="getfacingfromlocation"></a>

#### `GetFacingFromLocation(lLocation)` - Routine 225

Get the orientation value from lLocation.

**Parameters:**

- `lLocation`: `location`

**Returns:** `float`

<a id="getnearestcreaturetolocation"></a>

#### `GetNearestCreatureToLocation(nFirstCriteriaType, nFirstCriteriaValue, lLocation, nNth=1, nSecondCriteriaType=-1, nSecondCriteriaValue=-1, nThirdCriteriaType=-1, nThirdCriteriaValue=-1)` - Routine 226

Get the creature nearest to lLocation, subject to all the criteria specified.
- nFirstCriteriaType: CREATURE_TYPE_*
- nFirstCriteriaValue:
-> CLASS_TYPE_* if nFirstCriteriaType was CREATURE_TYPE_CLASS
-> SPELL_* if nFirstCriteriaType was CREATURE_TYPE_DOES_NOT_HAVE_SPELL_EFFECT
or CREATURE_TYPE_HAS_SPELL_EFFECT
-> TRUE or FALSE if nFirstCriteriaType was CREATURE_TYPE_IS_ALIVE
-> PERCEPTION_* if nFirstCriteriaType was CREATURE_TYPE_PERCEPTION
-> PLAYER_CHAR_IS_PC or PLAYER_CHAR_NOT_PC if nFirstCriteriaType was
CREATURE_TYPE_PLAYER_CHAR
-> RACIAL_TYPE_* if nFirstCriteriaType was CREATURE_TYPE_RACIAL_TYPE
-> REPUTATION_TYPE_* if nFirstCriteriaType was CREATURE_TYPE_REPUTATION
For example, to get the nearest PC, use
(CREATURE_TYPE_PLAYER_CHAR, PLAYER_CHAR_IS_PC)
- lLocation: We're trying to find the creature of the specified type that is
nearest to lLocation
- nNth: We don't have to find the first nearest: we can find the Nth nearest....
- nSecondCriteriaType: This is used in the same way as nFirstCriteriaType to
further specify the type of creature that we are looking for.
- nSecondCriteriaValue: This is used in the same way as nFirstCriteriaValue
to further specify the type of creature that we are looking for.
- nThirdCriteriaType: This is used in the same way as nFirstCriteriaType to
further specify the type of creature that we are looking for.
- nThirdCriteriaValue: This is used in the same way as nFirstCriteriaValue to
further specify the type of creature that we are looking for.
* Return value on error: OBJECT_INVALID

**Parameters:**

- `nFirstCriteriaType`: `int`
- `nFirstCriteriaValue`: `int`
- `lLocation`: `location`
- `nNth`: `int` (default: `1`)
- `nSecondCriteriaType`: `int` (default: `-1`)
- `nSecondCriteriaValue`: `int` (default: `-1`)
- `nThirdCriteriaType`: `int` (default: `-1`)
- `nThirdCriteriaValue`: `int` (default: `-1`)

**Returns:** `object`

<a id="getnearestobject"></a>

#### `GetNearestObject(nObjectType=32767, oTarget=0, nNth=1)` - Routine 227

Get the Nth object nearest to oTarget that is of the specified type.
- nObjectType: OBJECT_TYPE_*
- oTarget
- nNth
* Return value on error: OBJECT_INVALID

**Parameters:**

- `nObjectType`: `int` (default: `32767`)
- `oTarget`: `object` (default: `0`)
- `nNth`: `int` (default: `1`)

**Returns:** `object`

<a id="getnearestobjecttolocation"></a>

#### `GetNearestObjectToLocation(nObjectType, lLocation, nNth=1)` - Routine 228

Get the nNth object nearest to lLocation that is of the specified type.
- nObjectType: OBJECT_TYPE_*
- lLocation
- nNth
* Return value on error: OBJECT_INVALID

**Parameters:**

- `nObjectType`: `int`
- `lLocation`: `location`
- `nNth`: `int` (default: `1`)

**Returns:** `object`

<a id="getnearestobjectbytag"></a>

#### `GetNearestObjectByTag(sTag, oTarget=0, nNth=1)` - Routine 229

Get the nth Object nearest to oTarget that has sTag as its tag.
* Return value on error: OBJECT_INVALID

**Parameters:**

- `sTag`: `string`
- `oTarget`: `object` (default: `0`)
- `nNth`: `int` (default: `1`)

**Returns:** `object`

<a id="destroyobject"></a>

#### `DestroyObject(oDestroy, fDelay=0.0, bNoFade=0, fDelayUntilFade=0.0)` - Routine 241

Destroy oObject (irrevocably).
This will not work on modules and areas.
The bNoFade and fDelayUntilFade are for creatures and placeables only

**Parameters:**

- `oDestroy`: `object`
- `fDelay`: `float` (default: `0.0`)
- `bNoFade`: `int` (default: `0`)
- `fDelayUntilFade`: `float` (default: `0.0`)

<a id="getname"></a>

#### `GetName(oObject)` - Routine 253

Get the name of oObject.

**Parameters:**

- `oObject`: `object`

**Returns:** `string`

<a id="getdistancebetweenlocations"></a>

#### `GetDistanceBetweenLocations(lLocationA, lLocationB)` - Routine 298

Get the distance between lLocationA and lLocationB.

**Parameters:**

- `lLocationA`: `location`
- `lLocationB`: `location`

**Returns:** `float`

<a id="playanimation"></a>

#### `PlayAnimation(nAnimation, fSpeed=1.0, fSeconds=0.0)` - Routine 300

Play nAnimation immediately.
- nAnimation: ANIMATION_*
- fSpeed
- fSeconds: Duration of the animation (this is not used for Fire and
Forget animations) If a time of -1.0f is specified for a looping animation
it will loop until the next animation is applied.

**Parameters:**

- `nAnimation`: `int`
- `fSpeed`: `float` (default: `1.0`)
- `fSeconds`: `float` (default: `0.0`)

<a id="getdistancebetween2d"></a>

#### `GetDistanceBetween2D(oObjectA, oObjectB)` - Routine 319

Get the distance in metres between oObjectA and oObjectB in 2D.
* Return value if either object is invalid: 0.0f

**Parameters:**

- `oObjectA`: `object`
- `oObjectB`: `object`

**Returns:** `float`

<a id="getdistancebetweenlocations2d"></a>

#### `GetDistanceBetweenLocations2D(lLocationA, lLocationB)` - Routine 334

Get the distance between lLocationA and lLocationB. in 2D

**Parameters:**

- `lLocationA`: `location`
- `lLocationB`: `location`

**Returns:** `float`

<a id="getdistancetoobject2d"></a>

#### `GetDistanceToObject2D(oObject)` - Routine 335

Get the distance from the caller to oObject in metres.
* Return value on error: -1.0f

**Parameters:**

- `oObject`: `object`

**Returns:** `float`


### Other Functions

<a id="random"></a>

#### `Random(nMaxInteger)` - Routine 0

Get an integer between 0 and nMaxInteger-1.
Return value on error: 0

**Parameters:**

- `nMaxInteger`: `int`

**Returns:** `int`

<a id="printstring"></a>

#### `PrintString(sString)` - Routine 1

Output sString to the log file.

**Parameters:**

- `sString`: `string`

<a id="printfloat"></a>

#### `PrintFloat(fFloat, nWidth=18, nDecimals=9)` - Routine 2

Output a formatted float to the log file.
- nWidth should be a value from 0 to 18 inclusive.
- nDecimals should be a value from 0 to 9 inclusive.

**Parameters:**

- `fFloat`: `float`
- `nWidth`: `int` (default: `18`)
- `nDecimals`: `int` (default: `9`)

<a id="floattostring"></a>

#### `FloatToString(fFloat, nWidth=18, nDecimals=9)` - Routine 3

Convert fFloat into a string.
- nWidth should be a value from 0 to 18 inclusive.
- nDecimals should be a value from 0 to 9 inclusive.

**Parameters:**

- `fFloat`: `float`
- `nWidth`: `int` (default: `18`)
- `nDecimals`: `int` (default: `9`)

**Returns:** `string`

<a id="printinteger"></a>

#### `PrintInteger(nInteger)` - Routine 4

Output nInteger to the log file.

**Parameters:**

- `nInteger`: `int`

<a id="printobject"></a>

#### `PrintObject(oObject)` - Routine 5

Output oObject's ID to the log file.

**Parameters:**

- `oObject`: `object`

<a id="executescript"></a>

#### `ExecuteScript(sScript, oTarget, nScriptVar=-1)` - Routine 8

Make oTarget run sScript and then return execution to the calling script.
If sScript does not specify a compiled script, nothing happens.
- nScriptVar: This value will be returned by calls to GetRunScriptVar.

**Parameters:**

- `sScript`: `string`
- `oTarget`: `object`
- `nScriptVar`: `int` (default: `-1`)

<a id="setcamerafacing"></a>

#### `SetCameraFacing(fDirection)` - Routine 45

Change the direction in which the camera is facing
- fDirection is expressed as anticlockwise degrees from Due East.
(0.0f=East, 90.0f=North, 180.0f=West, 270.0f=South)
This can be used to change the way the camera is facing after the player
emerges from an area transition.

**Parameters:**

- `fDirection`: `float`

<a id="getsubscreenid"></a>

#### `GetSubScreenID()` - Routine 53

Returns the ID of the subscreen that is currently onscreen.  This will be one of the
SUBSCREEN_ID_* constant values.

**Returns:** `int`

<a id="cancelcombat"></a>

#### `CancelCombat(oidCreature)` - Routine 54

Cancels combat for the specified creature.

**Parameters:**

- `oidCreature`: `object`

<a id="pausegame"></a>

#### `PauseGame(bPause)` - Routine 57

Pauses the game if bPause is TRUE.  Unpauses if bPause is FALSE.

**Parameters:**

- `bPause`: `int`

<a id="getstringlength"></a>

#### `GetStringLength(sString)` - Routine 59

Get the length of sString
* Return value on error: -1

**Parameters:**

- `sString`: `string`

**Returns:** `int`

<a id="getstringuppercase"></a>

#### `GetStringUpperCase(sString)` - Routine 60

Convert sString into upper case
* Return value on error: ""

**Parameters:**

- `sString`: `string`

**Returns:** `string`

<a id="getstringlowercase"></a>

#### `GetStringLowerCase(sString)` - Routine 61

Convert sString into lower case
* Return value on error: ""

**Parameters:**

- `sString`: `string`

**Returns:** `string`

<a id="getstringright"></a>

#### `GetStringRight(sString, nCount)` - Routine 62

Get nCount characters from the right end of sString
* Return value on error: ""

**Parameters:**

- `sString`: `string`
- `nCount`: `int`

**Returns:** `string`

<a id="getstringleft"></a>

#### `GetStringLeft(sString, nCount)` - Routine 63

Get nCounter characters from the left end of sString
* Return value on error: ""

**Parameters:**

- `sString`: `string`
- `nCount`: `int`

**Returns:** `string`

<a id="insertstring"></a>

#### `InsertString(sDestination, sString, nPosition)` - Routine 64

Insert sString into sDestination at nPosition
* Return value on error: ""

**Parameters:**

- `sDestination`: `string`
- `sString`: `string`
- `nPosition`: `int`

**Returns:** `string`

<a id="getsubstring"></a>

#### `GetSubString(sString, nStart, nCount)` - Routine 65

Get nCount characters from sString, starting at nStart
* Return value on error: ""

**Parameters:**

- `sString`: `string`
- `nStart`: `int`
- `nCount`: `int`

**Returns:** `string`

<a id="findsubstring"></a>

#### `FindSubString(sString, sSubString)` - Routine 66

Find the position of sSubstring inside sString
* Return value on error: -1

**Parameters:**

- `sString`: `string`
- `sSubString`: `string`

**Returns:** `int`

<a id="fabs"></a>

#### `fabs(fValue)` - Routine 67

Maths operation: absolute value of fValue

**Parameters:**

- `fValue`: `float`

**Returns:** `float`

<a id="cos"></a>

#### `cos(fValue)` - Routine 68

Maths operation: cosine of fValue

**Parameters:**

- `fValue`: `float`

**Returns:** `float`

<a id="sin"></a>

#### `sin(fValue)` - Routine 69

Maths operation: sine of fValue

**Parameters:**

- `fValue`: `float`

**Returns:** `float`

<a id="tan"></a>

#### `tan(fValue)` - Routine 70

Maths operation: tan of fValue

**Parameters:**

- `fValue`: `float`

**Returns:** `float`

<a id="acos"></a>

#### `acos(fValue)` - Routine 71

Maths operation: arccosine of fValue
* Returns zero if fValue > 1 or fValue < -1

**Parameters:**

- `fValue`: `float`

**Returns:** `float`

<a id="asin"></a>

#### `asin(fValue)` - Routine 72

Maths operation: arcsine of fValue
* Returns zero if fValue >1 or fValue < -1

**Parameters:**

- `fValue`: `float`

**Returns:** `float`

<a id="atan"></a>

#### `atan(fValue)` - Routine 73

Maths operation: arctan of fValue

**Parameters:**

- `fValue`: `float`

**Returns:** `float`

<a id="log"></a>

#### `log(fValue)` - Routine 74

Maths operation: log of fValue
* Returns zero if fValue <= zero

**Parameters:**

- `fValue`: `float`

**Returns:** `float`

<a id="pow"></a>

#### `pow(fValue, fExponent)` - Routine 75

Maths operation: fValue is raised to the power of fExponent
* Returns zero if fValue ==0 and fExponent <0

**Parameters:**

- `fValue`: `float`
- `fExponent`: `float`

**Returns:** `float`

<a id="sqrt"></a>

#### `sqrt(fValue)` - Routine 76

Maths operation: square root of fValue
* Returns zero if fValue <0

**Parameters:**

- `fValue`: `float`

**Returns:** `float`

<a id="abs"></a>

#### `abs(nValue)` - Routine 77

Maths operation: integer absolute value of nValue
* Return value on error: 0

**Parameters:**

- `nValue`: `int`

**Returns:** `int`

<a id="getcasterlevel"></a>

#### `GetCasterLevel(oCreature)` - Routine 84

Get the Caster Level of oCreature.
* Return value on error: 0;

**Parameters:**

- `oCreature`: `object`

**Returns:** `int`

<a id="getiseffectvalid"></a>

#### `GetIsEffectValid(eEffect)` - Routine 88

* Returns TRUE if eEffect is a valid effect.

**Parameters:**

- `eEffect`: `effect`

**Returns:** `int`

<a id="geteffectdurationtype"></a>

#### `GetEffectDurationType(eEffect)` - Routine 89

Get the duration type (DURATION_TYPE_*) of eEffect.
* Return value if eEffect is not valid: -1

**Parameters:**

- `eEffect`: `effect`

**Returns:** `int`

<a id="geteffectsubtype"></a>

#### `GetEffectSubType(eEffect)` - Routine 90

Get the subtype (SUBTYPE_*) of eEffect.
* Return value on error: 0

**Parameters:**

- `eEffect`: `effect`

**Returns:** `int`

<a id="inttostring"></a>

#### `IntToString(nInteger)` - Routine 92

Convert nInteger into a string.
* Return value on error: ""

**Parameters:**

- `nInteger`: `int`

**Returns:** `string`

<a id="getfirstobjectinarea"></a>

#### `GetFirstObjectInArea(oArea=1, nObjectFilter=1)` - Routine 93

Get the first object in oArea.
If no valid area is specified, it will use the caller's area.
- oArea
- nObjectFilter: OBJECT_TYPE_*
* Return value on error: OBJECT_INVALID

**Parameters:**

- `oArea`: `object` (default: `1`)
- `nObjectFilter`: `int` (default: `1`)

**Returns:** `object`

<a id="getnextobjectinarea"></a>

#### `GetNextObjectInArea(oArea=1, nObjectFilter=1)` - Routine 94

Get the next object in oArea.
If no valid area is specified, it will use the caller's area.
- oArea
- nObjectFilter: OBJECT_TYPE_*
* Return value on error: OBJECT_INVALID

**Parameters:**

- `oArea`: `object` (default: `1`)
- `nObjectFilter`: `int` (default: `1`)

**Returns:** `object`

<a id="d2"></a>

#### `d2(nNumDice=1)` - Routine 95

Get the total from rolling (nNumDice x d2 dice).
- nNumDice: If this is less than 1, the value 1 will be used.

**Parameters:**

- `nNumDice`: `int` (default: `1`)

**Returns:** `int`

<a id="d3"></a>

#### `d3(nNumDice=1)` - Routine 96

Get the total from rolling (nNumDice x d3 dice).
- nNumDice: If this is less than 1, the value 1 will be used.

**Parameters:**

- `nNumDice`: `int` (default: `1`)

**Returns:** `int`

<a id="d4"></a>

#### `d4(nNumDice=1)` - Routine 97

Get the total from rolling (nNumDice x d4 dice).
- nNumDice: If this is less than 1, the value 1 will be used.

**Parameters:**

- `nNumDice`: `int` (default: `1`)

**Returns:** `int`

<a id="d6"></a>

#### `d6(nNumDice=1)` - Routine 98

Get the total from rolling (nNumDice x d6 dice).
- nNumDice: If this is less than 1, the value 1 will be used.

**Parameters:**

- `nNumDice`: `int` (default: `1`)

**Returns:** `int`

<a id="d8"></a>

#### `d8(nNumDice=1)` - Routine 99

Get the total from rolling (nNumDice x d8 dice).
- nNumDice: If this is less than 1, the value 1 will be used.

**Parameters:**

- `nNumDice`: `int` (default: `1`)

**Returns:** `int`

<a id="d10"></a>

#### `d10(nNumDice=1)` - Routine 100

Get the total from rolling (nNumDice x d10 dice).
- nNumDice: If this is less than 1, the value 1 will be used.

**Parameters:**

- `nNumDice`: `int` (default: `1`)

**Returns:** `int`

<a id="d12"></a>

#### `d12(nNumDice=1)` - Routine 101

Get the total from rolling (nNumDice x d12 dice).
- nNumDice: If this is less than 1, the value 1 will be used.

**Parameters:**

- `nNumDice`: `int` (default: `1`)

**Returns:** `int`

<a id="d20"></a>

#### `d20(nNumDice=1)` - Routine 102

Get the total from rolling (nNumDice x d20 dice).
- nNumDice: If this is less than 1, the value 1 will be used.

**Parameters:**

- `nNumDice`: `int` (default: `1`)

**Returns:** `int`

<a id="d100"></a>

#### `d100(nNumDice=1)` - Routine 103

Get the total from rolling (nNumDice x d100 dice).
- nNumDice: If this is less than 1, the value 1 will be used.

**Parameters:**

- `nNumDice`: `int` (default: `1`)

**Returns:** `int`

<a id="vectormagnitude"></a>

#### `VectorMagnitude(vVector)` - Routine 104

Get the magnitude of vVector; this can be used to determine the
distance between two points.
* Return value on error: 0.0f

**Parameters:**

- `vVector`: `vector`

**Returns:** `float`

<a id="getmetamagicfeat"></a>

#### `GetMetaMagicFeat()` - Routine 105

Get the metamagic type (METAMAGIC_*) of the last spell cast by the caller
* Return value if the caster is not a valid object: -1

**Returns:** `int`

<a id="getracialtype"></a>

#### `GetRacialType(oCreature)` - Routine 107

Get the racial type (RACIAL_TYPE_*) of oCreature
* Return value if oCreature is not a valid creature: RACIAL_TYPE_INVALID

**Parameters:**

- `oCreature`: `object`

**Returns:** `int`

<a id="fortitudesave"></a>

#### `FortitudeSave(oCreature, nDC, nSaveType=0, oSaveVersus=0)` - Routine 108

Do a Fortitude Save check for the given DC
- oCreature
- nDC: Difficulty check
- nSaveType: SAVING_THROW_TYPE_*
- oSaveVersus
Returns: 0 if the saving throw roll failed
Returns: 1 if the saving throw roll succeeded
Returns: 2 if the target was immune to the save type specified

**Parameters:**

- `oCreature`: `object`
- `nDC`: `int`
- `nSaveType`: `int` (default: `0`)
- `oSaveVersus`: `object` (default: `0`)

**Returns:** `int`

<a id="reflexsave"></a>

#### `ReflexSave(oCreature, nDC, nSaveType=0, oSaveVersus=0)` - Routine 109

Does a Reflex Save check for the given DC
- oCreature
- nDC: Difficulty check
- nSaveType: SAVING_THROW_TYPE_*
- oSaveVersus
Returns: 0 if the saving throw roll failed
Returns: 1 if the saving throw roll succeeded
Returns: 2 if the target was immune to the save type specified

**Parameters:**

- `oCreature`: `object`
- `nDC`: `int`
- `nSaveType`: `int` (default: `0`)
- `oSaveVersus`: `object` (default: `0`)

**Returns:** `int`

<a id="willsave"></a>

#### `WillSave(oCreature, nDC, nSaveType=0, oSaveVersus=0)` - Routine 110

Does a Will Save check for the given DC
- oCreature
- nDC: Difficulty check
- nSaveType: SAVING_THROW_TYPE_*
- oSaveVersus
Returns: 0 if the saving throw roll failed
Returns: 1 if the saving throw roll succeeded
Returns: 2 if the target was immune to the save type specified

**Parameters:**

- `oCreature`: `object`
- `nDC`: `int`
- `nSaveType`: `int` (default: `0`)
- `oSaveVersus`: `object` (default: `0`)

**Returns:** `int`

<a id="getspellsavedc"></a>

#### `GetSpellSaveDC()` - Routine 111

Get the DC to save against for a spell (10 + spell level + relevant ability
bonus).  This can be called by a creature or by an Area of Effect object.

**Returns:** `int`

<a id="magicaleffect"></a>

#### `MagicalEffect(eEffect)` - Routine 112

Set the subtype of eEffect to Magical and return eEffect.
(Effects default to magical if the subtype is not set)

**Parameters:**

- `eEffect`: `effect`

**Returns:** `effect`

<a id="supernaturaleffect"></a>

#### `SupernaturalEffect(eEffect)` - Routine 113

Set the subtype of eEffect to Supernatural and return eEffect.
(Effects default to magical if the subtype is not set)

**Parameters:**

- `eEffect`: `effect`

**Returns:** `effect`

<a id="extraordinaryeffect"></a>

#### `ExtraordinaryEffect(eEffect)` - Routine 114

Set the subtype of eEffect to Extraordinary and return eEffect.
(Effects default to magical if the subtype is not set)

**Parameters:**

- `eEffect`: `effect`

**Returns:** `effect`

<a id="getac"></a>

#### `GetAC(oObject, nForFutureUse=0)` - Routine 116

If oObject is a creature, this will return that creature's armour class
If oObject is an item, door or placeable, this will return zero.
- nForFutureUse: this parameter is not currently used
* Return value if oObject is not a creature, item, door or placeable: -1

**Parameters:**

- `oObject`: `object`
- `nForFutureUse`: `int` (default: `0`)

**Returns:** `int`

<a id="roundstoseconds"></a>

#### `RoundsToSeconds(nRounds)` - Routine 121

Convert nRounds into a number of seconds
A round is always 6.0 seconds

**Parameters:**

- `nRounds`: `int`

**Returns:** `float`

<a id="hourstoseconds"></a>

#### `HoursToSeconds(nHours)` - Routine 122

Convert nHours into a number of seconds

**Parameters:**

- `nHours`: `int`

**Returns:** `float`

<a id="turnstoseconds"></a>

#### `TurnsToSeconds(nTurns)` - Routine 123

Convert nTurns into a number of seconds
A turn is always 60.0 seconds

**Parameters:**

- `nTurns`: `int`

**Returns:** `float`

<a id="getfirstobjectinshape"></a>

#### `GetFirstObjectInShape(nShape, fSize, lTarget, bLineOfSight=0, nObjectFilter=1, vOrigin=0.0 0.0 0.0)` - Routine 128

Get the first object in nShape
- nShape: SHAPE_*
- fSize:
-> If nShape == SHAPE_SPHERE, this is the radius of the sphere
-> If nShape == SHAPE_SPELLCYLINDER, this is the radius of the cylinder
-> If nShape == SHAPE_CONE, this is the widest radius of the cone
-> If nShape == SHAPE_CUBE, this is half the length of one of the sides of
the cube
- lTarget: This is the centre of the effect, usually GetSpellTargetPosition(),
or the end of a cylinder or cone.
- bLineOfSight: This controls whether to do a line-of-sight check on the
object returned.
(This can be used to ensure that spell effects do not go through walls.)
- nObjectFilter: This allows you to filter out undesired object types, using
bitwise "or".
For example, to return only creatures and doors, the value for this
parameter would be OBJECT_TYPE_CREATURE | OBJECT_TYPE_DOOR
- vOrigin: This is only used for cylinders and cones, and specifies the
origin of the effect(normally the spell-caster's position).
Return value on error: OBJECT_INVALID

**Parameters:**

- `nShape`: `int`
- `fSize`: `float`
- `lTarget`: `location`
- `bLineOfSight`: `int` (default: `0`)
- `nObjectFilter`: `int` (default: `1`)
- `vOrigin`: `vector` (default: `0.0 0.0 0.0`)

**Returns:** `object`

<a id="getnextobjectinshape"></a>

#### `GetNextObjectInShape(nShape, fSize, lTarget, bLineOfSight=0, nObjectFilter=1, vOrigin=0.0 0.0 0.0)` - Routine 129

Get the next object in nShape
- nShape: SHAPE_*
- fSize:
-> If nShape == SHAPE_SPHERE, this is the radius of the sphere
-> If nShape == SHAPE_SPELLCYLINDER, this is the radius of the cylinder
-> If nShape == SHAPE_CONE, this is the widest radius of the cone
-> If nShape == SHAPE_CUBE, this is half the length of one of the sides of
the cube
- lTarget: This is the centre of the effect, usually GetSpellTargetPosition(),
or the end of a cylinder or cone.
- bLineOfSight: This controls whether to do a line-of-sight check on the
object returned. (This can be used to ensure that spell effects do not go
through walls.)
- nObjectFilter: This allows you to filter out undesired object types, using
bitwise "or". For example, to return only creatures and doors, the value for
this parameter would be OBJECT_TYPE_CREATURE | OBJECT_TYPE_DOOR
- vOrigin: This is only used for cylinders and cones, and specifies the origin
of the effect (normally the spell-caster's position).
Return value on error: OBJECT_INVALID

**Parameters:**

- `nShape`: `int`
- `fSize`: `float`
- `lTarget`: `location`
- `bLineOfSight`: `int` (default: `0`)
- `nObjectFilter`: `int` (default: `1`)
- `vOrigin`: `vector` (default: `0.0 0.0 0.0`)

**Returns:** `object`

<a id="signalevent"></a>

#### `SignalEvent(oObject, evToRun)` - Routine 131

Cause oObject to run evToRun

**Parameters:**

- `oObject`: `object`
- `evToRun`: `event`

<a id="eventuserdefined"></a>

#### `EventUserDefined(nUserDefinedEventNumber)` - Routine 132

Create an event of the type nUserDefinedEventNumber

**Parameters:**

- `nUserDefinedEventNumber`: `int`

**Returns:** `event`

<a id="vectornormalize"></a>

#### `VectorNormalize(vVector)` - Routine 137

Normalize vVector

**Parameters:**

- `vVector`: `vector`

**Returns:** `vector`

<a id="printvector"></a>

#### `PrintVector(vVector, bPrepend)` - Routine 141

Output vVector to the logfile.
- vVector
- bPrepend: if this is TRUE, the message will be prefixed with "PRINTVECTOR:"

**Parameters:**

- `vVector`: `vector`
- `bPrepend`: `int`

<a id="vector"></a>

#### `Vector(x=0.0, y=0.0, z=0.0)` - Routine 142

Create a vector with the specified values for x, y and z

**Parameters:**

- `x`: `float` (default: `0.0`)
- `y`: `float` (default: `0.0`)
- `z`: `float` (default: `0.0`)

**Returns:** `vector`

<a id="angletovector"></a>

#### `AngleToVector(fAngle)` - Routine 144

Convert fAngle to a vector

**Parameters:**

- `fAngle`: `float`

**Returns:** `vector`

<a id="vectortoangle"></a>

#### `VectorToAngle(vVector)` - Routine 145

Convert vVector to an angle

**Parameters:**

- `vVector`: `vector`

**Returns:** `float`

<a id="touchattackmelee"></a>

#### `TouchAttackMelee(oTarget, bDisplayFeedback=1)` - Routine 146

The caller will perform a Melee Touch Attack on oTarget
This is not an action, and it assumes the caller is already within range of
oTarget
* Returns 0 on a miss, 1 on a hit and 2 on a critical hit

**Parameters:**

- `oTarget`: `object`
- `bDisplayFeedback`: `int` (default: `1`)

**Returns:** `int`

<a id="touchattackranged"></a>

#### `TouchAttackRanged(oTarget, bDisplayFeedback=1)` - Routine 147

The caller will perform a Ranged Touch Attack on oTarget
* Returns 0 on a miss, 1 on a hit and 2 on a critical hit

**Parameters:**

- `oTarget`: `object`
- `bDisplayFeedback`: `int` (default: `1`)

**Returns:** `int`

<a id="setreturnstrref"></a>

#### `SetReturnStrref(bShow, srStringRef=0, srReturnQueryStrRef=0)` - Routine 152

SetReturnStrref
This function will turn on/off the display of the 'return to ebon hawk' option
on the map screen and allow the string to be changed to an arbitrary string ref
srReturnQueryStrRef is the string ref that will be displayed in the query pop
up confirming that you wish to return to the specified location.

**Parameters:**

- `bShow`: `int`
- `srStringRef`: `int` (default: `0`)
- `srReturnQueryStrRef`: `int` (default: `0`)

<a id="setcommandable"></a>

#### `SetCommandable(bCommandable, oTarget=0)` - Routine 162

Set whether oTarget's action stack can be modified

**Parameters:**

- `bCommandable`: `int`
- `oTarget`: `object` (default: `0`)

<a id="getcommandable"></a>

#### `GetCommandable(oTarget=0)` - Routine 163

Determine whether oTarget's action stack can be modified.

**Parameters:**

- `oTarget`: `object` (default: `0`)

**Returns:** `int`

<a id="gethitdice"></a>

#### `GetHitDice(oCreature)` - Routine 166

Get the number of hitdice for oCreature.
* Return value if oCreature is not a valid creature: 0

**Parameters:**

- `oCreature`: `object`

**Returns:** `int`

<a id="resistforce"></a>

#### `ResistForce(oSource, oTarget)` - Routine 169

Do a Force Resistance check between oSource and oTarget, returning TRUE if
the force was resisted.
* Return value if oSource or oTarget is an invalid object: FALSE

**Parameters:**

- `oSource`: `object`
- `oTarget`: `object`

**Returns:** `int`

<a id="changefaction"></a>

#### `ChangeFaction(oObjectToChangeFaction, oMemberOfFactionToJoin)` - Routine 173

Make oObjectToChangeFaction join the faction of oMemberOfFactionToJoin.
NB. ** This will only work for two NPCs **

**Parameters:**

- `oObjectToChangeFaction`: `object`
- `oMemberOfFactionToJoin`: `object`

<a id="getislistening"></a>

#### `GetIsListening(oObject)` - Routine 174

* Returns TRUE if oObject is listening for something

**Parameters:**

- `oObject`: `object`

**Returns:** `int`

<a id="setlistening"></a>

#### `SetListening(oObject, bValue)` - Routine 175

Set whether oObject is listening.

**Parameters:**

- `oObject`: `object`
- `bValue`: `int`

<a id="setlistenpattern"></a>

#### `SetListenPattern(oObject, sPattern, nNumber=0)` - Routine 176

Set the string for oObject to listen for.
Note: this does not set oObject to be listening.

**Parameters:**

- `oObject`: `object`
- `sPattern`: `string`
- `nNumber`: `int` (default: `0`)

<a id="teststringagainstpattern"></a>

#### `TestStringAgainstPattern(sPattern, sStringToTest)` - Routine 177

* Returns TRUE if sStringToTest matches sPattern.

**Parameters:**

- `sPattern`: `string`
- `sStringToTest`: `string`

**Returns:** `int`

<a id="getmatchedsubstring"></a>

#### `GetMatchedSubstring(nString)` - Routine 178

Get the appropriate matched string (this should only be used in
OnConversation scripts).
* Returns the appropriate matched string, otherwise returns ""

**Parameters:**

- `nString`: `int`

**Returns:** `string`

<a id="getmatchedsubstringscount"></a>

#### `GetMatchedSubstringsCount()` - Routine 179

Get the number of string parameters available.
* Returns -1 if no string matched (this could be because of a dialogue event)

**Returns:** `int`

<a id="getfactionweakestmember"></a>

#### `GetFactionWeakestMember(oFactionMember=0, bMustBeVisible=1)` - Routine 181

Get the weakest member of oFactionMember's faction.
* Returns OBJECT_INVALID if oFactionMember's faction is invalid.

**Parameters:**

- `oFactionMember`: `object` (default: `0`)
- `bMustBeVisible`: `int` (default: `1`)

**Returns:** `object`

<a id="getfactionstrongestmember"></a>

#### `GetFactionStrongestMember(oFactionMember=0, bMustBeVisible=1)` - Routine 182

Get the strongest member of oFactionMember's faction.
* Returns OBJECT_INVALID if oFactionMember's faction is invalid.

**Parameters:**

- `oFactionMember`: `object` (default: `0`)
- `bMustBeVisible`: `int` (default: `1`)

**Returns:** `object`

<a id="getfactionmostdamagedmember"></a>

#### `GetFactionMostDamagedMember(oFactionMember=0, bMustBeVisible=1)` - Routine 183

Get the member of oFactionMember's faction that has taken the most hit points
of damage.
* Returns OBJECT_INVALID if oFactionMember's faction is invalid.

**Parameters:**

- `oFactionMember`: `object` (default: `0`)
- `bMustBeVisible`: `int` (default: `1`)

**Returns:** `object`

<a id="getfactionleastdamagedmember"></a>

#### `GetFactionLeastDamagedMember(oFactionMember=0, bMustBeVisible=1)` - Routine 184

Get the member of oFactionMember's faction that has taken the fewest hit
points of damage.
* Returns OBJECT_INVALID if oFactionMember's faction is invalid.

**Parameters:**

- `oFactionMember`: `object` (default: `0`)
- `bMustBeVisible`: `int` (default: `1`)

**Returns:** `object`

<a id="getfactiongold"></a>

#### `GetFactionGold(oFactionMember)` - Routine 185

Get the amount of gold held by oFactionMember's faction.
* Returns -1 if oFactionMember's faction is invalid.

**Parameters:**

- `oFactionMember`: `object`

**Returns:** `int`

<a id="getfactionaveragereputation"></a>

#### `GetFactionAverageReputation(oSourceFactionMember, oTarget)` - Routine 186

Get an integer between 0 and 100 (inclusive) that represents how
oSourceFactionMember's faction feels about oTarget.
* Return value on error: -1

**Parameters:**

- `oSourceFactionMember`: `object`
- `oTarget`: `object`

**Returns:** `int`

<a id="getfactionaveragelevel"></a>

#### `GetFactionAverageLevel(oFactionMember)` - Routine 189

Get the average level of the members of the faction.
* Return value on error: -1

**Parameters:**

- `oFactionMember`: `object`

**Returns:** `int`

<a id="getfactionaveragexp"></a>

#### `GetFactionAverageXP(oFactionMember)` - Routine 190

Get the average XP of the members of the faction.
* Return value on error: -1

**Parameters:**

- `oFactionMember`: `object`

**Returns:** `int`

<a id="getfactionmostfrequentclass"></a>

#### `GetFactionMostFrequentClass(oFactionMember)` - Routine 191

Get the most frequent class in the faction - this can be compared with the
constants CLASS_TYPE_*.
* Return value on error: -1

**Parameters:**

- `oFactionMember`: `object`

**Returns:** `int`

<a id="getfactionworstac"></a>

#### `GetFactionWorstAC(oFactionMember=0, bMustBeVisible=1)` - Routine 192

Get the object faction member with the lowest armour class.
* Returns OBJECT_INVALID if oFactionMember's faction is invalid.

**Parameters:**

- `oFactionMember`: `object` (default: `0`)
- `bMustBeVisible`: `int` (default: `1`)

**Returns:** `object`

<a id="getfactionbestac"></a>

#### `GetFactionBestAC(oFactionMember=0, bMustBeVisible=1)` - Routine 193

Get the object faction member with the highest armour class.
* Returns OBJECT_INVALID if oFactionMember's faction is invalid.

**Parameters:**

- `oFactionMember`: `object` (default: `0`)
- `bMustBeVisible`: `int` (default: `1`)

**Returns:** `object`

<a id="getlistenpatternnumber"></a>

#### `GetListenPatternNumber()` - Routine 195

In an onConversation script this gets the number of the string pattern
matched (the one that triggered the script).
* Returns -1 if no string matched

**Returns:** `int`

<a id="getwaypointbytag"></a>

#### `GetWaypointByTag(sWaypointTag)` - Routine 197

Get the first waypoint with the specified tag.
* Returns OBJECT_INVALID if the waypoint cannot be found.

**Parameters:**

- `sWaypointTag`: `string`

**Returns:** `object`

<a id="adjustreputation"></a>

#### `AdjustReputation(oTarget, oSourceFactionMember, nAdjustment)` - Routine 209

Adjust how oSourceFactionMember's faction feels about oTarget by the
specified amount.
Note: This adjusts Faction Reputation, how the entire faction that
oSourceFactionMember is in, feels about oTarget.
* No return value

**Parameters:**

- `oTarget`: `object`
- `oSourceFactionMember`: `object`
- `nAdjustment`: `int`

<a id="getgoingtobeattackedby"></a>

#### `GetGoingToBeAttackedBy(oTarget)` - Routine 211

Get the creature that is going to attack oTarget.
Note: This value is cleared out at the end of every combat round and should
not be used in any case except when getting a "going to be attacked" shout
from the master creature (and this creature is a henchman)
* Returns OBJECT_INVALID if oTarget is not a valid creature.

**Parameters:**

- `oTarget`: `object`

**Returns:** `object`

<a id="feettometers"></a>

#### `FeetToMeters(fFeet)` - Routine 218

Convert fFeet into a number of meters.

**Parameters:**

- `fFeet`: `float`

**Returns:** `float`

<a id="yardstometers"></a>

#### `YardsToMeters(fYards)` - Routine 219

Convert fYards into a number of meters.

**Parameters:**

- `fYards`: `float`

**Returns:** `float`

<a id="inttofloat"></a>

#### `IntToFloat(nInteger)` - Routine 230

Convert nInteger into a floating point number.

**Parameters:**

- `nInteger`: `int`

**Returns:** `float`

<a id="floattoint"></a>

#### `FloatToInt(fFloat)` - Routine 231

Convert fFloat into the nearest integer.

**Parameters:**

- `fFloat`: `float`

**Returns:** `int`

<a id="stringtoint"></a>

#### `StringToInt(sNumber)` - Routine 232

Convert sNumber into an integer.

**Parameters:**

- `sNumber`: `string`

**Returns:** `int`

<a id="stringtofloat"></a>

#### `StringToFloat(sNumber)` - Routine 233

Convert sNumber into a floating point number.

**Parameters:**

- `sNumber`: `string`

**Returns:** `float`

<a id="getstringbystrref"></a>

#### `GetStringByStrRef(nStrRef)` - Routine 239

Get a string from the talk table using nStrRef.

**Parameters:**

- `nStrRef`: `int`

**Returns:** `string`

<a id="eventspellcastat"></a>

#### `EventSpellCastAt(oCaster, nSpell, bHarmful=1)` - Routine 244

Create an event which triggers the "SpellCastAt" script

**Parameters:**

- `oCaster`: `object`
- `nSpell`: `int`
- `bHarmful`: `int` (default: `1`)

**Returns:** `event`

<a id="getuserdefinedeventnumber"></a>

#### `GetUserDefinedEventNumber()` - Routine 247

This is for use in a user-defined script, it gets the event number.

**Returns:** `int`

<a id="randomname"></a>

#### `RandomName()` - Routine 249

Generate a random name.

**Returns:** `string`

<a id="getloadfromsavegame"></a>

#### `GetLoadFromSaveGame()` - Routine 251

Returns whether this script is being run
while a load game is in progress

**Returns:** `int`

<a id="getlastspeaker"></a>

#### `GetLastSpeaker()` - Routine 254

Use this in a conversation script to get the person with whom you are conversing.
* Returns OBJECT_INVALID if the caller is not a valid creature.

**Returns:** `object`

<a id="getlastperceived"></a>

#### `GetLastPerceived()` - Routine 256

Use this in an OnPerception script to get the object that was perceived.
* Returns OBJECT_INVALID if the caller is not a valid creature.

**Returns:** `object`

<a id="getlastperceptionheard"></a>

#### `GetLastPerceptionHeard()` - Routine 257

Use this in an OnPerception script to determine whether the object that was
perceived was heard.

**Returns:** `int`

<a id="getlastperceptioninaudible"></a>

#### `GetLastPerceptionInaudible()` - Routine 258

Use this in an OnPerception script to determine whether the object that was
perceived has become inaudible.

**Returns:** `int`

<a id="getlastperceptionseen"></a>

#### `GetLastPerceptionSeen()` - Routine 259

Use this in an OnPerception script to determine whether the object that was
perceived was seen.

**Returns:** `int`

<a id="getlastclosedby"></a>

#### `GetLastClosedBy()` - Routine 260

Use this in an OnClosed script to get the object that closed the door or placeable.
* Returns OBJECT_INVALID if the caller is not a valid door or placeable.

**Returns:** `object`

<a id="getlastperceptionvanished"></a>

#### `GetLastPerceptionVanished()` - Routine 261

Use this in an OnPerception script to determine whether the object that was
perceived has vanished.

**Returns:** `int`

<a id="getareaofeffectcreator"></a>

#### `GetAreaOfEffectCreator(oAreaOfEffectObject=0)` - Routine 264

This returns the creator of oAreaOfEffectObject.
* Returns OBJECT_INVALID if oAreaOfEffectObject is not a valid Area of Effect object.

**Parameters:**

- `oAreaOfEffectObject`: `object` (default: `0`)

**Returns:** `object`

<a id="showlevelupgui"></a>

#### `ShowLevelUpGUI()` - Routine 265

Brings up the level up GUI for the player.  The GUI will only show up
if the player has gained enough experience points to level up.
* Returns TRUE if the GUI was successfully brought up; FALSE if not.

**Returns:** `int`

<a id="getbuttonmashcheck"></a>

#### `GetButtonMashCheck()` - Routine 267

GetButtonMashCheck
This function returns whether the button mash check, used for the combat tutorial, is on

**Returns:** `int`

<a id="setbuttonmashcheck"></a>

#### `SetButtonMashCheck(nCheck)` - Routine 268

SetButtonMashCheck
This function sets the button mash check variable, and is used for turning the check on and off

**Parameters:**

- `nCheck`: `int`

<a id="objecttostring"></a>

#### `ObjectToString(oObject)` - Routine 272

Convert oObject into a hexadecimal string.

**Parameters:**

- `oObject`: `object`

**Returns:** `string`

<a id="getisimmune"></a>

#### `GetIsImmune(oCreature, nImmunityType, oVersus=1)` - Routine 274

- oCreature
- nImmunityType: IMMUNITY_TYPE_*
- oVersus: if this is specified, then we also check for the race and
alignment of oVersus
* Returns TRUE if oCreature has immunity of type nImmunity versus oVersus.

**Parameters:**

- `oCreature`: `object`
- `nImmunityType`: `int`
- `oVersus`: `object` (default: `1`)

**Returns:** `int`

<a id="getencounteractive"></a>

#### `GetEncounterActive(oEncounter=0)` - Routine 276

Determine whether oEncounter is active.

**Parameters:**

- `oEncounter`: `object` (default: `0`)

**Returns:** `int`

<a id="setencounteractive"></a>

#### `SetEncounterActive(nNewValue, oEncounter=0)` - Routine 277

Set oEncounter's active state to nNewValue.
- nNewValue: TRUE/FALSE
- oEncounter

**Parameters:**

- `nNewValue`: `int`
- `oEncounter`: `object` (default: `0`)

<a id="getencounterspawnsmax"></a>

#### `GetEncounterSpawnsMax(oEncounter=0)` - Routine 278

Get the maximum number of times that oEncounter will spawn.

**Parameters:**

- `oEncounter`: `object` (default: `0`)

**Returns:** `int`

<a id="setencounterspawnsmax"></a>

#### `SetEncounterSpawnsMax(nNewValue, oEncounter=0)` - Routine 279

Set the maximum number of times that oEncounter can spawn

**Parameters:**

- `nNewValue`: `int`
- `oEncounter`: `object` (default: `0`)

<a id="getencounterspawnscurrent"></a>

#### `GetEncounterSpawnsCurrent(oEncounter=0)` - Routine 280

Get the number of times that oEncounter has spawned so far

**Parameters:**

- `oEncounter`: `object` (default: `0`)

**Returns:** `int`

<a id="setencounterspawnscurrent"></a>

#### `SetEncounterSpawnsCurrent(nNewValue, oEncounter=0)` - Routine 281

Set the number of times that oEncounter has spawned so far

**Parameters:**

- `nNewValue`: `int`
- `oEncounter`: `object` (default: `0`)

<a id="getobjectseen"></a>

#### `GetObjectSeen(oTarget, oSource=0)` - Routine 289

Determine whether oSource sees oTarget.

**Parameters:**

- `oTarget`: `object`
- `oSource`: `object` (default: `0`)

**Returns:** `int`

<a id="getobjectheard"></a>

#### `GetObjectHeard(oTarget, oSource=0)` - Routine 290

Determine whether oSource hears oTarget.

**Parameters:**

- `oTarget`: `object`
- `oSource`: `object` (default: `0`)

**Returns:** `int`

<a id="getlastplayerdied"></a>

#### `GetLastPlayerDied()` - Routine 291

Use this in an OnPlayerDeath module script to get the last player that died.

**Returns:** `object`

<a id="setencounterdifficulty"></a>

#### `SetEncounterDifficulty(nEncounterDifficulty, oEncounter=0)` - Routine 296

Set the difficulty level of oEncounter.
- nEncounterDifficulty: ENCOUNTER_DIFFICULTY_*
- oEncounter

**Parameters:**

- `nEncounterDifficulty`: `int`
- `oEncounter`: `object` (default: `0`)

<a id="getencounterdifficulty"></a>

#### `GetEncounterDifficulty(oEncounter=0)` - Routine 297

Get the difficulty level of oEncounter.

**Parameters:**

- `oEncounter`: `object` (default: `0`)

**Returns:** `int`

<a id="talentspell"></a>

#### `TalentSpell(nSpell)` - Routine 301

Create a Spell Talent.
- nSpell: SPELL_*

**Parameters:**

- `nSpell`: `int`

**Returns:** `talent`

<a id="talentfeat"></a>

#### `TalentFeat(nFeat)` - Routine 302

Create a Feat Talent.
- nFeat: FEAT_*

**Parameters:**

- `nFeat`: `int`

**Returns:** `talent`

<a id="talentskill"></a>

#### `TalentSkill(nSkill)` - Routine 303

Create a Skill Talent.
- nSkill: SKILL_*

**Parameters:**

- `nSkill`: `int`

**Returns:** `talent`

<a id="geteffectspellid"></a>

#### `GetEffectSpellId(eSpellEffect)` - Routine 305

Get the spell (SPELL_*) that applied eSpellEffect.
* Returns -1 if eSpellEffect was applied outside a spell script.

**Parameters:**

- `eSpellEffect`: `effect`

**Returns:** `int`

<a id="getcreaturehastalent"></a>

#### `GetCreatureHasTalent(tTalent, oCreature=0)` - Routine 306

Determine whether oCreature has tTalent.

**Parameters:**

- `tTalent`: `talent`
- `oCreature`: `object` (default: `0`)

**Returns:** `int`

<a id="getcreaturetalentrandom"></a>

#### `GetCreatureTalentRandom(nCategory, oCreature=0, nInclusion=0)` - Routine 307

Get a random talent of oCreature, within nCategory.
- nCategory: TALENT_CATEGORY_*
- oCreature
- nInclusion: types of talent to include

**Parameters:**

- `nCategory`: `int`
- `oCreature`: `object` (default: `0`)
- `nInclusion`: `int` (default: `0`)

**Returns:** `talent`

<a id="getcreaturetalentbest"></a>

#### `GetCreatureTalentBest(nCategory, nCRMax, oCreature=0, nInclusion=0, nExcludeType=-1, nExcludeId=-1)` - Routine 308

Get the best talent (i.e. closest to nCRMax without going over) of oCreature,
within nCategory.
- nCategory: TALENT_CATEGORY_*
- nCRMax: Challenge Rating of the talent
- oCreature
- nInclusion: types of talent to include
- nExcludeType: TALENT_TYPE_FEAT or TALENT_TYPE_FORCE, type of talent that we wish to ignore
- nExcludeId: Talent ID of the talent we wish to ignore.
A value of TALENT_EXCLUDE_ALL_OF_TYPE for this parameter will mean that all talents of
type nExcludeType are ignored.

**Parameters:**

- `nCategory`: `int`
- `nCRMax`: `int`
- `oCreature`: `object` (default: `0`)
- `nInclusion`: `int` (default: `0`)
- `nExcludeType`: `int` (default: `-1`)
- `nExcludeId`: `int` (default: `-1`)

**Returns:** `talent`

<a id="getgoldpiecevalue"></a>

#### `GetGoldPieceValue(oItem)` - Routine 311

Get the gold piece value of oItem.
* Returns 0 if oItem is not a valid item.

**Parameters:**

- `oItem`: `object`

**Returns:** `int`

<a id="getisplayableracialtype"></a>

#### `GetIsPlayableRacialType(oCreature)` - Routine 312

* Returns TRUE if oCreature is of a playable racial type.

**Parameters:**

- `oCreature`: `object`

**Returns:** `int`

<a id="jumptolocation"></a>

#### `JumpToLocation(lDestination)` - Routine 313

Jump to lDestination.  The action is added to the TOP of the action queue.

**Parameters:**

- `lDestination`: `location`

<a id="getlastattacktype"></a>

#### `GetLastAttackType(oCreature=0)` - Routine 317

Get the attack type (SPECIAL_ATTACK_*) of oCreature's last attack.
This only works when oCreature is in combat.

**Parameters:**

- `oCreature`: `object` (default: `0`)

**Returns:** `int`

<a id="getlastattackmode"></a>

#### `GetLastAttackMode(oCreature=0)` - Routine 318

Get the attack mode (COMBAT_MODE_*) of oCreature's last attack.
This only works when oCreature is in combat.

**Parameters:**

- `oCreature`: `object` (default: `0`)

**Returns:** `int`

<a id="getlastassociatecommand"></a>

#### `GetLastAssociateCommand(oAssociate=0)` - Routine 321

Get the last command (ASSOCIATE_COMMAND_*) issued to oAssociate.

**Parameters:**

- `oAssociate`: `object` (default: `0`)

**Returns:** `int`

<a id="givegoldtocreature"></a>

#### `GiveGoldToCreature(oCreature, nGP)` - Routine 322

Give nGP gold to oCreature.

**Parameters:**

- `oCreature`: `object`
- `nGP`: `int`

<a id="setlocked"></a>

#### `SetLocked(oTarget, bLocked)` - Routine 324

Set the locked state of oTarget, which can be a door or a placeable object.

**Parameters:**

- `oTarget`: `object`
- `bLocked`: `int`

<a id="getlocked"></a>

#### `GetLocked(oTarget)` - Routine 325

Get the locked state of oTarget, which can be a door or a placeable object.

**Parameters:**

- `oTarget`: `object`

**Returns:** `int`

<a id="getclickingobject"></a>

#### `GetClickingObject()` - Routine 326

Use this in a trigger's OnClick event script to get the object that last
clicked on it.
This is identical to GetEnteringObject.

**Returns:** `object`

<a id="setassociatelistenpatterns"></a>

#### `SetAssociateListenPatterns(oTarget=0)` - Routine 327

Initialise oTarget to listen for the standard Associates commands.

**Parameters:**

- `oTarget`: `object` (default: `0`)

<a id="getlastweaponused"></a>

#### `GetLastWeaponUsed(oCreature)` - Routine 328

Get the last weapon that oCreature used in an attack.
* Returns OBJECT_INVALID if oCreature did not attack, or has no weapon equipped.

**Parameters:**

- `oCreature`: `object`

**Returns:** `object`

<a id="getlastusedby"></a>

#### `GetLastUsedBy()` - Routine 330

Get the last object that used the placeable object that is calling this function.
* Returns OBJECT_INVALID if it is called by something other than a placeable or
a door.

**Returns:** `object`

<a id="getblockingdoor"></a>

#### `GetBlockingDoor()` - Routine 336

Get the last blocking door encountered by the caller of this function.
* Returns OBJECT_INVALID if the caller is not a valid creature.

**Returns:** `object`

<a id="getisdooractionpossible"></a>

#### `GetIsDoorActionPossible(oTargetDoor, nDoorAction)` - Routine 337

- oTargetDoor
- nDoorAction: DOOR_ACTION_*
* Returns TRUE if nDoorAction can be performed on oTargetDoor.

**Parameters:**

- `oTargetDoor`: `object`
- `nDoorAction`: `int`

**Returns:** `int`

<a id="dodooraction"></a>

#### `DoDoorAction(oTargetDoor, nDoorAction)` - Routine 338

Perform nDoorAction on oTargetDoor.

**Parameters:**

- `oTargetDoor`: `object`
- `nDoorAction`: `int`

<a id="getlastdisarmed"></a>

#### `GetLastDisarmed()` - Routine 347

Get the last object that disarmed the trap on the caller.
* Returns OBJECT_INVALID if the caller is not a valid placeable, trigger or
door.

**Returns:** `object`

<a id="getlastdisturbed"></a>

#### `GetLastDisturbed()` - Routine 348

Get the last object that disturbed the inventory of the caller.
* Returns OBJECT_INVALID if the caller is not a valid creature or placeable.

**Returns:** `object`

<a id="getlastlocked"></a>

#### `GetLastLocked()` - Routine 349

Get the last object that locked the caller.
* Returns OBJECT_INVALID if the caller is not a valid door or placeable.

**Returns:** `object`

<a id="getlastunlocked"></a>

#### `GetLastUnlocked()` - Routine 350

Get the last object that unlocked the caller.
* Returns OBJECT_INVALID if the caller is not a valid door or placeable.

**Returns:** `object`

<a id="getinventorydisturbtype"></a>

#### `GetInventoryDisturbType()` - Routine 352

Get the type of disturbance (INVENTORY_DISTURB_*) that caused the caller's
OnInventoryDisturbed script to fire.  This will only work for creatures and
placeables.

**Returns:** `int`

<a id="showupgradescreen"></a>

#### `ShowUpgradeScreen(oItem=1)` - Routine 354

Displays the upgrade screen where the player can modify weapons and armor

**Parameters:**

- `oItem`: `object` (default: `1`)

<a id="versusracialtypeeffect"></a>

#### `VersusRacialTypeEffect(eEffect, nRacialType)` - Routine 356

Set eEffect to be versus nRacialType.
- eEffect
- nRacialType: RACIAL_TYPE_*

**Parameters:**

- `eEffect`: `effect`
- `nRacialType`: `int`

**Returns:** `effect`

<a id="versustrapeffect"></a>

#### `VersusTrapEffect(eEffect)` - Routine 357

Set eEffect to be versus traps.

**Parameters:**

- `eEffect`: `effect`

**Returns:** `effect`

<a id="getistalentvalid"></a>

#### `GetIsTalentValid(tTalent)` - Routine 359

* Returns TRUE if tTalent is valid.

**Parameters:**

- `tTalent`: `talent`

**Returns:** `int`

<a id="getattemptedattacktarget"></a>

#### `GetAttemptedAttackTarget()` - Routine 361

Get the target that the caller attempted to attack - this should be used in
conjunction with GetAttackTarget(). This value is set every time an attack is
made, and is reset at the end of combat.
* Returns OBJECT_INVALID if the caller is not a valid creature.

**Returns:** `object`

<a id="gettypefromtalent"></a>

#### `GetTypeFromTalent(tTalent)` - Routine 362

Get the type (TALENT_TYPE_*) of tTalent.

**Parameters:**

- `tTalent`: `talent`

**Returns:** `int`

<a id="getidfromtalent"></a>

#### `GetIdFromTalent(tTalent)` - Routine 363

Get the ID of tTalent.  This could be a SPELL_*, FEAT_* or SKILL_*.

**Parameters:**

- `tTalent`: `talent`

**Returns:** `int`

<a id="playpazaak"></a>

#### `PlayPazaak(sEndScript, nMaxWager, bShowTutorial=0, oOpponent=1)` - Routine 364

Starts a game of pazaak.
- nOpponentPazaakDeck: Index into PazaakDecks.2da; specifies which deck the opponent will use.
- sEndScript: Script to be run when game finishes.
- nMaxWager: Max player wager.  If <= 0, the player's credits won't be modified by the result of the game and the wager screen will not show up.
- bShowTutorial: Plays in tutorial mode (nMaxWager should be 0).

**Parameters:**

- `sEndScript`: `string`
- `nMaxWager`: `int`
- `bShowTutorial`: `int` (default: `0`)
- `oOpponent`: `object` (default: `1`)

<a id="getlastpazaakresult"></a>

#### `GetLastPazaakResult()` - Routine 365

Returns result of last Pazaak game.  Should be used only in an EndScript sent to PlayPazaak.
* Returns 0 if player loses, 1 if player wins.

**Returns:** `int`

<a id="displayfeedbacktext"></a>

#### `DisplayFeedBackText(oCreature, nTextConstant)` - Routine 366

displays a feed back string for the object spicified and the constant
repersents the string to be displayed see:FeedBackText.2da

**Parameters:**

- `oCreature`: `object`
- `nTextConstant`: `int`

<a id="addjournalquestentry"></a>

#### `AddJournalQuestEntry(szPlotID, nState, bAllowOverrideHigher=0)` - Routine 367

Add a journal quest entry to the player.
- szPlotID: the plot identifier used in the toolset's Journal Editor
- nState: the state of the plot as seen in the toolset's Journal Editor
- bAllowOverrideHigher: If this is TRUE, you can set the state to a lower
number than the one it is currently on

**Parameters:**

- `szPlotID`: `string`
- `nState`: `int`
- `bAllowOverrideHigher`: `int` (default: `0`)

<a id="removejournalquestentry"></a>

#### `RemoveJournalQuestEntry(szPlotID)` - Routine 368

Remove a journal quest entry from the player.
- szPlotID: the plot identifier used in the toolset's Journal Editor

**Parameters:**

- `szPlotID`: `string`

<a id="getjournalentry"></a>

#### `GetJournalEntry(szPlotID)` - Routine 369

Gets the State value of a journal quest.  Returns 0 if no quest entry has been added for this szPlotID.
- szPlotID: the plot identifier used in the toolset's Journal Editor

**Parameters:**

- `szPlotID`: `string`

**Returns:** `int`

<a id="playrumblepattern"></a>

#### `PlayRumblePattern(nPattern)` - Routine 370

PlayRumblePattern
Starts a defined rumble pattern playing

**Parameters:**

- `nPattern`: `int`

**Returns:** `int`

<a id="stoprumblepattern"></a>

#### `StopRumblePattern(nPattern)` - Routine 371

StopRumblePattern
Stops a defined rumble pattern

**Parameters:**

- `nPattern`: `int`

**Returns:** `int`

<a id="sendmessagetopc"></a>

#### `SendMessageToPC(oPlayer, szMessage)` - Routine 374

Send a server message (szMessage) to the oPlayer.

**Parameters:**

- `oPlayer`: `object`
- `szMessage`: `string`

<a id="getattemptedspelltarget"></a>

#### `GetAttemptedSpellTarget()` - Routine 375

Get the target at which the caller attempted to cast a spell.
This value is set every time a spell is cast and is reset at the end of
combat.
* Returns OBJECT_INVALID if the caller is not a valid creature.

**Returns:** `object`

<a id="getlastopenedby"></a>

#### `GetLastOpenedBy()` - Routine 376

Get the last creature that opened the caller.
* Returns OBJECT_INVALID if the caller is not a valid door or placeable.

**Returns:** `object`

<a id="openstore"></a>

#### `OpenStore(oStore, oPC, nBonusMarkUp=0, nBonusMarkDown=0)` - Routine 378

Open oStore for oPC.

**Parameters:**

- `oStore`: `object`
- `oPC`: `object`
- `nBonusMarkUp`: `int` (default: `0`)
- `nBonusMarkDown`: `int` (default: `0`)

<a id="getfirstfactionmember"></a>

#### `GetFirstFactionMember(oMemberOfFaction, bPCOnly=1)` - Routine 380

Get the first member of oMemberOfFaction's faction (start to cycle through
oMemberOfFaction's faction).
* Returns OBJECT_INVALID if oMemberOfFaction's faction is invalid.

**Parameters:**

- `oMemberOfFaction`: `object`
- `bPCOnly`: `int` (default: `1`)

**Returns:** `object`

<a id="getnextfactionmember"></a>

#### `GetNextFactionMember(oMemberOfFaction, bPCOnly=1)` - Routine 381

Get the next member of oMemberOfFaction's faction (continue to cycle through
oMemberOfFaction's faction).
* Returns OBJECT_INVALID if oMemberOfFaction's faction is invalid.

**Parameters:**

- `oMemberOfFaction`: `object`
- `bPCOnly`: `int` (default: `1`)

**Returns:** `object`

<a id="getjournalquestexperience"></a>

#### `GetJournalQuestExperience(szPlotID)` - Routine 384

Get the experience assigned in the journal editor for szPlotID.

**Parameters:**

- `szPlotID`: `string`

**Returns:** `int`

<a id="jumptoobject"></a>

#### `JumpToObject(oToJumpTo, nWalkStraightLineToPoint=1)` - Routine 385

Jump to oToJumpTo (the action is added to the top of the action queue).

**Parameters:**

- `oToJumpTo`: `object`
- `nWalkStraightLineToPoint`: `int` (default: `1`)

<a id="setmappinenabled"></a>

#### `SetMapPinEnabled(oMapPin, nEnabled)` - Routine 386

Set whether oMapPin is enabled.
- oMapPin
- nEnabled: 0=Off, 1=On

**Parameters:**

- `oMapPin`: `object`
- `nEnabled`: `int`

<a id="popupguipanel"></a>

#### `PopUpGUIPanel(oPC, nGUIPanel)` - Routine 388

Spawn a GUI panel for the client that controls oPC.
- oPC
- nGUIPanel: GUI_PANEL_*
* Nothing happens if oPC is not a player character or if an invalid value is
used for nGUIPanel.

**Parameters:**

- `oPC`: `object`
- `nGUIPanel`: `int`

<a id="addmulticlass"></a>

#### `AddMultiClass(nClassType, oSource)` - Routine 389

This allows you to add a new class to any creature object

**Parameters:**

- `nClassType`: `int`
- `oSource`: `object`

<a id="getislinkimmune"></a>

#### `GetIsLinkImmune(oTarget, eEffect)` - Routine 390

Tests a linked effect to see if the target is immune to it.
If the target is imune to any of the linked effect then he is immune to all of it

**Parameters:**

- `oTarget`: `object`
- `eEffect`: `effect`

**Returns:** `int`

<a id="setxp"></a>

#### `SetXP(oCreature, nXpAmount)` - Routine 394

Sets oCreature's experience to nXpAmount.

**Parameters:**

- `oCreature`: `object`
- `nXpAmount`: `int`

<a id="getxp"></a>

#### `GetXP(oCreature)` - Routine 395

Get oCreature's experience.

**Parameters:**

- `oCreature`: `object`

**Returns:** `int`

<a id="inttohexstring"></a>

#### `IntToHexString(nInteger)` - Routine 396

Convert nInteger to hex, returning the hex value as a string.
* Return value has the format "0x????????" where each ? will be a hex digit
(8 digits in total).

**Parameters:**

- `nInteger`: `int`

**Returns:** `string`

<a id="getisday"></a>

#### `GetIsDay()` - Routine 405

* Returns TRUE if it is currently day.

**Returns:** `int`

<a id="getisnight"></a>

#### `GetIsNight()` - Routine 406

* Returns TRUE if it is currently night.

**Returns:** `int`

<a id="getisdawn"></a>

#### `GetIsDawn()` - Routine 407

* Returns TRUE if it is currently dawn.

**Returns:** `int`

<a id="getisdusk"></a>

#### `GetIsDusk()` - Routine 408

* Returns TRUE if it is currently dusk.

**Returns:** `int`

<a id="getisencountercreature"></a>

#### `GetIsEncounterCreature(oCreature=0)` - Routine 409

* Returns TRUE if oCreature was spawned from an encounter.

**Parameters:**

- `oCreature`: `object` (default: `0`)

**Returns:** `int`

<a id="getlastplayerdying"></a>

#### `GetLastPlayerDying()` - Routine 410

Use this in an OnPlayerDying module script to get the last player who is dying.

**Returns:** `object`

<a id="getstartinglocation"></a>

#### `GetStartingLocation()` - Routine 411

Get the starting location of the module.

**Returns:** `location`

<a id="changetostandardfaction"></a>

#### `ChangeToStandardFaction(oCreatureToChange, nStandardFaction)` - Routine 412

Make oCreatureToChange join one of the standard factions.
** This will only work on an NPC **
- nStandardFaction: STANDARD_FACTION_*

**Parameters:**

- `oCreatureToChange`: `object`
- `nStandardFaction`: `int`

<a id="getgold"></a>

#### `GetGold(oTarget=0)` - Routine 418

Get the amount of gold possessed by oTarget.

**Parameters:**

- `oTarget`: `object` (default: `0`)

**Returns:** `int`

<a id="getlastrespawnbuttonpresser"></a>

#### `GetLastRespawnButtonPresser()` - Routine 419

Use this in an OnRespawnButtonPressed module script to get the object id of
the player who last pressed the respawn button.

**Returns:** `object`

<a id="setlightsaberpowered"></a>

#### `SetLightsaberPowered(oCreature, bOverride, bPowered=1, bShowTransition=0)` - Routine 421

SetLightsaberPowered
Allows a script to set the state of the lightsaber.  This will override any
game determined lightsaber powerstates.

**Parameters:**

- `oCreature`: `object`
- `bOverride`: `int`
- `bPowered`: `int` (default: `1`)
- `bShowTransition`: `int` (default: `0`)

<a id="getisopen"></a>

#### `GetIsOpen(oObject)` - Routine 443

* Returns TRUE if oObject (which is a placeable or a door) is currently open.

**Parameters:**

- `oObject`: `object`

**Returns:** `int`

<a id="takegoldfromcreature"></a>

#### `TakeGoldFromCreature(nAmount, oCreatureToTakeFrom, bDestroy=0)` - Routine 444

Take nAmount of gold from oCreatureToTakeFrom.
- nAmount
- oCreatureToTakeFrom: If this is not a valid creature, nothing will happen.
- bDestroy: If this is TRUE, the caller will not get the gold.  Instead, the
gold will be destroyed and will vanish from the game.

**Parameters:**

- `nAmount`: `int`
- `oCreatureToTakeFrom`: `object`
- `bDestroy`: `int` (default: `0`)

<a id="setdialogplaceablecamera"></a>

#### `SetDialogPlaceableCamera(nCameraId)` - Routine 461

Cut immediately to placeable camera 'nCameraId' during dialog.  nCameraId must be
an existing Placeable Camera ID.  Function only works during Dialog.

**Parameters:**

- `nCameraId`: `int`

<a id="getsolomode"></a>

#### `GetSoloMode()` - Routine 462

Returns: TRUE if the player is in 'solo mode' (ie. the party is not supposed to follow the player).
FALSE otherwise.

**Returns:** `int`

<a id="getmaxstealthxp"></a>

#### `GetMaxStealthXP()` - Routine 464

Returns the maximum amount of stealth xp available in the area.

**Returns:** `int`

<a id="setmaxstealthxp"></a>

#### `SetMaxStealthXP(nMax)` - Routine 468

Set the maximum amount of stealth xp available in the area.

**Parameters:**

- `nMax`: `int`

<a id="getcurrentstealthxp"></a>

#### `GetCurrentStealthXP()` - Routine 474

Returns the current amount of stealth xp available in the area.

**Returns:** `int`

<a id="surrendertoenemies"></a>

#### `SurrenderToEnemies()` - Routine 476

Use this on an NPC to cause all creatures within a 10-metre radius to stop
what they are doing and sets the NPC's enemies within this range to be
neutral towards the NPC. If this command is run on a PC or an object that is
not a creature, nothing will happen.

<a id="setcurrentstealthxp"></a>

#### `SetCurrentStealthXP(nCurrent)` - Routine 478

Set the current amount of stealth xp available in the area.

**Parameters:**

- `nCurrent`: `int`

<a id="getcreaturesize"></a>

#### `GetCreatureSize(oCreature)` - Routine 479

Get the size (CREATURE_SIZE_*) of oCreature.

**Parameters:**

- `oCreature`: `object`

**Returns:** `int`

<a id="awardstealthxp"></a>

#### `AwardStealthXP(oTarget)` - Routine 480

Award the stealth xp to the given oTarget.  This will only work on creatures.

**Parameters:**

- `oTarget`: `object`

<a id="getstealthxpenabled"></a>

#### `GetStealthXPEnabled()` - Routine 481

Returns whether or not the stealth xp bonus is enabled (ie. whether or not
AwardStealthXP() will actually award any available stealth xp).

**Returns:** `int`

<a id="setstealthxpenabled"></a>

#### `SetStealthXPEnabled(bEnabled)` - Routine 482

Sets whether or not the stealth xp bonus is enabled (ie. whether or not
AwardStealthXP() will actually award any available stealth xp).

**Parameters:**

- `bEnabled`: `int`

<a id="getlasttrapdetected"></a>

#### `GetLastTrapDetected(oTarget=0)` - Routine 486

Get the last trap detected by oTarget.
* Return value on error: OBJECT_INVALID

**Parameters:**

- `oTarget`: `object` (default: `0`)

**Returns:** `object`

<a id="getnearesttraptoobject"></a>

#### `GetNearestTrapToObject(oTarget=0, nTrapDetected=1)` - Routine 488

Get the trap nearest to oTarget.
Note : "trap objects" are actually any trigger, placeable or door that is
trapped in oTarget's area.
- oTarget
- nTrapDetected: if this is TRUE, the trap returned has to have been detected
by oTarget.

**Parameters:**

- `oTarget`: `object` (default: `0`)
- `nTrapDetected`: `int` (default: `1`)

**Returns:** `object`

<a id="getattemptedmovementtarget"></a>

#### `GetAttemptedMovementTarget()` - Routine 489

the will get the last attmpted movment target

**Returns:** `object`

<a id="getblockingcreature"></a>

#### `GetBlockingCreature(oTarget=0)` - Routine 490

this function returns the bloking creature for the k_def_CBTBlk01 script

**Parameters:**

- `oTarget`: `object` (default: `0`)

**Returns:** `object`

<a id="getchallengerating"></a>

#### `GetChallengeRating(oCreature)` - Routine 494

Get oCreature's challenge rating.
* Returns 0.0 if oCreature is invalid.

**Parameters:**

- `oCreature`: `object`

**Returns:** `float`

<a id="getfoundenemycreature"></a>

#### `GetFoundEnemyCreature(oTarget=0)` - Routine 495

Returns the found enemy creature on a pathfind.

**Parameters:**

- `oTarget`: `object` (default: `0`)

**Returns:** `object`

<a id="getmovementrate"></a>

#### `GetMovementRate(oCreature)` - Routine 496

Get oCreature's movement rate.
* Returns 0 if oCreature is invalid.

**Parameters:**

- `oCreature`: `object`

**Returns:** `int`

<a id="getstealthxpdecrement"></a>

#### `GetStealthXPDecrement()` - Routine 498

Returns the amount the stealth xp bonus gets decreased each time the player is detected.

**Returns:** `int`

<a id="setstealthxpdecrement"></a>

#### `SetStealthXPDecrement(nDecrement)` - Routine 499

Sets the amount the stealth xp bonus gets decreased each time the player is detected.

**Parameters:**

- `nDecrement`: `int`

<a id="duplicateheadappearance"></a>

#### `DuplicateHeadAppearance(oidCreatureToChange, oidCreatureToMatch)` - Routine 500

**Parameters:**

- `oidCreatureToChange`: `object`
- `oidCreatureToMatch`: `object`

<a id="cutsceneattack"></a>

#### `CutsceneAttack(oTarget, nAnimation, nAttackResult, nDamage)` - Routine 503

CutsceneAttack
This function allows the designer to specify exactly what's going to happen in a combat round
There are no guarentees made that the animation specified here will be correct - only that it will be played,
so it is up to the designer to ensure that they have selected the right animation
It relies upon constants specified above for the attack result

**Parameters:**

- `oTarget`: `object`
- `nAnimation`: `int`
- `nAttackResult`: `int`
- `nDamage`: `int`

<a id="setlockorientationindialog"></a>

#### `SetLockOrientationInDialog(oObject, nValue)` - Routine 505

SetLockOrientationInDialog
Allows the locking and unlocking of orientation changes for an object in dialog
- oObject - Object
- nValue - TRUE or FALSE

**Parameters:**

- `oObject`: `object`
- `nValue`: `int`

<a id="setlockheadfollowindialog"></a>

#### `SetLockHeadFollowInDialog(oObject, nValue)` - Routine 506

SetLockHeadFollowInDialog
Allows the locking and undlocking of head following for an object in dialog
- oObject - Object
- nValue - TRUE or FALSE

**Parameters:**

- `oObject`: `object`
- `nValue`: `int`

<a id="cutscenemove"></a>

#### `CutsceneMove(oObject, vPosition, nRun)` - Routine 507

CutsceneMoveToPoint
Used by the cutscene system to allow designers to script combat

**Parameters:**

- `oObject`: `object`
- `vPosition`: `vector`
- `nRun`: `int`

<a id="enablevideoeffect"></a>

#### `EnableVideoEffect(nEffectType)` - Routine 508

EnableVideoEffect
Enables the video frame buffer effect specified by nEffectType, which is
an index into VideoEffects.2da. This video effect will apply indefinitely,
and so it should *always* be cleared by a call to DisableVideoEffect().

**Parameters:**

- `nEffectType`: `int`

<a id="disablevideoeffect"></a>

#### `DisableVideoEffect()` - Routine 508

EnableVideoEffect
Enables the video frame buffer effect specified by nEffectType, which is
an index into VideoEffects.2da. This video effect will apply indefinitely,
and so it should *always* be cleared by a call to DisableVideoEffect().

<a id="startnewmodule"></a>

#### `StartNewModule(sModuleName, sWayPoint=, sMovie1=, sMovie2=, sMovie3=, sMovie4=, sMovie5=, sMovie6=)` - Routine 509

Shut down the currently loaded module and start a new one (moving all
currently-connected players to the starting point.

**Parameters:**

- `sModuleName`: `string`
- `sWayPoint`: `string` (default: ``)
- `sMovie1`: `string` (default: ``)
- `sMovie2`: `string` (default: ``)
- `sMovie3`: `string` (default: ``)
- `sMovie4`: `string` (default: ``)
- `sMovie5`: `string` (default: ``)
- `sMovie6`: `string` (default: ``)

<a id="dosingleplayerautosave"></a>

#### `DoSinglePlayerAutoSave()` - Routine 512

Only if we are in a single player game, AutoSave the game.

<a id="getgamedifficulty"></a>

#### `GetGameDifficulty()` - Routine 513

Get the game difficulty (GAME_DIFFICULTY_*).

**Returns:** `int`

<a id="getuseractionspending"></a>

#### `GetUserActionsPending()` - Routine 514

This will test the combat action queu to see if the user has placed any actions on the queue.
will only work during combat.

**Returns:** `int`

<a id="revealmap"></a>

#### `RevealMap(vPoint=0.0 0.0 0.0, nRadius=-1)` - Routine 515

RevealMap
Reveals the map at the given WORLD point 'vPoint' with a MAP Grid Radius 'nRadius'
If this function is called with no parameters it will reveal the entire map.
(NOTE: if this function is called with a valid point but a default radius, ie. 'nRadius' of -1
then the entire map will be revealed)

**Parameters:**

- `vPoint`: `vector` (default: `0.0 0.0 0.0`)
- `nRadius`: `int` (default: `-1`)

<a id="settutorialwindowsenabled"></a>

#### `SetTutorialWindowsEnabled(bEnabled)` - Routine 516

SetTutorialWindowsEnabled
Sets whether or not the tutorial windows are enabled (ie. whether or not they will
appear when certain things happen for the first time).

**Parameters:**

- `bEnabled`: `int`

<a id="showtutorialwindow"></a>

#### `ShowTutorialWindow(nWindow)` - Routine 517

ShowTutorialWindow
Pops up the specified tutorial window.  If the tutorial window has already popped
up once before, this will do nothing.

**Parameters:**

- `nWindow`: `int`

<a id="startcreditsequence"></a>

#### `StartCreditSequence(bTransparentBackground)` - Routine 518

StartCreditSequence
Starts the credits sequence.  If bTransparentBackground is TRUE, the credits will be displayed
with a transparent background, allowing whatever is currently onscreen to show through.  If it
is set to FALSE, the credits will be displayed on a black background.

**Parameters:**

- `bTransparentBackground`: `int`

<a id="iscreditsequenceinprogress"></a>

#### `IsCreditSequenceInProgress()` - Routine 519

IsCreditSequenceInProgress
Returns TRUE if the credits sequence is currently in progress, FALSE otherwise.

**Returns:** `int`

<a id="swmg_setlateralaccelerationpersecond"></a>

#### `SWMG_SetLateralAccelerationPerSecond(fLAPS)` - Routine 520

Sets the minigame lateral acceleration/sec value

**Parameters:**

- `fLAPS`: `float`

<a id="swmg_getlateralaccelerationpersecond"></a>

#### `SWMG_GetLateralAccelerationPerSecond()` - Routine 521

Returns the minigame lateral acceleration/sec value

**Returns:** `float`

<a id="getdifficultymodifier"></a>

#### `GetDifficultyModifier()` - Routine 523

**Returns:** `float`

<a id="getappearancetype"></a>

#### `GetAppearanceType(oCreature)` - Routine 524

Returns the appearance type of oCreature (0 if creature doesn't exist)
- oCreature

**Parameters:**

- `oCreature`: `object`

**Returns:** `int`

<a id="floatingtextstrrefoncreature"></a>

#### `FloatingTextStrRefOnCreature(nStrRefToDisplay, oCreatureToFloatAbove, bBroadcastToFaction=1)` - Routine 525

Display floaty text above the specified creature.
The text will also appear in the chat buffer of each player that receives the
floaty text.
- nStrRefToDisplay: String ref (therefore text is translated)
- oCreatureToFloatAbove
- bBroadcastToFaction: If this is TRUE then only creatures in the same faction
as oCreatureToFloatAbove
will see the floaty text, and only if they are within range (30 metres).

**Parameters:**

- `nStrRefToDisplay`: `int`
- `oCreatureToFloatAbove`: `object`
- `bBroadcastToFaction`: `int` (default: `1`)

<a id="floatingtextstringoncreature"></a>

#### `FloatingTextStringOnCreature(sStringToDisplay, oCreatureToFloatAbove, bBroadcastToFaction=1)` - Routine 526

Display floaty text above the specified creature.
The text will also appear in the chat buffer of each player that receives the
floaty text.
- sStringToDisplay: String
- oCreatureToFloatAbove
- bBroadcastToFaction: If this is TRUE then only creatures in the same faction
as oCreatureToFloatAbove
will see the floaty text, and only if they are within range (30 metres).

**Parameters:**

- `sStringToDisplay`: `string`
- `oCreatureToFloatAbove`: `object`
- `bBroadcastToFaction`: `int` (default: `1`)

<a id="gettrapdisarmable"></a>

#### `GetTrapDisarmable(oTrapObject)` - Routine 527

- oTrapObject: a placeable, door or trigger
* Returns TRUE if oTrapObject is disarmable.

**Parameters:**

- `oTrapObject`: `object`

**Returns:** `int`

<a id="gettrapdetectable"></a>

#### `GetTrapDetectable(oTrapObject)` - Routine 528

- oTrapObject: a placeable, door or trigger
* Returns TRUE if oTrapObject is detectable.

**Parameters:**

- `oTrapObject`: `object`

**Returns:** `int`

<a id="gettrapdetectedby"></a>

#### `GetTrapDetectedBy(oTrapObject, oCreature)` - Routine 529

- oTrapObject: a placeable, door or trigger
- oCreature
* Returns TRUE if oCreature has detected oTrapObject

**Parameters:**

- `oTrapObject`: `object`
- `oCreature`: `object`

**Returns:** `int`

<a id="gettrapflagged"></a>

#### `GetTrapFlagged(oTrapObject)` - Routine 530

- oTrapObject: a placeable, door or trigger
* Returns TRUE if oTrapObject has been flagged as visible to all creatures.

**Parameters:**

- `oTrapObject`: `object`

**Returns:** `int`

<a id="gettrapbasetype"></a>

#### `GetTrapBaseType(oTrapObject)` - Routine 531

Get the trap base type (TRAP_BASE_TYPE_*) of oTrapObject.
- oTrapObject: a placeable, door or trigger

**Parameters:**

- `oTrapObject`: `object`

**Returns:** `int`

<a id="gettraponeshot"></a>

#### `GetTrapOneShot(oTrapObject)` - Routine 532

- oTrapObject: a placeable, door or trigger
* Returns TRUE if oTrapObject is one-shot (i.e. it does not reset itself
after firing.

**Parameters:**

- `oTrapObject`: `object`

**Returns:** `int`

<a id="gettrapcreator"></a>

#### `GetTrapCreator(oTrapObject)` - Routine 533

Get the creator of oTrapObject, the creature that set the trap.
- oTrapObject: a placeable, door or trigger
* Returns OBJECT_INVALID if oTrapObject was created in the toolset.

**Parameters:**

- `oTrapObject`: `object`

**Returns:** `object`

<a id="gettrapkeytag"></a>

#### `GetTrapKeyTag(oTrapObject)` - Routine 534

Get the tag of the key that will disarm oTrapObject.
- oTrapObject: a placeable, door or trigger

**Parameters:**

- `oTrapObject`: `object`

**Returns:** `string`

<a id="gettrapdisarmdc"></a>

#### `GetTrapDisarmDC(oTrapObject)` - Routine 535

Get the DC for disarming oTrapObject.
- oTrapObject: a placeable, door or trigger

**Parameters:**

- `oTrapObject`: `object`

**Returns:** `int`

<a id="gettrapdetectdc"></a>

#### `GetTrapDetectDC(oTrapObject)` - Routine 536

Get the DC for detecting oTrapObject.
- oTrapObject: a placeable, door or trigger

**Parameters:**

- `oTrapObject`: `object`

**Returns:** `int`

<a id="getlockkeyrequired"></a>

#### `GetLockKeyRequired(oObject)` - Routine 537

* Returns TRUE if a specific key is required to open the lock on oObject.

**Parameters:**

- `oObject`: `object`

**Returns:** `int`

<a id="getlockkeytag"></a>

#### `GetLockKeyTag(oObject)` - Routine 538

Get the tag of the key that will open the lock on oObject.

**Parameters:**

- `oObject`: `object`

**Returns:** `int`

<a id="getlocklockable"></a>

#### `GetLockLockable(oObject)` - Routine 539

* Returns TRUE if the lock on oObject is lockable.

**Parameters:**

- `oObject`: `object`

**Returns:** `int`

<a id="getlockunlockdc"></a>

#### `GetLockUnlockDC(oObject)` - Routine 540

Get the DC for unlocking oObject.

**Parameters:**

- `oObject`: `object`

**Returns:** `int`

<a id="getlocklockdc"></a>

#### `GetLockLockDC(oObject)` - Routine 541

Get the DC for locking oObject.

**Parameters:**

- `oObject`: `object`

**Returns:** `int`

<a id="getpclevellingup"></a>

#### `GetPCLevellingUp()` - Routine 542

Get the last PC that levelled up.

**Returns:** `object`

<a id="setplaceableillumination"></a>

#### `SetPlaceableIllumination(oPlaceable=0, bIlluminate=1)` - Routine 544

Set the status of the illumination for oPlaceable.
- oPlaceable
- bIlluminate: if this is TRUE, oPlaceable's illumination will be turned on.
If this is FALSE, oPlaceable's illumination will be turned off.
Note: You must call RecomputeStaticLighting() after calling this function in
order for the changes to occur visually for the players.
SetPlaceableIllumination() buffers the illumination changes, which are then

**Parameters:**

- `oPlaceable`: `object` (default: `0`)
- `bIlluminate`: `int` (default: `1`)

<a id="getplaceableillumination"></a>

#### `GetPlaceableIllumination(oPlaceable=0)` - Routine 545

* Returns TRUE if the illumination for oPlaceable is on

**Parameters:**

- `oPlaceable`: `object` (default: `0`)

**Returns:** `int`

<a id="getisplaceableobjectactionpossible"></a>

#### `GetIsPlaceableObjectActionPossible(oPlaceable, nPlaceableAction)` - Routine 546

- oPlaceable
- nPlaceableAction: PLACEABLE_ACTION_*
* Returns TRUE if nPlacebleAction is valid for oPlaceable.

**Parameters:**

- `oPlaceable`: `object`
- `nPlaceableAction`: `int`

**Returns:** `int`

<a id="doplaceableobjectaction"></a>

#### `DoPlaceableObjectAction(oPlaceable, nPlaceableAction)` - Routine 547

The caller performs nPlaceableAction on oPlaceable.
- oPlaceable
- nPlaceableAction: PLACEABLE_ACTION_*

**Parameters:**

- `oPlaceable`: `object`
- `nPlaceableAction`: `int`

<a id="getfirstpc"></a>

#### `GetFirstPC()` - Routine 548

Get the first PC in the player list.
This resets the position in the player list for GetNextPC().

**Returns:** `object`

<a id="getnextpc"></a>

#### `GetNextPC()` - Routine 548

Get the first PC in the player list.
This resets the position in the player list for GetNextPC().

**Returns:** `object`

<a id="settrapdetectedby"></a>

#### `SetTrapDetectedBy(oTrap, oDetector)` - Routine 550

Set oDetector to have detected oTrap.

**Parameters:**

- `oTrap`: `object`
- `oDetector`: `object`

**Returns:** `int`

<a id="getistrapped"></a>

#### `GetIsTrapped(oObject)` - Routine 551

Note: Only placeables, doors and triggers can be trapped.
* Returns TRUE if oObject is trapped.

**Parameters:**

- `oObject`: `object`

**Returns:** `int`

<a id="seteffecticon"></a>

#### `SetEffectIcon(eEffect, nIcon)` - Routine 552

SetEffectIcon
This will link the specified effect icon to the specified effect.  The
effect returned will contain the link to the effect icon and applying this
effect will cause an effect icon to appear on the portrait/charsheet gui.
eEffect: The effect which should cause the effect icon to appear.
nIcon: Index into effecticon.2da of the effect icon to use.

**Parameters:**

- `eEffect`: `effect`
- `nIcon`: `int`

**Returns:** `effect`

<a id="faceobjectawayfromobject"></a>

#### `FaceObjectAwayFromObject(oFacer, oObjectToFaceAwayFrom)` - Routine 553

FaceObjectAwayFromObject
This will cause the object oFacer to face away from oObjectToFaceAwayFrom.
The objects must be in the same area for this to work.

**Parameters:**

- `oFacer`: `object`
- `oObjectToFaceAwayFrom`: `object`

<a id="popupdeathguipanel"></a>

#### `PopUpDeathGUIPanel(oPC, bRespawnButtonEnabled=1, bWaitForHelpButtonEnabled=1, nHelpStringReference=0, sHelpString=)` - Routine 554

Spawn in the Death GUI.
The default (as defined by BioWare) can be spawned in by PopUpGUIPanel, but
if you want to turn off the "Respawn" or "Wait for Help" buttons, this is the
function to use.
- oPC
- bRespawnButtonEnabled: if this is TRUE, the "Respawn" button will be enabled
on the Death GUI.
- bWaitForHelpButtonEnabled: if this is TRUE, the "Wait For Help" button will
be enabled on the Death GUI.
- nHelpStringReference
- sHelpString

**Parameters:**

- `oPC`: `object`
- `bRespawnButtonEnabled`: `int` (default: `1`)
- `bWaitForHelpButtonEnabled`: `int` (default: `1`)
- `nHelpStringReference`: `int` (default: `0`)
- `sHelpString`: `string` (default: ``)

<a id="settrapdisabled"></a>

#### `SetTrapDisabled(oTrap)` - Routine 555

Disable oTrap.
- oTrap: a placeable, door or trigger.

**Parameters:**

- `oTrap`: `object`

<a id="exportallcharacters"></a>

#### `ExportAllCharacters()` - Routine 557

Force all the characters of the players who are currently in the game to
be exported to their respective directories i.e. LocalVault/ServerVault/ etc.

<a id="writetimestampedlogentry"></a>

#### `WriteTimestampedLogEntry(sLogEntry)` - Routine 560

Write sLogEntry as a timestamped entry into the log file

**Parameters:**

- `sLogEntry`: `string`

<a id="getfactionleader"></a>

#### `GetFactionLeader(oMemberOfFaction)` - Routine 562

Get the leader of the faction of which oMemberOfFaction is a member.
* Returns OBJECT_INVALID if oMemberOfFaction is not a valid creature.

**Parameters:**

- `oMemberOfFaction`: `object`

**Returns:** `object`

<a id="swmg_setspeedblureffect"></a>

#### `SWMG_SetSpeedBlurEffect(bEnabled, fRatio=0.75)` - Routine 563

Turns on or off the speed blur effect in rendered scenes.
bEnabled: Set TRUE to turn it on, FALSE to turn it off.
fRatio: Sets the frame accumulation ratio.

**Parameters:**

- `bEnabled`: `int`
- `fRatio`: `float` (default: `0.75`)

<a id="endgame"></a>

#### `EndGame(nShowEndGameGui=1)` - Routine 564

Immediately ends the currently running game and returns to the start screen.
nShowEndGameGui: Set TRUE to display the death gui.

**Parameters:**

- `nShowEndGameGui`: `int` (default: `1`)

<a id="getrunscriptvar"></a>

#### `GetRunScriptVar()` - Routine 565

Get a variable passed when calling console debug runscript

**Returns:** `int`

<a id="getcreaturemovmenttype"></a>

#### `GetCreatureMovmentType(oidCreature)` - Routine 566

This function returns a value that matches one of the MOVEMENT_SPEED_... constants
if the OID passed in is not found or not a creature then it will return
MOVEMENT_SPEED_IMMOBILE.

**Parameters:**

- `oidCreature`: `object`

**Returns:** `int`

<a id="gethasinventory"></a>

#### `GetHasInventory(oObject)` - Routine 570

Determine whether oObject has an inventory.
* Returns TRUE for creatures and stores, and checks to see if an item or placeable object is a container.
* Returns FALSE for all other object types.

**Parameters:**

- `oObject`: `object`

**Returns:** `int`

<a id="getstrrefsoundduration"></a>

#### `GetStrRefSoundDuration(nStrRef)` - Routine 571

Get the duration (in seconds) of the sound attached to nStrRef
* Returns 0.0f if no duration is stored or if no sound is attached

**Parameters:**

- `nStrRef`: `int`

**Returns:** `float`

<a id="addtoparty"></a>

#### `AddToParty(oPC, oPartyLeader)` - Routine 572

Add oPC to oPartyLeader's party.  This will only work on two PCs.
- oPC: player to add to a party
- oPartyLeader: player already in the party

**Parameters:**

- `oPC`: `object`
- `oPartyLeader`: `object`

<a id="removefromparty"></a>

#### `RemoveFromParty(oPC)` - Routine 573

Remove oPC from their current party. This will only work on a PC.
- oPC: removes this player from whatever party they're currently in.

**Parameters:**

- `oPC`: `object`

<a id="swmg_getlastevent"></a>

#### `SWMG_GetLastEvent()` - Routine 583

OnAnimKey
get the event and the name of the model on which the event happened
SWMG_GetLastEvent

**Returns:** `string`

<a id="swmg_getlasteventmodelname"></a>

#### `SWMG_GetLastEventModelName()` - Routine 584

SWMG_GetLastEventModelName

**Returns:** `string`

<a id="swmg_getobjectbyname"></a>

#### `SWMG_GetObjectByName(sName)` - Routine 585

gets an object by its name (duh!)
SWMG_GetObjectByName

**Parameters:**

- `sName`: `string`

**Returns:** `object`

<a id="swmg_playanimation"></a>

#### `SWMG_PlayAnimation(oObject, sAnimName, bLooping=1, bQueue=0, bOverlay=0)` - Routine 586

plays an animation on an object
SWMG_PlayAnimation

**Parameters:**

- `oObject`: `object`
- `sAnimName`: `string`
- `bLooping`: `int` (default: `1`)
- `bQueue`: `int` (default: `0`)
- `bOverlay`: `int` (default: `0`)

<a id="swmg_getlastbullethitdamage"></a>

#### `SWMG_GetLastBulletHitDamage()` - Routine 587

OnHitBullet
get the damage, the target type (see TARGETflags), and the shooter
SWMG_GetLastBulletHitDamage

**Returns:** `int`

<a id="swmg_getlastbullethittarget"></a>

#### `SWMG_GetLastBulletHitTarget()` - Routine 588

SWMG_GetLastBulletHitTarget

**Returns:** `int`

<a id="swmg_getlastbullethitshooter"></a>

#### `SWMG_GetLastBulletHitShooter()` - Routine 589

SWMG_GetLastBulletHitShooter

**Returns:** `object`

<a id="swmg_onbullethit"></a>

#### `SWMG_OnBulletHit()` - Routine 591

the default implementation of OnBulletHit
SWMG_OnBulletHit

<a id="swmg_onobstaclehit"></a>

#### `SWMG_OnObstacleHit()` - Routine 592

the default implementation of OnObstacleHit
SWMG_OnObstacleHit

<a id="swmg_getlastfollowerhit"></a>

#### `SWMG_GetLastFollowerHit()` - Routine 593

returns the last follower and obstacle hit
SWMG_GetLastFollowerHit

**Returns:** `object`

<a id="swmg_getlastobstaclehit"></a>

#### `SWMG_GetLastObstacleHit()` - Routine 594

SWMG_GetLastObstacleHit

**Returns:** `object`

<a id="swmg_getlastbulletfireddamage"></a>

#### `SWMG_GetLastBulletFiredDamage()` - Routine 595

gets information about the last bullet fired
SWMG_GetLastBulletFiredDamage

**Returns:** `int`

<a id="swmg_getlastbulletfiredtarget"></a>

#### `SWMG_GetLastBulletFiredTarget()` - Routine 596

SWMG_GetLastBulletFiredTarget

**Returns:** `int`

<a id="swmg_getobjectname"></a>

#### `SWMG_GetObjectName(oid=0)` - Routine 597

gets an objects name
SWMG_GetObjectName

**Parameters:**

- `oid`: `object` (default: `0`)

**Returns:** `string`

<a id="swmg_ondeath"></a>

#### `SWMG_OnDeath()` - Routine 598

the default implementation of OnDeath
SWMG_OnDeath

<a id="swmg_isfollower"></a>

#### `SWMG_IsFollower(oid=0)` - Routine 599

a bunch of Is functions for your pleasure
SWMG_IsFollower

**Parameters:**

- `oid`: `object` (default: `0`)

**Returns:** `int`

<a id="swmg_isplayer"></a>

#### `SWMG_IsPlayer(oid=0)` - Routine 600

SWMG_IsPlayer

**Parameters:**

- `oid`: `object` (default: `0`)

**Returns:** `int`

<a id="swmg_isenemy"></a>

#### `SWMG_IsEnemy(oid=0)` - Routine 601

SWMG_IsEnemy

**Parameters:**

- `oid`: `object` (default: `0`)

**Returns:** `int`

<a id="swmg_istrigger"></a>

#### `SWMG_IsTrigger(oid=0)` - Routine 602

SWMG_IsTrigger

**Parameters:**

- `oid`: `object` (default: `0`)

**Returns:** `int`

<a id="swmg_isobstacle"></a>

#### `SWMG_IsObstacle(oid=0)` - Routine 603

SWMG_IsObstacle

**Parameters:**

- `oid`: `object` (default: `0`)

**Returns:** `int`

<a id="swmg_ondamage"></a>

#### `SWMG_OnDamage()` - Routine 605

SWMG_OnDamage

<a id="swmg_getlasthpchange"></a>

#### `SWMG_GetLastHPChange()` - Routine 606

SWMG_GetLastHPChange

**Returns:** `int`

<a id="swmg_removeanimation"></a>

#### `SWMG_RemoveAnimation(oObject, sAnimName)` - Routine 607

SWMG_RemoveAnimation

**Parameters:**

- `oObject`: `object`
- `sAnimName`: `string`

<a id="swmg_getcameranearclip"></a>

#### `SWMG_GetCameraNearClip()` - Routine 608

SWMG_GetCameraNearClip

**Returns:** `float`

<a id="swmg_getcamerafarclip"></a>

#### `SWMG_GetCameraFarClip()` - Routine 609

SWMG_GetCameraFarClip

**Returns:** `float`

<a id="swmg_setcameraclip"></a>

#### `SWMG_SetCameraClip(fNear, fFar)` - Routine 610

SWMG_SetCameraClip

**Parameters:**

- `fNear`: `float`
- `fFar`: `float`

<a id="swmg_getplayer"></a>

#### `SWMG_GetPlayer()` - Routine 611

SWMG_GetPlayer

**Returns:** `object`

<a id="swmg_getenemycount"></a>

#### `SWMG_GetEnemyCount()` - Routine 612

SWMG_GetEnemyCount

**Returns:** `int`

<a id="swmg_getenemy"></a>

#### `SWMG_GetEnemy(nEntry)` - Routine 613

SWMG_GetEnemy

**Parameters:**

- `nEntry`: `int`

**Returns:** `object`

<a id="swmg_getobstaclecount"></a>

#### `SWMG_GetObstacleCount()` - Routine 614

SWMG_GetObstacleCount

**Returns:** `int`

<a id="swmg_getobstacle"></a>

#### `SWMG_GetObstacle(nEntry)` - Routine 615

SWMG_GetObstacle

**Parameters:**

- `nEntry`: `int`

**Returns:** `object`

<a id="swmg_getsphereradius"></a>

#### `SWMG_GetSphereRadius(oFollower)` - Routine 619

SWMG_GetSphereRadius

**Parameters:**

- `oFollower`: `object`

**Returns:** `float`

<a id="swmg_setsphereradius"></a>

#### `SWMG_SetSphereRadius(oFollower, fRadius)` - Routine 620

SWMG_SetSphereRadius

**Parameters:**

- `oFollower`: `object`
- `fRadius`: `float`

<a id="swmg_getnumloops"></a>

#### `SWMG_GetNumLoops(oFollower)` - Routine 621

SWMG_GetNumLoops

**Parameters:**

- `oFollower`: `object`

**Returns:** `int`

<a id="swmg_setnumloops"></a>

#### `SWMG_SetNumLoops(oFollower, nNumLoops)` - Routine 622

SWMG_SetNumLoops

**Parameters:**

- `oFollower`: `object`
- `nNumLoops`: `int`

<a id="swmg_getposition"></a>

#### `SWMG_GetPosition(oFollower)` - Routine 623

SWMG_GetPosition

**Parameters:**

- `oFollower`: `object`

**Returns:** `vector`

<a id="swmg_getgunbankcount"></a>

#### `SWMG_GetGunBankCount(oFollower)` - Routine 624

SWMG_GetGunBankCount

**Parameters:**

- `oFollower`: `object`

**Returns:** `int`

<a id="swmg_getgunbankbulletmodel"></a>

#### `SWMG_GetGunBankBulletModel(oFollower, nGunBank)` - Routine 625

SWMG_GetGunBankBulletModel

**Parameters:**

- `oFollower`: `object`
- `nGunBank`: `int`

**Returns:** `string`

<a id="swmg_getgunbankgunmodel"></a>

#### `SWMG_GetGunBankGunModel(oFollower, nGunBank)` - Routine 626

SWMG_GetGunBankGunModel

**Parameters:**

- `oFollower`: `object`
- `nGunBank`: `int`

**Returns:** `string`

<a id="swmg_getgunbankdamage"></a>

#### `SWMG_GetGunBankDamage(oFollower, nGunBank)` - Routine 627

SWMG_GetGunBankDamage

**Parameters:**

- `oFollower`: `object`
- `nGunBank`: `int`

**Returns:** `int`

<a id="swmg_getgunbanktimebetweenshots"></a>

#### `SWMG_GetGunBankTimeBetweenShots(oFollower, nGunBank)` - Routine 628

SWMG_GetGunBankTimeBetweenShots

**Parameters:**

- `oFollower`: `object`
- `nGunBank`: `int`

**Returns:** `float`

<a id="swmg_getgunbanklifespan"></a>

#### `SWMG_GetGunBankLifespan(oFollower, nGunBank)` - Routine 629

SWMG_GetGunBankLifespan

**Parameters:**

- `oFollower`: `object`
- `nGunBank`: `int`

**Returns:** `float`

<a id="swmg_getgunbankspeed"></a>

#### `SWMG_GetGunBankSpeed(oFollower, nGunBank)` - Routine 630

SWMG_GetGunBankSpeed

**Parameters:**

- `oFollower`: `object`
- `nGunBank`: `int`

**Returns:** `float`

<a id="swmg_getgunbanktarget"></a>

#### `SWMG_GetGunBankTarget(oFollower, nGunBank)` - Routine 631

SWMG_GetGunBankTarget

**Parameters:**

- `oFollower`: `object`
- `nGunBank`: `int`

**Returns:** `int`

<a id="swmg_setgunbankbulletmodel"></a>

#### `SWMG_SetGunBankBulletModel(oFollower, nGunBank, sBulletModel)` - Routine 632

SWMG_SetGunBankBulletModel

**Parameters:**

- `oFollower`: `object`
- `nGunBank`: `int`
- `sBulletModel`: `string`

<a id="swmg_setgunbankgunmodel"></a>

#### `SWMG_SetGunBankGunModel(oFollower, nGunBank, sGunModel)` - Routine 633

SWMG_SetGunBankGunModel

**Parameters:**

- `oFollower`: `object`
- `nGunBank`: `int`
- `sGunModel`: `string`

<a id="swmg_setgunbankdamage"></a>

#### `SWMG_SetGunBankDamage(oFollower, nGunBank, nDamage)` - Routine 634

SWMG_SetGunBankDamage

**Parameters:**

- `oFollower`: `object`
- `nGunBank`: `int`
- `nDamage`: `int`

<a id="swmg_setgunbanktimebetweenshots"></a>

#### `SWMG_SetGunBankTimeBetweenShots(oFollower, nGunBank, fTBS)` - Routine 635

SWMG_SetGunBankTimeBetweenShots

**Parameters:**

- `oFollower`: `object`
- `nGunBank`: `int`
- `fTBS`: `float`

<a id="swmg_setgunbanklifespan"></a>

#### `SWMG_SetGunBankLifespan(oFollower, nGunBank, fLifespan)` - Routine 636

SWMG_SetGunBankLifespan

**Parameters:**

- `oFollower`: `object`
- `nGunBank`: `int`
- `fLifespan`: `float`

<a id="swmg_setgunbankspeed"></a>

#### `SWMG_SetGunBankSpeed(oFollower, nGunBank, fSpeed)` - Routine 637

SWMG_SetGunBankSpeed

**Parameters:**

- `oFollower`: `object`
- `nGunBank`: `int`
- `fSpeed`: `float`

<a id="swmg_setgunbanktarget"></a>

#### `SWMG_SetGunBankTarget(oFollower, nGunBank, nTarget)` - Routine 638

SWMG_SetGunBankTarget

**Parameters:**

- `oFollower`: `object`
- `nGunBank`: `int`
- `nTarget`: `int`

<a id="swmg_getlastbullethitpart"></a>

#### `SWMG_GetLastBulletHitPart()` - Routine 639

SWMG_GetLastBulletHitPart

**Returns:** `string`

<a id="swmg_isgunbanktargetting"></a>

#### `SWMG_IsGunBankTargetting(oFollower, nGunBank)` - Routine 640

SWMG_IsGunBankTargetting

**Parameters:**

- `oFollower`: `object`
- `nGunBank`: `int`

**Returns:** `int`

<a id="swmg_getplayeroffset"></a>

#### `SWMG_GetPlayerOffset()` - Routine 641

SWMG_GetPlayerOffset
returns a vector with the player rotation for rotation minigames
returns a vector with the player translation for translation minigames

**Returns:** `vector`

<a id="swmg_getplayerinvincibility"></a>

#### `SWMG_GetPlayerInvincibility()` - Routine 642

SWMG_GetPlayerInvincibility

**Returns:** `float`

<a id="swmg_getplayerspeed"></a>

#### `SWMG_GetPlayerSpeed()` - Routine 643

SWMG_GetPlayerSpeed

**Returns:** `float`

<a id="swmg_getplayerminspeed"></a>

#### `SWMG_GetPlayerMinSpeed()` - Routine 644

SWMG_GetPlayerMinSpeed

**Returns:** `float`

<a id="swmg_getplayeraccelerationpersecond"></a>

#### `SWMG_GetPlayerAccelerationPerSecond()` - Routine 645

SWMG_GetPlayerAccelerationPerSecond

**Returns:** `float`

<a id="swmg_getplayertunnelpos"></a>

#### `SWMG_GetPlayerTunnelPos()` - Routine 646

SWMG_GetPlayerTunnelPos

**Returns:** `vector`

<a id="swmg_setplayeroffset"></a>

#### `SWMG_SetPlayerOffset(vOffset)` - Routine 647

SWMG_SetPlayerOffset

**Parameters:**

- `vOffset`: `vector`

<a id="swmg_setplayerinvincibility"></a>

#### `SWMG_SetPlayerInvincibility(fInvincibility)` - Routine 648

SWMG_SetPlayerInvincibility

**Parameters:**

- `fInvincibility`: `float`

<a id="swmg_setplayerspeed"></a>

#### `SWMG_SetPlayerSpeed(fSpeed)` - Routine 649

SWMG_SetPlayerSpeed

**Parameters:**

- `fSpeed`: `float`

<a id="swmg_setplayerminspeed"></a>

#### `SWMG_SetPlayerMinSpeed(fMinSpeed)` - Routine 650

SWMG_SetPlayerMinSpeed

**Parameters:**

- `fMinSpeed`: `float`

<a id="swmg_setplayeraccelerationpersecond"></a>

#### `SWMG_SetPlayerAccelerationPerSecond(fAPS)` - Routine 651

SWMG_SetPlayerAccelerationPerSecond

**Parameters:**

- `fAPS`: `float`

<a id="swmg_setplayertunnelpos"></a>

#### `SWMG_SetPlayerTunnelPos(vTunnel)` - Routine 652

SWMG_SetPlayerTunnelPos

**Parameters:**

- `vTunnel`: `vector`

<a id="swmg_getplayertunnelneg"></a>

#### `SWMG_GetPlayerTunnelNeg()` - Routine 653

SWMG_GetPlayerTunnelNeg

**Returns:** `vector`

<a id="swmg_setplayertunnelneg"></a>

#### `SWMG_SetPlayerTunnelNeg(vTunnel)` - Routine 654

SWMG_SetPlayerTunnelNeg

**Parameters:**

- `vTunnel`: `vector`

<a id="swmg_getplayerorigin"></a>

#### `SWMG_GetPlayerOrigin()` - Routine 655

SWMG_GetPlayerOrigin

**Returns:** `vector`

<a id="swmg_setplayerorigin"></a>

#### `SWMG_SetPlayerOrigin(vOrigin)` - Routine 656

SWMG_SetPlayerOrigin

**Parameters:**

- `vOrigin`: `vector`

<a id="swmg_getgunbankhorizontalspread"></a>

#### `SWMG_GetGunBankHorizontalSpread(oEnemy, nGunBank)` - Routine 657

SWMG_GetGunBankHorizontalSpread

**Parameters:**

- `oEnemy`: `object`
- `nGunBank`: `int`

**Returns:** `float`

<a id="swmg_getgunbankverticalspread"></a>

#### `SWMG_GetGunBankVerticalSpread(oEnemy, nGunBank)` - Routine 658

SWMG_GetGunBankVerticalSpread

**Parameters:**

- `oEnemy`: `object`
- `nGunBank`: `int`

**Returns:** `float`

<a id="swmg_getgunbanksensingradius"></a>

#### `SWMG_GetGunBankSensingRadius(oEnemy, nGunBank)` - Routine 659

SWMG_GetGunBankSensingRadius

**Parameters:**

- `oEnemy`: `object`
- `nGunBank`: `int`

**Returns:** `float`

<a id="swmg_getgunbankinaccuracy"></a>

#### `SWMG_GetGunBankInaccuracy(oEnemy, nGunBank)` - Routine 660

SWMG_GetGunBankInaccuracy

**Parameters:**

- `oEnemy`: `object`
- `nGunBank`: `int`

**Returns:** `float`

<a id="swmg_setgunbankhorizontalspread"></a>

#### `SWMG_SetGunBankHorizontalSpread(oEnemy, nGunBank, fHorizontalSpread)` - Routine 661

SWMG_SetGunBankHorizontalSpread

**Parameters:**

- `oEnemy`: `object`
- `nGunBank`: `int`
- `fHorizontalSpread`: `float`

<a id="swmg_setgunbankverticalspread"></a>

#### `SWMG_SetGunBankVerticalSpread(oEnemy, nGunBank, fVerticalSpread)` - Routine 662

SWMG_SetGunBankVerticalSpread

**Parameters:**

- `oEnemy`: `object`
- `nGunBank`: `int`
- `fVerticalSpread`: `float`

<a id="swmg_setgunbanksensingradius"></a>

#### `SWMG_SetGunBankSensingRadius(oEnemy, nGunBank, fSensingRadius)` - Routine 663

SWMG_SetGunBankSensingRadius

**Parameters:**

- `oEnemy`: `object`
- `nGunBank`: `int`
- `fSensingRadius`: `float`

<a id="swmg_setgunbankinaccuracy"></a>

#### `SWMG_SetGunBankInaccuracy(oEnemy, nGunBank, fInaccuracy)` - Routine 664

SWMG_SetGunBankInaccuracy

**Parameters:**

- `oEnemy`: `object`
- `nGunBank`: `int`
- `fInaccuracy`: `float`

<a id="swmg_getisinvulnerable"></a>

#### `SWMG_GetIsInvulnerable(oFollower)` - Routine 665

GetIsInvulnerable
This returns whether the follower object is currently invulnerable to damage

**Parameters:**

- `oFollower`: `object`

**Returns:** `int`

<a id="swmg_startinvulnerability"></a>

#### `SWMG_StartInvulnerability(oFollower)` - Routine 666

StartInvulnerability

**Parameters:**

- `oFollower`: `object`

<a id="swmg_getplayermaxspeed"></a>

#### `SWMG_GetPlayerMaxSpeed()` - Routine 667

GetPlayerMaxSpeed
This returns the player character's max speed

**Returns:** `float`

<a id="swmg_setplayermaxspeed"></a>

#### `SWMG_SetPlayerMaxSpeed(fMaxSpeed)` - Routine 668

SetPlayerMaxSpeed
This sets the player character's max speed

**Parameters:**

- `fMaxSpeed`: `float`

<a id="addjournalworldentry"></a>

#### `AddJournalWorldEntry(nIndex, szEntry, szTitle=World Entry)` - Routine 669

AddJournalWorldEntry
Adds a user entered entry to the world notices

**Parameters:**

- `nIndex`: `int`
- `szEntry`: `string`
- `szTitle`: `string` (default: `World Entry`)

<a id="addjournalworldentrystrref"></a>

#### `AddJournalWorldEntryStrref(strref, strrefTitle)` - Routine 670

AddJournalWorldEntryStrref
Adds an entry to the world notices using stringrefs

**Parameters:**

- `strref`: `int`
- `strrefTitle`: `int`

<a id="barkstring"></a>

#### `BarkString(oCreature, strRef)` - Routine 671

BarkString
this will cause a creature to bark the strRef from the talk table
If creature is specefied as OBJECT_INVALID a general bark is made.

**Parameters:**

- `oCreature`: `object`
- `strRef`: `int`

<a id="deletejournalworldallentries"></a>

#### `DeleteJournalWorldAllEntries()` - Routine 672

DeleteJournalWorldAllEntries
Nuke's 'em all, user entered or otherwise.

<a id="deletejournalworldentry"></a>

#### `DeleteJournalWorldEntry(nIndex)` - Routine 673

DeleteJournalWorldEntry
Deletes a user entered world notice

**Parameters:**

- `nIndex`: `int`

<a id="deletejournalworldentrystrref"></a>

#### `DeleteJournalWorldEntryStrref(strref)` - Routine 674

DeleteJournalWorldEntryStrref
Deletes the world notice pertaining to the string ref

**Parameters:**

- `strref`: `int`

<a id="playvisualareaeffect"></a>

#### `PlayVisualAreaEffect(nEffectID, lTarget)` - Routine 677

PlayVisualAreaEffect

**Parameters:**

- `nEffectID`: `int`
- `lTarget`: `location`

<a id="setjournalquestentrypicture"></a>

#### `SetJournalQuestEntryPicture(szPlotID, oObject, nPictureIndex, bAllPartyMemebers=1, bAllPlayers=0)` - Routine 678

SetJournalQuestEntryPicture

**Parameters:**

- `szPlotID`: `string`
- `oObject`: `object`
- `nPictureIndex`: `int`
- `bAllPartyMemebers`: `int` (default: `1`)
- `bAllPlayers`: `int` (default: `0`)

<a id="setnpcselectability"></a>

#### `SetNPCSelectability(nNPC, nSelectability)` - Routine 708

SetNPCSelectability

**Parameters:**

- `nNPC`: `int`
- `nSelectability`: `int`

<a id="getnpcselectability"></a>

#### `GetNPCSelectability(nNPC)` - Routine 709

GetNPCSelectability

**Parameters:**

- `nNPC`: `int`

**Returns:** `int`

<a id="clearalleffects"></a>

#### `ClearAllEffects()` - Routine 710

Clear all the effects of the caller.
* No return value, but if an error occurs, the log file will contain
"ClearAllEffects failed.".

<a id="getstandardfaction"></a>

#### `GetStandardFaction(oObject)` - Routine 713

GetStandardFaction
Find out which standard faction oObject belongs to.
* Returns INVALID_STANDARD_FACTION if oObject does not belong to
a Standard Faction, or an error has occurred.

**Parameters:**

- `oObject`: `object`

**Returns:** `int`

<a id="giveplotxp"></a>

#### `GivePlotXP(sPlotName, nPercentage)` - Routine 714

GivePlotXP
Give nPercentage% of the experience associated with plot sPlotName
to the party
- sPlotName
- nPercentage

**Parameters:**

- `sPlotName`: `string`
- `nPercentage`: `int`

<a id="getcategoryfromtalent"></a>

#### `GetCategoryFromTalent(tTalent)` - Routine 735

Get the Category of tTalent.

**Parameters:**

- `tTalent`: `talent`

**Returns:** `int`

<a id="surrenderbyfaction"></a>

#### `SurrenderByFaction(nFactionFrom, nFactionTo)` - Routine 736

This affects all creatures in the area that are in faction nFactionFrom...
- Makes them join nFactionTo
- Clears all actions
- Disables combat mode

**Parameters:**

- `nFactionFrom`: `int`
- `nFactionTo`: `int`

<a id="changefactionbyfaction"></a>

#### `ChangeFactionByFaction(nFactionFrom, nFactionTo)` - Routine 737

This affects all creatures in the area that are in faction nFactionFrom.
making them change to nFactionTo

**Parameters:**

- `nFactionFrom`: `int`
- `nFactionTo`: `int`

<a id="playroomanimation"></a>

#### `PlayRoomAnimation(sRoom, nAnimation)` - Routine 738

PlayRoomAnimation
Plays a looping animation on a room

**Parameters:**

- `sRoom`: `string`
- `nAnimation`: `int`

<a id="showgalaxymap"></a>

#### `ShowGalaxyMap(nPlanet)` - Routine 739

ShowGalaxyMap
Brings up the Galaxy Map Gui, with 'nPlanet' selected.  'nPlanet' can only be a planet
that has already been set available and selectable.

**Parameters:**

- `nPlanet`: `int`

<a id="setplanetselectable"></a>

#### `SetPlanetSelectable(nPlanet, bSelectable)` - Routine 740

SetPlanetSelectable
Sets 'nPlanet' selectable on the Galaxy Map Gui.

**Parameters:**

- `nPlanet`: `int`
- `bSelectable`: `int`

<a id="getplanetselectable"></a>

#### `GetPlanetSelectable(nPlanet)` - Routine 741

GetPlanetSelectable
Returns wheter or not 'nPlanet' is selectable.

**Parameters:**

- `nPlanet`: `int`

**Returns:** `int`

<a id="setplanetavailable"></a>

#### `SetPlanetAvailable(nPlanet, bAvailable)` - Routine 742

SetPlanetAvailable
Sets 'nPlanet' available on the Galaxy Map Gui.

**Parameters:**

- `nPlanet`: `int`
- `bAvailable`: `int`

<a id="getplanetavailable"></a>

#### `GetPlanetAvailable(nPlanet)` - Routine 743

GetPlanetAvailable
Returns wheter or not 'nPlanet' is available.

**Parameters:**

- `nPlanet`: `int`

**Returns:** `int`

<a id="getselectedplanet"></a>

#### `GetSelectedPlanet()` - Routine 744

GetSelectedPlanet
Returns the ID of the currently selected planet.  Check Planetary.2da
for which planet the return value corresponds to. If the return is -1
no planet is selected.

**Returns:** `int`

<a id="setareafogcolor"></a>

#### `SetAreaFogColor(oArea, fRed, fGreen, fBlue)` - Routine 746

SetAreaFogColor
Set the fog color for the area oArea.

**Parameters:**

- `oArea`: `object`
- `fRed`: `float`
- `fGreen`: `float`
- `fBlue`: `float`

<a id="getislivecontentavailable"></a>

#### `GetIsLiveContentAvailable(nPkg)` - Routine 748

GetIsLiveContentAvailable
Determines whether a given live content package is available
nPkg = LIVE_CONTENT_PKG1, LIVE_CONTENT_PKG2, ..., LIVE_CONTENT_PKG6

**Parameters:**

- `nPkg`: `int`

**Returns:** `int`

<a id="resetdialogstate"></a>

#### `ResetDialogState()` - Routine 749

ResetDialogState
Resets the GlobalDialogState for the engine.
NOTE: NEVER USE THIS UNLESS YOU KNOW WHAT ITS FOR!
only to be used for a failing OnDialog script

<a id="getispoisoned"></a>

#### `GetIsPoisoned(oObject)` - Routine 751

GetIsPoisoned
Returns TRUE if the object specified is poisoned.

**Parameters:**

- `oObject`: `object`

**Returns:** `int`

<a id="getspelltarget"></a>

#### `GetSpellTarget(oCreature=0)` - Routine 752

GetSpellTarget
Returns the object id of the spell target

**Parameters:**

- `oCreature`: `object` (default: `0`)

**Returns:** `object`

<a id="setsolomode"></a>

#### `SetSoloMode(bActivate)` - Routine 753

SetSoloMode
Activates/Deactivates solo mode for the player's party.

**Parameters:**

- `bActivate`: `int`

<a id="cancelpostdialogcharacterswitch"></a>

#### `CancelPostDialogCharacterSwitch()` - Routine 757

<a id="noclicksfor"></a>

#### `NoClicksFor(fDuration)` - Routine 759

**Parameters:**

- `fDuration`: `float`

<a id="holdworldfadeinfordialog"></a>

#### `HoldWorldFadeInForDialog()` - Routine 760

<a id="shipbuild"></a>

#### `ShipBuild()` - Routine 761

**Returns:** `int`

<a id="surrenderretainbuffs"></a>

#### `SurrenderRetainBuffs()` - Routine 762

<a id="getfirstinpersistentobject"></a>

#### `GetFirstInPersistentObject(oPersistentObject=0, nResidentObjectType=1, nPersistentZone=0)`

**Parameters:**

- `oPersistentObject`: `object` (default: `0`)
- `nResidentObjectType`: `int` (default: `1`)
- `nPersistentZone`: `int` (default: `0`)

**Returns:** `object`

<a id="getnextinpersistentobject"></a>

#### `GetNextInPersistentObject(oPersistentObject=0, nResidentObjectType=1, nPersistentZone=0)`

**Parameters:**

- `oPersistentObject`: `object` (default: `0`)
- `nResidentObjectType`: `int` (default: `1`)
- `nPersistentZone`: `int` (default: `0`)

**Returns:** `object`

<a id="aurpoststring"></a>

#### `AurPostString(sString, nX, nY, fLife)`

post a string to the screen at column nX and row nY for fLife seconds
582. AurPostString

**Parameters:**

- `sString`: `string`
- `nX`: `int`
- `nY`: `int`
- `fLife`: `float`

<a id="swmg_getsoundfrequency"></a>

#### `SWMG_GetSoundFrequency(oFollower, nSound)`

683. SWMG_GetSoundFrequency
Gets the frequency of a trackfollower sound

**Parameters:**

- `oFollower`: `object`
- `nSound`: `int`

**Returns:** `int`

<a id="swmg_setsoundfrequency"></a>

#### `SWMG_SetSoundFrequency(oFollower, nSound, nFrequency)`

684. SWMG_SetSoundFrequency
Sets the frequency of a trackfollower sound

**Parameters:**

- `oFollower`: `object`
- `nSound`: `int`
- `nFrequency`: `int`

<a id="swmg_getsoundfrequencyisrandom"></a>

#### `SWMG_GetSoundFrequencyIsRandom(oFollower, nSound)`

685. SWMG_GetSoundFrequencyIsRandom
Gets whether the frequency of a trackfollower sound is using the random model

**Parameters:**

- `oFollower`: `object`
- `nSound`: `int`

**Returns:** `int`

<a id="swmg_setsoundfrequencyisrandom"></a>

#### `SWMG_SetSoundFrequencyIsRandom(oFollower, nSound, bIsRandom)`

686. SWMG_SetSoundFrequencyIsRandom
Sets whether the frequency of a trackfollower sound is using the random model

**Parameters:**

- `oFollower`: `object`
- `nSound`: `int`
- `bIsRandom`: `int`

<a id="swmg_getsoundvolume"></a>

#### `SWMG_GetSoundVolume(oFollower, nSound)`

687. SWMG_GetSoundVolume
Gets the volume of a trackfollower sound

**Parameters:**

- `oFollower`: `object`
- `nSound`: `int`

**Returns:** `int`

<a id="swmg_setsoundvolume"></a>

#### `SWMG_SetSoundVolume(oFollower, nSound, nVolume)`

688. SWMG_SetSoundVolume
Sets the volume of a trackfollower sound

**Parameters:**

- `oFollower`: `object`
- `nSound`: `int`
- `nVolume`: `int`

<a id="isavailablecreature"></a>

#### `IsAvailableCreature(nNPC)`

696. IsAvailableNPC
This returns whether a NPC is in the list of available party members

**Parameters:**

- `nNPC`: `int`

**Returns:** `int`

<a id="getnpcaistyle"></a>

#### `GetNPCAIStyle(oCreature)`

705.
Returns the party members ai style

**Parameters:**

- `oCreature`: `object`

**Returns:** `int`

<a id="setnpcaistyle"></a>

#### `SetNPCAIStyle(oCreature, nStyle)`

707.
Sets the party members ai style

**Parameters:**

- `oCreature`: `object`
- `nStyle`: `int`

<a id="getminonehp"></a>

#### `GetMinOneHP(oObject)`

715. GetMinOneHP
Checks to see if oObject has the MinOneHP Flag set on them.

**Parameters:**

- `oObject`: `object`

**Returns:** `int`

<a id="setminonehp"></a>

#### `SetMinOneHP(oObject, nMinOneHP)`

716. SetMinOneHP
Sets/Removes the MinOneHP Flag on oObject.

**Parameters:**

- `oObject`: `object`
- `nMinOneHP`: `int`

<a id="swmg_getplayertunnelinfinite"></a>

#### `SWMG_GetPlayerTunnelInfinite()`

717. SWMG_GetPlayerTunnelInfinite
Gets whether each of the dimensions is infinite

**Returns:** `vector`

<a id="swmg_setplayertunnelinfinite"></a>

#### `SWMG_SetPlayerTunnelInfinite(vInfinite)`

718. SWMG_SetPlayerTunnelInfinite
Sets whether each of the dimensions is infinite

**Parameters:**

- `vInfinite`: `vector`

<a id="getlasthostiletarget"></a>

#### `GetLastHostileTarget(oAttacker=0)`

721. GetLastAttackTarget
Returns the last attack target for a given object

**Parameters:**

- `oAttacker`: `object` (default: `0`)

**Returns:** `object`

<a id="getlastattackaction"></a>

#### `GetLastAttackAction(oAttacker=0)`

722. GetLastAttackAction
Returns the last attack action for a given object

**Parameters:**

- `oAttacker`: `object` (default: `0`)

**Returns:** `int`

<a id="getlastforcepowerused"></a>

#### `GetLastForcePowerUsed(oAttacker=0)`

723. GetLastForcePowerUsed
Returns the last force power used (as a spell number that indexes the Spells.2da) by the given object

**Parameters:**

- `oAttacker`: `object` (default: `0`)

**Returns:** `int`

<a id="getlastcombatfeatused"></a>

#### `GetLastCombatFeatUsed(oAttacker=0)`

724. GetLastCombatFeatUsed
Returns the last feat used (as a feat number that indexes the Feats.2da) by the given object

**Parameters:**

- `oAttacker`: `object` (default: `0`)

**Returns:** `int`

<a id="getlastattackresult"></a>

#### `GetLastAttackResult(oAttacker=0)`

725. GetLastAttackResult
Returns the result of the last attack

**Parameters:**

- `oAttacker`: `object` (default: `0`)

**Returns:** `int`

<a id="getwasforcepowersuccessful"></a>

#### `GetWasForcePowerSuccessful(oAttacker=0)`

726. GetWasForcePowerSuccessful
Returns whether the last force power used was successful or not

**Parameters:**

- `oAttacker`: `object` (default: `0`)

**Returns:** `int`

<a id="getfirstattacker"></a>

#### `GetFirstAttacker(oCreature=0)`

727. GetFirstAttacker
Returns the first object in the area that is attacking oCreature

**Parameters:**

- `oCreature`: `object` (default: `0`)

**Returns:** `object`

<a id="getnextattacker"></a>

#### `GetNextAttacker(oCreature=0)`

728. GetNextAttacker
Returns the next object in the area that is attacking oCreature

**Parameters:**

- `oCreature`: `object` (default: `0`)

**Returns:** `object`

<a id="setformation"></a>

#### `SetFormation(oAnchor, oCreature, nFormationPattern, nPosition)`

729. SetFormation
Put oCreature into the nFormationPattern about oAnchor at position nPosition
- oAnchor: The formation is set relative to this object
- oCreature: This is the creature that you wish to join the formation
- nFormationPattern: FORMATION_*
- nPosition: Integer from 1 to 10 to specify which position in the formation
oCreature is supposed to take.

**Parameters:**

- `oAnchor`: `object`
- `oCreature`: `object`
- `nFormationPattern`: `int`
- `nPosition`: `int`

<a id="setforcepowerunsuccessful"></a>

#### `SetForcePowerUnsuccessful(nResult, oCreature=0)`

731. SetForcePowerUnsuccessful
Sets the reason (through a constant) for why a force power failed

**Parameters:**

- `nResult`: `int`
- `oCreature`: `object` (default: `0`)

<a id="getisdebilitated"></a>

#### `GetIsDebilitated(oCreature=0)`

732. GetIsDebilitated
Returns whether the given object is debilitated or not

**Parameters:**

- `oCreature`: `object` (default: `0`)

**Returns:** `int`

<a id="playmovie"></a>

#### `PlayMovie(sMovie)`

733. PlayMovie
Playes a Movie.

**Parameters:**

- `sMovie`: `string`

<a id="savenpcstate"></a>

#### `SaveNPCState(nNPC)`

734. SaveNPCState
Tells the party table to save the state of a party member NPC

**Parameters:**

- `nNPC`: `int`

<a id="suppressstatussummaryentry"></a>

#### `SuppressStatusSummaryEntry(nNumEntries=1)`

763. SuppressStatusSummaryEntry
This will prevent the next n entries that should have shown up in the status summary
from being added
This will not add on to any existing summary suppressions, but rather replace it.  So
to clear the supression system pass 0 as the entry value

**Parameters:**

- `nNumEntries`: `int` (default: `1`)

<a id="getcheatcode"></a>

#### `GetCheatCode(nCode)`

764. GetCheatCode
Returns true if cheat code has been enabled

**Parameters:**

- `nCode`: `int`

**Returns:** `int`

<a id="setmusicvolume"></a>

#### `SetMusicVolume(fVolume=1.0)`

765. SetMusicVolume
NEVER USE THIS!

**Parameters:**

- `fVolume`: `float` (default: `1.0`)

<a id="ismovieplaying"></a>

#### `IsMoviePlaying()`

768. IsMoviePlaying
Checks if a movie is currently playing.

**Returns:** `int`

<a id="queuemovie"></a>

#### `QueueMovie(sMovie, bSkippable)`

769. QueueMovie
Queues up a movie to be played using PlayMovieQueue.
If bSkippable is TRUE, the player can cancel the movie by hitting escape.
If bSkippable is FALSE, the player cannot cancel the movie and must wait
for it to finish playing.

**Parameters:**

- `sMovie`: `string`
- `bSkippable`: `int`

<a id="playmoviequeue"></a>

#### `PlayMovieQueue(bAllowSeparateSkips)`

770. PlayMovieQueue
Plays the movies that have been added to the queue by QueueMovie
If bAllowSeparateSkips is TRUE, hitting escape to cancel a movie only
cancels out of the currently playing movie rather than the entire queue
of movies (assuming the currently playing movie is flagged as skippable).
If bAllowSeparateSkips is FALSE, the entire movie queue will be cancelled
if the player hits escape (assuming the currently playing movie is flagged
as skippable).

**Parameters:**

- `bAllowSeparateSkips`: `int`

<a id="yavinhackclosedoor"></a>

#### `YavinHackCloseDoor(oidDoor)`

771. YavinHackCloseDoor
This is an incredibly hacky function to allow the doors to be properly
closed on Yavin without running into the problems we've had.  It is too
late in development to fix it correctly, so thus we do this.  Life is
hard.  You'll get over it

**Parameters:**

- `oidDoor`: `object`


### Party Management

<a id="switchplayercharacter"></a>

#### `SwitchPlayerCharacter(nNPC)` - Routine 11

Switches the main character to a specified NPC
-1 specifies to switch back to the original PC

**Parameters:**

- `nNPC`: `int`

**Returns:** `int`

<a id="setpartyleader"></a>

#### `SetPartyLeader(nNPC)` - Routine 13

Sets (by NPC constant) which party member should be the controlled
character

**Parameters:**

- `nNPC`: `int`

**Returns:** `int`

<a id="getpartymembercount"></a>

#### `GetPartyMemberCount()` - Routine 126

GetPartyMemberCount
Returns a count of how many members are in the party including the player character

**Returns:** `int`

<a id="addpartymember"></a>

#### `AddPartyMember(nNPC, oCreature)` - Routine 574

Adds a creature to the party
Returns whether the addition was successful
AddPartyMember

**Parameters:**

- `nNPC`: `int`
- `oCreature`: `object`

**Returns:** `int`

<a id="removepartymember"></a>

#### `RemovePartyMember(nNPC)` - Routine 575

Removes a creature from the party
Returns whether the removal was syccessful
RemovePartyMember

**Parameters:**

- `nNPC`: `int`

**Returns:** `int`

<a id="isobjectpartymember"></a>

#### `IsObjectPartyMember(oCreature)` - Routine 576

Returns whether a specified creature is a party member
IsObjectPartyMember

**Parameters:**

- `oCreature`: `object`

**Returns:** `int`

<a id="getpartymemberbyindex"></a>

#### `GetPartyMemberByIndex(nIndex)` - Routine 577

Returns the party member at a given index in the party.
The order of members in the party can vary based on
who the current leader is (member 0 is always the current
party leader).
GetPartyMemberByIndex

**Parameters:**

- `nIndex`: `int`

**Returns:** `object`

<a id="addavailablenpcbyobject"></a>

#### `AddAvailableNPCByObject(nNPC, oCreature)`

694. AddAvailableNPCByObject
This adds a NPC to the list of available party members using
a game object as the template
Returns if true if successful, false if the NPC had already
been added or the object specified is invalid

**Parameters:**

- `nNPC`: `int`
- `oCreature`: `object`

**Returns:** `int`

<a id="removeavailablenpc"></a>

#### `RemoveAvailableNPC(nNPC)`

695. RemoveAvailableNPC
This removes a NPC from the list of available party members
Returns whether it was successful or not

**Parameters:**

- `nNPC`: `int`

**Returns:** `int`

<a id="addavailablenpcbytemplate"></a>

#### `AddAvailableNPCByTemplate(nNPC, sTemplate)`

697. AddAvailableNPCByTemplate
This adds a NPC to the list of available party members using
a template
Returns if true if successful, false if the NPC had already
been added or the template specified is invalid

**Parameters:**

- `nNPC`: `int`
- `sTemplate`: `string`

**Returns:** `int`

<a id="spawnavailablenpc"></a>

#### `SpawnAvailableNPC(nNPC, lPosition)`

698. SpawnAvailableNPC
This spawns a NPC from the list of available creatures
Returns a pointer to the creature object

**Parameters:**

- `nNPC`: `int`
- `lPosition`: `location`

**Returns:** `object`

<a id="isnpcpartymember"></a>

#### `IsNPCPartyMember(nNPC)`

699. IsNPCPartyMember
Returns if a given NPC constant is in the party currently

**Parameters:**

- `nNPC`: `int`

**Returns:** `int`

<a id="getpartyaistyle"></a>

#### `GetPartyAIStyle()`

704.
Returns the party ai style

**Returns:** `int`

<a id="setpartyaistyle"></a>

#### `SetPartyAIStyle(nStyle)`

706.
Sets the party ai style

**Parameters:**

- `nStyle`: `int`

<a id="showpartyselectiongui"></a>

#### `ShowPartySelectionGUI(sExitScript=, nForceNPC1=-1, nForceNPC2=-1)`

ShowPartySelectionGUI
Brings up the party selection GUI for the player to
select the members of the party from
if exit script is specified, will be executed when
the GUI is exited

**Parameters:**

- `sExitScript`: `string` (default: ``)
- `nForceNPC1`: `int` (default: `-1`)
- `nForceNPC2`: `int` (default: `-1`)

<a id="setavailablenpcid"></a>

#### `SetAvailableNPCId()`

767. SetAvailableNPCId
This will set the object id that should be used for a specific available NPC


### Player Character Functions

<a id="setplayerrestrictmode"></a>

#### `SetPlayerRestrictMode(bRestrict)` - Routine 58

SetPlayerRestrictMode
Sets whether the player is currently in 'restricted' mode

**Parameters:**

- `bRestrict`: `int`

<a id="getplayerrestrictmode"></a>

#### `GetPlayerRestrictMode(oObject=0)` - Routine 83

GetPlayerRestrictMode
returns the current player 'restricted' mode

**Parameters:**

- `oObject`: `object` (default: `0`)

**Returns:** `int`

<a id="getispc"></a>

#### `GetIsPC(oCreature)` - Routine 217

* Returns TRUE if oCreature is a Player Controlled character.

**Parameters:**

- `oCreature`: `object`

**Returns:** `int`

<a id="getpcspeaker"></a>

#### `GetPCSpeaker()` - Routine 238

Get the PC that is involved in the conversation.
* Returns OBJECT_INVALID on error.

**Returns:** `object`

<a id="getgender"></a>

#### `GetGender(oCreature)` - Routine 358

Get the gender of oCreature.

**Parameters:**

- `oCreature`: `object`

**Returns:** `int`

<a id="givexptocreature"></a>

#### `GiveXPToCreature(oCreature, nXpAmount)` - Routine 393

Gives nXpAmount to oCreature.

**Parameters:**

- `oCreature`: `object`
- `nXpAmount`: `int`

<a id="getplotflag"></a>

#### `GetPlotFlag(oTarget=0)` - Routine 455

Determine whether oTarget is a plot object.

**Parameters:**

- `oTarget`: `object` (default: `0`)

**Returns:** `int`

<a id="setplotflag"></a>

#### `SetPlotFlag(oTarget, nPlotFlag)` - Routine 456

Set oTarget's plot object status.

**Parameters:**

- `oTarget`: `object`
- `nPlotFlag`: `int`

<a id="getsubrace"></a>

#### `GetSubRace(oCreature)` - Routine 497

GetSubRace of oCreature
Returns SUBRACE_*

**Parameters:**

- `oCreature`: `object`

**Returns:** `int`

<a id="setcameramode"></a>

#### `SetCameraMode(oPlayer, nCameraMode)` - Routine 504

Set the camera mode for oPlayer.
- oPlayer
- nCameraMode: CAMERA_MODE_*
* If oPlayer is not player-controlled or nCameraMode is invalid, nothing
happens.

**Parameters:**

- `oPlayer`: `object`
- `nCameraMode`: `int`


### Skills and Feats

<a id="getlastspellcaster"></a>

#### `GetLastSpellCaster()` - Routine 245

This is for use in a "Spell Cast" script, it gets who cast the spell.
The spell could have been cast by a creature, placeable or door.
* Returns OBJECT_INVALID if the caller is not a creature, placeable or door.

**Returns:** `object`

<a id="getlastspell"></a>

#### `GetLastSpell()` - Routine 246

This is for use in a "Spell Cast" script, it gets the ID of the spell that
was cast.

**Returns:** `int`

<a id="gethasfeat"></a>

#### `GetHasFeat(nFeat, oCreature=0)` - Routine 285

Determine whether oCreature has nFeat, and nFeat is useable.
- nFeat: FEAT_*
- oCreature

**Parameters:**

- `nFeat`: `int`
- `oCreature`: `object` (default: `0`)

**Returns:** `int`

<a id="gethasskill"></a>

#### `GetHasSkill(nSkill, oCreature=0)` - Routine 286

Determine whether oCreature has nSkill, and nSkill is useable.
- nSkill: SKILL_*
- oCreature

**Parameters:**

- `nSkill`: `int`
- `oCreature`: `object` (default: `0`)

**Returns:** `int`

<a id="getskillrank"></a>

#### `GetSkillRank(nSkill, oTarget=0)` - Routine 315

Get the number of ranks that oTarget has in nSkill.
- nSkill: SKILL_*
- oTarget
* Returns -1 if oTarget doesn't have nSkill.
* Returns 0 if nSkill is untrained.

**Parameters:**

- `nSkill`: `int`
- `oTarget`: `object` (default: `0`)

**Returns:** `int`

<a id="getlastspellharmful"></a>

#### `GetLastSpellHarmful()` - Routine 423

Use this in a SpellCast script to determine whether the spell was considered
harmful.
* Returns TRUE if the last spell cast was harmful.

**Returns:** `int`

<a id="gethasfeateffect"></a>

#### `GetHasFeatEffect(nFeat, oObject=0)` - Routine 543

- nFeat: FEAT_*
- oObject
* Returns TRUE if oObject has effects on it originating from nFeat.

**Parameters:**

- `nFeat`: `int`
- `oObject`: `object` (default: `0`)

**Returns:** `int`


### Sound and Music Functions

<a id="playsound"></a>

#### `PlaySound(sSoundName)` - Routine 46

Play sSoundName
- sSoundName: TBD - SS

**Parameters:**

- `sSoundName`: `string`

<a id="soundobjectplay"></a>

#### `SoundObjectPlay(oSound)` - Routine 413

Play oSound.

**Parameters:**

- `oSound`: `object`

<a id="soundobjectstop"></a>

#### `SoundObjectStop(oSound)` - Routine 414

Stop playing oSound.

**Parameters:**

- `oSound`: `object`

<a id="soundobjectsetvolume"></a>

#### `SoundObjectSetVolume(oSound, nVolume)` - Routine 415

Set the volume of oSound.
- oSound
- nVolume: 0-127

**Parameters:**

- `oSound`: `object`
- `nVolume`: `int`

<a id="soundobjectsetposition"></a>

#### `SoundObjectSetPosition(oSound, vPosition)` - Routine 416

Set the position of oSound.

**Parameters:**

- `oSound`: `object`
- `vPosition`: `vector`

<a id="musicbackgroundplay"></a>

#### `MusicBackgroundPlay(oArea)` - Routine 425

Play the background music for oArea.

**Parameters:**

- `oArea`: `object`

<a id="musicbackgroundstop"></a>

#### `MusicBackgroundStop(oArea)` - Routine 426

Stop the background music for oArea.

**Parameters:**

- `oArea`: `object`

<a id="musicbackgroundsetdelay"></a>

#### `MusicBackgroundSetDelay(oArea, nDelay)` - Routine 427

Set the delay for the background music for oArea.
- oArea
- nDelay: delay in milliseconds

**Parameters:**

- `oArea`: `object`
- `nDelay`: `int`

<a id="musicbackgroundchangeday"></a>

#### `MusicBackgroundChangeDay(oArea, nTrack)` - Routine 428

Change the background day track for oArea to nTrack.
- oArea
- nTrack

**Parameters:**

- `oArea`: `object`
- `nTrack`: `int`

<a id="musicbackgroundchangenight"></a>

#### `MusicBackgroundChangeNight(oArea, nTrack)` - Routine 429

Change the background night track for oArea to nTrack.
- oArea
- nTrack

**Parameters:**

- `oArea`: `object`
- `nTrack`: `int`

<a id="musicbattleplay"></a>

#### `MusicBattlePlay(oArea)` - Routine 430

Play the battle music for oArea.

**Parameters:**

- `oArea`: `object`

<a id="musicbattlestop"></a>

#### `MusicBattleStop(oArea)` - Routine 431

Stop the battle music for oArea.

**Parameters:**

- `oArea`: `object`

<a id="musicbattlechange"></a>

#### `MusicBattleChange(oArea, nTrack)` - Routine 432

Change the battle track for oArea.
- oArea
- nTrack

**Parameters:**

- `oArea`: `object`
- `nTrack`: `int`

<a id="ambientsoundplay"></a>

#### `AmbientSoundPlay(oArea)` - Routine 433

Play the ambient sound for oArea.

**Parameters:**

- `oArea`: `object`

<a id="ambientsoundstop"></a>

#### `AmbientSoundStop(oArea)` - Routine 434

Stop the ambient sound for oArea.

**Parameters:**

- `oArea`: `object`

<a id="ambientsoundchangeday"></a>

#### `AmbientSoundChangeDay(oArea, nTrack)` - Routine 435

Change the ambient day track for oArea to nTrack.
- oArea
- nTrack

**Parameters:**

- `oArea`: `object`
- `nTrack`: `int`

<a id="ambientsoundchangenight"></a>

#### `AmbientSoundChangeNight(oArea, nTrack)` - Routine 436

Change the ambient night track for oArea to nTrack.
- oArea
- nTrack

**Parameters:**

- `oArea`: `object`
- `nTrack`: `int`

<a id="musicbackgroundgetdaytrack"></a>

#### `MusicBackgroundGetDayTrack(oArea)` - Routine 558

Get the Day Track for oArea.

**Parameters:**

- `oArea`: `object`

**Returns:** `int`

<a id="musicbackgroundgetnighttrack"></a>

#### `MusicBackgroundGetNightTrack(oArea)` - Routine 559

Get the Night Track for oArea.

**Parameters:**

- `oArea`: `object`

**Returns:** `int`

<a id="ambientsoundsetdayvolume"></a>

#### `AmbientSoundSetDayVolume(oArea, nVolume)` - Routine 567

Set the ambient day volume for oArea to nVolume.
- oArea
- nVolume: 0 - 100

**Parameters:**

- `oArea`: `object`
- `nVolume`: `int`

<a id="ambientsoundsetnightvolume"></a>

#### `AmbientSoundSetNightVolume(oArea, nVolume)` - Routine 568

Set the ambient night volume for oArea to nVolume.
- oArea
- nVolume: 0 - 100

**Parameters:**

- `oArea`: `object`
- `nVolume`: `int`

<a id="musicbackgroundgetbattletrack"></a>

#### `MusicBackgroundGetBattleTrack(oArea)` - Routine 569

Get the Battle Track for oArea.

**Parameters:**

- `oArea`: `object`

**Returns:** `int`

<a id="soundobjectfadeandstop"></a>

#### `SoundObjectFadeAndStop(oSound, fSeconds)` - Routine 745

SoundObjectFadeAndStop
Fades a sound object for 'fSeconds' and then stops it.

**Parameters:**

- `oSound`: `object`
- `fSeconds`: `float`

<a id="soundobjectsetfixedvariance"></a>

#### `SoundObjectSetFixedVariance(oSound, fFixedVariance)`

124. SoundObjectSetFixedVariance
Sets the constant variance at which to play the sound object
This variance is a multiplier of the original sound

**Parameters:**

- `oSound`: `object`
- `fFixedVariance`: `float`

<a id="soundobjectgetfixedvariance"></a>

#### `SoundObjectGetFixedVariance(oSound)`

188. SoundObjectGetFixedVariance
Gets the constant variance at which to play the sound object

**Parameters:**

- `oSound`: `object`

**Returns:** `float`

<a id="soundobjectgetpitchvariance"></a>

#### `SoundObjectGetPitchVariance(oSound)`

689. SoundObjectGetPitchVariance
Gets the pitch variance of a placeable sound object

**Parameters:**

- `oSound`: `object`

**Returns:** `float`

<a id="soundobjectsetpitchvariance"></a>

#### `SoundObjectSetPitchVariance(oSound, fVariance)`

690. SoundObjectSetPitchVariance
Sets the pitch variance of a placeable sound object

**Parameters:**

- `oSound`: `object`
- `fVariance`: `float`

<a id="soundobjectgetvolume"></a>

#### `SoundObjectGetVolume(oSound)`

691. SoundObjectGetVolume
Gets the volume of a placeable sound object

**Parameters:**

- `oSound`: `object`

**Returns:** `int`



================================================================================
TSL-ONLY FUNCTIONS ù fill-in content for TSL stub sections
================================================================================

### Abilities and Stats

<a id="setbonusforcepoints"></a>

#### `SetBonusForcePoints(oCreature, nBonusFP)`

RWT-OEI 02/06/04
SetBonusForcePoints - This sets the number of bonus force points
that will always be added to that character's total calculated
force points.

**Parameters:**

- `oCreature`: `object`
- `nBonusFP`: `int`

<a id="addbonusforcepoints"></a>

#### `AddBonusForcePoints(oCreature, nBonusFP)`

RWT-OEI 02/06/04
AddBonusForcePoints - This adds nBonusFP to the current total
bonus that the player has. The Bonus Force Points are a pool
of force points that will always be added after the player's
total force points are calculated (based on level, force dice,
etc.)

**Parameters:**

- `oCreature`: `object`
- `nBonusFP`: `int`

<a id="getbonusforcepoints"></a>

#### `GetBonusForcePoints(oCreature)`

RWT-OEI 02/06/04
GetBonusForcePoints - This returns the total number of bonus
force points a player has. Bonus Force Points are a pool of
points that are always added to a player's Max Force Points.
ST: Please explain how a function returning VOID could return a
numerical value? Hope it works changing the return type...

**Parameters:**

- `oCreature`: `object`

**Returns:** `int`


### Actions

<a id="actionfollowowner"></a>

#### `ActionFollowOwner(fRange=2.5)`

843
RWT-OEI 07/20/04
Similiar to ActionFollowLeader() except the creature
follows its owner
nRange is how close it should follow. Note that once this
action is queued, it will be the only thing this creature
does until a ClearAllActions() is used.

**Parameters:**

- `fRange`: `float` (default: `2.5`)

<a id="actionswitchweapons"></a>

#### `ActionSwitchWeapons()`

853
ActionSwitchWeapons
Forces the creature to switch between Config 1 and Config 2
of their equipment. Does not work in dialogs. Works with


### Effects System

<a id="effectforcebody"></a>

#### `EffectForceBody(nLevel)`

DJS-OEI 12/15/2003
Create a Force Body effect
- nLevel: The level of the Force Body effect.
0 = Force Body
1 = Improved Force Body
2 = Master Force Body

**Parameters:**

- `nLevel`: `int`

**Returns:** `effect`

<a id="effectfury"></a>

#### `EffectFury()`

DJS-OEI 1/2/2004
Create a Fury effect.

**Returns:** `effect`

<a id="effectblind"></a>

#### `EffectBlind()`

DJS-OEI 1/3/2004
Create a Blind effect.

**Returns:** `effect`

<a id="effectfpregenmodifier"></a>

#### `EffectFPRegenModifier(nPercent)`

DJS-OEI 1/4/2004
Create an FP regeneration modifier effect.

**Parameters:**

- `nPercent`: `int`

**Returns:** `effect`

<a id="effectvpregenmodifier"></a>

#### `EffectVPRegenModifier(nPercent)`

DJS-OEI 1/4/2004
Create a VP regeneration modifier effect.

**Parameters:**

- `nPercent`: `int`

**Returns:** `effect`

<a id="effectcrush"></a>

#### `EffectCrush()`

DJS-OEI 1/9/2004
Create a Force Crush effect.

**Returns:** `effect`

<a id="effectdroidconfused"></a>

#### `EffectDroidConfused()`

809
new function for droid confusion so inherint mind immunity can be
avoided.

**Returns:** `effect`

<a id="effectforcesight"></a>

#### `EffectForceSight()`

823
DJS-OEI 5/5/2004
Creates a Force Sight effect.

**Returns:** `effect`

<a id="effectmindtrick"></a>

#### `EffectMindTrick()`

848
Create a Mind Trick effect

**Returns:** `effect`

<a id="effectfactionmodifier"></a>

#### `EffectFactionModifier(nNewFaction)`

849
Create a Faction Modifier effect.

**Parameters:**

- `nNewFaction`: `int`

**Returns:** `effect`

<a id="effectdroidscramble"></a>

#### `EffectDroidScramble()`

852
Create a Droid Scramble effect

**Returns:** `effect`


### Item Management

<a id="getitemcomponent"></a>

#### `GetItemComponent()`

FAK-OEI 12/15/2003
Get the number of components for an item

**Returns:** `int`

<a id="getitemcomponentpiecevalue"></a>

#### `GetItemComponentPieceValue()`

FAK-OEI 12/15/2003
Get the number of components for an item in pieces

**Returns:** `int`


### Object Query and Manipulation

<a id="removeeffectbyid"></a>

#### `RemoveEffectByID(oCreature, nEffectID)`

867
JF-OEI 10-07-2004
Remove an effect by ID

**Parameters:**

- `oCreature`: `object`
- `nEffectID`: `int`

<a id="removeeffectbyexactmatch"></a>

#### `RemoveEffectByExactMatch(oCreature, eEffect)`

868
RWT-OEI 10/07/04
This script removes an effect by an identical match
based on:
Must have matching EffectID types.
Must have the same value in Integer(0)
Must have the same value in Integer(1)
I'm specifically using this function for Mandalore's implant swapping
script and it will probably not be useful for anyone else. If you're
not sure what this script function does, see me before using it.

**Parameters:**

- `oCreature`: `object`
- `eEffect`: `effect`


### Other Functions

<a id="getfeatacquired"></a>

#### `GetFeatAcquired(nFeat, oCreature=0)` - Routine 285

Determine whether oCreature has nFeat, and nFeat is useable.
PLEASE NOTE!!! - This function will return FALSE if the target
is not currently able to use the feat due to daily limits or
other restrictions. Use GetFeatAcquired() if you just want to

**Parameters:**

- `nFeat`: `int`
- `oCreature`: `object` (default: `0`)

**Returns:** `int`

<a id="getspellacquired"></a>

#### `GetSpellAcquired(nSpell, oCreature=0)` - Routine 377

Determine whether oCreature has nSpell memorised.
PLEASE NOTE!!! - This function will return FALSE if the target
is not currently able to use the spell due to lack of sufficient
Force Points. Use GetSpellAcquired() if you just want to

**Parameters:**

- `nSpell`: `int`
- `oCreature`: `object` (default: `0`)

**Returns:** `int`

<a id="getscriptparameter"></a>

#### `GetScriptParameter(nIndex)`

DJS-OEI
768. GetScriptParameter
This function will take the index of a script parameter
and return the value associated with it. The index
of the first parameter is 1.

**Parameters:**

- `nIndex`: `int`

**Returns:** `int`

<a id="setfadeuntilscript"></a>

#### `SetFadeUntilScript()`

RWT-OEI 12/10/03
769. SetFadeUntilScript
This script function will make it so that the fade cannot be lifted under any circumstances
other than a call to the SetGlobalFadeIn() script.
This function should be called AFTER the fade has already been called. For example, you would

<a id="showchemicalupgradescreen"></a>

#### `ShowChemicalUpgradeScreen(oCharacter)`

FAK-OEI 12/15/2003
Start the GUI for Chemical Workshop

**Parameters:**

- `oCharacter`: `object`

<a id="getchemicals"></a>

#### `GetChemicals()`

FAK-OEI 12/15/2003
Get the number of chemicals for an item

**Returns:** `int`

<a id="getchemicalpiecevalue"></a>

#### `GetChemicalPieceValue()`

FAK-OEI 12/15/2003
Get the number of chemicals for an item in pieces

**Returns:** `int`

<a id="getspellforcepointcost"></a>

#### `GetSpellForcePointCost()`

DJS-OEI 12/30/2003
Get the number of Force Points that were required to
cast this spell. This includes modifiers such as Room Force
Ratings and the Force Body power.
* Return value on error: 0

**Returns:** `int`

<a id="swmg_getswoopupgrade"></a>

#### `SWMG_GetSwoopUpgrade(nSlot)`

FAK - OEI 1/12/04
Minigame grabs a swoop bike upgrade

**Parameters:**

- `nSlot`: `int`

**Returns:** `int`

<a id="showswoopupgradescreen"></a>

#### `ShowSwoopUpgradeScreen()`

FAK-OEI 1/12/2004
Displays the Swoop Bike upgrade screen.

<a id="grantfeat"></a>

#### `GrantFeat(nFeat, oCreature)`

DJS-OEI 1/13/2004
Grants the target a feat without regard for prerequisites.

**Parameters:**

- `nFeat`: `int`
- `oCreature`: `object`

<a id="grantspell"></a>

#### `GrantSpell(nSpell, oCreature)`

DJS-OEI 1/13/2004
Grants the target a spell without regard for prerequisites.

**Parameters:**

- `nSpell`: `int`
- `oCreature`: `object`

<a id="spawnmine"></a>

#### `SpawnMine(nMineType, lPoint, nDetectDCBase, nDisarmDCBase, oCreator)`

DJS-OEI 1/13/2004
Places an active mine on the map.
nMineType - Mine Type from Traps.2DA
lPoint - The location in the world to place the mine.
nDetectDCBase - This value, plus the "DetectDCMod" column in Traps.2DA
results in the final DC for creatures to detect this mine.
nDisarmDCBase - This value, plus the "DisarmDCMod" column in Traps.2DA
results in the final DC for creatures to disarm this mine.
oCreator - The object that should be considered the owner of the mine.
If oCreator is set to OBJECT_INVALID, the faction of the mine will be
considered Hostile1, meaning the party will be vulnerable to it.

**Parameters:**

- `nMineType`: `int`
- `lPoint`: `location`
- `nDetectDCBase`: `int`
- `nDisarmDCBase`: `int`
- `oCreator`: `object`

<a id="swmg_gettrackposition"></a>

#### `SWMG_GetTrackPosition(oFollower)`

FAK - OEI 1/15/04
Yet another minigame function. Returns the object's track's position.

**Parameters:**

- `oFollower`: `object`

**Returns:** `vector`

<a id="swmg_setfollowerposition"></a>

#### `SWMG_SetFollowerPosition(vPos)`

FAK - OEI 1/15/04
minigame function that lets you psuedo-set the position of a follower object

**Parameters:**

- `vPos`: `vector`

**Returns:** `vector`

<a id="setfakecombatstate"></a>

#### `SetFakeCombatState(oObject, nEnable)`

RWT-OEI 01/16/04
A function to put the character into a true combat state but the reason set to
not real combat. This should help us control animations in cutscenes with a bit
more precision. -- Not totally sure this is doing anything just yet. Seems
the combat condition gets cleared shortly after anyway.
If nEnable is 1, it enables fake combat mode. If 0, it disables it.
WARNING: Whenever using this function to enable fake combat mode, you should
have a matching call to it to disable it. (pass 0 for nEnable).

**Parameters:**

- `oObject`: `object`
- `nEnable`: `int`

<a id="swmg_destroyminigameobject"></a>

#### `SWMG_DestroyMiniGameObject(oObject)`

FAK - OEI 1/23/04
minigame function that deletes a minigame object

**Parameters:**

- `oObject`: `object`

<a id="getownerdemolitionsskill"></a>

#### `GetOwnerDemolitionsSkill(oObject)`

DJS-OEI 1/26/2004
Returns the Demolitions skill of the creature that
placed this mine. This will often be 0. This function accepts
the object that the mine is attached to (Door, Placeable, or Trigger)
and will determine which one it actually is at runtime.

**Parameters:**

- `oObject`: `object`

**Returns:** `int`

<a id="setorientonclick"></a>

#### `SetOrientOnClick(oCreature=0, nState=1)`

RWT-OEI 01/29/04
Disables or Enables the Orient On Click behavior in creatures. If
disabled, they will not orient to face the player when clicked on
for dialogue. The default behavior is TRUE.

**Parameters:**

- `oCreature`: `object` (default: `0`)
- `nState`: `int` (default: `1`)

<a id="getinfluence"></a>

#### `GetInfluence(nNPC)`

DJS-OEI 1/29/2004
Gets the PC's influence on the alignment of a CNPC.
Parameters:
nNPC - NPC_* constant identifying the CNPC we're interested in.
If this character is not an available party member, the return
value with be 0. If the character is in the party, but has an
attitude of Ambivalent, this will be -1.

**Parameters:**

- `nNPC`: `int`

**Returns:** `int`

<a id="setinfluence"></a>

#### `SetInfluence(nNPC, nInfluence)`

DJS-OEI 1/29/2004
Sets the PC's influence on the alignment of a CNPC.
Parameters:
nNPC - NPC_* constant identifying the CNPC we're interested in.
If this character is not an available party member, nothing
will happen.
nInfluence - The new value for the influence on this CNPC.

**Parameters:**

- `nNPC`: `int`
- `nInfluence`: `int`

<a id="modifyinfluence"></a>

#### `ModifyInfluence(nNPC, nModifier)`

DJS-OEI 1/29/2004
Modifies the PC's influence on the alignment of a CNPC.
Parameters:
nNPC - NPC_* constant identifying the CNPC we're interested in.
If this character is not an available party member, nothing
will happen.
nModifier - The modifier to the current influence on this CNPC.
This may be a negative value to reduce the influence.

**Parameters:**

- `nNPC`: `int`
- `nModifier`: `int`

<a id="getracialsubtype"></a>

#### `GetRacialSubType(oTarget)`

FAK - OEI 2/3/04
returns the racial sub-type of the oTarget object

**Parameters:**

- `oTarget`: `object`

**Returns:** `int`

<a id="incrementglobalnumber"></a>

#### `IncrementGlobalNumber(sIdentifier, nAmount)`

DJS-OEI 2/3/2004
Increases the value of the given global number by the given amount.
This function only works with Number type globals, not booleans. It
will fail with a warning if the final amount is greater than the max
of 127.

**Parameters:**

- `sIdentifier`: `string`
- `nAmount`: `int`

<a id="decrementglobalnumber"></a>

#### `DecrementGlobalNumber(sIdentifier, nAmount)`

DJS-OEI 2/3/2004
Decreases the value of the given global number by the given amount.
This function only works with Number type globals, not booleans. It
will fail with a warning if the final amount is less than the minimum
of -128.

**Parameters:**

- `sIdentifier`: `string`
- `nAmount`: `int`

<a id="swmg_setjumpspeed"></a>

#### `SWMG_SetJumpSpeed(fSpeed)`

FAK - OEI 2/11/04
SWMG_SetJumpSpeed -- the sets the 'jump speed' for the swoop
bike races. Gravity will act upon this velocity.

**Parameters:**

- `fSpeed`: `float`

<a id="yavinhackdoorclose"></a>

#### `YavinHackDoorClose(oCreature)`

808

**Parameters:**

- `oCreature`: `object`

<a id="isstealthed"></a>

#### `IsStealthed(oCreature)`

END PC CODE MERGER
810
DJS-OEI 3/8/2004
Determines if the given creature is in Stealth mode or not.
0 = Creature is not stealthed.
1 = Creature is stealthed.
This function will return 0 for any non-creature.

**Parameters:**

- `oCreature`: `object`

**Returns:** `int`

<a id="ismeditating"></a>

#### `IsMeditating(oCreature)`

811
DJS-OEI 3/12/2004
Determines if the given creature is using any Meditation Tree
Force Power.
0 = Creature is not meditating.
1 = Creature is meditating.
This function will return 0 for any non-creature.

**Parameters:**

- `oCreature`: `object`

**Returns:** `int`

<a id="isintotaldefense"></a>

#### `IsInTotalDefense(oCreature)`

812
DJS-OEI 3/16/2004
Determines if the given creature is using the Total Defense
Stance.
0 = Creature is not in Total Defense.
1 = Creature is in Total Defense.
This function will return 0 for any non-creature.

**Parameters:**

- `oCreature`: `object`

**Returns:** `int`

<a id="sethealtarget"></a>

#### `SetHealTarget(oidHealer, oidTarget)`

813
RWT-OEI 03/19/04
Stores a Heal Target for the Healer AI script. Should probably
not be used outside of the Healer AI script.

**Parameters:**

- `oidHealer`: `object`
- `oidTarget`: `object`

<a id="gethealtarget"></a>

#### `GetHealTarget(oidHealer)`

814
RWT-OEI 03/19/04
Retrieves the Heal Target for the Healer AI script. Should probably
not be used outside of the Healer AI script.

**Parameters:**

- `oidHealer`: `object`

**Returns:** `object`

<a id="getrandomdestination"></a>

#### `GetRandomDestination(oCreature, rangeLimit)`

815
RWT-OEI 03/23/04
Returns a vector containing a random destination that the
given creature can walk to that's within the range of the
passed parameter.

**Parameters:**

- `oCreature`: `object`
- `rangeLimit`: `int`

**Returns:** `vector`

<a id="isformactive"></a>

#### `IsFormActive(oCreature, nFormID)`

816
DJS-OEI 3/25/2004
Returns whether the given creature is currently in the
requested Lightsaber/Consular Form and can make use of
its benefits. This function will perform trumping checks
and lightsaber-wielding checks for those Forms that require
them.

**Parameters:**

- `oCreature`: `object`
- `nFormID`: `int`

**Returns:** `int`

<a id="getspellformmask"></a>

#### `GetSpellFormMask(nSpellID)`

817
DJS-OEI 3/28/2004
Returns the Form Mask of the requested spell. This is used
to determine if a spell is affected by various Forms, usually
Consular forms that modify duration/range.

**Parameters:**

- `nSpellID`: `int`

**Returns:** `int`

<a id="getspellbaseforcepointcost"></a>

#### `GetSpellBaseForcePointCost(nSpellID)`

818
DJS-OEI 3/29/2004
Return the base number of Force Points required to cast
the given spell. This does not take into account modifiers
of any kind.

**Parameters:**

- `nSpellID`: `int`

**Returns:** `int`

<a id="setkeepstealthindialog"></a>

#### `SetKeepStealthInDialog(nStealthState)`

819
RWT-OEI 04/05/04
Setting this to TRUE makes it so that the Stealth status is
left on characters even when entering cutscenes. By default,
stealth is removed from anyone taking part in a cutscene.
ALWAYS set this back to FALSE on every End Dialog node in
the cutscene you wanted to stay stealthed in. This isn't a
flag that should be left on indefinitely. In fact, it isn't
saved, so needs to be set/unset on a case by case basis.

**Parameters:**

- `nStealthState`: `int`

<a id="haslineofsight"></a>

#### `HasLineOfSight(vSource, vTarget, oSource=1, oTarget=1)`

820
RWT-OEI 04/06/04
This returns TRUE or FALSE if there is a clear line of sight from
the source vector to the target vector. This is used in the AI to
help the creatures using ranged weapons find better places to shoot
when the player moves out of sight.

**Parameters:**

- `vSource`: `vector`
- `vTarget`: `vector`
- `oSource`: `object` (default: `1`)
- `oTarget`: `object` (default: `1`)

**Returns:** `int`

<a id="showdemoscreen"></a>

#### `ShowDemoScreen(sTexture, nTimeout, nDisplayString, nDisplayX, nDisplayY)`

821
FAK - OEI 5/3/04
ShowDemoScreen, displays a texture, timeout, string and xy for string

**Parameters:**

- `sTexture`: `string`
- `nTimeout`: `int`
- `nDisplayString`: `int`
- `nDisplayX`: `int`
- `nDisplayY`: `int`

**Returns:** `int`

<a id="forceheartbeat"></a>

#### `ForceHeartbeat(oCreature)`

822
DJS-OEI 5/4/2004
Forces a Heartbeat on the given creature. THIS ONLY WORKS FOR CREATURES
AT THE MOMENT. This heartbeat should force perception updates to occur.

**Parameters:**

- `oCreature`: `object`

<a id="isrunning"></a>

#### `IsRunning(oCreature)`

824
FAK - OEI 5/7/04
gets the walk state of the creature: 0 walk or standing, 1 is running

**Parameters:**

- `oCreature`: `object`

**Returns:** `int`

<a id="swmg_playerapplyforce"></a>

#### `SWMG_PlayerApplyForce(vForce)`

825
FAK - OEI 5/24/04
applies a velocity to the player object

**Parameters:**

- `vForce`: `vector`

<a id="setforfeitconditions"></a>

#### `SetForfeitConditions(nForfeitFlags)`

DJS-OEI 6/12/2004

**Parameters:**

- `nForfeitFlags`: `int`

<a id="getlastforfeitviolation"></a>

#### `GetLastForfeitViolation()`

827
DJS-OEI 6/12/2004
This function returns the last FORFEIT_* condition that the player
has violated.

**Returns:** `int`

<a id="modifyreflexsavingthrowbase"></a>

#### `ModifyReflexSavingThrowBase(aObject, aModValue)`

828
AWD-OEI 6/21/2004
This function does not return a value.
This function modifies the BASE value of the REFLEX saving throw for aObject

**Parameters:**

- `aObject`: `object`
- `aModValue`: `int`

<a id="modifyfortitudesavingthrowbase"></a>

#### `ModifyFortitudeSavingThrowBase(aObject, aModValue)`

829
AWD-OEI 6/21/2004
This function does not return a value.
This function modifies the BASE value of the FORTITUDE saving throw for aObject

**Parameters:**

- `aObject`: `object`
- `aModValue`: `int`

<a id="modifywillsavingthrowbase"></a>

#### `ModifyWillSavingThrowBase(aObject, aModValue)`

830
AWD-OEI 6/21/2004
This function does not return a value.
This function modifies the BASE value of the WILL saving throw for aObject

**Parameters:**

- `aObject`: `object`
- `aModValue`: `int`

<a id="getscriptstringparameter"></a>

#### `GetScriptStringParameter()`

DJS-OEI 6/21/2004
831
This function will return the one CExoString parameter
allowed for the currently running script.

**Returns:** `string`

<a id="getobjectpersonalspace"></a>

#### `GetObjectPersonalSpace(aObject)`

832
AWD-OEI 6/29/2004
This function returns the personal space value of an object

**Parameters:**

- `aObject`: `object`

**Returns:** `float`

<a id="adjustcreatureattributes"></a>

#### `AdjustCreatureAttributes(oObject, nAttribute, nAmount)`

833
AWD-OEI 7/06/2004
This function adjusts a creatures stats.
oObject is the creature that will have it's attribute adjusted
The following constants are acceptable for the nAttribute parameter:
ABILITY_STRENGTH
ABILITY_DEXTERITY
ABILITY_CONSTITUTION
ABILITY_INTELLIGENCE
ABILITY_WISDOM
ABILITY_CHARISMA
nAmount is the integer vlaue to adjust the stat by (negative values will work).

**Parameters:**

- `oObject`: `object`
- `nAttribute`: `int`
- `nAmount`: `int`

<a id="setcreatureailevel"></a>

#### `SetCreatureAILevel(oObject, nPriority)`

834
AWD-OEI 7/08/2004
This function raises a creature's priority level.

**Parameters:**

- `oObject`: `object`
- `nPriority`: `int`

<a id="resetcreatureailevel"></a>

#### `ResetCreatureAILevel(oObject)`

835
AWD-OEI 7/08/2004
This function raises a creature's priority level.

**Parameters:**

- `oObject`: `object`

<a id="addavailablepupbytemplate"></a>

#### `AddAvailablePUPByTemplate(nPUP, sTemplate)`

836
RWT-OEI 07/17/04
This function adds a Puppet to the Puppet Table by
template.
Returns 1 if successful, 0 if there was an error
This does not spawn the puppet or anything. It just
adds it to the party table and makes it available for
use down the line. Exactly like AddAvailableNPCByTemplate

**Parameters:**

- `nPUP`: `int`
- `sTemplate`: `string`

**Returns:** `int`

<a id="addavailablepupbyobject"></a>

#### `AddAvailablePUPByObject(nPUP, oPuppet)`

837
RWT-OEI 07/17/04
This function adds a Puppet to the Puppet Table by
creature ID
Returns 1 if successful, 0 if there was an error
This does not spawn the puppet or anything. It just
adds it to the party table and makes it available for
use down the line. Exactly like AddAvailableNPCByTemplate

**Parameters:**

- `nPUP`: `int`
- `oPuppet`: `object`

**Returns:** `int`

<a id="assignpup"></a>

#### `AssignPUP(nPUP, nNPC)`

838
RWT-OEI 07/17/04
This function assigns a PUPPET constant to a
Party NPC.  The party NPC -MUST- be in the game
before calling this.
Both the PUP and the NPC have
to be available in their respective tables
Returns 1 if successful, 0 if there was an error

**Parameters:**

- `nPUP`: `int`
- `nNPC`: `int`

**Returns:** `int`

<a id="spawnavailablepup"></a>

#### `SpawnAvailablePUP(nPUP, lLocation)`

839
RWT-OEI 07/17/04
This function spawns a Party PUPPET.
This must be used whenever you want a copy
of the puppet around to manipulate in the game
since the puppet is stored in the party table
just like NPCs are.  Once a puppet is assigned
to a party NPC (see AssignPUP), it will spawn
or disappear whenever its owner joins or leaves
the party.
This does not add it to the party automatically,
just like SpawnNPC doesn't. You must call AddPuppet()
to actually add it to the party

**Parameters:**

- `nPUP`: `int`
- `lLocation`: `location`

**Returns:** `object`

<a id="getpupowner"></a>

#### `GetPUPOwner(oPUP=0)`

841
RWT-OEI 07/19/04
This returns the object ID of the puppet's owner.
The Puppet's owner must exist and must be in the party
in order to be found.
Returns invalid object Id if the owner cannot be found.

**Parameters:**

- `oPUP`: `object` (default: `0`)

**Returns:** `object`

<a id="getispuppet"></a>

#### `GetIsPuppet(oPUP=0)`

842
RWT-OEI 07/19/04
Returns 1 if the creature is a Puppet in the party.
Otherwise returns 0. It is possible for a 'party puppet'
to exist without actually being in the party table.
such as when SpawnAvailablePUP is used without subsequently
using AddPartyPuppet to add the newly spawned puppet to
the party table. A puppet in that in-between state would
return 0 from this function

**Parameters:**

- `oPUP`: `object` (default: `0`)

**Returns:** `int`

<a id="getispartyleader"></a>

#### `GetIsPartyLeader(oCharacter=0)`

844
RWT-OEI 07/21/04
Returns TRUE if the object ID passed is the character
that the player is actively controlling at that point.
Note that this function is *NOT* able to return correct
information during Area Loading since the player is not
actively controlling anyone at that point.

**Parameters:**

- `oCharacter`: `object` (default: `0`)

**Returns:** `int`

<a id="removenpcfrompartytobase"></a>

#### `RemoveNPCFromPartyToBase(nNPC)`

846
JAB-OEI 07/22/04
Will remove the CNPC from the 3 person party, and remove
him/her from the area, effectively sending the CNPC back
to the base. The CNPC data is still stored in the
party table, and calling this function will not destroy
the CNPC in any way.
Returns TRUE for success.

**Parameters:**

- `nNPC`: `int`

**Returns:** `int`

<a id="creatureflourishweapon"></a>

#### `CreatureFlourishWeapon(oObject)`

847
AWD-OEI 7/22/2004
This causes a creature to flourish with it's currently equipped weapon.

**Parameters:**

- `oObject`: `object`

<a id="changeobjectappearance"></a>

#### `ChangeObjectAppearance(oObjectToChange, nAppearance)`

850
ChangeObjectAppearance
oObjectToChange = Object to change appearance of

**Parameters:**

- `oObjectToChange`: `object`
- `nAppearance`: `int`

<a id="getisxbox"></a>

#### `GetIsXBox()`

851
GetIsXBox
Returns TRUE if this script is being executed on the X-Box. Returns FALSE
if this is the PC build.

**Returns:** `int`

<a id="playoverlayanimation"></a>

#### `PlayOverlayAnimation(oTarget, nAnimation)`

854
DJS-OEI 8/29/2004
PlayOverlayAnimation
This function will play an overlay animation on a character
even if the character is moving. This does not cause an action
to be placed on the queue. The animation passed in must be
designated as an overlay in Animations.2DA.

**Parameters:**

- `oTarget`: `object`
- `nAnimation`: `int`

<a id="unlockallsongs"></a>

#### `UnlockAllSongs()`

855
RWT-OEI 08/30/04
UnlockAllSongs
Calling this will set all songs as having been unlocked.
It is INTENDED to be used in the end-game scripts to unlock
any end-game songs as well as the KotOR1 sound track.

<a id="disablemap"></a>

#### `DisableMap(nFlag=0)`

856
RWT-OEI 08/31/04
Passing TRUE into this function turns off the player's maps.
Passing FALSE into this function re-enables them. This change
is permanent once called, so it is important that there *is*
a matching call to DisableMap(FALSE) somewhere or else the

**Parameters:**

- `nFlag`: `int` (default: `0`)

<a id="detonatemine"></a>

#### `DetonateMine(oMine)`

857
RWT-OEI 08/31/04
This function schedules a mine to play its DETONATION
animation once it is destroyed. Note that this detonates
the mine immediately but has nothing to do with causing
the mine to do any damage to anything around it. To
get the mine to damage things around it when it detonates
do:
AssignCommand(<mine>,ExecuteScript( "k_trp_generic",<mine>));
right before you call DetonateMine(). By my experience so far

**Parameters:**

- `oMine`: `object`

<a id="disablehealthregen"></a>

#### `DisableHealthRegen(nFlag=0)`

858
RWT-OEI 09/06/04
This function turns off the innate health regeneration that all party
members have. The health regen will *stay* off until it is turned back
on by passing FALSE to this function.

**Parameters:**

- `nFlag`: `int` (default: `0`)

<a id="setcurrentform"></a>

#### `SetCurrentForm(oCreature, nFormID)`

859
DJS-OEI 9/7/2004
This function sets the current Jedi Form on the given creature. This
call will do nothing if the target does not know the Form itself.

**Parameters:**

- `oCreature`: `object`
- `nFormID`: `int`

<a id="setdisabletransit"></a>

#### `SetDisableTransit(nFlag=0)`

860
RWT-OEI 09/09/04
This will disable or enable area transit

**Parameters:**

- `nFlag`: `int` (default: `0`)

<a id="setinputclass"></a>

#### `SetInputClass(nClass)`

861
RWT-OEI 09/09/04
This will set the specific input class.
The valid options are:
0 - Normal PC control
1 - Mini game control
2 - GUI control
3 - Dialog Control
4 - Freelook control

**Parameters:**

- `nClass`: `int`

<a id="setforcealwaysupdate"></a>

#### `SetForceAlwaysUpdate(oObject, nFlag)`

862
RWT-OEI 09/15/04
This script allows an object to recieve updates even if it is outside
the normal range limit of 250.0f meters away from the player. This should
ONLY be used for cutscenes that involve objects that are more than 250
meters away from the player. It needs to be used on a object by object
basis.
This flag should *always* be set to false once the cutscene it is needed
for is over, or else the game will spend CPU time updating the object
when it doesn't need to.
For questions on use of this function, or what its purpose is, check
with me.

**Parameters:**

- `oObject`: `object`
- `nFlag`: `int`

<a id="enablerain"></a>

#### `EnableRain(nFlag)`

863
RWT-OEI 09/15/04
This function enables or disables rain

**Parameters:**

- `nFlag`: `int`

<a id="displaymessagebox"></a>

#### `DisplayMessageBox(nStrRef, sIcon=)`

864
RWT-OEI 09/27/04
This function displays the generic Message Box with the strref
message in it
sIcon is the resref for an icon you would like to display.

**Parameters:**

- `nStrRef`: `int`
- `sIcon`: `string` (default: ``)

<a id="displaydatapad"></a>

#### `DisplayDatapad(oDatapad)`

865
RWT-OEI 09/28/04
This function displays a datapad popup. Just pass it the
object ID of a datapad.

**Parameters:**

- `oDatapad`: `object`

<a id="removeheartbeat"></a>

#### `RemoveHeartbeat(oPlaceable)`

866
CTJ-OEI 09-29-04
Removes the heartbeat script on the placeable.  Useful for
placeables whose contents get populated in the heartbeat
script and then the heartbeat no longer needs to be called.

**Parameters:**

- `oPlaceable`: `object`

<a id="adjustcreatureskills"></a>

#### `AdjustCreatureSkills(oObject, nSkill, nAmount)`

869
DJS-OEI 10/9/2004
This function adjusts a creature's skills.
oObject is the creature that will have its skill adjusted
The following constants are acceptable for the nSkill parameter:
SKILL_COMPUTER_USE
SKILL_DEMOLITIONS
SKILL_STEALTH
SKILL_AWARENESS
SKILL_PERSUADE
SKILL_REPAIR
SKILL_SECURITY
SKILL_TREAT_INJURY
nAmount is the integer value to adjust the stat by (negative values will work).

**Parameters:**

- `oObject`: `object`
- `nSkill`: `int`
- `nAmount`: `int`

<a id="enablerendering"></a>

#### `EnableRendering(oObject, bEnable)`

871
DJS-OEI 10/15/2004
This function will allow the caller to modify the rendering behavior
of the target object.
oObject - The object to change rendering state on.
bEnable - If 0, the object will stop rendering. Else, the object will render.

**Parameters:**

- `oObject`: `object`
- `bEnable`: `int`

<a id="getcombatactionspending"></a>

#### `GetCombatActionsPending(oCreature)`

872
RWT-OEI 10/19/04
This function returns TRUE if the creature has actions in its
Combat Action queue.

**Parameters:**

- `oCreature`: `object`

**Returns:** `int`

<a id="savenpcbyobject"></a>

#### `SaveNPCByObject(nNPC, oidCharacter)`

873
RWT-OEI 10/26/04
This function saves the party member at that index with the object
that is passed in.

**Parameters:**

- `nNPC`: `int`
- `oidCharacter`: `object`

<a id="savepupbyobject"></a>

#### `SavePUPByObject(nPUP, oidPuppet)`

874
RWT-OEI 10/26/04
This function saves the party puppet at that index with the object
that is passed in. For the Remote, just use '0' for nPUP

**Parameters:**

- `nPUP`: `int`
- `oidPuppet`: `object`

<a id="getisplayermadecharacter"></a>

#### `GetIsPlayerMadeCharacter(oidCharacter)`

875
RWT-OEI 10/29/04
Returns TRUE if the object passed in is the character that the player
made at the start of the game

**Parameters:**

- `oidCharacter`: `object`

**Returns:** `int`


### Party Management

<a id="addpartypuppet"></a>

#### `AddPartyPuppet(nPUP, oidCreature)`

840
RWT-OEI 07/18/04
This adds an existing puppet object to the party. The
puppet object must already exist via SpawnAvailablePUP
and must already be available via AddAvailablePUP*
functions.

**Parameters:**

- `nPUP`: `int`
- `oidCreature`: `object`

**Returns:** `int`

<a id="getpartyleader"></a>

#### `GetPartyLeader()`

845
RWT-OEI 07/21/04
Returns the object ID of the character that the player
is actively controlling. This is the 'Party Leader'.
Returns object Invalid on error
Note that this function is *NOT* able to return correct
information during Area Loading since the player is not
actively controlling anyone at that point.

**Returns:** `object`


### Skills and Feats

<a id="getskillrankbase"></a>

#### `GetSkillRankBase(nSkill, oObject=0)`

870
DJS-OEI 10/10/2004
This function returns the base Skill Rank for the requested
skill. It does not include modifiers from effects/items.
The following constants are acceptable for the nSkill parameter:
SKILL_COMPUTER_USE
SKILL_DEMOLITIONS
SKILL_STEALTH
SKILL_AWARENESS
SKILL_PERSUADE
SKILL_REPAIR
SKILL_SECURITY
SKILL_TREAT_INJURY
oObject is the creature that will have its skill base returned.

**Parameters:**

- `nSkill`: `int`
- `oObject`: `object` (default: `0`)

**Returns:** `int`


