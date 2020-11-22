import bpy
from bpy.props import PointerProperty


class BTOOLS_OT_convert_to_decal(bpy.types.Operator):
    """Setup array
    """

    bl_idname = "btools.convert_to_decal"
    bl_label = "Convert To Decal"
    bl_options = {"REGISTER", "UNDO", "PRESET"}

    @classmethod
    def poll(cls, context):
        context.mode == "OBJECT" and context.selected_objects and context.object.type == "MESH"

    def execute(self, context):
        #Array.build(context)
        return {"FINISHED"}


classes = (BTOOLS_OT_convert_to_decal,)


def register_decal():
    bpy.types.Scene.btools_ground_object = PointerProperty(
        type=bpy.types.Object, description="Object to place decal on")

    for cls in classes:
        bpy.utils.register_class(cls)


def unregister_decal():
    del bpy.types.Scene.btools_ground_object

    for cls in classes:
        bpy.utils.unregister_class(cls)
