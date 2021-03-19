#!/usr/bin/env python
"""Tools.

mallib: meta decorators for refactoring etc.
@author: Paweł Sobkowiak
@contact: pawel.sobkowiak@gmail.com
Copyright © 2011 Paweł Sobkowiak

"""

import collections
import functools


class MarkJournal(collections.defaultdict):
    def __init__(self):
        super().__init__(lambda: collections.defaultdict(int))

    def print_all_counters(self):
        for label in self:
            self.print_counter(label)

    def print_counter(self, label):
        for counter, count in self[label].items():
            print(label, counter, count)


# a module global to hold @mark decorator findings
MARK = MarkJournal()


def mark(label, *, journal=None, enable=True):
    if journal is None:
        journal = MARK

    def decorator(func):
        if not enable:
            return func

        func_counter = f'{func.__module__}:{func.__qualname__}'

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            journal[label][func_counter] += 1
            return func(*args, **kwargs)

        return wrapper

    return decorator
