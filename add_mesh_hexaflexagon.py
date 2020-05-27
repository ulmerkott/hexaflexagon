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
    mesh = create_hexaflexagon_mesh(self.scale, self.sides)
    object= object_data_add(context, mesh, operator=self)
    generate_uv_map(object)

def create_hexaflexagon_mesh(scale, sides):
    # Add one extra face for glueing with the first face
    faces = sides * 3 + 1
    vert_cols = faces + 2

    verts = []
    verts_backside = []
    faces = []
    faces_backside = []

    # Calculate height with help from old friend Pythagoras
    height = (scale**2 - (scale / 2.0)**2)**0.5

    # Start with the upper left triangle vertex.
    # col      -> 0 1 2 3 4 5
    # upper    -> 0---3---6 ...
    #              \ / \ / \ /
    # lower    ->   2---5---8
    # backside ->  / \ / \ / \
    #             1---4---7 ...
    upper = True
    for col in range(0, vert_cols):
        verts.append(Vector((col * (scale / 2), height * upper, 0)))

        # Create mirrored backside vertex
        if upper:
            verts.append(Vector((col * (scale / 2), -height * upper, 0)))

        # We can't create faces between first two columns
        if col >= 2:
            s = len(verts)
            # Upper face
            if col%2 == 0:
                faces.append([s-5, s-3, s-2])
            else:
                faces.append([s-4, s-2, s-1])
            # Back side face
            faces.append([s-4, s-3, s-1])

        # Switch between upper/lower for each iteration
        upper = not upper 

    mesh = bpy.data.meshes.new(name="Hexaflexagon")
    mesh.from_pydata(verts, [], faces)

    # Useful for development when the mesh may be invalid.
    mesh.validate(verbose=True)
    return mesh


def generate_uv_map(obj):
    # TODO: Generate a usable UV map
    obj.data.uv_layers.new(name="HexaflexagonUV")
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.object.editmode_toggle()
    obj.select_set(False)


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
