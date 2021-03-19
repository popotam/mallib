#!/usr/bin/env python
"""Tools.

mallib: common library for mal projects
@author: Paweł Sobkowiak
@contact: pawel.sobkowiak@gmail.com
Copyright © 2011 Paweł Sobkowiak

"""


def test_mark_function():
    from .meta import MARK, mark

    @mark('test')
    def adder(a, b):
        return a + b

    adder(2, 2)
    print(MARK)
    assert MARK['test']['mallib.tests:adder'] == 1


def test_mark_method():
    from .meta import MARK, mark

    class Adder(object):
        @mark('test')
        def adder_method(self, a, b):
            return a + b

    Adder().adder_method(2, 2)
    print(MARK)
    assert MARK['test']['mallib.tests.Adder:adder_method'] == 1


def test_mark_other_journal():
    from .meta import MARK, mark
    import collections
    journal = collections.defaultdict(lambda: collections.defaultdict(int))

    @mark('test', journal=journal)
    def adder_other_journal(a, b):
        return a + b

    adder_other_journal(2, 2)
    print(MARK)
    print(journal)
    assert MARK['test']['mallib.tests:adder_other_journal'] == 0
    assert journal['test']['mallib.tests:adder_other_journal'] == 1


def test_mark_disabled():
    from .meta import MARK, mark

    @mark('test', enable=False)
    def add_disabled(a, b):
        return a + b

    add_disabled(2, 2)
    print(MARK)
    assert MARK['test']['mallib.tests:add_disabled'] == 0
