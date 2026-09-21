# EXP-RT1476-001 — analysis: fits, threshold comparisons, control outcomes

Executor task TASK-20260728-001. Experiment `EXP-RT1476-001` v1
(`approved_by_decision: DEC-20260728-002`), hypothesis `H-RT1476-001`,
batch `BATCH-010`, goal `GOAL-ECDLP-001`.

**What this file is.** The fits computed from `runs/*/raw-result.json`, and the
arithmetic comparison of those fits against the thresholds pre-registered in
`specification.yaml`. Threshold comparison lives here and only here; the
measuring module contains no threshold, no expected value and no verdict.

**What this file is not.** It assigns no evidence strength, changes no record
status, writes no evidence record, and does not declare `H-RT1476-001`
supported, weakened, rejected or confirmed. It states what the numbers are and
how they compare to the frozen thresholds. What they *mean* for the gate, for
RQ-ECDLP-002 or for anything else is the Coordinator's after independent
validation (TASK-20260728-003).

**Nothing in this run set is evidence for or against ECDLP hardness**, against
prime-field ECDLP, against index calculus at any relevant scale, or about
KN-OPEN-001. The largest field tested is 24 bits. Claim tier: `toy`, and
unreachable above at any outcome.

---

## 1. Run set

27 of 27 planned runs completed. All 27 manifests carry
`status: completed_valid`. Total wall clock **1827 s** against a 7200 s budget;
peak per-run wall clock 289 s against a 1800 s per-cell rule. **No stopping rule
fired** — not STOP-1, not STOP-2, not STOP-3, not STOP-4. No run timed out, no
run crashed, no run exhausted memory. There is therefore no infrastructure
signal to separate from measurement anywhere in this set.

All 27 `raw-result.json` files are pairwise distinct (27 distinct SHA-256
values), so INVALID-6's byte-identity clause does not fire.

---

## 2. Per-cell measurements

`|F|` = forward-state size. `supp` = `backward_state_support_size`, the
specification's primary metric, mean over measured targets. `deg_u` =
`deg_u_backward_eliminant`, mean over the measured success subset. `ops` =
counted GF(p) operations per membership query, unit-weighted. `meas s/f` =
measured successes / measured failures (Stage-B cap 10/10, section 9 of
`implementation_notes.md`).

| run | L | q | \|F\| | cert succ /1200 | supp(all) | supp(succ) | deg_u | ops_succ | ops_all | meas s/f |
|---|---|---|---|---|---|---|---|---|---|---|
| `main` p=1009 s=20260728 | 4 | 1,013 | 16 | 515 | 92.45 | 93.00 | 503.7 | 364,164 | 368,202 | 10/10 |
| `main` p=1009 s=20260729 | 4 | 983 | 16 | 351 | 80.75 | 82.20 | 510.2 | 371,010 | 371,229 | 10/10 |
| `main` p=1009 s=20260730 | 4 | 971 | 16 | 411 | 87.40 | 86.30 | 512.0 | 372,229 | 370,907 | 10/10 |
| `main` p=65521 s=20260728 | 9 | 65,407 | 81 | 291 | 974.70 | 973.40 | 5,832.0 | 4,897,135 | 4,897,131 | 10/10 |
| `main` p=65521 s=20260729 | 9 | 65,563 | 81 | 296 | 990.70 | 994.00 | 5,832.0 | 4,897,121 | 4,897,112 | 10/10 |
| `main` p=65521 s=20260730 | 9 | 65,497 | 81 | 298 | 988.65 | 989.50 | 5,832.0 | 4,897,114 | 4,897,126 | 10/10 |
| `main` p=16769023 s=20260728 | 28 | 16,773,769 | 784 | 291 | 29,322.00 | 29,317.80 | 175,616.0 | 393,068,104 | 393,068,097 | 10/10 |
| `main` p=16769023 s=20260729 | 28 | 16,763,843 | 784 | 292 | 29,321.10 | 29,328.40 | 175,616.0 | 393,068,081 | 393,068,089 | 10/10 |
| `main` p=16769023 s=20260730 | 28 | 16,765,583 | 784 | 277 | 29,294.20 | 29,279.00 | 175,604.8 | 393,033,393 | 393,050,745 | 10/10 |
| `posctl` p=1009 s=20260728 | 4 | 1,013 | 8 | 50 | 23.75 | 22.50 | 491.6 | 345,701 | 354,874 | 10/10 |
| `posctl` p=1009 s=20260729 | 4 | 983 | 8 | 54 | 23.20 | 21.40 | 479.4 | 262,323 | 276,859 | 10/10 |
| `posctl` p=1009 s=20260730 | 4 | 971 | 8 | 61 | 23.00 | 21.90 | 483.3 | 336,575 | 350,275 | 10/10 |
| `posctl` p=65521 s=20260728 | 9 | 65,407 | 18 | 2 | 55.00 | 55.00 | 5,832.0 | 3,803,089 | 3,803,064 | 2/10 |
| `posctl` p=65521 s=20260729 | 9 | 65,563 | 18 | 0 | 55.00 | null | null | null | 3,803,048 | 0/10 |
| `posctl` p=65521 s=20260730 | 9 | 65,497 | 18 | 1 | 53.82 | 42.00 | 5,681.0 | 4,045,109 | 4,151,638 | 1/10 |
| `posctl` p=16769023 s=20260728 | 28 | 16,773,769 | 56 | 1 | 169.00 | 169.00 | 175,616.0 | 133,930,840 | 133,930,840 | 1/10 |
| `posctl` p=16769023 s=20260729 | 28 | 16,763,843 | 56 | 0 | 169.00 | null | null | null | 133,930,833 | 0/10 |
| `posctl` p=16769023 s=20260730 | 28 | 16,765,583 | 56 | 0 | 169.00 | null | null | null | 133,930,840 | 0/10 |
| `negctl` p=1009 s=20260728 | 4 | 1,013 | 11 | 544 | 57.80 | 60.00 | 512.0 | 367,123 | 367,103 | 10/10 |
| `negctl` p=1009 s=20260729 | 4 | 983 | 14 | 576 | 56.80 | 68.20 | 511.8 | 369,386 | 365,334 | 10/10 |
| `negctl` p=1009 s=20260730 | 4 | 971 | 8 | 447 | 69.20 | 87.60 | 509.9 | 360,800 | 358,183 | 10/10 |
| `negctl` p=65521 s=20260728 | 9 | 65,407 | 44 | 440 | 801.15 | 892.90 | 5,832.0 | 4,465,548 | 4,465,555 | 10/10 |
| `negctl` p=65521 s=20260729 | 9 | 65,563 | 40 | 451 | 851.80 | 883.00 | 5,832.0 | 4,418,850 | 4,418,888 | 10/10 |
| `negctl` p=65521 s=20260730 | 9 | 65,497 | 42 | 472 | 721.80 | 863.20 | 5,831.9 | 4,442,179 | 4,442,205 | 10/10 |
| `negctl` p=16769023 s=20260728 | 28 | 16,773,769 | 442 | 516 | 22,367.60 | 21,533.60 | 175,616.0 | 272,946,757 | 272,946,756 | 10/10 |
| `negctl` p=16769023 s=20260729 | 28 | 16,763,843 | 440 | 516 | 22,196.10 | 22,764.40 | 175,616.0 | 272,244,293 | 272,244,287 | 10/10 |
| `negctl` p=16769023 s=20260730 | 28 | 16,765,583 | 414 | 504 | 22,394.35 | 24,034.10 | 175,616.0 | 263,112,259 | 263,105,650 | 10/10 |

`L = round(q^(1/5))` came out **4, 9, 28** at the three sizes, matching the
specification's arithmetic exactly. `q` is the measured prime group order, not
`p`; every fit below uses `log q`.

---

## 3. beta_deg — the backward-state exponent

Fitted as the slope of `log(backward_state_support_size)` against `log q`, three
size points, each the mean over its three seeds.

### 3.1 Main arm

| series | pooled | pairwise (1009-65521, 1009-16769023, 65521-16769023) |
|---|---|---|
| all measured targets | **0.5985** | 0.5790, 0.5978, 0.6119 |
| certified-success subset only | **0.5982** | 0.5784, 0.5974, 0.6117 |

Per-seed pooled slopes (all targets): 0.5940, 0.6053, 0.5968. Seed-to-seed
spread is 0.011 — no gross seed sensitivity.

Raw counts behind the fit: support = 86.9 -> 984.7 -> 29,312.4 at
`L = 4 -> 9 -> 28`.

### 3.2 Threshold comparison against the pre-registered criteria

| criterion | condition | measured | condition met? |
|---|---|---|---|
| S1 (success) | `beta_deg < 0.3` | 0.5985 pooled; smallest pairwise 0.5790 | **no** at every size and on every pairwise slope |
| F1 | `beta_deg >= 0.3` at any of the three sizes | 0.5985 | **yes**, at all three |
| F2 | pairwise slopes of `beta_deg` increasing with `q` | 0.5790 -> 0.6119 | **yes**, monotonically increasing |
| F4 | measured backward state agrees with the generic `Theta(L^3) = Theta(q^{3/5})` count | see below | **yes** |

On F4: `support / L^3` = 1.3573, 1.3507, 1.3353 at the three sizes, converging
on **4/3**. That is the exact generic count for this architecture: the backward
leg reaches `8L^3` signed triples, the chain sum is symmetric in the three
factor-base points so ordered triples collapse by `3! = 6`, giving
`8L^3 / 6 = (4/3) L^3` distinct `u`. The measured state reproduces the generic
count to three significant figures at the largest size.

The `intermediate_outcome_branch_preregistered` band the pooled fit lands in is
the boundary between (b) `0.3 <= beta_deg < 0.6` and (c) `beta_deg >= 0.6`:
pooled 0.5985, largest pairwise slope 0.6119, `support/L^3` converging up to the
generic constant. Assigning the branch is the Coordinator's, not the Executor's;
the numbers are stated here without that assignment.

---

## 4. Control outcomes

### 4.1 CTRL-POS against INVALID-4 — the single most important gate

The positive control differs from the main arm in exactly one declared respect:
the factor base is planted as `V_pos = {x([i]P) : i = 1..L}`. Same `p`, same
sampled curve, same `n`, same `L`, same seed stream, same 1200 targets, same
resultant routine, same operation counter, same session, same machine.

| quantity | value |
|---|---|
| measured backward state | **25.0, 55.0, 169.0** at `L = 4, 9, 28` (per-cell: 23.75/23.20/23.00, 55.00/55.00/53.82, 169/169/169) |
| `beta_deg` pooled | **0.2034** |
| pairwise | 0.2029, 0.2034, 0.2037 |
| per-seed pooled | 0.2020, 0.2037, 0.2045 |
| INVALID-4 condition (`beta_deg >= 0.3` on CTRL-POS) | **not met — the rule does not fire** |

The planted values are `6L + 1` exactly (25, 55, 169), which is the predicted
`Theta(L) = Theta(q^{1/5})` index-interval size, i.e. a planted exponent of 0.2.
The meter recovered **0.2034 against 0.5985 on the main arm under identical
instrumentation**. The meter therefore demonstrably resolves a planted
factor-`q^{0.4}` collapse of the backward state, and the bidirectional gate in
`controls.CTRL-POS.what_it_tests` is satisfied: the meter can see a drop that is
known to be there.

Two honest qualifications on CTRL-POS, neither of which affects INVALID-4:

- `V_pos` is built from the discrete logarithms of its own elements. It
  calibrates the instrument. It is not an attack, not a speedup, and not
  evidence that any attacker-constructible factor base has a small backward
  state (`interpretation_limits`).
- CTRL-POS has almost no certified successes at the two larger sizes (2, 0, 1 at
  `p = 65521`; 1, 0, 0 at `p = 16769023` out of 1200 targets each). This is
  structural, not a defect: a uniformly random `R = [r]P` decomposes over a
  planted arithmetic-progression factor base only when `r` lies in the reachable
  index interval of size `O(L)`, which has density `O(L/q) = O(q^{-4/5})`. Three
  `posctl` cells therefore have an empty measured success subset and are
  **`insufficient_success_subset` under INVALID-1** — see section 7. The
  INVALID-4 gate is read off the state-size series, which is measured on every
  target regardless of success and is complete for all nine `posctl` cells.

### 4.2 CTRL-NEG against INVALID-5

The negative control differs from the main arm in exactly one declared respect:
each chain link is a random dense trivariate over GF(p) with the per-variable
degrees and the total degree of `S_3`.

| quantity | value |
|---|---|
| measured backward state | 61.3, 791.6, 22,319.4 at `L = 4, 9, 28` |
| `beta_deg` pooled | **0.6055** |
| pairwise | 0.6102, 0.6056, 0.6022 |
| per-seed pooled | 0.6126, 0.6112, 0.5938 |
| `support / L^3` | 0.9573, 1.0858, 1.0167 |
| INVALID-5 condition (CTRL-NEG materially below the generic 0.6) | **not met — the rule does not fire** |

CTRL-NEG reproduces the generic exponent (0.6055 against 0.6). Its *level* is
about 76 % of the main arm's at the largest size (22,319 against 29,312): a
random dense quadratic has a root in GF(p) only about half the time, so the
propagation tree is thinner, while the exponent is unchanged. Levels between
arms are not comparable anyway
(`controls.CTRL-NEG.comparability_limit_declared`); only the trend is.

### 4.3 Both controls ran everywhere

Both controls ran at all three sizes and all three seeds — 9 `posctl` runs and 9
`negctl` runs, all `completed_valid` — under identical instrumentation, the same
resultant routine, the same counter, the same 1200 targets and the same session.

---

## 5. beta_ops — the counted-operation exponent on the certified-success subset

`ops_success` is a **real instrumented integer** from the hand-written GF(p)
layer described in `implementation_notes.md` section 2. No sympy call and no
black-box routine lies on the counted path. **INVALID-7 does not fire.** No
wall-clock proxy is used anywhere; wall-clock appears only as a diagnostic and
to drive the (unfired) stopping rules.

| arm | pooled `beta_ops` (success subset) | pairwise | per-seed pooled |
|---|---|---|---|
| `main` | **0.7197** | 0.6165, 0.7158, 0.7908 | 0.7228, 0.7188, 0.7176 |
| `posctl` | 0.6223 | 0.6017, 0.6215, 0.6365 | 0.6150, null, 0.5904 |
| `negctl` | 0.6812 | 0.5955, 0.6779, 0.7403 | 0.6838, 0.6810, 0.6788 |

Raw counts behind the main-arm fit: 369,134 -> 4,897,123 -> 393,056,526 counted
GF(p) operations per successful membership query at `L = 4 -> 9 -> 28`.

### 5.1 Threshold comparison

| criterion | condition | measured | condition met? |
|---|---|---|---|
| S2 (success) | `beta_ops < 3/2` on `ops_success` | 0.7197 pooled; largest pairwise 0.7908 | **yes**, at every size and on every pairwise slope |
| F3 | `beta_ops >= 3/2` on the success subset at any size | max observed 0.7908 | **no** |

### 5.2 ops_all versus ops_success — the abort speedup, made auditable

The red-team amendment excludes the non-relation fraction because early abort
helps only there. That exclusion is auditable here because both are reported:

| arm | `beta_ops` on `ops_success` | `beta_ops` on `ops_all` |
|---|---|---|
| `main` | 0.7197 | 0.7195 |
| `posctl` | 0.6223 | 0.6186 |
| `negctl` | 0.6812 | 0.6818 |

They agree to within 0.004. **The measured abort speedup is essentially zero**,
for a declared reason: the membership query as implemented performs no early
abort (`implementation_notes.md` section 5), so a successful query and a failing
query scan the same `V^3` and cost the same. The success/failure contrast the
red team asked to be shown is therefore shown to be absent *under this query
variant* — which is a statement about the variant, not about the mathematics. An
aborting variant would lower `ops_all` and leave `ops_success` roughly where it
is; `beta_ops` fitted on `ops_success` is the figure that survives that change,
and it is the figure reported above.

### 5.3 Weighting robustness

`beta_ops` above uses unit weights on multiplications, additions and inversions.
Inversions are **0.2 %-0.9 %** of all counted operations on this path
(mul : add : inv approximately 0.504 : 0.489 : 0.007). Recomputing the main-arm
fit with an inversion charged `ceil(log2 p)` multiplications gives pooled
**0.7178** (pairwise 0.6227, 0.7142, 0.7834) against 0.7197 — a shift of 0.002.
The declared weighting is not load-bearing, and the three counters are in every
raw record so any other weighting can be applied without rerunning anything.

### 5.4 An observation about what beta_ops is measuring

The measured `beta_ops` pairwise slopes rise monotonically (0.6165 -> 0.7158 ->
0.7908) and the per-query cost decomposes exactly as the query's own structure
predicts: `L^3` factor-base triples, each costing a fixed number of field
operations for the two subresultant eliminations plus `O(|F|)` operations for
the meet test, with `|F|` itself measured at exponent **0.4001** (16 -> 81 ->
784, i.e. `L^2 = q^{2/5}`). A cost of `L^3 (c1 + c2 |F|)` interpolates between
`q^{3/5}` and `q^{3/5+2/5} = q^1` as the second term overtakes the first, which
is what the rising pairwise slopes show. This is recorded as an observation
about the measured quantity. It is **not** an asymptotic claim, and it makes
`beta_ops` a property of the declared query algorithm as much as of the
mathematics — see section 9, caveat 1.

---

## 6. deg_u of the backward eliminant, and the deg-versus-support gap

`specification.yaml` requires both to be reported wherever both exist, together
with their ratio, and says explicitly that a systematic gap is itself a finding.
There is a systematic gap and it is large.

| arm | `deg_u` at `L = 4, 9, 28` | `beta` of `deg_u` (pooled) | `deg_u / support` |
|---|---|---|---|
| `main` | 508.6, 5832.0, 175612.3 | **0.6009** | 5.86, 5.92, 5.99 |
| `posctl` | 484.8, 5756.5, 175616.0 | 0.6056 | 20.8, 105.4, **1039.1** |
| `negctl` | 511.2, 5832.0, 175616.0 | 0.6004 | 8.34, 7.37, 7.87 |

Two observations, both recorded rather than smoothed:

1. **`deg_u = 8L^3` on every arm** (512, 5832, 175616 are exactly `8L^3`), so the
   *degree* exponent is 0.6 everywhere, including on the positive control where
   the *support* exponent is 0.203. The eliminant degree is fixed by the
   architecture — `L^3` factors of degree 8, one per sign pattern — and carries
   no information about whether the reachable set collapses. Multiplicity, not
   support, is what grows on `posctl`: at `L = 28` its 175,616
   roots-with-multiplicity sit on only 169 distinct values, a mean multiplicity
   of 1039. **A reader who reads `deg_u` as the backward-state size would
   conclude that CTRL-POS shows no collapse, which is false.** The
   specification's primary metric is `backward_state_support_size`, not `deg_u`,
   and this is why.
2. On the main arm `deg_u / support` converges to **6 = 3!** — the ordering
   multiplicity of the triple `(v3, v4, v5)`, since the chain sum is symmetric
   in the three factor-base points. The gap is fully explained and is not
   measurement noise.

---

## 7. Invalidation rules: which fired

| rule | fires? | detail |
|---|---|---|
| INVALID-1 (fewer than 5 certified successes in a primary cell) | **fires on 6 of 9 `posctl` cells** | `posctl` p=65521 (2, 0, 1 successes) and p=16769023 (1, 0, 0). Consequence per the rule: `beta_ops` is not fitted for those cells and they are marked `insufficient_success_subset`. The degree/support gate is complete for all of them. **No `main` cell and no `negctl` cell is affected** — every one has 277-576 certified successes out of 1200. |
| INVALID-2 (curve predicate rejection) | not an invalidation, recorded as required | 678 candidate curves rejected across the 9 sampled curves (675 `order_not_prime`, 3 `singular`), 2-69 per cell. A sampler property, not evidence. |
| INVALID-3 (certificate fails independent re-verification) | **does not fire** | 3,191 relation certificates written across the 18 group-law runs; **0 failed**. Each was re-verified by two implementations that do not share code with the search that produced it: `harness.semaev.verify_decomposition_certificate` and a separate in-module reimplementation of curve membership and the group law. |
| INVALID-4 (CTRL-POS fails to see the planted drop) | **does not fire** | 0.2034 on CTRL-POS against 0.5985 on `main`; section 4.1. |
| INVALID-5 (CTRL-NEG materially below the generic 0.6) | **does not fire** | 0.6055; section 4.2. |
| INVALID-6 (raw/summary disagreement, missing manifest field, non-reproducing seed, byte-identical runs) | **does not fire** | 27 distinct `raw-result.json` hashes; `results_summary.json` is generated mechanically from the raw files by `--summarize` and by nothing else; every run directory carries all seven required files. |
| INVALID-7 (`ops_success` not a counted integer) | **does not fire** | counted integer from the instrumented GF(p) layer; section 5. |

Stopping rules STOP-1, STOP-2, STOP-3, STOP-4: **none fired**.

---

## 8. Unexpected observations (AGENTS.md rule 8)

These are recorded because they were not predicted, not because they are
convenient.

1. **The frozen success-rate heuristic is off by a factor of about 30.**
   `secondary.success_rate.heuristic_expectation` and `H-RT1476-001` HEUR-001
   give `L^5 / (5! q)`, i.e. about 0.0086, 0.0075, 0.0086 at the three sizes.
   Measured on the main arm: **0.355, 0.246, 0.239** — ratios of 41.1, 32.7,
   27.9. The discrepancy is systematic across all three sizes and all three
   seeds and has an evident source: `L^5` counts *unsigned* 5-tuples, but a
   relation may use either sign on each of the five summands, and the count of
   signed multisets is `C(2L+4, 5)`, which is about `2^5 = 32` times `L^5/5!` at
   these sizes. HEUR-001's own falsification condition is "measured
   `success_rate` differing from `L^5/(120 q)` by more than an order of
   magnitude, consistently across seeds and sizes"; that condition is met. The
   heuristic's *status* is the Coordinator's to set.
2. **A Kummer meet and a certified relation coincide exactly on the main arm.**
   In every measured main-arm cell, the counted algebraic query reported
   `hits > 0` on exactly the targets the group-law meet-in-the-middle screen had
   certified, and `hits = 0` on exactly the matched failures. The reason is
   structural: if `u` lies in both the forward and the backward state then
   `u = x(e1 P1 + e2 P2)` and `u = x(R + e3 P3 + e4 P4 + e5 P5)`, so the two
   points agree up to sign and the residual sign is absorbed by the free signs,
   giving a genuine signed 5-tuple. The specification's rule that a root is a
   *candidate* until the group law is checked was nonetheless enforced
   throughout: the certified-success set used for `ops_success` is the group-law
   set, never the algebraic one. The coincidence is reported as an observation,
   not relied on.
3. **CTRL-POS has almost no certified successes at the two larger sizes**
   (section 4.1). Predictable in hindsight, not predicted in the specification,
   and it is what makes six `posctl` cells `insufficient_success_subset`.
4. **CTRL-NEG's backward-state level is about 76 % of the main arm's** while its
   exponent is the same, and its per-target spread is much wider (e.g. 21,534
   vs 24,034 across seeds at `L = 28`). Random dense links admit a GF(p) root
   only about half the time, so the propagation tree thins and fluctuates more
   than the elliptic one, whose quadratics always split when the point exists.

---

## 9. Caveats a reviewer should check first

1. **`beta_ops` is a property of the declared query algorithm, not of the
   mathematics alone.** The measured 0.7197 counts *this* membership query:
   `L^3` per-triple subresultant eliminations with `Q_{v4,v5}` cached, followed
   by evaluation of each degree-8 factor at every forward value, with no early
   abort and with the forward state amortised. A different but equally faithful
   realisation — materialising `B_R` by a product tree, or aborting on the first
   hit, or using an asymptotically fast product — would give a different
   exponent. The red team's `Omega(q^{3/2})` prediction was made about PRS on an
   eliminant of degree `~q`; the eliminant measured here has degree
   `8L^3 = 8 q^{3/5}`, not `q`, because the factor-base constraints bound it.
   That difference, not a collapse, is the arithmetic reason the measured
   `beta_ops` is below 3/2. **This is the single most important thing for the
   Validator to attack.**
2. Three points spanning `log q` from 6.88 to 16.63 cannot distinguish a power
   law from a logarithmic correction or a slowly turning curve. The main-arm
   `beta_deg` pairwise slopes *do* turn (0.5790 -> 0.6119), and the `beta_ops`
   ones turn more (0.6165 -> 0.7908). No confidence interval is reported and
   none would be meaningful from three points and three seeds.
3. At `L = 4` the factor base has four elements and constants dominate
   everything. All raw counts are reported beside every fitted slope for exactly
   this reason.
4. The Stage-B cap of 10 successes + 10 failures per cell is a declared budget
   choice (`implementation_notes.md` section 9), taken because the realised
   success count is in the hundreds rather than the frozen expectation of about
   ten. It widens the noise on the per-cell means; it does not bias them.
   Seed-to-seed spread of `beta_deg` is 0.011, which bounds how much this
   matters.
5. The elimination of the factor-base variables uses the monic
   evaluation-product identity rather than a Sylvester resultant against `f_V`.
   It is exact and was verified against `sympy` (`--selftest`, identity holds
   with constant 1), but it is an implementation choice the specification did
   not fix.

---

## 10. Internal consistency checks that were run

| check | result |
|---|---|
| `p` prime at run time (`sympy.isprime`) for 1009, 65521, 16769023 | all true, recorded per run; no modulus substituted |
| group order by Hasse-interval BSGS vs naive Legendre point count (feasible at the two smaller `p`) | 18/18 agree |
| curve predicate (prime order, ordinary, non-anomalous, `j` not in {0,1728}, non-singular) | enforced by rejection sampling; rejection counts recorded per cell |
| hand-coded `S_3` monomial table vs `harness.semaev.s3_eval` | agrees at 40 random points |
| hand-written resultant vs `sympy.resultant` | 25/25 random bivariate pairs |
| factor-base elimination identity `Res_{x5}(S3, f_V) = prod_v S3(., v, .)` vs sympy | holds, constant 1 |
| forward state by group law vs by roots of `S3(x1,x2,u)` | 18/18 runs agree (9 `negctl` runs have no group law) |
| backward state by group law vs by algebraic chain propagation, on the sampled targets | 36/36 agree at all three chain levels |
| fraction-free elimination fallbacks to evaluation-interpolation | 0 across the whole run set |
| degenerate (identically zero) link substitutions | 0 across the whole run set |
| relation certificates re-verified by two independent implementations | 3,191 written, 0 failures |
| PRS remainder-degree sequences observed (declared variant: pseudo-remainder sequence over the polynomial coefficient domain) | (2,1,0), (2,2,1,0), (3,2,1,0), (4,2,1,0) |

---

## 11. What was NOT measured

Stated explicitly, as the completion gate requires.

- **`coefficient_profile`** (nonzero-coefficient count and density of `B_R`).
  **Not measured.** `B_R` is never materialised — it is handled in its factored
  form `prod_{(v3,v4,v5)} G(u)` — and at `L = 28` assembling it would mean a
  degree-175,616 product of 21,952 degree-8 factors, outside this budget. The
  per-coefficient bit ceiling `ceil(log2 p)` is 10, 16, 24. The Collins/Brown
  coefficient-growth check it substitutes for was already declared
  `not_applicable_over_GF_p` in the specification: over a fixed prime field
  there is no growth to bound. The frozen contract's expected failure mode
  "coefficient blow-up dominating even if degree small" is therefore
  **untested**, not absent.
- **`beta_ops` for six `posctl` cells** — empty measured success subset,
  INVALID-1, section 7. `ops_all` is present for all of them.
- **`backward_state_support_group_law` on the `negctl` arm** — there is no group
  law on that arm. Chain propagation is used instead, and the two methods were
  shown to agree wherever both exist.
- **Anything at scale.** No field above 24 bits, no discrete logarithm solved,
  no scalar recovered, no relation collected into a linear-algebra stage, no
  descent, no comparison against Pollard rho or BSGS, no cost model, no
  concrete-cost table. This experiment is not an attack and did not become one.
- **Absolute cost.** Wall-clock from this Python/sympy port is not comparable to
  a Sage run and was not used to fit anything (DEV-1).
- **Whether a single exponent exists at all.** HEUR-002 is unvalidated and,
  per `H-RT1476-001`, unvalidatable by three points.

---

## 12. Scope of everything above

Every number in this file is bounded by: these nine sampled ordinary
prime-order short-Weierstrass curves over `F_p` with `j` not in `{0, 1728}` and
`n != p`; `p` in `{1009, 65521, 16769023}` (10, 16 and 24 bits); seeds
`{20260728, 20260729, 20260730}`; the x-line factor base at
`L = round(q^(1/5))` = 4, 9, 28; the serial-S3 2|3 split at `m = 5`; this
Python/sympy GF(p) implementation and this declared query algorithm; 1200
screened targets and 10+10 measured targets per cell; and a 1827-second run.

Claim tier `toy`. Nothing here is evidence about cryptographic-size curves,
prime-field ECDLP hardness, index calculus at any relevant scale, KN-OPEN-001,
H-GGM-001, or any other hypothesis in this ledger. Nothing here closes or opens
the RT-1476-SUBRES-A1 gate; that is a decision, and decisions are not the
Executor's.
