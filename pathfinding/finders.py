#!/usr/bin/env python
# -*- coding: utf-8 -*-
u'''Finder functions.

mallib: common library for mal projects
@author: Paweł Sobkowiak
@contact: pawel.sobkowiak@gmail.com
Copyright © 2011 Paweł Sobkowiak

'''

import bisect
import logging
from time import time

from constants import NOT_PASSABLE

logger = logging.getLogger('malpath')


class NoPathFound(Exception):
    pass


#def dist_heuristic(node1, node2):
#    x1, y1, z1 = node1.xyz
#    x2, y2, z2 = node2.xyz
#    return abs(x1 - x2) + abs(y1 - y2) + abs(z1 - z2)


def find_path(src, dst, max_nodes_checked=1000000):
    """ Implementation of A* algorithm """
    global logger
    if src == dst:
        return []
    success = None
    start_time = time()

    dx, dy, dz = dst.xyz
    x, y, z = src.xyz
    heuristic = (abs(x - dx) + abs(y - dy) + abs(z - dz))
    ### costs = { node: (g, h, parent), ... }
    costs = {src: (0, heuristic, None)}
    ### queue = [(g + h, g, node), ...]
    queue = [(heuristic, 0, src)]
    opened = set([src])
    closed = set()

    while queue:
        node_f, node_g, node = queue.pop(0)
        # optimalization - it is better to check if node is already
        # in closed list, than to remove touple from queue list
        if node in closed:
            continue

        # check if destination has been achieved
        if node == dst:
            success = True
            break
        elif len(closed) > max_nodes_checked:
            success = False
            break

        # move node to closed list
        opened.remove(node)
        closed.add(node)

        # check every neighbouring nodes
        for connection in node.connections:
            cost = connection.cost
            neighbour = connection.destination
            if cost == NOT_PASSABLE or neighbour in closed:
                continue
            cost += node_g
            if neighbour in opened:
                old_g, h, parent = costs[neighbour]
                if cost < old_g:
                    # update node cost
                    costs[neighbour] = (cost, h, node)
                    bisect.insort(queue, (cost + h, cost, neighbour))
            else:
                # add node to opened list
                x, y, z = neighbour.xyz
                heuristic = (abs(x - dx) + abs(y - dy) + abs(z - dz))
                costs[neighbour] = (cost, heuristic, node)
                bisect.insort(queue, (cost + heuristic, cost, neighbour))
                opened.add(neighbour)

    if success is None:
        logger.error("No path found - opened list empty - find_path(%s, %s)",
                     src, dst)
        raise NoPathFound("opened list empty - find_path(%s, %s)"
                          % (src, dst))

    # backtracing path
    path = []
    parent = costs[node][2]
    while parent:
        path.append(node)
        node = parent
        parent = costs[node][2]

    # calculating stats
    total_cost = costs[dst][0] if success else -1
    calculation_time = time() - start_time
    logger.debug("astar %.3f %s->%s lenght=%i closed=%i total_cost=%i heur=%i",
            calculation_time, src.xyz, dst.xyz, len(path),
            len(closed), total_cost, costs[src][1])
    return path


def find_nearest_targets(src, target_getter,
                         count=1, max_distance=100000):
    """
    Uses Dijkstra algorithm to find nodes that have any target
    returned by given target getter
    """
    global logger
    destinations = []
    start_time = time()

    costs = {src: (0, None)}
    queue = [(0, src)]
    opened = set([src])
    closed = set()
    while queue:
        node_cost, node = queue.pop(0)
        # optimalization - it is better to check if node is already
        # in closed list, than to remove touple from queue list
        if node in closed:
            continue

        # check if we achieved destination
        if node_cost > max_distance:
            break
        targets = target_getter(node)
        if targets:
            destinations.append((node, targets))
            if len(destinations) >= count:
                break

        # move to closed list
        opened.remove(node)
        closed.add(node)

        # check every neighbouring node
        for connection in node.connections:
            cost = connection.cost
            neighbour = connection.destination
            if cost == NOT_PASSABLE or neighbour in closed:
                continue
            cost += node_cost
            if neighbour in opened:
                if cost < costs[neighbour][0]:
                    # update neighbour cost
                    costs[neighbour] = (cost, node)
                    bisect.insort(queue, (cost, neighbour))
            else:
                # add to opened list
                costs[neighbour] = (cost, node)
                bisect.insort(queue, (cost, neighbour))
                opened.add(neighbour)

    # backtracing paths
    paths = []
    for destination, targets in destinations:
        path = []
        node = destination
        parent = costs[node][1]
        while parent:
            path.append(node)
            node = parent
            parent = costs[node][1]
        paths.append({'path': path, 'destination': destination,
                      'cost': costs[destination][0], 'targets': targets})

    # calculating stats
    calculation_time = time() - start_time
    logger.debug("dijkstra %.3f from %s paths_found=%i closed_list=%i",
            calculation_time, src.xyz, len(paths), len(closed))
    return paths
