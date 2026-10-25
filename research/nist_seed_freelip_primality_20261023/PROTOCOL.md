# Frozen FreeLIP 1.0 order-test replay

**Frozen:** 2026-10-23 UTC, before compiling the archival source or testing any curve order. **Question:** Could the unmodified FreeLIP 1.0 probable-prime routine itself reject one or more of the eleven reconstructed prime-order seed curves while accepting the ten published controls?

## Inputs and implementation

- Read the eleven seed-level omitted classes in `research/nist_seed_skipped_curves_20261016/assessed.json`, SHA-256 `370e79ce0bff8f26bb437fe37d1756f3f8261a5c00e9062ba41cf70f272e8841`.
- Read the ten `published_controls` in that directory's `traits.json`, SHA-256 `a1102bd487379d223581863fab731d6eb6957bf0e264b450f1c7b298279b0b67`. Deduplicate P-224 coefficient signs by using the eleven assessed rows.
- Use FreeLIP 1.0 upstream tarball `https://ftp.kh.edu.tw/Linux/Debian/debian-archive/dists/Debian-1.3.1/main/source/math/freelip_1.0.orig.tar.gz`, SHA-256 `cd168c2ba0f9052d84072664b559219506050f583fdf58060517d59422f5bccc`; its `lip.c` SHA-256 is `5c507451e8c13323f106a66b5f76cdf17dfbe9eb7f289eb1ac0c706855625bff`. The archive header is dated 25 October 1996 and the contained README is dated 1 May 1995. Do not modify the archival `lip.c` or `lip.h`.
- Build a wrapper against `lip.c` on the current host with a generated `lippar.h` setting `PLAIN`; use 30-bit limbs and `SIZEOFLONG=8` for the host's 64-bit `long`. Record compiler, flags, warnings and source digests. If this build fails, record the failure and stop; do not silently switch arithmetic paths or edit the archive.

## Fixed cases, controls, and outcomes

For every exact order `n`, call `zstart()`, parse its decimal value with `zstrtoz`, reset FreeLIP's RNG with `zrstarts(7157891)`, and call `zprobprime(n,1)`; reset to the same seed and call `zprobprime(n,5)`; call `zprime(n,1,2)`. Preserve all three raw return values. Run the same matrix on known small prime 101, composites 15 and 221, and `3*n` for the published prime192v1 order. The 21 archived `n` values have separately certified primality; do not reinterpret them based on this replay. Fail closed on input/hash mismatch, parse mismatch, crash, signal, missing output, or a control returning an unexpected classification.

Predeclared interpretation:

- If all 21 prime orders return prime under all three calls and all controls pass, this excludes **this FreeLIP 1.0 routine under this exact modern build and call matrix** as a direct reason for rejecting the eleven. It does not identify the historical program, version, flags, arguments, or call path.
- If any true prime is rejected, preserve the exact input, command, stdout/stderr, build and platform details; independently reproduce the return before inferring a library behavior. A modern-build failure is not a historical rejection or an intrinsic curve weakness.
- If a control fails, or compilation/runtime fails, mark the replay invalid or indeterminate; do not count it as evidence about curve selection.

The run is bounded to 25 inputs, three calls each, 30 seconds per whole replay and 256 MiB resident memory. Use a new write-once run directory. Retain the wrapper, exact compile/run commands, environment, raw output, exit codes, timestamps, JSON rows, verification, report, diagram, and inspected PDF. This tests only a software workflow hypothesis. No official hypothesis status or ECDLP cost claim follows.
