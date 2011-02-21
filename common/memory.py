#!/usr/bin/env python
# -*- coding: utf-8 -*-
u'''Memory usage profiling code.

Malsimulation: Malleable World Simulator
@author: Paweł Sobkowiak
@contact: pawel.sobkowiak@gmail.com
Copyright © 2011 Paweł Sobkowiak

'''


def check_memory():
    try:
        from guppy import hpy
        hp = hpy().heap()
        print hp
        print hp.byrcs
    except ImportError:
        print "Aborting memory analysis - could not import heapy"
