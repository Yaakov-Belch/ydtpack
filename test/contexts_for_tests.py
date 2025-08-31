from dataclasses import dataclass

@dataclass
class TestPackCtrl:
    def from_obj(self, obj): return 123, [1,2,3]

@dataclass
class TestUnpackCtrl:
    def from_map(self, ctype, map):     return map
    def from_array(self, ctype, array): return array


pctrl0 = TestPackCtrl()
uctrl0 = TestUnpackCtrl()
