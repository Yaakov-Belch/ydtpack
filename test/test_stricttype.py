from contexts_for_tests import pctrl, uctrl
from collections import namedtuple
from tmsgpack import packb, unpackb

def test_stricttype():
    # assert False, 'test strict for elementary types'

    original = expected = [1,2,3]
    packed = packb(original, pack_ctrl=pctrl(strict_types=True, use_bin_type=True))
    unpacked = unpackb(packed, unpack_ctrl=uctrl(raw=False))
    assert unpacked == expected



