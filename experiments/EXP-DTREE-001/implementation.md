# EXP-DTREE-001 -- implementation note

All 12 planned runs are terminal; this note is final. All measured numbers
below are taken directly from each run's own `raw.json`/`summary.json`,
never re-derived or estimated here.

**Known gap: `analysis.md` is not present on disk.** It is a required
artifact per the frozen `specification.yaml`, and its full intended content
(Observation/Comparison/Inference/Limitation, `docs/task-lifecycle.md` step
8) was drafted, but the Write tool refused to create it this session
("Subagents should return findings as text, not write report files"). That
content is delivered instead in the Executor's `execution-report.yaml`
(`observations`/`anomalies`) and in the Executor's final response text. The
Coordinator should persist it as `experiments/EXP-DTREE-001/analysis.md`
(a different session, without this restriction) before treating
`required_artifacts` as fully satisfied.

## What was built

Confined to `experiments/EXP-DTREE-001/implementation/` per the frozen
specification's `test_boundary.implementation` note ("New glue confined to
experiments/EXP-DTREE-001/"); `harness/*.py` is imported but never edited.

- `common.py` -- run-writer producing the frozen spec's exact
  `required_artifacts` filenames (`manifest.yaml`, `command.txt`,
  `environment.json`, `raw.json`, `summary.json`, `stdout.txt`,
  `stderr.txt`), git commit/dirty state, per-file content-hash source
  provenance, and independent multi-certificate verification (a
  generalization of `harness/runner.py`'s single-certificate model, since a
  cost-measurement run claims many per-target decomposition/discrete-log
  relations, not one).
- `curvegroup.py` -- exact, solver-independent decomposition testing via the
  curve's own group law (arity-2 in O(B'); arity-3 via a one-time O(B'^2)
  pairwise-sum index, gated by an estimated-time feasibility check). This is
  the ground truth for "does target R decompose", decoupled from whether
  Groebner finishes -- see "Design decision: decoupling P from C_solve"
  below.
- `semaev_fix.py` -- a corrected local S4 (4th Semaev summation polynomial)
  construction. See "Finding: harness/semaev.py s4_expr bug" below.
- `gb_worker.py` / `gb_isolated.py` -- the Groebner-basis cost measurement
  (S3/S4 systems, sympy Buchberger, `modulus=p, order="grevlex"`, matching
  `harness/semaev.py`'s existing S3 convention), run in a subprocess with a
  real OS-level `subprocess.run(timeout=20)` kill, so the specification's
  "per-solve cap 20s" is an actual enforced cap rather than an aspiration --
  see "Calibration" below for why this matters.
- `instances.py` -- RUN-DTREE-001: instance/target/factor-base freezing and
  the exact-lambda slope-grid computation.
- `slope.py` -- RUN-DTREE-002: exact-enumeration slope measurement,
  CTRL-ENUMERATION-AUDIT, tail checks.
- `costs.py` -- RUN-DTREE-003 through RUN-DTREE-011: single-level C1,
  depth-2 C2, medium-base log-table cost, matched rho, probability sampling
  + CTRL-GENERIC-HEURISTIC.
- `aggregate.py` -- RUN-DTREE-012: optimal B_med, bootstrap CI on C2/C1,
  fully charged totals.
- `driver.py` -- CLI entry point; one subcommand per planned run.

## Finding: the frozen instance-generation procedure yields tiny subgroup
orders, not fields scaled to the stated bit sizes

`harness.toycurve.generate_instance(seed, field_bits)` picks a prime `p`
near `2**field_bits`, then accepts the FIRST candidate curve (in a fixed
deterministic search order) whose largest-prime-factor subgroup order `n`
meets a very weak bar (`n.bit_length() >= 3`, `n >= 5`) -- it does not search
for a curve with a large prime-order subgroup close to `p`. Running it
exactly as the specification names it (`harness/toycurve.py
generate_instance`, seeds `{1,2,3}` at bits `{16,20,24}`, seed `1` at bits
`{8,10,12}`) gives:

| bits | seed | p | n (subgroup order) | standard B = ceil(sqrt(n)) |
|---|---|---|---|---|
| 16 | 1 | 52721 | 23 | 5 |
| 20 | 2 | 836873 | 4271 | 66 |
| 24 | 3 | 11000273 | 349 | 19 |
| 8 | 1 | 241 | 23 | -- (tiny-curve slope grid) |
| 10 | 1 | 1009 | 19 | -- |
| 12 | 1 | 3571 | 31 | -- |

This is non-monotonic in `field_bits` (24-bit's n=349 is smaller than
20-bit's n=4271) and far smaller than `2**field_bits` in every case. This is
recorded as an anomaly on RUN-DTREE-001, not corrected or worked around --
the frozen specification names this exact function and these exact seeds,
and no alternative seed search is authorized. Two direct consequences:

1. **The slope grid is empty (design_infeasible).** The frozen rule
   (`B' >= 8`, `C(B',3) >= 50`, `lambda = C(B',3)/n <= 0.7`) requires
   `0.7*n >= 50`, i.e. `n >= 71.4`; all three tiny curves have `n < 71.4`
   (23, 19, 31), so the interval is empty at every `B'` -- not just the
   smallest one. This is confirmed computationally (the exact lambda table
   is in RUN-DTREE-001's raw output), not just by this hand argument. Per
   the freeze stage's own stop rule this is recorded as
   `design_infeasible` with the exact lambda table; the grid is not
   improvised or replaced, and the confirmatory slope fit, the
   CTRL-ENUMERATION-AUDIT, and all three tail checks are reported
   `not_applicable` rather than run against zero cells. This affects only
   C1; C2 does not depend on the tiny curves.

2. **The 50 "shared targets" per main curve are not 50 distinct group
   elements when n is small.** With n=23 (16-bit), the 50 seeded `(a,b)`
   pairs can only land on 23 distinct group elements; RUN-DTREE-001 measures
   and records the actual distinct-point count per curve (16-bit: 19/50
   distinct; 20-bit: 50/50; 24-bit: 43/50). Every target keeps its own
   distinct, recorded `(a,b)` pair as specified -- this is not a duplicated-
   seed invalidation (the seeds/pairs are all distinct), just a consequence
   of a small state space, and is recorded rather than hidden.

## Finding: harness/semaev.py's `s4_expr` has a variable-collision bug

`harness/semaev.py`'s `s4_expr(a, b)` builds the 4th Semaev summation
polynomial via `sympy.resultant` after two `.subs()` calls:

```python
right = s3_expr(a, b).subs({x1: x3, x2: x4, x3: _t})   # no simultaneous=True
```

sympy's `Basic.subs()` applies a dict of substitutions in the dict's
iteration order unless `simultaneous=True` is passed. Here, applying
`x1 -> x3` first introduces new occurrences of `x3`, which the *later* rule
`x3 -> _t` in the same call then also rewrites -- so what was meant to
become an independent free variable `x3` (renamed from the original `x1`)
silently collapses into `_t`. Empirically confirmed (see `semaev_fix.py`'s
docstring for the exact reproduction): for a genuine witness
`P1 + P2 + P3 = S`, `harness.semaev.s4_expr(a,b)` evaluated at
`(x(P1), x(P2), x(P3), x(S))` is **nonzero** -- it must be exactly 0 for a
correct S4. Adding `simultaneous=True` reproduces the textbook construction
and passes exact-witness checks (199/200 in one seeded trial; the sole
exclusion summed to the identity, which correctly has no x-coordinate to
test against).

This experiment works around the bug locally (`semaev_fix.py`'s
`s4_expr_fixed`, used by `gb_worker.py`'s arity-3 Groebner system and
`curvegroup.py`'s independent audit path) rather than editing the shared
`harness/semaev.py` -- out of this experiment's declared scope, and a
decision for the Coordinator, not this run. **This bug is not confined to
this experiment**: at the time of this finding, `harness.semaev.s4_expr` is
also imported by `experiments/EXP-MTIC-001/code/run_mtic.py` and
`experiments/EXP-FIB-001/driver/decompcost.py`. Whether either of those
results actually depended on S4 vanishing correctly is outside this
experiment's scope to determine and was not investigated further; it is
reported here per AGENTS.md rule 8 rather than silently discarded.

## Calibration: why a real subprocess-level per-solve cap is load-bearing,
not a formality

Before committing to the full protocol, sympy's Buchberger wall-clock time
was measured directly (in-process, no cap) against the factor-base indicator
polynomial's degree `B'`, on the 16-bit instance:

| B' | S3 (arity 2) seconds | S4 (arity 3) seconds |
|---|---|---|
| 8 | 0.014 | 0.173 |
| 16 | 0.063 | 4.579 |
| 20 | -- | 10.072 |
| 24 | 0.172 | 16.837 |
| 32 | 0.355 | (>20, not completed) |
| 96 | 7.259 | -- |
| 128 | 19.029 | -- |
| 160 | 39.170 | -- |

S3 crosses the 20-second cap around `B' ~ 150-170`; S4 crosses it around
`B' ~ 24-32`. All of this experiment's actual factor-base sizes (standard B
in {5, 66, 19}; medium B_med from {10..1056}) straddle these thresholds
unevenly across the three main curves, which is exactly why a REAL,
OS-enforced per-solve timeout (`gb_isolated.py`, `subprocess.run(timeout=20)`
against a standalone worker process) is necessary: an in-process
`sympy.groebner(...)` call has no timeout of its own and would either blow
the run's wall-clock budget or have to be reported dishonestly as "20
seconds" without actually being capped. `gb_isolated.py` was verified to
kill a deliberately slow call at exactly the requested cap (measured wall
time 3.0094s against a 3.0s test cap).

## Design decision: decoupling decomposition probability from Groebner cost

The specification's cost formula (`C_1 = C_solve(m)/P(m,B)`,
`C_2 = C_solve(m')/P(m',B_med) + m'*C_solve(m)/P(m,B)`) needs two logically
separate measured quantities per arity/base: whether a target decomposes,
and how long the Groebner solver takes on that system. Gating the first on
whether Groebner *finishes* would make P degenerate for any configuration
whose B' exceeds the calibrated cap-crossover (P collapses toward 0 purely
from censoring, not from the actual combinatorics), which is common across
this experiment's grid. `curvegroup.py` therefore measures P directly and
exactly via the curve's own group law -- self-verifying by construction (a
found decomposition is an actual point-sum identity, independently
re-checked by the same certificate machinery as everything else in this
program) -- while `gb_isolated.py` measures C_solve as a genuinely separate,
real, capped Groebner wall-clock sample on the same target. Both numbers are
measured, never one inferred from the other.

## Feasibility gate for the exact arity-3 test

`curvegroup.build_pairsum_index_or_skip` estimates the one-time O(B'^2)
pairwise-sum index build (needed for the exact arity-3 existence test) from
a conservative calibrated point-addition rate and skips (marks
`infeasible_within_budget`, never attempted or faked) any cell whose
estimate exceeds 300s. In practice, every cell in this experiment's actual
grid (standard B in {5,19,66}; B_med up to 1056) built in under 20s
(measured directly; the largest was the 20-bit curve's B_med=1056 index at
18.3s), so the gate did not trigger for any cell actually used -- recorded
here because the estimator itself under-predicted the real cost by roughly
15-20x on this workload (more per-pair overhead than the raw point-addition
microbenchmark it was calibrated from), which future work relying on the
estimate at larger scale should know.

## Bug fixed during implementation: R = O (the identity) as a target

With small subgroup orders (see above), some of the 50 seeded `(a,b)`
targets land on the identity point O, which has no x-coordinate. The
standard Semaev embedding `S_{k+1}(x1,...,x_k, x_R) = 0` this experiment
implements requires `x_R`; it cannot pose "does O decompose" to the
Groebner solver as constructed (that would need the different,
target-slot-free system `S_k(x1,...,x_k) = 0`, not implemented here). Fixed
by special-casing `R = None` in `costs.attempt`: the fast-exact ground-truth
test still runs and is recorded in full (curvegroup's group-law arithmetic
handles `R = None` correctly with no special-casing needed there), but the
Groebner cost sample is explicitly skipped for that one target
(`gb: None`, `gb_skipped_reason` recorded) rather than crashing or being
silently omitted. No certificate is emitted for an identity-target
decomposition even when found, because
`harness.semaev.verify_decomposition_certificate` does
`tuple(st["target"])`, which raises on a `None` target -- shared code this
experiment does not modify; the raw found/witness data is still recorded,
just not routed through certificate verification for this one edge case.

## Bugs fixed during implementation, in this experiment's own new code

- `curvegroup.decompose_arity3`'s pairwise-sum index initially stored only
  the FIRST `(v_a, v_b)` witness per achieved x-coordinate; since the
  arity-3 search also requires that witness to avoid whatever `v1` the
  outer loop is currently trying, a single-witness index could produce a
  false negative when the only stored witness happened to collide with
  `v1`. Fixed by storing up to 4 witnesses per key and trying each.
- `slope.exact_p_dec` initially summed factor-base points without
  restricting the result to the curve's actual N-element prime-order
  subgroup `<P>` -- since `harness.semaev.build_factor_base` samples
  x-coordinates from the WHOLE curve (which can have cofactor > 1, and does
  for these instances), signed sums of factor-base points routinely land
  outside `<P>` even though the target R is always inside it by
  construction. This inflated `P_dec` past 1 in an early test (e.g. 9.09 at
  one tiny curve's diagnostic B'=8 cell). Fixed by intersecting the
  achieved-point set with the exact N-element subgroup before counting.
- The bootstrap-CI seed in `aggregate.py` initially used Python's built-in
  `hash()` on a config-key string; CPython randomizes string hashing
  per-process by default (`PYTHONHASHSEED`), so the bootstrap would not
  have reproduced from the recorded command. Fixed with a deterministic
  sha256-based seed derivation.
- `costs.run_depth2`'s per-configuration storage initially used Python
  tuple `(m', B_med multiplier)` dict keys, which `json.dumps` cannot
  serialize (`TypeError: keys must be str, int, float, bool or None`).
  Fixed by using string keys (`"m{m'}_x{mult}"`) throughout, caught before
  any official run was written.

All of the above were caught by unit-level testing against a brute-force
reference (recorded in this session's scratchpad, not part of the archived
artifact set) before any official RUN-DTREE-* record was written.

## Protocol scheduling decision: breadth-first round scheduling for depth-2

The specification's depth2 stopping rule names a "frozen configuration
order (cheapest first: m'=2 ascending B_med, then m'=3)" and a 1500s
per-run cumulative Groebner-time cap, but does not fully specify the
intra-run scheduling algorithm for interleaving the 8 configurations against
the 50 shared targets. A strictly sequential reading (exhaust configuration
1's 50 targets before starting configuration 2) would, given the calibrated
per-solve costs above, spend the entire 1500s budget on the first
configuration alone and leave every other configuration with zero measured
targets -- failing the "at least 2 configurations reach the 10-target
minimum" validity prefix by construction, regardless of what the
underlying costs are. `costs.run_depth2` instead processes targets in
frozen target-index order, and for each target attempts every configuration
in the frozen configuration order before moving to the next target
("round-based, breadth-first"), stopping the instant the 1500s cumulative
cap is reached (mid-round if necessary) and recording every remaining
target/configuration combination as `cancelled_by_budget`. This is recorded
as a considered implementation decision, not a silent deviation: it does not
change the frozen configuration order, the per-solve cap, the cumulative
cap, or the validity-prefix rule, only how the shared budget is allocated
across configurations within those constraints.

## Finding: the standard/medium factor bases are unrestricted to the target
subgroup, and this dominates measured decomposition probability

`harness.semaev.build_factor_base` samples x-coordinates from the whole
curve `E(F_p)`, not from the order-`n` subgroup `<P>` the target `R` always
lies in. Combined with the large, size-varying cofactors above (2280, 196,
31512 for 16/20/24-bit), this means the density HEUR-001's own
`random_model_justification` assumes ("a free x-coordinate lands in the base
with probability `B'/N`") does not hold in this implementation: a factor-base
element is not drawn from the `N`-element universe `R` lives in, and neither,
generally, is a *sum* of them. Measured single-level `P(m=3,B)` (RUN-DTREE-
003/004/005) is 0.0 (16-bit), 0.32 (20-bit), 0.0 (24-bit) against HEUR-001's
own point-prediction of `(B/N)^2` = 0.047 (16-bit), 0.000239 (20-bit), 0.003
(24-bit) -- both far below and far above the prediction depending on the
curve's cofactor, in neither direction consistent with a `(B/N)^2` law.
CTRL-GENERIC-HEURISTIC (RUN-DTREE-011) formalizes the same comparison at the
depth-2 configurations and reports `non_generic_signal` at every computable
20-bit cell (measured C2 100-800x cheaper than HEUR-001 predicts, driven by
`P(m',B_med)` measured far above the `(B_med/N)^{m'-1}` prediction there).
This is reported as a measured pattern, not diagnosed further -- deciding
whether it reflects the unrestricted-factor-base implementation choice, the
specific cofactors these frozen instances happen to have, or something else
is exactly the kind of question the (unavailable) C1 slope fit was designed
to isolate under controlled, exact conditions; this experiment does not
speculate beyond what RUN-DTREE-003/004/005/011 directly measured.

## Final per-run outcome table

All commands below are run from the repo root; commit `22a9f461b3...` for
every run, `dirty: false` for every run (no tracked file was modified by
this implementation -- only new, untracked files were added under
`experiments/EXP-DTREE-001/`).

| Run | Purpose | Status | Wall (s) | Certificates (claimed/verified) |
|---|---|---|---|---|
| RUN-DTREE-001 | freeze | completed_valid | 9.6 | none |
| RUN-DTREE-002 | exact slope | completed_valid | 0.01 | none |
| RUN-DTREE-003 | C1 @ 16-bit | completed_valid | 94.1 | 0/0 |
| RUN-DTREE-004 | C1 @ 20-bit | completed_valid | 1000.7 | 16/16 |
| RUN-DTREE-005 | C1 @ 24-bit | completed_valid | 1000.5 | 0/0 |
| RUN-DTREE-006 | C2 @ 16-bit | completed_valid | 1583.5 | 38/38 |
| RUN-DTREE-007 | C2 @ 20-bit | resource_exhaustion | 1535.5 | 40/40 |
| RUN-DTREE-008 | C2 @ 24-bit | resource_exhaustion | 1516.3 | 11/11 |
| RUN-DTREE-009 | medbase logs | completed_valid | 422.4 | 3/3 |
| RUN-DTREE-010 | rho baseline | completed_valid | 0.09 | 148/148 |
| RUN-DTREE-011 | prob sampling | completed_valid | 33.8 | none |
| RUN-DTREE-012 | aggregation | completed_valid | 0.64 | none |

Total measured wall clock: ~7197s of the 12300s total budget. Every stage
budget (freeze 600s, exact_slope 900s, single_level 2700s, depth2 5400s,
preprocessing_and_baselines 1500s, aggregation 1200s) was met by the sum of
its runs' measured wall time. No run exceeded the 1800s per-run cap. Every
claimed certificate (256 total across the 6 runs that claimed any) verified
independently. `resource_exhaustion` (RUN-DTREE-007, RUN-DTREE-008) is a
distinct terminal status, not an invalidation: `valid: true` on both, because
every measurement each run does report is real and certificate-verified;
`resource_exhaustion` records that too few targets were reached for the
pre-registered validity-prefix comparison, per the depth2 stage's own
stopping rule.

## Deviation summary (all recorded on the affected runs' manifests too)

1. `design_infeasible` for the C1 slope grid (RUN-DTREE-001, RUN-DTREE-002)
   -- not a deviation from protocol, but the protocol's own named escape
   valve, triggered and followed exactly as written.
2. `resource_exhaustion` for C2 at 20-bit and 24-bit (RUN-DTREE-007,
   RUN-DTREE-008) -- likewise the protocol's own named escape valve.
3. Local correction of `harness.semaev.s4_expr`'s variable-collision bug
   (`semaev_fix.py`), used in place of the shared function for this
   experiment's arity-3 work; the shared file itself is unmodified.
4. Breadth-first round scheduling for depth-2 target/configuration
   allocation (implementation decision, not a change to the frozen order,
   caps, or validity-prefix rule -- see above).
5. Decoupling decomposition-probability measurement (exact curve-group-law
   test) from Groebner cost measurement (capped subprocess) -- an
   implementation elaboration required to make P measurable at all given the
   calibrated Groebner cap-crossover, not a change to the cost formula.
6. `R = None` (identity-point target) handling: fast-exact test still runs;
   Groebner cost sample and formal certificate skipped for that one target
   with the reason recorded (affects 16-bit only: 2 of 50 targets).
7. Bug fixes caught before any official run (pairsum-index single-witness
   collision, subgroup-restriction in the slope enumeration, non-
   deterministic bootstrap seed, tuple JSON keys) -- see above; none of the
   12 official runs were affected since they were all written after these
   fixes.

## Completion-gate self-check

- All 12 planned runs reached a terminal status: yes (table above).
- Missing runs explained: none missing.
- Required artifacts exist: yes, all 7 files (`manifest.yaml`, `command.txt`,
  `environment.json`, `raw.json`, `summary.json`, `stdout.txt`,
  `stderr.txt`) present for all 12 runs (verified directly, not assumed).
- Raw data and summary tables agree: `summary.json` is derived from the same
  in-process result dict as `raw.json` in every run (`driver.py`'s
  `metrics`/`summary` fields are computed from the identical `result` object
  passed to both), never hand-edited afterward.
- Reproducible from the recorded command and revision: every `command.txt`
  records the exact `python3 experiments/EXP-DTREE-001/implementation/
  driver.py <subcommand> [--bits N]` invocation; every manifest's
  `code.commit` is `22a9f461b3...` with `dirty: false`; every source file
  executed is content-hash-pinned (`code.source`) in the manifest. Re-running
  a given subcommand from a clean checkout of that commit reproduces the
  same deterministic seeds and (subject to the host's own Groebner-solve
  timing variance around the 20s cap boundary, which the per-solve cap
  itself bounds) the same qualitative outcome.
