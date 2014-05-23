ARCH=64
CONST_FLAGS=
# -g -DDEBUG
CFLAGS=-c -Wall -I/usr/local/include -I/usr/local/mysql/include -I. -m$(ARCH) $(CONST_FLAGS)
UNAME_S := $(shell uname -s)
ifeq ($(UNAME_S),Linux)
    CCFLAGS += -D LINUX
endif
ifeq ($(UNAME_S),Darwin)
	CFLAGS+=-Wno-padded -Weverything -Wno-unused-parameter
endif



LDFLAGS=$(CONST_FLAGS)

all: test_cffi_locking.so test_mmap_sharing.so

clean:
	@rm -rf test_cffi_locking.so
	@rm -rf test_mmap_sharing.so
	@rm -rf *.o *.csv

test_cffi_locking.so: linked_list.o test_cffi_locking.o
	@$(CC) $(LDFLAGS) -shared -o test_cffi_locking.so linked_list.o test_cffi_locking.o

test_mmap_sharing.so: test_mmap_sharing.o
	@$(CC) $(LDFLAGS) -shared -o test_mmap_sharing.so linked_list.o test_mmap_sharing.o

test: clean all
	@for test in test_mmap_sharing test_cffi_locking; do \
	    echo $$test; \
	    python $$test.py; \
	    echo "" ; \
	done