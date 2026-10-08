# Adding a parameter set

A parameter set is a level with its own prime `p` (**must be prime and
`≡ 3 (mod 4)`**). `SVARIANT_S` in the top `CMakeLists.txt` is the single source
of truth — every module iterates it. Only `gf` is architecture-specific;
everything else is `ref` for all builds, so a new set is mostly new field code
plus folder stubs. Example throughout: `p607_1` for `p = 2**607 - 1`.

## Scripted

`scripts/add_parameter_set.py` does everything below automatically. Point
`--modarith` (or `$MODARITH_DIR`) at a
[modarith](https://github.com/mcarrickscott/modarith) checkout:
```bash
MODARITH_DIR=/path/to/modarith \
    scripts/add_parameter_set.py p607_1 '2**607-1'```
- `--security <bits>` sets the target security level explicitly; otherwise it is
  derived from the prime size (`round(logp/128)*64`). It drives the challenge,
  response and signature sizes, so set it when prime size and security level are
  decoupled.
- Without `--asm` the set is registered in the ref/opt-only managed
  `SVARIANT_S` block, so `broadwell`/`arm64` builds skip it.
- `--asm` additionally generates x86-64 assembly
  (`scripts/gen_fp/gen_fp_asm_broadwell.py`), AArch64 assembly
  (`scripts/gen_fp/gen_fp_asm_arm64.py`) and the sat64 binding
  (`gen_fp_c.py`) into `src/gf/{sat64,broadwell,arm64}/<name>/`, and registers
  the set in the asm-capable block instead (the two asm builds share that
  gate, so a set always gets both backends or neither). Requires
  `p = c*2^t - 1` with ≥ 4 spare bits in the top limb and **at most 11
  limbs** (x86-64 pointer spilling is enabled automatically:
  `--spill-pointers` at 9–10 limbs, `--spill-pointers-max` at 11; arm64
  needs no flags). Test on both hosts; the broadwell and arm64 KATs must be
  bit-identical to ref.
- `--lvl 1` optionally set up the level target

The script writes no precomputed data itself — generate it and build:
```bash
cmake -B build -DSQISIGN_BUILD_TYPE=ref
cmake --build build --target precomp_p607_1   # requires SageMath
cmake -B build -DSQISIGN_BUILD_TYPE=ref        # re-configure: new headers
cmake --build build
ctest --test-dir build -R p607_1
```
`make precomp_<name>` produces the `include/` headers (`fp_constants.h`,
`encoded_sizes.h`, …) and the NIST `api.h`. To generate KATs and add them to `KAT/`:
```bash
cmake --build build --target PQCgenKAT_sign_p607_1
( cd build/apps && ./PQCgenKAT_sign_p607_1 )
cp build/apps/PQCsignKAT_*_SQIsign_p607_1.{req,rsp} KAT/
```
(`scripts/update_kats.sh <build-dir>` does this for every built set.)

## Manual steps

To add a set `<name>` by hand instead:

### 1. Field arithmetic — `src/gf/ref/<name>/`
- `fp_<tag>_64.inc`, `fp_<tag>_32.inc` (included by the `fp_<tag>.c` radix
  glue): generate the core with modarith
  (`python3 monty.py 64 0x<p>`, writes `field.c`), then append the SQIsign
  `fp_*` wrappers + `fp_encode`/`fp_decode`/`fp_decode_reduce`. Copy the tail of
  `src/gf/ref/p324_3/fp_p324_3_64.inc` and adjust the Montgomery constants
  `ONE/TWO_INV/THREE_INV`, the limb count (`Nlimbs`) and the byte lengths.
  `fp_exp3div4` maps to `modpro` (valid because p ≡ 3 mod 4).
- `CMakeLists.txt`:
  ```cmake
  set(SOURCE_FILES_GF_SPECIFIC
      fp_<tag>.c
  )
  include(../lvlx.cmake)
  ```
- `test/CMakeLists.txt`: `include(../../lvlx_test.cmake)`

### 2. Parameters — `src/precomp/ref/<name>/`
- `sqisign_parameters.txt`:
  ```
  lvl = <N>
  p = 0x<p>
  ```
- `CMakeLists.txt`: `include(../lvlx.cmake)`
- an empty `include/` directory — `make precomp` fills it (`fp_constants.h`,
  `encoded_sizes.h`, …). `fp_constants.h`'s `NWORDS_FIELD` is taken from the
  modarith `Nlimbs` of the step-1 field code.

### 3. NIST API — `src/nistapi/<name>/`
- `api.c`: copy `src/nistapi/api.c` verbatim. (`api.h` is generated in step 6.)

### 4. Pass-through stubs (identical one-liners)
For each of `ec hd id2iso signature verification`:
`src/<mod>/ref/<name>/CMakeLists.txt` → `include(../lvlx.cmake)`, and add
`test/CMakeLists.txt` → `include(../../lvlx_test.cmake)` for `ec id2iso signature`.

### 5. Register in the top `CMakeLists.txt`
Add `<name>` to `SVARIANT_S`; guard it if it has no broadwell/arm64 assembly:
```cmake
if(SQISIGN_BUILD_TYPE STREQUAL "ref" OR SQISIGN_BUILD_TYPE STREQUAL "opt")
    list(APPEND SVARIANT_S "<name>")
endif()
```

### 6. Generate precomputed data + build (needs SageMath)
`make precomp_<name>` runs the `precompute_*.sage` scripts, producing the five
precomp `.c` (`ec_params/e0_basis/torsion_constants/quaternion_data/
endomorphism_action`), the `include/*.h` headers and `api.h`. cmake needs those
`.c` to exist *before* it can configure, so create empty placeholders first
(the one thing the script does for you here):
```bash
( cd src/precomp/ref/<name> && touch \
    ec_params.c e0_basis.c torsion_constants.c quaternion_data.c endomorphism_action.c )
cmake -B build -DSQISIGN_BUILD_TYPE=ref
cmake --build build --target precomp_<name>   # fills in the .c + headers
cmake -B build -DSQISIGN_BUILD_TYPE=ref        # re-configure: pick up the new headers
cmake --build build
ctest --test-dir build -R <name>
```
`make precomp` (no suffix) does this for *every* level; `precomp_<name>` just
this one.

### Notes
- The manual flow above is ref/opt-only. For **broadwell** and **arm64**, use
  the generators (`--asm`, or run `gen_fp_asm_broadwell.py`,
  `gen_fp_asm_arm64.py` and `gen_fp_c.py` from `scripts/gen_fp/` by hand).
- `precompute_sizes.sage` writes `api.h` to `nistapi/lvl{lvl}`. Name the set
  `lvl<N>` (matching `lvl = <N>`) for the path to line up, or change that line.
  (The script derives it from the folder name, so any name works there.)
- Encoded width: `fp_encode`/`fp_decode` must span `FP_ENCODED_BYTES =
  ceil(logp/64)*8` bytes (zero-padded), which exceeds modarith's `Nbytes` when
  `logp` is far from a 64-bit boundary (e.g. 80 vs 76 for 2^607-1).

## Sets added with this tooling

| set | level | prime | builds |
|---|---|---|---|
| p324_3 | 1 | 3·2^324−1 | ref/opt/broadwell/arm64 |
| p500_27 | 3 | 27·2^500−1 | ref/opt/broadwell/arm64 |
| p664_17 | 5 | 17·2^664−1 | ref/opt/broadwell/arm64 |
