bl_info = {
    "name": "QuickUvMap",
    "author": "Matty",
    "version": (1, 4),
    "blender": (4, 2, 0),
    "location": "View3D > Tool Shelf",
    "description": "Press E to process all selected objects; press Q to process only the last selected object safely.",
    "category": "UV"
}

import bpy

class UVSmartProjectOperatorAll(bpy.types.Operator):
    """Create New UV Map and Apply UV Smart Project to All Selected Objects (Linked Data Fix)"""
    bl_idname = "uv.smart_project_all_linked"
    bl_label = "UV Smart Project to All Selected Objects (Linked Data Fix)"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        selected_objects = context.selected_objects
        
        # Store the original selection for re-selection later
        original_selection = selected_objects[:]
        
        # Track processed meshes to avoid duplicating UV maps on linked data
        processed_meshes = set()
        
        for obj in selected_objects:
            if obj.type == 'MESH' and obj.data.name not in processed_meshes:
                # Temporarily hide all other objects
                for other_obj in selected_objects:
                    if other_obj != obj:
                        other_obj.hide_set(True)
                
                # Make the current object active
                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.mode_set(mode='OBJECT')
                
                # Get the mesh data
                mesh = obj.data
                
                # Ensure it has UV layers
                if not mesh.uv_layers:
                    self.report({'WARNING'}, f"Object {obj.name} has no UV map. Skipping.")
                    continue
                
                # Create a new UV map
                new_uv_map = mesh.uv_layers.new(name="NewUVMap")
                new_uv_map.active = True
                
                # Ensure the first UV map remains unaffected
                for uv_layer in mesh.uv_layers:
                    if uv_layer != new_uv_map:
                        uv_layer.active_render = False
                
                # Switch to edit mode to apply UV Smart Project
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.uv.smart_project()
                bpy.ops.object.mode_set(mode='OBJECT')
                
                # Unhide all objects
                for other_obj in selected_objects:
                    other_obj.hide_set(False)
                
                # Mark this mesh as processed
                processed_meshes.add(mesh.name)
        
        # Re-select all originally selected objects
        for obj in original_selection:
            obj.select_set(True)
        
        return {'FINISHED'}

class UVSmartProjectOperatorLast(bpy.types.Operator):
    """Create New UV Map and Apply UV Smart Project to Last Selected Object Safely"""
    bl_idname = "uv.smart_project_last_safe_linked"
    bl_label = "UV Smart Project to Last Selected Object (Safe with Linked Data)"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        # Get the last selected object
        obj = context.view_layer.objects.active
        
        if not obj or obj.type != 'MESH':
            self.report({'WARNING'}, "No valid last selected object found.")
            return {'CANCELLED'}
        
        # Store the original selection for re-selection later
        original_selection = context.selected_objects[:]
        
        # Deselect all other objects
        for other_obj in original_selection:
            if other_obj != obj:
                other_obj.select_set(False)
        
        # Get the mesh data
        mesh = obj.data
        
        # Ensure it has UV layers
        if not mesh.uv_layers:
            self.report({'WARNING'}, f"Object {obj.name} has no UV map. Skipping.")
            return {'CANCELLED'}
        
        # Create a new UV map
        new_uv_map = mesh.uv_layers.new(name="NewUVMap")
        new_uv_map.active = True
        
        # Ensure the first UV map remains unaffected
        for uv_layer in mesh.uv_layers:
            if uv_layer != new_uv_map:
                uv_layer.active_render = False
        
        # Switch to edit mode to apply UV Smart Project
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.uv.smart_project()
        bpy.ops.object.mode_set(mode='OBJECT')
        
        # Reselect all originally selected objects
        for other_obj in original_selection:
            other_obj.select_set(True)
        
        return {'FINISHED'}
    
def register():
    bpy.utils.register_class(UVSmartProjectOperatorAll)
    bpy.utils.register_class(UVSmartProjectOperatorLast)
    
    # Add keymap for the 'E' key
    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(name='Object Mode', space_type='EMPTY')
    kmi_e = km.keymap_items.new(UVSmartProjectOperatorAll.bl_idname, 'E', 'PRESS')
    kmi_q = km.keymap_items.new(UVSmartProjectOperatorLast.bl_idname, 'Q', 'PRESS')

def unregister():
    bpy.utils.unregister_class(UVSmartProjectOperatorAll)
    bpy.utils.unregister_class(UVSmartProjectOperatorLast)
    
    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps['Object Mode']
    for kmi in km.keymap_items:
        if kmi.idname in {UVSmartProjectOperatorAll.bl_idname, UVSmartProjectOperatorLast.bl_idname}:
            km.keymap_items.remove(kmi)
    wm.keyconfigs.addon.keymaps.remove(km)

if __name__ == "__main__":
    register()
