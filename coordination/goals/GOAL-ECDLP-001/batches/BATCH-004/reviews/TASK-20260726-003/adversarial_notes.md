# Adversarial Notes — TASK-20260726-003

**Reviewer:** Independent non-originating session, `review-xhigh` policy
**Targets:** H-IC-001 hypothesis, EXP-IC-001 specification
**Date:** 2026-07-26
**Verdict:** REVISE

---

## 1. Snapshot validation

Commit `6a4f0705` is verified: reachable from HEAD, parent `3bc44688`,
exactly 3 changed paths, SHA-256 values match the receipt for both
`ledger/hypotheses/H-IC-001.yaml` and
`experiments/EXP-IC-001/specification.yaml`. No issues.

---

## 2. The calibration is a mismatched ratio (BO-1, blocking)

### The mechanism

`group_ops_per_second = group_operations / wall_seconds` is the calibration
factor that converts Groebner wall-time to group-operation equivalents.

### What `group_operations` actually counts

In `harness/rho.py`, the `ops` counter is incremented **only** inside the
`walk()` function (line 51: `ops += 1`), once per walk step. It does **not**
count:

- **Precomputation** (lines 41-45): 32 branch steps, each computing
  `E.mul(c, P)` and `E.mul(d, Q)` via double-and-add (~`log2(n)` group ops
  per `E.mul`). This is ~`32 * 2 * log2(n)` uncounted group ops.
- **Restart initialization** (lines 55-58): up to 12 restarts, each doing
  `E.mul(a0, P)` and `E.mul(b0, Q)` — ~`2 * log2(n)` uncounted group ops
  per restart.
- **Final verification** (line 69): `E.mul(int(k), P) == Q` — ~`log2(n)`
  uncounted group ops.

### What `wall_seconds` actually measures

In `harness/fixed_curve_preprocessing.py` (`_run_rho`, lines 48-55),
`started = time.time()` before `rho.solve(inst)` and
`finished = time.time()` after. So `wall_seconds` includes precomputation +
restarts + walk + verification — the **entire** `rho.solve()` call.

### The mismatch

`group_ops_per_second = walk_steps / (precomp_time + restart_time + walk_time + verification_time)`

This is not a group-operation rate — it is a walk-step rate diluted by all
non-walk overhead.

### Numerical magnitude

| Bits | sqrt(N) ~  | Uncounted precomp ops | Overhead fraction |
|------|-----------|----------------------|-------------------|
| 8    | 16        | ~544                 | **97%**           |
| 12   | 64        | ~800                 | **93%**           |
| 16   | 256       | ~1,056               | **81%**           |
| 20   | 1,024     | ~1,312               | **56%**           |
| 24   | 4,096     | ~1,568               | 28%               |
| 28   | 16,384    | ~1,824               | 10%               |
| 32   | 65,536    | ~2,080               | 3%                |
| 36   | 262,144   | ~2,336               | 1%                |

At 8-12 bits, the calibration factor is diluted by >90%. The
`group_ops_per_second` value at those bit sizes is less than 10% of the
true group-op rate. Any T_desc_gops value derived from this calibration at
small bit sizes is unreliable by an order of magnitude.

The spec's `Calibration reliability check` control flags instances where
`rho_group_operations < 100`, but this threshold is based on the walk-step
count (the biased quantity), not on total computational work. A run with
50 walk steps and 3,000 precomputation group ops has `group_operations =
50` and is flagged, but the real issue is that `wall_seconds` includes
3,050 group ops of work while only 50 are counted.

### Bias direction

The underestimate makes T_desc_gops smaller, biasing toward
T_desc < sqrt(N) (K* finite). This contradicts the hypothesis prediction
at small bit sizes (T_desc >= sqrt(N)), so it complicates rather than
uniformly supports the hypothesis. At large bit sizes (28-36), the bias
is <10% and does not materially affect the conclusion.

### Fix

Count ALL group operations in `rho.py` (add `ops +=` increments in
precomputation, restart initialization, and verification), or measure
`wall_seconds` for the walk phase only (start timer after precomputation,
stop before verification).

---

## 3. The conversion is apples-to-oranges (BO-2, blocking)

### The fundamental problem

Groebner basis computation does **polynomial arithmetic**: Buchberger
S-pair reduction, polynomial multiplication, and GCD over `F_p[x1, x2]`.
Rho does **group arithmetic**: modular inversion, multiplication, and
addition on `E(F_p)`.

The calibration assumes wall-time is a fair common currency between these
two primitives. It is not. Wall-time depends on:

1. **The operation**: polynomial reduction vs point addition have
   fundamentally different costs per "unit of mathematical work."
2. **The implementation**: sympy's Buchberger is an unoptimized
   textbook algorithm. A production F4/F5 implementation (e.g., Magma,
   FLINT) could be 100-1000x faster on the same polynomial system.
   Python's double-and-add is also unoptimized.
3. **The overhead**: Python interpreter overhead, memory allocation,
   garbage collection affect both implementations differently.

The ratio `groebner_seconds * group_ops_per_second` is therefore a ratio
of two implementation overheads, not a comparison of mathematical costs.
The same experiment with a different Groebner implementation could give
a T_desc_gops value that differs by orders of magnitude, potentially
reversing the K* finiteness conclusion.

### What the hypothesis mechanism claims

The mechanism states: "the Groebner solve time is dominated by the
polynomial operation count (fixed by degree 14, 2 variables), which is
independent of p." This is a claim about **theoretical** operation count.
But the **measured** wall-time (and thus T_desc_gops) is
implementation-bound. The prior evidence (EV-FCP-002/003) supports
~0.04-0.05s across 16-36 bits **with sympy on macOS arm64**, but this is
an artifact of sympy's Buchberger being dominated by fixed polynomial-
structure overhead at toy scale, not a mathematical invariant.

### The trivial-ideal caveat

Both EV-FCP-002 and EV-FCP-003 note: "No decompositions found at any bit
size; all Groebner solves return trivial ideals. Cost for non-trivial
systems may differ." The ~0.04-0.05s timing is for computing the Groebner
basis of a system with **no solutions** (the basis is `[1]`). When a
decomposition **does** exist (at 8-12 bits), the Groebner basis is non-
trivial and the computation may follow a different branch of Buchberger's
algorithm, with potentially different cost. T_desc at 8-12 bits (with
solutions) may not be comparable to T_desc at 16-36 bits (without
solutions).

### Fix

- Report absolute wall times (groebner_seconds, rho_wall_seconds) alongside
  group-op equivalents, so the implementation-bound nature is visible.
- Add a sensitivity analysis: if feasible, run the same decomposition with
  a faster Groebner implementation and compare.
- Label the T_desc_gops values as implementation-bound throughout.
- Report T_desc separately for `decomposition_found=true` and
  `decomposition_found=false` instances.

---

## 4. The S_rel heuristic is wrong by factor B (BO-4, blocking)

### The heuristic

The hypothesis and spec use:

```
S_rel = B * (N/B)^{m-1} * T_desc_gops
```

For m=2: `S_rel = N * T_desc_gops`.

The stated reasoning: "the decomposition probability per random point is
approximately (B/N)^{m-1} = B/N for m=2, so the expected number of attempts
per relation is N/B, and B relations require B * (N/B) = N attempts."

### Why this is wrong

For m=2 (S_3 decomposition), a random target R decomposes as
R = P1 + P2 where P1, P2 are factor-base points. The factor base has B
x-coordinates. The number of ordered pairs (x1, x2) is B^2. For fixed x1,
S_3(x1, x2, xR) = 0 is degree 2 in x2, giving ~2 roots in F_p. The
probability that a random x2 in F_p is a root is ~2/p ~ 2/N. The
probability that x2 is also in the factor base (size B) is
`B * (2/N) = 2B/N`. With B choices for x1, the total probability per
random target is `B * (2B/N) = 2B^2/N`.

The heuristic's `(B/N)^{m-1} = B/N` gives a probability of B/N. The correct
probability is ~2B^2/N. The heuristic **underestimates the probability by
factor ~2B (= 28)** and thus **overestimates S_rel by factor ~2B**.

### Correct formula

```
S_rel = B * (N / (2B^2)) * T_desc_gops = (N / (2B)) * T_desc_gops
```

For B=14: `S_rel = (N/28) * T_desc_gops`, not `N * T_desc_gops`.

### Bias direction

Overestimating S_rel by factor ~28 inflates S*T^2 by the same factor,
biasing toward S*T^2 >= N (the hypothesis's "no non-generic advantage"
prediction). If the correct S_rel were used, S*T^2 would be 28x smaller,
potentially changing the conclusion at some bit sizes.

### Why the error likely occurred

The formula `(B/N)^{m-1}` gives the probability that **one specific**
factor-base choice (out of B^{m-1} possible choices for the first m-1
variables) leads to a valid decomposition. It is the probability per
individual check, not per Groebner solve. But the cost T_desc is for a
**full Groebner solve** that checks all B^{m-1} choices simultaneously.
The heuristic mixes the per-check probability with the per-solve cost.

### Fix

Use `S_rel = (N / B^{m-1}) * T_desc_gops`, which for m=2 gives
`S_rel = (N/B) * T_desc_gops`. Alternatively, measure S_rel directly at
8-12 bits where decompositions are found.

---

## 5. The S*T^2 >= N criterion is tautological (BO-5, blocking)

### The derivation

Given the heuristic `S_rel = N * T_desc_gops` (m=2):

```
S = S_rel + S_LA ≈ S_rel = N * T_desc_gops
T = T_desc_gops + T_verify ≈ T_desc_gops  (T_verify = 2, negligible)

S * T^2 = N * T_desc_gops * T_desc_gops^2 = N * T_desc_gops^3
```

The success condition `S * T^2 >= N` becomes:

```
N * T_desc_gops^3 >= N
T_desc_gops^3 >= 1
T_desc_gops >= 1.0
```

### Why this is tautological

T_desc_gops >= 1.0 means the Groebner solve takes at least as long as one
group operation. For sympy's Buchberger on a degree-14 polynomial system
in 2 variables, the wall time is ~0.04-0.05s (from EV-FCP-002/003). Even
with the most dilute calibration factor (~10 ops/sec at 8 bits),
T_desc_gops = 0.04 * 10 = 0.4, which is close to 1.0. At any bit size
where the calibration is reliable (>= 16 bits), the calibration factor is
>100 ops/sec, giving T_desc_gops = 0.04 * 100 = 4.0 >> 1.0.

So S*T^2 >= N is **guaranteed by the formula** at all bit sizes where the
calibration is reliable. The experiment cannot observe S*T^2 < N because
the heuristic makes it impossible by construction.

### With the corrected heuristic

Using `S_rel = (N/B) * T_desc_gops`:

```
S * T^2 = (N/B) * T_desc_gops^3
S * T^2 >= N  <=>  T_desc_gops >= B^{1/3} ≈ 2.41
```

Still almost always true (T_desc_gops = 4.0 >> 2.41 at 16+ bits). The
tautological nature persists.

### The alternative outcome is unreachable

The alternative outcome (S*T^2 < N, triggering the "non-generic signal"
review path) requires T_desc_gops < 1.0 (heuristic) or < 2.41 (corrected).
Both are nearly impossible for sympy Groebner. The experiment is
structurally biased toward the "no non-generic advantage" conclusion.

### Consequence

The experiment's **novel contribution** — comparing the crossover cost to
the generic S*T^2 = N preprocessing frontier — is vacuous. The comparison
is determined by the heuristic formula, not by empirical data. The only
genuinely testable part is the K* finiteness question (T_desc vs sqrt(N)),
which is a relatively straightforward extension of EV-FCP-002/003.

### Fix

Either:
1. **Measure S_rel directly** at 8-12 bits and use the measured value
   (extrapolated to larger bit sizes) instead of the heuristic.
2. **Drop the S*T^2 frontier comparison** and test only K* finiteness.
3. **Add a sensitivity analysis**: compute S*T^2 under the heuristic,
   the corrected formula, and the measured S_rel (at 8-12 bits). Report
   all three. If they disagree, the heuristic matters; if they agree, the
   conclusion is robust.
4. If the S*T^2 comparison is kept, **label it as a heuristic calculation**,
   not an experimental result.

---

## 6. S_rel is never measured (BO-6, blocking)

### The problem

At toy scale (bits >= 16), B^2/N << 1, so no decompositions are found and
no relations can be collected. The entire S (dominated by S_rel) is
**estimated**, not measured. The S*T^2 comparison is a formula-driven
result, not an empirical observation.

### The missed opportunity

At 8-12 bits, decompositions ARE found:

| Bits | B^2/N      | Decompositions found? |
|------|-----------|----------------------|
| 8    | 0.77      | Yes (likely)          |
| 12   | 0.0048    | Possibly              |
| 16   | 0.00030   | No                    |

At 8 bits, the decomposition probability is ~77%, so relation collection
should succeed quickly. The experiment could:

1. Run relation collection at 8 bits: pick random points, decompose, count
   attempts until B+margin verified relations are obtained.
2. Measure the total wall time and total attempts → empirical S_rel.
3. Compare measured S_rel to the heuristic estimate at 8 bits.
4. If the heuristic is off by factor B (as predicted), flag this and
   adjust the estimate for larger bit sizes.

The spec does not include this measurement. This is a significant gap
because it means the S*T^2 comparison rests entirely on an unvalidated
heuristic.

### Fix

Add a direct S_rel measurement at 8-12 bits as a supplementary run type.
The `decomposition_found` metric is already collected per target; add a
relation-collection mode that runs until B relations are found and
records the total cost.

---

## 7. The calibration factor grows 10,000x across the tested range (NBO-1, non-blocking)

### Observation

The calibration factor `group_ops_per_second` grows from ~10 ops/sec
(8-bit, estimated) to ~100K ops/sec (36-bit, estimated) — a ~10,000x
increase. This growth is driven by:

- At small bit sizes: Python overhead and precomputation dominate
  wall_seconds, diluting the group-op rate.
- At large bit sizes: the walk dominates wall_seconds, and the group-op
  rate approaches the true computational rate.

### Consequence

T_desc_gops = groebner_seconds * group_ops_per_second grows with bit size
even if groebner_seconds is constant. The hypothesis attributes the
T_desc/sqrt(N) decrease to "T_desc in group-ops grows slowly while sqrt(N)
grows exponentially," but the "slow" growth of T_desc_gops is dominated by
the calibration factor's growth, not by any mathematical property of the
Groebner computation.

The experiment is essentially measuring **how fast rho's
group_ops_per_second grows with bit size** (a property of the rho
implementation and its overhead structure), not how the Groebner cost
compares to sqrt(N) mathematically.

### Fix

Report the calibration factor at each bit size and analyze its growth
rate. Show T_desc_gops / sqrt(N) alongside groebner_seconds / rho_wall_seconds
to distinguish the calibration artifact from the mathematical signal.

---

## 8. Claim tier mislabeling (NBO-3, non-blocking)

The experiment tests bit sizes 8-36. Per `docs/claims-and-verification.md`:

- `toy`: max field bit size <= 32
- `medium`: 32 < max field bit size <= 96

The 36-bit instances exceed the toy tier ceiling. The hypothesis says "toy
prime fields of 8-36 bits" and the interpretation_limits say "Toy scale
only (max 36 bits)," both of which are incorrect for the 36-bit instances.

This is a pre-existing pattern (EV-FCP-003 also labels 36-bit evidence as
`claim_tier: toy`), but it should be corrected. The claim tier for evidence
from this experiment should be `medium` (or the minimum of toy and medium
= toy for the <=32-bit subset and medium for the 36-bit subset).

---

## 9. Summary of the adversarial position

The experiment has a **valid core** (measuring T_desc vs sqrt(N) to
determine K* finiteness at toy scale) wrapped in a **vacuous shell** (the
S*T^2 frontier comparison, which is tautological given the heuristic).

The five blocking objections are fixable:

1. **BO-1**: Fix the rho calibration to count all group ops (or time the
   walk phase only).
2. **BO-2**: Acknowledge the apples-to-oranges nature and report absolute
   wall times alongside group-op equivalents.
3. **BO-4**: Correct the S_rel heuristic or measure S_rel directly.
4. **BO-5**: Drop or empirically ground the S*T^2 comparison.
5. **BO-6**: Add direct S_rel measurement at 8-12 bits.

The K* finiteness measurement at 28-36 bits (where the calibration bias is
<10%) is sound and should be preserved. The S*T^2 frontier comparison
needs to be either made empirical or removed.

**Verdict: REVISE.** The design should be returned for revision before
execution. The K* finiteness question is worth testing; the S*T^2 frontier
comparison is not, as designed.
