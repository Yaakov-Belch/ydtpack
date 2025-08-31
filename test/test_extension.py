from contexts_for_tests import pctrl0, uctrl0
import array
import ydtpack as ydtpack

def test_overriding_hooks():
    def default(obj):
        if isinstance(obj, int):
            return {"__type__": "long", "__data__": str(obj)}
        else:
            return obj

    obj = {"testval": 1823746192837461928374619}
    refobj = {"testval": default(obj["testval"])}
    refout = ydtpack.packb(refobj, pack_ctrl=pctrl0)
    assert isinstance(refout, (str, bytes))
    testout = ydtpack.packb(obj, pack_ctrl=pctrl0, default=default)

    assert refout == testout
