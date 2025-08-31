#!/usr/bin/env python
from contexts_for_tests import pctrl0, uctrl0
from pytest import raises
from ydtpack import packb, unpackb

def test_bad_hook():
    with raises(TypeError):
        packed = packb([3, 1 + 2j], pack_ctrl=pctrl0, default=lambda o: o)
        unpacked = unpackb(packed, unpack_ctrl=uctrl0, use_list=1)


def _arr_to_str(arr):
    return "".join(str(c) for c in arr)


def test_array_hook():
    packed = packb([1, 2, 3], pack_ctrl=pctrl0)
    unpacked = unpackb(packed, unpack_ctrl=uctrl0, list_hook=_arr_to_str, use_list=1)
    assert unpacked == "123"


class DecodeError(Exception):
    pass


