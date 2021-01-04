import sys

import bmesh
from bmesh.ops import create_vert, contextual_create
from mathutils import Vector
from mathutils.geometry import intersect_line_line_2d, interpolate_bezier

from btools.utils import crash_safe, get_edit_mesh, BMEdge


class Intersection:
    lerp_point = None

    @classmethod
    @crash_safe
    def build(cls, context, props):
        """ Create intersection
        """

        # Get selected edges
        me = get_edit_mesh()
        bm = bmesh.from_edit_mesh(me)
        bm.select_history.validate()
        edges = [elem for elem in bm.select_history if isinstance(elem, BMEdge)]

        if len(edges) < 4:
            return {"CANCELLED"}

        # Generate start points for every connection to allow for calculating center connection points
        last_edge = edges[-1]
        start_points = list()
        end_points = list()
        center_point = cls.get_center_point(edges)

        start_points, end_points = cls.calculate_start_end_points(edges, last_edge, center_point, start_points, end_points)

        last_edge = edges[0]

        for i in range(1, len(edges), 2):
            edge = edges[i]
            first_vert = edge.verts[0].co
            second_vert = edge.verts[1].co
            direction = (second_vert - first_vert).xy.normalized()
            last_first_vert = last_edge.verts[0].co
            last_second_vert = last_edge.verts[1].co
            last_direction = (last_second_vert - last_first_vert).xy.normalized()
            distance = (first_vert - last_first_vert).xy.length * 4

            # Use the points that are nearest to the center
            start_vert = second_vert
            start_tangent = first_vert.xy + direction * distance
            end_vert = last_second_vert
            end_tangent = last_first_vert.xy + last_direction * distance

            if (second_vert - center_point).xy.length > (first_vert - center_point).xy.length:
                start_vert = first_vert
                start_tangent = second_vert.xy - direction * distance

            if (last_second_vert - center_point).xy.length > (last_first_vert - center_point).xy.length:
                end_vert = last_first_vert
                end_tangent = last_second_vert.xy - last_direction * distance

            cls.find_intersection(start_vert, start_tangent, end_vert, end_tangent)
            accurate_distance = (start_vert - center_point).length + (end_vert - center_point).length

            if cls.lerp_point is None:
                # Center point is better than nothing
                cls.lerp_point = (first_vert + second_vert + last_first_vert + last_second_vert) / 4

            cls.add_inner_outer_vertices(start_vert, end_vert, accurate_distance, props, start_points, end_points, i,
                                     bm, center_point)

            # Change variables for next iteration
            cls.distance = sys.float_info.max
            cls.lerp_point = None
            last_edge = edges[(i + 1) % len(edges)]

        bmesh.update_edit_mesh(me, True)
        return {"FINISHED"}

    @classmethod
    @crash_safe
    def add_inner_outer_vertices(cls, start_vert, end_vert, accurate_distance, props, start_points, end_points, i, bm, center_point):
        # Loop to generate vertices
        start_tangent = (start_vert.xy + 2 * cls.lerp_point).xy / 3
        end_tangent = (end_vert.xy + 2 * cls.lerp_point).xy / 3

        # Generate xy points by interpolating the generated curve
        positions_xy = interpolate_bezier(start_vert.xy, start_tangent,
                                          end_tangent, end_vert.xy,
                                          max(4, int(accurate_distance / props.vertex_distance)))
        time_step = 1.0 / (len(positions_xy) - 1)

        start_center_point = (start_vert.xy + start_points[int(i / 2 + 1) % len(start_points)]) / 2
        end_center_point = (end_vert.xy + end_points[int(i / 2) % len(end_points)]) / 2

        t = 0
        j = 0
        center_added = False
        last_outer_vert = None
        last_inner_vert = None

        while j < len(positions_xy):
            real_t = min(1, t)
            # Get the z position between the start and end z
            position_z = start_vert.z + (end_vert.z - start_vert.z) * real_t

            # Outer vertex
            outer_vert = create_vert(bm, co=(positions_xy[j].x, positions_xy[j].y, position_z))

            # Inner vertex
            if real_t < 0.5:
                position = start_center_point.lerp(center_point, real_t * 2)
                position_z = start_vert.z + (center_point.z - start_vert.z) * real_t * 2
                inner_vert = create_vert(bm, co=(position.x, position.y, position_z))
            else:
                if not center_added:
                    # Point has naturally generated in the center
                    if real_t * 2 == 0.5 or real_t * 2 - time_step == 0.5:
                        center_added = True
                    else:
                        # Move current point to center
                        inner_vert = create_vert(bm, co=center_point)
                        center_added = True
                else:
                    position = center_point.xy.lerp(end_center_point, (real_t - 0.5) * 2)
                    position_z = center_point.z + (end_vert.z - center_point.z) * (real_t - 0.5) * 2
                    inner_vert = create_vert(bm, co=(position.x, position.y, position_z))

            # Add faces
            if last_inner_vert is not None and not last_inner_vert == inner_vert and not last_outer_vert == outer_vert:
                contextual_create(bm, geom=[last_outer_vert["vert"][0], last_inner_vert["vert"][0],
                                            outer_vert["vert"][0], inner_vert["vert"][0]])

            last_outer_vert = outer_vert
            last_inner_vert = inner_vert

            j += 1
            t += time_step

    @classmethod
    @crash_safe
    def calculate_start_end_points(cls, edges, last_edge, center_point, start_points, end_points):
        for i in range(0, len(edges), 2):
            first_vert = edges[i].verts[0].co
            second_vert = edges[i].verts[1].co
            last_first_vert = last_edge.verts[0].co
            last_second_vert = last_edge.verts[1].co

            # Use the points that are nearest to the center
            start_vert = first_vert
            end_vert = last_first_vert

            if (second_vert - center_point).xy.length < (first_vert - center_point).xy.length:
                start_vert = second_vert

            if (last_second_vert - center_point).xy.length < (last_first_vert - center_point).xy.length:
                end_vert = last_second_vert

            # Save variables for later use
            start_points.append(start_vert.xy)
            end_points.append(end_vert.xy)

            # Change variable for next iteration
            last_edge = edges[(i + 1) % len(edges)]

        return start_points, end_points

    @classmethod
    @crash_safe
    def get_center_point(cls, edges):
        center = Vector((0.0, 0.0, 0.0))

        for edge in edges:
            center += edge.verts[0].co
            center += edge.verts[1].co

        center /= (2 * len(edges))
        return center

    @classmethod
    @crash_safe
    def find_intersection(cls, first_point, second_point, third_point, forth_point):
        # 3D to 2D
        first_point = first_point.xy
        second_point = second_point.xy
        third_point = third_point.xy
        forth_point = forth_point.xy

        intersection = intersect_line_line_2d(first_point, second_point, third_point, forth_point)

        # No intersection found
        if intersection is None:
            return

        # Store data
        cls.lerp_point = intersection

    @classmethod
    @crash_safe
    def connect_sidewalks(cls, context, props):
        # Get selected edges
        me = get_edit_mesh()
        bm = bmesh.from_edit_mesh(me)
        bm.select_history.validate()
        edges = [elem for elem in bm.select_history if isinstance(elem, BMEdge)]

        if not len(edges) == 4:
            return {"CANCELLED"}

        center_point = cls.get_center_point(edges)
        last_edge = edges[0]
        last_vertices = list()

        for i in range(1, len(edges), 2):
            edge = edges[i]
            first_vert = edge.verts[0].co
            second_vert = edge.verts[1].co
            direction = (second_vert - first_vert).xy.normalized()
            last_first_vert = last_edge.verts[0].co
            last_second_vert = last_edge.verts[1].co
            last_direction = (last_second_vert - last_first_vert).xy.normalized()
            distance = (first_vert - last_first_vert).xy.length * 4

            # Use the points that are nearest to the center
            start_vert = second_vert
            start_tangent = first_vert.xy + direction * distance
            end_vert = last_second_vert
            end_tangent = last_first_vert.xy + last_direction * distance

            if (second_vert - center_point).xy.length > (first_vert - center_point).xy.length:
                start_vert = first_vert
                start_tangent = second_vert.xy - direction * distance

            if (last_second_vert - center_point).xy.length > (last_first_vert - center_point).xy.length:
                end_vert = last_first_vert
                end_tangent = last_second_vert.xy - last_direction * distance

            cls.find_intersection(start_vert, start_tangent, end_vert, end_tangent)

            if i == 1:
                accurate_distance = (start_vert - center_point).length + (end_vert - center_point).length

            if cls.lerp_point is None:
                # Center point is better than nothing
                cls.lerp_point = (first_vert + second_vert + last_first_vert + last_second_vert) / 4

            # Loop to generate vertices
            start_tangent = (start_vert.xy + 2 * cls.lerp_point).xy / 3
            end_tangent = (end_vert.xy + 2 * cls.lerp_point).xy / 3

            # Generate xy points by interpolating the generated curve
            positions_xy = interpolate_bezier(start_vert.xy, start_tangent,
                                              end_tangent, end_vert.xy,
                                              max(4, int(accurate_distance / props.vertex_distance)))

            last_vert = None

            # Add vertices
            for j in range(len(positions_xy)):
                xy = positions_xy[j]
                z = start_vert.z + (end_vert.z - start_vert.z) * (float(j) / (len(positions_xy) - 1))
                vert = create_vert(bm, co=(xy.x, xy.y, z))

                # Add faces
                if last_vertices and i > 1:
                    if last_vert:
                        contextual_create(bm, geom=[last_vert["vert"][0], vert["vert"][0],
                                                    last_vertices[len(last_vertices) - j]["vert"][0],
                                                    last_vertices[len(last_vertices) - j - 1]["vert"][0]])
                else:
                    last_vertices.append(vert)

                last_vert = vert

            # Change variables for next iteration
            cls.distance = sys.float_info.max
            cls.lerp_point = None
            last_edge = edges[(i + 1) % len(edges)]

        bmesh.update_edit_mesh(me, True)
        return {"FINISHED"}
