import bmesh
import bpy

from btools.utils import crash_safe, bm_from_obj, bm_to_obj


class Decal:
    @classmethod
    @crash_safe
    def build(cls, context, props):
        """ Place decal
        """

        # Add modifiers
        if not context.object.modifiers:
            # Array
            bpy.ops.object.modifier_add(type="SUBSURF")
            modifier = context.object.modifiers["Subdivision"]
            modifier.subdivision_type = "SIMPLE"
            modifier.levels = props.subdivision_level

            # Shrinkwrap
            bpy.ops.object.modifier_add(type="SHRINKWRAP")
            modifier = context.object.modifiers["Shrinkwrap"]
            modifier.target = context.scene.btools_ground_object
            modifier.offset = props.ground_offset
            modifier.use_negative_direction = True
            modifier.wrap_method = "PROJECT"
            modifier.project_limit = 1000

            # Apply modifiers
            bpy.ops.object.modifier_apply(modifier="Subdivision")
            bpy.ops.object.modifier_apply(modifier="Shrinkwrap")

            # Limited dissolve
            obj = context.object
            bm = bm_from_obj(obj)
            bmesh.ops.dissolve_limit(bm, angle_limit=props.max_angle, verts=bm.verts, edges=bm.edges)
            bm_to_obj(bm, obj)
