# Remote worker control failure

The n43-poly01 v2 worker failed in its first node-local software control on an AMD EPYC7R13 host. No scientific solution count, closure, or certificate check ran. All uploaded result artifact hashes were verified after S3 download. The native failure code was not preserved by the old validator; the first producer emitted no diagnostic text.

The retained M4RI library build enabled AVX-512, while the failed worker used an older CPU generation. This supports a portability mismatch as a suspected cause, not a directly observed signal diagnosis. Per-node controls prevented an unsupported worker from producing a scientific result.

The replacement library is configured with --disable-sse2 and CFLAGS=-O3 -march=x86-64 -mtune=generic, with empty SIMD_FLAGS. Local reference-byte, exact-count and odd-degree full-worker controls pass. A new validator persists every subprocess return code before reporting failure. The old bundle, job and protocol remain unchanged. A prospective protocol amendment is required before a corrected attempt of this same input.

Exit criterion: a replacement worker must pass controls on its actual node and reach the original input's scientific stages. Local controls alone do not satisfy that criterion. This failed attempt gives no LFD inference and is not an additional independent sample.
