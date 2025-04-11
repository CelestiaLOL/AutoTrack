bl_info = {
    "name": "AutoTrack",
    "author": "CelestiaLOL",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Sidebar > AutoTrack Tab",
    "description": "Automatically assigns Track To constraint to new mesh/light/camera objects if 'Track' Empty exists.",
    "category": "Object",
}

import bpy
from bpy.app.handlers import persistent

# Function to add Track To constraint

def add_track_constraint(obj):
    if not bpy.context.scene.track_plugin_enabled:
        return

    if getattr(obj, "exclude_from_track_plugin", False):
        return

    allowed_types = []
    if bpy.context.scene.track_plugin_apply_to_meshes:
        allowed_types.append('MESH')
    if bpy.context.scene.track_plugin_apply_to_lights:
        allowed_types.append('LIGHT')
    if bpy.context.scene.track_plugin_apply_to_cameras:
        allowed_types.append('CAMERA')

    if obj.type not in allowed_types:
        return

    track_empty = bpy.data.objects.get(bpy.context.scene.track_target_name)
    if track_empty:
        existing = [c for c in obj.constraints if c.type == 'TRACK_TO']
        if not existing:
            constraint = obj.constraints.new('TRACK_TO')
            constraint.target = track_empty
            constraint.track_axis = 'TRACK_NEGATIVE_Z'
            constraint.up_axis = 'UP_Y'
            constraint.owner_space = 'WORLD'
            constraint.target_space = 'WORLD'

# Improved handler to detect newly added objects reliably
@persistent

def object_add_handler(scene):
    if not bpy.context.scene.track_plugin_enabled:
        return

    current_names = {obj.name for obj in scene.objects}
    new_objs = current_names - object_add_handler.known_objects
    object_add_handler.known_objects = current_names

    for name in new_objs:
        obj = bpy.data.objects.get(name)
        if obj:
            add_track_constraint(obj)

object_add_handler.known_objects = set()

@persistent
def init_known_objects(scene):
    object_add_handler.known_objects = set(obj.name for obj in scene.objects)

# Operator to create a Sphere Empty named as user-defined target
class OBJECT_OT_CreateSphereEmptyOperator(bpy.types.Operator):
    bl_idname = "object.create_sphere_empty"
    bl_label = "Create Sphere Empty"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        bpy.ops.object.empty_add(type='SPHERE', radius=0.3)
        track = context.active_object
        track.name = context.scene.track_target_name
        track.location = (0, 0, 0)
        track.rotation_euler = (0, 0, 0)
        track.scale = (1, 1, 1)
        track.hide_select = False
        return {'FINISHED'}

# Operator to manually apply to selected
class OBJECT_OT_ApplyTrackToSelectedOperator(bpy.types.Operator):
    bl_idname = "object.apply_track_to_selected"
    bl_label = "Apply to Selected"
    bl_description = "Manually apply Track To constraint to selected object(s)"

    def execute(self, context):
        count = 0
        for obj in context.selected_objects:
            before = len(obj.constraints)
            add_track_constraint(obj)
            after = len(obj.constraints)
            if after > before:
                count += 1

        self.report({'INFO'}, f"Track To constraint applied to {count} object(s).")
        return {'FINISHED'}

# Operator to parent Track empty to selected object
class OBJECT_OT_ParentTrackEmptyOperator(bpy.types.Operator):
    bl_idname = "object.parent_track_empty"
    bl_label = "Parent Track to Target"
    bl_description = "Parent the Track empty to the selected object or unparent if none"

    def execute(self, context):
        track_empty = bpy.data.objects.get(context.scene.track_target_name)
        target = context.scene.track_parent_target

        if not track_empty:
            self.report({'WARNING'}, "Track empty not found")
            return {'CANCELLED'}

        if target:
            track_empty.parent = target
            track_empty.matrix_parent_inverse.identity()
            track_empty.location = (0, 0, 0)
            track_empty.rotation_euler = (0, 0, 0)
            track_empty.scale = (1, 1, 1)
            track_empty.hide_select = True
            self.report({'INFO'}, f"Track parented to {target.name}")
        else:
            track_empty.parent = None
            track_empty.hide_select = False
            self.report({'INFO'}, "Track unparented")

        return {'FINISHED'}

# Operator to remove all Track To constraints
class OBJECT_OT_RemoveTrackConstraints(bpy.types.Operator):
    bl_idname = "object.remove_track_constraints"
    bl_label = "Remove Track Constraints"

    def execute(self, context):
        count = 0
        for obj in context.selected_objects:
            before = len(obj.constraints)
            obj.constraints.clear()
            after = len(obj.constraints)
            count += before - after

        self.report({'INFO'}, f"Removed {count} Track To constraint(s).")
        return {'FINISHED'}

# UI Panel
class OBJECT_PT_TrackPluginPanel(bpy.types.Panel):
    bl_label = "🧲 AutoTrack"
    bl_idname = "OBJECT_PT_track_plugin_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'AutoTrack'

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.prop(context.scene, "track_plugin_enabled", text="Enable Plugin")
        box.label(text="Track Target Name:")
        box.prop(context.scene, "track_target_name", text="")

        col = box.column()
        col.prop(context.scene, "show_affect_options", icon="TRIA_DOWN" if context.scene.show_affect_options else "TRIA_RIGHT", emboss=False, text="Affect what?")
        if context.scene.show_affect_options:
            sub = col.box()
            sub.prop(context.scene, "track_plugin_apply_to_meshes", text="Meshes")
            sub.prop(context.scene, "track_plugin_apply_to_lights", text="Lights")
            sub.prop(context.scene, "track_plugin_apply_to_cameras", text="Cameras")

        layout.separator()
        layout.label(text="Track Empty Controls:")
        row = layout.row(align=True)
        row.scale_y = 1.4
        row.operator("object.create_sphere_empty", text="Add Track Empty")

        layout.label(text="Apply/Remove Constraints:")
        row = layout.row(align=True)
        row.scale_y = 1.4
        row.operator("object.apply_track_to_selected", text="Apply to Selected")
        row = layout.row(align=True)
        row.scale_y = 1.4
        row.operator("object.remove_track_constraints", text="Remove Constraints")

        layout.separator()
        layout.label(text="Track Parenting:")
        row = layout.row(align=True)
        row.prop(context.scene, "track_parent_target", text="")
        row.operator("object.parent_track_empty", text="Parent")

        layout.separator()
        layout.label(text="Object Settings:")
        obj = context.object
        if obj:
            layout.prop(obj, "exclude_from_track_plugin")

# Register / Unregister

def register():
    bpy.utils.register_class(OBJECT_OT_CreateSphereEmptyOperator)
    bpy.utils.register_class(OBJECT_OT_ApplyTrackToSelectedOperator)
    bpy.utils.register_class(OBJECT_OT_ParentTrackEmptyOperator)
    bpy.utils.register_class(OBJECT_OT_RemoveTrackConstraints)
    bpy.utils.register_class(OBJECT_PT_TrackPluginPanel)
    bpy.types.Scene.track_plugin_enabled = bpy.props.BoolProperty(default=False)
    bpy.types.Scene.track_plugin_apply_to_meshes = bpy.props.BoolProperty(default=True)
    bpy.types.Scene.track_plugin_apply_to_lights = bpy.props.BoolProperty(default=False)
    bpy.types.Scene.track_plugin_apply_to_cameras = bpy.props.BoolProperty(default=False)
    bpy.types.Scene.show_affect_options = bpy.props.BoolProperty(default=True)
    bpy.types.Scene.track_parent_target = bpy.props.PointerProperty(type=bpy.types.Object)
    bpy.types.Scene.track_target_name = bpy.props.StringProperty(default="Track")
    bpy.app.handlers.load_post.append(init_known_objects)
    bpy.app.handlers.depsgraph_update_post.append(object_add_handler)
    bpy.types.Object.exclude_from_track_plugin = bpy.props.BoolProperty(name="Exclude from Track Plugin", default=False)

def unregister():
    bpy.utils.unregister_class(OBJECT_OT_CreateSphereEmptyOperator)
    bpy.utils.unregister_class(OBJECT_OT_ApplyTrackToSelectedOperator)
    bpy.utils.unregister_class(OBJECT_OT_ParentTrackEmptyOperator)
    bpy.utils.unregister_class(OBJECT_OT_RemoveTrackConstraints)
    bpy.utils.unregister_class(OBJECT_PT_TrackPluginPanel)
    del bpy.types.Scene.track_plugin_enabled
    del bpy.types.Scene.track_plugin_apply_to_meshes
    del bpy.types.Scene.track_plugin_apply_to_lights
    del bpy.types.Scene.track_plugin_apply_to_cameras
    del bpy.types.Scene.show_affect_options
    del bpy.types.Scene.track_parent_target
    del bpy.types.Scene.track_target_name
    del bpy.types.Object.exclude_from_track_plugin
    if object_add_handler in bpy.app.handlers.depsgraph_update_post:
        bpy.app.handlers.depsgraph_update_post.remove(object_add_handler)
    if init_known_objects in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(init_known_objects)

if __name__ == "__main__":
    register()

register, unregister = register, unregister
