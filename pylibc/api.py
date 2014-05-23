import cffi
# monkey patch cffi to return itself on cdef


def return_self(func):
    def wrapper(self, *args):
        func(self, *args)
        return self
    return wrapper

cffi.FFI.cdef = return_self(cffi.FFI.cdef)

ffi = cffi.FFI()
ffi.cdef("""
//implemented
void *mmap(void *addr, size_t len, int prot, int flags, int fd, size_t offset);
int munmap(void *, size_t);

//unimplemented
int mlockall(int);
int munlockall(void);

int mlock(const void *, size_t);
int msync(void *, size_t, int);

int munlock(const void *, size_t);

int madvise(void *, size_t, int);
""")

_libc = ffi.dlopen(None)
