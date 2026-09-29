---
id: KN-FIND-b0c3c9
type: internal_finding
title: >-
  The prime-field chained digit twin shows deficit exactly 0 at every tested
  cell with the D=8 kernel spanned by the Koszul vector, on a demonstrably
  sensitive instrument - but the zero does NOT attribute to characteristic 2,
  because two- to eleven-generator subsystems of the binary system return 0 at
  p=2 as well
tags: [semaev, weil-descent, chained-system, digit-presentation, macaulay, rank-deficit, syzygy, koszul, prime-field, characteristic-2, descent-multiplicity, instrument-sensitivity, null-object, negative-result, negative-scope, ecdlp]
confidence: reported
internal_refs: [EV-PFDR-e67f06, DEC-20260904-63a809, H-PFDR-9aadc0, EXP-PFDR-20ee58]
proof_status: derivation
proof_refs:
  - coordination/reviews/pfdr-battery-20260904/reviews/TASK-20260904-0d66e3/derivation-note-R1-baseline.md
  - coordination/reviews/pfdr-battery-20260904/reviews/TASK-20260904-0d66e3/R2-sensitivity-table.md
  - coordination/reviews/pfdr-battery-20260904/reviews/TASK-20260904-0d66e3/r2-sensitivity.json
  - coordination/reviews/pfdr-battery-20260904/reviews/TASK-20260904-0d66e3/proves-too-much-table.md
  - coordination/reviews/pfdr-battery-20260904/reviews/TASK-20260904-0d66e3/pt-generator-threshold.json
  - coordination/reviews/pfdr-battery-20260904/reviews/TASK-20260904-0d66e3/R3-calibration-convention.md
  - coordination/reviews/pfdr-battery-20260904/reviews/TASK-20260904-0d66e3/R4-null-adequacy-and-confounds.md
  - coordination/reviews/pfdr-battery-20260904/reviews/TASK-20260904-0d66e3/R0-regeneration-diff.md
  - coordination/reviews/pfdr-battery-20260904/reviews/TASK-20260904-a7eead/rederivation.yaml
  - experiments/EXP-PFDR-20ee58/stage0-derivation.md
claim_tier: toy
added: 2026-09-04
superseded_by: null
---

## Finding

Two halves, of equal weight. Citing the first without the second misrepresents
the measurement.

### 1. The measurement: deficit exactly 0, on an instrument that can move

For the prime-field chained digit twin — `E1 = S_3(x_1, x_2, u)`,
`E2 = S_3(u, x_3, x_R)` with a **free** internal node `u` and base-2 digit
leaves, `m = 3`, `d = 2` — the two quartic generators admit **no syzygy
`(q_1, q_2)` with `deg q_i <= 4` other than the Koszul relation**:

- `rows(D) − rank(Mac_D) − koszul(D) = 0` on **all 246 twin draws** at every
  `D`, at `s ∈ {3,4,5}` with `D <= 8` and `s = 6` with `D <= 6`, over
  `p ∈ {4099, 16411, 65537}` and six generic-`j` curves per prime with certified
  planted targets.
- At the deciding cell the `D = 8` left kernel is **exactly one-dimensional and
  is spanned by the explicit Koszul vector**, whose multipliers all have degree
  ≤ 4 and are therefore legal rows. This is what makes "rows − rank − koszul =
  0" a statement about *syzygies* rather than a coincidence between two counts,
  and it should be recorded alongside the integer whenever the result is cited.
- Counts (deciding cell, `s = 3`, `p = 4099`, `D = 5..8`): rows
  22/114/374/886, columns 825/1291/1793/2304, rank 22/114/374/885, koszul
  0/0/0/1, zero-product rows 0.

**The zero is a measurement, not a blind spot.** Planted non-Koszul syzygies
fire at exactly the predicted degrees under the identical meter, ring,
convention and multiplier degrees:

| planted object | deficit at `D = 5..8` |
| --- | --- |
| A1 (common linear factor) | `[0, 0, 1, 10]` |
| A2 (common quadratic factor) | `[0, 1, 11, 56]` |
| A3 (common cubic factor) | `[1, 11, 57, 186]` |
| D1 (idempotent common factor `a_0`) | `[2, 20, 95, 289]` |
| the twin | `[0, 0, 0, 0]` |
| an ordinary random quartic pair | `[0, 0, 0, 0]` |

Observed dynamic range at `D = 8` on two-quartic objects in this ring: **0..805**
against an absolute ceiling of 884, with **resolution 1** — exact integers, no
noise floor. This closes the contract's own required input (a planted-syzygy
positive control **in the same manifest lineage**) at the twin's shape, which
the meter's own validation note did not do: it ran in squarefree and ordinary
modes with base quadrics at `D* = 3, 4`, never in mixed mode with two quartics.
The gap was open when the numbers were read and is now closed in the claim's
favour.

### 2. The non-attribution: the zero does not isolate characteristic

Holding `p = 2`, the ring, the convention and the meter fixed and varying **only
the number of descended quadrics** of the binary chained system, the deficit is

`[0, 0, 0]` for `j = 2, 3, 4, 5, 6, 7, 8, 9, 10, 11`, and `[0, 1, 32]` only at
`j = 12`, the complete descent block. Mixed subsets of 2, 4, 8 and 16 generators
are also exactly 0.

**Two generators return deficit 0 at `p = 2` — on the very object where the
deficit is known to exist, and where the Boolean idempotent law and
Frobenius-linear squaring are both PRESENT.** "Deficit 0 on the twin" is
therefore fully reproduced without invoking characteristic at all. The
experiment varied characteristic, generator count and encoding *together*, and
its zero does not attribute to any of them.

Stated narrowly: a subsystem need not inherit a syzygy of the whole system, so
this does **not prove** that descent multiplicity is the carrier. It shows the
measurement **does not separate** "the mechanism is characteristic-2 specific"
from "the mechanism needs a descent block of many generators, which the twin
lacks at any characteristic". That sub-question is **inconclusive in both
directions** and is recorded as `KN-OPEN-d6ad3f`.

## Scope and limitations

- **THIS IS NOT A STATEMENT ABOUT SUMMATION POLYNOMIALS, ELLIPTIC CURVES OR THE
  ECDLP.** The measured quantity is identical — `[0,0,0,0]` — for the Semaev
  arm, the support-matched null, the topology-matched null, the singular
  non-curve cubic **and an ordinary random quartic pair**. On this quantity the
  twin is not distinguishable from a generic pair of quartics. The nearby
  object's agreement is *forced*: `A` and `B` occur only in monomials of total
  degree ≤ 3, so the degree-4 parts of the generic-curve and singular-cubic
  generators are equal monomial for monomial.
- **The supportable closure is narrow: the route through THIS PARTICULAR TWIN is
  closed at the tested cells.** It does **not** follow that "the 8·dim V law has
  no prime-field analogue", because the DESCENDED prime-field object was never
  built. KN-FIND-006 states its law only for FULL systems (exactly `n` quadrics
  plus `n` cubics in `nb = 2n` variables, `k = 3..7`) and records `8*dim(V)` as
  measured-exact, not derived; the twin is not a full system at any `s`.
- The identification that makes the twin a test at all — that `s` instantiates
  KN-FIND-006's `k` — is **asserted, not derived**, and is unnumbered. In
  KN-FIND-006 `k` is simultaneously `dim V`, the number of descended equations
  per `S_3`, and the variable count per leaf; the twin reproduces only the third
  and sets the second to 1, and the generator-count ladder shows the second is
  the load-bearing one at `p = 2`.
- **The baseline is part rigorous and part heuristic, and the record must not
  call the whole of it derived.** RIGOROUS: with exactly two degree-4 generators
  there is one Koszul pair and no third generator, so `koszul(D) = 0` for
  `D < 8` and 1 at `D = 8` is exact and cannot over-count, and the Frobenius
  family is empty for `p > 2`. HEURISTIC: that the rank *attains* `rows − koszul`
  is Fröberg/Bardet–Faugère–Salvy genericity, i.e. HEUR-001, and it is FALSE for
  the four structured objects above. **M1 is an empirical branch, not a theorem.**
- The twin's whole trivial-syzygy budget at `D = 8` is **one** Koszul pair,
  against 78 at the binary calibration cell. The twin is measured where almost
  nothing can happen for any pair of quartics; the exclusion is real and the
  space of relations it excludes is small.
- **HEUR-002 was NOT TESTED.** With every observation 0, the p-ladder spread is
  0, the curve spread is 0 for arithmetic reasons and the affine fit is
  degenerate (`rss = 0`, a point interval). A vacuous confirmation.
- The binary calibration reproduces under two independent implementations and
  **both** conventions — graded `[0, 1, 31]`, cumulative `[0, 1, 32]`, and the
  `D = 5` cumulative 1322 — and both integers are KN-FIND-006's own. A record
  must not write "the same convention returned 31 there and 0 here": the
  calibration headline is `deficit_graded` and the twin headline is
  `deficit_pairwise`. The calibration fixture is a **same-construction**
  known-answer test, not a byte-exact replay (Sage is absent on the host; the
  system was rebuilt in pure Python and every archived invariant reproduces).
- `NULL-TOPOLOGY` is not a distinct control at `E2` at any tested `s` (`E2`'s
  support **is** its whole topology box) and is a near-duplicate at `E1`, so the
  null band width is 0 by construction and "inside the band" reduces to "exactly
  0". All six curve templates are identical, so the null arms carry no curve
  variability.
- The deciding cell replicates over **11 distinct generator systems, not 12**
  (the generators depend on `(p, A, B, x_R)` alone — `u` is never substituted —
  and one curve's two targets share `x_R`).
- `"The twin at p = 2"` is not a characteristic-only perturbation: the digit
  leaves collapse to their lowest bit (six of nine digit variables vanish at
  `s = 3`) and the generator degree drops from 4 to 3. `p = 2` is not a member
  of the twin's `(s, p)` family.
- No cost claim, no exponent, no attack, no security consequence. The cost image
  of even a nonzero deficit is zero unless the solve bit flips, and `sol(D)` is
  False at every recorded `(cell, arm, D)`.

## Evidence

- `EV-PFDR-e67f06` (evidence) and `DEC-20260904-63a809` (decision, `support`).
- EXP-PFDR-20ee58, fourteen `completed_valid` runs, 246 twin draws; **every
  joint of both blinded reviewers holds**, and the non-attribution comes from
  the proves-too-much control rather than from a broken joint.
- Independent recomputation: the deciding-cell deficit vector re-derived
  **blind** (no manifest opened before the phase boundary) and the binary
  calibration recomputed under independent GF(2) code (TASK-20260904-a7eead);
  870 of 870 deficit entries regenerated from the raw records, the Koszul-line
  kernel identified, the sensitivity ladder and the generator-count threshold
  computed (TASK-20260904-0d66e3).
- The instrument-adequacy pattern used here is recorded as a reusable control in
  `KN-TECH-1cd4bb`; the unbuilt successor object is `KN-OPEN-d6ad3f`.
