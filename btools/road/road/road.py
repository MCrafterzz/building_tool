import math

import bmesh
import bpy
from mathutils import Matrix

from ...utils import (
    bm_to_obj,
    crash_safe,
    bm_from_obj,
    filter_geom
)


class Road:
    @classmethod
    @crash_safe
    def build(cls, context, prop):
        """ Extrude object
        """
        obj = context.object
        bm = bm_from_obj(obj)

        # Create curve
        curve = cls.create_curve(context)

        # Extrude road
        cls.extrude_road(context, prop, bm)

        bm_to_obj(bm, obj)

        return obj

    @classmethod
    def create_curve(cls, context):
        # Create curve
        name = "curve_" + str("{:0>3}".format(len(bpy.data.objects) + 1))
        curve_data = bpy.data.curves.new(name=name, type='CURVE')
        curve_data.dimensions = '3D'
        curve_data.resolution_u = 500
        spline = curve_data.splines.new(type='BEZIER')

        # Add point
        spline.bezier_points.add(1)
        spline.bezier_points[1].co = (0, 10, 0)
        spline.bezier_points[0].handle_left_type = spline.bezier_points[0].handle_right_type = "AUTO"
        spline.bezier_points[1].handle_left_type = spline.bezier_points[1].handle_right_type = "AUTO"

        # Add to scene
        curve_obj = bpy.data.objects.new(name=name, object_data=curve_data)
        curve_obj.parent = context.object
        context.collection.objects.link(curve_obj)

        return curve_obj

    @classmethod
    @crash_safe
    def extrude_road(cls, context, prop, bm):
        # Extrude once
        geom = bmesh.ops.extrude_face_region(bm, geom=bm.edges)
        verts = filter_geom(geom["geom"], bmesh.types.BMVert)

        bmesh.ops.transform(bm, matrix=Matrix.Translation((0, prop.interval, 0)),
                            verts=verts)

        # Continue to extrude
        if prop.extrusion_type == "STRAIGHT":
            cls.extrude_straight(context, prop, bm)
        else:
            cls.extrude_curved(context, prop, bm)

        return {"FINISHED"}

    @classmethod
    @crash_safe
    def extrude_straight(cls, context, prop, bm):
        # Add modifiers
        if not context.object.modifiers:
            # Array
            bpy.ops.object.modifier_add(type="ARRAY")
            modifier = context.object.modifiers["Array"]
            modifier.show_in_editmode = True
            modifier.show_on_cage = True
            modifier.fit_type = "FIT_LENGTH"
            modifier.fit_length = prop.length
            modifier.use_merge_vertices = True
            modifier.relative_offset_displace = [0, 1, 0]

        return {"FINISHED"}

    @classmethod
    @crash_safe
    def extrude_curved(cls, context, prop, bm):
        curve = context.object.children[0]
        curve.data.bevel_object = context.object

        # Rotate vertices
        bmesh.ops.rotate(bm, matrix=Matrix.Rotation(math.radians(90.0), 3, 'Y'), verts=bm.verts)

        # Add modifiers
        if not context.object.modifiers:
            # Array
            bpy.ops.object.modifier_add(type="ARRAY")
            modifier = context.object.modifiers["Array"]
            modifier.fit_type = "FIT_CURVE"
            modifier.use_merge_vertices = True
            modifier.curve = curve
            modifier.relative_offset_displace = [0, 1, 0]

            # Curve
            bpy.ops.object.modifier_add(type="CURVE")
            modifier = context.object.modifiers["Curve"]
            modifier.object = curve
            modifier.deform_axis = "POS_Y"

        return {"FINISHED"}

    @classmethod
    @crash_safe
    def finalize_road(cls, context):
        if context.active_object is None:
            return {"FINISHED"}

        # Apply modifiers
        bpy.ops.object.modifier_apply(modifier="Array")
        bpy.ops.object.modifier_apply(modifier="Curve")

        # Remove curve
        if len(context.active_object.children) > 0 and context.active_object.children[0].type == "CURVE":
            bpy.data.objects.remove(context.active_object.children[0])

        # Uv calculations
        bm = bm_from_obj(context.active_object)
        count = int(len(context.active_object.to_mesh().vertices) / 2)
        uv_layer = bm.loops.layers.uv.new()
        sections = len(bm.verts) // count
        total_distance = 0

        uv_coords = []

        bm.verts.ensure_lookup_table()
        bm.verts.index_update()
        last_position = (bm.verts[0].co + bm.verts[count].co) / 2  # Calculate center of road
        texture_scale = 0.1

        # Calculate uvs for all vertices
        for i in range(sections):
            current_position = (bm.verts[i * count].co + bm.verts[(i + 1) * count - 1].co) / 2  # Calculate center of road
            total_distance += (last_position - current_position).length

            for j in range(count):
                uv_coords.append((j % 2, total_distance * texture_scale))

            last_position = current_position

        # Set uvs
        for f in bm.faces:
            for l in f.loops:
                if l.vert.index < len(uv_coords):
                    l[uv_layer].uv = uv_coords[l.vert.index]

        bm_to_obj(bm, context.active_object)

        return {"FINISHED"}
