#!/usr/bin/env python
from contexts_for_tests import pctrl, uctrl
from ydtpack import packb, unpackb
from collections import namedtuple


class MyList(list):
    pass


class MyDict(dict):
    pass


class MyTuple(tuple):
    pass


MyNamedTuple = namedtuple("MyNamedTuple", "x y")


def test_types():
    assert packb(MyDict(), pack_ctrl=pctrl()) == packb(dict(), pack_ctrl=pctrl())
    assert packb(MyList(), pack_ctrl=pctrl()) == packb(list(), pack_ctrl=pctrl())
    assert packb(MyNamedTuple(1, 2), pack_ctrl=pctrl()) == packb((1, 2), pack_ctrl=pctrl())
