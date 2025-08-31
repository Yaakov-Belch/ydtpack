#!/usr/bin/env python
from contexts_for_tests import pctrl0, uctrl0

import sys
import pytest
from ydtpack import packb, unpackb


def test_unpack_buffer():
    from array import array

    buf = array("b")
    buf.frombytes(packb((b"foo", b"bar"), pack_ctrl=pctrl0))
    obj = unpackb(buf, unpack_ctrl=uctrl0, use_list=1)
    assert [b"foo", b"bar"] == obj


def test_unpack_bytearray():
    buf = bytearray(packb((b"foo", b"bar"), pack_ctrl=pctrl0))
    obj = unpackb(buf, unpack_ctrl=uctrl0, use_list=1)
    assert [b"foo", b"bar"] == obj
    expected_type = bytes
    assert all(type(s) == expected_type for s in obj)


def test_unpack_memoryview():
    buf = bytearray(packb((b"foo", b"bar"), pack_ctrl=pctrl0))
    view = memoryview(buf)
    obj = unpackb(view, unpack_ctrl=uctrl0, use_list=1)
    assert [b"foo", b"bar"] == obj
    expected_type = bytes
    assert all(type(s) == expected_type for s in obj)
