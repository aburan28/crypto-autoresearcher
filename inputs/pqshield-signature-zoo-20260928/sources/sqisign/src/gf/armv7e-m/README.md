# ARMv7E-M (Cortex-M4) field arithmetic

Optimized GF(p) arithmetic for the three SQIsign primes, generated with
[m4-modarith](https://github.com/Crypto-TII/m4-modarith) (commit `a04e297`), the code generator described in
"Generation of Fast Finite Field Arithmetic for Cortex-M4 with ECDH and SQIsign Applications" (TCHES 2025/4).
The code is saturated 32-bit Montgomery arithmetic (R = 2^(32·nlimbs)) written as Thumb-2/DSP inline assembly
(UMULL/UMAAL), constant-time by construction, and compiles only with `arm-none-eabi-gcc` for ARMv7E-M targets.

This directory is not part of the CMake build. Its sole consumer is `scripts/gen_pqm4_sources.sh`, which packages
it as the `m4f` implementation for [the-sqisign-pqm4](https://github.com/SQISign/the-sqisign-pqm4); the packages
must be compiled with `-DSQISIGN_GF_IMPL_SAT32` so that `fp_constants.h` selects the saturated limb counts
(11/16/21 at 32-bit radix) and `e0_basis.c` selects the matching Montgomery constants. A `_Static_assert` in each
wrapper enforces this.

## Layout

Per prime (`p324_3` = 3·2^324−1, `p500_27` = 27·2^500−1, `p664_17` = 17·2^664−1):

- `code_<prime>_mont.c` — verbatim m4-modarith output (all functions `static`, suffixed `_<prime>_ct`), except
  for the provenance header and the symbol-suffix rename documented below. Never edit by hand; regenerate.
- `fp_<prime>_armv7em.c` — the SQIsign `fp_*` wrapper: `#include`s the generated file, aliases the plain modarith
  names to the suffixed ones, and provides the API of `src/gf/ref/include/fp.h` with the same semantics as the
  reference wrappers (rendered from `scripts/add_parameter_set_templates/field.c.j2`).

## Regeneration recipe

Requirements: python3, and the Go tool [`addchain`](https://github.com/mmcloughlin/addchain) on `PATH`
(m4-modarith silently produces a broken `modpro` without it — check `command -v addchain` first). Run in a
scratch directory: `addchain` drops `inv.acc`/`ac.txt` files in the CWD.

```sh
git clone https://github.com/Crypto-TII/m4-modarith && cd m4-modarith && git checkout a04e297 && cd ..
python3 m4-modarith/scripts/m4generator.py '3*2**324-1'  mont | sed 's/_323241_ct/_p324_3_ct/g'   > code_p324_3_mont.c
python3 m4-modarith/scripts/m4generator.py MFP500        mont | sed 's/_MFP500_ct/_p500_27_ct/g'  > code_p500_27_mont.c
python3 m4-modarith/scripts/m4generator.py '17*2**664-1' mont | sed 's/_1726641_ct/_p664_17_ct/g' > code_p664_17_mont.c
```

Notes:
- p500_27 uses the `MFP500` preset (same prime; it sets `optfsb=True`, matching the published TCHES artifact).
  p324_3 and p664_17 have no preset, so the prime is passed as an expression and the generator derives the raw
  symbol suffix from it (`_323241_ct`, `_1726641_ct`); the `sed` renames give the committed `_<prime>_ct` names.
- Then re-add the provenance header at the top of each file (copy it from the committed version).
- The wrappers were rendered from `scripts/add_parameter_set_templates/field.c.j2` (unmodified template) with
  `core` = the `#include` + alias-`#define` block, `nlimbs` = 11/16/21, `nbytes` = 41/64/84 (= ceil(log2(p)/8);
  do NOT use the generated `Nbytes_*_ct` macro, which is nlimbs·4), `enc_bytes` = 48/64/88 (`FP_ENCODED_BYTES`),
  and `ZERO`/`ONE`/`TWO_INV`/`THREE_INV` from `mont_limbs(v, p, base=32, N=nlimbs)` of
  `scripts/add_parameter_set.py`, followed by the trailing `_Static_assert`. The saturated-32 `BASIS_E0_PX/QX`
  branches in `src/precomp/ref/<prime>/e0_basis.c` are the same values re-encoded with R = 2^(32·nlimbs)
  (`scripts/precomp/cformat.py` emits them for new parameter sets).
