# ATTAINABILITY CHECK — ATTAIN-RR-SMTH-1 (TASK-20260801-012)

Deliverable 1 of 2. Independent review of `experiments/EXP-SMTH-001/specification.yaml`
hash-bound at snapshot commit `d40bf3adde9cefd2b79fafdd56fde7bc61614894`
(TASK-20260801-011, parent `d72163e67`, 3 declared paths).

**VERDICT OF THIS FILE: FAIL. Two independent branch-level unreachability defects.
Recommendation to TASK-20260801-013: DO_NOT_APPROVE.**

Role mapping recorded honestly: the dispatch queue assigns role `reviewer`; this
harness has no dedicated reviewer subagent, so the **red-team subagent serves the
reviewer role**. This session did not author the artifact under review.

---

## 0. Method

Every load-bearing number below was recomputed from scratch in this session, not
checked by reading. Dickman `rho` was obtained by RK4 solution of
`u rho'(u) = -rho(u-1)`, `rho = 1` on `[0,1]`, step `1e-4`, and agrees with the
contract's frozen table to within 0.002 % at `u = 1..6`.

Two of the findings below could not be settled by arithmetic alone, so I ran two
**reviewer-side sanity computations**. These are explicitly NOT EXP-SMTH-001 runs,
produce no evidence record, and discharge nothing:

- `S3-CHECK` — the third summation polynomial on a real toy curve
  `y^2 = x^3 + 7x + 11` over `p = 46349`, 120 factor-base points, all 7260
  unordered half-tuples `i <= j`.
- `NULL-DRY` — the declared OBJ-NULL-UNIF arm executed end to end: 8 independent
  draws of `n = 131328` uniform integers on `[1, p^2]` per cell, each factored with
  sympy 1.14.0, LPF extracted, and pushed through the frozen KS-DS-1, RATE-DS-1,
  TAIL-DS-1 and DECAY-1 rules with the frozen ladders. Seeds 1000–1007. Ranges
  matched to the contract's declared `p^2 / D ≈ 0.515`: `X = 2.147e9` (0.4999·2^32)
  and `X = 5.669e11` (0.5156·2^40).

Scripts are in this session's scratchpad, not in the repository; they are ~60 lines
each and are described precisely enough above to be rebuilt.

---

## 1. Arithmetic the contract asserts — line by line

| Quantity | Contract | Recomputed | Verdict |
|---|---|---|---|
| `C(513,2)` | 131328 | **131328** | CONFIRMED |
| `131328 >= 100000` with 31.3 % margin | yes | yes, +31.328 % | CONFIRMED |
| `C(65,2)`, `C(129,2)`, `C(257,2)` | 2080 / 8256 / 32896 | **2080 / 8256 / 32896** | CONFIRMED |
| least `Bfb` with `C(Bfb+1,2) >= 1e5` | 447 → 100128 | **447 → 100128** (446 → 99681) | CONFIRMED |
| KS threshold `max(0.05, 1.63/sqrt(n))` | `max(0.05, 0.004498) = 0.05` | **0.00449789 → 0.05** | CONFIRMED |
| two-sample threshold `1.63*sqrt(2/n)` | 0.006362 | **0.00636098** | CONFIRMED (rounding) |
| `rho(2..6)` | .30685 / .048608 / .0049109 / .00035473 / .00001965 | agree to 0.002 % | CONFIRMED |
| `n*rho(u)` at u = 2,3,4,5,6 | 40300 / 6384 / 645 / 46.6 / 2.58 | **40298 / 6383.6 / 644.9 / 46.59 / 2.581** | CONFIRMED |
| DECAY-1 threshold `100*rho(6)/rho(2)` | 0.006404 | **0.00640378** | CONFIRMED |
| `n` needed to power u = 6, `30/rho(6)` | 1526718 | **1526718** | CONFIRMED |
| DECAY-1 crossing count at u = 6 | "841 counts" | **258** on a genuine sample | **WRONG (harmless)** |
| TAIL-DS-1 pass probability for a correct null | "about 1 − 1/e" (0.632) | **1/e = 0.368 analytically; 0/16 empirically** | **WRONG (fatal)** |

Two errors, one cosmetic and one decisive.

**The 841 figure.** Crossing DECAY-1 needs `p_hat(u6) > 0.00640378 * p_hat(u2)`.
The contract multiplied the threshold by `p_hat(u2) = 1`, which is the BATCH-020
stand-in's value, not a genuine sample's. For a genuine sample
`p_hat(u2) ≈ rho(2) = 0.30685`, so the crossing count is
`0.00640378 * 0.30685 * 131328 = 258`, not 841. The conclusion the contract draws
survives untouched — a Poisson count of mean 2.58 cannot reach 258 either — but a
number stated in an attainability argument and out by a factor 3.26 is exactly the
class of unchecked arithmetic this duty exists to catch.

**The TAIL figure is the batch-ending one and is treated in §3.**

## 1a. Ladder rungs recomputed from the frozen integer `Bsm`

Every `u` was recomputed as `ln(D)/ln(Bsm)`, never asserted.

| bits | Bsm | recomputed u | rho(u) | n·rho(u) | powered (≥30)? |
|---|---|---|---|---|---|
| 20 (D = 2^40) | 1048576 | 2.00000 | 0.306853 | 40298.4 | YES |
| 20 | 10321 | 3.00001 | 0.0486075 | 6383.5 | YES |
| 20 | 1024 | 4.00000 | 0.0049109 | 644.9 | YES |
| 20 | 256 | 5.00000 | 0.00035472 | 46.59 | YES |
| 20 | 102 | 5.99482 | 0.00001996 | **2.62** | NO |
| 16 (D = 2^32) | 65536 | 2.00000 | 0.306853 | 40298.4 | YES |
| 16 | 1626 | 2.99987 | 0.0486212 | 6385.3 | YES |
| 16 | 256 | 4.00000 | 0.0049109 | 644.9 | YES |
| 16 | 84 | 5.00601 | 0.00034887 | 45.82 | YES |
| 16 | 40 | 6.01286 | 0.00001890 | **2.48** | NO |

The ladders are correctly constructed: every rung lands within 0.013 of its target
`u`. POW-1's exclusion of the u = 6 rung is arithmetically right, and the expected
counts it quotes (2.58) come from `u = 6` exactly rather than from the recomputed
`u = 5.99482 / 6.01286` (true values 2.62 and 2.48). That is a self-inconsistency
with the contract's own "every rho evaluation uses the RECOMPUTED u" policy, but it
changes no decision.

**Rung-level note the contract does not make.** `8*rho(2) = 2.455 > 1`, so at the
u = 2 rung the upper edge of RATE-DS-1 is unattainable by construction: that rung
can only ever fail low. This is benign, but it means "the band is wide" at u = 2 is
true only on one side.

**Rung-level note that is not benign.** `u` is defined from `D`, but the samples live
on `[1, p^2] ≈ 0.515 D`. Recomputing, this alone inflates the true smooth rate above
`rho(u_D)` by factors 1.08, 1.16, 1.27, 1.39, 1.54 at the five rungs (bits = 20).
Finite-`X` effects at `X ≈ 2^32`–`2^40` inflate it much further. NULL-DRY measured, on
a *correct* uniform null, `p_hat / rho(u_D)` of

- bits 16: **1.18, 1.47, 2.13, 4.41, 10.07**
- bits 20: **1.13, 1.30, 1.73, 2.64, 6.87**

So a correct null already sits at 4.4× (bits 16) and 2.6× (bits 20) inside a band whose
edge is 8×, at the u = 5 rung, and **outside the band at the u = 6 rung at bits 16**
(10.07 > 8). The u = 6 breach is harmless only because POW-1 excludes that rung —
but its cause is systematic model bias, not the low count POW-1 attributes it to.
Consequence: POW-1's stated remedy, "n >= 1526718 would power u = 6", is a trap. At
that `n` the u = 6 rung would not become a powered pass; it would become a
**systematic RATE-DS-1 failure** driven by finite-`X` inflation. That remedy is
ranked into BATCH-023 by M-2's `mandatory_companions` and should not be.

---

## 2. Branch-by-branch verdicts

### M-0 — INTEGRITY GUARD — **REACHABLE, and reachable involuntarily (defect)**

Reachable by construction, as claimed: a short sample set, an out-of-range `N_ij`, a
failed factorization re-check, or the 7200 s stop all land here, and the Validator can
force the range check from the raw record. The declared workload (1050624
factorizations) is genuinely capable of hitting the wall clock, though my timing
(sympy `factorint`, ~0.04 ms at 2^32 and ~0.1 ms at 2^40) suggests factorization will
take minutes, not the budgeted 5400 s.

**But M-0 is not merely reachable — under the frozen design it fires with
certainty.** See §4, defect A-2. A guard that fires on every possible outcome is not a
guard; it makes M-1, M-2, M-4 and M-6 jointly unreachable.

### M-5 leg (a) — null fails `bit_size_pass` — **FIRES WITH NEAR-CERTAINTY ON A CORRECT APPARATUS. FATAL.**

The contract offers one route to firing (base-2 logarithms in the rho evaluation) and
that route is fine. What it does not do is check the *negative* side of leg (a) — that
a correct implementation does **not** fire it. It does not, and this is the batch-ending
finding. Full treatment in §3.

Secondary finding on the same leg: at bits = 16 the KS-DS-1 statistic of a *correct*
uniform null against the asymptotic Dickman LPF CDF measured
**0.04838, 0.04850, 0.04875, 0.04889, 0.04911, 0.04972, 0.04980, 0.05061** across the
eight draws, against a threshold of 0.05 — spread ±0.0007, so this is systematic
finite-`X` bias of ≈0.049 sitting on a 0.05 threshold, and **1 of 8 correct nulls
failed KS-DS-1 outright**. At bits = 20 the same statistic is 0.0375–0.0387, safe.
So even setting TAIL aside, leg (a) carries an ≈10 % false-fire probability at
bits = 16 from KS alone, on a knife-edge that any innocuous implementation choice
(handling of `N = 1`, of prime `N`, or a `p` with a slightly different `p^2/D`) can flip.
The contract's claim that "KS-DS-1's threshold 0.05 is eleven times the alpha = 0.01
critical value 0.004498, so a correct sample passes with large margin" compares the
threshold to *sampling noise* and silently omits the *model bias*, which is what
actually consumes it.

### M-5 leg (b) — DV-6 fails to reject — **REACHABLE on both sides; the certificate is weaker than claimed**

Firing side: reachable (an ENC-A that reproduces ENC-B, a tied-support KS bug).
Non-firing side: reachable — ENC-A is a product of two integers below `p`, provably far
smoother than uniform on `[1, p^2]`, so `ks2` is of order 0.1 against a 0.00636
threshold. Both sides sound.

**Objection recorded, not fatal.** DV-6 certifies power against a *smoothness-shifted*
alternative. The alternative DV-4 actually faces is an *equidistribution* defect in the
joint law of `(e_1, e_2)`, which — because ENC-B interleaves two field elements in base
`p` — may perturb the LPF statistic of `N` arbitrarily little while being a gross
departure from uniformity. Passing DV-6 therefore bounds no Type II error in the
direction that matters. The quarantine is honest; the certificate is narrower than the
role assigned to it.

### M-5 leg (c) — DV-7 rejects — **REACHABLE on both sides. Quarantine sound.**

Firing side reachable via an off-by-one in the base-`p` concatenation. Non-firing side
exact by the bijection. I verified the bijection claim independently: with `lift` the
representative in `[0, p)`, `N = lift(e_1)*p + lift(e_2) + 1` is injective on
`[0,p) x [0,p)` and its image is exactly `[1, p^2]` — the map is a bijection, so
OBJ-NULL-SYNTH and OBJ-NULL-UNIF are the same law, as claimed. DV-7 appears in no
branch condition other than M-5(c), and DV-6 in none other than M-5(b): **the
quarantines are structurally real and neither leaks into M-1, M-2, M-4 or M-6.**

### M-1 — STAND-IN TELL — **REACHABLE on both sides. The one branch whose attainability argument is fully sound.**

Firing side: the BATCH-020 stand-in gives `p_hat(u2) = 1` (since `Bsm = 2^20 > p`) and
`p_hat(u6) = rho(ln p / ln 102) ≈ 0.049–0.053`, a ratio 7.6–8.2× above the 0.00640378
threshold. Confirmed. Non-firing side: NULL-DRY measured decay ratios of
**5.27e-4** (bits 16) and **3.95e-4** (bits 20) on correct nulls, both an order of
magnitude below the threshold — so a correct measurement does not fire M-1 by noise.
Confirmed empirically, not just by the Poisson argument.

Minor gap: DV-5 is defined "per encoding and bit size" but M-1's condition reads only
ENC-B. A DECAY firing on ENC-A is therefore recorded and classified by nothing. Harmless
here (I compute the ENC-A ratio as ≈`rho(ln p/ln Bsm)^2 ≈ 0.0024 < 0.0064`, so it will not
fire), but it is an unstated scope restriction inside a frozen rule.

### M-2 — CONSISTENT WITH DICKMAN — **UNREACHABLE IN PRACTICE. This is the BATCH-021 D-2 defect, repeated.**

The contract's argument is structurally the right argument: *the null arm runs the
identical code path, so if the null can produce an M-2-pattern measurement then the
M-2 pattern is reachable*. I endorse the form of the argument. Its premise is
**empirically false**: the null does not produce an M-2-pattern measurement, because
it fails TAIL-DS-1, and hence fails `bit_size_pass`, in 16 of 16 draws. See §3.

Conjunct-by-conjunct, at the frozen thresholds, on a correct null:

| conjunct | contract's claim | measured / recomputed |
|---|---|---|
| RATE u = 2 | band [0.03836, 1.0] | passes (p_hat 0.35–0.36) |
| RATE u = 3 | band [0.006076, 0.38886] | passes (0.063–0.071) |
| RATE u = 4 | band [0.000614, 0.039287] | passes (0.0085–0.0105) |
| RATE u = 5 | band [0.0000443, 0.0028378] | passes, at 2.6–4.4× of centre |
| KS-DS-1 ≤ 0.05 | "large margin" | **0.0385 at bits 20; 0.0490 ± 0.0007 at bits 16 → 7/8** |
| TAIL-DS-1 `p_ext*n ≥ 1` | "probability about 1 − 1/e" | **0/8 and 0/8** |
| DV-4 ≤ 0.006361 | 99 % | accepted (not simulated) |

So M-2 is not reachable by an achievable correct measurement. Under the truth of
HEUR-DS-1 and a flawless implementation, the run lands in **M-5, MAP SUSPENDED**.

### M-4 — DEVIATION FROM DICKMAN — **formally reachable; the contract's demonstration is invalid on both of its legs; and it is reachable mostly by noise**

Formally, nothing in the design caps DV-4 away from its rejection region, so M-4 is not
unreachable in the BATCH-021 sense. But the contract was required to demonstrate that
an *achievable* measurement lands there, and its demonstration fails twice:

1. **The diagonal claim is mathematically false.** The contract says the 512 diagonal
   draws `i = j` give "`S_3(x, x, Z)` … a forced square structure that biases `e_2`
   toward the quadratic residues". S3-CHECK: the standard third summation polynomial is
   `S_3(x1,x2,Z) = (x1-x2)^2 Z^2 - 2[(x1+x2)(x1x2+a)+2b] Z + [(x1x2-a)^2 - 4b(x1+x2)]`,
   verified on a real curve to vanish exactly at `x(P±Q)`. Its leading coefficient in
   `Z` is `(x1-x2)^2`, which is **identically zero on the diagonal**. On `x1 = x2` the
   polynomial collapses to degree 1 with the single root `x(2P)` — verified numerically.
   There is no root multiset of size two, no `e_2`, and no QR bias. `e_1 = -c_1/c_2` and
   `e_2 = c_0/c_2` are *undefined*, being divisions by zero.
2. **The density argument measures the wrong CDF.** "Any bias that concentrates `e_2`
   on a set of density at most 1/2 displaces the CDF of `N` by up to 0.25 in supremum
   norm, which is 39 times the DV-4 threshold." The CDF of `N` is not what DV-4 tests.
   Consistently with KS-DS-1, DV-4 is a two-sample KS on the LPF statistic
   `Z_j = ln N_j / ln P_max(N_j)`. Concentrating `e_2` on the quadratic residues —
   a set that is multiplicatively structured but essentially generic with respect to the
   factorization of `e_1·p + e_2 + 1` — displaces the `Z` CDF by approximately nothing.
   The contract elsewhere forbids exactly this species of substitution ("comparing a CDF
   of raw polynomial degrees to rho is a category error"); it commits the analogous one
   in its own attainability block.

What *is* true: M-4 fires readily — but largely for the wrong reason. On a correct
apparatus, if the null happens to clear TAIL at both cells (rare), the real arm fails
TAIL independently at each cell with probability ≈1, so **M-4 is the modal substantive
branch under the truth of the hypothesis**. A branch that records `weaken` on
H-SMTH-001 when the heuristic is exactly true is worse than an unreachable one.

### M-6 — SPLIT VERDICT — **reachable; stated reason is weak but the branch is fine**

The factor-base density argument (0.78 % of `F_p` at bits 16 vs 0.049 % at bits 20) is a
plausible mechanism and the branch has no cap. Independently, M-6 is reachable through
the bits-16-vs-bits-20 asymmetry I measured directly: KS-DS-1 sits at 0.049 at bits 16
and 0.0385 at bits 20 against a 0.05 threshold, so the two cells genuinely can and will
diverge — though again for a finite-`X` reason rather than a Semaev one, which means an
M-6 landing would be over-interpreted as "the data do not discriminate the explanations"
when the actual explanation is a model-calibration artifact common to both objects.

---

## 3. THE BATCH-ENDING FINDING — TAIL-DS-1 makes the whole map unreachable

TAIL-DS-1, inherited verbatim from `EXP-DS-001/specification.v2.yaml` (I checked the
source text; the reuse is genuine and verbatim), reads:

> Let `p_ext` be the model probability under rho of observing a sample at least as
> smooth as the smoothest `N_j` in the sample. Pass iff `p_ext * n >= 1`.

**Analytically.** `p_ext = rho(max_j u_j) = min_j rho(u_j)`. Under the model the rule
itself invokes, `rho(u_j)` is uniform on (0,1), so `n·p_ext → Exp(1)` and
`P(pass) = (1 - 1/n)^n = 0.36788`. Not "about `1 - 1/e`" as the contract states in
`m_2_attainable` — the contract has the probability **inverted**. The correct value is
`1/e`, and the rule fails more often than it passes on a perfect sample.

**Empirically it is far worse than `1/e`**, because at `X ≈ 2^32`–`2^40` the asymptotic
`rho` massively under-predicts the density of very smooth integers deep in the tail,
which is precisely where `p_ext` is evaluated. NULL-DRY, 8 draws per cell of
`n = 131328` genuinely uniform integers on `[1, p^2]`:

```
bits 16   p_ext*n =  0.00023, 0.00018, 0.0000004, 0.00224, 0.02700, 0.00008, 0.00506, 0.04392
bits 20   p_ext*n =  0.17466, 0.04713, 0.00059,   0.73122, 0.08755, 0.07899, 0.05238, 0.02546
```

**TAIL-DS-1 passed 0 of 8 at bits 16 and 0 of 8 at bits 20.** The largest value observed
anywhere is 0.73, and the bits-16 values are three to six orders of magnitude below the
threshold. This is structural, not marginal: it is the finite-`X` correction to Dickman,
which grows without bound as `u` grows, being applied at `u ≈ 7–11`.

**Consequences under the frozen precedence order, on a flawless implementation and with
HEUR-DS-1 exactly true:**

1. `bit_size_pass` requires TAIL. OBJ-NULL-UNIF therefore fails `bit_size_pass` at both
   bit sizes.
2. M-5 leg (a) fires: "OBJ-NULL-UNIF itself fails `bit_size_pass` at either bit size".
3. M-5 precedes M-1, M-2, M-4 and M-6. **MAP SUSPENDED. No disposition about
   HEUR-DS-1 in either direction.**
4. Therefore **M-1, M-2, M-4 and M-6 are jointly unreachable** by a correct measurement.

This is the BATCH-021 D-2 failure mode reproduced exactly, arriving through a
probabilistic guard instead of a hard enumeration cap. In BATCH-021 `split_search`
capped `U <= 0.4706` so `U >= 0.9` could not fire on any object. Here TAIL-DS-1 caps the
null's `p_ext*n` far below 1 so `bit_size_pass` cannot hold on any object, and the guard
that reads "the instrument is broken" fires precisely *because the instrument is
correct*. **The experiment could not confirm its hypothesis even if the hypothesis were
true.** Even taking the optimistic analytic figure `1/e` per cell rather than the
measured 0/16, the arithmetic is: `P(M-5 does not fire) = 0.368^2 = 0.135`,
`P(M-2) ≈ 0.018`, `P(M-4) ≈ 0.055`. On the measured figures those become ≈0, ≈0 and ≈0.

Inheriting the threshold verbatim is not a defence. Verbatim reuse of frozen thresholds
is the right policy and the contract applies it correctly; but the named duty here is
attainability *at these parameters*, and this is the first time in the lane that
TAIL-DS-1 has ever been load-bearing, because the HEUR arm never ran. A threshold that
was never exercised is not a validated threshold.

---

## 4. Second independent unreachability defect — the 512 degenerate half-tuples

Established by S3-CHECK, not by reading: the leading coefficient of
`S_3(x_i, x_j, Z)` in `Z` is `(x_i - x_j)^2`, zero over `F_p` **iff `x_i = x_j`**.
Over 7260 half-tuples on a real toy curve I measured exactly 120 degenerate pairs —
exactly the diagonal — and 7140 non-degenerate ones. Scaled to `Bfb = 512`:

- **Exactly 512 of the 131328 enumerated half-tuples `i <= j` are degenerate**
  (0.3899 %). `e_1` and `e_2` are undefined on all of them, ENC-B is undefined, and ENC-A
  is undefined.

The contract enumerates `i <= j`, fixes `n_per_set = 131328` as exhaustive, requires the
three other sample sets to be drawn at that same `n` because "the two-sample KS threshold
assumes matched sample sizes", instructs the run to "record and count every half-tuple
with `c_2 == 0`", and then fires M-0 on "a sample set with fewer than 131328 recorded
samples". It never says what value a degenerate draw contributes. The two available
readings give different branches:

- **A-2(i), drop them** — the only mathematically available choice, since `e_1, e_2` do
  not exist — leaves the two OBJ-REAL sets at `C(512,2) = 130816`. **M-0 fires
  deterministically, on every possible outcome, before any statistic is read.** The
  favourable branch is unreachable for a second, wholly independent reason.
- **A-2(ii), sentinel them** — the contract authorises no sentinel; whatever is chosen
  contaminates `p_hat` at every rung with 0.39 % of a manufactured value, breaks the
  matched `n` for DV-4 (`131328` null vs `130816` usable real `Z_j`), and constitutes an
  undeclared post-freeze design choice made by the Executor.

A pre-registered rule whose branch depends on an undeclared implementation choice is not
fully pre-registered. This is my answer to "can you construct a plausible result the map
classifies twice or not at all": **yes — the actual, certain result of this design is one
the map classifies differently depending on a decision the contract never made.**

Note also that the M-0 degenerate trigger is written as "a DEGENERATE draw count above
1 percent of half-tuples without an explicit declaration". 512/131328 = 0.39 %, so that
clause is silent, and the count-shortfall clause fires instead — an interaction the
contract did not anticipate.

The defect is cheaply repairable (enumerate `i < j`, `n = C(512,2) = 130816 >= 10^5`,
and re-derive the matched `n` and the DV-4 threshold `1.63*sqrt(2/130816) = 0.006374`),
but I do not author repairs; that is the Coordinator's.

---

## 5. Collateral finding on INT-1 that the attainability duty surfaced

S3-CHECK also settles a claim in `step_3_invariants`. The contract prefers ENC-B over a
root-by-root lift because `(e_1, e_2)` "is well defined whether the roots lie in `F_p` or
in `F_{p**2}`, which a root-by-root integer lift would not be". Over the frozen factor
base this justification is **vacuous**: the roots of `S_3(x_i, x_j, Z)` are
`x(P_i + P_j)` and `x(P_i - P_j)`, and for `P_i, P_j ∈ E(F_p)` both lie in `F_p` always.
Measured: **7140 of 7140** non-degenerate half-tuples split over `F_p`; zero irreducible.

That does not make ENC-B illegitimate — it is a genuine complete invariant of the fibre —
but it removes the stated reason for preferring it over the obvious alternative, and the
alternative matters: the intermediate the claw table is actually keyed on (the contract's
own `step_1` says so) is the x-coordinate `x(P_i ± P_j)`, an integer **below `p`**, not
an object of size `p^2`. The frozen `D = 2^(2*bits)` fits ENC-B and not that object. So
the object's size was chosen to fit a frozen bound rather than the bound derived from the
object. `H-SMTH-001.interpretation_limits` concedes that a different faithful encoding
could carry a different law, which is honest; but `objects.OBJ-REAL.role`, "the quantity
HEUR-DS-1 is about", and `confirmatory_status_note` overstate it.

---

## 6. Summary table

| band / branch | reachable by an achievable measurement? | contract's demonstration |
|---|---|---|
| M-0 | yes — and fires with certainty (defect A-2) | sound as far as it goes |
| M-5(a) fire | yes | sound |
| M-5(a) not fire | **NO — measured 0/16 on a correct null** | **inverted probability; FATAL** |
| M-5(b) both sides | yes | sound; certificate narrower than claimed |
| M-5(c) both sides | yes | sound; bijection independently verified |
| M-1 fire | yes (stand-in, 8.2×) | sound |
| M-1 not fire | yes (measured 5.3e-4, 4.0e-4) | sound |
| M-2 | **NO — pre-empted by M-5(a); also by M-0** | premise empirically false |
| M-4 | formally yes, but modal-under-truth | **invalid on both legs** |
| M-6 | yes | weak reason, branch fine |
| Bsm rungs u = 2,3,4,5 (both cells) | yes, all powered | sound |
| Bsm rung u = 6 (both cells) | correctly declared unattainable as a RATE decision, correctly confined to DECAY-1, and the confinement genuinely does not spoil DECAY-1 (verified: crossing needs 258 counts against a mean of 2.6) | **the one place the contract does this exactly right** — but its stated remedy for powering it is a trap (§1a) |

The u = 6 confinement is the part of ATTAIN-RR-SMTH-1 that works, and it should be kept
verbatim in any successor. It is genuine, checkable, pre-declared handling of a known
unattainable band — the discipline BATCH-021 lacked. The process change is real. It
simply was not applied to the two bands that actually decide this experiment.

---

## 7. Verdict

**FAIL — REVISE.** Two independent defects each make the substantive branches
unreachable by a correct measurement:

- **A-1 (fatal).** TAIL-DS-1 fails on a correct uniform null with near-certainty
  (0/16 measured; `1/e` even under the idealised model), so M-5 leg (a) fires
  deterministically and M-1, M-2, M-4, M-6 are jointly unreachable. The contract's
  `m_2_attainable` states the governing probability inverted.
- **A-2 (fatal).** ENC-B and ENC-A are undefined on exactly 512 of the 131328 enumerated
  half-tuples, so either M-0 fires on every possible outcome or the frozen rule is
  underdetermined at the point where M-0 fires.

Plus three material but non-fatal defects: M-4's attainability demonstration is invalid
on both legs (§2); KS-DS-1 at bits = 16 sits on its threshold on a correct null (§2);
and the u = 5 RATE band's headroom is largely consumed by systematic model bias, with
POW-1's u = 6 remedy actively counter-productive (§1a).

Forward guidance, naming what remains open rather than authoring a repair: the
experiment already carries a matched null on an identical code path, and the real-versus-
null comparison DV-4 is immune to every finite-`X` bias found here, because both arms
carry it equally. The cheapest discriminating route is to make the null-referenced
comparison the load-bearing decision variable and to re-found or re-calibrate the three
absolute-model tests (KS-DS-1, RATE-DS-1, TAIL-DS-1) against the measured null rather
than against the asymptotic `rho` — with the recognition that this redrafts frozen
EXP-DS-001 thresholds and so needs its own protocol amendment and review cycle. Cheaper
still, and worth pricing before rebuilding this apparatus: since ENC-B is a bijection,
the question the experiment actually asks is whether `(e_1, e_2)` is equidistributed on
`F_p x F_p`. A direct chi-square or two-dimensional KS on `(e_1, e_2)` answers that with
far more power, no factorization, no Dickman model, and no finite-`X` bias at all. The
smoothness apparatus is a lossy functional of the quantity of interest, and this review
found it to be the lossiest part of the design.
