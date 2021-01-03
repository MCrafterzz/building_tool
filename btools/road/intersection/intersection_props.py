import bpy

from bpy.props import (
    FloatProperty
)


class IntersectionProperty(bpy.types.PropertyGroup):
    vertex_distance: FloatProperty(
        name="Vertex Distance",
        min=0.1,
        max=2,
        default=0.5,
        unit="LENGTH",
        description="Distance between vertices",
    )

    def draw(self, context, layout):
        box = layout.box()
        col = box.column(align=True)
        col.prop(self, "vertex_distance", text="Vertex Distance")
