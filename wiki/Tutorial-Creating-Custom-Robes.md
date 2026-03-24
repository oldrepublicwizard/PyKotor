# Tutorial: Creating custom robes

*This tutorial is merged from the Holocron Toolset in-app help (Tools/HolocronToolset/src/toolset/help/tutorials/).*

This tutorial covers creating a new, custom-textured robe and adding it to the game. The steps use KotOR 1 but are very similar for TSL.

## Step 1: Extract Resources

Extract the necessary files into a folder for editing.

1. Get the **player model textures** (male and female). Use the existing red robes: **pmbi03** and **pfbi03**. In the Textures tab, tick **Decompile** and **Extract TXI options**. Find them under the "tpa" texture packs in the dropdown.
2. Get the **icon**: **ia_jedirobe_003** from the "gui" option in the texture pack dropdown.

You should have 6 files. Rename the numbers from **03/003** to **05/005** (we are making a fifth robe variant).

![Extract textures](https://raw.githubusercontent.com/OldRepublicDevs/HolocronToolset/refs/heads/master/src/toolset/help/images/tutorials1-creatingCustomRobes=1.png)

## Step 2: Edit the textures

Edit the images in an editor that supports transparency (e.g. Paint.NET on Windows; avoid MS Paint). For this example the robes are retextured to a greenish colour.

![Edit textures](https://raw.githubusercontent.com/OldRepublicDevs/HolocronToolset/refs/heads/master/src/toolset/help/images/tutorials1-creatingCustomRobes=2.png)

## Step 3: Create the item file

Under **Core** → **Items**, open **g_a_jedirobe01**.

![Open item](https://raw.githubusercontent.com/OldRepublicDevs/HolocronToolset/refs/heads/master/src/toolset/help/images/tutorials1-creatingCustomRobes=3.png)
![Item editor](https://raw.githubusercontent.com/OldRepublicDevs/HolocronToolset/refs/heads/master/src/toolset/help/images/tutorials1-creatingCustomRobes=4.png)

Change:

- **Tag** and **ResRef** to something unique (e.g. **greenrobes**).
- **Texture Variation** to **5** (matching the renamed texture files).
- **Name** and **Description** if desired: click the ellipsis (**...**) next to the text field → **None** → enter your text.

![Set fields](https://raw.githubusercontent.com/OldRepublicDevs/HolocronToolset/refs/heads/master/src/toolset/help/images/tutorials1-creatingCustomRobes=5.png)
![Name/description](https://raw.githubusercontent.com/OldRepublicDevs/HolocronToolset/refs/heads/master/src/toolset/help/images/tutorials1-creatingCustomRobes=6.png)

Save the file with the same name as the ResRef (e.g. **greenrobes**). You should have 7 files.

![Save](https://raw.githubusercontent.com/OldRepublicDevs/HolocronToolset/refs/heads/master/src/toolset/help/images/tutorials1-creatingCustomRobes=7.png)

## Step 4: Install and test

Copy all files into your game's **override** folder. In-game, use the cheat **giveitem greenrobes** and equip from inventory.

![Override](https://raw.githubusercontent.com/OldRepublicDevs/HolocronToolset/refs/heads/master/src/toolset/help/images/tutorials1-creatingCustomRobes=8.png)
![In-game](https://raw.githubusercontent.com/OldRepublicDevs/HolocronToolset/refs/heads/master/src/toolset/help/images/tutorials1-creatingCustomRobes=9.png)

### See also

- [GFF-UTI](GFF-UTI) -- Item (UTI) format
- [TPC-File-Format](TPC-File-Format) -- Textures
- [Mod Creation Best Practices](Mod-Creation-Best-Practices) -- Override and compatibility
- [Concepts](Concepts#override-folder) -- Override folder
- [Home — toolchain overview](Home#documentation) -- When to use HoloPatcher vs CLI vs diff tools
- [HoloPatcher README for Mod Developers](HoloPatcher-README-for-mod-developers) -- Shipping a patcher-based mod
- [Concepts — module packaging](Concepts#module-packaging-for-mod-authors-override-vs-modules) -- When override alone is not enough
