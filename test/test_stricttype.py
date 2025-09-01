from contexts_for_tests import pctrl, uctrl
from collections import namedtuple
from tmsgpack import packb, unpackb


def test_namedtuple():
    T = namedtuple("T", "foo bar")

    def default(o):
        if isinstance(o, T):
            return dict(o._asdict())
        raise TypeError(f"Unsupported type {type(o)}")

    packed = packb(T(1, 42), pack_ctrl=pctrl(strict_types=True, use_bin_type=True), default=default)
    unpacked = unpackb(packed, unpack_ctrl=uctrl(raw=False))
    assert unpacked == {"foo": 1, "bar": 42}



