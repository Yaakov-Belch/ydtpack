#!/usr/bin/env python
from contexts_for_tests import pctrl0, uctrl0
from pytest import raises
from ydtpack import packb, unpackb, Unpacker, FormatError, StackError, OutOfData

import datetime


class DummyException(Exception):
    pass


def test_raise_on_find_unsupported_value():
    with raises(TypeError):
        packb(datetime.datetime.now())


def test_invalidvalue():
    incomplete = b"\xd9\x97#DL_"  # raw8 - length=0x97
    with raises(ValueError):
        unpackb(incomplete, unpack_ctrl=uctrl0)

    with raises(OutOfData):
        unpacker = Unpacker(unpack_ctrl=uctrl0)
        unpacker.feed(incomplete)
        unpacker.unpack()

    with raises(FormatError):
        unpackb(b"\xc1", unpack_ctrl=uctrl0)  # (undefined tag)

    with raises(FormatError):
        unpackb(b"\x91\xc1", unpack_ctrl=uctrl0)  # fixarray(len=1) [ (undefined tag) ]

    with raises(StackError):
        unpackb(b"\x91" * 3000, unpack_ctrl=uctrl0)  # nested fixarray(len=1)


def test_strict_map_key():
    valid = {"unicode": 1, b"bytes": 2}
    packed = packb(valid, pack_ctrl=pctrl0, use_bin_type=True)
    assert valid == unpackb(packed, unpack_ctrl=uctrl0, raw=False, strict_map_key=True)

    invalid = {42: 1}
    packed = packb(invalid, pack_ctrl=pctrl0, use_bin_type=True)
    with raises(ValueError):
        unpackb(packed, unpack_ctrl=uctrl0, raw=False, strict_map_key=True)
