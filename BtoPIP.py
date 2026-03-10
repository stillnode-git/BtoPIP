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
import os

scene = bpy.context.scene
object = bpy.ops.object

# Project Name property
bpy.types.Scene.project_name = bpy.props.StringProperty(
    name = "Project Name",
    description = "Edit the project title.",
    default = "default"
    )

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
            
            folder = f"//{scene.project_name}.pipmak/{e.name}/"
            folder = bpy.path.abspath(folder)
            
            scene.render.resolution_x = 1024
            scene.render.resolution_y = 1024
            scene.render.image_settings.file_format = "JPEG"
            
            camera.location = (e.location.x, e.location.y, e.location.z + 1.80)
            camera.data.type = 'PERSP'
            camera.data.lens = 18
            
            scene.render.filepath = os.path.join(folder, f"n{e.name}_front.jpg")
            camera.rotation_euler = (math.pi/2, 0, 0)
            bpy.ops.render.render(write_still=True)
            
            scene.render.filepath = os.path.join(folder, f"n{e.name}_right.jpg")
            camera.rotation_euler = (math.pi/2, 0, -(math.pi/2))
            bpy.ops.render.render(write_still=True)
            
            scene.render.filepath = os.path.join(folder, f"n{e.name}_back.jpg")
            camera.rotation_euler = (math.pi/2, 0, math.pi)
            bpy.ops.render.render(write_still=True)    
            
            scene.render.filepath = os.path.join(folder, f"n{e.name}_left.jpg")
            camera.rotation_euler = (math.pi/2, 0, math.pi/2)
            bpy.ops.render.render(write_still=True)  
            
            scene.render.filepath = os.path.join(folder, f"n{e.name}_bottom.jpg")
            camera.rotation_euler = (0, 0, 0)
            bpy.ops.render.render(write_still=True)     
            
            scene.render.filepath = os.path.join(folder, f"n{e.name}_top.jpg")
            camera.rotation_euler = (math.pi, 0, 0)
            bpy.ops.render.render(write_still=True)    
            
            # write hotspot.png
            scene.render.resolution_x = 360
            scene.render.resolution_y = 180
            scene.render.image_settings.file_format = "PNG"
            
            scene.render.filepath = f"//{scene.project_name}.pipmak/{e.name}/hotspots.png"
            bpy.ops.render.render(write_still=True)    
            
            # write nodes lua file
            lua_text = f""" 
            --This tells Pipmak what images to use to form the cubic panorama node. The
            --panorama is made up of six JPEG images, front, right, back, left, top, and
            --bottom. These are projected onto a virtual cube, and the players eyes are 
            --placed at the center.  
            cubic {{ "n{e.name}_front.jpg", "n{e.name}_right.jpg", "n{e.name}_back.jpg", "n{e.name}_left.jpg", "n{e.name}_top.jpg", "n{e.name}_bottom.jpg" }}

            --This tells Pipmak what file to use to define the "hotspots" of the node-
            --regions within the panorama that allow an action to take place when the 
            --player clicks on it. This is an color indexed PNG(Portable Network Graphics)
            --image.
            hotspotmap "hotspots.png"

            --The hotspots are arranged in descending order, according to their order in
            --the palatte the indexed PNG uses.  

            --In this case, there is only one. 
            --This tells the engine that when the hotspot is clicked, the player should 
            --be transported to node "2", and that when over the hopspot, the cursor should
            --change to the "pipmak.hand_forward" cursor. 
            hotspot {{ target = 2, cursor = pipmak.hand_forward }}
            """
            
            filepath = os.path.join(folder, "node.lua")
            
            with open(filepath, "w") as f:
                f.write(lua_text)               
                
        # write main.lua
        
        folder = f"//{scene.project_name}.pipmak/"
        folder = bpy.path.abspath(folder)
        
        lua_text = f"""
        --This line is a comment.
        --The version of the software.
        version (0.27)
        --The title of the software.
        title "{scene.project_name}"
        --The starting node of the software, in this case the menu.
        startnode (1)
        --A function. This function tells Pipmak, on starting a new game, about 
        --the state of several "variables", or "states".
        --This example tells Pipmak that the trapdoor is NOT open, e.g. FALSE.
        onopenproject (
            function()
                state.trapDoorOpen = false
            end
        )
        """     

        filepath = os.path.join(folder, "main.lua")   
        
        with open(filepath, "w") as f:
            f.write(lua_text)                       

        return {'FINISHED'}
    
    
class BTOPIP_PT_panel(bpy.types.Panel):
    bl_label = "BTOPIP"
    bl_idname = "BTOPIP_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "BTOPIP"
    
    def draw(self, context):
        layout = self.layout
        layout.prop(scene, "project_name")
        layout.operator("btopip.renderbtn")


## CLASS LIST ##

classes = (
    BTOPIP_OT_renderbtn,
    BTOPIP_PT_panel
)    


## REGISTER, UNREGISTER ##
        
def register():    
    for c in classes:
        bpy.utils.register_class(c)
    
def unregister():    
    for c in reversed(classes):
        bpy.utils.unregister_class(c)
                    
if __name__ == "__main__":
    register()                    