from contexts_for_tests import pctrl0, uctrl0
from collections import namedtuple
from ydtpack import packb, unpackb


def test_namedtuple():
    T = namedtuple("T", "foo bar")

    def default(o):
        if isinstance(o, T):
            return dict(o._asdict())
        raise TypeError(f"Unsupported type {type(o)}")

    packed = packb(T(1, 42), pack_ctrl=pctrl0, strict_types=True, use_bin_type=True, default=default)
    unpacked = unpackb(packed, unpack_ctrl=uctrl0, raw=False)
    assert unpacked == {"foo": 1, "bar": 42}


def test_tuple():
    t = ("one", 2, b"three", (4,))

    def default(o):
        if isinstance(o, tuple):
            return {"__type__": "tuple", "value": list(o)}
        raise TypeError(f"Unsupported type {type(o)}")

    def convert(o):
        if o.get("__type__") == "tuple":
            return tuple(o["value"])
        return o

    data = packb(t, pack_ctrl=pctrl0, strict_types=True, use_bin_type=True, default=default)
    expected = unpackb(data, unpack_ctrl=uctrl0, raw=False, object_hook=convert)

    assert expected == t


