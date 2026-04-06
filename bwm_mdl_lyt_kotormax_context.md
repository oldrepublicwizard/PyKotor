Discord conversation:
```
r [T3M4],  — 6:29 AM
Anyone know how to get the walkways for two map models to line up together in order to let you cross over from one to the other, in Blender? I was able to get two models lined up, but I just can not get it to let me walk into the new model. I tried using two separate models with separate walkways with vertex painting each side. I tried adding metal walkmeshes to every part of the walklmesh.
I tried combining two walkmeshes together, and I also tried using another part of the same model, with the same walkmesh, to see if that would work. Still can't cross over. Feel like I'm doing something wrong.
Wizard [C#],  — 6:32 AM
I've heard that question a lot lately with blender. I think there's actual functionality gaps, my understanding is the guy who put kotorblender together did not test everything under the sun. Conversely I think there was a regression introduced by v5 (or might have been 4.2)

You'll want to use kotormax/gmax unless you have some coding knowledge as you'll either have to fix kotorblender yourself or wait until the community can properly patch it.
Well actually, check the normal stuff. You using the latest version?
https://github.com/OpenKotOR/kotorblender
GitHub
GitHub - OpenKotOR/kotorblender: Blender add-on to import & e...
Blender add-on to import & export KotOR models. Contribute to OpenKotOR/kotorblender development by creating an account on GitHub.
GitHub - OpenKotOR/kotorblender: Blender add-on to import & e...
r [T3M4],  — 6:33 AM
4.0.3
Wizard [C#],  — 6:36 AM
ah
the walkmeshes in general are convoluted. First just ensure you're using the latest version of kotorblender (OpenKotOR is part of the OpenKotOR community and they maintain dead projects such as kotorblender and others). I don't think your blender version itself is too important.
One thing about room models is they have a walkmesh inside of them too. I believe the one in the wok file has a bit more info in it. 

This is where understanding the nwn engine can shed some light. Nwn was a client/server architecture because it was built to be multi-player. Because they reused a lot of nwn stuff from the aurora engine to make the odyssey engine, that client server communication layer is still in KotOR. Now I'm not sure how deep you're invested into how it all works at a low lvl, but there is a concept of a client and server inside the EXE. All have to do is read the strings inside the EXE and you'll find debug messages that provide clues to that end.

Now that being said:
one walkmesh is for client-side computation
the other is for server-side computation.

I believe the server-side one is the WOK file, but I can't remember for sure.

Camera collision won't work in KotOR without one of them and I think it's the one inside the MDL file of the room.

The materials have indexes into surfacemat.2da I believe that tell you what surface it is and whether it is walkable for example. There are also a list of adjacent walkable faces in the WOK file. The adjacent face list helps you reconstruct which faces are touching which and on which sides.

The other thing they have is a perimeter list the perimeter list works with the adjacent list, if there isn't an adjacent walkable face then that edge is a perimeter. The perimeter that is on an edge that is adjacent to the room edge that a player can walk acrossed has a transitionID which is the index ID of the adjacent room in the area room list

At the edges the implementation sets up arrows that point inwards to the very next AABB/face, those need to be correctly lined up or you'll run into that issue. (degenerated AABB tree). In my tools i'm still trying to implement that functionality properly but that said I think blender is painting over the vertexes and hashing them that way, which is somewhat a hacky way to do it and that may indeed be causing an issue with the game in some scenarios. The holocron toolset's indoor builder i believe is using teh same code
but tldr for now you may want to just use kotormax/gmax since that's been battle-tested over the last decade or so, and itself was what the game developers themselves used
Wizard [C#],  — 6:44 AM
there are a few people here even that have been waiting for the developers in the community to address and properly streamline all of this but it's still in progress, check back soon  I might have something in the next week or so.
Wizard [C#],  — 6:52 AM
speaking of the community also maintains kotormax here: https://github.com/OpenKotOR/KOTORMax
r [T3M4],  — 7:43 AM
How do you import mdl files into gmax with kotormax?
Seem to only be able to look for 3d studio meshes
Wizard [C#],  — 7:44 AM
You're going to be doing a lot of research if you go down that path fair warning. It was frustrating to get setup on my end initially.
but basically you'll need to convert to ascii i think using mdlops
note the extension that kotormax is asking you for, and the gui control that iirc is a checkbox next to 'MDLOps' or not.

there's two ascii formats i thik kotormax only supports one of them though. Either .mdl.ascii or .ascii.mdl
You'll want to actually find a walkthrough/guide of some kind on deadlystream/mixmojo though
It isn't pleasant to use but it does work, that's how mods such as Kotor III and probably even RoR were made 10-20 years ago
ah, glamorous was the word i was looking for
my advice? if you're working on a large mod take a break and work on a different part of it. Kotor development has hit a sort of renaissance and there's at least three people including me working on a better solution for stuff like this
but nonetheless i'll try to help with kotormax i guess if you want to go that route
r [T3M4],  — 7:52 AM
Im trying to import an ascii model and it just says no appropriate import module found
Wizard [C#],  — 7:52 AM
Yeah I remember running into that
Has something to do with the extensions and the settings you set beforehand.
check the model extensions i think they need to be exactly .mdl.ascii or .ascii.mdl or something
r [T3M4],  — 7:54 AM
mdledit.mdl.ascii
Wizard [C#],  — 7:54 AM
i have an idea actually
r [T3M4],  — 7:54 AM
203tell-mdledit.mdl.ascii
Wizard [C#],  — 7:54 AM
that filename is cursed
r [T3M4],  — 7:54 AM
Is the name I get when converting 203tell to ascii
Wizard [C#],  — 7:55 AM
one sec
What are you trying to do anyway? like what's the end goal? You just trying to create some levels or what? also is this k1 or tsl?
203tell probably is tsl
r [T3M4],  — 7:58 AM
TSL, and I'm trying to add new areas to Citadel Station on Telos
Wizard [C#],  — 7:58 AM
Gotcha
r [T3M4],  — 7:58 AM
For some of the doors that are just door textures, replacing those with actual doors/areas
I just can't get the walkmeshes right
 [C#], 
Wizard [C#],  — 7:59 AM
Yup that's a large blocker people run into what i was explaining here
one sec
are you using gmax or 3ds max?
r [T3M4],  — 8:01 AM
gmax
Wizard [C#],  — 8:07 AM
ah nice this might actually work
https://github.com/copilot/share/003c039a-4140-8891-8041-0e4be4864158]
I now have a thorough, authoritative picture of the entire codebase, the KOTORMax import/export pipeline, the `dotascii`/`g_dotAscii` setting, the walkmesh system, the LYT/VIS workflow, and the MDLEdit vs MDLOps distinction. Let me compile the full, definitive guide.

---

# The Complete, Authoritative KOTORMax + Area Modding Workflow for TSL

message.txt
17 KB
TLDR:
✔ Rename file to 203tel.mdl.ascii
✔ Launch via kotormax.exe
✔ Ensure .ascii filter matches
✔ Enable Export WOK File
✔ Walkmesh = OdysseyWalkmesh (Area), correct materials, room links
✔ LYT/VIS updated if adding rooms
✔ Door = correct DWK + door material + room links
✔ Export → compile with MDLEdit
The “No Appropriate Import Module” Error
It’s caused by the file dialog filter, controlled by dotascii (“Use .ascii by default”).
If checked (default): KOTORMax expects *.mdl.ascii.
If unchecked: It expects *.mdl.
Your file must match the filter.

Fix:
Rename your file to something clean like:
203tel.mdl.ascii
(no -mdledit, no extra dots)

---

MDLEdit vs MDLOps
Use MDLEdit. It’s the modern, correct tool.
MDLEdit outputs proper *.mdl.ascii.
MDLOps outputs ASCII but with .mdl extension → rename if needed.

---

Correct Import Workflow
Extract 203tel.mdl/mdx.
Convert to ASCII using MDLEdit → 203tel.mdl.ascii.
Launch GMax via kotormax.exe (mandatory).
Ensure “Use .ascii By Default” matches your file extension.
Import via KOTORMax’s MDL Loading panel.
KOTORMax will auto‑import pwk/dwk if present.

---

Walkmeshes — The Real Pain Point
Types
Area walkmesh → .wok → inside the room MDL (aabb node)
Placeable walkmesh → .pwk
Door walkmesh → .dwk (closed/open1/open2)

Creating a correct area walkmesh
Model floor mesh.
Apply OdysseyWalkmesh modifier.
Set type = Area (aabb).
Paint materials (Stone/Metal = walkable, Nonwalk = walls).
Parent under the room’s OdysseyBase.
Enable “Export WOK File” (off by default!).
Use Room Linker to define room transitions.

---

LYT & VIS
LYT = room positions.
VIS = room visibility.
KOTORMax imports/exports both.
Use “Import Layout (with models)” to load the whole area.
Add your new room, assign layout number, export.

---

Doors
To make real doors instead of textures:
You need a proper door model + door.dwk (closed/open1/open2).
Your room’s walkmesh must have Door material on the threshold.
Room links must connect the two rooms.
Node names must end in:
_wg_closed
_wg_open1
_wg_open2

---

Exporting
Select the room’s OdysseyBase.
Export → produces mdl.ascii, wok.ascii, pwk/dwk.ascii.
Compile all ASCII → binary using MDLEdit.
Drop binaries into Override or module RIM.
 
trust
 [C#], 
r [T3M4],  — 8:13 AM
"Ensure .ascii filter matches", "Enable Export WOK File", is that done in the gmax?
"Ensure “Use .ascii By Default” matches your file extension.,
Import via KOTORMax’s MDL Loading panel."
Wizard [C#],  — 8:14 AM
It depends if you're using mdlops or mdledit. The guide assunes you're using mdledit as stated though. There should be a button somewhere in the kotormax extension/toolbar
send a screenshot of what you're seeing
r [T3M4],  — 8:16 AM
I had to run the script for KOTORmax to show up
Image
Wizard [C#],  — 8:16 AM
Okay that's a lot different than what I was doing in 3ds max last
Neat
Expand the MDL Loading/Exporting so I can see what it has available there
(left side)
r [T3M4],  — 8:17 AM
Image
Image
Wizard [C#],  — 8:19 AM
I think the blocker is actually in one of the other sections. This interface is ridiculously bad
Oh it's right here
Image
r [T3M4],  — 8:21 AM
Image
I got it imported, not sure how to select the walkmesh though
lol
Wizard [C#],  — 8:22 AM
let's find out
if this actually works for you i'm writing a full tutorial for the next guy as embarrassingly you've gotten further than i did the last time i tried i got too frustrated with the interface and decided to just work on a rewrite of this lol
r [T3M4],  — 8:24 AM
I can see why
It seems a lot more confusing than blender 
Wizard [C#],  — 8:24 AM
Am not kidding when there's literally three different alternatives being developed right now lol
one of them i'll recommend if this doesn't work
oh this response is much better
If two KotOR room models line up visually but you still can’t walk from one to the other, the problem is usually not the visible geometry. It’s the room-to-room walkmesh links. In KotOR indoor areas, crossing between rooms depends on the room walkmesh’s roomlinks / transition edges, not just matching vertices or painting surfaces. Those links need to be reassigned in KOTORMax (or another dedicated roomlink-capable tool), especially if you are adding or rearranging rooms. (deadlystream.com>)

Also: for this specific workflow, KOTORBlender is not the reliable tool for finalizing room transitions. Community sources explicitly note that this functionality is available in KOTORMax, while Blender support is incomplete or absent for this part of the pipeline. (deadlystream.com)
 

What actually has to be fixed
For an indoor area like Telos/Citadel Station, you need all of these to agree:

The rooms must be positioned correctly in the area layout
Each room’s walkmesh edge must physically line up with the neighboring room
The roomlinks must be reassigned to the new adjacency
The area .lyt and .vis must include the new/custom rooms
The exported room must include/update its .wok
You must compile back to binary with a modern tool such as MDLEdit / newer MDLOps

If you only do #1 and #2, you can get a model that looks correct but still blocks crossing. (deadlystream.com)

---

Important correction to the earlier advice
Per your note, I’m not going to dwell on the .ascii import issue.

The real blocker for the end goal is this:

You do not fix room crossing just by:
lining up meshes,
combining walkmeshes,
repainting walkmesh materials,
or editing roomlinks by hand in ASCII and expecting the compiler to preserve bad/incomplete linkage.

Community guidance on Deadly Stream specifically says that when using vanilla rooms in a changed layout, the original roomlinks no longer match, and the solution is to load the area and reassign the room links in KOTORMax. (deadlystream.com)

---

What the UI in your screenshots is showing
From the screenshots:

Left panel is the KOTORMax rollout stack.
You have:
MDL Loading
MDL Exporting
Preferences
Area Tools collapsed
In Preferences, the checkbox Export WOK File is visible.
In MDL Loading, Use Layout Position is visible.

Those two items matter, but for your final objective:

1) Export WOK File
Yes — that is set in gmax/KOTORMax, exactly where your screenshot shows it. If you are editing an area room and expect the walkmesh to update, this should generally be enabled before export. (deadlystream.com)

2) Use Layout Position
This is not magic auto-layout from a random .lyt in the folder. Community discussion says it works when layout data is embedded/exported appropriately, and the proper way to load an area layout is through Area Tools. (deadlystream.com)

So for room editing, don’t just import one model and hope layout handling sorts itself out. Load the area via Area Tools / LYT workflow first, then work inside that scene. (deadlystream.com)

---

The correct workflow in gmax/KOTORMax
Goal A: add or reposition a room and make the player walk across the seam
Step 1: work with a full area setup, not isolated room guessing
For indoor modules, extract into one working folder at minimum:

the room models you are editing
their walkmeshes / .wok
the area .lyt
the area .vis

KOTORMax supports LYT and VIS import/export, and that is the intended pipeline for this kind of work. (deadlystream.com)
 
sry for the ai use man i'm on my phone and i don't understand this maxscript schema its using lol
but this response looks correct
lemme know when you're ready for step 1 and i'll send the rest
there's a few more i just didn't want to spam the chat lol
r [T3M4],  — 8:31 AM
What if you reuse a part of the same model/walkmesh? Like if I cut out part of the walkmesh and put it where the doorway is for the new area, and reuse the part of the same model that is right next to it? 
Im ready to try and position the walkmeshes correctly, just not sure how to do that
So just using one model and cutting a part off of it and reusing it
Is it okay to just port in individual models instead of importing the lyt? It's telling me invalid ascii when trying to import lyt. Doe all the models for the layout need to be converted before trying to use the lyt file?
:thumbsup:
Click to react
:joy:
Click to react
:heart:
Click to react
Add Reaction
Reply
Forward
More

Wizard [C#], C# — 8:52 AMThursday, March 12, 2026 8:52 AM
hmm one sec
:thumbsup:
Click to react
:joy:
Click to react
:heart:
Click to react
Add Reaction
Edit
Forward
More
[8:53 AM]Thursday, March 12, 2026 8:53 AM
You’re probably loading the .lyt in the wrong panel.
Don’t load it through MDL Loading — that importer expects model ASCII, so it throws “invalid ascii.” Load the .lyt from Area Tools instead. If you want it to pull the room models in automatically, put the area’s ASCII room models in the same folder and enable options like With VIS file / With models if present. Also, Use Layout Position in MDL Loading won’t help for vanilla-decompiled models; that only works for models whose ASCII already has layout-position data embedded from a previous KOTORMax export. (deadlystream.com)
:thumbsup:
Click to react
:joy:
Click to react
:heart:
Click to react
Add Reaction
Edit
Forward
More
[8:53 AM]Thursday, March 12, 2026 8:53 AM
For this first test honestly I wouldn't even touch VIS. Literally delete it fully from the module
:thumbsup:
Click to react
:joy:
Click to react
:heart:
Click to react
Add Reaction
Edit
Forward
More
[8:54 AM]Thursday, March 12, 2026 8:54 AM
It's a useless resource that just adds complexity on top of an already enormous amount of complexity
:thumbsup:
Click to react
:joy:
Click to react
:heart:
Click to react
Add Reaction
Edit
Forward
More

r [T3M4], T3M4 — 8:58 AMThursday, March 12, 2026 8:58 AM

:thumbsup:
Click to react
:joy:
Click to react
:heart:
Click to react
Add Reaction
Reply
Forward
More
[8:58 AM]Thursday, March 12, 2026 8:58 AM
Thats the new area I have attatched, but without no workable walkmesh
:thumbsup:
Click to react
:joy:
Click to react
:heart:
Click to react
Add Reaction
Reply
Forward
More
[8:59 AM]Thursday, March 12, 2026 8:59 AM
It resues the same walkmesh (highlighted in black)
:thumbsup:
Click to react
:joy:
Click to react
:heart:
Click to react
Add Reaction
Reply
Forward
More
[9:00 AM]Thursday, March 12, 2026 9:00 AM
That's just from porting the mdl
:thumbsup:
Click to react
:joy:
Click to react
:heart:
Click to react
Add Reaction
Reply
Forward
More

Wizard [C#], C# — 9:00 AMThursday, March 12, 2026 9:00 AM
i wonder how hard it'd be to pull that ai agent as a discord bot to answer questions like this lol
[9:00 AM]Thursday, March 12, 2026 9:00 AM
i might do that after you figure this out for the next guy

r [T3M4], T3M4 — 9:01 AMThursday, March 12, 2026 9:01 AM
I tried to load the lyt via area tools, and got that error.
[9:01 AM]Thursday, March 12, 2026 9:01 AM
Although I only have 203tell converted to ascii, the rest from the lyt are still in binary

Wizard [C#], C# — 9:02 AMThursday, March 12, 2026 9:02 AM
Yeah, that screenshot tells the story.,
What you have there is basically visual geometry plus reused/copied walkmesh-looking data, but not a valid new room transition setup yet. Reusing the same black-highlighted walkmesh chunk from the original room is okay as a starting shape, but the game is not going to treat that as “new connected room works now.” You still need the new room’s own walkmesh boundary and then the roomlink between the two rooms. (deadlystream.com)

What this means in practice,
Right now, think of it like this:

visible model = what you see,
walkmesh shape = where movement can happen,
roomlink = what tells the engine “crossing this edge moves you into that neighboring room”,

You currently have the first, and maybe part of the second, but not the third. That’s why porting the MDL by itself won’t solve it. (deadlystream.com)

So, directly answering you:,
Yes, you can reuse part of the same walkmesh as a template.
No, you should not rely on that reused piece by itself as the final solution.

If that black section is just copied from the original room, then the next thing you need to do is:

Make it the threshold shape only,
,
Use that copied section just to form the new doorway/floor crossing area.
[9:03 AM]Thursday, March 12, 2026 9:03 AM
this one might be hallucinatory i forgot to RAG it
[9:03 AM]Thursday, March 12, 2026 9:03 AM
but it sounds right, lemme know and i'll regenerate. you know actually is gmax open source?
[9:03 AM]Thursday, March 12, 2026 9:03 AM
oh that's an idea
[9:04 AM]Thursday, March 12, 2026 9:04 AM
LOL I think this is an alternate universe. Wth. That's not gmax  (edited)Thursday, March 12, 2026 9:05 AM
[9:05 AM]Thursday, March 12, 2026 9:05 AM
https://github.com/buyrs/gmax-crm (edited)Thursday, March 12, 2026 9:09 AM

@r
 [T3M4], T3M4
Although I only have 203tell converted to ascii, the rest from the lyt are still in binary

Wizard [C#], C# — 9:05 AMThursday, March 12, 2026 9:05 AM
Waymin. I have no idea if you need all of the pieces or not
[9:06 AM]Thursday, March 12, 2026 9:06 AM
But your message really doesn't make sense. LYT is an ascii file
[9:07 AM]Thursday, March 12, 2026 9:07 AM
Oh you mean the model. I'd probably do the adjoining rooms too just to remove extra variables you don't want to be testing
[9:07 AM]Thursday, March 12, 2026 9:07 AM
Like when you go into the game, if you can't walk to the next room, it'll narrow down the problem if you regenerate those as well.

r [T3M4], T3M4 — 9:07 AMThursday, March 12, 2026 9:07 AM
Meaning all the other models found in the layout of the room are still in binary, vs the one that I converted to ascii
[9:08 AM]Thursday, March 12, 2026 9:08 AM
But I'm just reusing part of that same model to add a new area
[9:08 AM]Thursday, March 12, 2026 9:08 AM
Same model same walkmesh

Wizard [C#], C# — 9:08 AMThursday, March 12, 2026 9:08 AM
I thought you were adding a whole new area to an existing module?
[9:08 AM]Thursday, March 12, 2026 9:08 AM
you probably need a new model or at least to modify that model and the walkmesh i would expect

r [T3M4], T3M4 — 9:09 AMThursday, March 12, 2026 9:09 AM
It's a "new" area, but it uses the area that's next to it

Wizard [C#], C# — 9:09 AMThursday, March 12, 2026 9:09 AM
Oh I see what's happening.
[9:09 AM]Thursday, March 12, 2026 9:09 AM
Yeah

r [T3M4], T3M4 — 9:09 AMThursday, March 12, 2026 9:09 AM
In the photo above in the top left, the two square things
[9:09 AM]Thursday, March 12, 2026 9:09 AM
I copied the one from the left and put it on the right part where the fake door was removed

Wizard [C#], C# — 9:10 AMThursday, March 12, 2026 9:10 AM
Doesn't look like you have the walkmesh loaded in that photo though?

r [T3M4], T3M4 — 9:10 AMThursday, March 12, 2026 9:10 AM
It's the black outline
:thumbsup:
Click to react
:joy:
Click to react
:heart:
Click to react
Add Reaction
Reply
Forward
More
[9:10 AM]Thursday, March 12, 2026 9:10 AM
The right part is the new area
:thumbsup:
Click to react
:joy:
Click to react
:heart:
Click to react
Add Reaction
Reply
Forward
More
[9:10 AM]Thursday, March 12, 2026 9:10 AM
It has the walkmesh, the left part is a transition area
:thumbsup:
Click to react
:joy:
Click to react
:heart:
Click to react
Add Reaction
Reply
Forward
More
[9:10 AM]Thursday, March 12, 2026 9:10 AM
Into the czerka compound
:thumbsup:
Click to react
:joy:
Click to react
:heart:
Click to react
Add Reaction
Reply
Forward
More

Wizard [C#], C# — 9:11 AMThursday, March 12, 2026 9:11 AM
Ah I see yes
:thumbsup:
Click to react
:joy:
Click to react
:heart:
Click to react
Add Reaction
Edit
Forward
More
NEW

r [T3M4], T3M4 — 9:12 AMThursday, March 12, 2026 9:12 AM
I can click on the walkmesh and select the entire thing
:thumbsup:
Click to react
:joy:
Click to react
:heart:
Click to react
Add Reaction
Reply
Forward
More
[9:12 AM]Thursday, March 12, 2026 9:12 AM
Not sure how to start editing the verticies though
```

---

AI LLM Agent recursing over KOTORMax:
Yeah, that screenshot tells the story.

What you have there is basically **visual geometry plus reused/copied walkmesh-looking data**, but **not a valid new room transition setup yet**. Reusing the same black-highlighted walkmesh chunk from the original room is okay as a **starting shape**, but the game is not going to treat that as “new connected room works now.” You still need the **new room’s own walkmesh boundary** and then the **roomlink** between the two rooms. ([deadlystream.com](https://deadlystream.com/topic/5731-kotormax/?utm_source=openai))

## What this means in practice

Right now, think of it like this:

- **visible model** = what you see
- **walkmesh shape** = where movement can happen
- **roomlink** = what tells the engine “crossing this edge moves you into that neighboring room”

You currently have the first, and maybe part of the second, but not the third. That’s why porting the MDL by itself won’t solve it. ([deadlystream.com](https://deadlystream.com/topic/11729-k1-creating-a-new-room-in-an-existing-module/?utm_source=openai))

## So, directly answering you:

**Yes, you can reuse part of the same walkmesh as a template.**  
**No, you should not rely on that reused piece by itself as the final solution.**

If that black section is just copied from the original room, then the next thing you need to do is:

### 1. Make it the threshold shape only
Use that copied section just to form the new doorway/floor crossing area.

Make sure:
- it lines up in **Top** view
- it lines up in **Front/Left** view
- same floor height
- no overlap
- no gap
- no skinny junk triangles at the seam

### 2. Keep each room’s walkmesh separate
Do **not** make one giant combined walkmesh across both rooms.

Each room should still have its **own** walkmesh / room boundary. The seam between them is where the room transition happens.

### 3. Load the area with the LYT from **Area Tools**
Don’t keep trying to solve this from isolated model imports. The reason the LYT mattered is because KOTORMax expects layout import through **Area Tools**, and that’s what gives you the right room context for placement and linking. The “invalid ascii” error happens when the `.lyt` is being treated like a model ASCII file instead of being loaded through the area workflow. ([deadlystream.com](https://deadlystream.com/topic/5731-kotormax/?utm_source=openai))

### 4. Then assign the roomlink across that seam
That is the actual “make it traversable” step.

If you only copy part of the old walkmesh and move it over, the engine still sees old adjacency unless you relink the room boundary to the new neighboring room. Community guidance on this is very clear: if you change which rooms are adjacent, the old roomlinks won’t match and must be reassigned in KOTORMax. ([deadlystream.com](https://deadlystream.com/topic/11729-k1-creating-a-new-room-in-an-existing-module/?utm_source=openai))

## What I want you to do next

Do this next, in order:

1. **Stop importing the `.lyt` from MDL Loading** if that’s what you were doing.
2. Expand **Area Tools** and import the area layout there.
3. Put the needed room ASCII models in the same folder as the `.lyt`/`.vis` if you want KOTORMax to load them with the layout.
4. Use the copied black walkmesh section only as a **starter threshold**.
5. Move/edit vertices until the new room’s threshold and old room’s threshold line up perfectly.
6. Keep the old room and new room as **separate rooms**.
7. After that, go to the **roomlink** step.

## Important warning

If you keep working from just a “ported MDL with reused black walkmesh,” you can absolutely get something that *looks* right in gmax and still never works in-game. That exact kind of failure shows up in other modders’ reports when roomlinks/layout context aren’t being handled properly. ([deadlystream.com](https://deadlystream.com/topic/11729-k1-creating-a-new-room-in-an-existing-module/?utm_source=openai))

## Short version you can follow right now

- **Reusing the same walkmesh chunk is okay**
- **It is only a template**
- **Do not merge both rooms into one walkmesh**
- **Load the area via LYT in Area Tools**
- **Then relink the room boundary**

If you want, send a screenshot of your **expanded Area Tools panel**, and I can tell you exactly which control to hit next.


--- another response:

No — **don’t just port/import individual room models instead of loading the LYT** if the goal is to fix room-to-room transitions. For this specific task, the LYT route is the correct one, because KOTORMax’s area workflow is what establishes the room context needed for layout positions and roomlink editing. Community guidance is explicit that **you load a LYT via Area Tools**, and optionally have it auto-load models from the same folder. The `Use Layout Position` checkbox in **MDL Loading** is **not** for loading vanilla rooms against a loose `.lyt`; it only works if the ASCII model already contains layout-position data in its header, which vanilla-decompiled models generally do **not** have. ([deadlystream.com](https://deadlystream.com/topic/5731-kotormax/))

The likely reason he is getting **“invalid ascii” when trying to import the LYT** is that he is trying to load the `.lyt` through the **MDL Loading** panel, which is for **ASCII model files**, not layout files. KOTORMax’s own feature list separates **ASCII model import/export** from **LYT/VIS import/export**, and a Deadly Stream answer specifically says: **“You load a LYT via the area tools.”** ([deadlystream.com](https://deadlystream.com/topic/5731-kotormax/))

## Direct answer to his question

Send him this:

**No, don’t skip the LYT for this.** If you’re trying to fix room transitions, importing individual models alone is the wrong workflow. The `.lyt` needs to be loaded from **Area Tools**, not from **MDL Loading**. The “invalid ascii” error usually means KOTORMax is treating the `.lyt` like a model ASCII file. Also, `Use Layout Position` in MDL Loading won’t help with vanilla-decompiled models, because that only works when the model ASCII already has layout position data written into its header from a prior KOTORMax export. ([deadlystream.com](https://deadlystream.com/topic/5731-kotormax/))

**And yes:** if you want the LYT import to pull the room models in automatically, the room models in that folder generally need to be available in the form KOTORMax expects for that workflow — i.e. the corresponding **ASCII models** in the same folder, not just raw binary game models. There’s a Deadly Stream note saying Area Tools can load models from the same folder at the same time, and another modding write-up says to import the layout file with **“With VIS file”** and **“With models”** checked. ([deadlystream.com](https://deadlystream.com/topic/5731-kotormax/))

## What he should do next, step by step

1. **Do not use `MDL Loading` to open the `.lyt`.**  
   That panel is for `.mdl.ascii` model import, which is why `.lyt` throws an ASCII error. ([deadlystream.com](https://deadlystream.com/topic/5731-kotormax/))

2. **Expand `Area Tools` in the left sidebar.**  
   Use the area/layout import function there.

3. **Load the `.lyt` from Area Tools**, not from the model importer.  
   If there are options like:
   - `With VIS file`
   - `With models`
   
   turn them on. That matches documented community workflow. ([deadlystream.com](https://deadlystream.com/topic/9496-inner-workings/page/6/?utm_source=openai))

4. **Put the area’s ASCII room models in the same folder as the `.lyt`**, so Area Tools can load them with the layout.  
   If auto-loading models doesn’t work, load the LYT first, then load the room ASCII models manually into that scene. A Deadly Stream explanation says manual model loading after LYT import should still place them correctly due to the pre-existing AuroraBase of the same name in the scene. ([deadlystream.com](https://deadlystream.com/topic/5731-kotormax/))

5. **Do not rely on raw binary `.mdl/.mdx` alone for this editing step.**  
   KOTORMax is an ASCII model workflow tool; its release page says it imports/exports **ascii model files** for KOTOR/KOTOR2. ([deadlystream.com](https://deadlystream.com/topic/5731-kotormax/))

## Do all layout models need to be converted first?

**Practically: yes, at least the ones you want loaded into the editable area scene should be in ASCII form.** KOTORMax’s import/export workflow is centered on ASCII models, and Area Tools’ “load models in same folder” behavior assumes those model sources are available in a KOTORMax-loadable form. If he only has the `.lyt` plus raw binaries, the layout import may load the room placeholders/layout structure, but not the editable room geometry/walkmesh content he actually needs. ([deadlystream.com](https://deadlystream.com/topic/5731-kotormax/))

So the safe instruction is:

- **Convert the room models you need to ASCII first**
- put them in the same folder as the `.lyt` and `.vis`
- then import the `.lyt` through **Area Tools**

## Important nuance

If he absolutely just wants to **look at one room**, then sure, importing individual models is fine. But if he wants to:
- align two rooms,
- fix crossing,
- edit roomlinks,
- or verify adjacency in the actual area,

then **he really does need the LYT/area workflow**. A later modder report also shows that hand-editing roomlinks outside the proper KOTORMax area workflow can fail to persist after recompilation, which is another reason not to shortcut this part. ([deadlystream.com](https://deadlystream.com/topic/11729-k1-creating-a-new-room-in-an-existing-module/?utm_source=openai))

## Short message version you can paste to him

**You’re probably loading the `.lyt` in the wrong panel.**  
Don’t load it through **MDL Loading** — that importer expects **model ASCII**, so it throws “invalid ascii.” Load the `.lyt` from **Area Tools** instead. If you want it to pull the room models in automatically, put the area’s **ASCII room models** in the same folder and enable options like **With VIS file** / **With models** if present. Also, `Use Layout Position` in MDL Loading won’t help for vanilla-decompiled models; that only works for models whose ASCII already has layout-position data embedded from a previous KOTORMax export. ([deadlystream.com](https://deadlystream.com/topic/5731-kotormax/))

If you want, I can now write the **exact next reply** you should send him in Discord style, short and natural.


---

yet another:

Here’s the **direct fix** for the problem described in that conversation:

## Short version

If two KotOR room models line up visually but you **still can’t walk from one to the other**, the problem is usually **not** the visible geometry. It’s the **room-to-room walkmesh links**. In KotOR indoor areas, crossing between rooms depends on the room walkmesh’s **roomlinks / transition edges**, not just matching vertices or painting surfaces. Those links need to be reassigned in **KOTORMax** (or another dedicated roomlink-capable tool), especially if you are adding or rearranging rooms. ([deadlystream.com](https://deadlystream.com/topic/8517-adding-existing-rooms-to-a-module/))

Also: for this specific workflow, **KOTORBlender is not the reliable tool** for finalizing room transitions. Community sources explicitly note that this functionality is available in **KOTORMax**, while Blender support is incomplete or absent for this part of the pipeline. ([deadlystream.com](https://deadlystream.com/topic/8517-adding-existing-rooms-to-a-module/))

---

# What actually has to be fixed

For an indoor area like Telos/Citadel Station, you need all of these to agree:

1. **The rooms must be positioned correctly in the area layout**
2. **Each room’s walkmesh edge must physically line up with the neighboring room**
3. **The roomlinks must be reassigned to the new adjacency**
4. **The area `.lyt` and `.vis` must include the new/custom rooms**
5. **The exported room must include/update its `.wok`**
6. **You must compile back to binary with a modern tool such as MDLEdit / newer MDLOps**

If you only do #1 and #2, you can get a model that *looks* correct but still blocks crossing. ([deadlystream.com](https://deadlystream.com/topic/8517-adding-existing-rooms-to-a-module/))

---

# Important correction to the earlier advice

Per your note, I’m **not** going to dwell on the `.ascii` import issue.

The real blocker for the end goal is this:

## You do **not** fix room crossing just by:
- lining up meshes,
- combining walkmeshes,
- repainting walkmesh materials,
- or editing roomlinks by hand in ASCII and expecting the compiler to preserve bad/incomplete linkage.

Community guidance on Deadly Stream specifically says that when using vanilla rooms in a changed layout, the original roomlinks no longer match, and the solution is to **load the area and reassign the room links in KOTORMax**. ([deadlystream.com](https://deadlystream.com/topic/8517-adding-existing-rooms-to-a-module/))

---

# What the UI in your screenshots is showing

From the screenshots:

- Left panel is the KOTORMax rollout stack.
- You have:
  - **MDL Loading**
  - **MDL Exporting**
  - **Preferences**
  - **Area Tools** collapsed
- In **Preferences**, the checkbox **Export WOK File** is visible.
- In **MDL Loading**, **Use Layout Position** is visible.

Those two items matter, but for your final objective:

## 1) `Export WOK File`
Yes — that is set in **gmax/KOTORMax**, exactly where your screenshot shows it. If you are editing an area room and expect the walkmesh to update, this should generally be enabled before export. ([deadlystream.com](https://deadlystream.com/files/file/1151-kotormax/))

## 2) `Use Layout Position`
This is **not** magic auto-layout from a random `.lyt` in the folder. Community discussion says it works when layout data is embedded/exported appropriately, and the proper way to load an area layout is through **Area Tools**. ([deadlystream.com](https://deadlystream.com/topic/5731-kotormax/?utm_source=openai))

So for room editing, don’t just import one model and hope layout handling sorts itself out. **Load the area via Area Tools / LYT workflow first**, then work inside that scene. ([deadlystream.com](https://deadlystream.com/topic/5731-kotormax/))

---

# The correct workflow in gmax/KOTORMax

## Goal A: add or reposition a room and make the player walk across the seam

### Step 1: work with a full area setup, not isolated room guessing
For indoor modules, extract into one working folder at minimum:

- the room models you are editing
- their walkmeshes / `.wok`
- the area `.lyt`
- the area `.vis`

KOTORMax supports **LYT and VIS import/export**, and that is the intended pipeline for this kind of work. ([deadlystream.com](https://deadlystream.com/files/file/1151-kotormax/))

### Step 2: load the area through **Area Tools**
In the screenshots, **Area Tools** is collapsed. Expand that and use the area/layout import functionality rather than importing a room in isolation. KOTORMax’s listed feature set explicitly includes **LYT and VIS file Import and Export**. ([deadlystream.com](https://deadlystream.com/files/file/1151-kotormax/))

Why this matters:
- the room indices/order matter,
- adjacency depends on the area layout,
- and roomlinks are tied to room relationships, not just mesh proximity. ([deadlystream.com](https://deadlystream.com/topic/8517-adding-existing-rooms-to-a-module/))

### Step 3: position the new/custom room correctly
Make sure the room is placed where it belongs in the layout.

If you are cloning/recycling vanilla rooms:
- give the room and related nodes **new custom names**
- do **not** rely on vanilla room models keeping their old links while being used in a new arrangement. Community advice explicitly warns that if the LYT uses vanilla room models, their walkmesh links still correspond to the original layout. ([deadlystream.com](https://deadlystream.com/topic/8517-adding-existing-rooms-to-a-module/))

### Step 4: line up the walkmesh seam physically
At the shared doorway / corridor seam:

- the walkable faces should meet cleanly
- no vertical mismatch
- no gap
- no overlap lip
- no blocking face with non-walkable material at the threshold

This is necessary, but **not sufficient**.

### Step 5: reassign the **roomlinks**
This is the key step most people miss.

KOTORMax includes a **Roomlink Editor** / roomlink functionality as one of its major added features. ([deadlystream.com](https://deadlystream.com/topic/5731-kotormax/))

You need to use that to tell the room walkmesh:
- which edge/face boundary connects to which neighboring room,
- using the room numbering/order defined by the layout.

This is why people can stand at a visually perfect seam and still fail to cross: the engine’s room transition data is wrong. The Deadly Stream explanation even shows the ASCII `roomlinks` entries and notes that KOTORMax is the practical solution for reassigning them. ([deadlystream.com](https://deadlystream.com/topic/8517-adding-existing-rooms-to-a-module/))

### Step 6: export with **Export WOK File** enabled
In your screenshot, that preference is already visible. Keep it enabled when exporting the edited room(s), otherwise you can wind up updating the model but not the corresponding area walkmesh file. ([deadlystream.com](https://deadlystream.com/files/file/1151-kotormax/))

### Step 7: export `.lyt` / `.vis` if the area layout changed
If you added a room, changed room positions, or changed visibility relationships, export the updated area layout data too. KOTORMax supports that directly. ([deadlystream.com](https://deadlystream.com/files/file/1151-kotormax/))

### Step 8: compile the ASCII outputs with MDLEdit / current MDLOps
KOTORMax’s own release page says it was designed for **MDLEdit** and the newer **MDLOps**, and that older MDLOps versions may ignore data or crash. ([deadlystream.com](https://deadlystream.com/files/file/1151-kotormax/))

---

# What to do specifically for the Telos/Citadel Station goal

The user’s goal was:

- TSL
- add new areas to Citadel Station
- replace fake door textures with real traversable areas/doors
- make walkmesh crossings work

For that, the practical route is:

## If you are adding a new room behind a “fake door”
1. Duplicate or create the new room model with unique names.
2. Add that room to the area layout.
3. Load the area in KOTORMax via the layout tools.
4. Align the new room’s threshold walkmesh with the existing room’s threshold.
5. Reassign the roomlinks for **both** sides of the connection.
6. Export updated room model(s), `.wok`, `.lyt`, and `.vis`.
7. Compile.
8. Test in-game.

If you skip step 5, the player often won’t cross even if the door opening looks perfect. ([deadlystream.com](https://deadlystream.com/topic/8517-adding-existing-rooms-to-a-module/))

---

# About doors specifically

If the end goal is not just an open threshold but an **actual functioning door**, then there are two separate concerns:

## A. Room-to-room traversal
Handled by:
- room walkmesh alignment
- roomlinks
- layout

## B. Door object behavior
Handled by:
- proper door model
- door walkmesh / doorhook setup as applicable
- module/UTD scripting/game-side door setup

In other words, fixing the seam crossing does **not automatically create a fully working scripted door**. It only solves the navigation boundary between rooms.

---

# What **not** to waste time on

For this exact problem, don’t keep cycling through these as your main fix:

- repainting all walkmesh to metal
- brute-force merging two walkmeshes together
- assuming Blender vertex paint alone defines valid transitions
- hand-editing roomlinks in ASCII without verifying KOTORMax’s roomlink assignment in the actual area scene

Those can affect collision/material behavior, but they do **not replace proper roomlink assignment**. ([deadlystream.com](https://deadlystream.com/topic/8517-adding-existing-rooms-to-a-module/))

---

# How to use the confusing gmax interface in practice

Based on your screenshots, here’s the most useful orientation:

## Left panel
This is where most KOTORMax work happens.

### `MDL Loading`
Use this for model import, but for room work do **not** rely on it alone.

### `Area Tools`
This is the one you should expand for area/layout work. Since KOTORMax supports **LYT/VIS import/export**, this is the section you want for loading the whole area context. ([deadlystream.com](https://deadlystream.com/files/file/1151-kotormax/))

### `MDL Exporting`
Use this to export the selected room/base after edits.

### `Preferences`
This is where the visible important toggles are in your screenshot:
- **Export WOK File** → keep on for room/walkmesh work
- **Use Base Pointers** → usually leave as default unless a guide says otherwise
- **Use .ascii By Default** → irrelevant here since your import issue is already solved

---

# Recommended concrete procedure for the user in that conversation

If I were answering that person directly, I’d say this:

1. **Stop trying to solve the crossing in Blender alone.**
   KOTORBlender may be fine for some geometry work, but indoor room transition linking is the part that needs **KOTORMax**. ([deadlystream.com](https://deadlystream.com/topic/8517-adding-existing-rooms-to-a-module/))

2. **In gmax, expand `Area Tools` and load the area layout (`.lyt` / `.vis`)**, not just a single room model. KOTORMax supports area import/export specifically for this. ([deadlystream.com](https://deadlystream.com/files/file/1151-kotormax/))

3. **Put both the original room and the new room into the same area scene** so you can verify the seam in-place.

4. **Align the walkmesh threshold exactly** where the two rooms meet.

5. **Open/use the Roomlink Editor / roomlink functionality and reassign the shared edge(s)** so each room knows the other room is adjacent. This is the actual fix for “can’t walk into the new room.” ([deadlystream.com](https://deadlystream.com/topic/8517-adding-existing-rooms-to-a-module/))

6. **Make sure `Export WOK File` is checked** in Preferences before export. Your screenshot shows that control directly in gmax. ([deadlystream.com](https://deadlystream.com/files/file/1151-kotormax/))

7. **Export the edited rooms and the updated area files** (`.lyt`, `.vis` as needed), then compile with **MDLEdit** or modern MDLOps. KOTORMax was designed for those tools. ([deadlystream.com](https://deadlystream.com/files/file/1151-kotormax/))

8. **Test in-game.**
   If the player still can’t cross:
   - verify both sides’ roomlinks, not just one side
   - verify the room order/index in the layout
   - verify you are using custom renamed room models, not unchanged vanilla references in a rearranged layout. ([deadlystream.com](https://deadlystream.com/topic/8517-adding-existing-rooms-to-a-module/))

---

# Best explanation of why this happens

The clearest external explanation I found is this Deadly Stream guidance:

- room crossing is defined in the walkmeshes by edges linking to adjoining rooms,
- the ASCII contains `roomlinks`,
- if you change which rooms are adjacent, the vanilla links no longer match,
- and the fix is to load the full layout and reassign the links in KOTORMax. ([deadlystream.com](https://deadlystream.com/topic/8517-adding-existing-rooms-to-a-module/))

That lines up exactly with the symptoms in your conversation.

---

# Concise final answer you could send

Use **gmax + KOTORMax**, not Blender, for the final room-transition fix. The reason the player can’t walk from one room into the next is almost certainly that the **roomlinks are wrong**, not just the mesh alignment. Load the **whole area** through **Area Tools** using the area’s **`.lyt` / `.vis`**, place the new/custom room in the proper layout position, line up the threshold walkmesh, then use KOTORMax’s **Roomlink Editor/functionality** to reassign the shared walkmesh edge(s) so each room links to the other. Keep **`Export WOK File` enabled** in Preferences, then export the updated room(s) and area files and compile with **MDLEdit** or current MDLOps. If you reused vanilla rooms in a new arrangement, rename them to custom models and relink them, because vanilla roomlinks still point to the original layout. ([deadlystream.com](https://deadlystream.com/topic/8517-adding-existing-rooms-to-a-module/))

If you want, I can turn this into a **clean step-by-step “click here / expand this panel / do this next” guide specifically for the exact KOTORMax gmax UI shown in the screenshots**.

-- and another:

Now I have a complete, authoritative picture from the source code. Let me compile the definitive answer.

---

## Authoritative KOTORMax Import Workflow for `203tell` (TSL Room Model)

Here's exactly what r needs to do, derived directly from the codebase.

---

### Step 1: Convert the binary `.mdl` to ASCII with MDLOps

KOTORMax **only reads ASCII MDL files** — the import function in `odyssey_fn_import.ms` explicitly checks whether the first byte of the file is `0` (i.e., a binary MDL header) and rejects it:

```maxscript name=odyssey_fn_import.ms url=https://github.com/OpenKotOR/KOTORMax/blob/af4e4a37ac498585b5bf169ac3c4bee874542e6f/KOTORMax/kotormax_scripts/odyssey_fn_import.ms#L530-L536
    -- Open up the file and check to see if its a binary file
    local binMdlStream = fopen pFile "rb"
    local isNotBinary = ReadByte binMdlStream
    fclose binMdlStream

    if (isNotBinary == 0) then MessageBox("Invalid ascii MDL file!")
```

Use MDLOps (or MDLedit) to convert `203tell.mdl` → ASCII. The output from MDLedit will be named something like `203tell-mdledit.mdl.ascii` — that's fine, but the **filename matters** (see Step 2).

---

### Step 2: Name the file correctly — `<modelname>.mdl.ascii`

This is the root of the "no appropriate import module found" problem. Look at how `kx_gui_import.ms` strips the filename to find companion `.pwk`/`.dwk` files:

```maxscript name=kx_gui_import.ms url=https://github.com/OpenKotOR/KOTORMax/blob/af4e4a37ac498585b5bf169ac3c4bee874542e6f/KOTORMax/kotormax_scripts/kx_gui_import.ms#L115-L122
		local StrictFilename = mdlFileName
		while matchPattern StrictFilename pattern:"*.*" do StrictFilename = getFilenameFile  StrictFilename
        local pwk_file = (getFilenamePath mdlFileName)+StrictFilename+".pwk.ascii"
		if (not kx_existFile pwk_file) then pwk_file = (getFilenamePath mdlFileName)+StrictFilename+".pwk"
        local dwk_file = (getFilenamePath mdlFileName)+StrictFilename+".dwk.ascii"
		if (not kx_existFile dwk_file) then dwk_file = (getFilenamePath mdlFileName)+StrictFilename+".dwk"
```

That `while matchPattern StrictFilename pattern:"*.*"` loop **strips ALL extensions** until there are none left. So `203tell-mdledit.mdl.ascii` strips down to `203tell-mdledit` — then it looks for `203tell-mdledit.pwk.ascii`, etc. This is not wrong per se, but the model name inside the ASCII file must match the actual model name `203tell`, not `203tell-mdledit`.

**Rename the file to exactly: `203tell.mdl.ascii`**

The browse dialog in KOTORMax is driven by the `g_dotAscii` setting:

```maxscript name=kx_gui_import.ms url=https://github.com/OpenKotOR/KOTORMax/blob/af4e4a37ac498585b5bf169ac3c4bee874542e6f/KOTORMax/kotormax_scripts/kx_gui_import.ms#L244-L249
	on import_browse_button pressed do
	(
		local sPattern = "Odyssey Ascii Model (*.mdl)|*.mdl|Odyssey Ascii Model (*.mdl.ascii)|*.mdl.ascii|"
		if kx_itob g_dotAscii then sPattern = "Odyssey Ascii Model (*.mdl.ascii)|*.mdl.ascii|Odyssey Ascii Model (*.mdl)|*.mdl|"
		
	    local filename = getOpenFileName caption:"Import mdl" types:sPattern
```

- If `g_dotAscii = 1` (the default in `kotormax.ini`), the file browser shows `.mdl.ascii` files **first** and `.mdl` second.
- If `g_dotAscii = 0`, it shows `.mdl` first.

Since `dotascii=1` is the default, the browse button will look for `.mdl.ascii` by default. **The file must have the `.mdl.ascii` extension** to show up without manually typing the filename.

---

### Step 3: Check/set the "Use .ascii By Default" checkbox in the Prefs rollout

From `kx_gui_speedbtns.ms`:

```maxscript name=kx_gui_speedbtns.ms url=https://github.com/OpenKotOR/KOTORMax/blob/af4e4a37ac498585b5bf169ac3c4bee874542e6f/KOTORMax/kotormax_scripts/kx_gui_speedbtns.ms#L449-L450
	checkbox chk_dotascii "Use .ascii By Default" checked:(kx_itob (g_dotAscii))
```

In the **Prefs** rollout of the KOTORMax floater, make sure **"Use .ascii By Default"** is **checked**. This makes the file browser prioritize `.mdl.ascii`. This matches `dotascii=1` in the ini.

---

### Step 4: The exact import workflow

1. Open GMax with KOTORMax loaded.
2. In the KOTORMax floater, expand the **"Import"** rollout (listed as `ImportRollout`).
3. Click the **browse button** next to the filename field.
4. Navigate to your `203tell.mdl.ascii` file and select it. It **will appear** in the dialog because the extension matches.
5. Leave the radio button on **"Import Geom+Anims"** (default, state 1).
6. Leave **"Use Layout Position"** checked (default) — TSL room models are positioned via `.lyt`, so this is correct.
7. Click **Import**.

KOTORMax will automatically look for `203tell.pwk.ascii` (or `.pwk`) and `203tell.dwk.ascii` (or `.dwk`) in the same directory and import them automatically if present.

---

### Step 5: For the walkmesh specifically

Since his goal is fixing **walkmeshes**, he needs the `.wok` file too. KOTORMax has a **walkmesh modifier** (`odyssey_mod_walkmesh.ms`) and `ImportOdysseyWalkmesh` function built in. For a room model like `203tell`:

- The walkmesh is embedded in the MDL itself as an `aabb` node — it gets imported automatically with the geometry.
- If he's **editing** the walkmesh (adding new walk areas), he needs to apply the **Odyssey Walkmesh modifier** to his new geometry. The `wokmat.ini` file in the repo defines the material types (walkable, non-walkable, etc.).
- After editing, export from KOTORMax — if **"Export WOK"** is checked in the Prefs rollout (`chk_exportwok`), it will write the `.wok` file alongside the `.mdl.ascii`.

---

### TL;DR Checklist

| Step | Action |
|------|--------|
| 1 | Convert `203tell.mdl` to ASCII using MDLOps/MDLedit |
| 2 | **Rename output file to `203tell.mdl.ascii`** (strip the `-mdledit` prefix garbage) |
| 3 | In KOTORMax Prefs rollout, confirm **"Use .ascii By Default"** is checked |
| 4 | In KOTORMax Import rollout, use the Browse button → it will now show `.mdl.ascii` files |
| 5 | Select `203tell.mdl.ascii` and click Import |
| 6 | For walkmesh editing, use the Odyssey Walkmesh modifier on new geometry and re-export with "Export WOK" enabled |

The "no appropriate import module found" error was almost certainly because the file was named `203tell-mdledit.mdl.ascii` — the `-mdledit` in the name isn't the issue per se, but if GMax's own import dialog was being used instead of KOTORMax's built-in browse button, it wouldn't know what to do with a `.mdl.ascii` file. **Always use KOTORMax's own Import rollout**, never File → Import from GMax's menu.