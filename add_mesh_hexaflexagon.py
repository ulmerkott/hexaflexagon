# GPL # "author": "Eric Svärd, ulmerkott, (https://www.github.com/ulmerkott)"

bl_info = {
    "name": "Hexaflexagon",
    "author": "Eric Svärd",
    "version": (0, 2),
    "blender": (2, 80, 0),
    "location": "View3D > Add > Mesh > New Object",
    "description": "Adds a new Hexaflexagon Mesh Object",
    "warning": "",
    "doc_url": "https://github.com/ulmerkott/hexaflexagon",
    "category": "Add Mesh",
}

import bpy
from bpy.types import Operator
from bpy.props import FloatProperty, IntProperty
from bpy_extras.object_utils import AddObjectHelper, object_data_add
from mathutils import Vector


def add_hexaflexagon(self, context):

    # Add one extra face for glueing with the first face
    faces = self.sides * 3 + 1
    verts_count = faces + 2

    verts = []
    faces = []
    edges = []

    # Calculate height with help from old friend Pythagoras
    height = (self.scale**2 - (self.scale / 2.0)**2)**0.5

    # Start with the lower left triangle vertex.
    # upper ->   2---4---*
    #           / \ / \ /
    # lower -> 1---3---5
    upper = False
    for v in range(0, verts_count):
        verts.append(Vector((v * (self.scale / 2), height * upper, 0)))

        # Need atleast 3 vertices for one face
        if v >= 2:
            faces.append([v-2, v-1, v])

        # Switch between upper/lower for each iteration
        upper = not upper 

    mesh = bpy.data.meshes.new(name="Hexaflexagon")
    mesh.from_pydata(verts, edges, faces)

    # Useful for development when the mesh may be invalid.
    mesh.validate(verbose=True)

    object_data_add(context, mesh, operator=self)
 

class OBJECT_OT_add_hexaflexagon(Operator, AddObjectHelper):
    """Create a new Hexaflexagon mesh object"""
    bl_idname = "mesh.add_hexaflexagon"
    bl_label = "Add Hexaflexagon"
    bl_options = {'REGISTER', 'UNDO',}

    scale: FloatProperty(
        name="Scale",
        default=1.0,
        description="scaling"
    )

    sides: IntProperty(
        name="Sides",
        description="Number of sides in the Hexaflexagon",
        min=3,
        default=3
    )

    def execute(self, context):
        add_hexaflexagon(self, context)
        return {'FINISHED'}


# Registration
def add_hexaflexagon_button(self, context):
    self.layout.operator(
        OBJECT_OT_add_hexaflexagon.bl_idname,
        text="Hexaflexagon",
        icon='PLUGIN')


# This allows you to right click on a button and link to documentation
def add_hexaflexagon_manual_map():
    url_manual_prefix = "https://docs.blender.org/manual/en/latest/"
    url_manual_mapping = (
        ("bpy.ops.mesh.add_hexaflexagon", "scene_layout/object/types.html"),
    )
    return url_manual_prefix, url_manual_mapping


def register():
    bpy.utils.register_class(OBJECT_OT_add_hexaflexagon)
    bpy.utils.register_manual_map(add_hexaflexagon_manual_map)
    bpy.types.VIEW3D_MT_mesh_add.append(add_hexaflexagon_button)


def unregister():
    bpy.utils.unregister_class(OBJECT_OT_add_hexaflexagon)
    bpy.utils.unregister_manual_map(add_hexaflexagon_manual_map)
    bpy.types.VIEW3D_MT_mesh_add.remove(add_hexaflexagon_button)


if __name__ == "__main__":
    register()
