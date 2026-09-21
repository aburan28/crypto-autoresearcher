# EXP-MLKEM-002 implementation notes

Executor task: `TASK-20260724-228`. Observations only; no hypothesis
status change.

## Reach mechanism (verbatim shim)

`implementation/comparison_probe.c` declares the library-local symbols
`mlkem_cmp`, `mlkem_cmp_avx2`, and `mlkem_cmp_neon` and links each
`libwolfssl.a` statically. Comparison logic, buffer lengths, and dispatch
conditions in wolfSSL source were not modified. Backend selection is a
compile-time macro on the harness only:

- `-DPROBE_BACKEND_SCALAR` → `mlkem_cmp` (no `USE_INTEL_SPEEDUP`)
- `-DPROBE_BACKEND_AVX2` → `mlkem_cmp_avx2`
- `-DPROBE_BACKEND_NEON` → `mlkem_cmp_neon`

Header compatibility: v5.9.1 provides `wolfssl/wolfcrypt/mlkem.h`; v5.9.2
folds the public API into `wc_mlkem.h`. The probe uses `__has_include` for
`mlkem.h` and always includes `wc_mlkem.h`.

## Configure lines actually used

Scalar (both tags):

```text
./configure --enable-static --disable-shared --enable-mlkem --enable-sha3 \
  --disable-examples --disable-crypttests --disable-asm --disable-intelasm \
  --disable-armasm --disable-aesni 'CFLAGS=-O2 -fvisibility=hidden'
```

AVX2 (both tags):

```text
./configure --enable-static --disable-shared --enable-mlkem --enable-sha3 \
  --disable-examples --disable-crypttests --enable-intelasm --enable-asm \
  'CFLAGS=-O2 -fvisibility=hidden'
```

NEON (both tags, cross):

```text
./configure --host=aarch64-linux-gnu --enable-static --disable-shared \
  --enable-mlkem --enable-sha3 --disable-examples --disable-crypttests \
  --enable-armasm --enable-asm --disable-intelasm \
  'CFLAGS=-O2 -fvisibility=hidden'
```

Scratch trees: `/tmp/exp-mlkem-002/wolfssl-{5.9.1,5.9.2}` worktrees;
builds under `/tmp/exp-mlkem-002/builds/`; probes under
`/tmp/exp-mlkem-002/harness/`. Nothing from builds was written into
`/workspace` except declared experiment artifacts.

## Source lock

Annotated tag objects match the specification expected SHAs. Peeled
commits used for builds:

- v5.9.1-stable → `1d363f3adceba9d1478230ede476a37b0dcdef24`
- v5.9.2-stable → `ac01707f552c611fbd135cc723b2682b3e7f80f2`

## Conformance anchor

Named anchor: `deterministic_encap_decap_self_consistency` via
`wc_MlKemKey_MakeKeyWithRandom` / `EncapsulateWithRandom` /
`Decapsulate`, plus scalar cross-commit equality of ciphertext and shared
secret SHA-256 digests for both seeds and all three parameter sets.
Strength: weakest accepted (self-consistency). Recorded under
CTRL-VALID-KAT and CTRL-SCALAR-CROSS-COMMIT.

## Negative harness

Deliberate truncated comparator `harness_truncated_cmp` in
`comparison_probe.c` compares only the first `sz/2` bytes. Exercised in
RUN-MLKEM-006 before any library-build grid conclusion. Detected omitted
ranges `[ct_len/2, ct_len)` for all three parameter sets.

## Protocol deviations / repairs within the executor session

1. First probe compile against v5.9.2 failed because `mlkem.h` was removed
   in that tag; fixed with `__has_include` (implementation_error repair,
   not a crypto re-run).
2. AVX2/NEON attest initially used a 64-byte buffer; `mlkem_cmp_avx2`
   size-specializes for 768/1088/1568. Attest length raised to 768; NEON
   unequal probe index set to 1 (early lane) because index 100 falls in
   the ignored half-block under the prefix reduction bug.
3. First RUN-MLKEM-008 qemu invocation lacked `-L /usr/aarch64-linux-gnu`;
   recorded then repaired in-session. Builds themselves succeeded on the
   first NEON attempt.
4. Wall-clock figures in run manifests for RUN-006/008 reflect the
   successful probe-execution pass after build reuse; earlier compile and
   configure time lived under `/tmp` and is noted here. Cumulative session
   wall time remained under the 5400 s budget.
5. Algorithm-18 integration on PREFIX-AVX2 silent indices did not accept
   on every index/seed (43/64 accepts). Primitive silent set
   `1536..1567` remains complete and reproducible; integration results
   are recorded in RUN-MLKEM-007 raw artifacts without claiming full
   integration agreement for every silent index.

## Scope exclusions honored

No key recovery, oracle construction, query chaining, attack-cost
estimation, timing/power/EM/cache/fault measurement, deployed-system
interaction, library comparison edits, or MLWE/passive-security claims.
