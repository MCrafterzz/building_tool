import bpy

from bpy.props import (
    FloatProperty, IntProperty
)


class DecalProperty(bpy.types.PropertyGroup):
    subdivision_level: IntProperty(
        name="Subdivision Level",
        min=1,
        max=5,
        default=3,
        description="Level of subdivision",
    )

    ground_offset: FloatProperty(
        name="Length",
        min=0.01,
        max=1,
        default=0.02,
        unit="LENGTH",
        description="Offset above the ground object",
    )

    max_angle: FloatProperty(
        name="Max Angle",
        min=0.001,
        max=15,
        default=0.0087,
        unit="ROTATION",
        description="Maximum angle to dissolve decal",
    )

    def draw(self, context, layout):
        box = layout.box()
        col = box.column(align=True)
        col.prop(self, "subdivision_level", text="Subdivision Level")
        col.prop(self, "ground_offset", text="Ground Offset")
        col.prop(self, "max_angle", text="Max Angle")
