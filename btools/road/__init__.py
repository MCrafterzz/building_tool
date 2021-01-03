from .road import register_road, unregister_road
from .array import register_array, unregister_array
from .decal import register_decal, unregister_decal
from .intersection import register_intersection, unregister_intersection

register_funcs = (
    register_road,
    register_array,
    register_decal,
    register_intersection,
)

unregister_funcs = (
    unregister_road,
    unregister_array,
    unregister_decal,
    unregister_intersection,
)


def register_road():
    for func in register_funcs:
        func()


def unregister_road():
    for func in unregister_funcs:
        func()
