# V2 build compatibility repair

This repair changes three code/build files, with no solver algorithm, configuration, backend, target, or cost-model change. The v1 source tree and its archived failed launch remain unchanged. No scientific cohort input or truth file was opened by these development checks.

1. `candidate/decoder.hpp`: rename only the inner fixed self-test variable `b` to `diag_backwards` and its one use. Reversing that identifier substitution reconstructs the v1 header byte for byte.
2. `baselines/build.py`: use the exact admitted C++20 project flags, including `-Wpedantic`, `-Wshadow` and `-Werror`, at `-O2`; add `-isystem vendor/include` for unchanged upstream GNU C public headers. ASan/UBSan adds instrumentation without changing `-O2`. The normal GNU11 C object recipe is unchanged.
3. `baselines/baselines.cpp`: replace only two quoted vendor include paths by the corresponding angle-bracket public header names. Reversing those two include substitutions reconstructs the v1 adapter byte for byte.

The baseline README documents the actual language and warning boundaries. All 13 vendored source/header/license hashes remain unchanged, and compiler dependencies resolve all five public headers to those exact bytes. The first attempt to apply the project warning flags without declaring this boundary failed on the vendor's GNU `__int128` typedefs; its stderr, command receipt and source snapshot are retained. No project warning was removed or disabled.

Normal and ASan/UBSan checks use the exact admitted C++ warning flags. Both profiles pass 2,966 candidate self-test checks, 333 candidate CLI checks, 269 baseline self-test checks, and baseline prefix/fallback CLI controls. The latter independently check 130 produced candidate equations across both profiles, all five answers per fixed target, matched A/A seeds and primitive vectors, matched fallback work, and stage reconciliation. Leak detection is explicitly disabled because unavailable under the host runtime; no leak result is claimed.

`v2-repair-receipt.json`, `source-comparison.json`, the minimal patches and raw command logs provide the exact new source hashes and evidence. Copied v1 manifests and development receipts are explicitly named historical. `repair/build/` contains only local test binaries and is not a publication path. Fresh prospective admission and a published live claim remain required before the scientific cohort can execute.
