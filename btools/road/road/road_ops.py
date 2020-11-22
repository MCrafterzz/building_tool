import bpy

from .road import Road
from .road_props import RoadProperty


class BTOOLS_OT_convert_to_road(bpy.types.Operator):
    """Create road
    """

    bl_idname = "btools.convert_to_road"
    bl_label = "Convert To Road"
    bl_options = {"REGISTER", "UNDO", "PRESET"}

    props: bpy.props.PointerProperty(type=RoadProperty)

    @classmethod
    def poll(cls, context):
        return context.mode == "OBJECT" and context.selected_objects and context.object.type == "MESH"

    def execute(self, context):
        Road.build(context, self.props)
        return {"FINISHED"}

    def draw(self, context):
        self.props.draw(context, self.layout)


class BTOOLS_OT_finalize_road(bpy.types.Operator):
    """Apply modifiers, remove curve, set uvs etc
    """

    bl_idname = "btools.finalize_road"
    bl_label = "Finalize Road"
    bl_options = {"REGISTER", "PRESET"}

    @classmethod
    def poll(cls, context):
        obj = context.object
        return context.mode == "OBJECT" and obj and obj.type == "MESH"

    def execute(self, context):
        Road.finalize_road(context)
        return {"FINISHED"}
