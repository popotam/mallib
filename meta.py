#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tools.

mallib: meta decorators for refactoring etc.
@author: Paweł Sobkowiak
@contact: pawel.sobkowiak@gmail.com
Copyright © 2011 Paweł Sobkowiak

"""
from __future__ import absolute_import, division, print_function

import collections
import inspect


class MarkJournal(collections.defaultdict):
    def __init__(self):
        super(MarkJournal, self).__init__(lambda: collections.defaultdict(int))

    def print_all_counters(self):
        for label in self:
            self.print_counter(label)

    def print_counter(self, label):
        for counter, count in self[label].items():
            print(label, counter, count)

# a module global to hold @mark decorator findings
MARK = MarkJournal()


def mark(label=None, journal=MARK, enable=True):
    def decorator(func):
        if not enable:
            return func
        func_counter = "%s:%s" % (func.__module__, func.__name__)

        def func_wrapper(*args, **kwargs):
            journal[label][func_counter] += 1
            return func(*args, **kwargs)

        def method_wrapper(self, *args, **kwargs):
            counter = "%s.%s:%s" % (
                        self.__class__.__module__,
                        self.__class__.__name__,
                        func.__name__)
            journal[label][counter] += 1
            return func(self, *args, **kwargs)

        args = inspect.getargspec(func).args
        if args and args[0] == 'self':
            method_wrapper.__name__ = func.__name__
            method_wrapper.__doc__ = func.__doc__
            return method_wrapper
        else:
            func_wrapper.__name__ = func.__name__
            func_wrapper.__doc__ = func.__doc__
            return func_wrapper

    return decorator
