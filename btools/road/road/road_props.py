import bpy

from bpy.props import (
    FloatProperty, BoolProperty, EnumProperty
)


class RoadProperty(bpy.types.PropertyGroup):
    extrusion_types = [
        ("STRAIGHT", "Straight", "", 0),
        ("CURVE", "Curve", "", 1),
    ]

    extrusion_type: EnumProperty(
        items=extrusion_types, default="STRAIGHT", description="Extrusion mode"
    )

    interval: FloatProperty(
        name="Interval",
        min=0.1,
        default=0.5,
        unit="LENGTH",
        description="Interval of vertices",
    )

    length: FloatProperty(
        name="Length",
        min=0.01,
        default=10,
        unit="LENGTH",
        description="Length of road",
    )

    def draw(self, context, layout):
        # Extrusion
        box = layout.box()
        box.label(text="Extrusion")
        col = box.column(align=True)
        col.prop(self, "extrusion_type", text="Extrusion Mode")
        col.prop(self, "interval", text="Interval")

        if self.extrusion_type == "STRAIGHT":
            col.prop(self, "length", text="Length")