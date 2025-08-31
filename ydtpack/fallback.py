"""Fallback pure Python implementation of ydtpack"""
import sys
import struct

if hasattr(sys, "pypy_version_info"):
    # StringIO is slow on PyPy, StringIO is faster.  However: PyPy's own
    # StringBuilder is fastest.
    from __pypy__ import newlist_hint

    try:
        from __pypy__.builders import BytesBuilder as StringBuilder
    except ImportError:
        from __pypy__.builders import StringBuilder
    USING_STRINGBUILDER = True

    class StringIO:
        def __init__(self, s=b""):
            if s:
                self.builder = StringBuilder(len(s))
                self.builder.append(s)
            else:
                self.builder = StringBuilder()

        def write(self, s):
            if isinstance(s, memoryview):
                s = s.tobytes()
            elif isinstance(s, bytearray):
                s = bytes(s)
            self.builder.append(s)

        def getvalue(self):
            return self.builder.build()

else:
    USING_STRINGBUILDER = False
    from io import BytesIO as StringIO

    newlist_hint = lambda size: []


from .exceptions import BufferFull, OutOfData, ExtraData, FormatError, StackError

TYPE_IMMEDIATE = 0
TYPE_ARRAY = 1
TYPE_MAP = 2
TYPE_RAW = 3
TYPE_BIN = 4
TYPE_EXT = 5

DEFAULT_RECURSE_LIMIT = 511

def _check_type_strict(obj, t, type=type, tuple=tuple):
    if type(t) is tuple:
        return type(obj) in t
    else:
        return type(obj) is t


def _get_data_from_buffer(obj):
    view = memoryview(obj)
    if view.itemsize != 1:
        raise ValueError("cannot unpack from multi-byte object")
    return view


def unpackb(packed, *, unpack_ctrl, **kwargs): # kwargs are obsolete hooks
    """
    Unpack an object from `packed`.

    Raises ``ExtraData`` when *packed* contains extra bytes.
    Raises ``ValueError`` when *packed* is incomplete.
    Raises ``FormatError`` when *packed* is not valid ydtpack.
    Raises ``StackError`` when *packed* contains too nested.
    Other exceptions can be raised during unpacking.

    See :class:`Unpacker` for options.
    """
    unpacker = Unpacker(
        None, unpack_ctrl=unpack_ctrl, buffer_size=len(packed), **kwargs,
    )
    unpacker.feed(packed)
    try:
        ret = unpacker._unpack()
    except OutOfData:
        raise ValueError("Unpack failed: incomplete input")
    except RecursionError:
        raise StackError
    if unpacker._got_extradata():
        raise ExtraData(ret, unpacker._get_extradata())
    return ret


_NO_FORMAT_USED = ""
_MSGPACK_HEADERS = {
    0xC4: (1, _NO_FORMAT_USED, TYPE_BIN),
    0xC5: (2, ">H", TYPE_BIN),
    0xC6: (4, ">I", TYPE_BIN),
    0xC7: (2, "Bb", TYPE_EXT),     # TYPE_EXT raises FormatError.
    0xC8: (3, ">Hb", TYPE_EXT),    # TYPE_EXT raises FormatError.
    0xC9: (5, ">Ib", TYPE_EXT),    # TYPE_EXT raises FormatError.
    0xCA: (4, ">f"),
    0xCB: (8, ">d"),
    0xCC: (1, _NO_FORMAT_USED),
    0xCD: (2, ">H"),
    0xCE: (4, ">I"),
    0xCF: (8, ">Q"),
    0xD0: (1, "b"),
    0xD1: (2, ">h"),
    0xD2: (4, ">i"),
    0xD3: (8, ">q"),
    0xD4: (1, "b1s", TYPE_EXT),    # TYPE_EXT raises FormatError.
    0xD5: (2, "b2s", TYPE_EXT),    # TYPE_EXT raises FormatError.
    0xD6: (4, "b4s", TYPE_EXT),    # TYPE_EXT raises FormatError.
    0xD7: (8, "b8s", TYPE_EXT),    # TYPE_EXT raises FormatError.
    0xD8: (16, "b16s", TYPE_EXT),  # TYPE_EXT raises FormatError.
    0xD9: (1, _NO_FORMAT_USED, TYPE_RAW),
    0xDA: (2, ">H", TYPE_RAW),
    0xDB: (4, ">I", TYPE_RAW),
    0xDC: (2, ">H", TYPE_ARRAY),
    0xDD: (4, ">I", TYPE_ARRAY),
    0xDE: (2, ">H", TYPE_MAP),
    0xDF: (4, ">I", TYPE_MAP),
}


class Unpacker:
    """Streaming tmsgpack unpacker.

    Arguments:

    :param unpack_ctrl:
        Unpack control context.

    :param file_like:
        File-like object having `.read(n)` method.
        If specified, unpacker reads serialized data from it and :meth:`feed()` is not usable.

    :param buffer_size:
        Set the buffer_size.

    :param callable object_hook:
        When specified, it should be callable.
        Unpacker calls it with a dict argument after unpacking ydtpack map.

    :param callable list_hook:
        This will be removed soon.  obsolete

    Example of streaming deserialize from file-like object::

        unpacker = Unpacker(file_like)
        for o in unpacker:
            process(o)

    Example of streaming deserialize from socket::

        unpacker = Unpacker()
        while True:
            buf = sock.recv(1024**2)
            if not buf:
                break
            unpacker.feed(buf)
            for o in unpacker:
                process(o)

    Raises ``ExtraData`` when *packed* contains extra bytes.
    Raises ``OutOfData`` when *packed* is incomplete.
    Raises ``FormatError`` when *packed* is not valid ydtpack.
    Raises ``StackError`` when *packed* contains too nested.
    Other exceptions can be raised during unpacking.
    """

    def __init__(
        self,
        file_like=None,
        unpack_ctrl=None,
        buffer_size=0,
        object_hook=None,
        list_hook=None,
    ):
        if unpack_ctrl is None:
            raise ValueError("No unpack_ctrl supplied.")

        if file_like is None:
            self._feeding = True
        else:
            if not callable(file_like.read):
                raise TypeError("`file_like.read` must be callable")
            self.file_like = file_like
            self._feeding = False

        #: array of bytes fed.
        self._buffer = bytearray()
        #: Which position we currently reads
        self._buff_i = 0

        # When Unpacker is used as an iterable, between the calls to next(),
        # the buffer is not "consumed" completely, for efficiency sake.
        # Instead, it is done sloppily.  To make sure we raise BufferFull at
        # the correct moments, we have to keep track of how sloppy we were.
        # Furthermore, when the buffer is incomplete (that is: in the case
        # we raise an OutOfData) we need to rollback the buffer to the correct
        # state, which _buf_checkpoint records.
        self._buf_checkpoint = 0

        o = unpack_ctrl.options
        if buffer_size == 0:
            self._max_buffer_size = o.max_buffer_size
            self._read_size       = o.read_size
        else:
            self._max_buffer_size = self._read_size = buffer_size

        self._read_size = o.read_size
        self._raw = bool(o.raw)
        self._strict_map_key = bool(o.strict_map_key)
        self._unicode_errors = o.unicode_errors
        self._use_list = o.use_list
        self._object_as_pairs = o.object_as_pairs
        self._max_str_len   = o.max_str_len
        self._max_bin_len   = o.max_bin_len
        self._max_array_len = o.max_array_len
        self._max_map_len   = o.max_map_len

        self._list_hook = list_hook
        self._object_hook = object_hook

        self._stream_offset = 0

        if list_hook is not None and not callable(list_hook):
            raise TypeError("`list_hook` is not callable")
        if object_hook is not None and not callable(object_hook):
            raise TypeError("`object_hook` is not callable")

    def feed(self, next_bytes):
        assert self._feeding
        view = _get_data_from_buffer(next_bytes)
        if len(self._buffer) - self._buff_i + len(view) > self._max_buffer_size:
            raise BufferFull

        # Strip buffer before checkpoint before reading file.
        if self._buf_checkpoint > 0:
            del self._buffer[: self._buf_checkpoint]
            self._buff_i -= self._buf_checkpoint
            self._buf_checkpoint = 0

        # Use extend here: INPLACE_ADD += doesn't reliably typecast memoryview in jython
        self._buffer.extend(view)

    def _consume(self):
        """Gets rid of the used parts of the buffer."""
        self._stream_offset += self._buff_i - self._buf_checkpoint
        self._buf_checkpoint = self._buff_i

    def _got_extradata(self):
        return self._buff_i < len(self._buffer)

    def _get_extradata(self):
        return self._buffer[self._buff_i :]

    def read_bytes(self, n):
        ret = self._read(n, raise_outofdata=False)
        self._consume()
        return ret

    def _read(self, n, raise_outofdata=True):
        # (int) -> bytearray
        self._reserve(n, raise_outofdata=raise_outofdata)
        i = self._buff_i
        ret = self._buffer[i : i + n]
        self._buff_i = i + len(ret)
        return ret

    def _reserve(self, n, raise_outofdata=True):
        remain_bytes = len(self._buffer) - self._buff_i - n

        # Fast path: buffer has n bytes already
        if remain_bytes >= 0:
            return

        if self._feeding:
            self._buff_i = self._buf_checkpoint
            raise OutOfData

        # Strip buffer before checkpoint before reading file.
        if self._buf_checkpoint > 0:
            del self._buffer[: self._buf_checkpoint]
            self._buff_i -= self._buf_checkpoint
            self._buf_checkpoint = 0

        # Read from file
        remain_bytes = -remain_bytes
        if remain_bytes + len(self._buffer) > self._max_buffer_size:
            raise BufferFull
        while remain_bytes > 0:
            to_read_bytes = max(self._read_size, remain_bytes)
            read_data = self.file_like.read(to_read_bytes)
            if not read_data:
                break
            assert isinstance(read_data, bytes)
            self._buffer += read_data
            remain_bytes -= len(read_data)

        if len(self._buffer) < n + self._buff_i and raise_outofdata:
            self._buff_i = 0  # rollback
            raise OutOfData

    def _read_header(self):
        typ = TYPE_IMMEDIATE
        n = 0
        obj = None
        self._reserve(1)
        b = self._buffer[self._buff_i]
        self._buff_i += 1
        if b & 0b10000000 == 0:
            obj = b
        elif b & 0b11100000 == 0b11100000:
            obj = -1 - (b ^ 0xFF)
        elif b & 0b11100000 == 0b10100000:
            n = b & 0b00011111
            typ = TYPE_RAW
            if n > self._max_str_len:
                raise ValueError(f"{n} exceeds max_str_len({self._max_str_len})")
            obj = self._read(n)
        elif b & 0b11110000 == 0b10010000:
            n = b & 0b00001111
            typ = TYPE_ARRAY
            if n > self._max_array_len:
                raise ValueError(f"{n} exceeds max_array_len({self._max_array_len})")
        elif b & 0b11110000 == 0b10000000:
            n = b & 0b00001111
            typ = TYPE_MAP
            if n > self._max_map_len:
                raise ValueError(f"{n} exceeds max_map_len({self._max_map_len})")
        elif b == 0xc0:
            obj = None
        # elif b == 0xc1: pass # never used
        elif b == 0xc2:
            obj = False
        elif b == 0xc3:
            obj = True
        elif 0xc4 <= b <= 0xc6:
            size, fmt, typ = _MSGPACK_HEADERS[b]
            self._reserve(size)
            if len(fmt) > 0:
                n = struct.unpack_from(fmt, self._buffer, self._buff_i)[0]
            else:
                n = self._buffer[self._buff_i]
            self._buff_i += size
            if n > self._max_bin_len:
                raise ValueError(f"{n} exceeds max_bin_len({self._max_bin_len})")
            obj = self._read(n)
        # elif 0xc7 <= b <= 0xc9: # ext8..ext32 removed
        elif 0xca <= b <= 0xd3:
            size, fmt = _MSGPACK_HEADERS[b]
            self._reserve(size)
            if len(fmt) > 0:
                obj = struct.unpack_from(fmt, self._buffer, self._buff_i)[0]
            else:
                obj = self._buffer[self._buff_i]
            self._buff_i += size
        # elif 0xd4 <= b <= 0xd8: # fixext 1-16 removed
        elif 0xd9 <= b <= 0xdb:
            size, fmt, typ = _MSGPACK_HEADERS[b]
            self._reserve(size)
            if len(fmt) > 0:
                (n,) = struct.unpack_from(fmt, self._buffer, self._buff_i)
            else:
                n = self._buffer[self._buff_i]
            self._buff_i += size
            if n > self._max_str_len:
                raise ValueError(f"{n} exceeds max_str_len({self._max_str_len})")
            obj = self._read(n)
        elif 0xdc <= b <= 0xdd:
            size, fmt, typ = _MSGPACK_HEADERS[b]
            self._reserve(size)
            (n,) = struct.unpack_from(fmt, self._buffer, self._buff_i)
            self._buff_i += size
            if n > self._max_array_len:
                raise ValueError(f"{n} exceeds max_array_len({self._max_array_len})")
        elif 0xde <= b <= 0xdf:
            size, fmt, typ = _MSGPACK_HEADERS[b]
            self._reserve(size)
            (n,) = struct.unpack_from(fmt, self._buffer, self._buff_i)
            self._buff_i += size
            if n > self._max_map_len:
                raise ValueError(f"{n} exceeds max_map_len({self._max_map_len})")
        else:
            raise FormatError("Unknown header: 0x%x" % b)
        if typ == TYPE_EXT:
            raise FormatError("Ext header not supported: 0x%x" % b)

        return typ, n, obj

    def _unpack(self):
        typ, n, obj = self._read_header()

        # TODO should we eliminate the recursion?
        if typ == TYPE_ARRAY:
            ytype = self._unpack() # <= XXX
            ret = newlist_hint(n)
            for i in range(n):
                ret.append(self._unpack())
            if self._list_hook is not None:
                ret = self._list_hook(ret)
            # TODO is the interaction between `list_hook` and `use_list` ok?
            return ret if self._use_list else tuple(ret)
        if typ == TYPE_MAP:
            ytype = self._unpack() # <= XXX
            if self._object_as_pairs:
                ret = tuple((self._unpack(), self._unpack()) for _ in range(n))
            else:
                ret = {}
                for _ in range(n):
                    key = self._unpack()
                    if self._strict_map_key and type(key) not in (str, bytes):
                        raise ValueError("%s is not allowed for map key" % str(type(key)))
                    if type(key) is str:
                        key = sys.intern(key)
                    ret[key] = self._unpack()
                if self._object_hook is not None:
                    ret = self._object_hook(ret)
            return ret
        if typ == TYPE_RAW:
            if self._raw:
                obj = bytes(obj)
            else:
                obj = obj.decode("utf_8", self._unicode_errors)
            return obj
        if typ == TYPE_BIN:
            return bytes(obj)
        assert typ == TYPE_IMMEDIATE
        return obj

    def __iter__(self):
        return self

    def __next__(self):
        try:
            ret = self._unpack()
            self._consume()
            return ret
        except OutOfData:
            self._consume()
            raise StopIteration
        except RecursionError:
            raise StackError

    next = __next__

    def unpack(self):
        try:
            ret = self._unpack()
        except RecursionError:
            raise StackError
        self._consume()
        return ret

    def tell(self):
        return self._stream_offset


class Packer:
    """
    tmsgpack Packer

    Usage::

        packer = Packer()
        astream.write(packer.pack(a))
        astream.write(packer.pack(b))

    Packer's constructor has some keyword arguments:

    :param pack_ctrl:
        Pack control context.

    :param callable default:
        Convert user type to builtin type that Packer supports.
        See also simplejson's document.

    Example of streaming deserialize from file-like object::

        unpacker = Unpacker(file_like)
        for o in unpacker:
            process(o)

    Example of streaming deserialize from socket::

        unpacker = Unpacker()
        while True:
            buf = sock.recv(1024**2)
            if not buf:
                break
            unpacker.feed(buf)
            for o in unpacker:
                process(o)

    Raises ``ExtraData`` when *packed* contains extra bytes.
    Raises ``OutOfData`` when *packed* is incomplete.
    Raises ``FormatError`` when *packed* is not valid ydtpack.
    Raises ``StackError`` when *packed* contains too nested.
    Other exceptions can be raised during unpacking.
    """

    def __init__(
        self,
        pack_ctrl=None,
        default=None,
    ):
        if pack_ctrl is None:
           raise(ValueError("No pack_ctrl supplied."))

        o = pack_ctrl.options
        self._strict_types = o.strict_types
        self._use_float = o.use_single_float
        self._use_bin_type = o.use_bin_type
        self._buffer = StringIO()
        self._unicode_errors = o.unicode_errors
        self._sort_keys = o.sort_keys

        if default is not None:
            if not callable(default):
                raise TypeError("default must be callable")
        self._default = default

    def _pack(
        self,
        obj,
        nest_limit=DEFAULT_RECURSE_LIMIT,
        check=isinstance,
        check_type_strict=_check_type_strict,
    ):
        default_used = False
        if self._strict_types:
            check = check_type_strict
            list_types = list
        else:
            list_types = (list, tuple)
        while True:
            if nest_limit < 0:
                raise ValueError("recursion limit exceeded")
            if obj is None:
                return self._buffer.write(b"\xc0")
            if check(obj, bool):
                if obj:
                    return self._buffer.write(b"\xc3")
                return self._buffer.write(b"\xc2")
            if check(obj, int):
                if 0 <= obj < 0x80:
                    return self._buffer.write(struct.pack("B", obj))
                if -0x20 <= obj < 0:
                    return self._buffer.write(struct.pack("b", obj))
                if 0x80 <= obj <= 0xFF:
                    return self._buffer.write(struct.pack("BB", 0xCC, obj))
                if -0x80 <= obj < 0:
                    return self._buffer.write(struct.pack(">Bb", 0xD0, obj))
                if 0xFF < obj <= 0xFFFF:
                    return self._buffer.write(struct.pack(">BH", 0xCD, obj))
                if -0x8000 <= obj < -0x80:
                    return self._buffer.write(struct.pack(">Bh", 0xD1, obj))
                if 0xFFFF < obj <= 0xFFFFFFFF:
                    return self._buffer.write(struct.pack(">BI", 0xCE, obj))
                if -0x80000000 <= obj < -0x8000:
                    return self._buffer.write(struct.pack(">Bi", 0xD2, obj))
                if 0xFFFFFFFF < obj <= 0xFFFFFFFFFFFFFFFF:
                    return self._buffer.write(struct.pack(">BQ", 0xCF, obj))
                if -0x8000000000000000 <= obj < -0x80000000:
                    return self._buffer.write(struct.pack(">Bq", 0xD3, obj))
                if not default_used and self._default is not None:
                    obj = self._default(obj)
                    default_used = True
                    continue
                raise OverflowError("Integer value out of range")
            if check(obj, (bytes, bytearray)):
                n = len(obj)
                if n >= 2**32:
                    raise ValueError("%s is too large" % type(obj).__name__)
                self._pack_bin_header(n)
                return self._buffer.write(obj)
            if check(obj, str):
                obj = obj.encode("utf-8", self._unicode_errors)
                n = len(obj)
                if n >= 2**32:
                    raise ValueError("String is too large")
                self._pack_raw_header(n)
                return self._buffer.write(obj)
            if check(obj, memoryview):
                n = obj.nbytes
                if n >= 2**32:
                    raise ValueError("Memoryview is too large")
                self._pack_bin_header(n)
                return self._buffer.write(obj)
            if check(obj, float):
                if self._use_float:
                    return self._buffer.write(struct.pack(">Bf", 0xCA, obj))
                return self._buffer.write(struct.pack(">Bd", 0xCB, obj))
            if check(obj, list_types):
                n = len(obj)
                self._pack_array_header(n)
                self._pack(None, nest_limit - 1)   # <= XXX
                for i in range(n):
                    self._pack(obj[i], nest_limit - 1)
                return
            if check(obj, dict):
                _items = sorted(obj.items()) if self._sort_keys else obj.items()
                return self._pack_map_pairs(len(obj), None, _items, nest_limit - 1)

            if not default_used and self._default is not None:
                obj = self._default(obj)
                default_used = 1
                continue

            raise TypeError(f"Cannot serialize {obj!r}")

    def pack(self, obj):
        try:
            self._pack(obj)
        except:
            self._buffer = StringIO()  # force reset
            raise
        ret = self._buffer.getvalue()
        self._buffer = StringIO()
        return ret

    def pack_map_pairs(self, object_type, pairs):
        self._pack_map_pairs(len(pairs), object_type, pairs)
        ret = self._buffer.getvalue()
        self._buffer = StringIO()
        return ret

    def pack_array_header(self, n):
        if n >= 2**32:
            raise ValueError
        self._pack_array_header(n)
        ret = self._buffer.getvalue()
        self._buffer = StringIO()
        return ret

    def pack_map_header(self, n):
        if n >= 2**32:
            raise ValueError
        self._pack_map_header(n)
        ret = self._buffer.getvalue()
        self._buffer = StringIO()
        return ret

    def _pack_array_header(self, n):
        if n <= 0x0F:
            return self._buffer.write(struct.pack("B", 0x90 + n))
        if n <= 0xFFFF:
            return self._buffer.write(struct.pack(">BH", 0xDC, n))
        if n <= 0xFFFFFFFF:
            return self._buffer.write(struct.pack(">BI", 0xDD, n))
        raise ValueError("Array is too large")

    def _pack_map_header(self, n):
        if n <= 0x0F:
            return self._buffer.write(struct.pack("B", 0x80 + n))
        if n <= 0xFFFF:
            return self._buffer.write(struct.pack(">BH", 0xDE, n))
        if n <= 0xFFFFFFFF:
            return self._buffer.write(struct.pack(">BI", 0xDF, n))
        raise ValueError("Dict is too large")

    def _pack_map_pairs(self, n, object_type, pairs, nest_limit=DEFAULT_RECURSE_LIMIT):
        self._pack_map_header(n)
        self._pack(object_type, nest_limit - 1)
        for k, v in pairs:
            self._pack(k, nest_limit - 1)
            self._pack(v, nest_limit - 1)

    def _pack_raw_header(self, n):
        if n <= 0x1F:
            self._buffer.write(struct.pack("B", 0xA0 + n))
        elif self._use_bin_type and n <= 0xFF:
            self._buffer.write(struct.pack(">BB", 0xD9, n))
        elif n <= 0xFFFF:
            self._buffer.write(struct.pack(">BH", 0xDA, n))
        elif n <= 0xFFFFFFFF:
            self._buffer.write(struct.pack(">BI", 0xDB, n))
        else:
            raise ValueError("Raw is too large")

    def _pack_bin_header(self, n):
        if not self._use_bin_type:
            return self._pack_raw_header(n)
        elif n <= 0xFF:
            return self._buffer.write(struct.pack(">BB", 0xC4, n))
        elif n <= 0xFFFF:
            return self._buffer.write(struct.pack(">BH", 0xC5, n))
        elif n <= 0xFFFFFFFF:
            return self._buffer.write(struct.pack(">BI", 0xC6, n))
        else:
            raise ValueError("Bin is too large")

    def bytes(self):
        """Return internal buffer contents as bytes object"""
        return self._buffer.getvalue()

    def getbuffer(self):
        """Return view of internal buffer."""
        if USING_STRINGBUILDER:
            return memoryview(self.bytes())
        else:
            return self._buffer.getbuffer()
