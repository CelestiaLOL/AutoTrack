#  AutoTrack – Blender Plugin

A handy Blender plugin that automatically adds a **Track To constraint** to newly added objects (Meshes, Lights, or Cameras) if an Empty named `"Track"` exists. Fully configurable through the Sidebar UI.

---

##  Features

-  Automatically adds `Track To` constraint on new Mesh, Light, or Camera objects
-  Supports custom empty naming
-  Manual controls for applying/removing constraints
-  UI to configure which object types are affected
-  Create a "Track" empty via a button
-  Parent the Track Empty to any object (with eyedropper)
-  Make objects immune to the plugin with a toggle

---

##  Installation

1. **Download the plugin**  
   Save the plugin script as a `.py` file.

2. **Install it in Blender**  
   - Open Blender.
   - Go to **Edit > Preferences > Add-ons**.
   - Click **Install**, then select the `AutoTrackPlugin.py` file.
   - Enable the add-on by checking the checkbox.

3. **Access the Plugin**  
   - Open the **3D Viewport**.
   - Go to the right Sidebar (**N** key) → **Track Tools** tab.

---

##  How To Use

1. Click **"Add Track Empty"** to create the tracking empty.
   - It will be named `"Track"` by default and placed at the origin.
   - It’s also hidden from selection when parented.

2. Enable the plugin with the **"Enable Plugin"** toggle.

3. Choose which object types should receive constraints (Meshes, Lights, Cameras).

4. Newly added objects will automatically track the `"Track"` Empty.

5. Use the **eyedropper tool** to parent the `"Track"` Empty to any object (it stays at the origin of the parent).

6. Use the **"Apply to Selected"** and **"Remove Constraints"** buttons to manually manage constraints.

7. Want an object excluded? Select it and toggle **"Exclude from Track Plugin"** in the Sidebar under Object properties.

---

##  Notes

- The `"Track"` Empty can be renamed using the "Track Target Name" field.
- Parenting keeps the Empty at the origin of the target object.
- The plugin avoids reapplying constraints on already constrained objects.

---

##  Compatibility

- Blender 2.80+
- Tested in Blender 4.4

---

## 🐾 Credits

Made with love by **CelestiaLOL** ✨  
Enjoy automating your camera and object rigs!



If u find any bugs
.
.
.
.
.
Cry about it HAHAHAHAHA
