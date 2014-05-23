#!/usr/bin/env python
import os
import time
import cffi
import locale
locale.setlocale(locale.LC_ALL, 'en_US')

ffi = cffi.FFI()
ffi.cdef("void start(void);")
ffi.cdef("int stop(void);")
ffi.cdef("void add_record(char *record, int length);")
lib = ffi.dlopen("test_cffi_locking.so")

RUNS = int(1e5)

NUM_GENERATIONS = 1000
DIGITS = len(str(RUNS))
FMT = "{0:0" + str(DIGITS) + "d}"
RECORD_FORMAT = 'x' * DIGITS + "\x003\x00put\x003\x00key\x005\x00value\x00"
RECORD_LENGTH = len(RECORD_FORMAT)


def write_to(target_lib, generation):
    record = FMT.format(generation) + RECORD_FORMAT[DIGITS:]
    target_lib.add_record(record, RECORD_LENGTH)
    return


def main(print_out=True, filename=None):
    lib.start()
    ts = time.time()
    n = 0
    while n < RUNS:
        write_to(lib, n)
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
    return ((1-(m/float(n)))*100, n-m)

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
