# Refutation note — RUN-HZM-001-c-primary-gate-only (derivation-note grade)

Record: authored 2026-09-08 by TASK-20260908-79b1b3 (Coordinator
composition) under REVIEW-PLAN-BATCH-98edec, per
`docs/claims-and-verification.md` "Refutation artifacts". Grade:
**derivation note** — closed-form algebra, machine-checked in exact
arithmetic at the exact points, independently re-derived blind
(TASK-20260908-422afa, freeze 033b76cf7b) and adversarially probed
(TASK-20260908-5d29c2, freeze 93ebc69381).

## Object refuted

The gate-survival leg of H-HZM-001: "under its own pinned published
formulas ... its fully charged expected work per solved target is
strictly below the frozen Pollard-rho comparison bound ceil(N^(1/2))"
at BOTH primary gate sizes (12,1) and (16,1)
(experiments/EXP-HZM-001/specification.yaml success_criterion).

## The pinned model (frozen 2026-07-27, re-approved 2026-09-06)

q(N,L,d) = 1-(1-1/N)^M; M = binom(L+d,d); H = binom(L+d,d-1);
charged expected per-target work >= H/q + setup + reconstruction +
verification; frozen rho bound = ceil(N^(1/2)) group-operation-
equivalents (KN-TECH-005 convention). Gate semantics: survive only if
STRICTLY below; meets-or-exceeds closes (falsification_criterion(b)).

## Derivation (from the blind re-derivation, exact arithmetic)

At d=1: H = binom(L+1,0) = 1 (base-invariant: binom(n,0)=1 for every
nonnegative n, so the l-vs-l' manuscript base ambiguity — the prior
round's inconclusive_misalignment — cannot affect this leg); M = L+1;
m := L+1; charged = 1/q = 1/(1-((N-1)/N)^m).

**Exact gate characterization.** For s = ceil(sqrt(N)), all quantities
positive, so every step is an equivalence:

charged >= s  <=>  q <= 1/s  <=>  ((N-1)/N)^m >= (s-1)/s  <=>
**s(N-1)^m >= (s-1)N^m**.

**Bernoulli lower bound.** charged >= N/m = N/(L+1) — exactly the
spec's audit bound N*d/(L+1) at d=1.

**Sufficient condition.** If s*m <= (s-1)^2 then charged > s. (From
N > (s-1)^2 and Bernoulli: charged >= N/m > (s-1)^2/m >= s.)

**Boundary and failure of the naive condition.** The boundary case is
N = m^2 (witness N=169, L=12: charged = 91733330193268616658399616009/
6811242446084424039884741641 ~= 13.4679 >= 13 = ceil(sqrt(169))). The
naive condition (L+1)^2 <= N is NOT sufficient (counterexample N=10,
L=2: charged = 1000/271 ~= 3.6900 < 4).

## Machine-checked evaluation at the two primary gate points

| point | m | exact test s(N-1)^m >= (s-1)N^m | sufficient cond. s*m <= (s-1)^2 | charged (exact) | rho bound | verdict |
|---|---|---|---|---|---|---|
| N=4096, L=12, d=1 | 13, s=64 | 5827479484036299113984741427568344645234375000000 >= 5754662696990430240427009028820364389895234387968: TRUE | 832 <= 3969: TRUE | 2^156/(2^156-4095^13) ~= 315.53872449119024 (float64 pipeline: 315.5387244911908) | 64 | FAILS gate (ratio 4.93) |
| N=65536, L=16, d=1 | 17, s=256 | 1942165026563222741278700503292981756185920726734641110137322219415997460937500000000 >= 1935080341865472316736182758749989535913334937337092101246922517513361690341125652480: TRUE | 4352 <= 65025: TRUE | 2^272/(2^272-65535^17) ~= 3855.52943330669 (float64 pipeline: 3855.5294333064226) | 256 | FAILS gate (ratio 15.06) |

Precision disclosure (blind finding): the committed floats are
BIT-EXACT reproductions of the float64 evaluation pipeline
1.0/(1.0-(1.0-1.0/N)**M), verified by simulation; they differ from the
correctly-rounded doubles of the exact rationals by 10 ulp (point 1)
and 588 ulp (point 2, amplified by cancellation at N=65536). This is
evaluation-precision rounding, not a mathematical discrepancy; every
integer/boolean field matches exactly and the gate verdict is
unaffected (margins are 4.93x / 15.06x).

## Control (proves-too-much)

Passing-point control (blind machinery, same code path): N=64, L=16,
d=1: charged = 5070602400912917605986812821504/1190981050261441216384181238721
= 4.257500486510538 < 8 = ceil(sqrt(64)) => survives = TRUE,
machinery_sane = true. The verdict machinery is not constant-false.
Sensitivity: substituting the bound q <= min(1,M/N) for the exact
formula changes charged to 4096/13 = 315.0769230769231 and 65536/17 =
3855.0588235294117 (deltas 0.4618 / 0.4706) — the committed figures
come from the exact pinned formula; both versions fail the gate, so
the verdict is insensitive to the substitution. Red-team probe (A6):
the rho baseline itself (cost = bound) is correctly classified
meets-or-exceeds, and the same closure argument run against the
passing point does not close it.

## Asymptotic corollary (conditional algebra, not a measurement)

For L = Theta(log N) (the spec's declared conditional-algebra regime),
charged >= N/(L+1) = N^(1-o(1)) > N^(1/2) for all sufficiently large
N: the gate is decisively failed asymptotically UNDER THE PINNED
FORMULAS. Per specification.yaml scale_relevance, this is a conditional
algebra statement from the pinned formulas, not a toy measurement, and
not a theorem about the route's actual cost independent of its model.

## Lower-bound direction (why omission cannot rescue)

The spec's own formula states charged expected per-target work >=
H/q + setup + reconstruction + verification. H/q is therefore a LOWER
bound on the fully charged cost; the eight omitted charged_stages can
only add cost. Failure at the bottleneck term implies failure of the
fully charged cost. Units: H/q is expected signature constructions
(per-attempt cost H x inverse success probability 1/q); the comparison
to the rho bound's group-operation-equivalents rests on the declared
poly(log N) bit-cost assumption, and the closure rests on the EXPONENT
gap N^(1-o(1)) vs N^(1/2), which polylog factors cannot reverse
(spec conversion_rule; red-team A3 boundary RT98-O2 adopted).

## Independent support chain

1. Producer run RUN-HZM-001-c-primary-gate-only (snapshot 3794391b64).
2. Coordinator re-derivation inside DEC-20260907-5b500d (same figures,
   by actually running the code).
3. Validator VAL-20260907-612101 RECOMP-1/2/3 (fresh process, literal
   command, first-principles algebra; bit-for-bit).
4. Blind J2 (TASK-20260908-422afa): exact-rational derivation, exact
   gate characterization, bit-exact float64-pipeline simulation,
   passing-point control, sensitivity check.
5. Red team J1 (TASK-20260908-5d29c2): A1-A6 all hold; even the most
   route-favorable base-2L reading of M fails both gates (164.32 vs
   64; 1986.42 vs 256).

## Scope of this refutation (rule 6)

Refuted: gate survival at d=1 under the pinned published formulas, at
the two primary gate sizes, and — as conditional algebra under the
same pinned formulas — in the L = Theta(log N) regime. NOT refuted:
the external publications' claims beyond their pinned model; the
general d in {2,3} manuscript-alignment question (base ambiguity live;
inconclusive_misalignment stands); the enumeration leg (never run);
any statement about standardized curves. No sub-rho route is certified
by this note; it closes one route under its own model.
