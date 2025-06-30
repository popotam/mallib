#!/usr/bin/env python
"""Performance framework for pathfinding.

mallib: common library for mal projects
@author: Paweł Sobkowiak
@contact: pawel.sobkowiak@gmail.com
Copyright © 2011 Paweł Sobkowiak

"""

import json
import logging
from optparse import OptionParser
import os
import sys
import time

from .finders import find_path, find_path_bisect_insort, find_path_heapq
from .sample import SampleXYZ, SampleConnection, SampleNode

FIND_FUNCTIONS = {
    'find_path': find_path,
    'find_path_bisect_insort': find_path_bisect_insort,
    'find_path_heapq': find_path_heapq,
}


class SimpleGraph(dict):
    node_class = SampleNode

    def get_or_create(self, xyz):
        if xyz not in self:
            self[xyz] = self.node_class(xyz)
        return self[xyz]


def find_all_paths(sample, find_func):
    t0 = time.time()
    for src in sample:
        for dst in sample:
            find_func(src, dst)
    return time.time() - t0


def main(path, repetitions, find_func):
    find_func = FIND_FUNCTIONS[find_func]
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
    for index in range(repetitions):
        print(index, ':', find_all_paths(sample, find_func))


if __name__ == '__main__':
    usage = "Usage: _performance.py [options] <graph.json>\n" + __doc__
    parser = OptionParser(usage=usage)
    parser.add_option(
        "-v",
        "--verbose",
        action="store_true",
        dest="verbose",
        help="log results for each path",
        default=False,
    )
    parser.add_option(
        "-r",
        "--repetitions",
        type="int",
        dest="repetitions",
        help="how many times repeat the measurement",
        default=10,
    )
    parser.add_option(
        "-f",
        "--find-function",
        type="str",
        dest="find_func",
        help="choose find function implementation {}".format(list(FIND_FUNCTIONS.keys())),
        default="find_path",
    )
    (options, args) = parser.parse_args()
    if options.find_func not in FIND_FUNCTIONS:
        print("Incorrect find function.")
        parser.print_help()
    if options.verbose:
        logging.basicConfig(level=logging.DEBUG)
    if len(args) < 1:
        parser.print_usage()
        sys.exit(1)
    path = args[0]
    if not os.path.exists(path):
        print("File: %s does not exist" % path)
        sys.exit(1)
    main(path, options.repetitions, options.find_func)
