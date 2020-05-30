# GPL # "author": "Eric Svärd, ulmerkott, (https://www.github.com/ulmerkott)"

bl_info = {
    "name": "Hexaflexagon",
    "author": "Eric Svärd",
    "version": (0, 3),
    "blender": (2, 80, 0),
    "location": "View3D > Add > Mesh > New Object",
    "description": "Adds a new Hexaflexagon Mesh Object",
    "warning": "",
    "doc_url": "https://github.com/ulmerkott/hexaflexagon",
    "category": "Add Mesh",
}

import bpy
from bpy.types import Operator
from bpy.props import FloatProperty, EnumProperty
from bpy_extras.object_utils import AddObjectHelper, object_data_add
from mathutils import Vector


def add_hexaflexagon(self, context):
    mesh = create_hexaflexagon_mesh(self.scale, int(self.sides))
    object= object_data_add(context, mesh, operator=self)
    create_side_materials(object, int(self.sides))
    generate_uv_map(object)


# Generate a list of distinct colors. Maximum count is 6.
def generate_colors(count):
    max_colors = 6
    if count > max_colors:
        raise(ValueError(f"Maximum number of colors are {max_colors}"))

    colors = []
    for index in range(count):
        # Generate a list of base colors from binary numbers where each color
        # takes the form of [r, g, b, 0]
        color = list(map(int, format(index + 1, "#05b")[2:])) + [0]
        colors.append(color)

    return colors


def create_side_materials(object, sides):
    # Define face order. Order depends on how the flexagon gets folded.
    # Order is per face index in the mesh.

    # Trihexaflexagon face order.
    #  +---+---+---+---+---+
    #   \2/1\1/3\3/2\2/1\1/
    #    +---+---+---+---+
    #   /3\3/2\2/1\1/3\3/2\
    #  +---+---+---+---+---+
    trihexa_order = [2,3,3,1,1,2,2,3,3,1,1,2,2,3,3,1,1,2]

    # Hexahexaflexagon face order.
    #  +---+---+---+---+---+---+---+---+---+
    #   \2/3\1/2\3/1\2/3\1/2\3/1\2/3\1/2\3/1\
    #    +---+---+---+---+---+---+---+---+---+
    #   /4\4/5\5/6\6/4\4/5\5/6\6/4\4/5\5/6\6/
    #  +---+---+---+---+---+---+---+---+---+
    hexahexa_order = [2,4,4,3,1,5,5,2,3,6,6,1,2,4,4,3,1,5,
                      5,2,3,6,6,1,2,4,4,3,1,5,5,2,3,6,6,1]

    side_colors = generate_colors(sides)

    # Add new material for each side and apply a distinct diffuse color
    for side in range(1, sides + 1):
        mat = bpy.data.materials.new(name = f"Side_{side}")
        mat.diffuse_color = side_colors[side - 1]
        object.data.materials.append(mat)

    face_order = trihexa_order
    if sides > 3:
        face_order = hexahexa_order

    # Assign faces to corresponding side material
    for index,face in enumerate(face_order):
        vertices = object.data.polygons[index].material_index = face - 1


def create_hexaflexagon_mesh(scale, sides):
    faces = sides * 3
    vert_columns = faces + 2

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
    for column in range(0, vert_columns):
        verts.append([column * (scale / 2), height * upper, 0])

        # Create mirrored backside vertex
        if upper:
            verts.append([column * (scale / 2), -height * upper, 0])

        # Face indices:
        #  +---+---+ ...
        #   \0/3\4/7\
        #    +---+---+..
        #   /1\2/5\6/
        #  +---+---+ ...
        # We can't create faces between first two columns
        if column >= 2:
            s = len(verts)
            # Upper face
            if column % 2 == 0:
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
    uv_layer = obj.data.uv_layers.new(name="HexaflexagonUV")
    bpy.ops.object.select_all(action="DESELECT")

    # Make UV triangles equilateral
    for i,uv_obj in uv_layer.data.items():
        if (i + 1) % 3 == 0:
            uv_obj.uv.x = 0.5
            uv_obj.uv.y = 0.75**0.5 # sqrt(1^2 - (1/2)^2)


class OBJECT_OT_add_hexaflexagon(Operator, AddObjectHelper):
    """Create a new Hexaflexagon mesh object"""
    bl_idname = "mesh.add_hexaflexagon"
    bl_label = "Add Hexaflexagon"
    bl_options = {'REGISTER', 'UNDO',}

    sides: EnumProperty(
        items=(("3", "Trihexaflexagon", "Three sided hexaflexagon"),
               ("6", "Hexahexaflexagon", "Six sided hexaflexagon")),
        name="Type",
        description="This will affect the number of sides."
    )

    scale: FloatProperty(
        name="Scale",
        default=1.0,
        description="scaling"
    )


    def draw(self, context):
        layout = self.layout
        layout.prop(self, "sides")
        layout.prop(self, "scale", expand=True)

        layout.prop(self, 'align', expand=True)
        layout.prop(self, 'location', expand=True)
        layout.prop(self, 'rotation', expand=True)


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
