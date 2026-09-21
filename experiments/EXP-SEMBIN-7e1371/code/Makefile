# Build recipe for the two ctypes libraries of EXP-SEMBIN-7e1371.
# Requires libm4ri-dev (Ubuntu: apt-get install libm4ri-dev). The .so files
# are gitignored (*.so); rebuild them before running run_cells.py.
CC ?= gcc
CFLAGS ?= -O2 -Wall -fPIC -shared
all: libclosure.so libgf2ech.so libcountm2.so libcountchain.so
libclosure.so: closure.c
	$(CC) $(CFLAGS) closure.c -o $@ -lm4ri
libgf2ech.so: gf2_echelon.c
	$(CC) $(CFLAGS) gf2_echelon.c -o $@ -lm4ri
clean:
	rm -f libclosure.so libgf2ech.so libcountm2.so libcountchain.so
.PHONY: all clean
libcountm2.so: count_m2.c
	$(CC) $(CFLAGS) count_m2.c -o $@
libcountchain.so: count_chain.c
	$(CC) $(CFLAGS) count_chain.c -o $@
