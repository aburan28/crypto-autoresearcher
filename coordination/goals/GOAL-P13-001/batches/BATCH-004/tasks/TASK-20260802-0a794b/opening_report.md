# BATCH-004 opening report: two frozen contracts

**Task:** TASK-20260802-0a794b (coordinator) · **Goal:** GOAL-P13-001 · **Batch:** BATCH-004
**Date:** 2026-08-02 · **Depends on:** TASK-20260802-baaeb1 (DEC-20260802-fa3b26, the budgeting supersession)

Two experiment contracts are frozen before any datum exists:

| id | path | object |
|---|---|---|
| `EXP-HEUR-d640d9` | `experiments/EXP-HEUR-d640d9/specification.yaml` | NC-3 + NC-6: the first direct test of Heuristic 1's random-integer model against exactly enumerated ground truth |
| `EXP-PEC-d7979c` | `experiments/EXP-PEC-d7979c/specification.yaml` | The c-programme closeout: NC2d-PROPER, NC2b-SLOPE, L2-WEIGHT |

Neither contract states a wall clock, a memory ceiling, a run cap, or a
per-phase reserve. Both carry an explicit `no_budget_declaration` and scientific
`stopping_rules`. Both restate the standing prohibitions verbatim in substance,
both restate REM-2 (the frozen contract governs over any dispatch message), and
both record their inventor-protocol Section 8 determination with its reason.

This report asserts no result. It records what was pre-registered and, equally
importantly, what each contract is structurally unable to deliver.

---

## 1. EXP-HEUR-d640d9 — the primary contract

### 1.1 Why it is the batch's primary objective

Three batches measured the per-entry **cost** of the table build. `P0` — the
success probability that comes from Heuristic 1 via Lemma 3.5 and multiplies all
eighteen margin rows identically — has never been tested. `H-P13-001`'s
`heuristic_1_status` records NC-3 and NC-6 as unrun for three consecutive
batches and names the term as the *binding* uncertainty in the programme, not a
background caveat. Continuing to refine `c` while `P0` carries an unbounded
constant-factor uncertainty optimises the wrong term.

### 1.2 The ceiling — stated first, in the contract's objective and again in `non_claims`

This is the single most important thing about the contract, and it is placed
before any protocol detail in the file (`THE_CEILING_OF_THIS_EXPERIMENT`).

> **Heuristic 1 is a TAIL statement and this experiment measures the BODY.**
> At the paper's own operating point `p = 5·2^248 − 1` the algorithm runs at
> `u = sqrt(log(p/2)) ≈ 13.1`, where `ρ(13) ≈ 2^-60`. No sample of any feasible
> size can ever contain an integer that smooth: with `N` samples the empirical
> resolution floor is `~1/N`. At the mandatory primes `p ≤ 22,000` the AOV bound
> gives `X_p = ⌊(p/2)^{1/3}⌋ ≤ 22`, so the **entire reachable `u`-range is about
> `[1, 4.5]`**; the optional sampled arm at `p ~ 2^28` reaches `X ~ 512` and
> `u ≲ 9`. The operating point is unreachable **by construction, not by effort**,
> which is exactly why the absence of a budget does not help here.

Consequences fixed in the contract:

- It **can falsify** the random-integer model in the tested body, at
  constant-factor level, in the tested scope. Per RT-H3 that is a falsification
  of the **model** (replace it with the measured distribution), not of the
  exponent.
- It **can never confirm Heuristic 1** — not partially, not "as far as it goes",
  not "consistent with".
- A non-rejection is **not** support for Heuristic 1, for `P0`, for any margin
  row, or for the attack. Prohibition `SP-H` in the contract forbids any record
  from saying otherwise, and is symmetric: no result here may be read as
  refuting Theorem 1.1 or the `p^{1/3+o(1)}` exponent either.

### 1.3 Prime range and exact enumeration method

Tiers are defined by a **rule**, never a hand-picked list, so no prime can be
selected or dropped after a number is seen:

| tier | rule | status |
|---|---|---|
| TIER-0 | every prime `11 ≤ p ≤ 199` | mandatory — instrument fidelity |
| TIER-1 | every prime `199 < p ≤ 2000` | mandatory — core |
| TIER-2 | every prime `2000 < p ≤ 8000` | extension, ascending |
| TIER-3 | every prime `8000 < p ≤ 22000` | reach (the AOV boundary NC-3 names), ascending |

**Ground truth** = the complete multiset `{(class, δ_E)}` over all conjugacy
classes of maximal orders in `B_{p,∞}`. Route Q (primary) constructs and
*verifies* a maximal order (closure, integrality, reduced discriminant `= p`),
enumerates the type set by BFS in the ℓ-ideal graph, and computes `δ_E` as the
minimum of `Nrd/p` on the two-sided ideal `P` of norm `p`, cross-checked against
the rank-3 trace-zero form. Route F (AOV eq. (7) Gram-matrix enumeration) is
admissible **only after** exact agreement with route Q at every TIER-0 prime and
10 declared random TIER-1 primes.

Two structural protections are worth naming:

- **The partial-prime rule.** A partially enumerated prime is discarded
  *entirely*. Enumeration order within a prime correlates with `δ_E` (small
  minima are found first), so a truncated single-prime enumeration is biased
  toward small `δ_E` and would manufacture exactly the smoothness excess the
  experiment exists to detect.
- **No formula from recollection is ever ground truth.** The classical count
  `⌊p/12⌋ + ε_p` may serve as a reference at larger primes *only after* it has
  been verified against a brute-force Hasse-invariant enumeration at every
  TIER-0 prime. If it disagrees, brute force governs and the formula is recorded
  as wrong.

**Environment constraint pinned in the contract:** Python 3.11 standard library
only — no SageMath, no numpy, no sympy, no gmpy2 (observed and recorded in
`RUN-PEC-49c773-a/environment.json`). The producer's designs in
`research/P13-HEUR-001` assume SageMath and AOV's published code; neither is
available. Every computation is specified as exact-integer pure Python, and a
needed dependency is an underspecification to report, never a licence to
substitute an approximate method.

### 1.4 The four pre-registered statistics, with thresholds fixed now

Every statistic is reported under three weightings, fixed in advance because
they differ exactly on the Galois-stable classes (the `δ_E = 1` spike):
**W-CURVE** (uniform over supersingular `j`-invariants — Heuristic 1's literal
measure, **primary**), **W-TYPE** (uniform over conjugacy classes — what
Section 4.2 actually samples), **W-MASS** (Eichler mass). Their difference is
itself a deliverable: it is the first quantification of the measure mismatch
RT-H2 raises qualitatively.

**S1 — sampler uniformity (RT-H2).** Sampler under test: non-backtracking walk
in the ℓ-ideal graph from a verified `O_0`, at three walk lengths
`L ∈ {1, 3, 10} × ⌈log2 p⌉` (under-mixing is the named failure mode, so walk
length is an independent variable rather than a convention).
- S1a **one-sample KS** of walk-sampled `log δ_E` against the **exact** enumerated
  CDF, Monte-Carlo null over ties (the reference is exact, so this is both correct
  and strictly more powerful than a two-sample test).
- S1b the **two-sample KS** NC-3(a) literally names, against an exact-uniform
  reference sample of the same size — which doubles as its own null object.
- S1c class-visit **chi-square** against uniform, plus TV distance with its
  exact-uniform reference distribution.
- S1d **T5 spike calibration**: walk-sampled `P(δ_E = 1)` against the exact
  enumerated fraction, exact binomial.
- **Rejection threshold:** per prime, MC `p < 0.05` with Holm correction across
  primes; `SAMPLER-REJECTED` at length `L` if the Fisher-combined `p` across
  primes is `< 0.001` (S1c/S1d reject at `p < 0.001` after Holm). S1a and S1b
  must agree; disagreement is a finding and the rejection verdict governs.
- **Consequence:** at a rejected `L`, every sampled-arm statistic is labelled
  `SAMPLER-CONFOUNDED` and excluded from every headline. The enumerated arm is
  untouched. **Scope honesty:** the paper does not state its sampler; a verdict
  here is about *this* walk sampler at *these* primes.

**S2 — the ℓ = 2 parity statistic (RT-H3).** ℓ = 2 is the one small prime B2's
nondegeneracy argument does not cover (discriminant `p/4`).
- Reported as NC-3(b) names it: `P(δ_E even)` vs `1/2` with **exact
  Clopper–Pearson 99% intervals, stratified by `p mod 8`**, under all three
  weightings.
- **But `1/2` is the wrong null and is reported descriptively only.** `δ_E ≤ 22`
  in the mandatory range and its size distribution is not uniform; a uniform
  integer in `[1,n]` is even with probability `⌊n/2⌋/n`. The **rejection
  statistic** is `z_2 = (p_obs − p_null)/sqrt(Var_obs + Var_null)` with
  `p_null = Σ w_i·(⌊n_i/2⌋/n_i)/Σ w_i` computed exactly at the observed sizes —
  the model's own prediction, with the size effect removed exactly.
- **Rejection threshold (all three required):** `|z_2| > 3` pooled under
  W-CURVE; **and** `|z_2| > 3` with the same sign in ≥ 2 of the four `p mod 8`
  strata; **and** the same sign in TIER-1 alone and in the union of higher
  completed tiers alone. Partial satisfaction ⇒ `INCONCLUSIVE`, reported with
  each clause's numbers.
- **Consequence if met:** the random-integer parity model is rejected in tested
  scope; the constant factor is reported in bits. It does **not** refute the
  exponent.

**S3 — the size-model double fit (RT-H1 / B6).** Observable: `P⁺(δ_E)`, the
largest prime factor — exactly what Figures 1–2 plot.
- **M1** (own size `n_i`): `f1(y|n) = #{m ≤ n : P⁺(m) = y}/n`, exact by sieve.
  **M2** (AOV bound size `X_p = ⌊(p/2)^{1/3}⌋`): `f2(y) = #{m ≤ X_p : P⁺(m) = y}/X_p`,
  exact. **No Dickman asymptotics anywhere** — `u` is small and the asymptotic
  is not the model.
- **Discrimination criterion:** full-sample log-likelihood ratio
  `LLR = Σ w_i[ln f1(y_i|n_i) − ln f2(y_i)]`. Preference is **DECISIVE only if**
  `|LLR| > 10` nats **and** the sign is stable across all four of: each completed
  tier; each `p mod 8` stratum; all ten folds of a 10-fold split; both W-CURVE
  and W-TYPE. Otherwise `NOT-DISCRIMINATED`.
- **Mandatory null calibration:** the same LLR on NULL-B (M1-truth) and NULL-B2
  (M2-truth), 200 replications each. **If the observed `|LLR|` lies inside the
  span of the two null distributions the discrimination is VOID** — this blocks
  the "large `N` makes any LLR look decisive" artifact.
- **Absolute goodness of fit** for each model separately: randomized
  probability-integral transform (exactly uniform under the true model even for
  discrete data) plus one-sample KS with MC null; a model is rejected at
  `p < 0.001`. **If both are rejected that is the headline** and a stronger
  falsification than choosing between them.
- **Order-statistic anecdotes are prohibited** as evidence for or against either
  model; the smoothest sample may be reported only with the mandatory
  "non-discriminating (RT-H1(2))" label. This is the exact over-read RT-H1
  identified in the paper's own Section 4.2.

**S4 — the disjointness ratio (RT-H4 / NC-6).** Two events are pinned apart
because conflating them is the trap: `E-SMOOTH = {δ_E is B-smooth}` (Heuristic 1's
literal event, what Lemma 3.4/3.5 needs) and `E-EXISTS = {∃ B-smooth n ≤ X_p
represented}` (what the first-moment route actually bounds). **S4c measures the
gap `P(E-EXISTS) − P(E-SMOOTH)`, which no artifact in this programme has ever
measured.**
- **D1** = empirical mean count / exact first moment via Hurwitz class numbers
  `H(4np)` — the **instrument check** on the trace-formula machinery. Its
  normalization constant is fixed by a declared identity and **verified** at
  TIER-0 against the enumerated total; if verification fails, D1 is
  `UNCALIBRATED` and the first-moment arm is not used.
- **D2** = `P(count ≥ 1)/E[count]`. **D2_ref(λ) = (1 − e^{−λ})/λ** is the exact
  independent-events reference — `D2` is below 1 even under perfect independence
  (`0.9516` at `λ = 0.1`), so a threshold stated against 1 would fire on a
  perfectly disjoint process.
- **Primary statistic: `D2* = D2 / D2_ref(λ̂)`**, which equals 1 exactly under
  disjointness.
- **Three rarity regimes** chosen by rule: the `B` in `{2,…,19}` whose measured
  `λ̂` is nearest `0.30`, `0.10`, `0.03`. **REFUTED IN TESTED SCOPE** if
  `D2* ≤ 0.85` with a 99% bootstrap upper bound below `0.95` in ≥ 2 regimes
  **and the deficit does not shrink as `λ̂` decreases**. **CONSISTENT** if the
  99% CI contains 1 in all reached regimes. Otherwise **INCONCLUSIVE**, said
  plainly.
- The direction of `D2*` as `λ` falls is the inventor-protocol structural tell:
  a quantity that fails to move toward its predicted limit as the parameter
  driving it there increases is an artifact signature.

### 1.5 Null objects and the void criterion

| null | shape | targets |
|---|---|---|
| **NULL-A** | random positive-definite integral **ternary forms of the same determinant**, run through the identical short-vector code path | S2, S3, S4 — the inventor-protocol "same shape, arithmetic origin removed" object |
| **NULL-B** | `δ_E` → uniform integer in `[1, n_i]` (M1 truth), 200 reps | exact null for S2's rejection statistic; M1 calibration arm for S3 |
| **NULL-B2** | `δ_E` → uniform integer in `[1, X_p]` (M2 truth), 200 reps | M2 calibration arm for S3 |
| **NULL-C** | Poissonized redistribution of the same total events at measured `λ̂`, 10,000 reps | exact reference distribution of `D2*` under perfect disjointness at the same finite sample |

**Void criterion (binding):** any signal from the arithmetic object that appears
at the same magnitude and sign in its null is declared **VOID** — an artifact —
and is not reported as a finding. A void signal is never repaired by adjusting
the instrument, re-choosing a threshold, or restricting the range. VOID is
terminal for its own statistic; the run continues.

**Instrument fidelity on an exactly known count (IF-1).** The certifying
identity is

```
n_types(p) = ( #SS(p) + #{classes with δ_E = 1} ) / 2
```

with `#SS(p)` computed by brute-force Hasse-invariant testing at TIER-0. Both
sides are computed independently and must agree exactly. This one identity
simultaneously certifies the enumeration's completeness, the conjugacy test's
soundness, the Galois bookkeeping, and the `δ_E = 1` spike — without relying on
any recalled class-number formula. Failure ⇒ the enumeration is **not** ground
truth; stop the enumerated arm and report. That is an infrastructure outcome,
never evidence about Heuristic 1 (AGENTS.md rule 5). IF-2 (minimum computed two
ways), IF-3 (route agreement), IF-4 (conjugacy-test soundness via theta series),
IF-5 (AOV bound as a free empirical check) and IF-6 (an optional external anchor,
explicitly labelled an unverified secondary quotation) complete the battery.

### 1.6 Stopping rules — scientific only

Normal end: TIER-0 + TIER-1 completely enumerated, S1–S4 computed with all nulls,
IF-1..IF-6 all with verdicts. Extension tiers end at tier completion; a partial
tier contributes only its complete primes. Terminal instrument failure (IF-1/2/4)
stops the enumerated arm. S1 rejecting at all three lengths ends the sampled arm
only. **Sufficiency clause:** once the mandatory tiers and the `10^4`-record floor
are met, stopping at the end of *any complete tier* is a fully valid terminal
state needing no justification beyond naming the tier.

**What a partial result means** (stated in the contract): evidence about exactly
the primes completely enumerated, weightings computed, `B` values reached and the
`u`-range actually attained — each reported as a number, not an adjective. No
extrapolation in `p` from a truncated ladder. "A partial result that fails to
falsify is even less than a complete non-falsification: it is silence."

---

## 2. EXP-PEC-d7979c — the closeout contract

This contract **supersedes no record**. `EXP-PEC-49c773`, `EXP-PEC-6be870` and
their runs, evidence and reviews are read-only, and control **C-IMMUT** records
their hashes before and after execution so the BATCH-004 Validator's
byte-unchanged check is anchored in the run itself.

### 2.1 NC2d-PROPER — the legitimate retirement route for FC-4

**Grid:** `ℓ ∈ {47, 101, 151, 211}` — all above `KARATSUBA_THRESHOLD = 16` (so
IMPL-A and IMPL-B do *not* execute the identical code path, which RT3-C3(a)
showed made the committed C-PSCALE a schoolbook-only measurement) and all inside
the primary window `W-MID`. Same three primes as the committed run
(`p1 < 2^20`, `p2 < 2^30`, `p3 < 2^40`, all `≡ 3 mod 4`), 4 `j` each, **both
implementations** (new — the committed C-PSCALE ran IMPL-A only and therefore
said nothing about the series supplying the bracket's low end), plus the null arm.

**Alpha band: `[0.85, 1.15]`**, carried **verbatim** from `EXP-PEC-49c773`'s
`C-PSCALE.preregistered_prediction.acceptance_band`. It is deliberately not
re-derived, re-centred or widened: changing an acceptance band between the run
where it nearly fired and the run designed to settle it would be
indistinguishable from tuning. The interval reading is fixed *now* as the
jackknife leave-one-ℓ-out range of the pooled estimate, with the per-ℓ range
reported beside it; if the two readings disagree the result is
`READING-DEPENDENT` and the wider reading governs.

**Primary designation rule, fixed across every outcome before the number is
seen** — four cases (`CASE-CONTAINED` → MEASURED-CONSISTENT; `CASE-DISJOINT` →
alpha = 1 FALSIFIED, primary becomes `alpha_hat`; `CASE-OVERLAPPING` → primary
alpha = 1 with the discrepancy declared; `CASE-READING-DEPENDENT` → wider
reading governs) — applied **separately** to PRIMARY-A, PRIMARY-B and NULL. `c`
at `alpha = 0` **and** `alpha = 1` is always reported under every outcome.

**What retires FC-4.** Exactly one word is available: `RETIRED-BY-MEASUREMENT`,
`STANDS`, or `INCONCLUSIVE`. Retirement requires **all five** of:

- (a) FC-4-NEW (`|α_primary − α_null| > 0.15`, threshold carried verbatim) does
  **not** fire on the new grid, for both implementation arms;
- (b) `α_primary`'s interval is **contained** in `[0.85, 1.15]`, both arms, both
  readings;
- (c) `α_null`'s interval is contained in the band, both readings;
- (d) no residual trend of `α̂(ℓ)` in `ℓ` across the four new `ℓ`;
- (e) **RG-CONTROL reproduces**: the old grid `ℓ ∈ {3,5,7,11,13}` is
  re-measured **in the same run**, reproduces all five committed per-ℓ `α̂`
  values and both committed pooled values to within `0.02`, **and reproduces the
  FC-4 firing itself**.

Clause (e) is the answer to the obvious objection against this design, and the
contract says so in terms: **avoiding the failing region is not the same as
retiring the falsifier.** Measuring only `{47,101,151,211}` would *relocate* the
falsifier — it could not distinguish "the inconsistency is a property of small
ℓ" from "it has gone away for some other reason, or was never reproducible".
Exhibiting the firing and its absence in the same run, same instrument, same
primes, same seeds, is what makes the comparison a measurement of the mechanism.

**What leaves it standing:** FC-4-NEW firing on the new grid (then L5 must be
*replaced* by the measured exponent, and that is the headline); either interval
escaping the band; a residual trend in `ℓ`; RG-CONTROL failing to reproduce
(then the two runs differ for an unknown reason and no cross-grid comparison is
admissible); or RG-CONTROL reproducing the values while the committed FC-4
firing does **not** reproduce (which is itself the finding, and still not a
retirement). **Any truncation of either grid ⇒ `INCONCLUSIVE`** — stated in
advance so stopping short can never become a retirement.

The governance position is restated and binding: **a post-hoc restriction of the
ℓ-grid cannot lift a pre-registered falsifier.** FC-4 fired as written; nothing
here un-fires it. Control **C-KARA** additionally verifies the design premise in
both directions (the implementations must be bit-identical below the threshold
and must differ above it); if it fails, the design premise is void and no
retirement verdict may be reported.

### 2.2 NC2b-SLOPE — and yes, its tolerance carries a variance term

**Does the tolerance carry a variance term? YES, explicitly.** This is the direct
repair of Validator finding V-1.

```
SE_pred(level, window) = s · sqrt( 1/n + (x* − x̄)² / Sxx ),   x* = log2(B_opt(level))
T(level, window)       = max( 0.25, 2 · SE_pred(level, window) )
```

`SE_pred` is the standard error of the fitted mean at the extrapolation point —
exactly the quantity the gate compares against a known truth. The lever arm
`(x* − x̄)` *is* the 7.5–18 unmeasured octaves, which is why V-1's noise
half-widths grow from `±0.1506` bits at `log2 B_opt = 14.2` to `±1.3626` bits on
an 8-point window at `26.1`. The factor 2 (≈95%) is fixed now, not chosen later;
the `0.25`-bit floor prevents a degenerate zero tolerance on the noiseless arm.

**Power classification (the substantive part of the V-1 repair):** any
`(window, level)` point whose `T` exceeds `1.0` bit is classified `NO-POWER` and
its verdict does **not** count toward the gate. V-1's own words are the
justification: on the 8-point W-TOP window at 768 bits "a pass there would not
have been evidence that it is unbiased". **What this costs is stated in the
contract:** a variance-aware tolerance is *wider* exactly where the data are
thin, so it is *harder* to detect a real bias at large `B_opt`. The count of
surviving `PASS-WITH-POWER` points is therefore itself a reported metric, and if
few survive, the honest conclusion is that the gate family has little power
there — a finding about the method, not a failure of the run.

**Truth arms.** Synthetic series are generated on the *exact* admitted ℓ grid of
`RUN-PEC-49c773-a`, so the window, spacing and lever arm are the real ones:
`T-POWER` (correctly specified — the gate arm), `T-BAND` (the Karatsuba
recursion staircase RT3-C2 identified), `T-SATURATE` (bounded approach to a
ceiling), and `T-BREAK` (a breakpoint *above* the entire measured range).

**Honest statement of power, binding in the contract:** the gate has power
against **estimator error under a correctly specified power law**; it has **no
power against misspecification of the law itself, which is what L1 actually
asserts**. `T-BREAK` is identical to `T-POWER` on every measured point and
different at `B_opt` — it is unfalsifiable from the measured range by
construction. Its extrapolation error is therefore not a gate but the **first
measurement of the L1 identifiability gap in bits**. After this experiment **L1
remains UNTESTED**; what changes is that its magnitude under three named
alternatives is on the record.

**NC2b-G1-VAR** additionally retro-fits the variance term onto the committed
gate of record at zero new measurement: the **ten** evaluation points (2 null
windows × 5 field sizes — ten, not the fifteen three committed files state, per
Validator V-5) are reclassified `PASS-WITH-POWER` / `FAIL` / `NO-POWER` and
reported *side by side* with the original fixed-0.75 verdicts. The original
verdict is not overwritten or contradicted — it was correct at its own
pre-registered tolerance and the Validator confirmed it. What is added is what it
could and could not resolve. This edits nothing immutable.

### 2.3 L2-WEIGHT — sign stated in advance

**Quantity:** `Δ(γ, X, B) = γ·log2(B) − log2( E_entry[ℓ^γ] )` with
`E_entry[ℓ^γ] = ∫ y^γ dS(y) / S(B)`, `S(y) = Σ_{d ≤ X, P(d) ≤ y} d` — RT3-C1's
own definition, adopted verbatim so its anchors are reproducible. Also computed
under `ψ(d)` weighting (RT3-C1 reports the change as `< 0.001` bits; this run
checks that rather than assuming it).

**Sign, stated in advance: the correction is ATTACK-FAVOURABLE.** Charging every
entry at `ℓ = B_opt` **overstates** the entry-weighted cost, so the correction
**reduces** the modelled overhead, **reduces** `c`, and **increases** the
modelled margin over Delfs–Galbraith. Predicted magnitude `0.60–1.00` bits at
every field size (`c` at NIST-I overstated by ≈ `0.038–0.063`). Recorded because
it matters for credibility: this correction was found and quantified by the **red
team against its own prior objection** (RT3-C1 is labelled ANTI-ATTACK-OBJECTION
in the committed report). **Falsifier of the sign:** a measured `Δ ≤ 0` falsifies
the prediction and becomes the headline of L2-WEIGHT; nothing is adjusted.

**Instrument check (L2-ANCHOR):** reproduce RT3-C1's exact-enumeration values —
`(X,B) = (10^7, 100)`: `Δ = 0.598` bits at `γ = 0.810`, `0.676` at `0.933`, over
`269,882` smooth `d`; `(10^8, 215)`: `0.625` and `0.704` over `2,792,530` smooth
`d` — to within `0.005` bits, with **exact** agreement on both integer counts.
This is the discriminating check RT3-C1 itself named. Failure ⇒ the L2-WEIGHT
instrument is **unverified**, its `Δ` values are non-citable, and the discrepancy
is reported in full; the run is not invalidated and nothing is tuned. The Dickman
comparator uses `RUN-P13VOW-001`'s committed cross-validated `ρ`, and the exact-
vs-asymptotic gap (RT3-C1: `0.868` Dickman against `0.598–0.625` exact) is
measured across a `B` ladder rather than asserted.

### 2.4 What EXP-PEC-d7979c cannot do

- It **cannot reduce the ~7.5 unmeasured octaves at NIST-I** (or ~18 at
  `log2 p = 768`) by a single octave. It quantifies the non-discrimination on
  three named alternatives — a different and much smaller thing.
- It cannot move `concrete_threat_nist1` off `INCONCLUSIVE` (SP-6).
- It cannot address **L4** (batched Sutherland-type evaluation), still the
  dominant residual at `11.50–13.25` bits — larger than everything measured here.
- **Nothing here bears on Heuristic 1 or on `P0`.** The two contracts measure
  opposite sides of the margin and neither substitutes for the other.
- A retirement of FC-4 removes a label worth at most `0.4277` bits at NIST-I and
  `0.6809` bits at `log2 p = 768`: FC-4 fired on the smallest term in the
  corrected law.
- `NC2b-SLOPE` is synthetic and carries **no empirical tier at all**;
  `L2-WEIGHT` is an exact integer enumeration and likewise asserts nothing about
  any field. The alpha estimate regresses across 40-, 60- and 80-bit fields and
  therefore carries a **`toy`** ceiling despite the primary instance being
  `medium`.

---

## 3. Section 8 determinations

**`EXP-HEUR-d640d9`: `proof_search_map_required: true`.** This is a deliberate
departure from the BATCH-003 precedent, so the reason is recorded rather than
assumed. Section 8 binds any "closure argument", and this contract's
falsification arm *is* a closure argument in preparation: a met threshold in S2,
S3 or S4 would be offered as a scoped refutation of the random-integer model, and
`docs/claims-and-verification.md` requires a checkable refutation artifact before
any adverse transition. The four audits are load-bearing here rather than
ceremonial — each maps one-to-one onto a standing red-team objection:

| audit | disposition |
|---|---|
| baseline reproduction | **DISCHARGED BY CONSTRUCTION** — IF-1's exactly-known-count identity against brute force; no recalled formula may serve as ground truth until verified; IF-2 reproduces every minimum by two routes |
| observation collision | **APPLICABLE, PARTIALLY CLOSED** — the collision *is* RT-H1 (the two size models produce nearly identical observables); S3 is the separator and is built so a collision is *detected* (`NOT-DISCRIMINATED` / `VOID`) rather than resolved by wishful reading. A **second collision is named and NOT closed**: at toy `u` the model that fits the body and the model that governs the tail are observationally identical, and no toy data separate them |
| quantifier order | **STATED** — Heuristic 1 quantifies uniformly in `p` and over a `u`-window; this experiment supports only "for the specific primes completed, for the specific `B` tested". Reading a finite-`p`, finite-`B` non-deviation as the uniform statement is the headline risk, and SP-H prohibits it |
| method ceiling + nearby object | **ADDRESSED** — the ceiling is stated up front, not in a footnote: under ideal tuning this method reaches `u ≲ 4.5` and never `u ~ 13`. NULL-A is the nearby object; a statistic that cannot distinguish maximal orders from random ternary forms of the same determinant has not identified the load-bearing structure, and the void criterion makes that terminal |

The map is recorded inline because **no hypothesis-level `proof_search_map` and
no numbered `HEUR-NNN` record exist for Heuristic 1 anywhere in this programme**,
which `docs/claims-and-verification.md` ("Heuristic records") requires. That is a
ledger gap, recorded rather than papered over, and it is a next action for the
BATCH-004 ledger archive — not something this experiment may fix.

**`EXP-PEC-d7979c`: `proof_search_map_required: false`.** Same reasoning the
Coordinator recorded for `EXP-PEC-49c773`, and recorded here rather than omitted.
It proposes no theorem, asymptotic bound, certificate family, reduction or
closure argument: it is (a) a bounded empirical re-measurement of a p-scaling
exponent on a different ℓ grid, (b) a synthetic estimator study with known ground
truth, and (c) an exact integer enumeration reproducing a committed
recomputation. Note the deliberate contrast with its sibling: `EXP-HEUR-d640d9`
carries the map because its falsification arm would be offered as a closure
argument; this one's would not. Two components are argumentative enough that the
four audits are addressed inline anyway — L5's `alpha = 1` derivation, and
NC2b-SLOPE, which is an identifiability study in experimental form (i.e. the
observation-collision audit made into a measurement).

---

## 4. Cross-cutting compliance

- **No budget anywhere.** Both contracts carry a binding `no_budget_declaration`.
  Note the concrete consequence for the closeout: in `EXP-PEC-49c773`, C-PSCALE
  was "NEW, BUDGET-CONDITIONAL, NON-GATING" and was the first item a truncation
  would drop; **here its successor is the primary item and is gating.** Nothing
  in either contract is conditional on remaining time.
- **Standing prohibitions restated in both**, so no Executor can cite a forbidden
  value: SP-1 (`c = 0.864` and variants), SP-2 (`γ = 0.9739` / `0.0488` /
  `1.1706` without the seam statement and homogeneous readings — a prohibition
  Validator V-3 found **breached** in a committed execution report, so the
  closeout contract requires the Executor to check every file it writes against
  it), SP-3 (`w = 2^30` only), SP-4 (`c` citable only as the bracket with its
  eight attachments), SP-5 (per-row bootstrap CIs are never the uncertainty),
  SP-6 (`concrete_threat_nist1` stays INCONCLUSIVE), plus SP-7/SP-8 in the
  closeout and **SP-H** in the heuristic contract (no result may be described as
  support for Heuristic 1, `P0`, any margin row, or the attack — and symmetrically
  none may be described as refuting Theorem 1.1).
- **REM-2 restated in both**: the frozen contract governs over any dispatch
  message; a disagreement is followed by the contract and reported as a
  discrepancy. The closeout contract additionally cites
  `INCIDENT-20260802-P13-03` in its `execution_order` note, because that is
  precisely where the previous incident occurred.
- **Inference provenance recorded in both**: `requested_policy:
  coordinator-orchestration-code`, `fallback_used: true`, `model_verified:
  false`, `inference_amendment: INFAMEND-20260802-P13-002`, with
  `degraded_requirements` (review-adversarial `xhigh` and executor-implementation
  `medium` recorded as UNVERIFIED rather than asserted as met) and the
  `not_degraded` note that independent sessions are genuinely satisfied.
  Executor-side requirements are stated separately.
- **Neither contract asserts a result.** Both define success as a property of the
  protocol being executed and reported, never of any value obtained: FC-4
  `STANDS` is a success; every NC2b-SLOPE point coming back `NO-POWER` is a
  success; four `INCONCLUSIVE` verdicts on the Heuristic 1 run is a success.

## 5. Next actions arising (for the ledger archive, not for this task)

1. Create the missing numbered heuristic record for Heuristic 1 required by
   `docs/claims-and-verification.md` ("Heuristic records"), so that
   `heuristic_under_test` can be filled with an id rather than `null`.
2. Create a hypothesis-level `proof_search_map` for the Heuristic-1 lane, of
   which `EXP-HEUR-d640d9`'s inline `section_8_determination` is currently the
   only instance.
3. Note for the eventual evidence record: if `EXP-HEUR-d640d9` falsifies the
   model, `docs/claims-and-verification.md` requires the refutation artifact to
   be archived **before** the decision relying on it, and a single unreplicated
   `empirical_only` result takes `weaken` + replication, never `reject_scoped`.
