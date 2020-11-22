import bpy
from bpy.props import PointerProperty

from .decal import BTOOLS_OT_convert_to_decal
from .decal_props import DecalProperty

classes = (DecalProperty, BTOOLS_OT_convert_to_decal,)

def register_decal():
    bpy.types.Scene.btools_ground_object = PointerProperty(
        type=bpy.types.Object, description="Object to place decal on")

    for cls in classes:
        bpy.utils.register_class(cls)


def unregister_decal():
    del bpy.types.Scene.btools_ground_object

    for cls in classes:
        bpy.utils.unregister_class(cls)
