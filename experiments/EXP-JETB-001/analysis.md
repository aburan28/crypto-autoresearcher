# EXP-JETB-001 analysis — D1 generic-model barrier for jet-augmented relation channels

**Primary run:** `RUN-JETB-001-a` (valid). **Lineage:** `RUN-JETB-001-f0` (failed_infrastructure,
implementation bug, no measurements — not evidence); `RUN-JETB-001-b` (valid, superseded by `-a`,
which adds the Newton regime split and fixes one JSON serialization defect; all shared
measurements bit-identical). Budget used: 3 of 8 allowed runs; total wall ≈ 17.4 s of 2400 s.

## 1. The model (formalization, standing in for the theory note)

Augmented generic model: Shoup generic group of prime order plus a *tangent oracle* answering
ε-consistency queries on the x-only summation variety S = 0: given a candidate point x and free
tangent parameters t, does S(x + εt) = 0 hold over F_p[ε]/ε²? Since

  S(x + εt) = S(x) + ε·(∇S(x)·t),

the ε-block is a **homogeneous** F_p-linear system in t (t = 0 always solves it). Hence, under
free tangent lifts, ε-consistency holds **iff** S(x) = 0, and the solution space ker ∇S(x) is by
definition the Zariski tangent space of the relation variety at x. **Simulability prediction: the
jet query adds no information beyond the zeroth-order relation structure.** For the addition law
itself, formal-group linearization says the first-order part of dual-number point addition is
Lie-algebra addition of ω-scalars (ω = dx/(2y) the invariant differential) — a simulable,
encoding-independent linear operation.

Frozen predictions (specification.yaml): P1 screen ≡ zeroth-order per tuple; P2 σ_true = 1;
P3 leakage = 0; P4 σ_pass/p_m = 1; P5 ε-solution dim = (#vars)−1 smooth / (#vars) singular;
P6 formal-group linearity exact; P7 one-step jet-linear (Newton) solve hit rate ~ 0, ≤ 2/p.
**P7 as frozen turned out imprecise — see §4.**

## 2. Setup (frozen)

p ∈ {101, 211, 431}; seeds 20260717..20260722 (fresh ordinary, non-anomalous, nonsingular
short-Weierstrass curve per instance, largest prime factor ℓ of #E with ℓ² ≥ #E, R in the
ℓ-subgroup); x-interval factor bases, B = max(8, ⌈√(2p)⌉) = 15/21/30, one min-y lift per x.
Varieties: m=2 target form S_R(x1,x2) = S3(x1,x2,x_R) over unordered FB pairs (i≤j); m=3 form
S3(x1,x2,x3) over unordered FB triples (i≤j≤k). Screen implemented two independent ways
(x-only Semaev jet with exact kernel linear algebra; dual-number addition chain with
constructively verified tangent-lift witnesses). 18 independent curve instances.

## 3. Measured results (pooled over 6 seeds per prime; per-seed rows in raw.json)

### m=2 variety S_R (FB pairs)

| p | tuples | true | p_m | σ_pass | σ_true | leakage | agree(P1) | σ_pass/p_m | ε-dim |
|---|---|---|---|---|---|---|---|---|---|
| 101 | 720 | 29 | 0.04028 | 0.04028 | 1.0 | 0.0 | 1.0 | 1.0 | {1: 29} |
| 211 | 1386 | 24 | 0.01732 | 0.01732 | 1.0 | 0.0 | 1.0 | 1.0 | {1: 24} |
| 431 | 2790 | 15 | 0.005376 | 0.005376 | 1.0 | 0.0 | 1.0 | 1.0 | {1: 15} |

### m=3 variety S3 (FB triples)

| p | tuples | true | p_m | σ_pass | σ_true | leakage | agree(P1) | σ_pass/p_m | ε-dim |
|---|---|---|---|---|---|---|---|---|---|
| 101 | 4080 | 134 | 0.03284 | 0.03284 | 1.0 | 0.0 | 1.0 | 1.0 | {2: 134} |
| 211 | 10626 | 200 | 0.01882 | 0.01882 | 1.0 | 0.0 | 1.0 | 1.0 | {2: 200} |
| 431 | 29760 | 277 | 0.009308 | 0.009308 | 1.0 | 0.0 | 1.0 | 1.0 | {2: 277} |

### Jet-linear (Newton) solve probe — one step from random starts on true relations

| p | regime | relations | starts | hits | σ_solve | prediction |
|---|---|---|---|---|---|---|
| 101 | non-degenerate | 28 | 2772 | 62 | 0.02237 | 2/p = 0.01980 |
| 101 | degenerate x1 = x_R | 1 | 100 | 100 | 1.0 | 1.0 (linear equation) |
| 211 | non-degenerate | 23 | 2289 | 24 | 0.01048 | 2/p = 0.009479 |
| 211 | degenerate x1 = x_R | 1 | 100 | 100 | 1.0 | 1.0 (linear equation) |
| 431 | non-degenerate | 15 | 1496 | 8 | 0.005348 | 2/p = 0.004640 |

### Other batteries

- Exhaustive p=101 (seed 20260717), all 10,201 pairs (x1,x2) ∈ F_p²: screen ≡ zeroth-order
  (0 mismatches); 2,025 baseline-checked pairs: S-test ≡ point arithmetic (0 mismatches);
  86 true relations, all ε-dim 1, 0 singular.
- Formal-group probe (P6): 1,745 tested random (P,Q,a,b) across 18 instances — zeroth-order
  failures 0, ω-linearity failures 0, swap-invariance failures 0 (55 skipped degenerates).
- Chain screen: 18 true (+,+)-chain relations, all constructively witnessed over dual numbers
  (0 failures; 4 skips on 2-torsion-lift degenerates).

## 4. Deviation from a frozen prediction — recorded, with full arithmetic

Frozen P7 ("Newton hit rate ~ 0, bounded by 2/p") is **imprecise**: the pooled σ_solve
(0.0564 at p=101, 0.0519 at p=211) exceeds 2/p. Cause, established exhaustively
(debug_newton.sage, all 101 starts enumerated): S_R(x1, z) = (x_R − x_1)²·z² + … drops from
degree 2 to **degree 1 exactly when x1 = x_R**, and one Newton step solves a linear equation
from every start. On non-degenerate fibers the exhaustive hit set is **exactly the 2 root-starts**
(2/p). The degree drop is zeroth-order-observable (a leading-coefficient vanishing), so the
excess carries no jet information. Non-degenerate ratios measured/expected: 1.13 (p=101),
1.11 (p=211), 1.15 (p=431) — consistent with Poisson noise at these counts (expected hits
≈ 55/22/7). **Suggested amendment (for the Coordinator):** P7 should read "hit rate = 2/p on
non-degenerate fibers; rate 1 on the x1 = x_R degree-drop fiber, which is zeroth-order
observable". This does not change the direction of the result: no non-simulable operation
was observed anywhere.

## 5. Controls

- **Positive control — PASS.** Semaev S-evaluation reproduces point-arithmetic relation truth
  on every one of 49,362 FB candidate tuples (m=2: 4,896; m=3: 44,466) and all 10,201
  exhaustive p=101 pairs (2,025 baseline-checked): 0 mismatches. All 67 constructed relations
  (P2 = R − P1 with x in FB) pass both the zeroth-order test and the tangent screen,
  with dual-number witnesses verified.
- **Negative control — PASS.** Leakage = 0 among all non-relation tuples, including 3,600
  uniform random pairs with explicit dual-repair tests (no ε-lift can repair a zeroth-order
  failure).

## 6. Unexpected observations (rule 8)

1. RUN-JETB-001-f0 crashed (ZeroDivisionError at a 2-torsion sum, y3 = 0) and review showed my
   first linearity convention (raw dx-components) was mathematically wrong; the correct law
   adds ω-scalars a/(2y). Fixed; infrastructure failure, not evidence.
2. The x1 = x_R degree-drop fiber (§4) — the only place a one-step jet-linear solve succeeds
   systematically, and it is zeroth-order-determined.
3. No singular true relation occurred anywhere (~59.5k tuples + exhaustive): all summation
   varieties were smooth at every tested F_p-point; ε-dim histograms are single-bin
   (1 for m=2, 2 for m=3, exactly the predicted smooth dimensions).
4. At p=101, seeds 20260717/18/19 independently produced curves of the same order N = 88
   (ℓ = 11); seeds 20/21 produced N = 111 (ℓ = 37). Instances remain independent (independent
   seeded searches, different curves A,B); recorded for transparency.
5. 43 Newton starts skipped (∂_2 S_R = 0 at the random base point); 55 formal-group probes
   skipped (degenerate random draws). All skips counted in raw.json.

## 7. Gate arithmetic (numbers, not verdict)

D1 promotion gate: *proved simulation theorem, or an explicit non-simulable operation validated
at all three toy sizes.* Toy-check contribution:

- Screen/zeroth-order mismatches: **0 / 0 / 0** at p = 101 / 211 / 431 (49,362 FB tuples +
  10,201 exhaustive pairs + 3,600 random negative pairs).
- σ_true: **1.0 / 1.0 / 1.0**. Leakage: **0 / 0 / 0**. σ_pass/p_m: **1.0 / 1.0 / 1.0**.
- ε-solution dims: predicted smooth values at 100% of true relations (both varieties).
- Formal-group linearity: **0 failures in 1,745 probes** (+ swap-invariance exact).
- σ_solve: matches the simulable-model prediction after the (zeroth-order-observable)
  degree-drop correction: 2/p on non-degenerate fibers, 1.0 on degenerate fibers.
- No explicit non-simulable operation was found at any of the three toy sizes; conversely this
  is **toy-scale consistency evidence, not a proof** of the simulation theorem.

## 8. Scope and limitations

Toy prime fields p ≤ 431 (~2^9), x-interval factor bases B ≤ 30, m ∈ {2,3} Semaev varieties,
single-lift (min-y) convention, 6 seeds per size. Behavior established only on the tested toy
distribution (rule 7): it may motivate the proof-track simulation theorem but does not
establish any P-256-scale statement. Model-level closure requires the actual theorem
(proof track), which is outside this experiment's scope.
