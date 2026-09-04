# R2 — sensitivity of the deficit meter at the twin's own shape: is M1 vacuous?

TASK-20260904-0d66e3 (red team). All objects live in the twin's ring (mixed:
9 squarefree digit variables + one free u), s = 3, p = 4099, cumulative
multipliers, `koszul(D) = koszul_pair_count`, meter snapshot `2d2083e5`.
Source: `r2_sensitivity.py` → `r2-sensitivity.json`; ceiling probes reported
inline below and reproducible from the same builder. **None of this is an
experiment run.**

## Why the existing positive control does not answer the question

The contract makes the meter's planted-syzygy positive control a REQUIRED INPUT
(`inputs.shared_meter` item (b)) and an invalidation rule. It was run
(`VALIDATION.md` §6) — but in **squarefree** mode (10 digit variables) and
**ordinary** mode (5 free variables), with base quadrics and k redundant
generators, at D* = 3, 4. It was **not** run in mixed mode, not at two quartics,
and not with cumulative multipliers of degree ≤ 4. The blocking calibration
(CTRL-BINARY-CALIBRATION) is likewise at a different shape: 24 generators of
degrees 2 and 3 over GF(2) at D = 3, 4. So before this note, no artifact showed
that the instrument returns a nonzero value at the shape the twin is measured
at. H-PFDR-9aadc0's own `method_ceiling.nearby_object_control` demands exactly
this ("A meter that cannot separate those two may not report a twin value").

## The sensitivity ladder (planted non-Koszul syzygies at the twin's shape)

`A(g)`: `E1 = h q1`, `E2 = h q2` with `deg h = g`, `deg q_i = 4 - g`, so the
syzygy `q2 E1 - q1 E2 = 0` has multiplier degree `4 - g` and first fits the
cumulative row set at `D = 8 - g`. The identity was verified as a polynomial
identity in the ring for each object. `D1`: common factor `a_0`, an idempotent.
`C`: `E2 = 7 E1`. `M`: both generators equal to one degree-4 digit monomial.
`N`: an independent random quartic pair. `T0`: the twin itself.

| object | gen degrees | deficit(5) | deficit(6) | deficit(7) | deficit(8) | predicted first firing |
|---|---|---|---|---|---|---|
| T0 twin (curve 4101, target 1) | 4, 4 | 0 | 0 | 0 | 0 | — |
| N random quartic pair | 4, 4 | 0 | 0 | 0 | 0 | — |
| A1 common factor deg 1 | 4, 4 | 0 | 0 | **1** | 10 | D = 7 ✓ |
| A2 common factor deg 2 | 4, 4 | 0 | **1** | 11 | 56 | D = 6 ✓ |
| A3 common factor deg 3 | 4, 4 | **1** | 11 | 57 | 186 | D = 5 ✓ |
| D1 idempotent factor a_0 | 4, 4 | **2** | 20 | 95 | 289 | D = 5 (duplication) + D = 7 |
| C proportional pair | 4, 4 | 11 | 57 | 187 | 442 | ceiling probe |
| M both = a_0a_1a_2a_3 | 4, 4 | 15 | 91 | 325 | **805** | ceiling probe |

Rows are 22 / 114 / 374 / 886 and columns 825 / 1291 / 1793 / 2304 at
D = 5 / 6 / 7 / 8 for every object (they depend only on the ring and the
generator degrees).

## Verdict on vacuity

**The instrument is not blind at the twin's shape and M1 is not vacuous.** Every
planted syzygy fired at exactly the predicted degree, and the smallest planted
effect the meter resolved is 1 (the deficit is an exact integer, so the
resolution is 1 and there is no noise floor). Observed dynamic range at D = 8 on
two-quartic objects in this ring: 0 … 805, against an absolute ceiling of
`rows - 1 - koszul = 884`.

## What M1 excludes, quantitatively

M1 at the tested cells asserts: *the twin's two quartics admit no syzygy
`(q1, q2)` with `deg q_i ≤ 4` other than the Koszul one* (D ≤ 8 with cumulative
multipliers is exactly the multiplier-degree-≤ 4 window). The excluded region is
therefore `{1, …, 805}` at D = 8 (observed range), `{1, …, 325}` at D = 7,
`{1, …, 91}` at D = 6, `{1, …, 15}` at D = 5.

Against the specific alternative the experiment was designed for, the exclusion
is comfortable:

- KN-FIND-006's law under the hypothesis's own identification `k ↦ s`
  (H-PFDR-9aadc0 `nearby_object_control`) predicts `8s - 1` = 23 / 31 / 39 at
  s = 3 / 4 / 5. All three are inside the instrument's range at D = 8 and would
  have been seen.
- On relative magnitude, the binary cell (D = 4) carries deficit 32 of 3912 rows
  = 0.82 %; 0.82 % of the twin's 886 rows is ≈ 7, likewise well inside range.
- M2's prediction (a nonzero s-slope in `deficit(8)`) would need only ≥ 1 per s
  point to be visible.

So the exclusion is real but it is an exclusion over a **very small space of
relations**: the twin's whole trivial-syzygy budget at D = 8 is 1 (one Koszul
pair), against 78 (66 Koszul pairs + 12 Frobenius) at the calibration cell. The
twin is measured where almost nothing can happen, for any pair of quartics. This
is a scope statement about the finding, not a defect in the measurement.

## The plan's second planted family is not constructible

`review_plan` R2 asks for `E2'' = w E1 + v` with `deg w ≤ 2` and
`deg E2'' = 4`. For `deg w ≥ 1`, `deg(w E1) = deg w + 4 > 4` in this ring, and
`deg w = 0` gives a proportional pair (object C). The A(g) family realises the
same intent and is substituted; recorded here so the composition can see the
substitution.
