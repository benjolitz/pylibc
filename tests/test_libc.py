import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from pylibc import mmap, munmap, ffi

if __name__ == "__main__":
    anonymous_map = mmap(size=1024)
    anonymous_map[0:10] = '1234567890'
    anonymous_map[100:110] = '0987654321'
    print ffi.string(ffi.cast('char *', anonymous_map + 100), 10)
    print ffi.string(ffi.cast('char *', anonymous_map - 0), 10)

    x = anonymous_map[:10]
    print type(x), x
    print anonymous_map._buffer[0:10]
    munmap(anonymous_map)
    print anonymous_map
