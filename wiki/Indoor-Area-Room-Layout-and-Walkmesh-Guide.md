# Indoor Area — Room Layout and Walkmesh Guide

This guide ties together **indoor module** authoring: room layout, walkmesh transitions, visibility, and packaging. It is a **wiki hub**; format details live on the linked format pages.

## Workflow overview

1. **Layout** — Define rooms and transforms in **[LYT](LYT-File-Format)**. Room order determines indices used elsewhere.
2. **Walkmesh** — Each room needs a **[BWM](BWM-File-Format)** (WOK) with correct **transition** indices matching the LYT room index for doorways and crossings. See [Transitions and Door Placement](BWM-File-Format#transitions-and-door-placement).
3. **Visibility** — **[VIS](VIS-File-Format)** describes which rooms can see which; keep it in sync with the LYT room names.
4. **Area data** — **[GFF ARE](GFF-Module-and-Area#are)** and the rest of the module set follow normal module layout. Resolution order is described under:

   - [Concepts — Resource resolution](Concepts#resource-resolution-order)
   - [Resource Formats and Resolution](Resource-Formats-and-Resolution)

## Tooling

- **Holocron Indoor Map Builder**
  - [User Guide](Indoor-Map-Builder-User-Guide)
  - [Implementation Guide](Indoor-Map-Builder-Implementation-Guide)
- **Community tools** — KOTORMax, kotorblender, kaurora; tradeoffs and links are summarized in:

  - [Area Modding and Room Transitions](Area-Modding-and-Room-Transitions)
  - [Blender Integration](Blender-Integration)

## Troubleshooting

- **Cannot walk between rooms** — Usually transition IDs on walkmesh edges, LYT order, or missing/incorrect VIS. Start with [Area Modding and Room Transitions](Area-Modding-and-Room-Transitions) and the user guide section [Room crossing and walkmesh](Indoor-Map-Builder-User-Guide#room-crossing-and-walkmesh).
- **Kit / template structure** — [Kit Structure Documentation](Kit-Structure-Documentation).

## See also

- [BWM File Format](BWM-File-Format)
- [LYT File Format](LYT-File-Format)
- [VIS File Format](VIS-File-Format)
- [Reverse Engineering Findings — BWM / walkmesh / AABB](reverse_engineering_findings#bwm-walkmesh-aabb-engine-implementation-analysis) — engine-side walkmesh tree behavior
