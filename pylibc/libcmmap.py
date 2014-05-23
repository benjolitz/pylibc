from .api import ffi, _libc
import errno

MMAP_PROT_MODES = {
    'PROT_NONE': 0x00,    # [MC2] no permissions
    'PROT_READ': 0x01,    # [MC2] pages can be read
    'PROT_WRITE': 0x02,    # [MC2] pages can be written
    'PROT_EXEC': 0x04    # [MC2] pages can be executed
}
MMAP_FLAGS = {
    'MAP_ANON': 0x1000,
    'MAP_FILE': 0x0000,
    'MAP_FIXED': 0x0010,
    'MAP_HASSEMAPHORE': 0x0200,
    'MAP_PRIVATE': 0x0002,
    'MAP_SHARED': 0x0001,
    'MAP_NOCACHE': 0x0400,
}

CDATA_METHODS = \
    ['__add__', '__delitem__', '__eq__', '__float__',
     '__format__', '__ge__', '__getitem__', '__gt__', '__hash__', '__int__',
     '__iter__', '__le__', '__len__', '__long__', '__lt__', '__ne__',
     '__nonzero__', '__radd__', '__reduce__', '__reduce_ex__', '__repr__',
     '__rsub__', '__setitem__', '__sizeof__', '__sub__']


def spawn(methodName):
    def wrapper(self, *args, **kwargs):
        return getattr(self.pointer, methodName)(*args, **kwargs)
    return wrapper


def apply_cdata_delegation(cls):
    for method in CDATA_METHODS:
        if not hasattr(cls, method):
            setattr(cls, method, spawn(method))


class MMAPWrapper(object):
    __slots__ = ['pointer', 'fd', 'mode', 'flags', 'size', '_buffer']

    def __init__(self, pointer, fd, mode, flags, size):
        self.pointer = pointer
        self.fd, self.mode = fd, mode
        self.flags, self.size = flags, size
        self._buffer = None

    def __getattr__(self, name):
        if name not in MMAPWrapper.__slots__:
            return getattr(self.pointer, name)
        return object.__getattr__(self, name)

    def __getitem__(self, key):
        if self._buffer is None:
            self._buffer = ffi.buffer(self.pointer, self.size)
        if isinstance(key, slice):
            return self._buffer[key.start or 0:key.stop or self.size]
        return self._buffer[key]

    def __setitem__(self, key, value):
        if self._buffer is None:
            self._buffer = ffi.buffer(self.pointer, self.size)
        if isinstance(key, slice):
            self._buffer[key.start or 0:key.stop or self.size] = value
        else:
            self._buffer[key] = value

apply_cdata_delegation(MMAPWrapper)

MUNMAP_ERR_CODE = {
    errno.EINVAL: (
        "The addr parameter was not page aligned (i.e., a multiple of the page"
        " size) or"
        " the len parameter was negative or zero or"
        " some part of the region being unmapped is not part of the currently "
        "valid address space.")
}

MMAP_ERR_CODES = {
    errno.EACCES: (
        "The flag PROT_READ was specified as part of the prot "
        "argument and fd was not open for reading.  The flags MAP_SHARED and "
        "PROT_WRITE were specified as part of the flags and prot argument and "
        "fd was not open for writing."),
    errno.EBADF: "The fd argument is not a valid open file descriptor.",
    errno.EINVAL: (
        "MAP_FIXED was specified and the addr argument was not page aligned, "
        "or part of the desired address space resides out of the valid address"
        " space for a user process. Or flags does not include either "
        "MAP_PRIVATE or MAP_SHARED. Or The len argument was negative. Or "
        "the offset argument was not page-aligned based on the page size as "
        "returned by getpagesize(3)."),
    errno.ENODEV: (
        "MAP_ANON has not been specified and the file "
        "fd refers to does not support mapping."),
    errno.ENOMEM: (
        "MAP_FIXED was specified and the addr argument was not available. "
        "MAP_FIXED was specified and the address range specified exceeds the "
        "address space limit for the process.  MAP_ANON was specified and "
        "insufficient memory was available."),
    errno.ENXIO: "Addresses in the specified range are invalid for fd.",
    errno.EOVERFLOW: (
        "Addresses in the specified range exceed "
        "the maximum offset set for fd.")
}


def mmap(fd=None, mode=None, flags=None, size=None):
    if size is None:
        size = ffi.sizeof('int')
    if mode is None:
        mode = MMAP_PROT_MODES['PROT_READ'] | MMAP_PROT_MODES['PROT_WRITE']
    if fd is None:
        fd = -1
    if flags is None:
        flags = MMAP_FLAGS['MAP_SHARED']
        if fd == -1:
            flags |= MMAP_FLAGS['MAP_ANON']

    ptr = _libc.mmap(ffi.NULL, size, mode, flags, fd, 0)
    if int(ffi.cast('int', ptr)) == -1:
        raise MemoryError(MMAP_ERR_CODES[ffi.errno])
    return MMAPWrapper(ptr, fd, mode, flags, size)


def munmap(mmap_obj):
    if mmap_obj.pointer == ffi.NULL:
        raise MemoryError("already deallocated")
    result = _libc.munmap(mmap_obj.pointer, mmap_obj.size)
    if result == -1:
        raise MemoryError(MUNMAP_ERR_CODE[ffi.errno])
    mmap_obj.pointer = ffi.NULL
    return mmap_obj


def madvise():
    raise NotImplementedError


def mlockall():
    raise NotImplementedError


def munlockall():
    raise NotImplementedError


def mlock():
    raise NotImplementedError


def msync():
    raise NotImplementedError


def munlock():
    raise NotImplementedError
