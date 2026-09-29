# proves_too_much control — run the argument against objects where its conclusion is KNOWN FALSE

TASK-20260904-0d66e3 (red team), EXP-PFDR-20ee58. Sources:
`pt_proves_too_much.py` → `pt-proves-too-much.json`;
`pt_generator_threshold.py` → `pt-generator-threshold.json`;
`r2_sensitivity.py` → `r2-sensitivity.json`. Meter snapshot `2d2083e5`, fixture
sha256 `62d89109f94ef658885ddb5289504df159de01ee4341852b34349d01724bf8e5`
(re-hashed here; matches VALIDATION.md). **No experiment run; constructed
objects only.**

The argument under test is the one the finding will rest on: *the two
ingredients of KN-FIND-006's binary degree-3 syzygy (an idempotent affine P; a
degenerate subset-sum) are absent over F_p, therefore the twin's baseline is
Koszul-only, therefore deficit 0 at every D ≤ 8.*

## Object 1 — the committed binary chained fixture at n = 12 (deficit KNOWN nonzero)

| reading | D = 2 | D = 3 | D = 4 |
|---|---|---|---|
| rows | 12 | 312 | 3912 |
| rank | 12 | 311 | 3802 |
| koszul (66 pairs + 12 Frobenius) | 0 | 0 | 78 |
| deficit cumulative (`rows - rank - koszul`) | 0 | **1** | **32** |
| deficit graded (increment) | 0 | **1** | **31** |

Reproduced independently here (my own load of the fixture into
`harness.macaulay_fp`, not the run's numbers): the meter returns 1 and 31 (or 32
cumulative). **The declared failure signature is met: the instrument is not
blind on the binary object.** The 12 quadrics alone carry the whole deficit
(`[0, 1, 32]`); the 12 cubics alone carry none (`[0, 0, 0]`).

### Object 1, red-team extension: the deficit as a function of GENERATOR COUNT

Hold p = 2, the ring, the convention and the meter fixed; vary only how many of
the 12 descended quadrics are present (fixture order):

| # quadrics | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | **12** |
|---|---|---|---|---|---|---|---|---|---|---|---|
| deficit cumulative (D2, D3, D4) | 0,0,0 | 0,0,0 | 0,0,0 | 0,0,0 | 0,0,0 | 0,0,0 | 0,0,0 | 0,0,0 | 0,0,0 | 0,0,0 | **0,1,32** |

Also 0 for the mixed subsets I tried: 2 gens (quadric+cubic), 4 gens, 8 gens,
16 gens (8 quadrics + 8 cubics).

**This is the finding of the control.** On the object where the deficit is known
to exist, restricting to the twin's shape — two generators — returns deficit
exactly 0, *at p = 2*. The deficit turns on only when the complete 12-generator
descent block is present, which is what KN-FIND-006's mechanism (a subset-sum of
descended quadrics degenerating to an affine form) requires. Consequently
"deficit 0 on the twin" is fully reproduced at p = 2 by an object that has both
"absent" ingredients present, and the measurement cannot by itself separate

  (H_char) the mechanism is characteristic-2 specific — the reading in
           F4 / `success_criterion` of the contract, and

  (H_count) the mechanism needs a descent block of many generators, which the
           twin does not have at any characteristic.

The argument survives at H_count, and that survival is the location worth
recording. (Caveat kept narrow: a subsystem need not inherit a syzygy of the
whole system, so this does not prove H_count; it shows the experiment does not
discriminate.)

## Object 2 — prime-field two-quartic systems with a planted non-Koszul syzygy

Premises of the argument, checked verbatim on each object (all in the twin's
ring at s = 3, p = 4099):

| object | (S2)/(S3 i): `f^2-f = 2a_0a_1 ≠ 0` | (S3 ii): top forms independent, both degree 4, no degenerate subset-sum | deficit(5..8) |
|---|---|---|---|
| T0 the twin | holds | holds (supports also disjoint) | 0, 0, 0, 0 |
| A1 (common factor deg 1) | holds | holds | 0, 0, **1**, 10 |
| A2 (common factor deg 2) | holds | holds | 0, **1**, 11, 56 |
| A3 (common factor deg 3) | holds | holds | **1**, 11, 57, 186 |
| D1 (idempotent factor a_0) | holds | holds | **2**, 20, 95, 289 |

**The declared failure signature is met.** The premises of (S2)–(S3) hold
verbatim on four objects whose deficit is nonzero, so the (S2)–(S3) argument
does not imply "deficit 0". Where would the implication have to come from? From
`stage0-derivation.md` §4, sentence "Hence the generic prediction is
`rank(Mac_D) = rows(D)` for D < 8 and `rows(8) - 1` at D = 8", and from
H-PFDR-9aadc0 (S2)'s "Hence the twin's generic baseline is Koszul ONLY". That
step is Fröberg/BFS genericity, i.e. HEUR-001 — it is carried correctly as a
heuristic in the hypothesis record and asserted without that label in the
derivation note. **M1 is an empirical branch, not a theorem**, exactly as the
plan anticipated. (A1 additionally has nonzero constant terms in both
generators, like the twin, so "has a constant term" is not the missing
separator either.)

## Object 3 — the twin itself at p = 2

### 3a, verbatim construction in the mixed ring (free u), p = 2

`(A, B, x_R) = (0, 1, 1)`: `E1 = a0·u^2 + a3·u^2 + a0·a3`,
`E2 = a6·u^2 + u^2 + a6`.

- **(S1) fails explicitly**: `deg E1 = deg E2 = 3`, not 4 — the cross term
  `2·2^{i+j} a_{k,i}a_{k,j}` vanishes because 2 is not a unit. The leaves also
  collapse (`x_k = a_{k,0}`), so six of the nine digit variables disappear: the
  p = 2 object is not the twin at another characteristic, it is a degenerate
  object.
- The generators involve u, so `E_i^2 ≠ E_i` and `frobenius_count` = 0 by
  default (correctly); forcing it would give 114 at D = 8.
- **Conclusion false**: `deficit_pairwise(D = 5..8) = [3, 26, 105, 265]`
  (and `[2, 16, 57, 117]` / `[2, 17, 67, 163]` at other (A, B, x_R)).

### 3b, pure Boolean reading (u replaced by one Boolean variable), p = 2

- `deg E1 = deg E2 = 2` — (S1) fails harder.
- **(S2) fails explicitly**: `P = a_0 + a_1` satisfies `P^2 = P`; every
  generator satisfies `f^2 = f`; `frobenius_count(D = 8) = 772 ≠ 0`, so the
  Frobenius family reappears in the baseline count exactly as the plan
  predicted.
- **Conclusion false**: `deficit_cumulative = [0, 0, 6, 38, 13, -59, -109]` and
  `[0, 2, 22, 96, 141, 139, 131]` at D = 2..8 (the negative
  `deficit_pairwise` values at high D are the pairwise Koszul count
  over-counting above the first second-syzygy degree; that over-count cannot
  occur for the twin, which has only two generators — see the R1 note §4a).

**Correction to the plan's stated signature.** `proves_too_much.failure_signature`
says "At p = 2 the Frobenius count must be nonzero and (S2) must fail
explicitly". That holds in reading 3b. It does **not** hold in reading 3a, the
verbatim mixed-ring construction: there `f^2 = f` fails for the generators
(they contain u, and `u^2 ≠ u`), the Frobenius count is legitimately 0, and what
fails first is **(S1)**, the degree claim. Both readings are recorded; in both,
the conclusion "deficit 0" is false, which is what the control asks.
