/*
 * MessagePack packing routine template
 *
 * Copyright (C) 2008-2010 FURUHASHI Sadayuki
 *
 *    Licensed under the Apache License, Version 2.0 (the "License");
 *    you may not use this file except in compliance with the License.
 *    You may obtain a copy of the License at
 *
 *        http://www.apache.org/licenses/LICENSE-2.0
 *
 *    Unless required by applicable law or agreed to in writing, software
 *    distributed under the License is distributed on an "AS IS" BASIS,
 *    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *    See the License for the specific language governing permissions and
 *    limitations under the License.
 */

#if defined(__LITTLE_ENDIAN__)
#define TAKE8_8(d)  ((uint8_t*)&d)[0]
#define TAKE8_16(d) ((uint8_t*)&d)[0]
#define TAKE8_32(d) ((uint8_t*)&d)[0]
#define TAKE8_64(d) ((uint8_t*)&d)[0]
#elif defined(__BIG_ENDIAN__)
#define TAKE8_8(d)  ((uint8_t*)&d)[0]
#define TAKE8_16(d) ((uint8_t*)&d)[1]
#define TAKE8_32(d) ((uint8_t*)&d)[3]
#define TAKE8_64(d) ((uint8_t*)&d)[7]
#endif

#ifndef ydtpack_pack_append_buffer
#error ydtpack_pack_append_buffer callback is not defined
#endif


/*
 * Integer
 */

#define ydtpack_pack_real_uint8(x, d) \
do { \
    if(d < (1<<7)) { \
        /* fixnum */ \
        ydtpack_pack_append_buffer(x, &TAKE8_8(d), 1); \
    } else { \
        /* unsigned 8 */ \
        unsigned char buf[2] = {0xcc, TAKE8_8(d)}; \
        ydtpack_pack_append_buffer(x, buf, 2); \
    } \
} while(0)

#define ydtpack_pack_real_uint16(x, d) \
do { \
    if(d < (1<<7)) { \
        /* fixnum */ \
        ydtpack_pack_append_buffer(x, &TAKE8_16(d), 1); \
    } else if(d < (1<<8)) { \
        /* unsigned 8 */ \
        unsigned char buf[2] = {0xcc, TAKE8_16(d)}; \
        ydtpack_pack_append_buffer(x, buf, 2); \
    } else { \
        /* unsigned 16 */ \
        unsigned char buf[3]; \
        buf[0] = 0xcd; _ydtpack_store16(&buf[1], (uint16_t)d); \
        ydtpack_pack_append_buffer(x, buf, 3); \
    } \
} while(0)

#define ydtpack_pack_real_uint32(x, d) \
do { \
    if(d < (1<<8)) { \
        if(d < (1<<7)) { \
            /* fixnum */ \
            ydtpack_pack_append_buffer(x, &TAKE8_32(d), 1); \
        } else { \
            /* unsigned 8 */ \
            unsigned char buf[2] = {0xcc, TAKE8_32(d)}; \
            ydtpack_pack_append_buffer(x, buf, 2); \
        } \
    } else { \
        if(d < (1<<16)) { \
            /* unsigned 16 */ \
            unsigned char buf[3]; \
            buf[0] = 0xcd; _ydtpack_store16(&buf[1], (uint16_t)d); \
            ydtpack_pack_append_buffer(x, buf, 3); \
        } else { \
            /* unsigned 32 */ \
            unsigned char buf[5]; \
            buf[0] = 0xce; _ydtpack_store32(&buf[1], (uint32_t)d); \
            ydtpack_pack_append_buffer(x, buf, 5); \
        } \
    } \
} while(0)

#define ydtpack_pack_real_uint64(x, d) \
do { \
    if(d < (1ULL<<8)) { \
        if(d < (1ULL<<7)) { \
            /* fixnum */ \
            ydtpack_pack_append_buffer(x, &TAKE8_64(d), 1); \
        } else { \
            /* unsigned 8 */ \
            unsigned char buf[2] = {0xcc, TAKE8_64(d)}; \
            ydtpack_pack_append_buffer(x, buf, 2); \
        } \
    } else { \
        if(d < (1ULL<<16)) { \
            /* unsigned 16 */ \
            unsigned char buf[3]; \
            buf[0] = 0xcd; _ydtpack_store16(&buf[1], (uint16_t)d); \
            ydtpack_pack_append_buffer(x, buf, 3); \
        } else if(d < (1ULL<<32)) { \
            /* unsigned 32 */ \
            unsigned char buf[5]; \
            buf[0] = 0xce; _ydtpack_store32(&buf[1], (uint32_t)d); \
            ydtpack_pack_append_buffer(x, buf, 5); \
        } else { \
            /* unsigned 64 */ \
            unsigned char buf[9]; \
            buf[0] = 0xcf; _ydtpack_store64(&buf[1], d); \
            ydtpack_pack_append_buffer(x, buf, 9); \
        } \
    } \
} while(0)

#define ydtpack_pack_real_int8(x, d) \
do { \
    if(d < -(1<<5)) { \
        /* signed 8 */ \
        unsigned char buf[2] = {0xd0, TAKE8_8(d)}; \
        ydtpack_pack_append_buffer(x, buf, 2); \
    } else { \
        /* fixnum */ \
        ydtpack_pack_append_buffer(x, &TAKE8_8(d), 1); \
    } \
} while(0)

#define ydtpack_pack_real_int16(x, d) \
do { \
    if(d < -(1<<5)) { \
        if(d < -(1<<7)) { \
            /* signed 16 */ \
            unsigned char buf[3]; \
            buf[0] = 0xd1; _ydtpack_store16(&buf[1], (int16_t)d); \
            ydtpack_pack_append_buffer(x, buf, 3); \
        } else { \
            /* signed 8 */ \
            unsigned char buf[2] = {0xd0, TAKE8_16(d)}; \
            ydtpack_pack_append_buffer(x, buf, 2); \
        } \
    } else if(d < (1<<7)) { \
        /* fixnum */ \
        ydtpack_pack_append_buffer(x, &TAKE8_16(d), 1); \
    } else { \
        if(d < (1<<8)) { \
            /* unsigned 8 */ \
            unsigned char buf[2] = {0xcc, TAKE8_16(d)}; \
            ydtpack_pack_append_buffer(x, buf, 2); \
        } else { \
            /* unsigned 16 */ \
            unsigned char buf[3]; \
            buf[0] = 0xcd; _ydtpack_store16(&buf[1], (uint16_t)d); \
            ydtpack_pack_append_buffer(x, buf, 3); \
        } \
    } \
} while(0)

#define ydtpack_pack_real_int32(x, d) \
do { \
    if(d < -(1<<5)) { \
        if(d < -(1<<15)) { \
            /* signed 32 */ \
            unsigned char buf[5]; \
            buf[0] = 0xd2; _ydtpack_store32(&buf[1], (int32_t)d); \
            ydtpack_pack_append_buffer(x, buf, 5); \
        } else if(d < -(1<<7)) { \
            /* signed 16 */ \
            unsigned char buf[3]; \
            buf[0] = 0xd1; _ydtpack_store16(&buf[1], (int16_t)d); \
            ydtpack_pack_append_buffer(x, buf, 3); \
        } else { \
            /* signed 8 */ \
            unsigned char buf[2] = {0xd0, TAKE8_32(d)}; \
            ydtpack_pack_append_buffer(x, buf, 2); \
        } \
    } else if(d < (1<<7)) { \
        /* fixnum */ \
        ydtpack_pack_append_buffer(x, &TAKE8_32(d), 1); \
    } else { \
        if(d < (1<<8)) { \
            /* unsigned 8 */ \
            unsigned char buf[2] = {0xcc, TAKE8_32(d)}; \
            ydtpack_pack_append_buffer(x, buf, 2); \
        } else if(d < (1<<16)) { \
            /* unsigned 16 */ \
            unsigned char buf[3]; \
            buf[0] = 0xcd; _ydtpack_store16(&buf[1], (uint16_t)d); \
            ydtpack_pack_append_buffer(x, buf, 3); \
        } else { \
            /* unsigned 32 */ \
            unsigned char buf[5]; \
            buf[0] = 0xce; _ydtpack_store32(&buf[1], (uint32_t)d); \
            ydtpack_pack_append_buffer(x, buf, 5); \
        } \
    } \
} while(0)

#define ydtpack_pack_real_int64(x, d) \
do { \
    if(d < -(1LL<<5)) { \
        if(d < -(1LL<<15)) { \
            if(d < -(1LL<<31)) { \
                /* signed 64 */ \
                unsigned char buf[9]; \
                buf[0] = 0xd3; _ydtpack_store64(&buf[1], d); \
                ydtpack_pack_append_buffer(x, buf, 9); \
            } else { \
                /* signed 32 */ \
                unsigned char buf[5]; \
                buf[0] = 0xd2; _ydtpack_store32(&buf[1], (int32_t)d); \
                ydtpack_pack_append_buffer(x, buf, 5); \
            } \
        } else { \
            if(d < -(1<<7)) { \
                /* signed 16 */ \
                unsigned char buf[3]; \
                buf[0] = 0xd1; _ydtpack_store16(&buf[1], (int16_t)d); \
                ydtpack_pack_append_buffer(x, buf, 3); \
            } else { \
                /* signed 8 */ \
                unsigned char buf[2] = {0xd0, TAKE8_64(d)}; \
                ydtpack_pack_append_buffer(x, buf, 2); \
            } \
        } \
    } else if(d < (1<<7)) { \
        /* fixnum */ \
        ydtpack_pack_append_buffer(x, &TAKE8_64(d), 1); \
    } else { \
        if(d < (1LL<<16)) { \
            if(d < (1<<8)) { \
                /* unsigned 8 */ \
                unsigned char buf[2] = {0xcc, TAKE8_64(d)}; \
                ydtpack_pack_append_buffer(x, buf, 2); \
            } else { \
                /* unsigned 16 */ \
                unsigned char buf[3]; \
                buf[0] = 0xcd; _ydtpack_store16(&buf[1], (uint16_t)d); \
                ydtpack_pack_append_buffer(x, buf, 3); \
            } \
        } else { \
            if(d < (1LL<<32)) { \
                /* unsigned 32 */ \
                unsigned char buf[5]; \
                buf[0] = 0xce; _ydtpack_store32(&buf[1], (uint32_t)d); \
                ydtpack_pack_append_buffer(x, buf, 5); \
            } else { \
                /* unsigned 64 */ \
                unsigned char buf[9]; \
                buf[0] = 0xcf; _ydtpack_store64(&buf[1], d); \
                ydtpack_pack_append_buffer(x, buf, 9); \
            } \
        } \
    } \
} while(0)


static inline int ydtpack_pack_uint8(ydtpack_packer* x, uint8_t d)
{
    ydtpack_pack_real_uint8(x, d);
}

static inline int ydtpack_pack_uint16(ydtpack_packer* x, uint16_t d)
{
    ydtpack_pack_real_uint16(x, d);
}

static inline int ydtpack_pack_uint32(ydtpack_packer* x, uint32_t d)
{
    ydtpack_pack_real_uint32(x, d);
}

static inline int ydtpack_pack_uint64(ydtpack_packer* x, uint64_t d)
{
    ydtpack_pack_real_uint64(x, d);
}

static inline int ydtpack_pack_int8(ydtpack_packer* x, int8_t d)
{
    ydtpack_pack_real_int8(x, d);
}

static inline int ydtpack_pack_int16(ydtpack_packer* x, int16_t d)
{
    ydtpack_pack_real_int16(x, d);
}

static inline int ydtpack_pack_int32(ydtpack_packer* x, int32_t d)
{
    ydtpack_pack_real_int32(x, d);
}

static inline int ydtpack_pack_int64(ydtpack_packer* x, int64_t d)
{
    ydtpack_pack_real_int64(x, d);
}


//#ifdef ydtpack_pack_inline_func_cint

static inline int ydtpack_pack_short(ydtpack_packer* x, short d)
{
#if defined(SIZEOF_SHORT)
#if SIZEOF_SHORT == 2
    ydtpack_pack_real_int16(x, d);
#elif SIZEOF_SHORT == 4
    ydtpack_pack_real_int32(x, d);
#else
    ydtpack_pack_real_int64(x, d);
#endif

#elif defined(SHRT_MAX)
#if SHRT_MAX == 0x7fff
    ydtpack_pack_real_int16(x, d);
#elif SHRT_MAX == 0x7fffffff
    ydtpack_pack_real_int32(x, d);
#else
    ydtpack_pack_real_int64(x, d);
#endif

#else
if(sizeof(short) == 2) {
    ydtpack_pack_real_int16(x, d);
} else if(sizeof(short) == 4) {
    ydtpack_pack_real_int32(x, d);
} else {
    ydtpack_pack_real_int64(x, d);
}
#endif
}

static inline int ydtpack_pack_int(ydtpack_packer* x, int d)
{
#if defined(SIZEOF_INT)
#if SIZEOF_INT == 2
    ydtpack_pack_real_int16(x, d);
#elif SIZEOF_INT == 4
    ydtpack_pack_real_int32(x, d);
#else
    ydtpack_pack_real_int64(x, d);
#endif

#elif defined(INT_MAX)
#if INT_MAX == 0x7fff
    ydtpack_pack_real_int16(x, d);
#elif INT_MAX == 0x7fffffff
    ydtpack_pack_real_int32(x, d);
#else
    ydtpack_pack_real_int64(x, d);
#endif

#else
if(sizeof(int) == 2) {
    ydtpack_pack_real_int16(x, d);
} else if(sizeof(int) == 4) {
    ydtpack_pack_real_int32(x, d);
} else {
    ydtpack_pack_real_int64(x, d);
}
#endif
}

static inline int ydtpack_pack_long(ydtpack_packer* x, long d)
{
#if defined(SIZEOF_LONG)
#if SIZEOF_LONG == 2
    ydtpack_pack_real_int16(x, d);
#elif SIZEOF_LONG == 4
    ydtpack_pack_real_int32(x, d);
#else
    ydtpack_pack_real_int64(x, d);
#endif

#elif defined(LONG_MAX)
#if LONG_MAX == 0x7fffL
    ydtpack_pack_real_int16(x, d);
#elif LONG_MAX == 0x7fffffffL
    ydtpack_pack_real_int32(x, d);
#else
    ydtpack_pack_real_int64(x, d);
#endif

#else
if(sizeof(long) == 2) {
    ydtpack_pack_real_int16(x, d);
} else if(sizeof(long) == 4) {
    ydtpack_pack_real_int32(x, d);
} else {
    ydtpack_pack_real_int64(x, d);
}
#endif
}

static inline int ydtpack_pack_long_long(ydtpack_packer* x, long long d)
{
#if defined(SIZEOF_LONG_LONG)
#if SIZEOF_LONG_LONG == 2
    ydtpack_pack_real_int16(x, d);
#elif SIZEOF_LONG_LONG == 4
    ydtpack_pack_real_int32(x, d);
#else
    ydtpack_pack_real_int64(x, d);
#endif

#elif defined(LLONG_MAX)
#if LLONG_MAX == 0x7fffL
    ydtpack_pack_real_int16(x, d);
#elif LLONG_MAX == 0x7fffffffL
    ydtpack_pack_real_int32(x, d);
#else
    ydtpack_pack_real_int64(x, d);
#endif

#else
if(sizeof(long long) == 2) {
    ydtpack_pack_real_int16(x, d);
} else if(sizeof(long long) == 4) {
    ydtpack_pack_real_int32(x, d);
} else {
    ydtpack_pack_real_int64(x, d);
}
#endif
}

static inline int ydtpack_pack_unsigned_short(ydtpack_packer* x, unsigned short d)
{
#if defined(SIZEOF_SHORT)
#if SIZEOF_SHORT == 2
    ydtpack_pack_real_uint16(x, d);
#elif SIZEOF_SHORT == 4
    ydtpack_pack_real_uint32(x, d);
#else
    ydtpack_pack_real_uint64(x, d);
#endif

#elif defined(USHRT_MAX)
#if USHRT_MAX == 0xffffU
    ydtpack_pack_real_uint16(x, d);
#elif USHRT_MAX == 0xffffffffU
    ydtpack_pack_real_uint32(x, d);
#else
    ydtpack_pack_real_uint64(x, d);
#endif

#else
if(sizeof(unsigned short) == 2) {
    ydtpack_pack_real_uint16(x, d);
} else if(sizeof(unsigned short) == 4) {
    ydtpack_pack_real_uint32(x, d);
} else {
    ydtpack_pack_real_uint64(x, d);
}
#endif
}

static inline int ydtpack_pack_unsigned_int(ydtpack_packer* x, unsigned int d)
{
#if defined(SIZEOF_INT)
#if SIZEOF_INT == 2
    ydtpack_pack_real_uint16(x, d);
#elif SIZEOF_INT == 4
    ydtpack_pack_real_uint32(x, d);
#else
    ydtpack_pack_real_uint64(x, d);
#endif

#elif defined(UINT_MAX)
#if UINT_MAX == 0xffffU
    ydtpack_pack_real_uint16(x, d);
#elif UINT_MAX == 0xffffffffU
    ydtpack_pack_real_uint32(x, d);
#else
    ydtpack_pack_real_uint64(x, d);
#endif

#else
if(sizeof(unsigned int) == 2) {
    ydtpack_pack_real_uint16(x, d);
} else if(sizeof(unsigned int) == 4) {
    ydtpack_pack_real_uint32(x, d);
} else {
    ydtpack_pack_real_uint64(x, d);
}
#endif
}

static inline int ydtpack_pack_unsigned_long(ydtpack_packer* x, unsigned long d)
{
#if defined(SIZEOF_LONG)
#if SIZEOF_LONG == 2
    ydtpack_pack_real_uint16(x, d);
#elif SIZEOF_LONG == 4
    ydtpack_pack_real_uint32(x, d);
#else
    ydtpack_pack_real_uint64(x, d);
#endif

#elif defined(ULONG_MAX)
#if ULONG_MAX == 0xffffUL
    ydtpack_pack_real_uint16(x, d);
#elif ULONG_MAX == 0xffffffffUL
    ydtpack_pack_real_uint32(x, d);
#else
    ydtpack_pack_real_uint64(x, d);
#endif

#else
if(sizeof(unsigned long) == 2) {
    ydtpack_pack_real_uint16(x, d);
} else if(sizeof(unsigned long) == 4) {
    ydtpack_pack_real_uint32(x, d);
} else {
    ydtpack_pack_real_uint64(x, d);
}
#endif
}

static inline int ydtpack_pack_unsigned_long_long(ydtpack_packer* x, unsigned long long d)
{
#if defined(SIZEOF_LONG_LONG)
#if SIZEOF_LONG_LONG == 2
    ydtpack_pack_real_uint16(x, d);
#elif SIZEOF_LONG_LONG == 4
    ydtpack_pack_real_uint32(x, d);
#else
    ydtpack_pack_real_uint64(x, d);
#endif

#elif defined(ULLONG_MAX)
#if ULLONG_MAX == 0xffffUL
    ydtpack_pack_real_uint16(x, d);
#elif ULLONG_MAX == 0xffffffffUL
    ydtpack_pack_real_uint32(x, d);
#else
    ydtpack_pack_real_uint64(x, d);
#endif

#else
if(sizeof(unsigned long long) == 2) {
    ydtpack_pack_real_uint16(x, d);
} else if(sizeof(unsigned long long) == 4) {
    ydtpack_pack_real_uint32(x, d);
} else {
    ydtpack_pack_real_uint64(x, d);
}
#endif
}

//#undef ydtpack_pack_inline_func_cint
//#endif



/*
 * Float
 */

static inline int ydtpack_pack_float(ydtpack_packer* x, float d)
{
    unsigned char buf[5];
    buf[0] = 0xca;

#if PY_VERSION_HEX >= 0x030B00A7
    PyFloat_Pack4(d, (char *)&buf[1], 0);
#else
    _PyFloat_Pack4(d, &buf[1], 0);
#endif
    ydtpack_pack_append_buffer(x, buf, 5);
}

static inline int ydtpack_pack_double(ydtpack_packer* x, double d)
{
    unsigned char buf[9];
    buf[0] = 0xcb;
#if PY_VERSION_HEX >= 0x030B00A7
    PyFloat_Pack8(d, (char *)&buf[1], 0);
#else
    _PyFloat_Pack8(d, &buf[1], 0);
#endif
    ydtpack_pack_append_buffer(x, buf, 9);
}


/*
 * Nil
 */

static inline int ydtpack_pack_nil(ydtpack_packer* x)
{
    static const unsigned char d = 0xc0;
    ydtpack_pack_append_buffer(x, &d, 1);
}


/*
 * Boolean
 */

static inline int ydtpack_pack_true(ydtpack_packer* x)
{
    static const unsigned char d = 0xc3;
    ydtpack_pack_append_buffer(x, &d, 1);
}

static inline int ydtpack_pack_false(ydtpack_packer* x)
{
    static const unsigned char d = 0xc2;
    ydtpack_pack_append_buffer(x, &d, 1);
}


/*
 * Array
 */

static inline int ydtpack_pack_array(ydtpack_packer* x, unsigned int n)
{
    if(n < 16) {
        unsigned char d = 0x90 | n;
        ydtpack_pack_append_buffer(x, &d, 1);
    } else if(n < 65536) {
        unsigned char buf[3];
        buf[0] = 0xdc; _ydtpack_store16(&buf[1], (uint16_t)n);
        ydtpack_pack_append_buffer(x, buf, 3);
    } else {
        unsigned char buf[5];
        buf[0] = 0xdd; _ydtpack_store32(&buf[1], (uint32_t)n);
        ydtpack_pack_append_buffer(x, buf, 5);
    }
}


/*
 * Map
 */

static inline int ydtpack_pack_map(ydtpack_packer* x, unsigned int n)
{
    if(n < 16) {
        unsigned char d = 0x80 | n;
        ydtpack_pack_append_buffer(x, &TAKE8_8(d), 1);
    } else if(n < 65536) {
        unsigned char buf[3];
        buf[0] = 0xde; _ydtpack_store16(&buf[1], (uint16_t)n);
        ydtpack_pack_append_buffer(x, buf, 3);
    } else {
        unsigned char buf[5];
        buf[0] = 0xdf; _ydtpack_store32(&buf[1], (uint32_t)n);
        ydtpack_pack_append_buffer(x, buf, 5);
    }
}


/*
 * Raw
 */

static inline int ydtpack_pack_raw(ydtpack_packer* x, size_t l)
{
    if (l < 32) {
        unsigned char d = 0xa0 | (uint8_t)l;
        ydtpack_pack_append_buffer(x, &TAKE8_8(d), 1);
    } else if (x->use_bin_type && l < 256) {  // str8 is new format introduced with bin.
        unsigned char buf[2] = {0xd9, (uint8_t)l};
        ydtpack_pack_append_buffer(x, buf, 2);
    } else if (l < 65536) {
        unsigned char buf[3];
        buf[0] = 0xda; _ydtpack_store16(&buf[1], (uint16_t)l);
        ydtpack_pack_append_buffer(x, buf, 3);
    } else {
        unsigned char buf[5];
        buf[0] = 0xdb; _ydtpack_store32(&buf[1], (uint32_t)l);
        ydtpack_pack_append_buffer(x, buf, 5);
    }
}

/*
 * bin
 */
static inline int ydtpack_pack_bin(ydtpack_packer *x, size_t l)
{
    if (!x->use_bin_type) {
        return ydtpack_pack_raw(x, l);
    }
    if (l < 256) {
        unsigned char buf[2] = {0xc4, (unsigned char)l};
        ydtpack_pack_append_buffer(x, buf, 2);
    } else if (l < 65536) {
        unsigned char buf[3] = {0xc5};
        _ydtpack_store16(&buf[1], (uint16_t)l);
        ydtpack_pack_append_buffer(x, buf, 3);
    } else {
        unsigned char buf[5] = {0xc6};
        _ydtpack_store32(&buf[1], (uint32_t)l);
        ydtpack_pack_append_buffer(x, buf, 5);
    }
}

static inline int ydtpack_pack_raw_body(ydtpack_packer* x, const void* b, size_t l)
{
    if (l > 0) ydtpack_pack_append_buffer(x, (const unsigned char*)b, l);
    return 0;
}

#undef ydtpack_pack_append_buffer

#undef TAKE8_8
#undef TAKE8_16
#undef TAKE8_32
#undef TAKE8_64

#undef ydtpack_pack_real_uint8
#undef ydtpack_pack_real_uint16
#undef ydtpack_pack_real_uint32
#undef ydtpack_pack_real_uint64
#undef ydtpack_pack_real_int8
#undef ydtpack_pack_real_int16
#undef ydtpack_pack_real_int32
#undef ydtpack_pack_real_int64
