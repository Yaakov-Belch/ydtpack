from .exceptions import *
import os
import sys


version = (1, 0, 5)
__version__ = "1.0.5"


if os.environ.get("YDTPACK_PUREPYTHON"):
    from .fallback import Packer, unpackb, Unpacker
else:
    try:
        from ._cydtpack import Packer, unpackb, Unpacker
    except ImportError:
        from .fallback import Packer, unpackb, Unpacker


def pack(o, stream, pack_ctrl, **kwargs):
    """
    Pack object `o` and write it to `stream`

    See :class:`Packer` for options.
    """
    packer = Packer(pack_ctrl=pack_ctrl, **kwargs)
    stream.write(packer.pack(o))


def packb(o, pack_ctrl, **kwargs):
    """
    Pack object `o` and return packed bytes

    See :class:`Packer` for options.
    """
    return Packer(pack_ctrl=pack_ctrl, **kwargs).pack(o)


def unpack(stream, unpack_ctrl, **kwargs):
    """
    Unpack an object from `stream`.

    Raises `ExtraData` when `stream` contains extra bytes.
    See :class:`Unpacker` for options.
    """
    data = stream.read()
    return unpackb(data, unpack_ctrl=unpack_ctrl, **kwargs)


