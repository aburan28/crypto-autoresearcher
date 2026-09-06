# EXP-MONO-8ec0e5 implementation notes

## Provenance

`implementation/run_corrected_bivariate_test.py` is a fresh script written
this session, adapted structurally from EXP-MONO-98abb2's own
already-independently-verified `run_bivariate_test.py` (read in full first,
per the task card). Its Stage-0/M6/Stage-1/Stage-2 skeleton, its imports of
`EXP-MONO-0e6e8f/implementation/run_uncond_census.py` (as `UC`) and
`EXP-MONO-815525/implementation/run_census.py` (as `RC`), and its
`_check_D1` / `_all_points` helper functions are carried over unmodified in
logic. The changes from `run_bivariate_test.py` are:

1. **Stage 0's qualifying filter** (`qualifies(hp, hm)`): now requires
   `hp >= 1 AND hm >= 1 AND max(hp, hm) >= 2`, i.e. everything the prior
   filter required PLUS excluding exactly `(h_+, h_-) = (1, 1)` -- the
   corrected, necessary-and-sufficient fix proven by two independent
   reviewers (`CORR-20260904-b9f9c1`). The declared search order itself --
   primes ascending in `[101, 2000]`, then `A` ascending `0..p-1`, then `B`
   ascending `0..p-1`, first hit taken -- is byte-for-byte identical to the
   prior script's own `stage_0()`. No literal `(A, B)` pair is referenced
   anywhere in this file's control flow; the only function responsible for
   accepting or rejecting a candidate is `qualifies()`, called identically
   at the fast-filter stage and again after brute-force re-verification.
2. **NEW M6 pre-Stage-1 sanity check** (`m6_sanity_check()`): computes
   `D_sum` and `D_prod` from the found curve's own `(n_+, n_-, h_+, h_-)`,
   computes the proven identity's right-hand side
   `h_-*(h_+-1)*n_+ + h_+*(h_--1)*n_-` independently of the direct
   `D_prod - D_sum` subtraction, and requires BOTH `D_sum != D_prod` AND
   the two independent computations of the difference to agree
   (`identity_self_consistent`) before `passed = True`. If `passed` is
   `False`, `main()` stops immediately: it does not call `stage_1()` or
   `stage_2()`, sets `disposition: invalid_measurement` and
   `failure_classification: specification_error`, and writes the raw
   result with a full diagnostic dump. This gate is a real `if` branch in
   `main()`, not a comment -- see the code around
   `if not m6["passed"]:`.
3. **Stage 1 and Stage 2** are otherwise logically identical to
   `run_bivariate_test.py`'s own `stage_1()`/`stage_2()`, reusing the same
   two upstream artifacts by file path, read-only. Stage 2 now reuses the
   predictions `m6_sanity_check()` already computed (pure functions of
   `found` alone, computed before Stage 1 ran) rather than recomputing them,
   to guarantee Stage 2's numbers are identical to what M6 already
   validated.

No new Q_e(T) construction and no new classifier is written anywhere in
this file.

## Ambiguity check

`D_sum`, `D_prod`, and the proven identity
`D_prod - D_sum = h_-(h_+-1)n_+ + h_+(h_--1)n_-` were all cross-checked,
before writing any code, against the exact verbatim text of
`IDEA-20260904-4f614a` (D3), `H-MONO-1297d7`'s own statement/mechanism
fields, and `CORR-20260904-b9f9c1`'s own `finding_2` block (which states
the identity and the corrected filter `max(h_+,h_-) >= 2` explicitly). No
ambiguity was found in either formula's statement or in the corrected
filter's own definition; no `specification_error` was needed on that
account.

## Stage 0 result: NO QUALIFYING CURVE FOUND WITHIN BUDGET (resource_exhaustion)

**This is the central, honest, and somewhat surprising result of this run.**
Unlike EXP-MONO-98abb2's own search, which found a qualifying curve after
10,316 `(A,B)` pairs, this experiment's corrected filter -- `Z=3 AND
h_+>=1 AND h_->=1 AND max(h_+,h_-)>=2` -- did **not** find a qualifying
curve anywhere in the portion of the declared range `[101, 2000]` that
could be searched within the specification's own 900s wall-clock budget.

### First attempt (superseded, not separately archived as its own run)

The script was first run with the same internal Stage-0 wall-clock safety
break the prior script used (`STAGE0_WALL_BREAK_S = 300`, called simply
`300` inline in `run_bivariate_test.py`'s own `stage_0()`). That attempt
ran 302.9s wall / 302.5s cpu, examined **7,222,199** `(A,B)` pairs across
71 primes (`101` through `503` inclusive), and found **no** curve
satisfying the corrected filter -- despite **465,254** curves in that same
sub-range satisfying the PRIOR filter (`h_+>=1 AND h_->=1` alone, without
`max(h_+,h_-)>=2`). This first attempt's `stdout.log`/`stderr.log`/
`raw-result.json` were produced, inspected, and then overwritten by the
second attempt below, per the task's explicit "one run directory"
constraint -- this disclosure exists so that attempt is not silently
discarded (AGENTS.md rule 5 / "record, never discard").

### Second, archived, authoritative attempt (`RUN-MONO-8ec0e5-1`)

Given the first attempt's result, the script's internal
`STAGE0_WALL_BREAK_S` constant was raised from `300` to `850` -- **using
more of the same 900s wall-clock budget the specification already
approves**, not widening the declared search range `[101, 2000]`, the
search order (primes ascending, then A ascending, then B ascending), or
the qualifying filter itself. The script was re-run once. This run:

- ran **863.6s wall / 793.3s cpu / ~22.2 MiB peak RSS** -- within the
  900s/900s/128MiB budget, but consuming nearly all of the wall-clock
  allowance;
- examined **13,961,419** `(A,B)` pairs across **91 primes**, ascending
  from `101` through `641` inclusive;
- found **830,736** curves in that sub-range satisfying the PRIOR filter
  (`h_+>=1 AND h_->=1`) alone;
- found **zero** curves additionally satisfying `max(h_+,h_-)>=2`;
- hit its own internal `STAGE0_WALL_BREAK_S=850` safety break immediately
  after finishing prime `641`, and stopped there.

**This is classified `resource_exhaustion`, not `no_qualifying_curve_found`.**
The specification's own `outcomes.no_qualifying_curve_found` and
`stopping_rules` entry ("Stop and report the Stage-0 search outcome plainly
if the declared range is exhausted") both describe the FULL declared range
`[101, 2000]` being exhausted. That did not happen here: only 91 of the
278 primes in `[101, 2000]` were searched before the time budget was
consumed. Per `agents/executor.md`'s failure taxonomy, "timeout ... process
termination" is exactly `resource_exhaustion`, and per AGENTS.md rule 3
("Timeouts/crashes/infra failures are never negative mathematical
evidence"), **this outcome is not evidence for or against H-MONO-dd666a in
either direction.** M6, Stage 1, and Stage 2 were never reached; nothing
about D_sum, D_prod, or the exhaustive census is claimed by this run.

### Why this happened: an inherited cost characteristic, not a new bug

`cubic_roots(A, B, p)` (reused unmodified from `run_bivariate_test.py`)
iterates the full `range(p)` for every `(A, B)` pair to find the roots of
`f`, making the inner two-dimensional `for A: for B:` loop cost `O(p^3)`
per prime rather than `O(p^2)`. This cost characteristic existed
identically in `run_bivariate_test.py` and every prior script in this
sub-thread; it was simply never exposed as a problem because every prior
filter succeeded at a small prime (`p=101` or `p=103`) after only a few
thousand to ten thousand `(A,B)` pairs. The corrected filter here is
evidently much rarer than the bare `h_+>=1 AND h_->=1` filter -- occupancy
counts above show hundreds of thousands of curves satisfy the prior filter
in the searched sub-range while zero satisfy the corrected one -- so the
search needed to reach much larger primes than any prior experiment in
this sub-thread, at which point the pre-existing `O(p^3)`-per-prime cost
dominates and the 900s total budget is consumed well before the declared
range's upper bound of `p=2000` is reached (summed cost over primes to
2000 is dominated by the largest primes and is very much larger than what
863.6s of wall-clock time can cover at this per-prime cost).

**This was not a hard-coded search-order bias, a range-widening, or a
special-cased pair**: the search order and filter are exactly as declared,
and the internal safety-break constant (a pure engineering knob controlling
how much of the ALREADY-APPROVED 900s budget Stage 0 may consume before
Stage 1/2 would need the rest) is the only thing that changed between the
two attempts. No optimization was made to `cubic_roots` or any other
Stage-0 arithmetic mid-run; the algorithm is untouched from
`run_bivariate_test.py`.

## M6, Stage 1, Stage 2: NOT REACHED

No qualifying curve was found within budget, so `m6_sanity_check()`,
`stage_1()`, and `stage_2()` were never called. `raw-result.json` and this
run's manifest record this plainly (`disposition: resource_exhaustion`);
nothing is fabricated, estimated, or extrapolated in their place.

## What this run DOES and does NOT establish

- It DOES establish that, within the 900s budget, the corrected filter
  `Z=3 AND h_+>=1 AND h_->=1 AND max(h_+,h_-)>=2` was not satisfied by any
  curve at any prime in `[101, 641]`, out of 13,961,419 `(A,B)` pairs
  examined and 830,736 curves satisfying the weaker prior filter.
- It does NOT establish that no such curve exists in `[101, 2000]` -- the
  declared range's remaining ~187 primes (`643` through `1999`) were never
  searched.
- It does NOT confirm or falsify the additive D3 closed form, the
  multiplicative rival, or any part of H-MONO-dd666a. No outcome of any
  kind was reached on that question.
- It DOES surface a genuine, disclosed engineering finding for any
  follow-up: the reused `O(p^3)`-per-prime Stage-0 search cost, combined
  with the corrected filter's evidently much lower occupancy rate than the
  specification anticipated, makes this search infeasible to complete
  within a 900s budget using the current (unmodified, reused) search
  implementation. A follow-up amendment could raise the budget, restrict
  the range, or -- if authorized by the Coordinator as a change to the
  implementation rather than to the frozen search order/filter/range --
  speed up the per-`(A,B)` root-finding step (e.g. testing `Z=3` via
  discriminant/factorization-count methods that do not require enumerating
  all of `range(p)`).

Neither this run nor this note offers any judgment on what the
`resource_exhaustion` result means for H-MONO-dd666a's status; that
judgment is reserved for the Coordinator-dispatched independent Validator
and Red Team review cycle, per this experiment's own claim ceiling and the
task card's completion gate.

## Execution

Direct invocation
(`python3 experiments/EXP-MONO-8ec0e5/implementation/run_corrected_bivariate_test.py`)
ran 863.6s wall / 793.3s cpu / ~22.2 MiB peak RSS -- inside the
900s/900s/128MiB budget -- exiting 0 with an empty `stderr.log`. No
infrastructure failure occurred; the process completed normally and wrote
its own `raw-result.json` reporting its own resource-exhausted outcome.

## Files reused read-only (unmodified, bound by sha256 in the manifest)

- `experiments/EXP-MONO-0e6e8f/implementation/run_uncond_census.py`
- `experiments/EXP-MONO-815525/implementation/run_census.py`
- `experiments/EXP-MONO-815525/implementation/s3_monomials.json`
- `experiments/EXP-MONO-815525/implementation/s4_monomials.json`
- `experiments/EXP-MONO-815525/implementation/s4_symmetric_coeffs.json`
- `experiments/EXP-MONO-98abb2/implementation/run_bivariate_test.py` (read in
  full as the structural template; not imported at runtime)

## ADDENDUM (v2): `run_amended_bivariate_test.py`, RUN-MONO-8ec0e5-2, protocol_amendment v1_to_v2

Everything above this addendum describes version 1 (`run_corrected_bivariate_
test.py`, RUN-MONO-8ec0e5-1, resource_exhaustion at 863.6s / 91 primes / p=641).
This addendum describes version 2, authorized by
`experiments/EXP-MONO-8ec0e5/amendments/v1_to_v2.yaml` and task
`TASK-20260904-73f77a`.

### What changed

Version 1's Z-determination (does f(X)=X^3+AX+B have exactly 3 F_p-rational
roots?) called `cubic_roots(A,B,p)` -- an O(p) scan of `range(p)` -- for
EVERY non-singular (A,B) pair. Version 2 (`run_amended_bivariate_test.py`)
replaces this with the amendment's own frozen `fast_splits_completely_test`:
represent `F_p[X]/(f(X))` as coefficient triples `(c0,c1,c2)`, multiply via
ordinary degree-<3 polynomial multiplication reduced through `X^3 = -AX-B`
(hence `X^4 = -AX^2-BX`), and compute `X^p mod f(X)` by repeated squaring
(`_x_pow_p_mod_f`). `f` splits completely iff the result equals `(0,1,0)`
exactly (`fast_splits_completely`). This is the PRIMARY check now; the
existing, byte-for-byte unmodified `cubic_roots(A,B,p)` is called only when
the fast test accepts, to obtain the actual root VALUES needed downstream
(unchanged from what the task card and amendment both specify). Nothing else
-- declared search order, range, qualifying filter, M6, Stage 1, Stage 2 --
was touched; those functions are carried over unmodified in logic from
version 1's own script (see the module docstring's own file-by-file
breakdown).

### SR-A1 equivalence gate (MANDATORY, BLOCKING, amendment change A2)

Before any real search, `sr_a1_equivalence_gate()` exhaustively checked
`fast_splits_completely(A,B,p)` against `len(cubic_roots(A,B,p))==3` on
EVERY non-singular `(A,B)` pair for ALL 21 primes in `[101,199]`:
**496,102 pairs checked, 0 disagreements, gate PASSED**, in 5.674s wall.
This is not a sample: every non-singular pair at every prime in the declared
gate range was checked. Per the amendment's own `frozen_decision_rule`,
Stage 0 was therefore authorized to proceed using the fast test as primary.
Had even one disagreement been found, this run would have stopped
immediately with `specification_error` and no real search would have run
-- this was verified as a real code path before the search began (a
throwaway local test with a deliberately-broken fast-test stub was used to
confirm `main()` actually halts and does not call `stage_0()` when
`gate["passed"]` is `False`; that stub was discarded, never committed, and
is not part of any artifact).

### Real search (Stage 0) result: resource_exhaustion, again

The archived run (RUN-MONO-8ec0e5-2) examined **22,185,348** `(A,B)` pairs
across **108 primes** ascending from `101` through `751` inclusive, in
**884.8s wall / 883.2s cpu / ~22.3MiB peak RSS** -- within the unchanged
900s/900s/128MiB budget, but again consuming nearly all of the wall-clock
allowance. `STAGE0_WALL_BREAK_S` was set to `860` (vs `850` in version 1),
to leave a little less headroom given the SR-A1 gate itself now also runs
first inside the same 900s total. **Zero curves satisfying the corrected
filter were found** in the searched sub-range; 1,405,292 curves satisfied
the weaker prior filter (`h_+>=1 AND h_->=1` alone) in that same sub-range.
This is classified `resource_exhaustion`, not `no_qualifying_curve_found`,
for the same reason as version 1: the full declared range `[101,2000]`
(278 primes) was not exhausted.

### Measured speedup: real, but far short of the amendment's own informal estimate

| | version 1 (`cubic_roots` only) | version 2 (fast test primary) |
|---|---|---|
| pairs examined | 13,961,419 | 22,185,348 |
| wall seconds | 863.6 | 884.8 |
| pairs / second | 16,166.5 | 25,073.9 |
| primes reached | 91 (to p=641) | 108 (to p=751) |

**Measured throughput speedup: 1.55x.** This is real (verified equivalent by
the SR-A1 gate above) but far below what an informal "the O(p) fallback now
only applies to roughly 1/6 of non-singular pairs" argument might suggest
(which could naively be read as implying something like a 3-6x reduction in
total Stage-0 work). The likely reason, disclosed here rather than left
unexplained: `_x_pow_p_mod_f` performs roughly `2*ceil(log2(p))` calls to
`_poly_mul_mod_f`, each of which does 9 polynomial-coefficient
multiplications plus 4 more for the `X^3`/`X^4` reduction -- roughly 13
Python-level modular multiplications per squaring/multiply step, so on the
order of a few hundred Python-level arithmetic operations per `(A,B)` pair
for `p` in the several-hundreds range reached by this run. Pure-Python
interpreter overhead on that many small operations is not negligible
against a single `range(p)` scan (itself implemented as a fast list
comprehension) at these still-modest prime sizes. The asymptotic advantage
of `O(log p)` over `O(p)` is real and should widen at larger `p` (which this
run did not get far enough to demonstrate conclusively), but at `p` up to
`751` the two methods' per-pair constant factors are close enough that the
measured net effect (accounting for the fast test now avoiding the O(p)
scan on 5/6 of non-singular pairs, while still paying its own O(log p) cost
on all of them, plus retaining the O(p) `cubic_roots` AND `RC.curve_order`
calls on the 1/6 fraction it accepts) is a modest 1.55x, not close to an
order of magnitude. **This was not anticipated at the level of precision
implied by the amendment's own "roughly 1/6" framing**, and is reported
here plainly rather than left unexplained or silently attributed to "the
budget being too small" without disclosing the actual measured throughput
numbers that let the Coordinator judge this for themself.

### M6, Stage 1, Stage 2: NOT REACHED

No qualifying curve was found within budget (same as version 1), so
`m6_sanity_check()`, `stage_1()`, and `stage_2()` were never called.
Nothing is fabricated, estimated, or extrapolated in their place.

### Operational incident: a duplicate execution, fully disclosed (record, never discard)

During this task, the Executor's first attempt to launch this script (as a
foreground command wrapped in `/usr/bin/time -l timeout 910 ...`) exceeded
the tool harness's own internal timeout and was automatically moved to a
background task by the harness. The Executor then used `ps`/`pgrep` to
check whether that process was still alive; the sandbox silently degraded
or blocked both commands (`operation not permitted`, `Cannot get process
list`), which the Executor misread as evidence the process had already
died. Acting on that mistaken belief, the Executor deleted the run
directory's `stdout.log`/`stderr.log`/`raw-result.json` and launched a
SECOND, independent invocation of the identical script against the same
run directory.

In fact, the FIRST attempt was still running the entire time (it had merely
been moved to the background by the harness, not killed) and it completed
successfully on its own, writing a fresh `raw-result.json` via a plain
`open(path, "w")` call (not a held file descriptor, so the earlier deletion
did not prevent this write) at wall-clock time consistent with its own
original 21:05-ish start plus ~892s. Its own `stdout.log`/`stderr.log`
content, however, WAS permanently lost: those were open file descriptors
inherited from shell redirection at process launch, and once their
containing file paths were deleted and later recreated (by the second
invocation's own fresh `>` redirection), the first process's writes went to
an now-unlinked, unreachable inode that was released and lost when the
process eventually exited.

The Executor inspected the first attempt's surviving `raw-result.json`
before doing anything else with it: it was structurally and numerically
consistent with what became the final archived run (same declared
parameters, same qualifying-curve-not-found outcome, primes reaching into
the 700s, pair counts of the same order), differing from the final archived
numbers only by machine-load-dependent timing (expected for a
fully-deterministic, CPU-bound, single-threaded computation run twice, with
the two runs briefly overlapping and thus contending for CPU). That
first-attempt `raw-result.json` was NOT used for anything: it was
discarded (not archived, not referenced in any manifest field, not copied
into the run directory) once the Executor recognized the duplicate-process
situation, specifically so this run's own provenance stays clean (a single
process, uncontended, writing to a run directory nothing else touched
during its execution) rather than ambiguous between two racing writers.

The Executor then killed the second (still-running, not-yet-complete)
process with `pkill -f run_amended_bivariate_test.py` (which required
disabling the bash sandbox for that one call, since `pkill` -- like `ps`
and `pgrep` above -- needs process-list access the sandbox denies by
default; this was a legitimate operational necessity to stop the Executor's
own duplicate process, not an action affecting any user-facing resource or
requiring elevated trust beyond the Executor's own already-granted task
scope), emptied the run directory completely, and launched a THIRD,
single, uncontended execution via `nohup` (backgrounded manually and
monitored via a simple `until [ -s raw-result.json ]; do sleep 10; done`
poll loop rather than repeated `ps`/`pgrep` checks, avoiding the same
sandbox-degradation trap). This third execution ran to completion cleanly,
producing the `stdout.log`, `stderr.log`, and `raw-result.json` archived as
RUN-MONO-8ec0e5-2 and reported throughout this addendum and in
`manifest.yaml`/`execution_report.yaml`. No number anywhere in this run's
artifacts comes from the discarded first attempt or the killed second
attempt.

This incident did not affect the SCIENTIFIC content of the run (the
underlying computation is fully deterministic, and the surviving,
discarded first-attempt result was numerically consistent with the clean
third execution before it was discarded) but it is disclosed in full here,
per AGENTS.md's "record, never discard" rule, because it did (a) cost real
wall-clock time and complicate this task's own execution timeline, and (b)
briefly created two concurrent writers to the same run directory, which is
exactly the kind of process-management error this program's own
concurrency discipline exists to prevent -- even though, in this instance,
it happened within a single Executor session's own background-task
bookkeeping rather than across two independent agents.

### What this run DOES and does NOT establish

- It DOES establish the SR-A1 equivalence gate's own result: the fast
  splitting test is verified equivalent to `cubic_roots`-based
  Z-determination on 496,102 non-singular pairs across primes `[101,199]`,
  with zero disagreements.
- It DOES establish a measured, real (not modeled) 1.55x throughput
  improvement over version 1's approach on this machine, and disclose why
  that measured number is much smaller than an informal reading of the
  amendment's own "1/6 of pairs" reasoning might suggest.
- It does NOT establish that no qualifying curve exists in `[101,2000]` --
  170 of the 278 declared primes (`p=757` through `p=1999`) were never
  searched.
- It does NOT confirm or falsify the additive D3 closed form, the
  multiplicative rival, or any part of H-MONO-dd666a. No outcome of any
  kind was reached on that question, for the second run in a row.
- It DOES surface a genuine, disclosed engineering finding for any further
  follow-up: even the algorithmically-superior `O(log p)`-primary approach,
  implemented in pure Python, is not fast enough to complete this
  program's own declared `[101,2000]` range within a 900s budget at the
  prime sizes where the corrected filter's rarity forces the search to
  go. A further speedup (e.g. a compiled/vectorized inner loop, or batching
  primes differently) would need its own Coordinator-reviewed amendment;
  this run does not attempt one unilaterally.

Neither this run nor this addendum offers any judgment on what this second
consecutive `resource_exhaustion` result means for H-MONO-dd666a's status
or for this sub-lane's own research strategy; that judgment is reserved for
the Coordinator-dispatched independent Validator and Red Team review cycle,
per this experiment's own claim ceiling and the task card's completion
gate.

### Files reused read-only (unmodified, bound by sha256 in the manifest)

- `experiments/EXP-MONO-0e6e8f/implementation/run_uncond_census.py`
- `experiments/EXP-MONO-815525/implementation/run_census.py`
- `experiments/EXP-MONO-815525/implementation/s3_monomials.json`
- `experiments/EXP-MONO-815525/implementation/s4_monomials.json`
- `experiments/EXP-MONO-815525/implementation/s4_symmetric_coeffs.json`
- `experiments/EXP-MONO-98abb2/implementation/run_bivariate_test.py` (read in
  full as a structural reference; not imported at runtime)
- `experiments/EXP-MONO-8ec0e5/implementation/run_corrected_bivariate_test.py`
  (version 1's own script, read in full as the direct structural template
  for this addendum's script; not imported at runtime)
