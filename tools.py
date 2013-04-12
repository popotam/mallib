#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''Tools.

mallib: common library for mal projects
@author: Paweł Sobkowiak
@contact: pawel.sobkowiak@gmail.com
Copyright © 2011 Paweł Sobkowiak

'''
from __future__ import absolute_import, division, print_function

import collections
import random
from time import time
from itertools import tee, izip, izip_longest, chain

from . import ordered_set

if hasattr(collections, 'OrderedDict'):
    OrderedDict = collections.OrderedDict
else:
    from . import ordered_dict
    OrderedDict = ordered_dict.OrderedDict

OrderedSet = ordered_set.OrderedSet

####################### FUNCTIONS #######################
flatten = chain.from_iterable


class Timer(object):
    def __init__(self):
        self.t0 = time()
        self.last_time = self.t0

    def check(self):
        new_time = time()
        output = "%3.3fs" % (new_time - self.last_time)
        self.last_time = new_time
        return output

    __call__ = check

    def total(self):
        return "%3.3fs" % (time() - self.t0)


def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return izip(a, b)


def grouper(n, iterable, fillvalue=None):
    "grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return izip_longest(fillvalue=fillvalue, *args)


def make_seed(randgen=None):
    if randgen is None:
        randgen = random
    return randgen.randint(0, 999999999)


def choice_weighted_by_slope(elements, altitudes, relative_height, rand=None):
    """
    >>> import random
    >>> random.seed(0)
    >>> choice_weighted_by_slope(['a','b','c'], {'a':100,'b':10,'c':-10}, 120)
    'c'
    """
    if rand is None:
        rand = random
    cumulation = 0
    cumulated_list = []
    for element in elements:
        cumulation += relative_height - altitudes[element]
        cumulated_list.append((cumulation, element))
    treshhold = rand.randint(0, cumulation)
    for score, element in cumulated_list:
        result = element
        if treshhold < score:
            break
    return result


def choose_lowest(elements, altitudes, rand=None):
    """
    >>> import random
    >>> random.seed(0)
    >>> choose_lowest(['a','b','c'], {'a':100,'b':-100,'c':-100})
    'c'
    """
    if rand is None:
        rand = random
    min_alt = min(altitudes.values())
    return rand.choice([element for element in elements
                        if altitudes[element] == min_alt])
