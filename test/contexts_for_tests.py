from tmsgpack import PackConfig, UnpackConfig
from dataclasses import dataclass

@dataclass
class TestPackCtrl:
    def from_obj(self, obj): return 123, [1,2,3]
    options: PackConfig

@dataclass
class TestUnpackCtrl:
    def from_dict(self, ctype, dct): return dct
    def from_list(self, ctype, lst): return lst
    options: UnpackConfig

def pctrl(**kwargs): return TestPackCtrl(options=PackConfig(**kwargs))
def uctrl(**kwargs): return TestUnpackCtrl(options=UnpackConfig(**kwargs))
