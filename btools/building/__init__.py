from ._register import register_generic, unregister_generic

from .balcony import register_balcony, unregister_balcony
from .door import register_door, unregister_door
from .fill import register_fill, unregister_fill
from .floor import register_floor, unregister_floor
from .floorplan import register_floorplan, unregister_floorplan
from .multigroup import register_multigroup, unregister_multigroup
from .railing import register_railing, unregister_railing
from .roof import register_roof, unregister_roof
from .stairs import register_stairs, unregister_stairs
from .window import register_window, unregister_window

# -- ORDER MATTERS --
register_funcs = (
    register_generic,
    register_railing,
    register_balcony,
    register_fill,
    register_door,
    register_floor,
    register_window,
    register_floorplan,
    register_stairs,
    register_roof,
    register_multigroup,
)

unregister_funcs = (
    unregister_generic,
    unregister_railing,
    unregister_balcony,
    unregister_fill,
    unregister_door,
    unregister_floor,
    unregister_window,
    unregister_floorplan,
    unregister_stairs,
    unregister_roof,
    unregister_multigroup,
)


def register_building():
    for func in register_funcs:
        func()


def unregister_building():
    for func in unregister_funcs:
        func()
