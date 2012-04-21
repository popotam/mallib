#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''Sample minimal implementations of pathfinding primitives.

mallib: common library for mal projects
@author: Paweł Sobkowiak
@contact: pawel.sobkowiak@gmail.com
Copyright © 2011 Paweł Sobkowiak

'''

import collections

SampleXYZ = collections.namedtuple('XYZ', 'x y z')
SampleConnection = collections.namedtuple('Connection', 'destination cost')


class SampleNode(object):
    def __init__(self, xyz, tags=None, connections=None):
        self.xyz = xyz
        self.tags = tags if tags is not None else set()
        self.connections = connections if connections is not None else []

    def __str__(self):
        return "N(%i,%i,%i)" % self.xyz

    def __repr__(self):
        return "N(%i,%i,%i)" % self.xyz
