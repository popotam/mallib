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


#def dist_heuristic(field1, field2):
#    x1, y1, z1 = field1.xyz
#    x2, y2, z2 = field2.xyz
#    return abs(x1 - x2) + abs(y1 - y2) + abs(z1 - z2)


def find_path(src, dst, max_fields_checked=1000000):
    """ Implementation of A* algorithm """
    global logger
    if src == dst:
        return []
    success = None
    start_time = time()

    dx, dy, dz = dst.xyz
    x, y, z = src.xyz
    heuristic = (abs(x - dx) + abs(y - dy) + abs(z - dz))
    ### costs = { field: (g, h, parent), ... }
    costs = {src: (0, heuristic, None)}
    ### queue = [(g + h, g, field), ...]
    queue = [(heuristic, 0, src)]
    opened = set([src])
    closed = set()

    while queue:
        field_f, field_g, field = queue.pop(0)
        # optimalization - it is better to check if field is already
        # in closed list, than to remove touple from queue list
        if field in closed:
            continue

        # check if destination has been achieved
        if field == dst:
            success = True
            break
        elif len(closed) > max_fields_checked:
            success = False
            break

        # move field to closed list
        opened.remove(field)
        closed.add(field)

        # check every neighbouring fields
        #field_g = costs[field][0]
        for connection in field.connections:
            cost = connection.cost
            neighbour = connection.destination
            if cost == NOT_PASSABLE or neighbour in closed:
                continue
            cost += field_g
            if neighbour in opened:
                old_g, h, parent = costs[neighbour]
                if cost < old_g:
                    # update field cost
                    costs[neighbour] = (cost, h, field)
                    bisect.insort(queue, (cost + h, cost, neighbour))
            else:
                # add field to opened list
                x, y, z = neighbour.xyz
                heuristic = (abs(x - dx) + abs(y - dy) + abs(z - dz))
                costs[neighbour] = (cost, heuristic, field)
                bisect.insort(queue, (cost + heuristic, cost, neighbour))
                opened.add(neighbour)

    if success is None:
        logger.error("No path found - opened list empty - find_path(%s, %s)",
                     src, dst)
        raise NoPathFound("opened list empty - find_path(%s, %s)"
                          % (src, dst))

    # backtracing path
    path = []
    parent = costs[field][2]
    while parent:
        path.append(field)
        field = parent
        parent = costs[field][2]

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
    Uses Dijkstra algorithm to find fields that has any target
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
        field_cost, field = queue.pop(0)
        # optimalization - it is better to check if field is already
        # in closed list, than to remove touple from queue list
        if field in closed:
            continue

        # check if we achieved destination
        if field_cost > max_distance:
            break
        targets = target_getter(field)
        if targets:
            destinations.append((field, targets))
            if len(destinations) >= count:
                break

        # move to closed list
        opened.remove(field)
        closed.add(field)

        # check every neighbouring field
        for connection in field.connections:
            cost = connection.cost
            neighbour = connection.destination
            if cost == NOT_PASSABLE or neighbour in closed:
                continue
            cost += field_cost
            if neighbour in opened:
                if cost < costs[neighbour][0]:
                    # update neighbour cost
                    costs[neighbour] = (cost, field)
                    bisect.insort(queue, (cost, neighbour))
            else:
                # add to opened list
                costs[neighbour] = (cost, field)
                bisect.insort(queue, (cost, neighbour))
                opened.add(neighbour)

    # backtracing paths
    paths = []
    for destination, targets in destinations:
        path = []
        field = destination
        parent = costs[field][1]
        while parent:
            path.append(field)
            field = parent
            parent = costs[field][1]
        paths.append({'path': path, 'destination': destination,
                      'cost': costs[destination][0], 'targets': targets})

    # calculating stats
    calculation_time = time() - start_time
    logger.debug("dijkstra %.3f from %s paths_found=%i closed_list=%i",
            calculation_time, src.xyz, len(paths), len(closed))
    return paths
