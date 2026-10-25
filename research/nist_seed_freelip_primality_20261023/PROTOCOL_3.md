# FreeLIP 1.0 missing string declarations

**Frozen:** 2026-10-23 UTC, after the second build failed and before any curve-order call. Additive to `PROTOCOL.md` and `PROTOCOL_2.md`; neither earlier run changes.

The compatibility build in `runs/freelip-20261023T2010Z/failure.json` reached `lip.c` but Clang rejected undeclared standard `strlen` and `strrchr` calls. Keep the exact generated `<malloc.h>` shim from protocol 2. Add only compiler arguments `-include string.h` so the standard prototypes are visible in `lip.c`; do not alter the archival source, wrapper, arithmetic options, input set, calls, controls or inference rules. Record the exact command and output in a fresh write-once directory. Stop on any further build or runtime failure, preserving the record before making a new change.
