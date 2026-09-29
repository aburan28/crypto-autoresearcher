# NAGAO-1994 height budget and cell reachability — TASK-20260823-f88f54

BATCH-da59ec · GOAL-ECQ-002 · H-ECQ-a609f8 · executor
repo commit at execution: `a039e9630b27f63c204eeff0e41ffeda3eddc6d2`, tree clean at start
requested policy `executor-implementation`; answered by `claude-opus-5` (no fallback, no downgrade)
budget 3600 s / 4 GB / 80 runs — used **12 runs**, ~100 s of wall clock, peak RSS well under 1 GB

Observations only. No hypothesis status is set here, no cell is claimed, nothing was sent to ICARM.

---

## 0. Headline (measured)

| pre-declared target | incumbent naive height | admissible box | deciding number |
| --- | --- | --- | --- |
| r ≥ 12 | 69.33878142645637 | **EMPTY** | measured min 109.505165, i.e. **+40.166384** above the cell |
| r ≥ 13 | 75.75973380404125 | **EMPTY** | **+33.745431** |
| r ≥ 14 | 85.18925824647027 | **EMPTY** | **+24.315907** |

Measured height budget over the declared parameter box (|num t| ≤ 60, den ≤ 6, 457 fibres):

```
naive_height  =  135.9758  +  0.3875 · log H(t)        R^2 = 0.000418,  n = 457
```

Zero of 1137 distinct measured fibres has naive height below any of the three targets.
Zero infrastructure timeouts. The exact height gate was applied FIRST, and because it left
nothing, **Mestre–Nagao ordering was never run** — there was no admissible set to order.

The Coordinator's recorded prior **P1 is not contradicted**: the box is empty at all three targets.

## 1. Nagao self-consistency, re-verified symbolically (RUN-…-001)

Coefficients were read programmatically out of BATCH-f2341e's `candidate_families.json`
(`NAGAO-1994.weierstrass_coefficients_in_t`); nothing was retyped. Exact integer polynomial
arithmetic, stdlib only.

Substituting x = (t+703)/15 into the transcribed quartic and multiplying by 15⁴ = 50625, against
9·N(t)² with N(t) = −224t³ − 844t² + 900484t + 2161725:

| t^k | 9·N² | quartic side | ratio |
| --- | --- | --- | --- |
| t⁰ | 42057494780625 | 65504716350802560000 | 1557504 |
| t¹ | 35038777948200 | 54573036809433292800 | 1557504 |
| t² | 7265001982104 | 11315269647134908416 | 1557504 |
| t³ | −22396228128 | −34882214894272512 | 1557504 |
| t⁴ | −3624340464 | −5644924770041856 | 1557504 |
| t⁵ | 3403008 | 5300198572032 | 1557504 |
| t⁶ | 451584 | 703343886336 | 1557504 |

The ratio is constant at all seven coefficients and 1557504 = 1248². The point
**((t+703)/15, 1248·N(t)/75) lies exactly on the transcribed quartic** — checked directly as a
polynomial identity, not only through the ratio. The Coordinator's claim reproduces; the
BATCH-f2341e verdict ("FAILS") was a false negative, caused by testing the section with y = N/75
instead of y = 1248·N/75.

Scope, stated because it is easy to overread: this establishes **self-consistency of the
transcription only**. It is not evidence that the coefficients are Nagao's published equation.
Source retrieval remains owed.

## 2. Quartic → Weierstrass, and what minimalisation strips (RUN-…-002, -003)

The quartic carries a rational point (§1), so it is isomorphic over Q(t) to its Jacobian. Using
I = 12ae − 3bd + c², J = 72ace + 9bcd − 27ad² − 27b²e − 2c³ and Y² = X³ − 27I·X − 27J:

| | degree in t | max |coeff| digits |
| --- | --- | --- |
| quartic c₄…c₀ | 2,2,4,4,6 | 12, 14, 17, 18, 19 |
| a₄ = −27·I(t) | 8 | 32 (66822723724830555775250985910272) |
| a₆ = −27·J(t) | 12 | 48 (210161338193283500750712771693539711197133144064) |

deg(a₄, a₆) = (8, 12) is consistent with an elliptic K3 (d = 2), matching the unconditional
d ≥ 2 that BATCH-f2341e derived from geometric rank 13.

**Independent cross-check of the conversion**: for each of 10 parameter values the specialised
quartic was passed to PARI `ellfromeqn` — a route that does not touch the I/J computation — and
its minimal model compared with the specialisation of the model above. **10/10 agreement on
`curve_key` (c4:c6), 0 disagreements.**

**Minimalisation, the number this batch exists to measure** (naive height, minimal-model
convention pinned by BATCH-f2341e CHECK 1):

| t | before | after | stripped | c₄ digits | c₆ digits |
| --- | --- | --- | --- | --- | --- |
| 0 | 231.452 | 124.400 | 107.053 | 34 → 19 | 51 → 28 |
| 1 | 231.453 | 119.534 | 111.918 | 34 → 18 | 51 → 26 |
| 2 | 231.453 | 111.217 | 120.236 | 34 → 17 | 51 → 25 |
| 3 | 231.454 | 132.719 | 98.735 | 34 → 20 | 51 → 30 |
| 703 | 285.943 | 174.025 | 111.918 | 42 → 26 | 63 → 38 |

Prior **P2 holds**: minimalisation strips a great deal — 98.7 to 120.2 in naive height, i.e.
14–17 decimal digits off c₄ and 21–26 off c₆. It is still nowhere near enough. What survives is
109.5–174, against targets of 69.3–85.2.

## 3. Height budget and the three admissible boxes (RUN-…-004, -005, -006)

`falsifier_height.py` was reused unmodified from the BATCH-f2341e pipeline (imported by path; no
file was written into that task's directory). Declared box |num t| ≤ 60, den ≤ 6 → 457 fibres,
0 timeouts:

* a = 135.9758, b = 0.3875, **R² = 0.000418**
* min 109.531 (t = ±58), median 137.585, max 171.361

R² ≈ 0.0004 says the parameter size explains essentially **none** of the height variation inside
this box: the family's own constants dominate and the small-parameter lever does not operate for
Nagao. Because of that the fit-derived budget is reported but is **not** the deciding number.
Reported for completeness, the fit gives max log H = −171.97 at r ≥ 12 (max H = 2.06e−75 < 1),
−155.40 at r ≥ 13 and −131.06 at r ≥ 14 — all empty on their face.

The deciding number is the **exact** one: the smallest naive height actually measured.

Note against a naive reading of the fit: the smallest heights in the box occur at *large even* t
(58, 62), not at small t. Small t is not optimal here.

## 4. Robustness probe outside the declared box (RUN-…-007)

Recorded separately and never merged into the declared measurement. Integer t, |t| ≤ 400 (801
fibres, 0 timeouts): min 109.505 at t = ±62, and the lower envelope flattens rather than
descending. **0 of 801 below 85.189.** Widening in the one direction that could have overturned
an empty box does not overturn it.

Union of both boxes: **1137 distinct parameters, 0 below any target.**

## 5. Secondary rank probe (RUN-…-009; RUN-…-008 preserved as an implementation error)

Not a sieve — the box is empty, so nothing was eligible and no ordering step ran. This probe
exists only to inform prior P3 and falsification clause 2. Every rank below is a **certified
lower bound** from `exact_certify.py` (exact, stdlib-only, independent of the PARI search that
produced the points), backed by that many exhibited independent points.

| t | certified rank ≥ | points exhibited | naive height | PARI search time |
| --- | --- | --- | --- | --- |
| 0 | 6 | 6 | 124.400 | 0.04 s |
| 1 | **14** | 14 | 119.534 | 73.0 s |
| 2 | 11 | 11 | 111.217 | 2.0 s |
| 62 | **12** | 12 | 109.505 | 12.9 s |

Prior P3 (certified rank ≥ 12) is met at t = 62 and exceeded at t = 1. t = 0 and t = 2 fall short
of 12; per the discipline fixed before the numbers were read, **a shortfall is a search outcome,
never a statement that the rank is below 12** (t = 0 is visibly a special fibre). Nothing here
supports falsification clause 2.

These curves are **not submittable** and no submission was made: each is 24–50 above its cell.

## 6. Independent height recomputation

Every reported naive height was recomputed from the minimal a-invariants alone, in stdlib integer
arithmetic (b₂, b₄, b₆, c₄, c₆ then log max(|c₄|³, c₆²)), with no PARI involvement.
**14/14 agree with the PARI value to < 1e−9.** The full a-invariants, c₄ and c₆ are in
`nagao_height_budget.json → independent_height_recomputation_from_a_invariants`, so a reviewer can
redo it from the record.

## 7. Anomaly: pre-declared incumbents vs the frozen frontier file

Unexpected, recorded, not resolved and not edited:

| cell | value pre-declared in H-ECQ-a609f8 | value in frontier_20260823.json | curve id | difference |
| --- | --- | --- | --- | --- |
| r ≥ 12 | 69.33878142645637 | 69.33884136527462 | 157 both | 6.0e−5 |
| r ≥ 13 | 75.75973380404125 | 75.76026257010892 | 158 both | 5.3e−4 |
| r ≥ 14 | 85.18925824647027 | 85.18925824647027 | 244 both | 0 (identical) |

Curve ids and submitter agree; only the 5th/4th decimal differs, and only for two of three cells.
The **pre-declared (frozen) values were used as the gate**, which for r ≥ 12 and r ≥ 13 is the
stricter of the two. Against measured gaps of 24–40 this changes no conclusion. Flagged for the
Coordinator because a frozen target that does not match its own cited source is a bookkeeping
defect worth a correction record, not something an executor should silently reconcile.

## 8. What this does and does not say about H-ECQ-a609f8

Reported as measurement; the judgement is the Reviewer's and the Coordinator's.

* Falsification clause 1 ("EMPTY admissible parameter box at all three pre-declared targets"):
  the measurement it asks for was taken, and all three boxes are empty at the exact gate, over
  1137 distinct fibres, with (a, b) = (135.9758, 0.3875), R² = 0.000418.
* Falsification clause 2 ("certified rank of small-t Nagao specialisations below 12"): certified
  rank 12 at t = 62 and 14 at t = 1. The shortfalls at t = 0, 2 are search outcomes, not rank
  bounds.
* Assumption 1 (transcription self-consistency): re-verified symbolically at all seven
  coefficients. Source retrieval still owed.
* The exclusions hold: r ≥ 15 and r ≥ 1 were not targeted and nothing here claims them.

Scope of every number above: the transcribed NAGAO-1994 quartic, its Jacobian Weierstrass model,
rational t with |num| ≤ 60 and den ≤ 6 plus integers |t| ≤ 400, PARI 2.15.4 via cypari 2.5.6, the
BATCH-f2341e naive-height convention. Nothing is claimed about other models of the same surface,
other families, or parameters outside these boxes.

## 9. Protocol deviations

1. `run_harness.py` was copied into this task's `scripts/` with only its TASK/BATCH/HYP/ROOT
   constants changed, because the original writes run directories inside BATCH-f2341e's task
   scope. The mathematical pipeline (`falsifier_height.py`, `pipeline.py`, `exact_certify.py`,
   `icarm_invariants.py`, `families.py`) was imported by path and **not modified or copied**.
2. Steps 1, 2 and 2b were first executed outside the harness while being developed; the recorded
   runs 001–003 re-executed the identical scripts under the harness and are the record.
3. RUN-…-008 called `evaluate_candidate(..., want_record=False)`, which skips the point search
   entirely, so it produced no rank numbers — an `implementation_error`. It is preserved, marked,
   and superseded by RUN-…-009. Nothing was reused from it.
4. Runs 010 and 011 built the deliverables and are superseded by 012 (010: submission-record key
   name missed 4 of 14 independent recomputations; 011: a hard-coded fibre count of 1258 double
   counted the 121-parameter overlap between the two boxes — corrected to the true union, 1137).
   All are preserved; the deliverables at the declared paths are those of RUN-…-012.
5. The wide probe (§4) goes outside the declared box. It is recorded as a separate probe with its
   own run and is never merged into the declared (a, b). It can only strengthen an empty box.

## 10. Artifacts

* `nagao_height_budget.json` — the measurement, per §1–§5 plus the frontier anomaly
* `cell_reachability.json` — per target: reachable or not, with the deciding number
* `report.md` — this file
* `runs/RUN-ECQNAG-f88f54-001 … -012/` — immutable run records
* `scripts/` — every script executed; `results/` — raw outputs
* no ICARM submission artifact exists, because no candidate passed the gate
