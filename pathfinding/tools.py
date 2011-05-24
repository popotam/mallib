#!/usr/bin/env python
# -*- coding: utf-8 -*-
u'''Tools and exporters for pathfinding.

mallib: common library for mal projects
@author: Paweł Sobkowiak
@contact: pawel.sobkowiak@gmail.com
Copyright © 2011 Paweł Sobkowiak

'''

import collections
import json
import random


def export_to_json(entry_node, fp=None, sample_size=10, only_passable=True):
    """Exports graph to JSON.

    Walks the graph starting from entry_node.
    Use file object to fp argument to export to file.
    Uses Node.xyz tuple as node identifier.
    """
    queue = collections.deque([entry_node])
    opened = set([entry_node])
    graph = []
    while queue:
        node = queue.pop()
        row = [node.xyz.x, node.xyz.y, node.xyz.z, []]
        for connection in node.connections:
            if only_passable and not connection.cost:
                continue
            dst = connection.destination
            if dst not in opened:
                opened.add(dst)
                queue.append(dst)
            row[3].append([dst.xyz.x, dst.xyz.y, dst.xyz.z,
                           int(connection.cost)])
        graph.append(row)
    opened = list(opened)
    sample = random.sample(opened, min(len(opened), sample_size))
    sample = [list(node.xyz) for node in sample]
    data = {'graph': graph, 'sample': sample}

    if fp is not None:
        json.dump(data, fp)
    else:
        return json.dumps(data)
