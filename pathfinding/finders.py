#!/usr/bin/env python
# -*- coding: utf-8 -*-
u'''Finder functions.

Malsimulation: Malleable World Simulator
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


def find_path(departure, destination, max_fields_checked=1000000):
    """ Implementation of A* algorithm """
    global logger
    if departure == destination:
        return []
    success = None
    start_time = time()

    path_g = {}
    path_h = {}
    path_f = {}
    path_parent = {}

    first_heuristic = (abs(departure.xyz.x - destination.xyz.x) +
                       abs(departure.xyz.y - destination.xyz.y) +
                       abs(departure.xyz.z - destination.xyz.z))
    path_g[departure] = 0
    path_h[departure] = first_heuristic
    path_f[departure] = first_heuristic
    path_parent[departure] = None
    opened_ordered = [(first_heuristic, departure)]
    opened = set([departure])
    closed = set()
    while opened_ordered:
        current_field = opened_ordered.pop(0)[1]
        # optimalization - it is better to check if field is already
        # in closed list, than to remove touple from opened_ordered list
        if current_field in closed:
            continue

        # check if destination has been achieved
        if current_field == destination:
            success = True
            break
        elif len(closed) > max_fields_checked:
            success = False
            break

        # move field to closed list
        opened.remove(current_field)
        closed.add(current_field)

        # check every neighbouring fields
        current_g = path_g[current_field]
        for direction, connection in current_field.connections.items():
            cost = connection.cost
            neighbour = connection.destination
            if cost != NOT_PASSABLE and neighbour not in closed:
                cost += current_g
                if neighbour in opened:
                    if path_g[neighbour] > cost:
                        # update field cost
                        path_g[neighbour] = cost
                        path_f[neighbour] = cost + path_h[neighbour]
                        path_parent[neighbour] = (direction, current_field)
                        bisect.insort(opened_ordered,
                                      (path_f[neighbour], neighbour))
                else:
                    # add field to opened list
                    heuristic = (abs(neighbour.xyz.x - destination.xyz.x) +
                                 abs(neighbour.xyz.y - destination.xyz.y) +
                                 abs(neighbour.xyz.z - destination.xyz.z))
                    path_g[neighbour] = cost
                    path_h[neighbour] = heuristic
                    path_f[neighbour] = cost + heuristic
                    path_parent[neighbour] = (direction, current_field)
                    bisect.insort(opened_ordered,
                                  (path_f[neighbour], neighbour))
                    opened.add(neighbour)

    if success is None:
        logger.error("No path found - opened list empty - find_path(%s, %s)",
                     departure, destination)
        raise NoPathFound("opened list empty - find_path(%s, %s)"
                          % (departure, destination))

    # backtracing path
    path = []
    node = path_parent[current_field]
    while node:
        path.append(node[0])
        current_field = node[1]
        node = path_parent[current_field]

    # calculating stats
    total_cost = path_g[destination] if success else -1
    calculation_time = time() - start_time
    logger.debug("astar %.3f %s->%s lenght=%i closed=%i total_cost=%i heur=%i",
            calculation_time, departure.xyz, destination.xyz, len(path),
            len(closed), total_cost, first_heuristic)
    return path


def find_nearest_targets(departure, target_getter,
                         count=1, max_distance=100000):
    """
    Uses Dijkstra algorithm to find fields that has any target
    returned by given target getter
    """
    global logger
    destinations = []
    start_time = time()

    path_cost = {departure: 0}
    path_parent = {departure: None}
    opened_ordered = [(0, departure)]
    opened = set([departure])
    closed = set()
    while opened_ordered:
        current_cost, current_field = opened_ordered.pop(0)
        # optimalization - it is better to check if field is already
        # in closed list, than to remove touple from opened_ordered list
        if current_field in closed:
            continue

        # check if we achieved destination
        if path_cost[current_field] > max_distance:
            break
        targets = target_getter(current_field)
        if targets:
            destinations.append((current_field, targets))
            if len(destinations) >= count:
                break

        # move to closed list
        opened.remove(current_field)
        closed.add(current_field)

        # check every neighbouring field
        for direction, connection in current_field.connections.items():
            neighbour_cost = connection.cost
            neighbour = connection.destination
            if neighbour_cost != NOT_PASSABLE and neighbour not in closed:
                neighbour_cost += current_cost
                if neighbour in opened:
                    if path_cost[neighbour] > neighbour_cost:
                        # update field cost
                        path_cost[neighbour] = neighbour_cost
                        path_parent[neighbour] = (direction, current_field)
                        bisect.insort(opened_ordered,
                                      (neighbour_cost, neighbour))
                else:
                    # add to opened list
                    path_cost[neighbour] = neighbour_cost
                    path_parent[neighbour] = (direction, current_field)
                    bisect.insort(opened_ordered, (neighbour_cost, neighbour))
                    opened.add(neighbour)

    # backtracing paths
    paths = []
    for destination, targets in destinations:
        path = []
        field = destination
        node = path_parent[field]
        while node:
            path.append(node[0])
            field = node[1]
            node = path_parent[field]
        paths.append({'path': path, 'destination': destination,
                      'cost': path_cost[destination], 'targets': targets})

    # calculating stats
    calculation_time = time() - start_time
    logger.debug("dijkstra %.3f from %s paths_found=%i closed_list=%i",
            calculation_time, departure.xyz, len(paths), len(closed))
    return paths
