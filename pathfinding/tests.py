#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''Tests.

mallib: common library for mal projects
@author: Paweł Sobkowiak
@contact: pawel.sobkowiak@gmail.com
Copyright © 2011 Paweł Sobkowiak

'''
from __future__ import absolute_import, division, print_function

import unittest

from .constants import NOT_PASSABLE
from .finders import find_path, find_nearest_targets, NoPathFound
from .sample import SampleXYZ, SampleConnection, SampleNode

MOCK_DIRECTIONS = (SampleXYZ(1, 0, 0), SampleXYZ(-1, 0, 0),
                   SampleXYZ(0, 1, 0), SampleXYZ(0, -1, 0))
SIZE_X, SIZE_Y = 10, 10


class MockNode(SampleNode):
    def __init__(self, graph, x, y, passable, tags=None):
        xyz = SampleXYZ(x, y, 0)
        super(MockNode, self).__init__(xyz, tags)
        self.passable = passable
        self.graph = graph

    def generate_connections(self):
        self.connections = []
        for direction in MOCK_DIRECTIONS:
            neighbor_xyz = SampleXYZ(self.x + direction.x,
                                     self.y + direction.y, 0)
            neighbor_field = self.graph.get(neighbor_xyz)
            if neighbor_field:
                cost = 1 if neighbor_field.passable else NOT_PASSABLE
                self.connections.append(SampleConnection(neighbor_field, cost))
        return self.connections

    @property
    def x(self):
        return self.xyz.x

    @property
    def y(self):
        return self.xyz.y


class MockGraph(dict):
    def __init__(self):
        for x in xrange(SIZE_X):
            for y in xrange(SIZE_Y):
                self[SampleXYZ(x, y, 0)] = MockNode(self, x, y, True)
        # set some unpassable fields
        self[8, 0, 0].passable = False
        self[8, 1, 0].passable = False
        self[9, 1, 0].passable = False
        # generate connections
        for field in self.values():
            field.generate_connections()
        # set some tags
        self[5, 5, 0].tags |= set(['single_target', 'target'])
        self[5, 9, 0].tags |= set(['target'])
        self[3, 2, 0].tags |= set(['target'])


class TestPathfinding(unittest.TestCase):
    def setUp(self):
        """ Build test graph to test pathfinders on it """
        self.graph = MockGraph()

    def test_find_path(self):
        departure = self.graph[(1, 1, 0)]
        destination = self.graph[(SIZE_X - 2, SIZE_Y - 2, 0)]
        found_path = find_path(departure, destination)
        self.assertEqual(len(found_path), 14)

    def test_find_path_to_unavailable_field(self):
        departure = self.graph[(1, 1, 0)]
        destination = self.graph[(9, 0, 0)]
        self.assertRaises(NoPathFound, find_path, *(departure, destination))

    def test_find_nearest_targets(self):
        condition = lambda field: 'single_target' in field.tags
        departure = self.graph[(1, 1, 0)]
        found_paths = find_nearest_targets(departure, condition)
        self.assertEqual(len(found_paths), 1)

    def test_find_nearest_targets_multiple_targets(self):
        condition = lambda field: 'target' in field.tags
        departure = self.graph[(1, 1, 0)]
        found_paths = find_nearest_targets(departure, condition, count=1000)
        self.assertEqual(len(found_paths), 3)

    def test_find_nearest_targets_limit_distance(self):
        condition = lambda field: 'target' in field.tags
        departure = self.graph[(1, 1, 0)]
        found_paths = find_nearest_targets(departure, condition, count=1000,
                                           max_distance=5)
        self.assertEqual(len(found_paths), 1)

    def test_find_nearest_targets_unavalable_target(self):
        condition = lambda field: 'no_such_target' in field.tags
        departure = self.graph[(1, 1, 0)]
        found_paths = find_nearest_targets(departure, condition)
        self.assertEqual(len(found_paths), 0)

if __name__ == '__main__':
    unittest.main()
