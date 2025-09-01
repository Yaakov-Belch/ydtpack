from ydtpack import PackConfig, UnpackConfig
from dataclasses import dataclass

@dataclass
class TestPackCtrl:
    def from_obj(self, obj): return 123, [1,2,3]
    options: PackConfig

@dataclass
class TestUnpackCtrl:
    def from_dict(self, ctype, dict):   return dict
    def from_array(self, ctype, array): return array
    options: UnpackConfig

def pctrl(**kwargs): return TestPackCtrl(options=PackConfig(**kwargs))
def uctrl(**kwargs): return TestUnpackCtrl(options=UnpackConfig(**kwargs))
