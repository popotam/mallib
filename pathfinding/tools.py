#!/usr/bin/env python
# -*- coding: utf-8 -*-
u'''Tools and exporters for pathfinding.

mallib: common library for mal projects
@author: Paweł Sobkowiak
@contact: pawel.sobkowiak@gmail.com
Copyright © 2011 Paweł Sobkowiak

'''

from collections import deque
import json


def export_to_json(entry_node, fp=None):
    """Exports graph to JSON.

    Walks the graph starting from entry_node.
    Use file object to fp argument to export to file.
    Uses Node.xyz tuple as node identifier.
    """
    queue = deque([entry_node])
    opened = set([entry_node])
    data = []
    while queue:
        node = queue.pop()
        row = list(node.xyz) + [[]]
        for connection in node.connections:
            dst = connection.destination
            if dst not in opened:
                opened.add(dst)
                queue.append(dst)
            row[3].append(list(dst.xyz) + [connection.cost])
        data.append(row)

    if fp is not None:
        json.dump(data, fp)
    else:
        return json.dumps(data)
