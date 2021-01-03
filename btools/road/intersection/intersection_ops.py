import bpy

from btools.road.intersection.intersection import Intersection
from btools.road.intersection.intersection_props import IntersectionProperty


class BTOOLS_OT_create_intersection(bpy.types.Operator):
    """Setup decal
    """

    bl_idname = "btools.create_intersection"
    bl_label = "Create Intersection"
    bl_options = {"REGISTER", "UNDO", "PRESET"}

    props: bpy.props.PointerProperty(type=IntersectionProperty)

    @classmethod
    def poll(cls, context):
        return context.mode == "EDIT_MESH" and context.selected_objects and len(context.selected_objects) == 1 and context.object.type == "MESH"

    def execute(self, context):
        Intersection.build(context, self.props)
        return {"FINISHED"}

    def draw(self, context):
        self.props.draw(context, self.layout)
