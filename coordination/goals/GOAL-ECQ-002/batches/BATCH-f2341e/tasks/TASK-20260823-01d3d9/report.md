# TASK-20260823-01d3d9 — family-agnostic specialise → certify → measure pipeline

Executor report. **Observations only**; no hypothesis is declared supported or
refuted here, and nothing was submitted to the ICARM endpoint.

- goal `GOAL-ECQ-002`, batch `BATCH-f2341e`, hypothesis `H-ECQ-d60d07`
- base commit `446ba7331` (working tree dirty with this task's own artifacts only)
- requested policy `executor-implementation`; the model that answered is recorded
  in each run's `environment.json` (`claude-opus-5`, `model_verified: false` — no
  `adapter doctor --probe` was run in this session). No fallback, no degraded
  requirement.
- budget 3600 s / 4 GB / 80 runs. Used: 10 run records, peak RSS 1.66 GB
  (RUN-ECQPIPE-01d3d9-006), aggregate child wall clock ≈ 1.6 ks.

Artifacts: `pipeline_validation.json` (every number below, machine-readable),
`pipeline/` (source + `README.md` documenting the entry point),
`runs/RUN-ECQPIPE-01d3d9-001 … -010` (immutable run records), `results/` (raw
producer outputs, copied into each run record as `raw-result.json`).

---

## 0. What the pipeline is, and what certifies what

`pipeline/pipeline.py` takes **any** Q(t) family as a JSON spec plus a parameter
box and runs: specialise (exact `Fraction`) → order by Mestre-Nagao → PARI
`ellrank` to *find* candidate points → **exact certification** → minimal model,
naive height, Faltings height, conductor → ICARM-format record. No family is
hard-coded; the base family from TASK-20260823-d1cb76 is passed with `--family`.

The rank number never comes from PARI. It comes from `pipeline/exact_certify.py`,
which is stdlib-only (`fractions`, `math`), treats the points as data, and proves
a lower bound in exact arithmetic:

1. each point is verified on the curve over Q in `Fraction` arithmetic;
2. non-torsion is checked directly against Mazur's theorem (orders 1–10, 12);
3. `#E(Q)_tors` is bounded exactly by `gcd_p #E(F_p)` over odd good primes
   (reduction is injective on torsion), `#E(F_p)` counted naively;
4. independence: for a prime ℓ coprime to that torsion bound and good primes p
   with ℓ | #E(F_p), the map ψ_p(X) = (#E(F_p)/ℓ)·X kills ℓE(F_p) and kills the
   reduction of E(Q)_tors, so a set of points whose stacked images
   ⊕_p ψ_p(P̄_i) ∈ ⊕_p E(F_p)[ℓ] have F_ℓ-rank k admits **no** primitive
   Z-relation modulo torsion: rank E(Q) ≥ k.

No floating point, no analytic rank, no `ellrank` `r_high`, no Selmer bound
enters that chain. The numerical height regulator is computed only to fill the
ICARM record's `regulator` field and is labelled `regulator_is_numerical: true`.

**Certifier negative controls** (RUN-ECQPIPE-01d3d9-001, run *before* any
certifier output was used): P and 2P on 37a1 → certifies 1, not 2; P, Q, P+Q on
389a1 → certifies 2, not 3; the true generators of 389a1 → 2; an off-curve point
→ rejected as off-curve; the 5-torsion point (5,5) on 11a1 → rejected as torsion.
All five pass.

---

## 1. CHECK 1 — reproduction against the frozen ICARM snapshot (the gate)

`RUN-ECQPIPE-01d3d9-004`: all **289** curves of the frozen snapshot
(`icarm_database_20260823.json`, declared sha256 `118db069…cadc59`), recomputed
from a-invariants alone, 210 s.

| metric | ours vs theirs | worst disagreement |
| --- | --- | --- |
| rank (re-certified from the board's own points, exact) | **289 / 289 agree** | none |
| naive height | **289 / 289** | max abs diff 2.8e-14 |
| Faltings height | **289 / 289** | max abs diff 1.8e-15 |
| minimal discriminant | **289 / 289** | none |
| curve_key (c4:c6) | **289 / 289** | none |
| conductor | **280 / 281 computed** | curve #288, see below |

The definitions that reproduce the board exactly — this is the gate, since a
wrong height convention would void every later comparison:

- `naive_height = log max(|c4|³, c6²)` of the **minimal** model;
- `faltings_height = −½·log A`, A = |Im(conj(ω1)·ω2)| the covolume of the period
  lattice of the minimal model. **The board's convention carries no
  (1/12)·log|Δ| term**: on curve 42 the alternatives (1/12)log|Δ| − ½log A and
  −log A miss the recorded value by 0.30 and 0.70 respectively, so the
  convention is pinned by measurement, not guessed;
- `conductor = ellglobalred(E)[1]`.

The two curves named in the handoff:

| curve | board rank → ours | board naive h → ours | board Faltings h → ours | conductor |
| --- | --- | --- | --- | --- |
| #244 `[0,0,0,-44788551847,2462203786988170]` | 14 → **14** | 85.18925824647027 → identical | 5.131289175169005 → identical | agrees |
| #276 (rank-15 incumbent) | 15 → **15** | 118.77017663505484 → identical | 7.821848213987553 → identical | agrees |

Also re-certified: #273, the rank-30 record curve, 30 → **30** exactly (ℓ = 2,
44 primes) after the certifier escalated its prime bound; its first pass reached
29, which is a search-bound limitation of the certifier and is recorded as such,
never as a statement about the curve. Six curves needed that escalation
(#273, #12, #11, #10, #168, #35).

Two exceptions, recorded rather than smoothed over:

- **#288** is the only `conductor_agrees: false`. The board stores **no**
  conductor for it (`null`); we computed one (full value in
  `pipeline_validation.json`). A gap on their side, not a numerical
  disagreement — every other field of #288 matches exactly.
- **8 curves** (#9, #10, #11, #12, #66, #67, #199, #289) exceeded the 15 s
  `ellglobalred` guard in the first pass — an infrastructure outcome (the
  conductor needs the factorisation of a very large discriminant), never a
  mathematical result. They are excluded from the 281 denominator and were
  retried with a 130 s guard in `RUN-ECQPIPE-01d3d9-010`; see
  `check_1_reproduction.conductor_retry` in `pipeline_validation.json`.

**Gate verdict: passed.** Rank certification, both height definitions,
discriminant and conductor reproduce the board on all 289 curves, with the two
exceptions above stated explicitly.

---

## 2. CHECK 2 — the cheap falsifier: height vs parameter size

`RUN-ECQPIPE-01d3d9-005`. The operationalisation was fixed in
`falsifier_height.py` before the numbers were read: measure X = log H(t)
(H = max(|num|, den) of the parameter) against Y = naive height of the minimal
model of the specialisation, over t = p/q with |p| ≤ 30, q ≤ 3 (~130 points per
family), and fit Y = a + b·X by least squares.

The families are **internal demo objects built in this task** (prescribe n
sections with polynomial coordinates in t, solve the resulting linear system for
the a-invariants over Q(t)). They are not the campaign base family and carry no
citation.

| family | claimed generic rank | n | min h | median h | fit | R² |
| --- | --- | --- | --- | --- | --- | --- |
| DEMO-NULL-r0 (y²=x³+t) | 0 | 130 | 10.75 | 23.16 | h = 17.97 + 2.14·log H | 0.11 |
| DEMO-SEC1-r1 | 1 | 129 | 12.95 | 30.40 | h = 15.29 + 5.59·log H | 0.43 |
| DEMO-SEC3-r3 | 3 | 129 | 17.53 | 65.12 | h = 8.70 + 21.19·log H | 0.78 |
| DEMO-SEC5-r5 | 5 | 131 | 11.39 | 189.78 | h = 5.56 + 67.37·log H | 0.94 |
| DEMO-SEC5-BIGCOEFF | 5 | 131 | 120.58 | 776.24 | h = 506.63 + 102.66·log H | 0.67 |

**Verdict, plainly: the mechanism survived its own falsification condition — and
the same check produced the number that decides whether it is usable.**

- H-ECQ-d60d07 declares the mechanism falsified if "minimal models of
  small-parameter specialisations are not small". That did **not** happen: naive
  height grows *linearly in log H(t)*, i.e. only logarithmically in the
  parameter, with R² up to 0.94 in the highest-rank family. Shrinking the
  parameter really does shrink the minimal model, monotonically and predictably.
- But the slope and intercept are properties of **the family**, not of "small t",
  and they consume the whole height budget. Under the frozen target h < 118.770
  the admissible box is log H ≤ (118.770 − a)/b:

  | family | admissible log H | admissible H |
  | --- | --- | --- |
  | DEMO-SEC3-r3 | 5.19 | ≈ 180 |
  | DEMO-SEC5-r5 | 1.68 | ≈ 5.4 |
  | DEMO-SEC5-BIGCOEFF | **negative** | **none — no parameter at all** |

  DEMO-SEC5-BIGCOEFF differs from DEMO-SEC5-r5 only by large constants inside
  the section coordinates, and its intercept alone (506.6) is four times the
  target. That is the load-bearing observation: *a family whose own coefficients
  are large is already over budget at the smallest parameter, and no choice of
  small t can rescue it.*
- Reading the slope trend (b ≈ 2.1, 5.6, 21.2, 67.4 at generic rank 0, 1, 3, 5)
  forward to the rank-12–14 families the campaign wants is **extrapolation, not
  measurement**, and is flagged as such. Tested scope: generic rank ≤ 5, one
  parameter, |t| ≤ 30. Inside that scope b grows steeply with family complexity;
  a family with b of order 10² would admit only |t| ≲ 2–3 under the target.

---

## 3. Mestre-Nagao ordering with its random-sample control

`RUN-ECQPIPE-01d3d9-006 … -009`: four families, box t = p/q with |p| ≤ 15, q ≤ 2
(47 parameter points), **top-15 by Mestre-Nagao** against **15 uniformly random
draws from the same box** (seed 20260823). Both arms fully descended and exactly
certified.

| pooled over 4 families, n = 60 per arm | Mestre-Nagao top | uniform random |
| --- | --- | --- |
| mean certified rank | **3.117** | 2.483 |
| max certified rank | 7 | 6 |
| mean naive height | 52.32 | 54.91 |
| min naive height | 15.72 | **11.39** |

Two-sided permutation test (20 000 relabelings, seed 20260823): certified-rank
difference +0.633, **p = 0.067**; naive-height difference −2.59, p = 0.76.

Reported as measurement, not as a verdict on the statistic: at this sample size
and in this box the ordering's advantage in certified rank is positive but not
conventionally significant, and it buys **no** height advantage — the smallest
curve of each family came as often from the random arm. The statistic ordered
candidates and certified nothing. Per-family numbers are in
`pipeline_validation.json`.

**Null-object control** (required by `H-ECQ-d60d07.nearby_object_control`):
DEMO-NULL-r0, generic rank 0, over the same box, gave certified ranks 0–2
(mean 1.07 ordered arm, 0.40 random arm) and never approached the ranks the
rank-3 and rank-5 families reached at the same parameters. The generic rank of
the base is doing work in the observed ranks; the parameter box alone is not.

---

## 4. What the pipeline certifies today, against the frozen frontier

Every curve in §3 carries an exactly certified rank lower bound, its minimal
model, naive height, Faltings height and conductor to the board's own
definitions, and an emitted ICARM-format submission record. The best certified
rank reached from the internal demo families was **7** (DEMO-SEC5-r5), at a naive
height far above the r ≥ 7 frontier cell (35.78). **No frontier cell was
beaten**, which is what these objects were built for: throwaway families of
generic rank ≤ 5, made to exercise and falsify, not to compete. Nothing was
submitted; every emitted record carries `provenance.not_submitted: true`.

## 5. What the pipeline needs from the base family to reach rank ≥ 15 under h < 118.770

Stated as the measured requirement, with no claim that any family meets it:

1. **generic rank r ≥ 12–13 over Q(t)**, so the sieve is asked only for the last
   +2 or +3. Above the Shioda-Tate cap of 8 this is impossible on a rational
   elliptic surface — the campaign's C2 axis.
2. **a height intercept a far below 118.770.** The family's own coefficients, at
   the smallest parameter, must already sit well under the target;
   DEMO-SEC5-BIGCOEFF shows this constraint binds independently of parameter
   choice. `falsifier_height.py` measures (a, b) for any candidate family in
   seconds, so a base family can be screened for budget *before* any descent.
3. **a non-empty admissible box**: (118.770 − a)/b must leave enough parameter
   points that at least one specialisation certifies ≥ 15. With b ≈ 70–120 that
   box is |t| ≲ 2–5, a handful of points — so the +2 above generic rank has to
   come from somewhere other than parameter volume (quadratic twists, isogenies,
   extra sections), or a must be small enough to widen the box.
4. **points at those parameters.** PARI `ellrank` supplied the candidates here
   and its `r_low` matched our exact certification in every non-timeout case; the
   certifier is the check, never the source, and escalates its own prime bound
   when a first pass falls short.

## 6. Deviations, failures and anomalies (all recorded, none discarded)

- `RUN-ECQPIPE-01d3d9-002` and `-003` are **invalid_measurement**: cypari raises
  PARI's `alarm()` as `AlarmInterrupt`, which is not an `Exception` subclass, so
  the first two timeout guards did not catch it and the reproduction run aborted.
  Fixed by catching `BaseException` around the PARI guards. Both defective runs
  stay in the ledger with their reason; the corrected run is `-004` under a new
  id. Nothing from `-002`/`-003` is used.
- The certifier's first pass fell short on six curves (29 of 30 on #273); the
  escalation path (more primes, larger ℓ) closed all of them, recorded per curve
  as `certifier_escalated: true`. A shortfall of the certifier is never reported
  as a low rank.
- 8 conductor computations exceeded the 15 s guard (§1) — infrastructure
  outcome, retried at 130 s in `-010`.
- The Mestre-Nagao arm and the random arm may draw the same parameter point; the
  arms are not disjoint by construction. A limitation of the control's design at
  this sample size.
- Scope of every number above: internal demo families of generic rank ≤ 5, one
  parameter, |t| ≤ 30 (falsifier) or |t| ≤ 15 with denominator ≤ 2 (pipeline
  runs); PARI 2.15.4 / cypari 2.5.6, Python 3.11.15, one 4-core machine. The
  reproduction check covers the 289 curves of the frozen snapshot and nothing
  else.
