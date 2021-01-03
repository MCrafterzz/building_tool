import bpy

from .decal_props import DecalProperty
from .decal import Decal


class BTOOLS_OT_convert_to_decal(bpy.types.Operator):
    """Setup decal
    """

    bl_idname = "btools.convert_to_decal"
    bl_label = "Convert To Decal"
    bl_options = {"REGISTER", "UNDO", "PRESET"}

    props: bpy.props.PointerProperty(type=DecalProperty)

    @classmethod
    def poll(cls, context):
        return context.mode == "OBJECT" and context.selected_objects and context.object.type == "MESH" and not context.scene.btools_ground_object == None

    def execute(self, context):
        Decal.build(context, self.props)
        return {"FINISHED"}

    def draw(self, context):
        self.props.draw(context, self.layout)
