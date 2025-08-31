#!/usr/bin/env python
from contexts_for_tests import pctrl, uctrl
from pytest import raises
from ydtpack import packb, unpackb

def test_bad_hook():
    with raises(TypeError):
        packed = packb([3, 1 + 2j], pack_ctrl=pctrl(), default=lambda o: o)
        unpacked = unpackb(packed, unpack_ctrl=uctrl(use_list=1))





