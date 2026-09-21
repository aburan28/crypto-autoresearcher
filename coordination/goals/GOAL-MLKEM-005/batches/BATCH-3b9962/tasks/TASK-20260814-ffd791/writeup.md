# TASK-20260814-ffd791 -- Stage 0 lead producer, writeup

goal / batch: GOAL-MLKEM-005 / BATCH-3b9962
scope: PREREG-8 section 1 (infrastructure re-verification) and section 2
(Stage 0 feasibility benchmark) ONLY. Section 3 (Stage 1) was NOT run.
`H-MLKEM-7d9bcc` stays `proposed`; `EXP-MLKEM-42ea04` stays
`review_required` / `approved_by: null`. No claim about C1, C2, or ML-KEM
security is made anywhere below.

---

## 1. Section 1 -- infrastructure re-verification: ALL THREE CHECKS PASSED

Full detail: `infra_verification_results.json`. Total wall clock 4.94s
(well under the 1800s/120s/120s component caps).

| # | check | result |
|---|---|---|
| 1 | fpylll installed, version recorded, `BKZ.reduction` callable with an explicit `block_size` and a default strategies file | **PASS** -- fpylll 0.6.4 (prebuilt manylinux wheel, installed via `pip3 install fpylll` in 1.5s; no from-source build was needed). `cysignals` had to be installed separately (`ModuleNotFoundError` on first `import fpylll` otherwise) -- recorded as protocol deviation DEV-2, not a failure. The wheel's own baked-in default strategies path does not exist on this host; a functionally equivalent strategies file at the OS package path (`/usr/share/libfplll8/strategies/default.json`) was used instead for every BKZ call in this task (deviation DEV-1). Smoke-tested with `BKZ.Param(block_size=10, ...)` on a toy `d=20` q-ary basis: succeeded. |
| 2 | real CBD(eta) sampler and FIPS 203 `Compress_d`/`Decompress_d`, independently re-derived and checked against Table 2 (`eta1=3, eta2=2, d_u=10, d_v=4`) | **PASS** -- CBD(2) and CBD(3) sampler checked against the EXACT combinatorial PMF (brute-force enumeration of all `2^(2*eta)` bit patterns per FIPS 203 Algorithm 8), not merely the mean/variance formula: variance matches `eta/2` to floating-point tolerance for both, and a chi-square goodness-of-fit test against 200,000 samples passes at alpha=0.001 for both (`p=0.032` for eta=2, `p=0.696` for eta=3). Compress_10/Decompress_10 and Compress_4/Decompress_4 round-trip error, measured over 2000 random points each, is exactly at the theoretical worst-case bound `round(q/2^(d+1))` (2 for d=10, 104 for d=4), never exceeding it. Table 2 note: PREREG-8's own scope values (`eta1=3, eta2=2, d_u=10, d_v=4`) match ML-KEM-512 exactly; ML-KEM-768 shares `d_u=10, d_v=4` and `eta2=2` but uses `eta1=2`, NOT `eta1=3` -- both are checked in `cbd_checks` (eta in {2,3}), and the task-card phrase "ML-KEM-512/768 Table 2 values" is disambiguated explicitly here rather than silently conflated. |
| 3 | batched (numpy/BLAS-style) nearest-plane Babai reproduces exact scalar Babai on hand-checkable small instances | **PASS** -- a from-scratch scalar (per-target Python loop) and a from-scratch batched (single vectorized loop over all targets at once) implementation of nearest-plane Babai, both built on an independent (non-fpylll) numpy Gram-Schmidt, agree bit-for-bit (max residual-vector diff `0.0`, max coefficient diff `0`) on 20 random targets each at `d in {4, 6, 8, 10}`. |

**Section 1 termination: CLEARED.** Proceeded to Stage 0.

---

## 2. Section 2 -- Stage 0 feasibility benchmark: 0/6 main-grid cells cleared

Full detail: `stage0_results.json`. Total Stage-0 script wall clock:
3466.19s (~58 minutes), well inside the task's own 25200s budget.

### 2.1 Main grid (6 cells, cap = 3600s each)

| d | beta | outcome | wall clock | peak RSS |
|---|---|---|---|---|
| 256 | 40 | **ERROR** | 70.2s | 62.9 MB |
| 256 | 55 | **ERROR** | 53.7s | 62.7 MB |
| 256 | 70 | **ERROR** | 79.3s | 62.6 MB |
| 512 | 40 | **ERROR** | 395.9s | 141.0 MB |
| 512 | 55 | **ERROR** | 404.9s | 140.9 MB |
| 512 | 70 | **ERROR** | 408.9s | 141.1 MB |

**Every single cell failed with the identical exception**:
`fpylll.util.ReductionError: b'infinite loop in babai'`, raised from
`BKZReduction.__call__`'s own internal `self.lll_obj()` call
(`fpylll/algorithms/bkz.py:123` -> `src/fpylll/fplll/lll.pyx:305`), before
any actual BKZ tour completed.

This is explicitly recorded as its **own, third outcome category**,
distinct from both:
- `NOT_COMPUTED` (the cap-timeout outcome PREREG-8 section 2.3 names --
  none of these 6 cells hit that; every one finished, with an error, in
  well under 410s against a 3600s cap), and
- a completed reduction (delta/tours/wall-clock reported as a measurement).

No wall-clock or delta number is reported for any of the 6 cells as if it
were a measured reduction time, because none of them reduced anything.

**Reproducibility check.** (d=256, beta=40) was independently re-run
out-of-band, from the same seed (`seed_used=1398073216`, derived
deterministically from `default_rng([715923, 0, 256, 40, 0, 0])` per
PREREG-8 section 3.5): identical exception, same message, ~69s to fail --
confirming this is a deterministic, reproducible failure of this
environment's fpylll/fplll build against this class of instance, not a
transient flake.

**Bounded root-cause diagnostic (out-of-band, NOT counted in the Stage-0
timing budget above, disclosed in full in `environment.json`
`stage0_infrastructure_finding`):**
- `float_type="mpfr"` (arbitrary precision GSO): **also failed**, with the
  identical exception, essentially instantly. This rules out a simple
  default-floating-point-precision explanation.
- `float_type="dd"` / `"qd"`: **not available** in this fpylll/fplll build
  (`ValueError: Float type '...' unknown`).
- `float_type="long double"`: **inconclusive** -- ran over 600s without
  erroring or completing, then was deliberately killed to stop it
  competing for this host's 4 vCPUs with the still-running official
  Stage-0 subprocess (avoiding contamination of the official wall-clock
  numbers above). Whether it would eventually have succeeded is not
  determined.
- No further remedy (different LLL delta, different strategies file,
  alternate fplll build) was attempted: PREREG-8 section 1 explicitly
  prohibits any hand-rolled BKZ substitute "under any circumstance," and
  further tuning of fplll's own internals is outside this task's own
  scope (measure Stage-0 feasibility, not repair infrastructure).

**Assessment (observation, not interpretation of C1/C2):** this looks like
a genuine incompatibility between this host's fpylll 0.6.4 / fplll build
and BKZ's own internal LLL preprocessing at `d in {256, 512}` on this
class of q-ary lattice (`IntegerMatrix.random(d, "qary", k=d//2, q=3329)`),
independent of `beta` (all three values fail identically) and largely
independent of `d` (both 256 and 512 fail, at somewhat different but not
qualitatively different wall-clock-to-failure). It is NOT resolved by the
one alternative precision setting that could be tested to a definite
result. This is squarely `infrastructure_error` per AGENTS.md rule 5 and
the Executor failure taxonomy -- never fabricated as, or silently folded
into, a finding about C1 or C2.

### 2.2 Toy-floor sweep (8f8f45's own control, cap = 900s per point)

Exhaustive search over the CBD(eta=2) alphabet at toy `d`, timing only
(see writeup discussion of the eta/beta_toy interpretation below).

| d | outcome | elapsed | points evaluated | fraction of alphabet |
|---|---|---|---|---|
| 8 | **COMPLETED** | 0.73s | 390,625 / 390,625 | 100% |
| 12 | **COMPLETED** | 251.0s | 244,140,625 / 244,140,625 | 100% |
| 16 | **NOT_COMPUTED** (cap exceeded) | 900.3s | partial (see stage0_results.json) | <100% |
| 20 | **NOT_COMPUTED** (cap exceeded) | 900.4s | partial (see stage0_results.json) | <100% |

**Selected toy-floor d = 12** (largest that completed within
`TOY_FLOOR_FEASIBILITY_CAP=900s`), per PREREG-8 section 2.3's own decision
rule.

**Protocol interpretation, flagged (PREREG-8 does not pin these down and
this executor's own reading is stated explicitly, not silently
substituted for the frozen text):**
- **eta = eta2 = 2** was used for the exhaustive alphabet (the error
  term's own CBD parameter under this protocol's scope), not eta1=3 (the
  secret/r parameter) -- read as the more literal match to
  `R = ||pi(e)||^2 / ||e||^2`'s own "e." A different reading (eta1=3, a
  larger 7-value-per-coordinate alphabet) would give slower, more
  conservative timings and might shift the selected d downward.
- **beta_toy = d // 2** was used for each toy sub-cell's own basis.
  PREREG-8 does not specify a beta for the toy-floor arm at all (only the
  main grid's beta values are pinned). Since the exhaustive search's own
  asymptotic cost is `O((2*eta+1)^d)`, driven by `d` and `eta`, this
  choice does not materially change the FEASIBILITY timing this sweep
  exists to measure, but IS a choice this document is making, not one
  PREREG-8 made.
- The reported `r_min_over_evaluated_subset` values (0.00173 at d=8,
  0.00100 at d=12) are exact combinatorial minima ONLY at d=8 and d=12
  (100% of the alphabet was evaluated at both); the NOT_COMPUTED entries
  for d=16/20 record a partial-search value explicitly labelled as such,
  never presented as an exact floor.
- This is Stage-0's own **feasibility timing measurement**, not Stage 1's
  own headline floor-test result -- no claim about C2 (floor confirmed /
  no floor / collision) is made here; PREREG-8 section 2.2's own text
  scopes this sweep to "report exhaustive-search wall-clock ... before
  committing to a specific d," which is exactly what is reported.

### 2.3 Termination branch

`n_cells_cleared = 0` (of 6). Per PREREG-8 section 2.3: "If EVERY cell is
dropped, `T-PROJNOISE-NODATA` fires for the WHOLE package; Stage 1 does
not run at all." Every one of the 6 main-grid cells failed to reach a
completed reduction -- none via a cap timeout as section 2.3's own text
literally anticipates, but via a deterministic, reproducible,
cap-independent exception recorded as its own ERROR outcome. This still
satisfies PREREG-8 section 4.3 item 1(b)'s broader language ("Stage 0
drops every (n, beta) cell") and its own stated MEANS ("this attempt did
not produce usable data at the affected scope, for a reason OTHER than
the hypothesis's own content") exactly: the reason here (fpylll/fplll's
own internal LLL failure) has nothing to do with C1 or C2's truth.

**TERMINATION BRANCH: `T-PROJNOISE-NODATA` fires for the WHOLE package.**

Per PREREG-8 section 4.3 item 1's own LICENSES/FORBIDS:
- LICENSED: citing this task's own cell-by-cell Stage-0 benchmark results
  (the ERROR outcome and its exact exception, and the toy-floor sweep's
  own completed/NOT_COMPUTED results and selected d) as a standalone,
  reportable infrastructure-timing deliverable (R-PN-OUT-1). Done above.
- FORBIDDEN: any statement about C1 or C2's truth, in either direction, at
  any of the 6 cells. None is made anywhere in this document.

Section 3 (Stage 1) does **not** run, per PREREG-8 section 2.3's own rule
and this task's own explicit scope. `H-MLKEM-7d9bcc` is **not** advanced
to `analyzed` or any other status by this task (it stays `proposed`).

---

## 3. Executor's own recommendation (not a decision) for a later Stage-1 dispatch

This is a recommendation only, per this task card's own "Report, don't
decide" instruction; sizing and dispatching any follow-up is a separate,
later Coordinator act.

1. **Do not dispatch PREREG-8's own Stage 1 as written.** Stage 1 requires
   real BKZ-beta reduction at exactly the 6 `(d, beta)` cells that all
   failed here, for a reason (an fpylll/fplll-internal exception,
   independent of beta and largely independent of d) that a larger
   compute budget, more draws, or a smaller Stage-1 grid cannot fix --
   sizing is not the bottleneck; the reduction itself does not run at all
   on this environment's current fpylll/fplll build against this specific
   class of q-ary lattice instance.
2. **The blocking question for any follow-up is a genuine infrastructure
   root-cause investigation**, not a re-run of Stage 0 at different
   parameters: e.g., (a) filing/checking this exact exception against the
   fpylll/fplll upstream issue tracker for this version (0.6.4) and this
   `IntegerMatrix.random(d, "qary", k=d//2, q=3329)` construction; (b)
   testing an entirely different fpylll/fplll build or version (this task
   used whatever `pip3 install fpylll` resolved to on this host, `0.6.4`,
   pinned but not chosen for any particular fplll-version compatibility);
   (c) testing whether a different LLL delta or a different basis
   generation method (e.g. building the q-ary lattice by hand rather than
   via `IntegerMatrix.random`'s own "qary" mode) avoids the degenerate
   case that appears to trigger the internal Babai loop divergence. None
   of this was attempted here, consistent with PREREG-8's own explicit
   prohibition on any hand-rolled BKZ substitute and this task's own scope
   (measure, don't repair).
3. **If a fix is found**, a fresh Stage-0 re-run (a NEW task/run, this
   run stays in the ledger as-is, marked exactly as it is above -- run
   records are immutable) would still be warranted before any Stage-1
   commitment, since no cell in this run ever reached a measured
   wall-clock/tours/delta figure to size Stage-1's own budget from.
   PREREG-8 section 6's own budget derivation (section 6.1-6.3) remains
   exactly the wide-uncertainty ESTIMATE it always was; nothing in this
   task narrows it, because no cell produced a real number.
4. **The toy-floor sweep DID produce usable, real numbers** (d=8: 0.73s;
   d=12: 251.0s, both exact; d=16/20: capped, partial). If a later
   dispatch wants ANY real signal from this task while the main-grid
   infrastructure issue is being fixed separately, the toy-floor arm's own
   exact-floor computation (not attempted here -- Stage 0 only timed the
   sweep, per PREREG-8 section 2.2's own scope) could, in principle, be
   run independently of the main grid's own fpylll BKZ issue, since it
   uses only LLL/light BKZ at very small d (this task's own toy points
   used `beta_toy = d//2 <= 10`, far below the failing 40-70 range) --
   but this is itself a NEW, separately-commissioned task, not something
   this document authorizes.

---

## 4. Budget accounting

| component | cap | actual |
|---|---|---|
| fpylll install/verify | <=1800s | ~1.5s (prebuilt wheel; no from-source build) |
| CBD/compression re-derivation | <=120s | included in the 4.94s section-1 total |
| batched-vs-scalar Babai exactness | <=120s | included in the 4.94s section-1 total |
| 6 Stage-0 cells | <=3600s each | 70.2s-408.9s each (all ERROR, none near cap) |
| toy-floor sweep | <=900s each of 4 points | 0.73s, 251.0s, 900.3s (cap), 900.4s (cap) |
| **task wall-clock hard cap** | **25200s** | **~3466s Stage-0 script + ~5s section 1 + ~5s installs + writeup/manifest overhead; well under cap** |

No budget line was exceeded. No cell was retried at a different
beta/dimension after failing (per PREREG-8's own explicit prohibition).

---

## 5. Artifacts

- `infra_verification.py`, `infra_verification_results.json` -- section 1
- `stage0_feasibility.py`, `stage0_results.json` -- section 2 (present:
  the task card's own "only if section 1 clears" condition was met)
- `command.txt`, `stdout.log`, `stderr.log`, `run_manifest.yaml`,
  `environment.json` -- this task's own reproduction record
- `run_start_utc.txt`, `run_end_utc.txt` -- wall-clock boundary timestamps
  for the recorded Stage-0 script invocation
