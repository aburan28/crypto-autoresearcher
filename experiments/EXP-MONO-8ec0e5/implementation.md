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
