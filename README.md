# tmsgpack: Typed MessagePack-inspired pack/unpack component

The tmsgpack format expresses **typed objects**: maps and arrays (or: dicts and lists)
with an `object_type` property.

Unlike msgpack and pickle, this is not a batteries-included end-to-end serialization
solution.  It is a composable component that helps you to build end-to-end communication
solutions.

Your system solution design will make decisions on:
* What objects are serializable and what objects are not.
* What code to use (and, maybe, dynamically load) to instantiate serialized objects.
* How to represent objects that are unpacked but not supposed to 'live' in this process.
* How to share dynamic data between different packs/unpacks.
* How to asynchronously load and integrate shared data from different sources.
* How to map typed object meaning between different programming languages.
* Whether and how to convert persisted "old" data to current, new semantics (schemas).
* How much to attach explicit meaning and predictable schemas to your object types.
* Whether or not to use the 'expression execution' capabilities of tmsgpack.
* etc.

This python package makes a minimal (backwards-incompatible) modification to the
msgpack format to make all this elegantly possible.  This package is based on
`msgpack v1.0.5`.

## TODO: Installation

## Usage
Packing and unpacking data is controlled by `pack_ctrl` and `unpack_ctrl` objects (see
below for details how to create them):
```
from tmsgpack import packb, unpackb
packed = packb(data, pack_ctrl=pack_ctrl)
unpacked = unpackb(packed, unpack_ctrl=unpack_ctrl)
```
For multiple uses, you can use packer and unpacker objects:
```
from tmsgpack import Packer, Unpacker
packer = Packer(pack_ctrl=pack_ctrl)
unpacker = Unpacker(unpack_ctrl=unpack_ctrl)

packed = packer.pack(data)
unpacked = unpacker.unpack(packed)
```

## Minimal pack_ctrl and unpack_ctrl objects
Minimal controllers allow only JSON-like objects and raise errors when you ask for more:
```
from tmsgpack import PackConfig, UnpackConfig
from dataclasses import dataclass

@dataclass
class MinimalPackCtrl:
    def from_obj(self, obj):
        raise TypeError(f'Cannot serialize {type(obj)} object.')
    options: PackConfig

@dataclass
class MinimalUnpackCtrl:
    def from_dict(self, ctype, dct):
        raise ValueError(f'Unpack type not supported: {ctype} data: {dct}')
    def from_list(self, ctype, lst):
        raise ValueError(f'Unpack type not supported: {ctype} data: {lst}')
    options: UnpackConfig

def pctrl(**kwargs): return MinimalPackCtrl(options=PackConfig(**kwargs))
def uctrl(**kwargs): return MinimalUnpackCtrl(options=UnpackConfig(**kwargs))

minimal_pack_ctrl = pctrl()
minimal_unpack_ctrl = uctrl()
```

## The API and configuration
As you see, the `pack_ctrl` object provides a method `from_obj`:
```
as_dict, data_type, data = pack_ctrl.from(obj)

# When `as_dict` is true, then `data` should be a dictionary.
# When `as_dict` is false, then `data` should be a list.

unpacked = unpack_ctrl.from_dict(data_type, data) # used when as_dict is true.
unpacked = unpack_ctrl.from_list(data_type, data) # used when as_dict is false.

## Controller configuration objects
The `PackConfig` and `UnpackConfig` objects provide the following options:
```python
config = PackConfig(
    use_single_float=False, use_bin_type=True,
    tuple_as_list=True, strict_types=False,
    unicode_errors='strict', sort_keys=False,
)
"""
:param bool use_single_float:
    Use single precision float type for float. (default: False)

:param bool use_bin_type:
    Use bin type introduced in tmsgpack spec 2.0 for bytes.
    It also enables str8 type for unicode. (default: True)

:param bool tuple_as_list:
    If true, tuples are serialized as lists.  (default: True)
    Otherwise, tuples are passed to pack_ctrl.from_obj(?).

:param bool strict_types:
    If set to true, types will be checked to be exact. (default: False)
    Derived classes are distinct and passed to pack_ctrl.from_obj(?).
    Dicts, lists and tuples are not affected by strict_types.

:param str unicode_errors:
    The error handler for encoding unicode. (default: 'strict')
    DO NOT USE THIS!!  This option is kept for very specific usage.

:param bool sort_keys:
    Sort output dictionaries by key. (default: False)
"""

config = UnpackConfig(
    read_size=16*1024, use_tuple=False, raw=False,
    strict_dict_key=False, object_as_pairs=False,
    unicode_errors='strict', max_buffer_size=0,
    max_str_len=-1, max_bin_len=-1, max_list_len=-1, max_dict_len=-1,
)
"""
Config object for unpack_ctrl.options

:param int read_size:
    Used as `file_like.read(read_size)`. (default: `min(16*1024, max_buffer_size)`)

:param bool use_tuple:
    If true, unpack a tmsgpack list as a Python tuple. (default: False)

:param bool raw:
    If true, unpack tmsgpack strings (raw) to Python bytes.
    Otherwise, unpack to Python str by decoding with UTF-8 encoding (default: False).

:param bool strict_dict_key:
    If true only str or bytes are accepted for dict (dict) keys. (default: False).

:param callable object_as_pairs:
    If true, handles dicts as tuples of pairs.
    Otherwise, as dicts (default: False).

:param str unicode_errors:
    The error handler for decoding unicode. (default: 'strict')
    This option should be used only when you have tmsgpack data which
    contains invalid UTF-8 string.

:param int max_buffer_size:
    Limits size of data waiting unpacked.  0 means 2**32-1.
    The default value is 100*1024*1024 (100MiB).
    Raises `BufferFull` exception when it is insufficient.
    You should set this parameter when unpacking data from untrusted source.

:param int max_str_len:
    Limits max length of str. (default: max_buffer_size)

:param int max_bin_len:
    Limits max length of bin. (default: max_buffer_size)

:param int max_list_len:
    Limits max length of list.
    (default: max_buffer_size)

:param int max_dict_len:
    Limits max length of dict.
    (default: max_buffer_size//2)
"""
```
## Development: Environment and testing

**TODO**: `git clone`

```
# Create a virtual environment in your project directory
cd ~/git/tmsgpack
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Upgrade pip (recommended)
pip install --upgrade pip

# Install the required dependencies
pip install -r requirements.txt

# Now you can run the tests
make test

# Run one test
pytest -v test/test_typed_objects.py
```

