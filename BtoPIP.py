#  ***** BEGIN GPL LICENSE BLOCK *****
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#  ***** END GPL LICENSE BLOCK *****

bl_info = {
    "name": "BtoPIP",
    "author": "Matthieu Gouby",
    "version": (1, 0),
    "blender": (5, 0, 1),
    "location": "View3D > Sidebar > BtoPIP",
    "description": "Render all images for Pipmak",
    "category": "Object",
}

import bpy
import math

scene = bpy.context.scene
object = bpy.ops.object

projectName = "default"

# get all empties
empties = [o for o in scene.objects if o.type == 'EMPTY']

# sort empties
empties.sort(key=lambda o: int(o.name))

# get cameras if any
cameras = [o for o in scene.objects if o.type == 'CAMERA']

# if not create one
if not cameras:
    object.camera_add(
        location=(0, 0, 0), 
        rotation=(math.pi, math.pi, 0)
    )
else:
    camera = cameras[0]
    scene.camera = camera
    camera.location=(0, 0, 0)
    camera.rotation_euler=(math.pi/2, 0, 0)
    
    
## RENDER BUTTON OPERATOR ##    

class BTOPIP_OT_renderbtn(bpy.types.Operator):
    bl_idname = "btopip.renderbtn"
    bl_label = "Render"
    
    def execute(self, context):
        
        # deselect all
        object.select_all(action='DESELECT')
                       
        # move camera to each empties then render the 6 images
        for e in empties:
            
            camera.location = (e.location.x, e.location.y, e.location.z + 1.80)
            
            scene.render.filepath = f"//{projectName}.pipmak/{e.name}/n{e.name}_front.png"
            camera.rotation_euler = (math.pi/2, 0, 0)
            bpy.ops.render.render(write_still=True)

        return {'FINISHED'}
    
    
class BTOPIP_PT_panel(bpy.types.Panel):
    bl_label = "BTOPIP"
    bl_idname = "BTOPIP_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "BTOPIP"
    
    def draw(self, context):
        layout = self.layout
        layout.operator("btopip.renderbtn")


## CLASS LIST ##

classes = (
    BTOPIP_OT_renderbtn,
    BTOPIP_PT_panel
)    


## REGISTER, UNREGISTER ##
        
def register():
    #bpy.utils.register_class(BTOPIP_OT_renderbtn)
    #bpy.utils.register_class(BTOPIP_PT_panel)
    
    for c in classes:
        bpy.utils.register_class(c)
    
def unregister():
    #bpy.utils.register_class(BTOPIP_OT_renderbtn)
    #bpy.utils.register_class(BTOPIP_PT_panel)
    
    for c in reversed(classes):
        bpy.utils.unregister_class(c)
                    
if __name__ == "__main__":
    register()                    