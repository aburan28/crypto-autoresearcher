# Build recipe for the two ctypes libraries of EXP-SEMBIN-c2c312.
# Requires libm4ri-dev (Ubuntu: apt-get install libm4ri-dev). The .so files
# are gitignored (*.so); rebuild them before running run_cells.py.
CC ?= gcc
CFLAGS ?= -O2 -Wall -fPIC -shared
all: libclosure.so libgf2ech.so
libclosure.so: closure.c
	$(CC) $(CFLAGS) closure.c -o $@ -lm4ri
libgf2ech.so: gf2_echelon.c
	$(CC) $(CFLAGS) gf2_echelon.c -o $@ -lm4ri
clean:
	rm -f libclosure.so libgf2ech.so
.PHONY: all clean
