#!/usr/bin/env python
import time
import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import locale
locale.setlocale(locale.LC_ALL, 'en_US')

import pylibc

import cffi

RUNS = int(1e5)

DIGITS = len(str(RUNS))
FMT = "{0:0" + str(DIGITS) + "d}"
RECORD_FORMAT = 'x' * DIGITS + "\x003\x00put\x003\x00key\x005\x00value\x00"
RECORD_LENGTH = len(RECORD_FORMAT)
NUM_GENERATIONS = 2**9 / RECORD_LENGTH

ffi = cffi.FFI()
ffi.cdef("void link_mmap(void *mmap, int mmap_size, int record_size);")
ffi.cdef("void start(void);")
ffi.cdef("int stop(void);")

lib = ffi.dlopen('test_mmap_sharing.so')


def write_to(target_memory_mapping, generation):
    offset = (generation % NUM_GENERATIONS)*RECORD_LENGTH
    try:
        while int(
                target_memory_mapping[offset:offset+RECORD_LENGTH][:3]
                or 0) != 0:
            # busy wait until the C thread marks the generation occupying this
            # space as "dead"
            # prone to locking!
            pass
    except ValueError:
        # special case when the space is just a bunch of binary zeroes
        # ('\x00\x00\x00')
        pass
    record = FMT.format(generation) + RECORD_FORMAT[DIGITS:]
    target_memory_mapping[offset:offset+RECORD_LENGTH] = \
        record
    return


def main(print_out=True, filename=None):
    anonymous_map = pylibc.mmap(size=RECORD_LENGTH*NUM_GENERATIONS)

    lib.link_mmap(anonymous_map.pointer, anonymous_map.size, RECORD_LENGTH)

    lib.start()
    ts = time.time()
    n = 0
    while n < RUNS:
        write_to(anonymous_map, n)
        n += 1
    tend = time.time()
    m = lib.stop()
    if print_out:
        print "Did {0} runs in {1} seconds. Rate: {2}".format(
            n, tend - ts, locale.format("%f", RUNS/(tend - ts), grouping=True))
        print "Read {0} distinct records".format(m)
        print "Data Loss {0:.2f}%, {1} entries missing".format(
            (1-(m/float(n)))*100, n-m)
    if filename is not None:
        if not os.path.exists(filename):
            with open(filename, 'w') as fh:
                fh.write("Data Loss %, entries missing,\n")
        with open(filename, 'a+') as fh:
            fh.write("{0:.2f}, {1},\n".format((1-(m/float(n)))*100, n-m))
    return ((1-(m/float(n)))*100, n-m,)

if __name__ == "__main__":
    try:
        import __pypy__
        __pypy__
    except ImportError:
        pass
    else:
        for x in xrange(0, 20):
            main(False)
    datas = []
    for x in xrange(14):
        datas.append(main(False, __file__+'.csv'))
    try:
        import statistics
    except ImportError:
        try:
            import backports.statistics as statistics
        except ImportError:
            print(
                "Need a statistics module, via Py3.4 or "
                "backports.statistics to get stdev and means!")
        print("Lost requests: {1:.3f} ± {0:.3f}".format(
            statistics.stdev([x[1] for x in datas]),
            statistics.mean([x[1] for x in datas])))
        print("Lost percentage (%): {1:.3f} ± {0:.3f}".format(
            100*statistics.stdev([x[0] for x in datas]),
            100*statistics.mean([x[0] for x in datas])))
    main(True)
