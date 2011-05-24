#!/usr/bin/env python
# -*- coding: utf-8 -*-
u'''Performance framework for pathfinding.

mallib: common library for mal projects
@author: Paweł Sobkowiak
@contact: pawel.sobkowiak@gmail.com
Copyright © 2011 Paweł Sobkowiak

'''

import json
import os
import sys

from finders import find_path
from sample import SampleXYZ, SampleConnection, SampleNode


class SimpleGraph(dict):
    node_class = SampleNode

    def get_or_create(self, xyz):
        if xyz not in self:
            self[xyz] = self.node_class(xyz)
        return self[xyz]


def main(path):
    data = json.load(open(path))
    graph = SimpleGraph()
    for node_data in data['graph']:
        xyz = SampleXYZ(*node_data[:3])
        node = graph.get_or_create(xyz)
        for conn_data in node_data[3]:
            conn_node = graph.get_or_create(SampleXYZ(*conn_data[:3]))
            connection = SampleConnection(conn_node, conn_data[3])
            node.connections.append(connection)
    sample = [graph[SampleXYZ(*node)] for node in data['sample']]
    import time
    t0 = time.time()
    find_path(sample[0], sample[-1])
    print time.time() - t0

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print "Usage: %s <graph.json>" % sys.argv[0]
        sys.exit(1)
    path = sys.argv[1]
    if not os.path.exists(path):
        print "File: %s does not exist" % path
        sys.exit(1)
    main(path)
