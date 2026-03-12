# Indoor area room layout and walkmesh guide

Goal: explain the practical workflow for adding, reusing, moving, and debugging indoor area rooms in KotOR, with special focus on layout, walkmeshes, roomlinks, doors, and testing.

## What this guide is for

Use this guide when you are trying to do any of the following:

- Reuse an existing room model in a new place
- Add a brand-new room to an existing module
- Make two rooms connect so the player can actually walk between them
- Replace fake door textures with real door transitions
- Understand which files matter when indoor area modding goes wrong

This guide is intentionally written as a workflow document rather than a binary format reference. For the underlying format details, use the linked reference pages.

### Quick start

In short: extract the area's **[LYT](LYT-File-Format)**, **[VIS](VIS-File-Format)**, and the room models and walkmeshes you need → load the area via the **layout workflow** (Area Tools), not by importing a single room model → edit the seam and **roomlinks** for both sides → enable **Export WOK File** when exporting → compile ASCII back to binary → test in-game. Transition IDs in the walkmesh are 0-based **room indices** from the **[LYT](LYT-File-Format)** order; see [BWM File Format — Edges](BWM-File-Format#edges) and [LYT File Format — Room definitions](LYT-File-Format#room-definitions).

## Before you start

This is a hard part of KotOR modding. If you are stuck, that does not mean you are missing something obvious. The workflow is awkward because several different resources have to agree at the same time, and older community tools were built around assumptions that are not obvious to new modders. In short, the tooling is not where we need it to be yet. Nonetheless, here is a guide, based on everything I know.

If you remember only one thing before starting, remember this:

- **Indoor room crossing is a layout problem, a walkmesh problem, and a transition-link problem at the same time.**

It is almost never just one isolated mesh-editing task.

## Prerequisites

You do not need every tool in existence, but you do need a workflow that covers four jobs:

1. Extract the area's *room resources*.
2. Load or edit the area with layout awareness.
3. Export updated *walkmesh* data.
4. Compile edited ASCII back to binary.

In the source material, the most repeatedly recommended combination is:

- **KOTORMax** For area/layout-aware editing and roomlink work
- **MDLEdit** for *ASCII* and binary conversion

You may still use *Blender* with *KotorBlender* (specifically use [**KotorBlender**](https://github.com/OldRepublicDevs/kotorblender) as [seedhartha's](https://github.com/seedhartha) repo is no longer maintained). or other tools for geometry work, but if your specific goal is **make room crossing actually function**, the current evidence still points back to a roomlink-capable workflow.

**You're ready when:**

- [ ] You have a working folder with the area's **[LYT](LYT-File-Format)**, **[VIS](VIS-File-Format)**, and the room models and walkmeshes you need (see [LYT File Format](LYT-File-Format), [VIS File Format](VIS-File-Format), [BWM File Format](BWM-File-Format)).
- [ ] Room models you will edit are (or can be) converted to ASCII for the layout workflow.
- [ ] **KOTORMax** (or another layout-capable workflow) and **[MDLEdit](https://deadlystream.com/files/file/1150-mdledit/)** (or a modern ASCII compiler) are available.

## Quick Glossary

These terms get mixed together a lot, so it helps to separate them early.

### Room

A room is one positioned area chunk in the **[LYT](LYT-File-Format)**. In indoor modules, each room usually has its own model and its own *walkmesh*.

### Walkmesh *seam*

The *seam* is the physical boundary where two room walkmeshes meet. The seam has to line up geometrically.

### Roomlink / *transition edge*

This is the logic that says "if the player crosses this edge, they move into room X." A seam can look perfect and still fail if the *roomlink* is wrong.

### *Door hook*

A **[LYT](LYT-File-Format)** *door hook* is a placement reference. It is **not** the same thing as a *roomlink*, and it is **not** the thing that makes crossing work.

### AABB

For indoor room work, AABB matters because room models can contain collision-related AABB data in the **[MDL](MDL-MDX-File-Format)**. The **[WOK](BWM-File-Format)** still carries the main pathfinding and room transition information.

## The mental model first

Before touching tools, keep this model in mind:

1. A room's **visual model** is the room **[MDL/MDX](MDL-MDX-File-Format)**.
2. A room's **main gameplay walkmesh** is the **[WOK](BWM-File-Format)**.
3. A room can also contain **AABB collision data inside the MDL**, which matters for camera collision and related engine behavior.
4. The **[LYT](LYT-File-Format)** places rooms into the area and establishes their order.
5. The **[VIS](VIS-File-Format)** decides which rooms are visible from which other rooms.
6. The **roomlinks / *transition edges*** in the *walkmesh* decide whether crossing an edge moves the player into another room.

The biggest trap is assuming that visual alignment is enough. It is not. Two rooms can line up perfectly in 3D space and still fail in-game because the transition data is wrong.

## How walkmeshes, models, layout, and VIS work

This section explains in plain terms what each piece does and how they fit together. For full format details and field-by-field descriptions, use the linked reference pages.

**Models (**[MDL/MDX](MDL-MDX-File-Format)**)** — The room’s visible geometry: walls, floor, ceiling, and any embedded collision boxes (AABB) the engine uses for things like camera collision. The model says *what the room looks like* and where its origin is. It does **not** by itself define where the player can walk or how rooms connect. For more information, see [MDL/MDX File Format](MDL-MDX-File-Format).

**Walkmeshes (**[WOK](BWM-File-Format)**)** — A separate, simplified “floor” made of triangles that defines where the player and NPCs can stand and walk. Each room has its own **[WOK](BWM-File-Format)**. The *walkmesh* stores which edges are boundaries and, on those edges, a **transition ID** (a number pointing to another room). When the player crosses a boundary edge, the engine uses that ID to move them into the correct room. So the *walkmesh* answers *where you can walk* and *which room you enter when you cross a seam*. For more information, see [BWM File Format](BWM-File-Format).

**Layout (**[LYT](LYT-File-Format)**)** — A text file that lists every room in the area and its position (and rotation) in world space. The **order** of rooms in this list is what the game uses as the room index: first room = 0, second = 1, and so on. Those same numbers are the transition IDs stored in the *walkmesh*. So the **[LYT](LYT-File-Format)** answers *where each room is* and *what number identifies each room* for transitions. For more information, see [LYT File Format](LYT-File-Format).

**Visibility (**[VIS](VIS-File-Format)**)** — A file that describes which rooms are visible from which other rooms. The engine uses it to avoid drawing rooms that are behind walls or too far away. It affects only **what is drawn**, not collision or walking. Getting the layout and *walkmesh* right is more important first; **[VIS](VIS-File-Format)** can be simplified or omitted while you debug crossing. For more information, see [VIS File Format](VIS-File-Format).

**How they work together** — The **[LYT](LYT-File-Format)** places each room model and its **[WOK](BWM-File-Format)** in the world. When you cross the boundary between two rooms, the *walkmesh’s* transition ID (which matches the **[LYT](LYT-File-Format)** room order) tells the engine which room you entered. The **[VIS](VIS-File-Format)** file then controls which of those rooms are rendered from your current position. All four have to be consistent for an area to look and behave correctly.

**Format and implementation reference** — The wiki has full specifications and PyKotor implementation code for each format:

| What | Format reference | PyKotor implementation |
|------|------------------|------------------------|
| Walkmeshes (**[WOK](BWM-File-Format)**) | [BWM File Format](BWM-File-Format) | [`resource/formats/bwm/`](https://github.com/OldRepublicDevs/PyKotor/tree/master/Libraries/PyKotor/src/pykotor/resource/formats/bwm) |
| Layout (**[LYT](LYT-File-Format)**) | [LYT File Format](LYT-File-Format) | [`resource/formats/lyt/`](https://github.com/OldRepublicDevs/PyKotor/tree/master/Libraries/PyKotor/src/pykotor/resource/formats/lyt) |
| Visibility (**[VIS](VIS-File-Format)**) | [VIS File Format](VIS-File-Format) | [`resource/formats/vis/`](https://github.com/OldRepublicDevs/PyKotor/tree/master/Libraries/PyKotor/src/pykotor/resource/formats/vis) |
| Room Models (**[MDL/MDX](MDL-MDX-File-Format)**) | [MDL/MDX File Format](MDL-MDX-File-Format) | [`resource/formats/mdl/`](https://github.com/OldRepublicDevs/PyKotor/tree/master/Libraries/PyKotor/src/pykotor/resource/formats/mdl) |

## The files that matter

### Room model: **[MDL/MDX](MDL-MDX-File-Format)**

The room model contains the visible geometry. In practice, room models may also carry **embedded walkmesh/AABB data** used by the engine for **camera collision** and related spatial queries. **Camera collision will not work correctly without this embedded data** in the room **[MDL/MDX](MDL-MDX-File-Format)**.

Indoor areas therefore have **two** walkmesh-related data sources: the standalone **[WOK](BWM-File-Format)** file (pathfinding, room transitions, adjacency, perimeters) and the **Walkmesh/AABB data inside the room MDL** (camera collision and related client-side behavior). The *Odyssey* engine reuses architecture from the Aurora/NWN codebase, which was originally built for client–server multiplayer; traces of that separation remain in the executable (e.g. in debug strings and code paths). In practice, the **[WOK](BWM-File-Format)** is the primary source for pathfinding and room-to-room transitions, while the **[MDL/MDX](MDL-MDX-File-Format)**-embedded data is required for correct *camera collision*. Both must be consistent for full correctness. For more detail, see [BWM File Format](BWM-File-Format) and [MDL/MDX File Format](MDL-MDX-File-Format) (AABB mesh nodes).

### Room walkmesh: **[WOK](BWM-File-Format)**

The **[WOK](BWM-File-Format)** is the main area walkmesh. It contains walkable faces, **adjacency data**, **perimeter edges**, and **transition IDs** that tell the engine which neighboring room a boundary edge leads to.

**Materials and *Walkability*** — Each face has a material index that references [`surfacemat.2da`](2DA-surfacemat). That table defines the surface type and, in the **walk** column, whether the face is walkable. Non-walkable materials are used for walls and blocked regions; walkable materials define the floor and traversable thresholds.

**Adjacency and Perimeter** — The **[WOK](BWM-File-Format)** stores a **list of *adjacent* walkable faces** *per face* (which faces share which edges). From this, the engine reconstructs which faces touch and on which sides. An edge that has **no** adjacent walkable face is a **perimeter edge** — a boundary of the walkable region. The **perimeter list** works with this adjacency data to define closed boundary loops. A perimeter edge that forms the **room boundary** (one the player can walk across) carries a **transition ID**: the **0-based index of the adjacent room** in the area’s room list — i.e. the order of that room in the **[LYT](LYT-File-Format)**. For full binary layout, see [BWM File Format](BWM-File-Format) (adjacencies, edges, perimeters).

**AABB tree and boundary alignment** — The **[WOK](BWM-File-Format)** also includes an **AABB tree** for fast spatial queries. At boundary edges the engine relies on AABB nodes and their connectivity (e.g. significant plane and child pointers) being **correctly aligned** to the perimeter and face data. Misaligned or **degenerate AABB** structures at seams can cause "can’t cross" or stuck behavior even when geometry and transition IDs look correct. Tools that do not fully replicate the binary AABB/perimeter structure (e.g. vertex-color or hash-based roomlink storage) may work in many cases but can produce edge-case failures in-game. For authoritative behavior and layout, see [BWM File Format](BWM-File-Format) and [Game Engine BWM/AABB Implementation](Game-Engine-BWM-AABB-Implementation).

### Layout: **[LYT](LYT-File-Format)**

The **[LYT](LYT-File-Format)** positions rooms in world space. Just as importantly for room transitions, the **order of rooms in the **[LYT](LYT-File-Format)** defines the 0-based room index** used by *walkmesh transition IDs*.

If you add, remove, or reorder rooms, old *transition IDs* may become wrong even if the geometry still looks correct.

### Visibility: **[VIS](VIS-File-Format)**

The **[VIS](VIS-File-Format)** controls room-to-room visibility, not collision or *transitions*. When you are first trying to make a new room work, it is often useful to simplify **[VIS](VIS-File-Format)** or temporarily leave it out so you can isolate layout and walkmesh problems first.

### Surface materials: [surfacemat.2da](2DA-surfacemat)

Walkmesh faces in the **[WOK](BWM-File-Format)** store a **material index** per face. That index points into [surfacemat.2da](2DA-surfacemat), which defines the surface type and, in the **`walk`** column, whether the face is walkable. The engine uses this at runtime to decide where the player and NPCs can stand and path. If the seam between rooms is painted with a non-walkable material (or the wrong row), the engine may treat the boundary as blocked even when geometry and *transition IDs* are correct. For format details, see [2DA surfacemat](2DA-surfacemat) and [BWM File Format — Materials](BWM-File-Format#materials).

### **[GIT](GFF-GIT)** and **[ARE](GFF-ARE)**

The **[GIT](GFF-GIT)** handles dynamic things such as doors, placeables, creatures, triggers, and *transitions*. The **[ARE](GFF-ARE)** room entries are useful for room-related data such as ambient audio, but they do not by themselves make room crossing work.

One common misunderstanding is to treat **[LYT](LYT-File-Format)** *door hooks* as the thing that creates *room-to-room* traversal. They do not. They are placement references. Actual crossing still depends on *walkmesh transitions* and the rest of the area setup.

## What has to agree before room crossing works

For *room crossing* to work reliably, all of these must agree:

1. The rooms must be positioned correctly in the layout.
2. The walkmesh seam between both rooms must physically line up.
3. The roomlinks must point to the correct neighboring room indices.
4. The **[LYT](LYT-File-Format)** and **[VIS](VIS-File-Format)** must include the correct rooms.
5. The room's updated **[WOK](BWM-File-Format)** must actually be exported.
6. Any edited ASCII resources must be compiled back to binary.

If you only do the first two steps, you can get a *room* that looks correct and still blocks crossing.

## Recommended workflow

The currently documented community workflow is strongly centered on **loading the whole area layout first**, then editing inside that *layout-aware* scene. This matters because *roomlinks* depend on *room* context, not just on the local *mesh*.

### Step 1: Decide what kind of change you are making

There are three common jobs:

- **Reusing an existing room in a new place**
- **Creating a new custom room**
- **Turning a fake doorway into a real transition**

All three use the same general pipeline, but the amount of *walkmesh* and *door* work increases from left to right.

### Step 2: build a complete working folder

For serious indoor *room* work, do not operate on isolated files if you can avoid it. Gather the area resources into one working folder:

- the *Room Models* you want to work on
- the corresponding *walkmeshes*
- the area's **[LYT](LYT-File-Format)**
- the area's **[VIS](VIS-File-Format)**
- Any related *door* resources if you are working on doors

This matches the practical workflow described by modders working on new *rooms*: keep the layout, visibility, models, and walkmeshes together so the editing tool has full context.

As a practical rule, also consider converting the *adjoining rooms* you plan to test against into the same editable form, not just the one *room* you care about. That reduces variables when you are debugging a seam.

### Step 3: Use a *layout-aware* workflow, ***NOT*** an *isolated model* workflow

This is the single most important practical rule:

- **Load the area through the layout workflow**
- **Do not try to solve *room transitions* by importing one *room model* in isolation**

Community guidance around **KOTORMax** is explicit on this point: you load a **[LYT](LYT-File-Format)** via *Area Tools*. Trying to feed a **[LYT](LYT-File-Format)** file into a *model importer* is what produces the familiar *"invalid ascii"* style failure, because the importer expects **Model [MDL/MDX](MDL-MDX-File-Format) ASCII**, not a **Layout [LYT](LYT-File-Format) file**.

> **Warning:** Loading the **[LYT](LYT-File-Format)** via the model importer causes **"invalid ascii"** errors. Always use **Area Tools** / **layout workflow**.

Related rule: **Use Layout Position** is not a substitute for loading the **[LYT](LYT-File-Format)**. That option is only useful when the *model ASCII* already contains *layout-position data* from a previous export. Vanilla-decompiled *room models* generally do not have that embedded data.

### Step 4: Convert models to the form your editor expects

For the currently documented **[KOTORMax](https://github.com/OldRepublicDevs/KOTORMax)**-centered workflow, room editing normally happens through the *ASCII model* pipeline:

1. Extract the **binary [MDL/MDX](MDL-MDX-File-Format) model resources**.
2. Convert them to **ASCII** using a modern compiler/decompiler workflow (mdledit, for now).
3. Load the [LYT](LYT-File-Format) layout and Ascii models in the editor.
4. Make the changes.
5. Export **ASCII** again.
6. Compile back to **binary** in **mdledit**.

Community documentation consistently recommends **MDLEdit** over older **MDLOps** for this workflow because old **[MDLOps](https://github.com/OldRepublicDevs/MDLOps)** builds can ignore data or crash on newer **[KOTORMax](https://github.com/OldRepublicDevs/KOTORMax)** output.

### Step 5: treat KOTORMax import options correctly

The source material repeatedly calls out two options that confuse people:

#### `Export WOK File`

This is exactly what it sounds like: when enabled, the exported room includes updated **[WOK](BWM-File-Format)** data. If you change *walkmesh-related* information and this is off, you can do all the right editing work and still test the old walkmesh in-game.

For area *room* work, assume this should be on unless you have a specific reason not to write **[WOK](BWM-File-Format)**.

#### `Use Layout Position`

This option is often misunderstood. It is **not** a replacement for loading the **[LYT](LYT-File-Format)** itself. Community discussion indicates it only helps when the ASCII Model **[MDL/MDX](MDL-MDX-File-Format)** already has *layout-position data* embedded in its header from a previous export. That usually does **not** apply to *vanilla-decompiled *room models*.

So:

- Use **Area Tools / **layout import** to load the actual area.
- Do **not** rely on **Use Layout Position** to magically line up *vanilla room models* against a loose **[LYT](LYT-File-Format)**.

### Step 6: Simplify first, then add complexity back

When you are making a *seam* work for the first time, reduce variables (and this is why you want to keep the area resources in one folder):

- Keep the test focused on one connection.
- Postpone fancy visibility tuning.
- Postpone door polish if you are only testing traversal.
- If necessary, temporarily simplify or remove **[VIS](VIS-File-Format)** during early testing.

Several sources in your provided material treat **[VIS](VIS-File-Format)** as something you can leave out while proving the *seam* and *roomlinks* first, then bring back once the crossing works.

## Reusing an existing room in a new place

This is the case that confuses most modders because it looks *deceptively simple*.

### What people expect

They *duplicate* a room, move it somewhere else, line the geometry up, maybe adjust the *walkmesh*, and expect the player to walk across.

### What actually happens

The *duplicated room* still carries transition assumptions based on its old adjacency. If the room's old *walkmesh* linked to its original neighbors, those transition IDs are now wrong for the new layout.

### The correct approach

1. Give the *duplicated room* **new, unique names**.
2. Put the new room into the layout.
3. Align the new room's *walkmesh* seam to the neighboring room.
4. Reassign the roomlinks so each side points at the correct room index in the current LYT.
5. Export the updated *walkmesh*.
6. Compile and test.

The crucial point is this: **reusing *vanilla room geometry* is fine, but reusing *vanilla roomlinks* is not** once the *room* is in a different place.

### Can you reuse part of the same walkmesh?

Yes, but only as a **starting shape**.

Using a *copied chunk* of the original *walkmesh* can help you block out a doorway or threshold quickly, but the game will not treat that copied piece as a valid new *room transition* unless you also:

- Make sure the seam itself is correct.
- Give the new room its own valid *walkmesh* boundary.
- Assign correct *roomlinks* between the old room and the new one.

This is why *"I copied the black-highlighted section from the existing room"* often produces something that looks close but still never becomes *traversable*.

## Creating a brand-new room in an existing area

When making a *new *room*, think in layers.

### Layer 1: visual geometry

Build or modify the *visible room geometry* first. This is the part that makes the *room* look right.

### Layer 2: room walkmesh

Create or modify the *room's *walkmesh* so the floor area is actually walkable, the walls are not, and the seam aligns with any neighboring room you want to connect to.

### Layer 3: materials

Paint or assign correct *walkmesh materials*. Use [`surfacemat.2da`](2DA-surfacemat) as the meaning table:

- Walkable floor surfaces should use walkable materials.
- Wall and blocked regions should use non-walkable materials.
- Doorway thresholds should use the correct material for the intended interaction.

### Layer 4: roomlinks

This is where many attempts fail. The *new room* needs proper boundary transitions, and the neighboring room needs reciprocal transitions back into the new room.

If the two sides do not reference each other correctly, the player can hit a *visually perfect seam* and still be blocked.

### Layer 5: layout and visibility

Add the room to the **[LYT](LYT-File-Format)** and, when needed, to the **[VIS](VIS-File-Format)**. If the room is missing from the layout, the transition IDs cannot line up correctly. If the **[VIS](VIS-File-Format)** is wrong, the room may render badly or disappear, even though collision is correct.

### Layer 6: naming and identity

Give new resources unique names. If you *duplicate* an existing *room* and keep old names, you make it much harder to reason about:

- which room the **[LYT](LYT-File-Format)** is actually referencing
- which *walkmesh* belongs to which *room*
- which transition ID should point where

The source material you provided explicitly notes that changing adjacency often goes hand in hand with using **custom room names** rather than continuing to point at *vanilla room identities*.

## Doors and *fake door* replacements

Replacing a *fake door texture* with a real *door* is more than a model swap.

### You need all of these pieces

- a real *door model*
- a *door walkmesh* (**[DWK](BWM-File-Format)**) with the proper states
- a threshold that uses the correct *walkmesh* material
- a roomlink arrangement that makes sense on both sides
- dynamic area data in the **[GIT](GFF-GIT)**   

*Door walkmesh* naming matters. Community documentation repeatedly points to the closed/open state naming pattern:

- `_wg_closed`
- `_wg_open1`
- `_wg_open2`

If the *door setup* is incomplete, you may get a visible door that still does not behave like a real traversal point.

### Door hooks vs real door behavior

Do not confuse these:

- **[LYT](LYT-File-Format) *door hooks*** suggest where a door belongs. This literally exists only for editors and toolsets, it does nothing in the game.
- **[GIT](GFF-GIT) data** defines the actual dynamic *door* instance.
- **[DWK](BWM-File-Format) and *walkmesh transitions*** determine whether crossing and *door* behavior feel correct in play.

Another way to say it: **[LYT](LYT-File-Format)** can help you place a door, but it does not replace the rest of the door setup.

### Are fake door textures easier to replace by extending one room?

Sometimes people consider extending one *room's *walkmesh* deep into the new space instead of creating a proper second room. That can work as a crude shortcut, but it also collapses behavior you may want to keep separate, such as room-based ambient audio and cleaner room-to-room logic.

If your goal is a proper new room, treat it as a proper new room.

## What *not* to rely on

These things do **not** solve room crossing on their own:

- Lining up visible *room meshes*.
- Combining *walkmeshes* into one big surface.
- Repainting materials without fixing transitions.
- Changing the *ARE* room list and expecting traversal to update.
- Editing roomlinks by hand in ASCII and assuming the compiler will preserve incomplete or invalid linkage.
- Relying on **[LYT](LYT-File-Format) *door hooks*** as if they were the traversal system.

These may be part of the workflow, but none of them replace proper roomlink assignment.

### Walkmesh structure tips

Community practice suggests keeping individual *walkmesh* sections to roughly 100 polygons or less; larger sections are often split into multiple parts for stability. When building or editing *walkmesh* geometry, weld vertices with a small tolerance (e.g. 0.1 cm) and ensure perimeter edges are clean. For multi-part *walkmeshes* in one room, **[LYT](LYT-File-Format) *door hooks*** lines in the layout can define the seam between parts and help with **[VIS](VIS-File-Format)* and room behaviour. See [BWM File Format](BWM-File-Format) and [LYT *door hooks*](LYT-File-Format#door-hooks).

## Tool choice in practice

Based on the currently available documentation and community reports:

- **[KOTORMax](https://github.com/OldRepublicDevs/KOTORMax)** is the workflow most consistently described as supporting layout import/export, **[VIS](VIS-File-Format) import/export**, and roomlink editing for indoor rooms.
- **[KOTORBlender](https://github.com/OldRepublicDevs/KOTORBlender)** is useful for geometry work, but the sources you provided repeatedly describe it as incomplete or unreliable for final *room-to-room* transition work.
- **[MDLEdit](https://deadlystream.com/files/file/1150-mdledit/)** is the safer modern choice for compiling and decompiling ASCII in this workflow.

That does not mean other tools are useless. It means that if the specific problem is **indoor room crossing**, the existing evidence points to a layout-aware, roomlink-capable workflow as the most reliable path.

## A KOTORMax-centered walkthrough

The current source material is not clean enough to document every button label with full certainty across different versions of **GMax** and **3ds Max**. What it does support clearly is the overall workflow.

### 1. Prepare the folder

Put these together:

- the room models you need to work on
- the room *walkmeshes*
- the area's **[LYT](LYT-File-Format)**
- the area's **[VIS](VIS-File-Format)**, if you are using it during import

If the tool expects *ASCII models* for layout-aware loading, make sure the rooms you actually need to edit are available in *ASCII* form.

### 2. Open the area through the layout workflow

Do ***not*** load the **[LYT](LYT-File-Format)** through the model-loading panel.

Instead:

- Open the layout using the **Area Tools** style workflow.
- Enable options like loading the **[VIS](VIS-File-Format)** or loading models at the same time if your version exposes them.
- Work inside the scene produced by that import.

This is the step that gives you *room-to-room* context.

### 3. Confirm the scene contains what you expect

Before editing anything else, confirm:

- The right rooms are present.
- The *room* you want to modify is actually the one you are editing.
- The adjoining room is present if you need to inspect the seam.

If the adjoining *room* is missing, stop and fix the scene setup before touching *walkmesh*s.

**Checkpoint:** Before editing, confirm the scene matches [How to test intelligently](#how-to-test-intelligently) Test 1 (*room appears*).

### 4. Make the physical seam correct

Adjust the new or reused *room* so the boundary physically lines up with the neighboring *room*. This includes:

- Floor height.
- Edge shape.
- *threshold* width
- Doorway opening.

Do not worry yet about whether the seam is *traversable*. At this stage you are making it geometrically correct.

### 5. Make the walkmesh correct

Now inspect the *walkmesh* itself:

- Is the threshold actually part of a walkable floor?
- Are the wall faces still non-walkable?
- Does the seam line up in walkmesh space, not just visual model space?

If you are using a *copied walkmesh piece*, reshape it into the *threshold* you actually need rather than treating the copied chunk as finished data.

### 6. Reassign the roomlinks

This is the step people *skip*.

For each side of the seam:

- Identify the boundary edge(s).
- Assign the correct neighboring *room index*.
- Make sure the connection is reciprocal.

If *room A* points to *room B*, *room B* must also point back to *room A* at the corresponding seam.

### 7. Export with **WOK** enabled

Make sure the export is writing out the updated **[WOK](BWM-File-Format)**. If not, you are not testing your *walkmesh* changes.

**Checkpoint:** Verify the exported **[WOK](BWM-File-Format)** is present and updated; see Test 6 in [How to test intelligently](#how-to-test-intelligently) (*doors behave like real doors*).

### 8. Compile and test

Compile the ASCII back to binary using a modern toolchain (**[MDLEdit](https://deadlystream.com/files/file/1150-mdledit/)**), then test in-game.

**Checkpoint:** Test in order: room appears → stand on floor → cross seam (Tests 1–3 in [How to test intelligently](#how-to-test-intelligently)). If crossing fails, use [Troubleshooting by symptom](#troubleshooting-by-symptom) (*crossing fails*).

If the *seam* still fails, do not immediately start changing five more things. Return to the troubleshooting section below and isolate the failure.

## A practical end-to-end sequence

If you want one *checklist* to follow, use this:

1. Extract the room models, walkmeshes, **[LYT](LYT-File-Format)**, and **[VIS](VIS-File-Format)** into one working folder.
2. Convert the room models you need into *ASCII* using a modern toolchain.
3. Load the area through the layout workflow, not through isolated model import.
4. If supported by the tool, load the layout together with the models and VIS.
5. Duplicate or create the room with **new unique names**.
6. Move the room into place in the layout.
7. Align the *seam* between the new *room's *walkmesh* and the neighboring *room's *walkmesh*.
8. Assign walkmesh materials correctly.
9. Reassign the roomlinks for **both** sides of the connection.
10. If the change involves doors, finish the door model, **[DWK](BWM-File-Format)**, *threshold*, and **[GIT](GFF-GIT)**-side setup.
11. Export the updated room with **WOK export enabled**.
12. Compile ASCII back to binary.
13. Test in-game with a simplified **[VIS](VIS-File-Format)** if necessary.
14. Only after traversal works should you spend time polishing visibility, doors, and audio details.

## How to test intelligently

Do not test everything at once. Use a **layered test order**.

### Test 1: does the new room appear

If the *room* is missing entirely, check the **[LYT Layout](LYT-File-Format)** first.

### Test 2: can the player stand on the floor

If not, inspect *walkmesh materials* and export *state*.

### Test 3: can the player cross the seam

If not, assume *roomlinks* are wrong until proven *otherwise*.

### Test 4: does visibility behave

If geometry pops in or vanishes *incorrectly*, inspect **[VIS](VIS-File-Format)**.

### Test 5: do doors behave like real doors

If not, inspect **[DWK](BWM-File-Format)**, *threshold material*, and *dynamic area* setup.

### Test 6: did you actually test the updated resources

If nothing seems to change from one build to the next, verify the most boring explanation first:

- Are the updated binaries the ones the game is loading?
- Did the compile step succeed?
- Did the exported **[WOK](BWM-File-Format)** actually update?
- Are you mixing old binary resources with new ASCII assumptions?

## Frequently asked questions

### Why does **KOTORMax** say "No Appropriate Import Module"?

This usually means the *file extension* does not match what the current import filter expects.

The source material you provided repeatedly points to the *`.ascii`* setting and filename filter as a common cause. In practical terms:

- If the tool is expecting *`*.mdl.ascii`*, give it *`*.mdl.ascii`*.
- If it is expecting *`*.mdl`*, give it that instead.
- Do not assume the *file* is wrong until you check what the importer is actually filtering for.

If you are using **[MDLEdit](https://deadlystream.com/files/file/1150-mdledit/)** , the expected result is typically a proper *`.mdl.ascii`* workflow. If you are using an older **[MDLOps](https://github.com/OldRepublicDevs/MDLOps)** variant, the extension behavior may be less convenient and may require renaming.

### Do I need to launch through `kotormax.exe`?

The context material treats that as part of the expected workflow. If **KOTORMax** is not appearing correctly, or the integration behaves inconsistently, verify that you launched **GMax** or **3ds Max** through the **KOTORMax-aware** entry point rather than opening the host application first and hoping the scripts load the same way.

### Do all the *room models* in the layout need to be converted to *ASCII* first?

Not necessarily every single *room* in the area, but at least the *rooms* you need to edit or inspect in-context should be available in the form the *layout-aware* workflow expects.

The safest practical instruction is:

- Convert the *rooms* you actually need for the test.
- Place those *ASCII models* alongside the **[LYT](LYT-File-Format)** and **[VIS](VIS-File-Format)**.
- Then load the layout through Area Tools.

If only one *room* is *ASCII* and everything else remains binary, you may end up with incomplete context, missing geometry, or a scene that is harder to debug.

### Can I just import individual *room models* instead of importing the **[LYT](LYT-File-Format)**?

If your goal is only to inspect a single *room model*, yes.

If your goal is to:

- Align two *rooms*.
- Fix *room crossing*.
- Verify adjacency.
- Edit *roomlinks*.
- Make a new *room* function as part of a real area.

Then **no**, importing individual *models* alone is the wrong workflow. The *room transition* problem depends on layout context.

### Why does loading the **[LYT](LYT-File-Format)** give me an "invalid ascii" error?

The most likely cause is that the **[LYT](LYT-File-Format)** is being loaded through the *model* importer rather than the *layout* importer.

In other words:

- *MDL Loading* expects *model ASCII*.
- The **[LYT](LYT-File-Format)** should be loaded through the area/layout workflow.

This is one of the most repeated failure modes in the source material.

### What does `Use Layout Position` actually do?

It does **not** mean "load this vanilla *room* according to whatever **[LYT](LYT-File-Format)** happens to be nearby."

Based on the provided community explanations, it only works when the *model ASCII* already contains layout-position data embedded from an earlier **KOTORMax** export. That means it is not the normal answer for vanilla-decompiled *room* workflows.

### What does *Export WOK File* actually do?

It controls whether your export writes updated *room walkmesh* data.

If you changed thresholds, *room boundaries*, or *walkmesh-related* behavior and *Export WOK File* is off, you can easily test stale data and conclude the whole workflow is broken when the real issue is simply that the updated **[WOK](BWM-File-Format)** was never written out.

### Can I reuse part of the same model and part of the same walkmesh?

Yes, as a **template**.

No, as a complete solution.

That reused chunk can help you shape the new *threshold* or *floor crossing* area, but it does not automatically create valid new *room-to-room* traversal. You still need:

- A proper seam.
- A valid boundary for the new *room*.
- Updated *roomlinks* on both sides.

### Can I combine the two rooms into one giant walkmesh?

For proper indoor *room-to-room* transitions, that is generally the wrong approach.

The source material repeatedly reinforces that each *room* should keep its own *walkmesh* and that crossing should happen through *room-to-room* *transition edges* at the seam.

### Are **[LYT](LYT-File-Format) *door hooks*** the same thing as *roomlinks*?

No.

**[LYT](LYT-File-Format) *door hooks* help define intended door placement. They are not the thing that actually makes crossing between two *rooms* work.

### Do the *`.are`* *room entries* make the *room traversable*?

No.

The material you provided repeatedly points out that *`.are`* *room entries* may matter for *room metadata* such as ambient audio, but they do not solve crossing by themselves.

### Should I leave VIS alone while I debug traversal?

In many cases, no.

Several parts of your source material recommend simplifying or even temporarily removing **[VIS](VIS-File-Format)** during early testing so you can prove the *seam*, *roomlinks*, and exported **[WOK](BWM-File-Format)** first. Once traversal works, bring **[VIS](VIS-File-Format)** back under *control*.

### Can I use **KOTORBlender** for the final *room transition* step?

The current source set does not support trusting *it* for that specific job.

The consistent message across the supplied material is:

- **KOTORBlender** can still be useful for *geometry work*.
- **KOTORMax** is the more trusted workflow for final *room-to-room* transition editing

### Do I really need unique names for the new room?

Yes, that is the safer path.

Once you start changing adjacency, reusing old *identities* makes it much harder to reason about:

- What the layout references.
- What the walkmesh belongs to.
- What *transition ID* should lead where.

### What if the seam looks perfect in the editor?

That is only one *checkpoint*.

A visually perfect seam proves almost nothing by itself. The game still needs the correct walkable *threshold*, *room boundary*, transition IDs, exported **[WOK](BWM-File-Format)**, and compiled binaries.

## Troubleshooting by symptom

| **Symptom** | **Likely cause** | **See below** |
|--------|---------------|-----------|
| Rooms line up but crossing blocked | Roomlinks wrong or pointing to old neighbor | [The rooms line up visually, but crossing is blocked](#the-rooms-line-up-visually-but-crossing-is-blocked) |
| Only part of floor works | Materials, seam, or **[WOK](BWM-File-Format)* export* | [The room exists, but only part of the floor works](#the-room-exists-but-only-part-of-the-floor-works) |
| Room disappears or draws badly | **[VIS](VIS-File-Format)** | [The room seems correct, but it disappears or draws badly](#the-room-seems-correct-but-it-disappears-or-draws-badly) |
| Copied room behaves like old room | Naming, *walkmesh linkage*, or layout context | [A copied room still behaves like the old room](#a-copied-room-still-behaves-like-the-old-room) |
| Roomlinks in ASCII don't survive recompile | Bypassing layout-aware *roomlink* workflow | [Editing roomlinks in ASCII does not seem to survive recompilation](#editing-roomlinks-in-ascii-does-not-seem-to-survive-recompilation) |
| *LYT* import "invalid ascii" | *LYT* loaded via *model* importer | [The *LYT* import throws an "invalid ascii" style error](#the-lyt-import-throws-an-invalid-ascii-style-error) |
| Nothing changed in-game | Export/compile/path chain | [Nothing changed in-game after export](#nothing-changed-in-game-after-export) |

### The rooms line up visually, but crossing is blocked

Most likely cause: the roomlinks still point to the old neighbor or were never assigned correctly for the new seam.

→ Reassign roomlinks for both sides of the seam: [A KOTORMax-centered walkthrough](#a-kotormax-centered-walkthrough) step 6. See also [What has to agree before room crossing works](#what-has-to-agree-before-room-crossing-works).

### The room exists, but only part of the floor works

Most likely cause: incorrect *walkmesh materials*, bad seam alignment, or an outdated **[WOK](BWM-File-Format)** export.

Check all of these:

- Is the threshold actually walkable?
- Are the floor faces using the material you think they are?
- Did a copied *walkmesh chunk* create thin or broken triangles at the seam?
- Did you export the **[WOK](BWM-File-Format)** after editing?

### The room seems correct, but it disappears or draws badly

Most likely cause: **[VIS](VIS-File-Format)** needs to be updated or simplified for debugging.

Do not immediately rewrite the room because of this. First determine whether the problem is visibility-only or whether traversal is also failing.

### A copied room still behaves like the old room

Most likely cause: the room was duplicated visually, but the model naming, *walkmesh linkage*, or layout context still reflects the original room.

Also check whether you are still effectively reusing the old room's transition assumptions.

### Editing roomlinks in ASCII does not seem to survive recompilation

Treat this as a warning sign that the workflow is bypassing the proper layout-aware roomlink step. The source material you provided includes examples of this exact failure.

If this happens, stop trying to force the ASCII by hand and return to the layout-aware roomlink workflow.

### The LYT import throws an "invalid ascii" style error

Most likely cause: the *LYT* is being loaded through a *model* importer instead of the area/layout workflow.

Secondary cause: the layout is trying to pull in models that are not available in the form the editor expects for that workflow.

→ Load the *LYT* via [Area Tools / layout workflow](#2-open-the-area-through-the-layout-workflow), not the *model* importer.

Also verify whether the models you expect to come in with the layout are available as ASCII, not only as raw binary resources.

### The model imports, but the area still has no useful room context

Most likely cause: you imported a *room model* successfully, but you never actually loaded the full layout.

This is a classic false success state. You can be "inside the tool" and still be working in the wrong context.

### The seam looks right, but the player still collides strangely with the camera

Do not forget the split between **[WOK](BWM-File-Format)** behavior and *MDL-embedded AABB* behavior. Traversal may come from one resource while camera behavior comes from another.

This can make it feel like "some of it worked" while other collision behavior remains broken.

### The room crossing works, but the room audio or presentation feels wrong

This often means you fixed traversal first but have not finished the rest of the area integration yet. That is normal. Finish crossing first, then return to **[ARE](GFF-ARE)**, **[GIT](GFF-GIT)**, **[VIS](VIS-File-Format)**, and door polish.

### The imported scene is confusing and I cannot tell what I am selecting

That is common in this workflow.

Stop and verify:

- Whether you are looking at visible *room geometry* or *walkmesh geometry*.
- Whether the room you copied is still one combined object or separate editable parts.
- Whether the adjoining room is present for seam comparison.

If you do not know what object you are editing, every later step becomes guesswork.

### I can select the walkmesh, but I do not know how to begin editing it

Treat that as a workflow checkpoint, not as a reason to improvise the whole area.

At that point, the correct next goals are:

1. Identify the threshold region only.
2. Reshape it so the seam is geometrically clean.
3. Keep the rooms separate.
4. Move on to *roomlink* reassignment.

Do not jump from "I can select the walkmesh" straight to "I will solve traversal by combining everything."

### Nothing changed in-game after export

Check the entire boring chain:

- The correct resources were exported.
- `Export WOK File` was enabled.
- ASCII was compiled back to binary.
- The right binaries were copied into the game-loading location.
- You are not testing an older override/module copy by mistake.

→ Follow the export→compile→override chain in [A practical end-to-end sequence](#a-practical-end-to-end-sequence) steps 11–13.

## Common myths and corrections

### "If the *LYT* has *door hooks*, that is the room connection system"

No. Door hooks are placement references. They are not the same thing as roomlinks.

### "If I repaint the *seam* as metal or stone, crossing will start working"

No. Correct material assignment matters, but it does not replace valid roomlinks.

### "If I can load one *model* successfully, I do not need the layout"

Not for indoor room transition work. The layout is what establishes room context.

### "*VIS* is part of collision"

No. VIS is visibility. It can still confuse debugging, which is why simplifying it early can be helpful.

### "*ARE* room entries are enough to define the new room"

No. They may matter for room metadata such as ambient audio, but they do not create traversal by themselves.

## If you are completely stuck

Return to the simplest possible case:

1. One existing *room*.
2. One adjacent *room*.
3. No fancy visibility tuning.
4. One *seam*.
5. One traversal goal.

Then verify, in this order:

- The **[LYT](LYT-File-Format)** scene is correct.
- The *seam* is physically correct.
- The *threshold* is walkable.
- The *roomlinks* are reciprocal.
- The **[WOK](BWM-File-Format)** was exported.
- The compiled *binaries* are the ones being tested.

If that minimal case works, add complexity back one layer at a time.

## The most important rules to remember

- Each room keeps its own walkmesh.
- Transition IDs point to **room indices in the **[LYT](LYT-File-Format)****.
- Layout context matters; isolated model editing is not enough for roomlinks.
- **[WOK](BWM-File-Format)** export matters; if the updated *walkmesh* is not written out, nothing else matters.
- Visual success is not traversal success.

## Community references

These sources informed the workflow described here and are worth reading when you need tool-specific details:

- [KOTORmax file by bead-v](https://deadlystream.com/files/file/1151-kotormax/) — download, feature list (**[LYT](LYT-File-Format)**/**[VIS](VIS-File-Format)** import/export, Roomlink Editor, Export **[WOK](BWM-File-Format)**), use with MDLEdit and MDLOps.
- [KOTORmax release topic](https://deadlystream.com/topic/5731-kotormax/) — Area Tools, loading **[LYT](LYT-File-Format)** via area tools, "invalid ascii" when loading **[LYT](LYT-File-Format)** in MDL Loading, Use Layout Position, ASCII workflow.
- [KOTORmax bug reporting thread](https://deadlystream.com/forum/topic/5734-kotormax-bug-reporting-thread/) — report crashes or errors when using KOTORMax.
- [MDLEdit](https://deadlystream.com/files/file/1150-mdledit/) — ASCII/binary model and walkmesh conversion; recommended with KOTORMax for this workflow.
- [Adding existing rooms to a module](https://deadlystream.com/topic/8517-adding-existing-rooms-to-a-module/) — roomlinks/transition edges, reassigning in KOTORMax, what must agree (layout, walkmesh, roomlinks, **[LYT](LYT-File-Format)**/**[VIS](VIS-File-Format)**, **[WOK](BWM-File-Format)**, compile), KOTORBlender limitations.
- [[K1] Creating a new room in an existing module](https://deadlystream.com/topic/11729-k1-creating-a-new-room-in-an-existing-module/) — roomlinks must be reassigned; hand-editing roomlinks outside KOTORMax can fail to persist after recompile.
- [Inner Workings (page 6)](https://deadlystream.com/topic/9496-inner-workings/page/6/) — "With **[VIS](VIS-File-Format)** file" / "With models" when importing layout in Area Tools.
- [Words of Wisdom for Harmonious Walkmeshes](https://deadlystream.com/topic/4704-words-of-wisdom-for-harmonious-walkmeshes/) — walkmesh structure, section size (~100 polies), borders, welding.
- [Cutting Doorways for KotOR/TSL Areas in 3DS Max](https://deadlystream.com/topic/9369-cutting-doorways-for-kotortsl-areas-in-3ds-max/) (video, Marius Fett).

**Other tools:** [KAurora](https://deadlystream.com/) (and related tooling) can also edit room links; KOTORMax with GMax (free) is still the most commonly recommended for layout and roomlink workflow.

**Video tutorials:** Quanon’s Knights of the Old Republic walkmesh series (3ds Max), and “Advanced map modeling (walkmeshes…)” style tutorials, cover layout import, locating the walkmesh, and basic editing — search for “KotOR walkmesh” or “KotOR module editing” on YouTube.

### Implementation and tooling notes

- **WOK world coordinates:** When building a module (e.g. with the Indoor Map Builder), the exported area WOK must be written with **world_coords** set appropriately after applying the LYT room transform; otherwise the player can spawn with no valid walkable face. See [Indoor Map Builder Implementation Guide](Indoor-Map-Builder-Implementation-Guide).
- **Room-local coordinates:** For raycasts or point-in-walkmesh tests in world space, the engine and some tooling expect **room-local** coordinates for the **[WOK](BWM-File-Format)** (world position minus the **[LYT](LYT-File-Format)** room position). Do not assume world-space coordinates match the **[WOK](BWM-File-Format)** vertex space.
- **Transition fields in code:** In PyKotor, `trans1`/`trans2`/`trans3` on walkmesh faces are transition metadata, not adjacency. For scripting or tooling that maps faces to indices, use identity-based lookups, not value-based. See [BWM File Format — Identity-aware indexing and PyKotor implementation notes](BWM-File-Format#identity-aware-indexing) for details.

### See also

- [2DA surfacemat](2DA-surfacemat)
- [Area Modding and Room Transitions](Area-Modding-and-Room-Transitions)
- [Blender Integration](Blender-Integration)
- [BWM File Format](BWM-File-Format)
- [GFF-ARE](GFF-ARE)
- [GFF-GIT](GFF-GIT)
- [Indoor Area Room Layout and Walkmesh Guide](Indoor-Area-Room-Layout-and-Walkmesh-Guide)
- [Indoor Map Builder Implementation Guide](Indoor-Map-Builder-Implementation-Guide)
- [Indoor Map Builder User Guide](Indoor-Map-Builder-User-Guide)
- [Kit-Structure-Documentation](Kit-Structure-Documentation)
- [LYT File Format](LYT-File-Format)
- [MDL/MDX File Format](MDL-MDX-File-Format)
- [VIS File Format](VIS-File-Format)
