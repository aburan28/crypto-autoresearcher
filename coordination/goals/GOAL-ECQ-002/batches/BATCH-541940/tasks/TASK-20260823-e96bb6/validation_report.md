# VAL-20260823-e96bb6 — independent validation, joints J1 and J2

Validator · TASK-20260823-e96bb6 · BATCH-541940 · GOAL-ECQ-002 · H-ECQ-8b600d

Snapshot read: **b6e071e03f84361ae1b6da3055ffaeb5ca1c8685**.
Requested policy `review-adversarial`; answered by **`claude-opus-5`** at reasoning effort
`xhigh` (the effort the `validator` agent binding carries for that policy),
`fallback_used: false`, `degraded_requirements: []`, `model_verified: false` — no
`adapter doctor --probe` was run in this session, so the resolved identifier is recorded
configuration rather than a probed fact.

**Blindness.** I read no output of the sibling reviewer TASK-20260823-33a825. It does not
exist in the tree: `coordination/goals/GOAL-ECQ-002/batches/BATCH-541940/tasks/` contains
exactly one entry, `TASK-20260823-416e78`. I read the review plan, the hypothesis, the goal,
the archive receipt, and the producer's package, and nothing else authored by a reviewer in
this round.

**Scope of this report.** I own J1 and J2 only. J3 and J4 (does tuple choice really move the
envelope; is the required null adequate) belong to the sibling. Where a finding of mine
touches those, I state the measurement and explicitly decline to adjudicate.

---

## 0. Terminal verdict, stated first

**`failed`, on my two joints.**

Everything I could recompute from the artifact recomputed **exactly** — every one of the 30
frontier rows, the envelope statistics, the 1 489/46 counts, the two-arm summary statistics,
the null-ladder matched window, the 5 092 distinct certified curves, the 86.7737 height, and
every certified rank I tested. The archive is sound: 100/100 declared hashes verify against
the snapshot tree. **The terminal negative — no cell taken at any of 30 rank thresholds — is
independently established and survives every check I ran.**

The receipt nevertheless fails, because three load-bearing statements in `report.md` are
false against the producer's own deliverable, and one of them contradicts the report's own
headline result:

| # | Report says | Artifact says |
| --- | --- | --- |
| F1 | §2: "none of those 46 produced a certified rank-12 fibre inside the searched T-box" | **8 of the 46 produced 12 certified rank-12 fibres inside the searched T-box**, including the report's own §1/§4 headline curve |
| F2 | §3: fibre at T=∞ is `I_14/I_12/I_10/I_8/I_6/I_4` per ceiling class; "the type of THAT fibre decides everything"; "18–20 `I_1` fibres over the finite T-line" | The fibre at ∞ is **`I_4` for 13 352 families and `I_6` for 39**. **No family anywhere has `I_8`, `I_10`, `I_12` or `I_14`.** Only **48 of 13 391** have all finite fibres irreducible |
| F3 | §5: "the ceiling stratification of §3 explains far more of the variance" | One-way η² by ceiling class = **0.028**; R² of envelope on `log P2` = **0.192**. The claim is backwards by ≈7× |

None of these changes the negative result. All three must be corrected by a superseding
record before this report is cited as the mechanism for anything.

A fourth finding is not an error but a missing control, and it is the most consequential
thing in this report: **the steep arm of the "two-arm law" fails a null-object control, and
the flat arm passes it** (§4.3). The half of the law the report emphasises is a degree count
that a structureless random surface reproduces *better* than Mestre's families do.

---

## 1. Archive and provenance checks

| check | result |
| --- | --- |
| 100 declared `path_sha256` recomputed against `git show b6e071e03:<path>` | **100 verified, 0 mismatched, 0 missing** |
| declared keyset vs `git ls-tree -r b6e071e03 <producer write_scope>` | 100 = 100, exact |
| `sha256(icarm_database_20260823.json)` vs H-ECQ-8b600d `frozen_snapshot_sha256` | `118db069…cadc59` = `118db069…cadc59` |
| `sha256(frontier_20260823.json)` vs the value the deliverable recorded at run time | `5eea69cf…850835` = `5eea69cf…850835` |
| frontier re-derived from the raw ICARM snapshot, all 30 thresholds | min naive height, `curve_id` and `n_curves_at_or_above` match on every row |
| ICARM's own `naive_height` for board curve 157 vs my `log max(|c4|³, c6²)` | 69.33884136527462 = 69.33884136527462 — the height convention is confirmed against an external source, not against the producer |
| in-flight commits cited by the manifests (`566cd442f`, `1e429e1b4`, `5b2168aad`, `93ad5e7bc`, `61a428da9`) | all exist, all ancestors of `b6e071e03` |
| any network or submission code in `scripts/` | none — no `requests`, `urllib`, `http`, or endpoint reference anywhere. "Nothing was submitted to ICARM" is supported by the code path |

### Run records

All 13 manifests carry id, task/goal/batch/hypothesis ids, `started_utc`, `wall_clock_seconds`,
`max_rss_kb`, `user_cpu_seconds`, `exit_code`, `status`, `git_commit`, `git_dirty: true`,
`seeds: [20260823]`, `certificate`, `budget`, `artifacts`. `environment.json` is byte-identical
across all 13 and carries the inference block (`requested_policy: executor-implementation`,
`resolved_model_id: claude-opus-5`, `reasoning_effort: medium`, `model_verified: false`,
`fallback_used: false`, `degraded_requirements: []`).

Sum of recorded wall clock = **2 460.9 s** (report says "~2 470 s"); peak RSS = 2 075 212 kB
= **2.03 GB**, so "peak RSS well inside 4 GB" is correct; 13 runs of an 80-run limit.

Two disclosed defects confirmed, both correctly handled as supersessions rather than edits:

- `RUN-ECQTUP-416e78-002/manifest.yaml` still reads `status: completed_valid`. It is superseded
  by `runs/VALIDITY-CORRECTION-RUN-002.md`, which is itself hash-bound by the archive. A
  consumer reading manifests alone would get the wrong status; that is the cost of immutability
  and the correction file is the right remedy.
- `certificate.kind: rank_lower_bound` is wrong in the manifests of runs 008, 009 and 010
  (pure measurement runs) and partially in 007. Confirmed by reading all 13 manifests. Disclosed
  in `implementation.md`; no deliverable depends on the field.

---

## 2. The archive receipt's six observations, adjudicated

The archive role raised these from the digest table without reading content. I read the content.

**O-RUN-002-EQUALS-RESULTS-RAW — the quarantine is COMPLETE.** `build_deliverables.py` opens
exactly six inputs: `tuple_envelope_scan_admissible.json` (RUN-003), `…_largespread.json`
(RUN-008), `…_spread57_74.json` (RUN-010), `null_ladder.json` (RUN-007), the three
`rank_search*.json` (RUN-005/006/011) and `certified_candidates.json` (RUN-004). It never opens
`results/tuple_envelope_scan_raw.json`, and no file under `scripts/` references that path at all.
The single RUN-002-derived datum in any deliverable is the hard-coded prose
`"10694 arbitrary tuples; 127 (1.2%) were admissible"`. I verified it against the raw file:
**10 694 rows, 127 with `deg_x_r == 4`, 10 567 with `deg_x_r == 5`.** Correct. Nothing downstream
of the height gate consumed the invalid run's output.

**O-RESULTS-MIRROR-RUNS** — confirmed and explained by `results/README.md`; `results/` was a
byte-identical mirror of run raw outputs and was partially deduplicated after the runs finished.
No run directory was touched.

**O-RUN-012-013-IDENTICAL** — both are deliverable builds. Their `best_candidates.json` outputs
are byte-identical because merging the spread-57–74 scan (RUN-010) changed deliverable 1 but not
deliverable 2: the rank-12 family `MESTRE-0,20,40,45,52,77` comes from the
`admissible_sampled_spread_57_400` stratum of **RUN-003**, not from RUN-010. Consistent with
`implementation.md` deviation 4. Benign; only RUN-013's output is the deliverable.

**O-RUN-009-STREAMS** — RUN-009 exited 2 on an `argparse` refusal of a flag that exists only in
the superseded `tuple_scan.py`; the diagnostic went to stderr and no stdout was produced. Operator
error, correctly recorded `invalid_measurement`, superseded by RUN-010. Per AGENTS.md core rule 5
this is an infrastructure/operator outcome and is not negative mathematical evidence; it is not
treated as such anywhere in the package.

**O-PRIMARY-DELIVERABLE-UNMATCHED** — confirmed: `tuple_envelope_scan.json` is assembled by
`build_deliverables.py` from three scans plus the null ladder, so it matches no single raw
result. Provenance traced end to end; I re-derived its summary blocks from the three source runs.

**O-ENVIRONMENT-UNIFORM** — confirmed, byte-identical across all 13 runs.

**O-BATCH-DOCS-UNBOUND (open item)** — I confirm the concern is live: `review_plan.yaml`,
`dispatch_queue.json` and `orchestrator_path_sha256.json` are not content-bound by any receipt.
I read `review_plan.yaml` at the snapshot commit; its binding rests on commit reachability alone.
This is the second batch to raise it. It does not affect any finding here.

---

## 3. J2 — height re-derived, rank re-certified, with my own code

I did not import, read-for-reuse, or invoke `exact_certify.py` or `build_deliverables.py`.
Everything in this section is mine, written from the statement of the quantity.

### 3.1 Naive height from a-invariants alone

For `[0, 0, 0, -75951713419, 5158556462007754]`:

```
b2 = 0                       b4 = -151903426838            b6 = 20634225848031016
c4 = b2^2 - 24 b4            = 3645682244112
c6 = -b2^3 + 36 b2 b4 - 216 b6 = -4456992783174699456
|c4|^3 = 48454759152074564819027247278303612928
 c6^2  = 19864784669271353518202571995926695936
naive_height = log max(|c4|^3, c6^2) = 86.77369390941135
```

**Exact agreement with the reported 86.77369390941135.**

*Minimality of the model, which the convention requires.* I recomputed
Δ = 16 545 124 121 992 599 132 421 687 084 708 864, verified the identity
c4³ − c6² = 1728 Δ, and factored Δ = 2¹⁰ · 23767 · 679822770033382319613563083.
A model is non-minimal at `p` only if v_p(Δ) ≥ 12; here **max_p v_p(Δ) = 10**, so the given
model is globally minimal and no scaling can reduce the height. The same check on all nine
distinct candidate curves: all nine minimal, all nine heights reproduce to `0.0`, and `c4`,
`c6`, `discriminant` as recorded all reproduce.

### 3.2 A second, fully independent derivation from the tuple

I re-implemented Mestre's construction from the `mechanism` field of H-ECQ-8b600d alone —
q(x) = Π(x − a_i), p = q(x−T)q(x+T), g the monic degree-6 truncated square root, r = g² − p,
the quartic → Jacobian map, clearing of denominators, minimalisation over Q[T], and
minimalisation of the specialisation over Z — and evaluated it at the reported (tuple, t):

| tuple | t | my height | producer | Δ |
| --- | --- | --- | --- | --- |
| (0,20,40,45,52,77) | 23 | 86.7736939094 | 86.7736939094 | 0.00e+00 |
| (0,1,2,5,6,7) | 1 | 25.4297385256 | 25.4297385256 | 0.00e+00 |
| (0,1,7,8,9,11) | 2 | 29.7727611270 | 29.7727611270 | 0.00e+00 |
| (0,1,29,32,33,37) | 10 | 61.1273905394 | 61.1273905394 | 0.00e+00 |
| (0,2,44,49,51,58) | 4 | 68.6386346419 | 68.6386346419 | 0.00e+00 |
| (0,1,53,55,64,67) | 9 | 74.1214782342 | 74.1214782342 | 0.00e+00 |
| (0,5,16,18,22,29) | 4 | 51.0697104504 | 51.0697104504 | 0.00e+00 |
| (0,2,17,18,25,28) | 2 | 49.5960009369 | 49.5960009369 | 0.00e+00 |
| **(−17,−16,10,11,14,17)** | 4 | **79.6237719007** | 79.6237719007 | 0.00e+00 |

The last row reproduces the published Mestre tuple A at 79.6238, matching the BATCH-f2341e
validator's independent 79.6 to four decimals through an implementation that shares no code
with either. The construction and the height convention are therefore established twice over,
end to end, from the tuple.

### 3.3 Rank ≥ 12, certified with my own certifier

**Method (mine).** Let ℓ be a prime with ℓ > 16, so ℓ is coprime to `#E(Q)_tors` by Mazur's
theorem and no torsion computation is needed. For a good prime `p` with ℓ ‖ N := #E(F_p), the
ℓ-Sylow of E(F_p) is cyclic of order ℓ and
`φ_p(P) = dlog_G((N/ℓ)·P)` is a homomorphism `E(F_p) → Z/ℓ` whose kernel contains every element
of order coprime to ℓ. If `P_1..P_s` were dependent in `E(Q)/tors` there would be a *primitive*
relation `Σ n_i P_i = T` (torsion), and `n ≢ 0 mod ℓ`; reducing and applying `φ_p` kills `T` and
gives `Σ n_i φ_p(P_i) ≡ 0 (mod ℓ)` for **every** such `p`. So F_ℓ-linear independence of the
rows over several primes certifies independence over Q. Integer arithmetic only: no floating
point, no Selmer bound, no PARI, no `ellrank` verdict.

**Result on `[0,0,0,-75951713419,5158556462007754]`.** All 23 exhibited points verified exactly
on the curve in rational arithmetic. ℓ = 17, 26 primes {41, 73, 271, …, 2633}:
**F_17-rank of the reduction matrix = 12**, independent columns
`[0,1,2,3,4,5,6,7,8,9,13,14]` — the *identical* index set the producer recorded, reached by a
different route. Stable at ℓ = 19, 23 and 29 (rank 12 in each, 30 primes each).

**Controls on my own certifier.**

| control | expected | got |
| --- | --- | --- |
| positive: board curve id 1 (published rank 12, h 79.3287), 12 points | ≥ 12 | 12 |
| positive: board curve id 157 (published rank 12, h 69.3388) | ≥ 12 | 12 |
| positive: board curve id 50 (published rank 11) | ≥ 11 | 11 |
| positive: board curve id 42 (published rank 1) | ≥ 1 | 1 |
| negative: {P₀, 2P₀, 3P₀, P₁, P₀+P₁} — true rank 2 | 2, not 5 | **2** |
| negative: all 23 points replaced by 2·themselves | 12, not more | 12 |
| negative: the 23 points duplicated to 46 columns | 12, not more | 12 |

**Coverage.** All nine distinct candidate curves re-certified at their claimed rank
(2, 5, 6, 7, 8, 9, 10, 11, 12 — exact agreement, none higher, none lower). A stratified sample
of 20 fibres from RUN-005/006/011 (6 of them rank ≥ 11) re-certified: **20 of 20 exact
agreement**, every exhibited point exactly on its curve.

**J2 verdict: `holds`.** The height is right, the model is minimal, the rank lower bound is
genuinely certified from exhibited points in exact arithmetic, and it does not rest on any
producer code.

### 3.4 The other J2-adjacent claims

- **"5 092 distinct curves were certified"** — recomputed as the number of distinct `curve_key`
  values carrying a `certified_rank_lower_bound` across RUN-004/005/006/011: **5 092**, exact.
- **"the four reported curves are not board curves rediscovered"** — confirmed. Going further
  than the report did, I checked **all 5 092** against the frozen snapshot: exactly **two** are
  board curves, ids **108** (rank ≥ 5, h 29.7728) and **162** (rank ≥ 9, h 74.3195). Neither is
  among the four §4 curves.
- **However**, board curve 108 *is* the "our best certified" entry in the §4 table at
  thresholds r ≥ 3, 4 and 5. `best_candidates.json` flags it correctly
  (`already_on_the_frozen_icarm_board: true`); **`report.md` does not say so anywhere.** No cell
  is claimed there, so C1′ is not at risk, but a reader of the report alone would take a
  rediscovered board curve for a curve this program exhibited.

---

## 4. J1 — the envelope law, and the per-family ceilings

### 4.1 Everything numeric reproduces

| quantity | reported | my recomputation |
| --- | --- | --- |
| n families | 13 391 | 13 391 |
| envelope min / median / max | 25.42973852559282 / 110.70448734398212 / 245.69015790294898 | identical |
| spread | 220.26041937735616 | identical |
| families with envelope < 79.329 | 1 489 | **1 489** |
| …of those, ceiling ≥ 12 | 46 | **46** (43 at ceiling 13, 3 at ceiling 15) |
| steep-arm slope median / IQR | 22.096606026773458 / [19.8319, 24.3180] | 22.096606026773458 / [19.8326, 24.3179] |
| flat-arm slope median | −0.4773008249340968 | identical |
| envelope ~ log P2 | a −4.536633, b 14.688963, sse 6 420 036.479, R² 0.191652 | identical |
| by-ceiling min envelopes (5/7/9/11/13/15) | 25.430 / 38.353 / 30.323 / 29.773 / 50.450 / 70.259 | identical |
| max certified rank by ceiling class | 5 / 7 / 8 / 9 / 12 / 12 | identical |
| null-ladder matched window and its four rungs | [5.099866427824199, 8.178077463849608]; 147/44.8367/101.1711, 44/42.7555/79.6141, 50/49.8501/111.2079, 96/69.0499/136.4378 | identical to 4 dp, window to 9 dp |
| per-rank-threshold table, all 30 rows | see deliverable | **all 30 reproduce; `cell_taken` false on every row** |

I also reproduced the tuple enumeration independently: **3 819 816 tuples tested, 5 817
admissible canonical tuples at spread ≤ 56** — exact match to the producer's counts.

**Frontier discipline.** `build_deliverables.py` opens the frozen frontier and the frozen
snapshot at run time, recomputes both sha256 values, and writes every one of the 30 incumbents
from what it read; all 30 reproduce. The pre-committed disbelief "any frontier value that was
TRANSCRIBED" is discharged, with **one exception worth recording**: `INTERMEDIATE_BENCHMARK =
79.329` is hard-coded in `build_deliverables.py`. It is declared as coming from H-ECQ-8b600d and
not from the frontier file, and H-ECQ-8b600d does carry 79.329 — but the frozen board's actual
value for curve 1 is **79.32867457792244**, so the benchmark is a rounded transcription, rounded
in the direction that makes it marginally *easier* to beat. Immaterial against a +7.4447 miss;
recorded because it is exactly the class of number the plan told me to distrust.

### 4.2 The two arms are genuinely fitted separately

Confirmed from `measure.two_arm_fit` and from the raw RUN-003 records: the breakpoint is free
(`k` ranges over 3 … len−2, chosen to minimise total SSE) and it is **not** pinned at the
30-small-t / 8-large-t seam of the box. Breakpoint index 30 occurs in only 78 of 5 627 families
(1.4%); the distribution is broad with a mode at 29 (620, 11%). The BATCH-da59ec failure mode —
one line fitted across the vertex, vertex landing on the box edge — is genuinely fixed. Crossover
`log H` has median 3.064 with q10/q90 = 2.254/3.907, comfortably interior to
[0, log 800 = 6.685]; only 60 of 13 391 fall outside the box.

### 4.3 The steep arm fails a null-object control; the flat arm passes it

`docs/inventor-protocol.md` §3 requires that a reported signal be measured against a null object
of the same shape before it is believed. **The producer ran no null object for the envelope law.**
(The null ladder in §6 controls the *rank* premise, which is the sibling's joint, not the law.)
So I ran one.

Null object: `Y² = X³ + A(T)X + B(T)` with `deg A = 8`, `deg B = 12` and random integer
coefficients — the same surface degree `d = 2`, the same T-box, the same minimalisation, the same
envelope construction, the same segmented fit, and **no Mestre structure of any kind**. Three
independent nulls with coefficient magnitudes spanning three orders (10⁴/10⁶, 10²/10³, 10/30),
35 families each:

| | steep-arm slope q25 / median / q75 | steep R² | flat-arm slope q10 / median / q90 | flat R² |
| --- | --- | --- | --- | --- |
| null-1 (coeffs ≤10⁴/10⁶) | 23.94 / **24.04** / 24.13 | **1.000** | 18.83 / **20.82** / 24.19 | 0.998 |
| null-2 (coeffs ≤10²/10³) | 23.96 / **24.02** / 24.22 | **1.000** | 18.34 / **21.01** / 23.10 | 0.997 |
| null-3 (coeffs ≤10/30) | 23.99 / **24.09** / 24.19 | **1.000** | 18.65 / **20.86** / 23.71 | 0.998 |
| **Mestre scan** | 19.83 / **22.10** / 24.32 | 0.898 | −5.47 / **−0.48** / +4.97 | 0.075 |

Two conclusions, and they point in opposite directions:

- **The steep arm carries no information.** A structureless degree-matched surface reproduces
  slope 24 at R² = 1.000 — *better* than Mestre's families do. "Steep arm of slope 12d = 24" is a
  restatement of `deg c4(T) = 4d = 8`, `deg c6(T) = 6d = 12` ⇒ `h(t) ~ 24 log t`. It is a degree
  count, not a fact about Shioda–Tate, about Mestre's construction, or about the tuple. The
  report presents its agreement with 24 as confirmation of the law; on this control it is the
  uninformative half, and Mestre's families agree with it *worse* than nothing does.
- **The flat arm is real and is construction-specific.** All three nulls have **no flat arm at
  all** — their left arm has slope ≈ 21 at R² ≈ 0.998, i.e. the null envelope is a single straight
  line and the segmented fit finds no genuine break. The Mestre families' left arm sits at median
  −0.48 with R² 0.075, the signature of a floor plus noise. The two-arm *structure* survives the
  control, and it is the half on which H-ECQ-8b600d's lever actually rests.

**And the hypothesis's own claim is better supported than the report shows.** H-ECQ-8b600d says
"the envelope minimum is governed by the INTERCEPT". The report never regresses envelope on the
intercept; it regresses on `log P2` and gets R² = 0.19. I ran the stated regression:

```
envelope ~ flat-arm intercept :  slope 0.8132,  R^2 = 0.7732,  n = 13391
```

The intercept claim is strongly supported. The report leaves its own hypothesis's strongest
measured result on the floor.

### 4.4 Why the steep median is 22.10, and why the report's explanation is wrong

The report explains median 22.10 < 24 as "what a box truncated at t = 800 should produce". That
is not what the artifact says. Using my own construction I measured the residual
`h(t) − 24 log t` at the eight large-t nodes for an 18-family sample: it **fluctuates by 13.2 to
43.0 log units within a single family**, against a total steep-arm rise of only
24·(log 800 − log 40) ≈ 71.9. Local slopes at t = 2000 → 20000 hit exactly 24.000 for several
families, so truncation at 800 is not the mechanism. The mechanism is arithmetic: minimalisation
removes a t-dependent amount, so `h(t)` sits *below* the 24 log t line by a fluctuating offset,
and the fitted slope is a noisy estimator of 24, biased low. Decisively against the truncation
story: **3 850 of 13 391 fitted steep slopes exceed 24**, up to **75.70** (and the minimum is
−6.34), which a downward truncation bias cannot produce.

The summary numbers are honest; the causal explanation attached to them is not supported.

### 4.5 F3 — the variance claim in §5 is backwards

> §5: "Content predicts the envelope in the mean and predicts it weakly; the ceiling
> stratification of §3 explains far more of the variance."

One-way ANOVA on the envelope with groups = own Shioda–Tate ceiling class:
**η² = 0.02798**. Linear R² of envelope on `log P2`: **0.19165**. The ceiling stratification
explains 2.8% of the envelope's variance; the content statistic explains 19.2%. Within the
dominant ceiling-9 class the content R² is unchanged (0.192), so the stratification is not even
absorbing the content signal. The ceiling matters for *which families can host rank 12* — which
is a true and important point — but it does not explain the envelope's variance, and the report
says the opposite.

### 4.6 J1(b) — the ceilings ARE computed from each family's own fibre configuration

This half of the joint **holds**, and the BATCH-da59ec F1 error is genuinely fixed.

- `surface.py` computes `10d − 2 − Σ_v deg(v)·(m_v − 1)` from the family's own discriminant
  factorisation. The generic bound 18 is stored under the key `generic_K3_bound_NOT_USED` and is
  never read. I confirmed by tracing `build_deliverables.py`.
- **I recomputed the ceiling from the recorded `fibre_types` for all 13 391 families: 0
  mismatches**, and `Σ deg·(m_v−1)` reproduces on all 13 391. All 13 391 have `d = 2`.
- I re-derived the whole chain — construction, Jacobian, minimal model over Q[T], discriminant
  factorisation, Kodaira type from `(v(c4), v(c6), v(Δ))` in residue characteristic 0, fibre at
  infinity by `(4d−deg a4, 6d−deg a6, 12d−deg Δ)`, and the ceiling — **with my own code** for
  eight families spanning all six ceiling classes:

| family | d | Σ(m_v−1) | ceiling (mine = producer) | Euler Σ deg·v_disc |
| --- | --- | --- | --- | --- |
| MESTRE-0,1,2,5,6,7 | 2 | 13 | **5** | 24 = 12d |
| MESTRE-0,1,2,8,9,10 | 2 | 11 | **7** | 24 |
| MESTRE-0,1,2,3,4,5 | 2 | 9 | **9** | 24 |
| MESTRE-0,1,7,8,9,11 | 2 | 7 | **11** | 24 |
| MESTRE-0,4,17,18,26,31 | 2 | 5 | **13** | 24 |
| MESTRE-0,1,55,56,57,62 | 2 | 3 | **15** | 24 |
| **MESTRE-PUBLISHED-A** | 2 | 3 | **15** | 24 |
| MESTRE-0,20,40,45,52,77 | 2 | 5 | **13** | 24 |

- **Proves-too-much control.** Mestre's published tuple A is an object whose conclusion is known:
  rank ≥ 11 over Q(T). If the ceiling code assigned it a ceiling below 11 the code would be
  wrong. It assigns **15**. The code does not prove too much on the one object where it could
  have been caught out.

### 4.7 F2 — but the §3 mechanism narrative is false against the artifact

The §3 table's *numbers* are all correct: `Σ(m_v−1)`, the ceilings, the family counts
(17/16/13257/5/82/14), the minimum envelopes and the max certified ranks all reproduce exactly.
Its **first column does not**. From the deliverable's own `fibre_types` field:

```
fibre type at T = infinity, across all 13 391 families:  I_4 : 13 352      I_6 : 39
                                                        (nothing else, at all)
families whose finite fibres are ALL irreducible:        48 of 13 391
Kodaira types actually present (deg-weighted): I_1 107936, I_2 79802, I_4 13386, I_6 39, I_3 20, III 2
```

The report's column `I_14 / I_12 / I_10 / I_8 / I_6 / I_4` is exactly `Σ(m_v−1) + 1` for each
row. It was **back-derived by assuming `Σ_v (m_v − 1) = m_∞ − 1` and inverting**, not read from
the fibre data — and that assumption is false for 13 343 of 13 391 families. Consequences:

- "Each has 18–20 `I_1` fibres over the finite T-line and exactly one multiplicative fibre at
  T = infinity" is true for **48** families. The modal class (13 256 families) has 8 `I_1`
  (degree-weighted) over the finite line **plus six `I_2` fibres**, which is where its
  `Σ(m_v−1) = 9` comes from. Concretely, `MESTRE-0,1,2,5,6,7` (ceiling 5, and the family holding
  the global minimum envelope 25.4297) has fibres
  `I_2, I_4, I_4, I_2, I_2, I_2, I_1(deg 2), I_1(deg 2), I_4(∞)` — an `I_4` at infinity, not an
  `I_14`.
- "the type of THAT fibre decides everything" is the reverse of the truth. The fibre at infinity
  is nearly constant across the population (`I_4`, 99.7%); the **discriminating variable is the
  reducible fibres over the finite T-line**.
- "This is exactly the mechanism the BATCH-da59ec validator found in Nagao's family (an `I_4` at
  infinity costing 3), generalised" is therefore not what was found. The `I_4` at infinity costs
  3 in almost every family here and explains none of the variation. The real finding — that the
  rank-hosting families are precisely those with **no reducible finite fibre** — is more specific
  and more useful, and it is stated nowhere.
- "Mestre's rank ≥ 11 statement is a statement about the sparse `I_4` subfamily (14 of the
  13 391)" — the count 14 is right, the label is wrong: 13 352 families have `I_4` at infinity.
  The 14 are the ceiling-15 families, i.e. those whose finite fibres are all `I_1`. (Both
  published tuples land there, which is the control in §4.6.)

Separately, the attribution "Mestre's rank ≥ 11 statement is a statement about …" is a claim
about Mestre's paper. `implementation.md` states the construction was taken from H-ECQ-8b600d and
the BATCH-da59ec validator, "not from memory of Mestre's paper", so the provenance of the
*construction* is `internal` and correctly declared; but this §3 sentence characterises the
*paper's scope* and is load-bearing for the report's structural story. Per AGENTS.md rule 9 that
is a `recalled` reference doing real work. The frozen board's own commentary for curve 1 records
only "Found by Mestre (1982). A historical rank ≥ 12 record, via Dujella's elliptic-curve
rank-records tables." Report as **incomplete evidence**, remedied by retrieval, not as
fabrication.

---

## 5. F1 — a budget-truncated, and in one place simply false, negative

This is the item the task card asked me to attack, and it is where the report is worst.

### 5.1 The false sentence

> §2: "Of the 1 489 families whose envelope is below 79.329, only **46** have a Shioda-Tate
> ceiling that even permits rank 12, and **none of those 46 produced a certified rank-12 fibre
> inside the searched T-box**."

The 1 489 and the 46 are correct. The rest is false. Scanning RUN-005/006/011 for every fibre
with `certified_rank_lower_bound ≥ 12`:

| run | family | t | h | ceiling | family envelope | in the 46? |
| --- | --- | --- | --- | --- | --- | --- |
| 006 | MESTRE-0,20,40,45,52,77 | 23 | **86.7737** | 13 | 69.2833 | **yes** |
| 011 | MESTRE-0,2,37,38,56,59 | 13/2 | 91.0445 | 13 | 72.4300 | yes |
| 006 | MESTRE-0,1,46,50,51,56 | 15/2 | 91.3854 | 13 | 67.6707 | yes |
| 006 | MESTRE-0,5,16,18,22,29 | 60 | 106.5748 | 13 | 51.0697 | yes |
| 011 | MESTRE-0,7,25,56,63,74 | 15, 27 | 107.8239, 109.5074 | 15 | 75.7845 | yes |
| 011 | MESTRE-0,3,31,41,56,61 | 4, 9, 30 | 109.8671, 113.8411, 120.0591 | 13 | 69.3953 | yes |
| 006 | MESTRE-0,4,30,35,43,50 | 12, 40 | 115.0901, 117.2745 | 13 | 71.1215 | yes |
| 006 | MESTRE-0,1,26,27,35,37 | 90 | 116.3032 | 13 | 58.6306 | yes |

**Eight of the 46 families produced twelve certified rank-12 fibres inside the searched T-box** —
the first of them being the report's own §1/§4 headline curve. §2 contradicts §1 and §4 of the
same document.

What is true, and what the report presumably meant: **no rank-12 fibre was found below 79.329**;
the minimum height over all certified rank-12 fibres anywhere is **86.77369390941135**. And the
substantive structural fact, which is more informative than the sentence that replaced it:

> within a family, the envelope minimum and the rank-12 locus are **disjoint**. The headline
> family's envelope minimum is at t = 4 with h = **69.28330998318052**, and I independently
> certified the rank there as **8** (PARI's own `r_high` at that fibre is also 8, so the rank is
> exactly 8). Its rank-12 fibre is at t = 23, 17.49 log units higher.

That 69.2833 is itself worth surfacing: it sits **below** the frozen r ≥ 12 incumbent 69.3388.
It is not a cell — the rank there is 8 — but it is the closest thing in the run to a near-miss,
and it appears nowhere in the report. This is exactly the number the plan's prior P1 told me to
find and disbelieve first; I re-derived it from a-invariants and from the construction, and it
is real, and it is a rank-8 curve.

### 5.2 The truncation the report does state, quantified

Confirmed from the raw records: RUN-005, RUN-006 and RUN-011 all carry
`time_budget_reached: true`, and `n_pari_alarms_infrastructure` = 0 + 2 + 1 = **3**, matching the
report. These are infrastructure outcomes and the package treats them as such — I found no place
where a timeout is presented as mathematical evidence. The general caveat is stated in §7 ("this
is a lower-bound search… fibres outside the T-box… are untested") and §8 ("the searched fibre
sets are smaller than the fibre sets the families offer, so the §4 minima are upper bounds").

What is **not** stated anywhere is how thin the search actually was:

- Of the 46 candidate families, coverage over the pre-declared 73-value T-box ranges from
  **4 to 66 fibres**. **Not one of the 46 was searched at all 73 values.** Six were searched at
  ≤ 20 (4, 7, 13, 18, 20, 20).
- Coverage by ceiling class, as families with any fibre searched: ceiling 9 → **295 of 13 257**;
  ceiling 13 → 53 of 82; ceiling 15 → 8 of 14; ceiling 11 → 3 of 5; ceiling 7 → 11 of 16;
  ceiling 5 → 13 of 17.
- Consequently the §3 column "max certified rank observed" (5, 7, 8, 9, 12, 12) is a maximum over
  a small and **deliberately non-random** subsample: RUN-006 and RUN-011 searched
  `--only-min-ceiling 12`, i.e. they spent the budget on precisely the two classes where 12
  appears, while ceiling 9 was reached only through the top-400-by-envelope RUN-005. The
  monotonicity the report reads as structural coupling is partly a map of where the budget went.
  I do not claim it is *only* that — the ceiling is a genuine upper bound on generic rank, and in
  classes 5 and 7 the observed maximum equals the ceiling exactly — but the confound is real and
  undisclosed.

So: the report does not, on my reading, present a timeout as negative evidence, and §7/§8 are
honest. But §2's negative-existence sentence about a specific enumerated set of 46 families
carries no inline caveat, and the per-family coverage that would let a reader judge it is
recorded nowhere.

---

## 6. Coverage and accounting gaps

**462 families were dropped with no record of which or why.** Across RUN-003/008/010:
13 984 attempted, **13 522 measured**, `n_family_failures = 0` and `n_refused_not_quartic = 0` in
every run. `tuple_scan_v2.py` computes `n_families_attempted = len(rows)+len(failures)+
len(refused)` but emits only `[r for r in rows if r['status']=='measured']`, so a family that
returns `no_measurable_fibre` vanishes into the arithmetic difference with no tuple recorded.
That is a coverage-record gap under the artifact policy and AGENTS.md rule 8.

**I closed the gap for the largest stratum myself.** I re-enumerated the spread ≤ 56 stratum
independently (3 819 816 tested, 5 817 admissible — exact match) and found the **248** canonical
admissible tuples absent from the deliverable. I then computed the surface discriminant for each
with my own code: **248 of 248 are genuinely degenerate** — `-16(4A(T)³+27B(T)²) ≡ 0`, so they
carry no elliptic surface at all. The exclusion is mathematically correct. Only its
*documentation* is missing. The honest scope sentence is "13 624 admissible, of which 462 are
degenerate and 131 are canonical duplicates across strata, leaving 13 391 measured", not §7's
"all canonical admissible integer 6-tuples of spread ≤ 74 (13 624 of them)".

**One duplicate family.** 13 391 rows = 13 390 distinct canonical tuples + 1: Mestre's published
tuple A appears both as `MESTRE-PUBLISHED-A` and as `MESTRE-0,1,27,28,31,34`, with **identical**
envelope 79.62377190070106. Statistically negligible; it is also an incidental confirmation that
the declared translation symmetry of the construction is exact.

**Null-ladder window exclusion asymmetry — flagged, not adjudicated.** The matched-content window
is built on `log P2`, which is undefined where `P2 ≤ 0` (possible once `q` has irreducible
quadratic factors). Excluded on that criterion: **0 of 150** in the k = 6 treatment, 2 of 68 at
k = 4, **16 of 72** at k = 2, **34 of 150** at k = 0. The exclusion rate is monotone in the
treatment variable. The four rungs' in-window statistics all reproduce exactly, so this is not a
recomputation failure; it is a question about whether the matched comparison is matched. **That
is joint J4 and belongs to the sibling reviewer.** I record the measurement and stop.

---

## 7. The admissibility identity, tested harder than the report tested it

Claim: with `c_i = 6 a_i − Σa`, `deg_x r = 4 ⟺ 12 Σ c_i^5 = 5 (Σ c_i²)(Σ c_i³)`, "verified
against the symbolic `deg_x r` on 400 random tuples with zero mismatches".

**The producer's stated control is essentially one-sided.** At an admissible density of 0.15%,
400 uniform draws expect 0.6 positives. My own 400 random draws produced **0 admissible** and
all 400 had `deg_x r = 5`, so a 400-tuple random test can only exercise the "both false" branch.
As stated, it is not evidence about the forward direction. (`implementation.md` deviation 6 is
right that nothing depends on it, because `tuple_scan_v2.py` re-checks `deg_x_r == 4` symbolically
per family and refuses otherwise — and indeed `n_refused_not_quartic = 0` in every run.)

**I established the identity outright instead.** Computing `r = g² − p` symbolically over Q[T]
with my own code on 200 random tuples:

```
[x^5] r  ==  ((24/5) P5 - 2 P2 P3) * T^2      exactly, with EVERY other T-coefficient zero
                                              200/200, no counterexamples
```

Since `[x^5] r` is a single monomial in T with that coefficient, `deg_x r = 4` holds **iff**
that coefficient vanishes, which is the stated identity. **False negatives are therefore
impossible**, and no admissible tuple can have been silently skipped by the pre-filter. I also
confirmed the positive branch on 60 producer-declared admissible tuples and both published
tuples (all `deg_x r = 4`, identity true), and the claimed translation and scaling invariance.

This one is stronger than the report claims, not weaker.

---

## 8. The recorded priors, held to

**P1 — "I expect tuple choice to move the envelope substantially… disbelieve ANY reported
envelope below 79.329; recompute such a curve's height from its minimal a-invariants alone and
check it is not a board curve rediscovered."**

Held to and discharged. 1 489 families do have envelopes below 79.329 and the numbers are real:
I re-derived the global minimum 25.42973852559282 (family `MESTRE-0,1,2,5,6,7`, t = 1) from the
minimal a-invariants alone *and* independently from the tuple through my own construction, and it
is not on the board. **But they are not comparable to 79.329.** 79.329 is a rank-12 value; the
envelope minima belong to fibres of low certified rank — the global-minimum fibre certifies at
rank 2, and the headline family's own envelope fibre at rank 8. On the metric that matters,
height at certified rank ≥ 12, the best is 86.7737, missing 79.329 by +7.4447 and the r ≥ 12 cell
by +17.4349. The producer states this plainly in §1 and again in §4 ("74.1215 at certified rank
≥ 11 … must not be read as beating" 79.329), and does not smuggle the raw-envelope reading. The
prior's optimistic pole is **not** confirmed on the cell-relevant metric.

My null control refines the prior further: of the 220-log-unit spread, the part attributable to
the *steep* arm is a degree count that a structureless null reproduces at R² = 1.000, while the
part attributable to the *flat arm intercept* is real and tuple-driven (R² 0.773 of the envelope
on the intercept). So the lever survives, but it lives entirely in the intercept — which is what
H-ECQ-8b600d said, and not what §5 of the report measured.

**P2 — "the best tuple lands near 79 and does not reach the r ≥ 12 cell."** Confirmed
independently: 86.7737 against 79.329 and 69.3388, both missed. **No `review-breakthrough`
escalation is triggered by anything I verified.**

**P3 — the required null.** Sibling's joint (J4). I reproduced its numbers exactly and recorded
the window-exclusion asymmetry in §6 without adjudicating.

**Pre-committed disbelief.**
1. *"Any claim that a cell was taken"* — none is claimed, and I verified independently that none
   was: recomputing "our best certified" per threshold from the 5 092-curve certified set and
   comparing to the frontier read from the frozen file gives `cell_taken = false` on all 30 rows.
   All four conditions of C1′ are moot because the first (a cell taken) fails; **the negative is
   correctly established for the tested scope**, with the scope caveats of §5.2.
2. *"Any frontier value that was TRANSCRIBED"* — discharged, with the `79.329` rounding recorded
   in §4.1.
3. *"Any ceiling taken from the generic K3 bound"* — discharged; every ceiling comes from the
   family's own fibre configuration, verified 13 391/13 391 and re-derived from scratch for 8.

---

## 9. What I could not check

- I did not probe the backend, so `model_verified: false` for this session as well as the
  producer's.
- "No network call was made at all" is supported by the absence of any network import or endpoint
  reference in `scripts/`, but I cannot verify the negative from the artifacts alone.
- Certified rank is a **lower** bound throughout, mine as well as the producer's. Nothing here
  says any of these curves has rank *exactly* 12.
- My ceiling re-derivation is complete for 8 families and arithmetic-only (from the recorded
  `fibre_types`) for the other 13 383. A `fibre_types` field that were itself wrong for some
  family outside my 8 would not be caught by the arithmetic check. The 8 were chosen to span all
  six ceiling classes and both fibre-at-infinity types.
- The Shioda–Tate ceiling `10d − 2 − Σ(m_v−1)` is the geometric bound over Q̄(T); the bound over
  Q(T) is at most this. `surface.py` says so and the deliverable does not claim otherwise.
- Coverage of the rank searches is what §5.2 reports; I did not extend any search.
