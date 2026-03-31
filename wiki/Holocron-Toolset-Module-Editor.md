# Holocron Toolset: Module Editor

The Module Editor is the primary workspace for editing module content in 3D or 2D. It renders the area geometry, placed objects, waypoints, triggers, and other spatial data from the currently loaded module, and lets you select, move, rotate, duplicate, and delete instances directly in the viewport. Open it from the Main Window via **Tools** → **Module Designer**.

## Controls

You can edit the controls in **Settings** (Main Window) under the **Module Designer** section.

**Tip:** Double-clicking an instance in the instance list snaps the camera to that object's location.

### Default controls (3D)

| Action                     | Keys                                 |
|----------------------------|--------------------------------------|
| Move Camera (XY)           | Hold **CTRL** and drag **LMB**       |
| Move Camera (Z)            | Hold **CTRL** and **Scroll**         |
| Move Camera (Camera Plane) | Hold **CTRL + ALT** and drag **LMB** |
| Rotate Camera              | Drag **MMB**                         |
| Zoom Camera                | **Scroll** vertically                |
| Zoom Camera                | Hold **CTRL** and drag **RMB**       |
| Select Object              | **LMB** on object                    |
| Move Object (XY)           | Drag **LMB**                         |
| Move Object (Z)            | Hold **SHIFT** and drag **LMB**      |
| Rotate Object (Yaw)        | Hold **ALT** and drag **LMB**        |
| Duplicate Object           | Hold **ALT** and **LMB**             |
| Delete Object              | **DEL**                              |
| Open Context Menu          | **RMB**                              |
| Move Camera to Selection   | **Z**                                |
| Move Camera to Cursor      | **X**                                |
| Move Camera to Entry Point | **C**                                |
| Rotate Camera Up/Down      | **Num1** / **Num3**                  |
| Rotate Camera Left/Right   | **Num7** / **Num9**                  |
| Move Camera (Numpad)       | **Num8/2/4/6**                       |
| Move Camera Up/Down        | **Q** / **E**                        |
| Zoom In/Out                | **+** / **-**                        |

### Default controls (3D – FreeCam mode)

| Action               | Keys  |
|----------------------|-------|
| Move Camera          | **W** / **S** / **A** / **D** |
| Move Camera Up/Down  | **Q** / **E** |

### Default controls (2D)

| Action                   | Keys                           |
|--------------------------|--------------------------------|
| Move Camera              | Hold **CTRL** and drag **LMB** |
| Rotate Camera            | Drag **MMB**                   |
| Zoom Camera              | **Scroll** or **CTRL + RMB**   |
| Select / Move / Rotate   | **LMB** / drag / **ALT**+drag |
| Duplicate / Delete       | **ALT + LMB** / **DEL**       |
| Context Menu             | **RMB**                        |
| Camera to Selection      | **Z**                          |

### See also

- [GFF-GIT](GFF-File-Format#git-game-instance-template) -- Game Instance Template (placeables, creatures, doors, etc.)
- [GFF-ARE](GFF-Module-and-Area#are) -- Area format
- [Indoor Map Builder User Guide](Indoor-Map-Builder-User-Guide) -- Building new areas
