from tmsgpack import packb, unpackb, PackConfig, UnpackConfig
from dataclasses import dataclass, is_dataclass, fields
from typing import Dict

@dataclass
class TypedPackCtrl:
    def from_obj(self, obj):
        if type(obj) is tuple: return [False, 'tuple', obj]
        if not is_dataclass(obj): raise TypeError(f'Cannot serialize {type(obj)} object.')
        as_dict = not getattr(obj, 'as_list', False)
        object_type = obj.__class__.__name__
        if as_dict:
            data = {
                field.name: getattr(obj, field.name)
                for field in fields(obj)
            }
        else:
            data = [
                getattr(obj, field.name)
                for field in fields(obj)
            ]
        return as_dict, object_type, data
    options: PackConfig

@dataclass
class TypedUnpackCtrl:
    constructors: Dict[str, callable]
    def from_dict(self, ctype, data): return self.constructors[ctype](**data)
    def from_list(self, ctype, data): return self.constructors[ctype]( *data)
    options: UnpackConfig

def pc(**kwargs): return TypedPackCtrl(options=PackConfig(**kwargs))
def uc(fns, **kwargs):
    return TypedUnpackCtrl(
        constructors={fn.__name__:fn for fn in fns},
        options=UnpackConfig(**kwargs),
    )

@dataclass
class Foo:
    y: str = 'Y'
    x: int = 1

@dataclass
class Bar:
    y: str = 'Y'
    x: int = 1
    as_list = True

@dataclass
class FooBar:
    y: str = 'Y'
    x: int = 1
    as_list: bool = False

@dataclass
class Add:
    x: int = 10
    y: int = 20

class Expr:
    @staticmethod
    def Add(x:int, y:int): return x+y

def run(input, expected=None):
    if expected is None: expected = input
    packed = packb(input, pack_ctrl=pc())
    output = unpackb(packed, unpack_ctrl=uc([Foo, Bar, FooBar, Expr.Add]))
    assert output == expected

def test_typed_foobar():
    run(Foo())  # Encoded as a typed dict
    run(Bar())  # Encoded as a typed list

def test_simple_expression():
    run(Add(Add(1,2), Add(2,3)), 8)

