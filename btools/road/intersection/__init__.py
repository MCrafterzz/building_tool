import bpy

from .intersection_ops import BTOOLS_OT_create_intersection, BTOOLS_OT_connect_sidewalks
from .intersection_props import IntersectionProperty

classes = (IntersectionProperty, BTOOLS_OT_create_intersection, BTOOLS_OT_connect_sidewalks)

def register_intersection():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister_intersection():
    for cls in classes:
        bpy.utils.unregister_class(cls)
