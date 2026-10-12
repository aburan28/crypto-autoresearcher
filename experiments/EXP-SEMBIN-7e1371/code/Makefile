# Build recipe for the two ctypes libraries of EXP-SEMBIN-7e1371.
# Requires libm4ri-dev (Ubuntu: apt-get install libm4ri-dev). The .so files
# are gitignored (*.so); rebuild them before running run_cells.py.
#
# M4RI_PREFIX selects an M4RI installation other than the system one, linked
# with an rpath so the same library is loaded at run time. libclosure needs a
# release with upstream commit 34b1b56 (M4RI issue #74, 2020-05-14), i.e.
# 20240729 or later: 0.0.20200125 (Ubuntu 24.04's libm4ri-dev) returned
# eliminations outside the row space at N = 44. Build it with
#   git clone https://github.com/malb/m4ri && cd m4ri && git checkout release-20240729
#   autoreconf -fi && ./configure --prefix=$PREFIX --disable-openmp && make && make check && make install
# then: make M4RI_PREFIX=$PREFIX. Every result records the library it loaded.
CC ?= gcc
CFLAGS ?= -O2 -Wall -fPIC -shared
M4RI_PREFIX ?=
ifneq ($(M4RI_PREFIX),)
M4RI_INC = -I$(M4RI_PREFIX)/include
M4RI_LIBS = -L$(M4RI_PREFIX)/lib -Wl,-rpath,$(M4RI_PREFIX)/lib -lm4ri
else
M4RI_INC =
M4RI_LIBS = -lm4ri
endif
all: libclosure.so libgf2ech.so libcountm2.so libcountchain.so
libclosure.so: closure.c
	$(CC) $(CFLAGS) $(M4RI_INC) closure.c -o $@ $(M4RI_LIBS)
libgf2ech.so: gf2_echelon.c
	$(CC) $(CFLAGS) gf2_echelon.c -o $@ -lm4ri
clean:
	rm -f libclosure.so libgf2ech.so libcountm2.so libcountchain.so
.PHONY: all clean
libcountm2.so: count_m2.c
	$(CC) $(CFLAGS) count_m2.c -o $@
libcountchain.so: count_chain.c
	$(CC) $(CFLAGS) count_chain.c -o $@
