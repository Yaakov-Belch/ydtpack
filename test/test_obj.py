#!/usr/bin/env python
from contexts_for_tests import pctrl0, uctrl0
from pytest import raises
from ydtpack import packb, unpackb

def test_decode_pairs_hook():
    packed = packb([3, {1: 2, 3: 4}], pack_ctrl=pctrl0)
    prod_sum = 1 * 2 + 3 * 4
    unpacked = unpackb(
        packed,
        unpack_ctrl=uctrl0,
        object_pairs_hook=lambda l: sum(k * v for k, v in l),
        use_list=1,
        strict_map_key=False,
    )
    assert unpacked[1] == prod_sum


def test_only_one_obj_hook():
    with raises(TypeError):
        unpackb(b"", unpack_ctrl=uctrl0, object_hook=lambda x: x, object_pairs_hook=lambda x: x)


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


