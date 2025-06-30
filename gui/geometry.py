#!/usr/bin/env python
"""Module for 3D geometry manipulation.

Malsimulation: Malleable World Simulator
@author: Paweł Sobkowiak
@contact: pawel.sobkowiak@gmail.com
Copyright © 2011 Paweł Sobkowiak

"""


from math import sqrt


from pyglet.gl import GLfloat, GLdouble

from mallib.meta import mark

UPWARD_VECTOR = (0.0, 0.0, 1.0)

Vector3f = GLfloat * 3
Vector4f = GLfloat * 4

FORWARD = (0, 0, -1)
BACKWARD = (0, 0, 1)
UPWARD = (0, 1, 0)
DOWNWARD = (0, -1, 0)
LEFTWARD = (-1, 0, 0)
RIGHTWARD = (1, 0, 0)

CUBE = (
    # FRONT
    0,
    0,
    0,
    1,
    0,
    0,
    1,
    1,
    0,
    1,
    1,
    0,
    0,
    1,
    0,
    0,
    0,
    0,
    # BACK
    0,
    0,
    1,
    0,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    0,
    1,
    0,
    0,
    1,
    # TOP
    0,
    1,
    0,
    1,
    1,
    0,
    1,
    1,
    1,
    1,
    1,
    1,
    0,
    1,
    1,
    0,
    1,
    0,
    # BOTTOM
    0,
    0,
    0,
    0,
    0,
    1,
    1,
    0,
    1,
    1,
    0,
    1,
    1,
    0,
    0,
    0,
    0,
    0,
    # LEFT
    0,
    0,
    0,
    0,
    1,
    0,
    0,
    1,
    1,
    0,
    1,
    1,
    0,
    0,
    1,
    0,
    0,
    0,
    # RIGHT
    1,
    0,
    0,
    1,
    0,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    1,
    0,
    1,
    0,
    0,
)

CUBE_NORMALS = FORWARD * 6 + BACKWARD * 6 + UPWARD * 6 + DOWNWARD * 6 + LEFTWARD * 6 + RIGHTWARD * 6


def sum_vectors(*args):
    return tuple(sum(column) for column in zip(*args))


def add_v4(v1, v2):
    return Vector4f(v1[0] + v2[0], v1[1] + v2[1], v1[2] + v2[2], v1[3] + v2[3])


def mul_v4_scal(v, s):
    return Vector4f(v[0] * s, v[1] * s, v[2] * s, v[3] * s)


def cross_product(bx, by, bz, cx, cy, cz):
    return by * cz - bz * cy, bz * cx - bx * cz, bx * cy - by * cx


def normal(p1, p2, p3):  # three points as arguments
    return cross_product(
        p1[0] - p2[0],
        p1[1] - p2[1],
        p1[2] - p2[2],
        p2[0] - p3[0],
        p2[1] - p3[1],
        p2[2] - p3[2],
    )


def normal_from_two_points(p1, p2):
    """
    first create a vector perpendicular to flat projection of p1p2
    (x, y) _|_ (-y, x)
    """
    x1, y1, z1 = p1
    x2, y2, z2 = p2
    # x3 = y2 - y1
    # y3 = x1 - x2
    # z3 = z1 (flat projection)
    return cross_product(
        x1 - x2,
        y1 - y2,
        z1 - z2,
        x2 + y1 - y2,  # x2 - x3
        y2 - x1 + x2,  # y2 - y3
        z2 - z1,
    )


@mark('refactor')
def inverse_if_downward(v):
    if v[2] < 0:
        return (-v[0], -v[1], -v[2])
    else:
        return v


def vector_length(v):
    x, y, z = v
    return sqrt(x * x + y * y + z * z)


def normalize(v):
    length = vector_length(v)
    return v[0] / length, v[1] / length, v[2] / length


def normalized_normal(v1, v2, v3):  # three points as arguments
    return normalize(normal(v1, v2, v3))


ORDER_FOR_TRIANGLE_CASTING = {0: [1, 2], 1: [2, 0], 2: [0, 1]}


def cast_triangle(points, limit, cast_down=True):
    """
    This is extended version of triangle trimming - use it if trimming needed
    """
    limit = float(limit)
    if cast_down:
        condition = [point[2] > limit for point in points]
    else:
        condition = [point[2] <= limit for point in points]
    s = sum(condition)
    if s == 3:
        return [(p[0], p[1], limit) for p in points]
    elif s == 2:
        new_points = []
        bad_vertex = condition.index(0)
        order = ORDER_FOR_TRIANGLE_CASTING[bad_vertex]
        for i in order:
            mul = (points[bad_vertex][2] - limit) / (points[bad_vertex][2] - points[i][2]) - 0.001
            new_x = points[bad_vertex][0] * (1.0 - mul) + points[i][0] * (mul)
            new_y = points[bad_vertex][1] * (1.0 - mul) + points[i][1] * (mul)
            new_points.append((new_x, new_y))
        return [
            (p[0], p[1], limit)
            for p in [
                points[order[0]],
                points[order[1]],
                new_points[0],
                points[order[1]],
                new_points[1],
                new_points[0],
            ]
        ]
    elif s == 1:
        new_points = []
        good_vertex = condition.index(True)
        new_points.append(points[good_vertex])
        order = ORDER_FOR_TRIANGLE_CASTING[good_vertex]
        for i in order:
            mul = (points[good_vertex][2] - limit) / (points[good_vertex][2] - points[i][2]) + 0.001
            new_x = points[good_vertex][0] * (1.0 - mul) + points[i][0] * (mul)
            new_y = points[good_vertex][1] * (1.0 - mul) + points[i][1] * (mul)
            new_points.append((new_x, new_y))
        return [(p[0], p[1], limit) for p in new_points]
    else:
        return []


def flat_clip_plane(rep_alt):
    return (GLdouble * 4)(0, 0, -1, rep_alt)
