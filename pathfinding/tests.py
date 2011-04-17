#!/usr/bin/env python
# -*- coding: utf-8 -*-
u'''Tests.

mallib: common library for mal projects
@author: Paweł Sobkowiak
@contact: pawel.sobkowiak@gmail.com
Copyright © 2011 Paweł Sobkowiak

'''

import unittest
import collections

from constants import NOT_PASSABLE
from finders import find_path, find_nearest_targets, NoPathFound

MockXYZ = collections.namedtuple('MockXYZ', 'x y z')
MockConnection = collections.namedtuple('MockConnection', 'destination cost')
MOCK_DIRECTIONS = (MockXYZ(1, 0, 0), MockXYZ(-1, 0, 0),
                   MockXYZ(0, 1, 0), MockXYZ(0, -1, 0))


class MockField(object):
    def __init__(self, graph, x, y, passable, tags=None):
        self.x = x
        self.y = y
        self.passable = passable
        self.graph = graph
        self.tags = tags if tags is not None else set()
        self.connections = []

    @property
    def xyz(self):
        return MockXYZ(self.x, self.y, 0)

    def generate_connections(self):
        self.connections = []
        for direction in MOCK_DIRECTIONS:
            neighbor_xyz = MockXYZ(self.x + direction.x,
                                   self.y + direction.y, 0)
            neighbor_field = self.graph.get(neighbor_xyz)
            if neighbor_field:
                cost = 1 if neighbor_field.passable else NOT_PASSABLE
                self.connections.append(MockConnection(neighbor_field, cost))
        return self.connections


class MockGraph(dict):
    def __init__(self):
        for x in xrange(10):
            for y in xrange(10):
                self[MockXYZ(x, y, 0)] = MockField(self, x, y, True)
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
        destination = self.graph[(8, 8, 0)]
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
