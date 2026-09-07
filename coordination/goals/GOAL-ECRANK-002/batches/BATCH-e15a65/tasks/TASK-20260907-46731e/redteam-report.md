# RED TEAM REPORT — TASK-20260907-46731e

- **Task**: TASK-20260907-46731e · **Goal**: GOAL-ECRANK-002 · **Batch**: BATCH-e15a65
- **Question**: RQ-ECRANK-27dcc5 · **Opening decision / frozen review plan**: `ledger/decisions/DEC-20260907-9953c0.yaml`
- **Package under review**: `experiments/EXP-ECRANK-73275e/` version 1, snapshot commit `03c6e3181bc54b67ab3904b5f6187dbe4e6cb3ad`
  (verified: `git diff --stat 03c6e318 HEAD -- experiments/EXP-ECRANK-73275e` is empty at this worktree HEAD `51af17ddf`)
- **Joints owned**: J5, J6, J7, plus the `proves_too_much` control. J1–J4 belong to TASK-20260907-d47eb0 and are not answered here.
- **Role**: red-team, `review-adversarial`, independent session. Read no sibling report.

## Standing limits on everything below

Every statement is scoped to: n ∈ {6, 8}; nested H ≤ 10^4 at n = 6 and ≤ 10^3 at n = 8; the seeded
10^4 b-tuple sample per construction arm; b-tuples in affine normal form b1 = 0, b2 = 1, b3..bn
distinct integers in [−20, 20] \ {0, 1}; support (−1, 2, 3, 5, 7, 11, 13); exact stdlib
`fractions.Fraction` arithmetic; the 1.0e8 counted-op cap; toy claim tier. Nothing here transfers to
cryptographic parameters, to rank over Q in general, or to any n outside {6, 8}.

I change no status, promote nothing, assign no F1–F4 finding, modify no raw artifact, commit
nothing, and state no whole-claim verdict. AGENTS.md core rule 3 binds throughout: the R5 counted-op
exhaustion, the `degenerate_deg_s_2` rejections, and every implementation shortfall named below are
instrument facts, never negative mathematical evidence about HEUR-1, C1, or H-ECRANK-36d8d7.

## What I actually computed (independence statement)

I ran **four** checks, all against committed bytes at the snapshot, all with code I wrote from the
mathematical definitions in a scratch directory. **No producer module was imported. No experimental
arm was re-run.** The R3 and R5 arms were not re-executed; R7's and R6's *inputs* were re-derived
from the committed driver's declared seeds, which is input reconstruction, not a re-run — no
certifier, no build, no run record was produced.

| # | check | inputs (committed) | outcome |
|---|---|---|---|
| C-A | degree of `s = g² − p` for the d=(1..1) Mestre object | R8 `raw-result.json` b-tuples; R7 tuples re-derived from seed 760812; 3000 random tuples per n | see J5(a) |
| C-B | full structural re-verification of all 28 R3 instances | R3 `raw-result.json` `found` | 28/28 pass, 10 checks each |
| C-C | root-fate audit of the 20 feasible R3 tuples | R3 `raw-result.json` | 34 roots, all fates explained |
| C-D | what object R6 actually solved | R6 tuples re-derived from seed 760806 | A = B = C = 0 on all 64 |

---

# J5 — do the controls discriminate?

**Verdict: BREAKS.** Not one of R6, R7(n=6), or R8 could have failed. R7(n=8) could have failed and
did not fail in the only direction it tests soundly. The counted R3 result has no positive control
behind it in this package or in its predecessor.

## The one fact that decides most of J5

Every control object in the package — R6's null family, R7's known-false family, R8's plants — is
built on the **all-ones class pattern d = (1, 1, …, 1)**. At n = 6 that value annihilates the
mechanism the counted arm measures, in two independent ways, and it does so as a theorem, not as an
outcome:

**(T1)** `E.mestre_polys` (`source/ecrank_engine.py:394`) sets `g = polysqrt_trunc(p, k)`, the unique
monic degree-k polynomial with `deg(p − g²) ≤ k − 1` (`ecrank_engine.py:380–391`). Therefore
`deg s = deg(g² − p) ≤ k − 1 = n/2 − 1`. At **n = 6 that is deg s ≤ 2**; at n = 8 it is ≤ 3.
`E.build_instance` accepts only `deg ∈ (3, 4)` and otherwise returns `degenerate_deg_s_%d`
(`ecrank_engine.py:806–808`). **So at n = 6 the d=(1..1) Mestre object is rejected for every b-tuple,
every seed, and every sample size.**

**(T2)** At d = (1,…,1) the interpolant δ = `lagrange_interp(xs, [1]*n)` is the **constant polynomial
1**. Hence for `g = x + t`, `s = δ·g² mod p = (x+t)²`, whose x^5 coefficient is identically zero.
The n = 6 ellipticity quadratic therefore has **A = B = C = 0 identically**, for every b-tuple and
every t. `NF.d1_quadratic_coeffs` (`source/null_family.py:20–47`) returns (0, 0, 0);
`construct._quad_rational_roots(0, 0, C)` returns `[]` at `construct.py:116–118`.
**So `construct.solve_n6(engine, b, [1]*6, H)` returns `kept = []` for every b and every H.**

C-A confirms (T1) empirically with independent code: deg s = 2 on **all 9** R8 b-tuples recorded in
`runs/RUN-ECRANK-73275e-R8-planted/raw-result.json`, deg s = 2 on **all 8** re-derived R7 n = 6
tuples, deg s = 3 on **all 8** re-derived R7 n = 8 tuples, and over 3000 random b-tuples per n:
n = 6 → {deg 2: 2999, deg 0: 1}, **never 3 or 4**; n = 8 → {deg 3: 2994, deg 2: 6}.
C-D confirms (T2) with independent code: (A, B, C) = (0, 0, 0) on **all 64** R6 tuples, δ of degree 0.

## J5(a) — R7, the known-false control

**n = 6: DOES NOT DISCRIMINATE — mathematically unsatisfiable as frozen.**
`experiments/EXP-ECRANK-73275e/specification.yaml` IV-1 requires "certified totals must equal n − 1
(5 …)" at n = 6. By (T1) the object it names has deg s ≤ 2 and is not an elliptic object at all — it
is a conic. No implementation of "the d = (1,1,…) Mestre degeneration at n = 6" can produce a rank
certificate, so the required value 5 is unreachable by construction, independently of this executor.
The recorded `n6_per_b_built: false` with `degenerate_deg_s_2` on 8 of 8
(`execution-report.yaml`, R7 `observations_quoted`) is the filter **behaving correctly on a genuinely
degenerate object** — the symmetric trap the Coordinator prior flagged is real — **and** that is
exactly why the control carries no information: the outcome was fixed before the seed was chosen.
Corroboration inside my read scope: `ledger/evidence/EV-ECRANK-8b35bb.yaml` `certificate_refs` lists
40 known-false certificates, `kf-n8-b00..b19` and `kf-n10-b00..b19` — **there is no `kf-n6-*`**. The
predecessor never ran this control at n = 6. The n = 6 clause is new in this contract and is ill-posed.

**n = 8: DISCRIMINATES IN ONE DIRECTION ONLY, AND PASSED THAT DIRECTION.**
`certify76.py` sets `certified = cert["certified_rank_lower_bound"]` (module docstring
`certify76.py:56–60`, "Claim: rank E0'(K_V) >= aggregate_total"). `aggregate_total` is a **lower
bound**. A lower bound that comes in at 5 or 6 instead of 7 is a completeness shortfall, not an
unsoundness: it cannot be a counterexample to the object under test. The direction that *is* a
soundness test — the certifier claiming **more** rank than the family admits — is exactly what
`EV-ECRANK-8b35bb` records the predecessor as testing: "`total = n` occurred ZERO times over 40
seeded instances … never exceeding n−1". Recorded here:
`n8_aggregate_totals: [5, 6, 7, 7, 7, 7, 6, 7]`, max 7 = n − 1, **0 of 8 above n − 1**. The
soundness half of the known-false control **passed**.
The frozen IV-1 text converted the predecessor's one-sided ceiling test into a two-sided equality
test on 8 freshly seeded tuples, which is a stronger and differently-directed requirement than the
control it inherits. That mis-transcription, not the mathematics, is what `n8_all_match: false`
records.

**Additional gap:** all 8 R7 n = 8 certificates record `n_classes: 1`
(`runs/RUN-ECRANK-73275e-R7-known-false/raw-result.json`, `results.8.per_b`). All 28 R3
certificates record `n_classes: 3`. The multi-class lift / Galois-eigenvector / "MINUS 1 if any
NONBASE class has certified_e < 2" aggregate machinery (`certify76.py:56–60`) that produced every
counted `aggregate_total` is exercised by **no** control at any n. `EV-ECRANK-8b35bb` `boundaries`
states the same gap for the predecessor: "the multi-class certificate path … was exercised by NO
certified instance anywhere in this experiment — all 58 certificates are single-class".
**The machinery that produced the 28 has never been controlled anywhere in this program.**

## J5(b) — R6, the null object

**Verdict: VACUOUS. Does not discriminate.**
The frozen contract requires (`specification.yaml` `inputs.null_family`) "the n = 6 quadratic with
its constant term sign-forced so no rational in-box solution can exist". By (T2) **there is no
quadratic to sign-force**: A = B = C = 0 on all 64 tuples R6 ran (C-D). `NF.null_constant(0,0,0)`
takes the `A == 0` sentinel branch and returns `Fr(1)` (`null_family.py:50–56`); then
`_quad_rational_roots(0, 0, 1)` returns `[]` at `construct.py:116–118` before any polynomial is
built. The R6 zero is the statement **"1 = 0 has no solution"**, decided by two integer equality
tests, 64 times.

Consequences, each checkable:
- The infeasibility proof frozen in `null_family.py:1–15` and `infeasible_proof` — "A·C_null > 0 and
  B² − 4·A·C_null < 0, so the quadratic has no real root" — is **false of the object that ran**:
  A·C_null = 0 (not > 0) and B² − 4AC_null = 0 (not < 0). The frozen proof describes a family R6
  never instantiated. PD-1 (`null_proof_first: null` in
  `runs/RUN-ECRANK-73275e-R6-null/raw-result.json`) removed the only record that would have shown this.
- R6 never reaches `build_instance`, never reaches the certifier (`_construct` passes
  `certifier=None` when `null_family=True`, `run_experiment.py:134–139`), never applies the r-height
  filter, and never increments a count. Its 37 416 counted ops are spent computing a quadratic that
  is identically zero.
- **Latent unsoundness in the null design**: on the `A == 0, B ≠ 0` branch `null_constant` returns a
  constant for which `_quad_rational_roots` returns the root `−C_null/B` — i.e. the "null" family
  would be *feasible*. C-C shows 6 of the 20 feasible R3 tuples (30%) have A = 0. R6 never met that
  branch only because at d = (1,…,1) B = 0 as well.
- The alternative explanation the prior named is therefore settled: R6's zero is **not** caused by
  `degenerate_deg_s_2` (R6 never calls `build_instance`); it is caused by an identically-zero
  ellipticity condition. Both explanations are equally uninformative about the counted path.

## J5(c) — R8, the planted positive control

**Verdict: NOT RUN, and unfalsifiable twice over.**
Recorded: `n_plants_declared: 9`, `n_plants_built: 0`, all `degenerate_deg_s_2`, `recovered: 0`,
`recovered_denominator: 0`, `log_log_slope: null`, `decade_ratios: {}`
(`runs/RUN-ECRANK-73275e-R8-planted/raw-result.json`). `recovered: []` means the loop at
`run_experiment.py:275–284` never executed a single iteration, so `construct.solve_n6` — the counted
solver — **was never called by the positive control**. The frozen exponent gate [0.699, 1.301] and
per-decade window [5, 20] were never evaluated. `recovered 0/0` is an empty denominator, not a rate.

The doubling matters: even if the 9 plants **had** built, (T2) says the recovery call
`construct.solve_n6(E, b, [1]*6, 10**4)` at `run_experiment.py:279` returns `kept = []` for every b,
because the all-ones pattern has A = B = C = 0. **IV-3 could not have passed under any outcome of
the build step.** A positive control that cannot succeed is not a control.

Two further recording defects, both consequences of the empty set:
- `iv9_distinct_h0: true` is vacuous: `used_h0` is empty and the comparison is `0 == 0`
  (`run_experiment.py:317`). The distinctness clause SR-8/IV-9 was reported PASS on an empty set.
- The h0-collision re-draw guard at `run_experiment.py:255–265` is dead code as written: `h0` is
  `None` for every failed build, `None` never enters `used_h0`, so `if h0 in used_h0` is never true.

## J5(d) — THE DECISIVE TEST: same code path or different?

**Finding: DIFFERENT PATHS.** Stated from committed source, with line references.

The counted R3 result traverses, per b-tuple:

```
construct_arm (construct.py:353)
  S1 sample_b                             construct.py:27
  S2 sample_dpat  (mixed-sign coset pattern)         construct.py:32
  S3 _n6_quad     (derive A,B,C for a general d)     construct.py:98
  S4 _quad_rational_roots                            construct.py:114
  S5 r = g(b_i); r_zero filter; r_height <= H filter  construct.py:80-88
  S6 E.build_instance                                ecrank_engine.py:793
  S7 C.certify_instance, MULTI-CLASS (n_classes = 3) certify76.py:293
  S8 counts_per_H accumulation                       construct.py:401-415
```

Coverage by the three controls:

| stage | R6 null | R7 known-false | R8 planted |
|---|---|---|---|
| S1 `sample_b` | yes | no (own loop, `run_experiment.py:196`) | no (own loop, `:250`) |
| S2 `sample_dpat` | **no** — `dpat = [1]*n` forced (`construct.py:377`) | **no** | **no** |
| S3 `_n6_quad` | **no** — `null_override` bypasses it (`construct.py:70-71`) | **no** — never calls `solve_n6` | **no** — loop never entered |
| S4 `_quad_rational_roots` | yes, but only its `A==0 and B==0 → []` exit | **no** | **no** |
| S5 r-construction / height filter | **no** (no roots) | **no** | **no** |
| S6 `build_instance` | **no** (`certifier=None`, no candidates) | yes — and this is where it is rejected | yes — rejected |
| S7 `certify_instance` multi-class | **no** | single-class only (`n_classes: 1` ×8) | **no** |
| S8 counting | vacuous | **no** | **no** |

**`construct._n6_quad` (construct.py:98–111) — the function that computes the ellipticity quadratic
whose 34 rational roots are the entire content of the R3 result — is executed by NO run in this
package other than R3 and its bit-for-bit replay R4.** Every control routes around it, because
`solve_n6` branches on `all(int(d) == 1 for d in dpat)` (`construct.py:74–75`) and every control uses
d = (1,…,1), which takes the `NF.d1_quadratic_coeffs` branch instead.

The disjointness is also visible in the data, not only the code: R3's coset is
`coset_V: [0, 1, 28, 29, 64, 65, 92, 93]` with observed member values {±22, ±286, ±2310, ±30030} —
**1 is not a member**, and 0 of 28 instances carry an all-ones pattern. R7 selects
`next(c for c in cosets if 1 in [...])` (`run_experiment.py:187–188`). **The counted arm and the
known-false control run over disjoint cosets.**

**The only run that traverses the counted path is R4, and R4 is a determinism control, not a
correctness control.** Under the frozen plan's own `failure_signature` clause (b), this is the
trigger; under `coordinator_prior` item (10) — "a finding that the R3 28 certified instances were
produced by a code path the controls never traverse" — this is the stated overturning finding.

**Honest qualification, so this does not prove too much.** The `degenerate_deg_s_2` *test* at
`ecrank_engine.py:806–808` **is** shared code: R3 executed it 28 times and passed it 28 times
(all `deg_s: 4`). What the controls never traverse is not that line; it is stages S2, S3, S5, the
multi-class S7 and S8, and — decisively — the *condition* deg s = 2 is unreachable from the counted
path, so no control outcome was ever contingent on anything the counted path does. The correct
statement is "the controls and the counted result share one terminal filter and nothing else",
not "the controls ran different code".

---

# J6 — hidden assumptions, omitted cost, scope honesty

**Verdict: BREAKS on (a) and (c); HOLDS WITH MATERIAL CAVEATS on (b).**

## J6(a) — hidden assumptions, numbered

**HA-1 (PD-3, what R5 actually measured).** `implementation.md` IC-732-3 and `construct.py:305`
set `Bbox = min(int(H), 20)` and enumerate **integer** (a, b) in [−Bbox, Bbox]², requiring both
resultants to vanish *exactly at an integer point*. **Corrected statement of what R5 measured:**
*R5 counted the integer points (a, b) ∈ [−20, 20]² at which `Res_c(Q5,Q6)` and `Res_c(Q5,Q7)`
simultaneously vanish, over the first 667 of 10 000 seeded b-tuples, and found none.* It did not
measure the number of rational in-box solutions of the n = 8 ellipticity system. Three separate
gaps, independent of the exhaustion:
  - *Coverage*: 41² = 1681 integer points per tuple against the declared height-H rational box.
    Rationals of height ≤ 100 number 12 175, so 1681/12 175² ≈ **1.1e−5** of the H = 100 domain;
    at H = 1000 it is ≈ **1.1e−9**.
  - *H-collapse*: `min(H, 20) = 20` for **both** declared levels H ∈ {100, 1000}. The two H levels
    were the identical enumeration. The n = 8 arm has no H-dependence to report.
  - *Geometry*: the true solution set of three quadratics in (a, b, c) is generically 8 points of
    algebraic degree up to 8; its (a, b)-projection is the intersection of two plane curves whose
    coordinates are almost never integers. **The enumeration's expected yield is ≈ 0 whatever the
    op budget.** R5's `found: 0` is therefore inert for a second reason beyond PD-2, and both reasons
    were determinable from the contract before the run.

**HA-2 (disclosure not in the record).** `implementation.md` IC-732-3 states the box restriction is
"Recorded in every R5 raw result". It is not. `grep -c "coeff_box_B\|scope_note"` returns **0** in
`runs/RUN-ECRANK-73275e-R5-construct-n8/{raw-result.json,manifest.yaml,stdout.log}` and 0 across the
whole `runs/` tree. The `scope_note` is returned by `solve_n8` in `meta` (`construct.py:341–350`),
and `meta` reaches the record only through a `near_miss_ledger` entry (`construct.py:397–400`) —
which is empty. The single most important scope limitation of the n = 8 arm survives only in
`implementation.md`.

**HA-3 (the near-miss ledger is structurally incomplete).** `specification.yaml`
`metrics.primary.construct_count` requires "the near-miss ledger (tuples with 0 solutions, recorded
with the failing condition)". `construct_arm` appends a near-miss entry only when `kept` is empty
(`construct.py:394–400`), so **per-root rejections on productive tuples are never recorded**. C-C
quantifies the loss on R3: 20 feasible tuples produced **34** candidate rational roots — 14 tuples
with 2 roots, 6 tuples with A = 0 and 1 root — of which 28 were kept, **5 were dropped for
`r_height > 10^4` and 1 for `r_zero`, and none of those 6 appears anywhere in the record**
(`near_miss_total: 0`). The H-dependence of `counts_per_H` is exactly the r-height filter, and the
record contains no data about the objects that filter removed.

**HA-4 (the primary metric's two filters are not implemented).** `metrics.primary.construct_count`
counts "**distinct-minimal-model** certified instances (nonsingular, twist class populated,
**certified rank above trivial**)", and `replication.independent_instances_note` promises
"cross-stream deduplication by minimal model before any count". `construct_arm` applies **neither**:
`found.append(rec)` and `counts[int(H)] += 1` run unconditionally (`construct.py:401–415`); no
minimal-model key is ever computed (`canonical_short_key` / `short_model_from_ainvs` exist in
`ecrank_engine.py` and are never called from `construct.py`); the certificate `verdict` is recorded
and never tested. **"Above trivial" is nowhere defined in the frozen contract.**
*Effect on the recorded number: none.* C-B computes the base-class Jacobian j-invariant for all 28
instances independently and finds **28 distinct j-invariants** (and all 28 verdicts are `PASS`), so
both missing filters would have been no-ops on this output. This is a latent counting defect, not
an actual one — recorded as a NOTE, not a BLOCK, on exactly that ground.

**HA-5 (silent all-ones branch in the counted solver).** `solve_n6` silently substitutes
`NF.d1_quadratic_coeffs` for `_n6_quad` when the pattern is all-ones (`construct.py:74–75`). The
frozen contract nowhere authorises two derivations of "the ellipticity quadratic". The substitution
is invisible in every run record.

**HA-6 (docstring overclaims the n = 8 method).** `construct.py:271–283` states the method runs
"for every rational (a, b) of height <= H with denominator <= H (the coefficient box) … exhaustive
evaluation of the resultants on the box lattice enumerates every in-box intersection", and
`_rational_candidates_univariate` (`construct.py:259–268`) asserts the search is "exact Bézout on
each slice". The correcting comment is 10 lines further down (`construct.py:294–305`). The
overclaiming text is what a reader reaches first.

**HA-7 (`peak_rss_bytes` is not per-run).** All eight runs executed in **one process**: `started_at`
of each run is 2–3 ms after the previous `finished_at` (16:30:07.478387 → 16:32:01.220126,
`manifest.yaml` timing blocks), matching `main()`'s sequential loop at `run_experiment.py:342–364`,
while each `command.txt` records a synthesised `--run R<k>` string built in code
(`run_experiment.py:53, 91, 126, 178, 238`) rather than the invoked command line. `peak_rss_bytes`
comes from `resource.getrusage(RUSAGE_SELF).ru_maxrss` (`run_common.py:85–88`), a **process
high-water mark**. Hence the byte-identical `30867456` in R3, R4, R5, R6, R7 and R8: the three tiny
control runs report R3/R5's peak, not their own.

## J6(b) — omitted end-to-end cost

**`counted_ops` is a LOWER bound on true cost, and no recorded statement uses it in the other
direction — except the stop rule itself.** The counter (`ecrank_engine.py:264–300`) wraps only
Fraction `__add__/__radd__/__sub__/__rsub__/__mul__/__rmul__/__truediv__/__rtruediv__/__pow__/
__rpow__/__floordiv__/__rfloordiv__`, plus `pow` and `isqrt`. It does **not** count Fraction
construction (and hence the gcd normalisation inside it), comparisons, negation, `abs`, integer
arithmetic, or list work. `implementation.md` IC-732-5 itemises the exclusions as "RNG calls,
wall-clock reads, JSON/YAML serialization, and filesystem I/O" — **and omits the two the successor
decision actually named**: `DEC-20260906-7448cf` requires "IC-1 counting-convention exclusions (RNG
calls, **Fraction-constructor gcd reductions, plain integer ops outside counted helpers**) either
counted or **explicitly bounded**". Neither of those two appears in IC-732-5, and nothing is bounded.
The demonstration is in the record: **R1 and R2 report `counted_exact_ops: 0` while consuming
0.324303 s and 0.313583 s** of wall clock. An op ledger that reports zero for a run that did
measurable work is not a cost measure; it is a Fraction-operation tally, and each tally unit has an
operand-size-dependent cost (R3 records `height_s` up to 19 604 200 and 38-digit `disc_s`).

**The exact-boolean cap flag is a tautology at the stop point.** `ops_cap_respected` is computed
after the run as `counted_ops < 1.0e8` (`run_common.py:172`), while the stop rule breaks at
`ops_count() >= OPS_CAP` (`construct.py:308, 370`). Any run that the stop rule fires on therefore
*necessarily* records `false`. R5's `ops_cap_respected: false` at `counted_ops: 100002120` means
"the stop rule worked, with a 2 120-op overshoot", not "the budget was violated". SR-9's exactness
is satisfied; its *diagnostic value* at the cap is nil. This is a fairness point in the executor's
favour and the Coordinator should not read `false` as a breach.

**The 1.0e8 cap and the declared 10^4 n = 8 sample are mutually inconsistent, and were before the
run.** R5 consumed 100 002 120 counted ops over 667 tuples = 149 928 ops/tuple; completing the
declared 10 000-tuple sample needs ≈ **1.50e9 counted ops = 15.0× the frozen per-run cap**, at
≈ 1135 s wall — comfortably inside the 7200 s per-run wall budget. **The binding constraint was the
op cap, not time, and the frozen contract's own numbers made the n = 8 arm unreachable at design
time.** (Extrapolated linearly from the tested 667 tuples; `Bbox` is fixed at 20 for both H levels,
so per-tuple cost is near-uniform.)

**Wall-clock instrumentation.** `wall_seconds_monotonic = time.monotonic() − t_mono` and
`wall_seconds_timestamp_span = time.time() − started_unix` (`run_common.py:130–131`) are two
*different system clocks* measuring the *same interval*, sampled one statement apart at each end.
**Correction to the frozen prior**: they are not identical in every run — R4 records
18.257394 / 18.257395 and R5 records 75.686747 / 75.686748, differing by exactly 1e−6; the other six
agree to 6 dp. The substantive point survives and is stronger than "one instrument twice": their
agreement measures the gap between two adjacent statements, not any uncertainty in the cost, so
SR-10 is **literally satisfied and purposively empty**. `DEC-20260906-7448cf`'s stated purpose for
SR-10 — "so the cost model is never quoted smaller than reality (total elapsed ~114.9 s versus
99.559 s reported)" — *is* met here: Σ per-run wall = 113.720816 s against 113.741739 s R1-start to
R8-finish, a 0.020923 s gap. **The load-bearing missing quantity is CPU time**, and
`cpu_seconds: null` in all eight runs by explicit design (`run_common.py:165–166`). Combined with
HA-7, the package's resource profile is: no CPU measure, a non-per-run memory measure, a
29–31 MB peak against a declared 8 GB envelope (a ~260× margin that constrains nothing), and an op
ledger that is a lower bound of unbounded looseness.

## J6(c) — scope honesty

**The producer's own language is clean.** `execution-report.yaml` sets `interpretation: none`,
declines to map facts to the success criterion, and a scan of `execution-report.yaml`, `runs/` and
`implementation.md` for `HEUR-1 | supports | confirms | demonstrat | validates | proves |
cryptograph | rank over | C1` returns exactly one hit: `implementation.md:6`, "no HEUR-1 verdict".
**No run record or executor statement reads beyond the tested scope.** The scope problems below are
in the frozen contract and in one summary field, upstream of or beside the executor.

**SO-1 (BLOCK) — the P4 comparison compares a measurement at n = 6 against a bound at n = 8, and the
same-n comparison does not separate the routes.** `specification.yaml` `metrics.secondary` reads
"measured incidence vs the **3e-4/draw** draw-route upper bound of EV-ECRANK-8b35bb", and P4 requires
"incidence > 3e-4 per tuple at the same per-tuple scale". The cited record says something else:
`EV-ECRANK-8b35bb` `obstruction.value` states "rule-of-three 95% upper bound **< 3e-4 instances per
b-tuple at n=8 (3/10^4)**". So:
  - **Unit error in the frozen contract**: 3e-4 is *per b-tuple*, not per draw. The per-draw figure
    from the same record (0 of 80 000 draws) is **3.75e-5**. The contract mislabels its own citation.
  - **The unstated assumption, named**: that the per-b-tuple certified-instance rate is comparable
    **across n** (n = 8 → n = 6) **and across route** (random draw → prescribed construction), i.e.
    that the b-tuple is the right common denominator and that n does not move the rate.
  - **The predecessor's own record contradicts the first half.** `EV-ECRANK-8b35bb` `observations`:
    "arm A (n=6, seed 760706) 1,000 seeded b-tuples … 0 constructed instances". The same-n
    rule-of-three 95% upper bound is **3/10^3 = 3.0e−3 per tuple**. R3's measured incidence is
    28/10^4 = **2.8e−3** per tuple (or 20/10^4 = 2.0e−3 feasible tuples). **At the same n and the
    same unit, the construction route's incidence sits below the draw route's own 95% upper bound.**
    The apparent 10× separation in P4 comes entirely from swapping n = 6 for n = 8 in the denominator.

**SO-2 (BLOCK) — the count does not move when the parameter that should move it is applied.**
`specification.yaml` `tail_checks` fixes the expectation: "The smallest and largest H-decade ratios
of N_6 are reported against the exponent +2 prediction (**factor 100 per decade**)". Observed
`counts_per_H: {100: 15, 1000: 22, 10000: 28}` gives decade ratios **1.467 and 1.273**. The count is
essentially flat in H over two decades where the frozen prediction is ×100 per decade. C-C explains
why mechanically: 9 980 of 10 000 tuples produced **no rational root at all** (`near_miss_total: 0`
means no tuple had roots that were all rejected), so the count is governed by how often
`disc = B² − 4AC` is a rational square — a quantity **independent of H** — and H enters only through
5 height rejections out of 34 roots. Under `docs/inventor-protocol.md` §3 this is the canonical
artifact-tell shape read in the informative direction: **the 28 is not an H-driven count and must
not be reported as N_6(H) with a decade law.** The required tail-check report of the decade ratios
against the +2 prediction is absent from `execution-report.yaml`.

**SO-3 (NOTE) — one summary field garbles the coverage state.** `execution-report.yaml`, R3
`iv8_untested_statement`: "*(single-class coverage count: 28 instances, all 3-class)*". Labelling
3-class instances as "single-class coverage" inverts the very state IV-8 exists to carry forward.
It understates rather than overstates — but the true state is materially new and should be recorded
as such: `EV-ECRANK-8b35bb` `boundaries` records that in the predecessor **all 58 certificates were
single-class**, whereas here **28 of 28 are 3-class**. The multi-class certification path is being
exercised in this program for the first time, and it is exercised with no control (J5(a)).

---

# J7 — the cheapest falsification control this result admits

**Verdict: HOLDS (the ranked list exists, three items are computable from committed bytes, and I ran
three of them).** Priced in analyst-minutes plus machine-seconds on the committed snapshot.

| rank | artifact | computable from committed bytes? | cost | ran? |
|---|---|---|---|---|
| **1** | **C-D: recompute (A, B, C) of the all-ones n = 6 ellipticity quadratic** | **yes** | ~10 min, **<1 s** | **YES** |
| **2** | **C-A: recompute deg(g² − p) for the d=(1..1) Mestre object** | **yes** | ~15 min, **~8 s** | **YES** |
| **3** | **C-B/C-C: re-verify the 28 R3 instances + root-fate audit + j-invariant dedup** | **yes** | ~45 min, **~4 s** | **YES** |
| 4 | plant one R3-shaped 3-class instance into the R7 path and one all-ones object into the R3 path (plan item iii) | **no** — requires executing `certify_instance` and `build_instance` | new run, ~1 min | no — this is an arm |
| 5 | re-derive the predecessor n = 6 arm at 10^4 tuples to make SO-1 a same-n comparison | no — requires the predecessor arm | new run, ~1 h | no |

**Why the plan's own item (i) is not rank 1, and what a successor needs.** Plan item (i) asks to
"re-verify the exhibited points of one recorded R3 instance against its Weierstrass equation … and
check non-torsion by Mazur". **That cannot be done from the committed bytes**: `construct_arm`
records only `{verdict, aggregate_total, n_classes, class_keys}` per instance
(`construct.py:406–411`). **No a-invariants and no curve points are in any R3 artifact.** Under
`docs/claims-and-verification.md` the R3 record therefore carries **no re-verifiable solution
certificate** — it carries the raw ingredients (b, d_pattern, r, s) from which one can rebuild the
identity chain, which is what I did, but not the Weierstrass model or its points.
**What a successor task would need, exactly**: for each counted instance, persist per class d the
integral a-invariants `ainv_d` and the exhibited image points `imgs` already computed inside
`certify_instance` (`certify76.py:376–392`), plus `cert["certified_rank_lower_bound"]` and the Mazur
witnesses. That is a ~6-line change to the `rec["certificate"]` dict in `construct.py:406–411` and
turns rank 1 into an independently re-verifiable certificate under the `Refutation artifacts` clause.

**What I ran, and the outcomes.**

**C-B — full independent re-verification of all 28 R3 instances. Result: NO COUNTEREXAMPLE. 28/28
pass every check.** From `runs/RUN-ECRANK-73275e-R3-construct-n6/raw-result.json` `found`, with my
own Lagrange interpolation, polynomial reduction, Sylvester-resultant discriminant and quartic
invariants:

| check | 28/28 |
|---|---|
| ellipticity — all coefficients of degree ≥ 5 of interp(b_i, d_i·r_i²) vanish | ✔ |
| the recorded `s` is reproduced exactly | ✔ |
| `deg s ∈ {3, 4}` (all 4) | ✔ |
| every r_i ≠ 0 | ✔ |
| disc(s) ≠ 0 **and equal to the recorded `disc_s`** | ✔ |
| forcing identity s(b_i) = d_i·r_i² | ✔ |
| M2 identity δ·g² ≡ s (mod ∏(x−b_i)) | ✔ |
| recorded `r_height` reproduced | ✔ |
| base-class points (b_i, r_i) lie on v² = (s/d1)(u) | ✔ |
| base class carries exactly 2 rational points | ✔ |

Also recomputed from the recorded r-heights alone: **counts_per_H = {100: 15, 1000: 22,
10000: 28}**, matching the record exactly. Dedup audit: **28 distinct base-class j-invariants**
(0 collisions), so HA-4's missing minimal-model filter would have been a no-op; the 84 class-curves
collapse to 28 distinct j-values exactly as quadratic twists must, which is the designed structure,
not an anomaly. **Basis: derivation from committed bytes (exact `Fraction`), not `empirical_only`.**

**C-C — root-fate audit.** Rebuilt the ellipticity quadratic for each of the 20 feasible tuples from
its recorded (b, d_pattern): 14 tuples with 2 rational roots, 6 with A = 0 and 1 root, 34 candidates
total → **28 kept, 5 rejected `r_height > 10^4`, 1 rejected `r_zero`, 0 unexplained**. My independent
reconstruction reproduces the recorded instance set exactly, root by root, including which roots were
dropped and why — none of which the record contains (HA-3).

**C-A and C-D** are reported in J5 above; both are BLOCK-supporting and both are cheap enough to be
re-run by the Coordinator in under 10 seconds.

**Net J7 statement.** The cheapest falsification of the *reading* of the 28 is not an attack on the
28 — I attacked it three ways and it held. It is **C-D**: ten minutes of exact arithmetic showing
that the object all three controls were built on has an identically-zero ellipticity condition, which
falsifies the reading that any control constrains the 28.

---

# Proves-too-much control

Run against all three frozen objects. Failure signature per
`ledger/decisions/DEC-20260907-9953c0.yaml` `proves_too_much.failure_signature`.

### Object 1 — the all-ones Mestre degeneration at n = 6 and n = 8, closed form n − 1

- **Does the argument go through where it is false?** **No.** The pipeline reports no certified
  instance **above** n − 1 on this family: n = 8 totals are [5, 6, 7, 7, 7, 7, 6, 7], max 7 = n − 1,
  0 of 8 above; n = 6 built nothing. Failure-signature clause **(a) does NOT trigger**.
- **Could the control have failed?** **At n = 8, yes, and it did not fail in the direction that
  tests soundness.** **At n = 6, no** — (T1) makes rejection certain for every b-tuple and seed.
- **Was it evaluated?** n = 8 yes (8 objects built and certified); n = 6 no object was ever presented
  to the certifier.
- **Note for the record**: R3's n = 6 instances carry `aggregate_total` 2 (×15) and 6 (×13), and 6
  exceeds 5 = n − 1. That is **not** a clause-(a) trigger: those are multi-class certificates over the
  degree-8 field K_V on a *different* coset (member values {±22, ±286, ±2310, ±30030}, 1 absent),
  not members of the all-ones family, and n − 1 is a closed form for the all-ones family only.

### Object 2 — the sign-forced R6 null family

- **Does the argument go through where it is false?** **No.** `found: []` exactly;
  `feasible_tuples: 0`. Failure-signature clause (a) second limb **does NOT trigger**.
- **Could the control have failed?** **No.** By (T2), (A, B, C) = (0, 0, 0) on all 64 tuples (C-D),
  `null_constant` returns 1, `_quad_rational_roots(0, 0, 1)` returns `[]` at two integer comparisons.
  The frozen object — "the n = 6 quadratic with its constant term sign-forced" — was never
  instantiated, and the infeasibility proof frozen in `null_family.py` is false of what ran
  (A·C_null = 0, disc = 0). The contract's second requirement, "the audit code must flag the
  infeasibility", is unmet in the record (`null_proof_first: null`, PD-1).
- **Was it evaluated?** The solver returned 0. Nothing downstream of `_quad_rational_roots` ran.

### Object 3 — the `degenerate_deg_s_2` rejection treated as a null object

- **Does the argument go through where it is false?** Not applicable in clause-(a) form; this object
  tests clause (b) directly.
- **Could the control have failed?** **No.** Clause (b) — "the controls' zeros are produced by a
  rejection path that the counted R3 path never traverses, so no control could have failed whatever
  the counted path did" — **TRIGGERS**, with the precision recorded in J5(d): the rejection *test*
  (`ecrank_engine.py:806–808`) is shared and the counted path passed it 28/28, but the *condition*
  deg s = 2 is unreachable from the counted path, and stages S2, S3, S5, multi-class S7 and S8 are
  traversed by no control at all.
- **Was it evaluated?** Yes, as a rejection, 8 times in R7 (n = 6) and 9 times in R8 — every time on
  an object the counted path cannot produce.

### Clause (c)

**TRIGGERS.** "The IV-3 planted family produced no plants at all, so the positive control never
evaluated": 0 of 9 built, `recovered: []`, exponent gate never reached — and by (T2) the recovery
solver would have returned `[]` even had every plant built.

### Consequence, as the frozen plan states it

Clauses **(b) and (c) both hold**, so under the plan's own text this round "FAILS as a review of the
counted result, regardless of the value 28 and regardless of every other joint verdict". **That is a
statement about the review's coverage, not about the 28's arithmetic.** Both halves are true and must
travel together: the 28 are independently re-verified (C-B, C-C) *and* uncontrolled.

### Does this reading also invalidate the predecessor EXP-ECRANK-76a70d?

**No, and here is exactly what distinguishes them.** My reading rests on two theorems tied to
n = 6 and to the all-ones pattern:
1. **(T1) is n-specific**: deg(g² − p) ≤ n/2 − 1 fails the {3,4} filter only at n = 6. The
   predecessor's known-false control ran at **n = 8 and n = 10** — `EV-ECRANK-8b35bb`
   `certificate_refs` lists `kf-n8-b00..b19` and `kf-n10-b00..b19`, **no `kf-n6-*`** — where
   deg s ≤ 3 and ≤ 4 respectively and objects build. Its 40 known-false and 18 planted certificates
   are all `verdict: PASS`, and its planted control recovered **1161/1161** with a log-log slope of
   0.905 inside the frozen window. **A control that recovers 1161 of 1161 plants plainly discriminated.**
2. **(T2) is pattern-and-route-specific**: it says the *construction* solver `solve_n6` is trivial at
   d = (1,…,1). The predecessor used the **draw route**, not `construct.solve_n6`, which did not
   exist there. (T2) cannot reach it.

The condition under which my reading *would* transfer is stated so it can be checked rather than
assumed: **if** the predecessor's controls were also built on an object its counted path cannot
produce, the same objection applies there. I did not test that — `experiments/EXP-ECRANK-76a70d/` is
outside my enumerated `read_scope` and I did not open it. A successor with that path in scope should
check it; the evidence I *can* see (1161/1161 plant recovery on the counted path) points the other
way. **A reading that killed the predecessor too would be defective, and this one does not.**

---

# BLOCK items, each with a worked falsification route

An objection I cannot make checkable is filed as a NOTE, not a BLOCK.

### BLOCK-1 — IV-1 at n = 6 is unsatisfiable as frozen; its recorded "failure" carries no information
*Evidence*: `specification.yaml` controls IV-1; `execution-report.yaml` R7 `n6_per_b_built: false`,
`n6_reason_all_eight: degenerate_deg_s_2`; `ecrank_engine.py:380–391, 394–405, 806–808`.
*Falsification route*: exhibit **one** b-tuple with b1 = 0, b2 = 1, b3..b6 distinct in
[−20,20]\{0,1} for which `s = g² − p` from the monic truncated square root has degree 3 or 4. Recipe:
compute p = ∏(x − b_i); find the monic degree-3 g with deg(p − g²) ≤ 2 (unique — verify the property
on your g and the algorithm is irrelevant); report deg(g² − p). My run: **deg = 2 on all 9 recorded
R8 tuples, all 8 re-derived R7 tuples, and 2999/3000 random tuples (the remaining one is deg 0);
never 3 or 4**. Producing a single counterexample refutes BLOCK-1.

### BLOCK-2 — IV-1 at n = 8 tests completeness of a lower bound, not soundness; the soundness half passed
*Evidence*: `certify76.py:56–60` ("Claim: rank E0'(K_V) >= aggregate_total") and
`certify76.py` `certified = cert["certified_rank_lower_bound"]`; R7 raw
`n8_aggregate_totals: [5,6,7,7,7,7,6,7]`; `EV-ECRANK-8b35bb` observations ("`total = n` occurred ZERO
times over 40 seeded instances … never exceeding n−1").
*Falsification route*: show that `aggregate_total` is a two-sided quantity — i.e. exhibit a
documented guarantee in the certifier that it returns the **exact** rank rather than a lower bound.
If such a guarantee exists, totals of 5 and 6 are genuine failures and BLOCK-2 falls. I found the
opposite text in the module's own docstring.

### BLOCK-3 — the R6 null object is vacuous and its frozen infeasibility proof is false of what ran
*Evidence*: `null_family.py:20–47, 50–56, 74–89`; `construct.py:74–75, 114–124, 377–387`;
`runs/RUN-ECRANK-73275e-R6-null/raw-result.json` (`found: []`, `null_proof_first: null`).
*Falsification route*: exhibit **one** b-tuple at n = 6 for which the all-ones ellipticity quadratic
has (A, B, C) ≠ (0, 0, 0). Recipe: δ = interp(b, (1,…,1)); for t ∈ {0, 1, −1} compute the x^5
coefficient of (δ·(x+t)²) mod ∏(x−b_i); interpolate. My run: **(0, 0, 0) on all 64 R6 tuples**, and
the reason is a one-line theorem (δ ≡ 1 ⇒ s = (x+t)², degree 2, so the x^5 coefficient vanishes
identically), so no counterexample exists. To falsify the *report* instead, show the R6 run record
contains any trace that the null family degenerated — `grep` for the infeasibility proof in the run
directory returns nothing.

### BLOCK-4 — IV-3 was not run and could not have passed
*Evidence*: `runs/RUN-ECRANK-73275e-R8-planted/raw-result.json` (`recovered: []`, `cells` all 0,
`log_log_slope: null`, `decade_ratios: {}`); `run_experiment.py:275–284, 317`.
*Falsification route*: exhibit a b-tuple for which `construct.solve_n6(E, b, [1]*6, 10**4)` returns a
non-empty `kept`. By BLOCK-3's theorem the quadratic is identically zero and
`_quad_rational_roots(0, 0, ·)` returns `[]` (`construct.py:116–118`), so any non-empty return
refutes BLOCK-4. Separately, `iv9_distinct_h0: true` is `0 == 0`; refute by exhibiting a non-empty
`used_h0` in the record.

### BLOCK-5 — the counted path S2, S3, S5, multi-class S7 and S8 are covered by no control
*Evidence*: the stage table in J5(d), with `construct.py:32, 70–75, 80–95, 98–111, 377, 401–415`,
`run_experiment.py:134–139, 187–199, 250–284`; R3 `coset_V: [0,1,28,29,64,65,92,93]` with member
values {±22, ±286, ±2310, ±30030} and 1 absent; all 28 R3 certificates `n_classes: 3` vs all 8 R7
certificates `n_classes: 1`.
*Falsification route*: exhibit any run in this package, other than R3 and its replay R4, whose
execution reaches `construct._n6_quad` or reaches `certify76.certify_instance` with more than one
class. Mechanically: add a call counter to `_n6_quad` and to the `classes` branch of
`certify_instance` and re-run R6, R7, R8 — expected counts 0 and 0. This is a successor run, not a
re-score of an executed run.

### BLOCK-6 — R5 did not measure the quantity the frozen contract defines, independently of PD-2
*Evidence*: `construct.py:294–305` (`Bbox = min(int(H), 20)`), `implementation.md` IC-732-3;
R5 raw `found: 0`, `near_miss_total: 0`, `exhaustion: {kind: counted_ops_cap, b_index: 666}`.
*Falsification route*: show that the declared height-H rational coefficient box coincides with the
enumerated integer box at either declared H. It does not: 1681 integer points against 12 175²
rationals of height ≤ 100 (≈1.1e−5) and ≈1.5e12 at H = 1000 (≈1.1e−9), and `min(H,20) = 20` makes the
two declared H levels the identical enumeration. Refute by exhibiting a rational, non-integer (a, b)
solution the enumeration would have found.

### BLOCK-7 — the P4 cross-experiment comparison does not separate the routes at fixed n
*Evidence*: `specification.yaml` `metrics.secondary` ("the 3e-4/draw draw-route upper bound") and
`preregistered_prediction.formula` P4; `EV-ECRANK-8b35bb` `obstruction.value` ("< 3e-4 instances per
b-tuple at n=8 (3/10^4)") and `observations` ("arm A (n=6 …) 1,000 seeded b-tuples … 0 constructed
instances"); R3 `found: 28` of `n_b_declared: 10000`.
*Falsification route*: run the predecessor's n = 6 draw arm at 10^4 b-tuples. If it still yields 0,
its per-tuple 95% upper bound falls to 3.0e−4 and 2.8e−3 separates from it by ~9×, and BLOCK-7 falls.
At the recorded 10^3 tuples the bound is 3.0e−3 and 2.8e−3 does not separate. **This is the single
cheapest experiment that would convert P4 from an artefact of changing n into a real comparison.**

### BLOCK-8 — the n = 8 arm's only scope disclosure exists in no run artifact
*Evidence*: `implementation.md` IC-732-3 "Recorded in every R5 raw result"; `grep -c
"coeff_box_B\|scope_note"` = 0 in R5 `raw-result.json`, `manifest.yaml`, `stdout.log`, and 0 across
`runs/`; `construct.py:341–350` returns it in `meta`, `construct.py:394–400` records `meta` only via
a `near_miss_ledger` entry, and `near_miss_total: 0`.
*Falsification route*: exhibit the string in any committed run artifact. One `grep` settles it.

## NOTES (checkable, not BLOCK)

- **N-1** HA-4: the minimal-model dedup and the "certified rank above trivial" filter are absent from
  the counting code, but C-B shows 28 distinct j-invariants and 28 `PASS` verdicts, so the recorded
  number is unaffected. Latent, not actual.
- **N-2** HA-3 / C-C: 6 candidate roots (5 height, 1 r_zero) are absent from the required near-miss
  ledger; the ledger's trigger condition cannot record per-root rejections on productive tuples.
- **N-3** HA-7: `peak_rss_bytes` is a process high-water mark reported per run; six runs share the
  byte-identical value 30867456. `command.txt` is synthesised from `argv` in code, not the invoked
  command line. Handed to the Coordinator; run-record integrity is J1, not mine.
- **N-4** HA-5, HA-6: the silent all-ones branch in `solve_n6` and the overclaiming `solve_n8`
  docstring.
- **N-5** SO-3: the `iv8_untested_statement` labels 3-class instances as "single-class coverage".
- **N-6** SR-11 as discharged ("exclusions reported") is weaker than `DEC-20260906-7448cf` requires
  ("counted or explicitly bounded"), and IC-732-5 omits the two exclusions that decision named.

---

# Whether I overturned the priors

| prior | outcome |
|---|---|
| (4) "IV-1 as frozen is NOT satisfied" | **REFINED, and its recommended reading rejected.** Literally unsatisfied, but for two reasons that carry no information about the counted path: unsatisfiable by construction at n = 6 (T1), and a completeness test on a one-sided bound at n = 8, whose soundness direction **passed** (0 of 8 above n − 1). Reading "the run set is invalid" from IV-1 would over-read it. |
| (5) "IV-3 did not discriminate" | **CONFIRMED and strengthened** to NOT RUN and *could not have passed* (T2). |
| (6) "the R6 zero is weaker than it looks" | **CONFIRMED and strengthened.** Not merely weak — vacuous: A = B = C = 0 on all 64 tuples, the solver returns before constructing anything, and the frozen infeasibility proof is false of the object that ran. Also **corrected**: the prior's live alternative — that `degenerate_deg_s_2` explains the empty R6 — is **wrong**; R6 never calls `build_instance`. |
| (7) "PD-3 is material" | **CONFIRMED and quantified** (1.1e−5 / 1.1e−9 coverage; `min(H,20)` collapses both H levels; the geometry makes the yield ≈ 0 whatever the budget). |
| (9) "one cost-model gap; `wall_seconds_*` identical in every one of the eight runs" | **PARTIALLY OVERTURNED on the premise, confirmed on the substance.** R4 (18.257394/18.257395) and R5 (75.686747/75.686748) differ by 1e−6; six of eight agree. They are two clocks over one interval; SR-10 is literally satisfied and purposively empty; the real gap is `cpu_seconds: null` ×8 plus a non-per-run RSS plus `counted_ops: 0` on two runs that did work. |
| (10) "what would overturn the prior as a whole: the 28 produced by a code path the controls never traverse" | **FOUND. The prior's own overturning condition holds** — see J5(d) and BLOCK-5. |
| the symmetric trap ("`degenerate_deg_s_2` may be the control passing") | **BOTH HORNS ARE TRUE.** The filter behaved correctly on a genuinely degenerate object **and** the control is uninformative, because the outcome was fixed by degree arithmetic before any seed was drawn. |
| second prior (`coordinator-prior-20260907T174252Z.md`), "a reading that proves too much about the predecessor is defective" | **Honoured.** My reading rests on two n-and-pattern-specific theorems that cannot reach the predecessor's n = 8/n = 10 known-false control or its 1161/1161 draw-route plant recovery. |

# Narrowest supported statement

*Scoped to n ∈ {6, 8}, H ≤ 10^4 / 10^3, the seeded 10^4 b-tuple sample, exact `Fraction` arithmetic,
the 1.0e8 counted-op cap, and toy tier:*

> The 28 objects recorded by RUN-ECRANK-73275e-R3 are, on independent recomputation from the
> committed bytes, 28 structurally valid and pairwise non-isomorphic n = 6 prescribed-square
> instances: each satisfies ellipticity, deg s = 4, nonsingularity, the forcing identity and the M2
> identity exactly, all 28 base-class j-invariants are distinct, and `counts_per_H = {15, 22, 28}`
> reproduces from the recorded r-heights. **No control in this package constrains them**: R6 is
> vacuous, R7's n = 6 half is unsatisfiable and its n = 8 half is single-class and only tests a bound
> the counted path does not use, R8 never ran, and no control traverses the ellipticity-quadratic
> solve or the multi-class certification that produced every counted value. The number 28 is **not**
> an H-driven count (decade ratios 1.47 and 1.27 against a frozen ×100 prediction) and, at fixed
> n = 6 and the same per-tuple unit, it does not separate from the predecessor draw route's own 95%
> upper bound (2.8e−3 vs 3.0e−3). Nothing here supports or refutes HEUR-1, moves H-ECRANK-36d8d7,
> touches C1, or extends beyond the tested scope.

# One next concrete action

**Design (do not yet approve) a controls-repair amendment to EXP-ECRANK-73275e whose single required
property is that every control object be drawn from the same coset and the same mixed-sign
multi-class d-pattern distribution as the counted arm** — i.e. replace the all-ones family, which
(T1) and (T2) render inert at n = 6, with a *plant built by the counted path itself*: take a
recorded R3 instance, perturb one r_i so the ellipticity condition is provably violated (negative
control) and re-inject an unperturbed one (positive control), and require the record to persist
`ainv_d` and the exhibited points per class so plan item J7(i) becomes computable. The one experiment
to queue beside it is **BLOCK-7's**: the predecessor n = 6 draw arm at 10^4 b-tuples, which is the
cheapest artifact that would make the P4 comparison mean anything.
