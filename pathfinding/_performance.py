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


def main(path):
    data = json.load(open(path))
    print data['graph'], data['sample']
    raise RuntimeError("To be implemented")


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print "Usage: %s <graph.json>" % sys.argv[0]
        sys.exit(1)
    path = sys.argv[1]
    if not os.path.exists(path):
        print "File: %s does not exist" % path
        sys.exit(1)
    main(path)
