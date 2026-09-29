# TASK-20260822-81141a — execution report

Goal `GOAL-ECQ-001`, batch `BATCH-7e06d3`, hypothesis `H-ECQ-cec3c4`,
question `RQ-ECQ-80f23c`.

This report records what was run, what was measured, and what failed. It does
not interpret significance and does not state whether the hypothesis is
supported.

Repo commit at execution: `f7d971625a8d6a4c39c351f5b1f4f9d4a0d46cb3` (dirty tree —
this task's own untracked artifacts). Implementation `src/pipeline.py` sha256
`8469e148713e44a925e83e95b565319e7ecd5200c0aa70d259f29234a78a2c4d` for runs
001–004; runs 005–006 used the same file with one additive CLI flag
(`--only-arm`) and the aggregation-only `assemble` subcommand appended
(see Deviations).

## Budget

| | limit | used |
|---|---|---|
| wall clock | 3000 s | **1993.0 s** (sum of the seven run manifests) |
| memory | 4 GB | **1.22 GB** peak RSS (RUN-004) |
| runs | 60 | **7** |

## Harness self-tests (RUN-ECQ-81141a-001) — both required, both reported

**(a) Re-verified rank-30 record curve**
(`experiments/EXP-ECRANK-e1e30e/runs/RUN-ECRANK-e1e30e-003/record_curve_input.json`),
30 generators supplied.

- returned rank: **30** — PASS (expected exactly 30)
- regulator determinant: `1.0720686604115654970290884760953064158e37` (38 digits),
  `10720686604115654970290884760953064067.13...` (77 digits)
- least eigenvalue: `0.29406575357597253` at both precisions
- these reproduce the values recorded in RUN-ECRANK-e1e30e-003 (1.07e37, 0.294).

**(b) Conductor-37 curve `[0,0,1,-1,0]`**, 18 points supplied from `ellratpoints(50)`.

- returned rank: **1** — PASS. Regulator `0.46000267415971956...` at both precisions.

A first version of the independence test used a *relative* determinant
criterion (`det / prod(diag)`) and returned **24** on fixture (a) — it
under-counted. That failure is why the shipped criterion is the incremental
one: a point is accepted only if it multiplies the Gram determinant by more
than `tol = 1e-6`, which is the squared distance of the new vector to the span
of the accepted ones and is therefore dimension-independent. The defective
criterion was replaced before any family number was produced; no result in
this package was computed with it.

## Stage 1 — rational elliptic surface with 8 sections (RUN-ECQ-81141a-002)

Configuration chosen by a deterministic seeded search (seed 81141) over 4000
candidate 8-point sets, 219 of which passed the general-position audit and
built. **The selection objective was model coefficient height only** — not
rank, and not any property of the specialisations.

Eight points in P^2(Q):
`(4:0:1) (-1:2:1) (-3:-2:1) (0:-1:1) (-2:-1:1) (2:0:1) (-4:2:1) (1:-2:1)`

- General-position audit (exact): no 3 collinear, no 6 on a conic, all
  distinct — **passed**.
- Cubics through the 8 points: kernel of the 8x10 exact rational system has
  dimension **2** — a genuine pencil `C_t = C1 + t*C2`. Solved with this
  task's own `Fraction` RREF; no floating point.
- **9th base point computed, not assumed**: `(197684347 : -60668562 : -45807609)`,
  obtained by eliminating `y` from `C1, C2` by resultant, dividing out the
  eight known `x`-coordinates, and taking the residual linear factor; then
  verified by exact substitution into both `C1` and `C2` (both give 0).
- Weierstrass family over Q(t), obtained by an explicit frame change
  (zero section -> `(0:1:0)`, its tangent -> the line at infinity, third
  tangent intersection -> `(1:0:0)`), not by `ellfromeqn` — because the map on
  points is needed and `ellfromeqn` returns only the Jacobian's invariants:

```
y^2 = x^3 - 27*c4(t)*x - 54*c6(t)
c4 = 59209471881*t^4 - 72876695976*t^3 + 32293889280*t^2 + 12854790432*t + 1344896064
c6 = -14721531609901221*t^6 + 26106405673782924*t^5 - 15081195539818296*t^4
     - 1580977877662224*t^3 - 1432084436788608*t^2 - 607452115008384*t - 61796844698112
```

- `deg c4 = 4`, `deg c6 = 6`, `deg disc = 12` — the numerical signature of a
  **rational** elliptic surface (Mordell–Weil rank <= 8 over Qbar(t)).
- The 8 sections (images of the other eight base points) are exhibited as
  polynomials `X(t)` of degree 2, `Y(t)` of degree 3, and each was verified
  **symbolically over Q(t)** to satisfy the curve equation identically.

### P1 check: the 8x8 Neron–Tate regulator at specialisations

| t | rank of the 8 sections | 8x8 regulator det (38 digits) |
|---|---|---|
| -1 | **8** | 1019096.05 |
| -7 | **8** | 3184383.19 |
| 7/5 | **8** | 2499514.05 |
| 11/3 | **8** | 9151812.0 |
| 3 | **8** | 1010027.36 |
| 1 | 4 | 1.98 (four exact zero eigenvalues) |
| 2 | 7 | 114827.0 |
| 1/2 | 7 | 22381.3 |
| 5 | 7 | 14713.1 |

Nonsingular 8x8 regulators at five independent `t` were obtained. The rank
drops at `t in {1, 2, 1/2, 5}` are reported as measured: the height matrices
there have exact zero eigenvalues at 77 digits (four of them at `t=1`), so they
are genuine exceptional specialisations, not a tolerance artefact. They are
recorded here rather than filtered out.

## Stage 2 — Mestre–Nagao sieve (RUN-ECQ-81141a-003)

`S(N) = sum_{p<=N} ((p+1-a_p)/p)*log p` with `N = 1000` (168 primes), `ellap`.
Used for **ordering only**; it contributes to no certified rank anywhere.

- **Tier 1 volume scored: 97 640 specialisations** — `t = p/q`, `gcd(p,q)=1`,
  `0 < |p| <= 2000`, `1 <= q <= 40`. Zero singular fibres in the domain.
- Cost: **1.028 ms per specialisation** (100.4 s total).
- Score range: max 1009.349, median 992.001, min 976.071.
- Tier 2 (matched sub-domain for the controlled comparison): `|p| <= 150`,
  `q <= 8`, **1548 specialisations**.

## Stage 3 — certification over Q (RUN-ECQ-81141a-004, -005, -007)

Rule applied throughout: **every reported rank is a lower bound from exhibited
points on that exact curve.** Points come from the 8 sections plus whatever
points `ellrank` exhibits; `ellrank`'s `r_low`/`r_high` are recorded but are
never used as a claim. Every point is re-verified in exact rational arithmetic
by this task's own code, and the r x r regulator is computed at 38 and 77
digits and required to agree.

### Matched-arm comparison (RUN-004, tier-2 domain, K = 60 per arm, overlap 2)

| | MN arm (top 60 of 1548 by S(1000)) | random control (60 of 1548, seed 81141) |
|---|---|---|
| certified rank >= 9 | **28 / 60 = 46.7 %** | **16 / 60 = 26.7 %** |
| certified rank >= 10 | **24 / 60 = 40.0 %** | **6 / 60 = 10.0 %** |
| certified rank >= 11 | **12 / 60 = 20.0 %** | **0 / 60 = 0 %** |
| max certified rank | 11 | 10 |
| rank histogram | 8:32, 9:4, 10:12, 11:12 | 8:44, 9:10, 10:6 |
| descent timeouts (8 s alarm) | 31 | 35 |

Caveat recorded with the numbers: a descent timeout floors that fibre at rank 8
(the sections alone), so **both** hit rates are lower bounds. Timeout counts
are comparable between arms (31 vs 35), so the confound is roughly balanced,
but it is not eliminated.

### Global top arm and best certified curve

Tier-1 top 20 by S(1000), 20 s alarm (RUN-004): 18 timeouts, max certified
rank **12**.

**Best certified curve: t = -65/22**

```
y^2 = x^3 + A x + B
A = -518228207838672723
B = 141005837549331272675978478
```

- 20 points exhibited (8 sections + 12 from descent), all on the curve in
  exact rational arithmetic;
- **certified rank 12**, independent subset indices `[0..7, 9, 10, 11, 12]`;
- 12x12 regulator `5833522604.95139622659344786969313882...` at 38 and 77
  digits, least eigenvalue `0.3462478885838063` at both.

Overall across all certified fibres (137 distinct `t`): rank 12 x1, rank 11 x12,
rank 10 x17, rank 9 x14, rank 8 x93.

### Independent re-verification (RUN-ECQ-81141a-007)

Top 15 curves re-checked by `src/verify.py`, which does not use the solver that
produced the points and cross-checks the on-curve test two ways (own `Fraction`
arithmetic and PARI `ellisoncurve`), recomputing the height matrix from
scratch. **All 15 agree**: same ranks, all points on curve by both tests,
discriminants nonzero.

## Stage 4 — the gap, as numbers

- **Axis 1, base rank over Q(t): achieved 8; the published records rest on
  roughly 18–20.** 8 is not a shortfall of effort — it is the ceiling of this
  construction: a pencil of plane cubics through 8 points is a *rational*
  elliptic surface, whose Mordell–Weil rank over Qbar(t) is at most 8. The
  measured `deg c4 = 4, deg c6 = 6, deg disc = 12` confirms the surface is
  rational. Gap on this axis: **10 to 12**, and it cannot be closed by sieving.
- **Axis 2, sieve volume: 97 640 specialisations scored at 1.028 ms each.**
  Certification, not scoring, was the binding cost: descent was attempted on
  140 fibres and timed out on 84 of them.
- **Best certified rank over Q: 12. Shortfall to the open target 31: 19.**
- Largest extra-over-base observed anywhere: **+4** (12 from a base of 8),
  once in 140 attempted fibres. Reaching 31 from a base of 8 would require +23
  from a single specialisation. Nothing measured here scales to that.
- Record ladder for context: 28 (2006), 29 (2024), 30 (2026). A rank-12 result
  from a rank-8 Q(t) base is not a fraction of the way to 31; the ladder rests
  on a different base-rank regime.

Full numbers, including the transfer assumptions and the tested-parameter
scope, are in `gap_analysis.json`.

## What failed

1. **84 of 140 descents timed out** at the 8 s / 20 s `alarm` guards
   (RUN-004). Classified `resource_exhaustion`, not negative evidence. Each
   timed-out fibre still carries its certified rank-8 floor from the sections.
2. **RUN-005 (90 s alarm on the tier-1 top 20) exhausted its 800 s internal
   budget after 10 of 20 candidates**; 9 of those 10 still timed out. The
   remaining 10 are recorded as `not_run_budget_exhausted`. The deeper alarm
   did **not** improve on RUN-004 — its best was 11, and it never reached
   `t = -65/22`. Both runs are retained in full; nothing was re-scored.
3. **`ellratpoints` at bound 100 found no points** on these specialised models
   (their coefficients are ~1e18–1e26), so all extra points came from
   `ellrank`'s 2-descent. This is a real limitation on the extra-point search.
4. **The first independence criterion under-counted the rank-30 fixture (24
   instead of 30).** Caught by self-test (a) before any family number was
   produced; described above.

## Deviations from the protocol

- **No `experiments/<EXP-ID>/specification.yaml` exists for this work.** The
  frozen contract used was `ledger/handoffs/TASK-20260822-81141a.yaml` together
  with `ledger/hypotheses/H-ECQ-cec3c4.yaml`; between them all required fields
  (objective, inputs, controls, metrics, budget, stopping rules, artifact list,
  completion gate, and the frozen predictions P1–P3) are present, so this was
  executed rather than refused. Flagged for the Coordinator.
- Run records live under the task `write_scope`
  (`.../TASK-20260822-81141a/runs/RUN-ECQ-81141a-00N/`) rather than under
  `experiments/`, because the handoff forbids writing outside the scope. Each
  run directory carries `manifest.yaml`, `manifest.json`, `command.txt`,
  `environment.json`, `stdout.log`, `stderr.log`, `raw-result.json`.
- `src/pipeline.py` gained an additive `--only-arm` flag and an
  aggregation-only `assemble` subcommand *after* RUN-004. Neither changes any
  computation used by runs 001–004, and no completed run was re-scored.
- `src/verify.py` (RUN-007) is a second implementation file beyond the declared
  `src/pipeline.py`; it exists to keep the re-verification independent of the
  solver.
- Nothing was tuned toward rank 31. The only search with an objective was the
  8-point configuration search, whose objective is model coefficient height.

## Environment

python 3.11.15; cypari -> PARI/GP 2.15.4; numpy 2.4.6; **no Sage, no sympy**.
Randomness: `random.Random` with explicit integer seeds only (81141 for the
configuration search and for the random control arm); recorded in every
artifact.

## Artifacts

`qt_family.json`, `certified_curves.json`, `gap_analysis.json`, `report.md`,
`src/pipeline.py`, `src/verify.py`, `src/runwrap.py`,
`runs/RUN-ECQ-81141a-001..007/`.
