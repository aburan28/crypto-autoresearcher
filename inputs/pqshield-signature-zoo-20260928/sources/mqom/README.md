# MQOM v3

The repository contains the reference C implementation of the *MQOM v3* digital signature scheme, a NIST PQC submission. See the [MQOM website](https://mqom.org/) for details.

## License

The MQOM code on this repository is under the MIT license: please check [LICENSE](LICENSE) for more information.
The repo also contains third party code possibly under other licenses, provided by the header in each concerned file (among other sources, MQOM uses code from [XKCP](https://github.com/XKCP/XKCP) for Keccak,
and [BearSSL](https://bearssl.org/) for C bitsliced AES and Rijndael).

## Dependencies

* To build: `Makefile`
* To use the helper `manage.py`: Python 3 (version >= 3.6)

## Software Architecture

```
+--------------------------------------------------------------------+
|                       NIST API  (crypto_sign.c)                    |
|        crypto_sign_keypair . crypto_sign . crypto_sign_open        |
+-------------------------------+------------------------------------+
                                |
           +--------------------+--------------------+
           |                    |                    |
    +------+-------+    +-------+--------+    +------+-------+
    |    KeyGen    |    |      Sign      |    |    Verify    |
    |  (keygen.c)  |    |   (sign.c)     |    | (sign.c /    |
    +------+-------+    +---+--------+---+    |sign_memopt.c)|
           |                |        |        +------+-------+
           |                |        |               |
           |   +------------+--+  +--+---------------+------+
           |   |     PIOP      |  |        BLC              |
           |   |     piop/     |  |        blc/             |
           |   |  def/memopt   |  |  CT: def/memopt         |
           |   |  bitslice     |  |  OT: def/memopt         |
           |   +------+--------+  +---------+---------------+
           |          |                     |
           +--+-------+----------+  +-------+-----------+
              |   expand_mq.c    |  |     GGM Tree      |
              | (MQ system from  |  |    ggm_tree/      |
              |   seed)          |  |  CT: small trees  |
              +------------------+  |    x1/batch       |
                                    |  OT: large tree   |
                                    |    bfs/dfs/incr   |
                                    +-------------------+

    +--------------------------+    +------------------------------+
    |   Field Arithmetic       |    |   Symmetric Primitives       |
    | fields_ref.h (portable)  |    | XOF xof.c (SHAKE/Keccak)     |
    | fields_avx2.h (AVX2)     |    | PRG prg.c (Rijndael CTR)     |
    | fields_avx512.h (AVX-512)|    | sha3/ (Keccak variants)      |
    | fields_arm_neon.h (NEON) |    | rijndael/ (AES variants)     |
    | fields_bitsliced/ (PIOP) |    +------------------------------+
    +--------------------------+
```

All compile-time parameters are injected via `parameters/mqom3_parameters_<variant>.h`,
selected automatically from the four-tuple `MQOM3_PARAM_SECURITY`, `MQOM3_PARAM_BASE_FIELD`,
`MQOM3_PARAM_TRADEOFF`, `MQOM3_PARAM_OT_VARIANT`. The public API follows the NIST convention:
`crypto_sign`, `crypto_sign_open`, `crypto_sign_keypair` in `crypto_sign.c`.

Two additional entry points sit alongside `Sign`/`Verify` without altering them: `Sign_Prepare`/
`Sign_Finalize` (`sign_pre.c`) split signing into a message-independent precomputation and a
short finalization once the message is known, and `StreamedVerify_*` (`verify_stream_ct.c` /
`verify_stream_ot.c`) verifies a signature incrementally from arbitrary-sized chunks instead of
the whole buffer at once. See [Pre-Signatures](#pre-signatures) and
[Streaming Verification](#streaming-verification) below.

## Quick Usage

The `manage.py` Python script is the recommended interface. To compile one or several schemes:

```bash
python3 manage.py compile [schemes ...]
```

where `[schemes ...]` is a non-empty list of MQOM instances in the format
`<category>_<base-field>_<trade-off>_<blc>`:
* `<category>` is `cat1`, `cat3`, or `cat5` (128-, 192-, or 256-bit security);
* `<base-field>` is `gf2` or `gf16`;
* `<trade-off>` is `shorter` (for `gf2` only), `fast` or `short` (for `gf16` only);
* `<blc>` is `ct` (Correlated Trees) or `ot` (One Tree).

You can use prefix-based wildcards. For example:
* `cat3` selects all Category III instances;
* `cat1_gf16` selects all Category I instances over GF(16);
* `all` selects all 18 instances.

```bash
python3 manage.py compile all
python3 manage.py compile cat1_gf16_fast_ct
python3 manage.py compile cat3 --no-kat --no-bench
```

It is also possible to compile directly with `make` using the `MQOM3_VARIANT` variable:

```bash
make clean && make MQOM3_VARIANT=cat1_gf16_fast_ct sign
make clean && make MQOM3_VARIANT=cat5_gf2_shorter_ot kat_gen
```

## Running Tests

```bash
# Run KAT generation + verification for one instance
python3 manage.py test cat1_gf16_fast_ct

# Run all 18 instances in parallel without valgrind
python3 manage.py test all --no-valgrind -p -1

# Run with sanitizers (ASan + UBSan)
make MQOM3_VARIANT=cat1_gf16_fast_ct USE_SANITIZERS=1 kat_check

# Embedded KAT self-test (no I/O, suitable for cross-compilation)
make MQOM3_VARIANT=cat1_gf16_fast_ct test_embedded_KAT
```

## Running Benchmarks

```bash
python3 manage.py bench cat1_gf16_fast_ct -n 100
```

or directly:

```bash
make MQOM3_VARIANT=cat1_gf16_fast_ct bench
./bench 100
```

## Pre-Signatures

`Sign()` splits naturally into a message-independent phase (BLC commit, PIOP evaluation) and a
short message-dependent phase (challenge sampling, BLC opening). `sign_pre.h` exposes that split
at two levels:

```c
/* Recommended: high-level, randomized wrappers - salt/mseed/mask_rnd are
 * generated internally (no caller-supplied randomness left to reuse), and
 * presig is wiped by crypto_sign_finalize() after use (success or failure),
 * so reusing that same buffer fails cleanly instead of silently succeeding. */
int crypto_sign_prepare(uint8_t presig[MQOM3_PRESIG_SIZE], const uint8_t sk[MQOM3_SK_SIZE]);

int crypto_sign_finalize(uint8_t sig[MQOM3_SIG_SIZE], unsigned long long *siglen,
                          const uint8_t *msg, unsigned long long mlen,
                          const uint8_t sk[MQOM3_SK_SIZE], uint8_t presig[MQOM3_PRESIG_SIZE]);

/* Low-level, deterministic primitives underneath - caller supplies all
 * randomness. For KAT generation, testing, or callers with their own CSPRNG;
 * see the SECURITY note above their declarations in sign_pre.h before using
 * these directly. */
int Sign_Prepare(const uint8_t sk[MQOM3_SK_SIZE], const uint8_t salt[MQOM3_PARAM_SALT_SIZE],
                  const uint8_t mseed[MQOM3_PARAM_SEED_SIZE],
                  const uint8_t mask_rnd[MQOM3_PARAM_PRESIGN_RND_SIZE],
                  uint8_t presig[MQOM3_PRESIG_SIZE]);

int Sign_Finalize(const uint8_t sk[MQOM3_SK_SIZE], const uint8_t *msg, unsigned long long mlen,
                   const uint8_t presig[MQOM3_PRESIG_SIZE], uint8_t sig[MQOM3_SIG_SIZE]);
```

The result of either level is byte-identical to a direct `Sign()` call with the same
`(salt, mseed, msg)`.

**Single use only.** `(salt, mseed, mask_rnd)` must be fresh, uniformly random, and never reused
across two `Sign_Prepare()` calls for the same `sk`; a given `presig` must be passed to
`Sign_Finalize()` for at most one message. 

`crypto_sign_prepare`/`crypto_sign_finalize` only partially remove this burden from the caller.
The randomness half is fully solved: there is no caller-supplied `(salt, mseed, mask_rnd)` left to
accidentally reuse. The presig half is not: `crypto_sign_finalize` wipes its `presig` argument in
place after use, so calling it again with that *same buffer* fails cleanly instead of silently
reopening the commitment - but a caller who copied `presig` before that call (persisted it, sent
it elsewhere, kept a second reference, ...) can still finalize that copy against a different
message and reopen the same commitment. That operational discipline - never persist or duplicate
a `presig` you intend to finalize only once - is still entirely on the caller at both API levels;
see the comment above the declarations in `sign_pre.h` for the full reasoning.

The `presig` is masked with an XOF keyed on `sk || mask_rnd` (only the 256-bit `mask_rnd` is
stored in clear), so it is safe against a passive eavesdropper while kept or transmitted outside
the signer between the two calls - but the mask is confidentiality-only, not an integrity tag,
and it does nothing to prevent the single-use requirement above from being violated by the
application itself.
Both levels are compiled in for every build, CT and OT alike, with no dedicated flag to set.
`MQOM3_PRESIG_SIZE` is a small, fixed constant per variant, independent of
`MEMORY_EFFICIENT_BLC`/`BLC_KEEP_ALL_TREES_IN_MEMORY`: `Sign_Prepare`/`Sign_Finalize` always
serialize a compressed, seed-based form of the BLC opening key (the "ckey": the master seed plus
the auxiliary values, with the salt and - for CT - the correlated-tree offset left out, since
both are recovered at parse time) into `presig`, never the
fully-expanded GGM tree that `BLC_KEEP_ALL_TREES_IN_MEMORY` builds cache purely as an internal
RAM/CPU tradeoff for `Sign()`/`Verify()` - that cache has no reason to leak into a persisted
pre-signature. One consequence: a `presig` produced by any build of a given variant (default or
`MEMORY_EFFICIENT_BLC=1`) is byte-compatible with `Sign_Finalize`/`crypto_sign_finalize` in any
other build of that same variant.

```bash
make MQOM3_VARIANT=cat1_gf16_fast_ct test_presign
./test_presign
```

## Streaming Verification

`StreamedVerify_*` (`verify_stream.h`) is an alternative to `Verify()` that consumes a signature
incrementally through an Init/Update/Finalize/Clean state machine, instead of requiring the whole
`MQOM3_SIG_SIZE`-byte signature in memory up front - useful when a signature arrives piecemeal
(network, flash read, etc.).

```c
stream_verify_ctx_t *StreamedVerify_Init(const uint8_t pk[MQOM3_PK_SIZE]);
int StreamedVerify_Update(stream_verify_ctx_t *ctx, const uint8_t *sigpart, size_t sigpartlen);
int StreamedVerify_Finalize(stream_verify_ctx_t *ctx, const uint8_t *msg, unsigned long long mlen);
void StreamedVerify_Clean(stream_verify_ctx_t *ctx);
```

Call `Update()` as many times as needed with arbitrary chunk boundaries (they need not line up
with any internal structure), then `Finalize()` once all `MQOM3_SIG_SIZE` bytes have been fed in.
Always call `Clean()` last, regardless of outcome - including after an `Update()` failure or an
abandoned stream where `Finalize()` is never reached - to release the context.

* `STREAM_VERIFY_BATCH=N` - number of repetitions buffered between two PIOP recomputation
  passes (default: `PIOP_NB_PARALLEL_REPETITIONS_VERIFY`); lower it for less peak memory, at
  the cost of more (smaller) PIOP calls.
* OT memory floor: the shared large tree is reconstructed as soon as the opening prefix
  (`T_open` path, hidden leaf commitments, `delta_x`) has arrived - in
  `BLC_OT_BATCH_SIZE`-sized passes, not one monolithic one - but the `alpha1` section only
  comes *after* that prefix in the byte stream, and the PIOP needs both. So
  `x_eval`/`u_eval`/`com1` for all `tau` repetitions stay resident from the tree pass through
  `Finalize()` regardless of `STREAM_VERIFY_BATCH` or `BLC_OT_BATCH_SIZE`; the batch size
  still bounds the tree traversal's own working set, just not the context's. The CT variant
  has no such floor: its `alpha1` is interleaved per-execution chunk, so it streams execution
  by execution. (Note this floor is specific to the *streamed* verifier; `Verify_memopt` reads
  the whole signature and therefore does shrink these buffers to `BLC_OT_BATCH_SIZE`.)

Like `Sign_Prepare`/`Sign_Finalize`, `StreamedVerify_*` is compiled in for every build and needs
no dedicated flag: it calls the memopt BLC/PIOP primitives directly by name, independently of
whatever `Verify()` itself is built with.

```bash
make MQOM3_VARIANT=cat1_gf16_fast_ct test_verify_stream
./test_verify_stream
```

## Advanced Usage

### Variant Parameters

The four compile-time axes are set via preprocessor variables and select the appropriate
parameter header from `parameters/`:
* `MQOM3_PARAM_SECURITY`: security level in bits; `128` (Cat I), `192` (Cat III), `256` (Cat V);
* `MQOM3_PARAM_BASE_FIELD`: log2 of the base field order; `1` for GF(2), `4` for GF(16);
* `MQOM3_PARAM_TRADEOFF`: `0` (fast), `1` (short), `2` (shorter - GF(2) only);
* `MQOM3_PARAM_OT_VARIANT`: `0` for CT (Correlated Trees), `1` for OT (One Tree).

These are normally set automatically by `MQOM3_VARIANT`. You can inspect the resulting
`EXTRA_CFLAGS` for a given instance with:

```bash
python3 manage.py env cat1_gf16_fast_ct
```

### Optimization Flags

**Rijndael/AES backend** - exactly one of the seven below is active, and selecting two is a
compile-time error (`rijndael/rijndael.h`). Selecting none lets `rijndael/rijndael_platform.h`
auto-detect, with priority VAES > AES-NI > ARM AES > bitslice:
* `RIJNDAEL_BITSLICE=1` - portable constant-time bitsliced implementation (default on
  non-x86/non-ARM platforms); adapted from [BearSSL](https://bearssl.org/constanttime.html);
* `RIJNDAEL_TABLE=1` - table-based implementation, faster but not constant-time;
* `RIJNDAEL_CONSTANT_TIME_REF=1` - constant-time flavour of the portable reference
  implementation (`rijndael/rijndael_ref.c`); correct and side-channel-conservative, but the
  slowest of the backends - meant as a readable baseline rather than a deployment choice;
* `RIJNDAEL_AES_NI=1` - AES-NI instruction set (x86, constant-time);
* `RIJNDAEL_VAES=1` - VAES (Vector AES) for batched Rijndael; auto-detected when compiling with
  `-march=native` on a VAES-capable CPU (`__VAES__` takes priority over AES-NI); within VAES, uses
  512-bit registers (AVX-512, 4 lanes/instruction) when `AVX512F+BW` are available, otherwise
  256-bit registers (AVX2, 2 lanes/instruction); note: `FORCE_PLATFORM_AVX2/AVX512` do not imply
  VAES since they do not pass `-mvaes` to the compiler - use the `*_VAES` profiles below for that;
  the x2/x4/x8 key schedule is
  further accelerated with GFNI (`VGF2P8AFFINEINVQB`) - both AES-128 (cat1) and Rijndael-256-256
  (cat3 and cat5) - when the compiler target provides it
  (`__GFNI__`, e.g. `-march=native` on a GFNI-capable CPU); opt out with
  `NO_RIJNDAEL_VAES_GFNI_KEYSCHED=1`;
* `RIJNDAEL_ARM_AES=1` - ARMv8 Crypto Extension hardware AES (AArch64 and ARMv7 with Crypto
  Extension); constant-time; auto-detected when `__ARM_FEATURE_CRYPTO` or `__ARM_FEATURE_AES` is
  defined (i.e. `-march=native` on ARMv8+crypto, or `FORCE_PLATFORM_AARCH64_AES`);
* `RIJNDAEL_EXTERNAL=1` - the implementation comes from the integrator. `rijndael_external.c`
  only ships `weak` placeholders, which the caller's own symbols override at link time; the
  expected symbols and their contract are in `rijndael/rijndael_external.h`. MQOM3 calls the
  `*_enc*` routines with `data_in == data_out`, so an external backend must read its whole
  input group before writing any output - one that cannot must add
  `RIJNDAEL_NO_INPUTS_ALIASING=1`.

**Rijndael modifiers** - these are *not* backends and do not belong to the exclusive set above;
they combine with whichever backend is active:
* `RIJNDAEL_OPT_ARMV7M=1` - dedicated ARMv7-M assembly (Category I only); uses the
  [LUT from SAC2016](https://github.com/Ko-/aes-armcortexm) for table mode or the
  ["fixsliced" implementation from TCHES2021](https://github.com/aadomn/aes) for bitslice -
  so it refines `RIJNDAEL_TABLE` or `RIJNDAEL_BITSLICE` rather than replacing them;
* `USE_WEAK_LOW_LEVEL_API=1` - makes Rijndael and Keccak symbols `weak`, allowing the caller
  to override them at link time with a hardware-accelerated backend (e.g. for embedded targets
  with a CRYP engine). Orthogonal to the backend choice: it changes symbol binding, not which
  implementation is compiled in - unlike `RIJNDAEL_EXTERNAL`, which compiles none.

**GF(256) multiplication tuning:**
* `NO_FIELDS_REF_SWAR_OPT=1` - disable the SWAR (SIMD Within A Register) optimization in the
  portable `FIELDS_REF` path; SWAR packs 4 GF(256) multiplications into one 32-bit word
  (`GF256_MULT_X4`), is constant-time, and is on by default;
* `USE_GF256_TABLE_MULT=1` - non-constant-time 65 kB multiplication table (faster on embedded
  targets without cache-timing risk);
* `USE_GF256_TABLE_LOG_EXP=1` - non-constant-time smaller log/exp tables (exclusive with the
  above);
* `GF256_MULT_TABLE_SRAM=1` - place the large multiplication table in SRAM instead of flash
  (constant cache behavior; only meaningful with `USE_GF256_TABLE_MULT=1`).

**Field arithmetic** (selected automatically, can be forced):
* `FIELDS_REF=1` - portable C reference (fallback when no SIMD is detected);
* `FIELDS_AVX2=1` - AVX2 (+ GFNI if available);
* `FIELDS_AVX512=1` - AVX-512 (+ GFNI if available);
* `FIELDS_NEON=1` - ARM NEON implementation (AArch64 and ARMv7+NEON); auto-detected on
  little-endian ARM only. The backend is little-endian by construction, so big-endian ARM
  falls back to `FIELDS_REF` and forcing `FIELDS_NEON=1` there is a compile-time error.
  Big-endian targets also need an explicit `KECCAK_PLATFORM=opt64` (or `plain32`);
* `NO_GFNI=1` - disable GFNI even when the CPU supports it.

**Keccak/XOF implementation** (auto-detected, can be forced):
* `KECCAK_PLATFORM=avx512|avx2|aarch64|arm32_neon|armv7m|opt64|plain32` - force a specific Keccak
  backend; auto-detection priority follows this order: `avx512` (x86-64 + AVX-512VL+F) >
  `avx2` (x86-64 + AVX2) > `armv7m` (ARMv7-M/EM) > `aarch64` (AArch64) > `arm32_neon`
  (ARMv7A+NEON) > `opt64` (portable 64-bit fallback);
* `USE_XOF_X4=1` - enable x4 parallel XOF (default on, disable with `USE_XOF_X4=0`);
* `USE_XOF_X8=1` - enable x8 parallel XOF; auto-enabled on `avx512` (native times8 kernel)
  and `aarch64` (2xtimes4 mlkem-native assembly); otherwise opt-in.

**Platform profiles** (force a complete platform configuration):
* `FORCE_PLATFORM_REF=1` - pure C, no `-march=native`;
* `FORCE_PLATFORM_AVX2=1` - AVX2 + AES-NI;
* `FORCE_PLATFORM_AVX2_GFNI=1` - AVX2 + AES-NI + GFNI;
* `FORCE_PLATFORM_AVX2_VAES=1` - AVX2 + VAES (adds `-mvaes`, so Rijndael auto-selects
  `RIJNDAEL_VAES` at its 256-bit sub-level instead of AES-NI);
* `FORCE_PLATFORM_AVX2_VAES_GFNI=1` - same plus GFNI, which also turns on the GFNI-accelerated
  VAES key schedule;
* `FORCE_PLATFORM_AVX512=1` - AVX-512 + AES-NI;
* `FORCE_PLATFORM_AVX512_GFNI=1` - AVX-512 + AES-NI + GFNI;
* `FORCE_PLATFORM_AVX512_VAES=1` - AVX-512 + VAES; `-mvaes` together with `-mavx512f` is what
  opens the 512-bit VAES forms, so this one lands on the `RIJNDAEL_VAES512` sub-level;
* `FORCE_PLATFORM_AVX512_VAES_GFNI=1` - same plus GFNI and the GFNI key schedule;
* `FORCE_PLATFORM_AARCH64=1` - AArch64, NEON fields, bitsliced Rijndael (no crypto extension);
* `FORCE_PLATFORM_AARCH64_AES=1` - AArch64, NEON fields, ARM hardware AES (`armv8-a+crypto`);
* `FORCE_PLATFORM_AARCH64_SHA3=1` - AArch64, NEON fields, bitsliced Rijndael, accelerated
  Keccak via SHA3 extension (`armv8-a+sha3`);
* `FORCE_PLATFORM_AARCH64_AES_SHA3=1` - AArch64, NEON fields, ARM hardware AES, accelerated
  Keccak via SHA3 extension (`armv8-a+crypto+sha3`);
* `FORCE_PLATFORM_ARM32_NEON=1` - ARMv7A+NEON, NEON fields, bitsliced Rijndael.

**Memory optimization** (for embedded or memory-constrained contexts):
* `MEMORY_EFFICIENT_BLC=1` - memory-optimized BLC (recomputes GGM paths instead of storing
  all leaves); required by `VERIFY_MEMOPT`;
* `MEMORY_EFFICIENT_PIOP=1` - memory-optimized PIOP (streams MQ matrices instead of
  materializing them); required by `VERIFY_MEMOPT`; incompatible with `USE_PIOP_CACHE` and
  `PIOP_BITSLICE`;
* `MEMORY_EFFICIENT_KEYGEN=1` - streaming MQ matrix generation during KeyGen;
* `SIGN_MEMOPT=1` - optimized signing processing repetitions in batches, mirroring
  `VERIFY_MEMOPT` (implies `MEMORY_EFFICIENT_BLC=1` and `MEMORY_EFFICIENT_PIOP=1`);
* `VERIFY_MEMOPT=1` - optimized verification processing repetitions in batches (implies
  `MEMORY_EFFICIENT_BLC=1` and `MEMORY_EFFICIENT_PIOP=1`);
* `SIGN_MEMOPT_STREAM_COM1=0/1` / `VERIFY_MEMOPT_STREAM_COM1=0/1` - stream the `com1` digests
  into `presig_id` batch by batch instead of keeping the whole `TAU`-sized array until the
  end. Trades one always-live `xof_context` for `(TAU - batch) * DIGEST_SIZE`, so it only
  pays off once the repetitions are actually batched - which is exactly the default: each
  flag is on iff its path is batched (`SIGN_MEMOPT_BATCH < TAU`, resp.
  `VERIFY_MEMOPT_BATCH < TAU`, where that effective batch is
  `PIOP_NB_PARALLEL_REPETITIONS_SIGN`/`_VERIFY` for CT and `BLC_OT_BATCH_SIZE` for OT).
  Override either one to force the behavior; the two are independent, since signing and
  verification have separate batch parameters. Output is byte-identical either way;
* `USE_PIOP_CACHE=0` - disable the PIOP cache (enabled by default; incompatible with
  `MEMORY_EFFICIENT_PIOP=1`);
* `BLC_DEFAULT_NO_KEEP_TREES=1` - do not keep full GGM trees in memory in the default BLC path
  (saves memory at the cost of recomputation; overridden by `MEMORY_EFFICIENT_BLC=1`);
* `PRG_ONE_RIJNDAEL_CTX=1` - use a single Rijndael context for PRG and PRG_pub;
* `SEED_COMMIT_MEMOPT=1` - memory-optimized seed commitment using a single Rijndael context;
* `BLC_NB_LEAF_SEEDS_IN_PARALLEL=N` - number of leaf seeds processed in parallel in the BLC
  memopt path (tune for memory/cycles trade-off; must divide `MQOM3_PARAM_NB_EVALS`; defaults
  to 8 in the fast-folding path, or to 1 in the slow-folding path - see `BLC_NO_FAST_FOLDING`
  below for what a value above 1 costs there);
* `BLC_NO_FAST_FOLDING=1` - skip the `NB_EVALS_LOG`-sized fast-folding scratch buckets in the
  BLC memopt path, accumulating each leaf's contribution directly into the output instead
  (`NB_EVALS` field multiplications instead of `NB_EVALS_LOG`, but no extra buffer); only has
  an effect where BLC memopt is compiled in (`MEMORY_EFFICIENT_BLC=1` or `VERIFY_MEMOPT=1`),
  CT and OT alike. `BLC_NB_LEAF_SEEDS_IN_PARALLEL` still defaults to 1 here (unchanged
  minimal-memory behavior), but an explicit value above 1 is supported too.
  This allows to explore multiple time-memory trade-offs.
* `GGMTREE_NB_ENC_CTX_IN_MEMORY=N` - number of GGM encryption contexts kept in memory;
* `SMALL_GGM_TREE_NB_SIMULTANEOUS_LEAVES_LOG=N` - log2 of the number of GGM leaves processed
  simultaneously in the batch tree path;
* `BLC_SEEDEXPAND_CACHE` - SeedExpand cache: **on by default** in the default BLC path
  (auto-defined in `blc_ct_default.c`/`blc_ot_default.c`); opt out with `NO_BLC_SEEDEXPAND_CACHE=1`; off by
  default in the memopt path, opt in with `BLC_SEEDEXPAND_CACHE=1`;
* `BLC_SEEDCOMMIT_CACHE=1` - enable SeedCommit cache in the memopt path (off by default);
* `USE_ENC_X8=1` (default on) / `USE_ENC_X8=0` - use x8 batched encryption in SeedExpand;
  set to `0` to reduce memory at a cycles cost;
* `USE_SIGNATURE_BUFFER_AS_TEMP=1` - reuse the output signature buffer as scratch storage
  during signing (avoids a temporary allocation).

**OT-specific tuning** (only relevant for `blc=ot` variants):
* `BLC_OT_BATCH_SIZE=N` - number of executions processed per large-tree traversal pass
  (default: `TAU`); reduce to trade memory for extra tree traversals. Under `SIGN_MEMOPT` /
  `VERIFY_MEMOPT` this is also the effective batch of the whole OT path. On the
  signing side it sizes `x0`/`u0`/`u1` (and `com1` once streaming is on); on the
  verification side `x_eval`/`u_eval`/`alpha1` (and `com1` likewise). Note the one
  buffer it does *not* shrink: `alpha0`/`alpha1` on the signing side stay `TAU`-sized
  as soon as you batch, because they must survive until the Hash_1/com2 pass - at the
  default they cost nothing only because they alias `u0`/`u1`, which batching gives
  up. So the first step below `TAU` hands back `2 * TAU * ETA` bytes before the batch
  starts paying. Dropping below `TAU` also turns `com1` streaming on (see
  `SIGN_MEMOPT_STREAM_COM1` above). The PIOP then consumes that window in sub-batches of
  `PIOP_NB_PARALLEL_REPETITIONS_SIGN`/`_VERIFY`;
* x8 batches are used for the large-tree BFS expansion by default whenever the encryption
  backend provides them (`USE_ENC_X8`, itself on by default), since x8 consistently
  outperforms x4; set `NO_LARGE_TREE_BFS_X8=1` to force the x4 batching path instead;
* `NO_LARGE_TREE_BFS=1` - use DFS instead of BFS for the large OT GGM tree (BFS is on by
  default for OT variants);
* `LARGE_GGM_TREE_INCR_BATCH=1` - in the memopt (DFS, `MEMORY_EFFICIENT_BLC=1`) large-tree
  traversal only, batch 2 independently-keyed tree nodes per derivation step (1 x2 encryption
  call instead of 2 separate ones) instead of deriving one node at a time; off (`0`) by
  default. Only pays off with a x2 (at least) Rijndael backend (e.g. bitsliced Rijndael
  `RIJNDAEL_BITSLICE=1`). **This flag governs the signing side only** - see the Verify
  counterpart just below. Byte-identical output either way (it only changes which block
  cipher entry point is used, not what is computed);
* `LARGE_GGM_TREE_INCR_BATCH_VERIFY=1` - same x2 pair batching, but for the *verification*
  side of the memopt large-tree traversal; off (`0`) by default **even when
  `LARGE_GGM_TREE_INCR_BATCH=1`**, deliberately. The two sides are switched independently
  because their trade-off differs: signing drives the constant-time (typically bitsliced)
  cipher, where pairing two derivations into one x2 call is a clear win; verification only
  handles public data and therefore drives the *public* cipher (typically table-based), which
  has no multi-key parallelism to exploit. 

**PIOP parallelism and bitslicing:**
* `PIOP_BITSLICE=1` - bitsliced PIOP across all `tau` repetitions (incompatible with
  `MEMORY_EFFICIENT_PIOP=1`); tuned by:
  * `FIELDS_BITSLICE_COMPOSITE=1` - use a composite field representation;
  * `FIELDS_BITSLICE_PUBLIC_JUMP=1` - allow branches on public inputs;
  * `BITSLICE_HYBRID_LEFTOVER_LIMIT=N` - threshold below which leftover repetitions fall back
    to the scalar (non-bitsliced) path (default: 10; must be ≤ 32);
* `PIOP_NB_PARALLEL_REPETITIONS_SIGN=N` / `PIOP_NB_PARALLEL_REPETITIONS_VERIFY=N` - batch
  repetitions to reduce buffer memory at the cost of extra recomputation cycles. Both default
  to `TAU`, i.e. no batching. For CT under `SIGN_MEMOPT`/`VERIFY_MEMOPT` these are the
  effective batch, so dropping below `TAU` also turns `com1` streaming on; for OT the
  effective batch is `BLC_OT_BATCH_SIZE` instead and these only size the PIOP sub-batches
  inside it.

**Security / cleansing:**
* `USE_ENC_CTX_CLEANSING=1` - cleanse Rijndael key schedule contexts after use
  (disabled by default for performance; enable in security-sensitive contexts).
  Forced on when building for liboqs (`MQOM3_FOR_LIBOQS`, see `common.h`), where cleansing
  is mandatory - do not expect the default there.

**Sanitizers:**
* `USE_SANITIZERS=1` - compile with ASan + UBSan + LSan.

## Embedded Targets

The MQOM3 implementation is designed to be portable. Cross-compilation for bare-metal Cortex-M4
targets is supported by passing `CC=arm-none-eabi-gcc` and appropriate `EXTRA_CFLAGS` to `make`.
The `test_embedded_KAT` target produces a self-contained binary (no filesystem I/O) suitable
for cross-compilation and simulation.

Further details, benchmarks, and a ready-to-flash firmware for STM32 boards (STM32F4Discovery
and Nucleo-L4R5ZI) are available in the [dedicated embedded repository](https://github.com/mqom/embedded-mqom).
Additional experimental optimizations for embedded platforms are described in the paper
[Breaking the Myth of MPCitH Inefficiency: Optimizing MQOM for Embedded Platforms](https://eprint.iacr.org/2026/078.pdf).
