# FreeLIP 1.0 host-header compatibility replay

**Frozen:** 2026-10-23 UTC, after the first replay failed during compilation and before any curve-order call. This is an additive follow-up to `PROTOCOL.md`. The first run and its failure record remain unchanged.

## Observed reason for follow-up

The first build failed because the archival `lip.c` includes `<malloc.h>`, absent from this macOS host. Its immutable failure is `runs/freelip-20261023T2007Z/failure.json`; zero cases ran. This is a portability issue, not evidence about a curve or the historical software.

## Single compatibility change

The launcher may generate a temporary header named `malloc.h` containing exactly `#include <stdlib.h>\n`, then add its temporary build directory to the compiler include path. The archival `lip.c` and `lip.h` must remain byte-for-byte identical to the tarball. All other source, compiler options, 25 inputs, three calls per input, RNG resets, controls, watchdog, and interpretation rules in `PROTOCOL.md` remain fixed. Record the shim bytes and SHA-256, compiler output, source and executable hashes. Use a new write-once run directory with an explicit compatibility flag. Stop and retain any further build/runtime failure; another change would need another frozen protocol.

This tests one exact modern build/call path. Agreement of classifications cannot show that the 1997 selection program used FreeLIP, this version, or these arguments. Disagreement requires independent reproduction before it bears on selection.
