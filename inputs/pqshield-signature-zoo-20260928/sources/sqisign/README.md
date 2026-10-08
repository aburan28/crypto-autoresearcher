# SQIsign

This library is a C implementation of SQIsign.

## Requirements

- CMake (version 3.13 or later)
- C11-compatible compiler

### Pre-computation

The constant values in the `src/precomp` directory were generated using the
pre-computation scripts in the `scripts/precomp` directory. It is not necessary
to execute these scripts to compile the project. The scripts have the following
requirements:
- [two-isogenies](https://github.com/ThetaIsogenies/two-isogenies)
  (`Theta-SageMath` version).
- [deuring-2D](https://github.com/Jonathke/deuring-2D)

## Build

For a generic build
```
$ mkdir -p build
$ cd build
$ cmake -DSQISIGN_BUILD_TYPE=ref ..
$ make
$ make test
```

An optimized executable with debug code and assertions disabled can be built
replacing the `cmake` command above by
```
cmake -DSQISIGN_BUILD_TYPE=<ref/broadwell/arm64> -DCMAKE_BUILD_TYPE=Release ..
```

## Build options

CMake build options can be specified with `-D<BUILD_OPTION>=<VALUE>`.

### SQISIGN_BUILD_TYPE

Specifies the build type for which SQIsign is built. The currently supported values are:
- `ref`: builds the plain reference implementation.
- `opt`: builds the optimized implementation which is the same as the reference
  implementation.
- `broadwell`: builds an additional optimized implementation targeting the Intel
  Broadwell architecture (and later). The optimizations are applied to the
  finite field arithmetic.
- `arm64`: builds an additional optimized implementation targeting 64-bit ARM
  (AArch64) cores. The optimizations are applied to the finite field arithmetic,
  using only baseline `armv8-a` instructions.

### ENABLE_SIGN

If set to `ON` (default), SQIsign is built with signature and verification functionality.
If set to `OFF`, SQIsign is built with verification functionality only.

### ENABLE_CT_TESTING

If set to `ON` (default: `OFF`), the library is built with valgrind client-request annotations for constant-time testing
(see the Constant-time tests section). Requires the valgrind development header
(`valgrind/memcheck.h`) and `CMAKE_BUILD_TYPE=RelWithDebInfo` — the suppressions need debug info, and assertions must be
disabled (`NDEBUG`) because asserts on secret-derived values are themselves secret-dependent branches; the configuration
fails otherwise. Outside valgrind the annotations are no-ops, but production builds should keep this `OFF`.

### CMAKE_BUILD_TYPE

Can be used to specify special build types. The options are:

- `Release`: Builds with optimizations enabled and assertions disabled.
- `Debug`: Builds with debug symbols.
- `ASAN`: Builds with AddressSanitizer memory error detector.
- `MSAN`: Builds with MemorySanitizer detector for uninitialized reads.
- `LSAN`: Builds with LeakSanitizer for run-time memory leak detection.
- `UBSAN`: Builds with UndefinedBehaviorSanitizer for undefined behavior detection.
- `COVERAGE`: Builds instrumented for gcov code coverage, at `-O0` and without LTO.
  See `scripts/coverage.sh`.

The default build type uses the flags `-O2 -Wstrict-prototypes -Wno-error=strict-prototypes -fvisibility=hidden -Wno-error=implicit-function-declaration -Wno-error=attributes`. (Notice that assertions remain enabled in this configuration, which harms performance.)

## Test

In the build directory, run `make test` or `ctest`.

The test harness consists of the following units:

- KAT test: `SQIsign_<level>_KAT`- tests against the KAT files in the `KAT`
  directory.
- Self-tests: `SQIsign_<level>_SELFTEST` - runs random self-tests
  (key generation, signature and verification).
- Sub-library specific unit-tests.

Note that, `ctest` has a default timeout of 1500s, which is applied to all tests
except the KAT tests. To override the default timeout, run
`ctest --timeout <seconds>`.

### Constant-time tests

Constant-time behavior is tested with valgrind memcheck in the ctgrind style: secrets are poisoned (marked undefined) at
the RNG, and memcheck reports any secret-dependent branch or memory index. Accepted exemptions (the remaining
non-constant-time parts of mp, id2iso and the quaternion layer) are filtered by `test/ct-quaternion.supp`. The
`sqisign_test_ct_<variant>` harnesses run one keypair + sign under this instrumentation. The `<variant>` suffix is the
parameter-set name (`p324_3`, `p500_27`, `p664_17`), i.e. `SVARIANT_S` in the top-level `CMakeLists.txt`. The modules
that do promise constant time (except for mp arithmetic and the calls to other modules) and are therefore fully checked 
are `hd`, `ec` and `gf`. Canonical invocation (mirrored by the
`ct-test` job in `.github/workflows/ct-test.yml`):

```
cmake -B build -DENABLE_CT_TESTING=ON -DCMAKE_BUILD_TYPE=RelWithDebInfo -DSQISIGN_TEST_REPS=1 -G Ninja
cmake --build build
valgrind --error-exitcode=1 --max-stackframe=4116160 --num-callers=25 -s \
    --suppressions=test/ct-quaternion.supp ./build/test/sqisign_test_ct_p324_3   # and p500_27, p664_17
```

Do not deviate from this recipe: some suppression entries only match frames valgrind resolves from debug info (hence
`RelWithDebInfo`) with sufficient recorded depth (hence `--num-callers=25`); without them the run produces many false
positives in libm.

#### The CT lattice reduction harness

`test/ct-quaternion.supp` exempts the big-integer (`src/mp`) and quaternion layers leaf-anchored and
caller-agnostic. That is a deliberate decision for a knowingly non-constant-time module, but it also silences
`src/quaternion/ref/lvlx/lll` — the *deliberately constant-time* reduction package that runs on top of them. A green
run of the harness above therefore says nothing about that package.

`sqisign_test_ct_lattice_<variant>` covers it. It drives the reduction entry points with poisoned inputs and runs
with **none** of those entries — only `test/ct-lattice-known.supp`, a short allowlist of findings that have been
identified and filed, so a new leak still fails the run. Never pass `ct-quaternion.supp` to it.

```
valgrind --error-exitcode=1 --max-stackframe=4116160 --num-callers=25 -s \
    --suppressions=test/ct-lattice-known.supp \
    ./build/src/quaternion/ref/p324_3/test/sqisign_test_ct_lattice_p324_3   # and p500_27, p664_17
```

Both harnesses are registered with ctest under the label `ct` when valgrind is found, so `ctest -L ct` runs the
whole constant-time suite locally. A plain `ctest` is unaffected.

## Known Answer Tests (KAT)

KAT are available in the `KAT` directory. They can be generated by running the
apps built in the `apps` directory:
```
apps/PQCgenKAT_sign_<level>
```

A successful execution will generate the `.req` and `.rsp` files.

A full KAT test is done as part of the test harness (see the Test section).

## Benchmarks

A benchmarking suite is built and can be executed with the following command:
```
apps/benchmark_<level> [--iterations=<iterations>]
```
where `<level>` specifies the SQIsign parameter set and `<iterations>` is the
number of iterations used for benchmarking; if the `--iterations` option is
omitted, a default of 10 iterations is used.

The benchmarks profile the key generation, signature and verification functions. The results are reported in CPU cycles if available on the host platform, and timing in nanoseconds otherwise.

## Examples

Example code that demonstrates how to use SQIsign with the NIST API is available
in `apps/example_nistapi.c`.

## Project Structure

The source code consists of a number of sub-libraries used to implement the
final SQIsign library:
- `common`: common code for hash function, seed expansion, PRNG, memory handling.
- `mp`: code for saturated-representation multiprecision arithmetic.
- `gf`: GF(p^2) and GF(p) arithmetic.
- `ec`: elliptic curves, isogenies and pairings. Everything that is purely
   finite-fieldy.
- `precomp`: constants and precomputed values.
- `quaternion`: quaternion orders and ideals.
- `hd`: code to compute (2,2)-isogenies in the theta model.
- `id2iso`: code for Ideal <-> Iso.
- `verification`: code for the verification protocol.
- `signature`: code for the key generation and signature protocols.

The dependencies are depicted below.
```
 ┌─┬──────────┬─┐        ┌─┬──────────┬─┐      ┌─┬──────────┬─┐
 │ ├──────────┤ │        │ ├──────────┤ │      │ ├──────────┤ │
 │ │  Keygen  │ │        │ │   Sign   │ │      │ │  Verify  │ │
 │ ├──────────┤ │        │ ├──────────┤ │      │ ├──────────┤ │
 └─┴────┬─────┴─┘        └─┴────┬─────┴─┘      └─┴────┬─────┴─┘
        │                       │                     │
        └──────────────────┐    │                     │
                           │    │                     │
┌─────────────────┐    ┌───▼────▼────────┐            │
│                 │    │                 │            │
│   Quaternions   ◄────┤  Ideal <-> Iso  ├────────┐   │
│                 │    │                 │        │   │
└────────┬────────┘    └────────┬────────┘        │   │
         │                      │                 │   │
         │                      │     ┌───────────────┘
         │                      │     │           │
┌────────▼────────┐    ┌────────▼─────▼──┐    ┌───▼────────────┐
│                 |    |                 |    |                |
|                 │    │       2D        │    │                │
│    Integers     │    │    Isogenies    ├────► Precomputation │
│                 │    │                 │    │                │
│                 │    │                 │    │                │
└─────────────────┘    └────────┬────────┘    └───▲────────────┘
                                │                 │
                                │                 │
                                │                 │
                       ┌────────▼────────┐        │
                       │                 │        │
                       │ Elliptic curves ├────────┘
                       │   & isogenies   │
                       │                 │
                       └──┬───────────┬──┘
                          │           │
                          │           │
                          │           │
              ┌───────────▼───┐   ┌───▼───────────┐
              │     GF(p)     │   │     Fixed     │
              │       &       │   │   precision   │
              │    GF(p^2)    │   │   integers    │
              └───────────────┘   └───────────────┘
```

## Cortex-M4 implementation

The full scheme (keypair generation, signing and verification) is supported in 32-bit embedded architectures running on bare metal environments such as the ARM Cortex-M4, but it is not directly supported by the build system of the present repository. The [pqm4 project](https://github.com/mupq/pqm4) is supported for evaluating SQIsign in the ARM Cortex-M4.

The glue code bridging pqm4's API to the library (`api.h`, `rng.h` and `pqm4_api.c`) is emitted by a dedicated generator, found in `apps/PQCgenKAT_sign_pqm4.c`.

A copy of the most recent version of pqm4 as of the round 2 submission deadline, including an implementation of SQIsign generated directly from this repository using the procedure explained next, is made available [here](https://github.com/SQISign/the-sqisign-pqm4), in the `sqisign` branch.

If changes are made to the library, the `scripts/gen_pqm4_sources.sh` shell script can be run, from the root folder of the repository, to generate a pqm4-compatible folder structure in `src/pqm4/sqisign_{p324_3,p500_27,p664_17}`, which can then be copied to the `crypto_sign` folder of pqm4. Note that the glue code generator is automatically run by this script.

The script takes an optional argument selecting the finite field arithmetic: `ref` (the default) packages the portable reference arithmetic (`src/gf/ref`) as the `ref` implementation directory of each scheme, `m4f` packages the optimized Cortex-M4 arithmetic generated by [m4-modarith](https://github.com/Crypto-TII/m4-modarith) (`src/gf/armv7e-m`; see the README there for provenance and regeneration instructions) as the `m4f` implementation directory, and `all` generates both. pqm4's testing and benchmarking tooling automatically exercises every implementation directory of a scheme, so `all` provides a direct ref-vs-m4f comparison.

## Acknowledgements

The reference implementation for finite field arithemtic (i.e., `src/gf/ref`)
was generated using [modarith](https://github.com/mcarrickscott/modarith) by
Michael Scott.

The optimized Cortex-M4 finite field arithmetic (i.e., `src/gf/armv7e-m`) was
generated using [m4-modarith](https://github.com/Crypto-TII/m4-modarith).

## License

SQIsign is licensed under Apache-2.0. See [LICENSE](LICENSE) and [NOTICE](NOTICE).

Third party code is used in some files:

- `src/common/ref/aes_c.c`; MIT: "Copyright (c) 2016 Thomas Pornin <pornin@bolet.org>"
- `src/common/generic/fips202.c`: CC0: Copyright (c) 2023, the PQClean team
- `src/common/generic/randombytes_system.c`: MIT: Copyright (c) 2017 Daan Sprenkels <hello@dsprenkels.com>
- `apps/PQCgenKAT_sign.c`, `apps/PQCgenKAT_sign_pqm4.c`, `src/common/ref/randombytes_ctrdrbg.c`, `test/test_kat.c`: by NIST (Public Domain)
