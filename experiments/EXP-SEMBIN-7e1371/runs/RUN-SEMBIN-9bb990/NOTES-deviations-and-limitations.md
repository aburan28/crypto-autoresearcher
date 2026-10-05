# RUN-SEMBIN-9bb990: protocol deviations, execution history, limitations

Written by the executing session as the run progressed. Every item is a fact
about how the measurement was performed, not an interpretation of it.

## Deviations from specification.yaml v1

1. **Draws.** The contract declares `draws_per_cell: 10` over five seeds. The
   exact solution counter ran on all 10 draws of every m = 2 window cell x
   subspace x B variant (40 instances per cell); the single-level degree-4 block
   ran on draw 0 of every cell x subspace x B variant; the degree-4 CLOSURE,
   which is the expensive instrument, ran on **two** draws per m = 2 cell and
   one draw per off-diagonal cell. A degree-4 closure costs about 3 minutes at
   N = 35 and 12 minutes at N = 40 on this host and grows with the square of the
   column count; 10 draws x 24 cells x 4 variants was not affordable.

2. **Draw selection for the closure is a declared rule, not a choice.** For each
   m = 2 cell, on the paper's Table 2 convention (low-degree-polynomial subspace,
   random B), the closure ran on the FIRST solution-free draw and the FIRST
   solution-bearing draw in the contract's draw order, as determined by the exact
   counter BEFORE any degree was measured. The rule is in
   `code/../../../tmp` scheduler `m2_sched.py`, reproduced in this package as
   `schedulers/m2_sched.py`. Both instances are reported; neither was selected
   after seeing a verdict.

3. **Subspace and B for the off-diagonal sweeps.** One variant only
   (low-degree-polynomial, B = 1) rather than all four, for cost. The contract's
   invalidation rule 4 binds the m = 2 window to the paper's convention and that
   is honoured there; the off-diagonal sweeps are internally consistent but do
   not vary the convention.

4. **Memory-capped closures.** The closure's accumulated basis alone occupies
   `ncols^2/8` bytes, so the cap is sized per cell and the largest cells were run
   alone. Cells whose degree-4 column count exceeds 200,000 were not attempted
   and are recorded `unreached_declared` WITH their column count, per the
   contract's stopping rule 2.

5. **F4 traces.** msolve 0.6.5 with explicit field equations does not complete at
   the m = 2 window on this host: at n = 40 it hit a 6 GB cap after 5 rounds
   (maximum step degree 3 seen) in 1538 s. Those traces are recorded unreached
   and are **not** evidence about d_F4. Where a completion IS affordable -- the
   smaller t >= 3 cells -- both instruments ran on the same bytes, which is the
   contract's `certificate_soundness` control.

6. **The `nearby_object` control degenerates at m = 2 and is reported, not
   simulated.** Eq. (4) at m = 2 is `S_3(x_1, x_2, R_X) = 0`, which is exactly
   eq. (5) at t = 2: the two systems are byte-identical (checked, see
   `code/eq4sys.py` and the smoke test in this package). The control is therefore
   informative only at m >= 3, which is where the contract's stopping rule places
   it.

7. **`S_5` and beyond are not implemented.** The eq. (4) control needs the
   summation polynomial `S_{m+1}`; `S_4` is built here as the Sylvester resultant
   of two copies of `S_3` and checked against the group law. `m >= 4` would need
   `S_5` and larger Sylvester determinants; those cells are recorded
   `not_implemented` and no verdict is claimed for them.

8. **The driver changed while the run was in flight, and the per-worker hashes
   say so.** `run_cert.py` gained `--draw-list`, `--no-single`, and the
   chained-system exact counter after the first workers had launched. The
   changes are additive -- no instrument's arithmetic was altered -- but a
   worker launched before a change did not see it, so the n = 40 closure took
   its `|V(I)|` from `count_m2.c` where later workers take it from
   `count_chain.c`. The two are independent programs that agree wherever both
   apply. `manifest.yaml` publishes `code_sha256_by_worker` and sets
   `code_changed_during_run: true` rather than flattening this to one hash.

9. **Two contract cells are not representable by the instrument at all.** Both
   M4RI instruments carry monomials as 64-bit masks (`closure_cert._csr` packs
   them into `array("Q")`), so `N > 64` overflows. `(12,6,6,3)` at `N = 66` and
   `(12,6,6,4)` at `N = 72` therefore have no certificate of either kind, and
   this is an INSTRUMENT LIMIT, not a memory cap: a bigger machine does not
   help, widening the mask is a code change. They are recorded with status
   `not_representable_instrument_limit`, their exact `|V(I)|` (which the chain
   counter computes regardless, since it indexes field elements rather than
   monomials), and their degree-4 column counts. Found by a crash --
   `OverflowError: int too big to convert` -- which took down the single-level
   pass after 22 of 24 cells; the driver now declares the limit instead of
   raising, and the two cells were re-run to record it.

## Instruments added beyond the contract's list

The contract names the degree-4 Macaulay certificate and a Groebner completion.
Two more were needed and are reported as first-class instruments:

- **Exact `|V(I)|` by enumeration** (`count_chain.c`, and `count_m2.c` as an
  independent second program at t = 2). The certificate's verdict is
  "standard monomials = |V(I)|", and at the m = 2 window no Groebner run
  completes on this host, so without an independent count every verdict in the
  region the experiment is about would read `undetermined`. Every equation of the
  chain is F_2-affine in the one unknown it is solved for, which makes the count
  exhaustive and cheap. The two programs agree wherever both apply, and both
  agree with msolve's quotient dimension wherever msolve completed.
- **The summation-polynomial identity check** (`sumpoly_check.py`): `S_3` and
  `S_4` are verified against the curve's group law (r points summing to O make
  the polynomial vanish; random x-tuples do not). Neither the closure nor F4
  would notice if the generator built the wrong polynomial.

## STOP: the degree-4 closure is UNSOUND on at least one measured instance

This is the run's most important result and it is a result about the
INSTRUMENT, not about Semaev. The contract anticipates it: stopping rule 4
says to stop the route and report a certificate/Groebner disagreement as a
refutation of the certificate method. The disagreement found here is with
EXACT ENUMERATION, which is stronger than a Groebner completion.

**The contradiction.** Cell `(43,2,2,22)`, low-degree-polynomial subspace,
random B, draw 0, system sha256 `8cca16b9a4365e5337219ad9a5f77be819c53b1f0ce565d9a07ed52dfec023b9`
(regenerated and verified byte-identical to the instance the worker ran):

  * two independent exhaustive counters (`count_chain.c` and `count_m2.c`,
    `cross_check_agrees: true`) report `|V(I)| = 2`;
  * both claimed solutions were substituted back and verified: each satisfies
    `S_3(x_1, x_2, z) = 0` over `F_{2^43}`, each has both coordinates in `V`,
    and each satisfies ALL 43 descended Boolean equations (0 violated);
  * the degree-4 closure on those same bytes reported `contains_one: true`,
    i.e. `1 in W_4`, i.e. no solutions, and the run recorded
    `verdict: sufficient, basis: 1 in W_D`.

A system with a common zero cannot have 1 in its ideal: every polynomial
combination of the generators vanishes at that zero. So the closure derived an
element that is not in the ideal, and the recorded verdict for this cell is
INVALID.

**A second defect, in the recording.** `closure_cert.closure_certificate`'s
`contains_one` branch sets `s = 0` and returns `sufficient` WITHOUT comparing
against `s_known`. The instrument therefore held the information needed to
detect its own failure -- an independently measured `|V(I)| = 2` -- and
discarded it. Every `1 in W_D` verdict in this run and in RUN-SEMBIN-b6eb9f
went through that branch.

**Direction of the bias, which is the part that matters.** If the closure's row
space exceeds the true degree-4 slice of the ideal, the rank is too high, so
the standard-monomial count is too LOW, so sufficiency is declared too
readily. The error therefore pushes toward CONFIRMING Assumption 1. An
instrument whose failure mode agrees with the hypothesis under test cannot be
used to support it.

**What survives, cell by cell.**

  * Verdicts decided by the standard-monomial route agree with an independent
    exact count and are corroborated: `(17,3,3,6)` std 6 = |V(I)| 6;
    `(19,3,3,7)` std 15 = 15; `(17,3,3,7)` std 42 = 42; `(13,4,4,4)` std 24 = 24.
  * Verdicts via `contains_one` at `(40,2,2,20)`, `(41,2,2,21)`,
    `(42,2,2,21)` and `(44,2,2,22)` are on instances the counter
    independently reports EMPTY, so their conclusions agree with the truth --
    but they were produced by the unsound path and are not independent
    confirmations of it.
  * `(43,2,2,22)` is the one confirmed-invalid verdict.
  * `(45,2,2,23)` was stopped mid-closure and wrote nothing.

**RUN-SEMBIN-b6eb9f (merged, PR #1264).** Eight of its nineteen `sufficient`
verdicts came through the same `contains_one` branch, and there `solutions: 0`
was set BY that branch rather than measured. All eight were re-checked here
with the exact counter: every one has `|V(I)| = 0`, so that run's conclusions
stand. It could not have caught this failure, having no independent count --
it was unverified, not wrong. A correction record against it is a Coordinator
act and is not written here.

**Root cause: NOT established, and the first published hypothesis is RETRACTED.**

The note originally committed here (and in PR #1268) proposed that the
multiplier degree is taken from the row's leading monomial while reduced rows
carry higher-degree terms, so products exceed `D` and are silently truncated by
`write_product`'s `if (c >= 0)` guard. **That hypothesis is wrong and is
withdrawn.** The column order in `closure.c` is DESCENDING by degree -- the
constant monomial sits at `ncols_ - 1`, which is exactly how `contains_one` is
tested (`is_pivot_[ncols_ - 1]`). Under a descending order the leading monomial
of a row is its HIGHEST-degree term, so bounding the multiplier degree by
`D - deg(leading)` keeps every term of the product within degree `D` by
construction. That is why the instrumented build reports ZERO dropped terms
everywhere it has been measured. The mechanism I named cannot be the cause.

Ruled out so far, each by measurement rather than by reading:

  * **Truncation.** `dropped_terms_above_D` is 0 at every solution-bearing
    instance measured, `N = 12, 16, 20, 24, 28, 34`, all of which also return
    `std = |V(I)|` exactly.
  * **`contains_one` detection.** It is `is_pivot_[ncols_ - 1]` after
    `mzd_echelonize(M, 1)`, i.e. reduced row echelon form, so a pivot in the
    constant column means that row's first nonzero IS the constant and the row
    is exactly 1. The monotone accumulation of `is_pivot_` is also sound,
    because the row space only grows across iterations.
  * **Batching.** On one fixed instance at `N = 28` with `|V(I)| = 2`, memory
    caps of 4.0, 0.5 and 0.1 GB all return `std = 2` correctly, and caps of
    0.03 and 0.01 GB report `unreached_memory_cap` rather than a wrong answer.
    The batched path degrades honestly.

Confirmed sound at `N <= 34`; confirmed unsound at `N = 44`. The onset in
between is not yet located: a scan over `N = 36, 38, 40, 42` on
solution-bearing draws was started twice and lost both times to the container
(one OOM, one restart), and is running again. The honest statement remains:
the instrument is demonstrably unsound at `N = 44`, demonstrably sound at
`N <= 34`, and the boundary and the mechanism are unknown.

**ROOT CAUSE FOUND: M4RI's `mzd_echelonize` returns rows outside the row
space of its input.**

Method (`-DECH_EVALCHECK` build of `closure.c`). A verified common zero of the
generators is a linear functional that every element of the ideal vanishes on,
and row reduction only forms linear combinations of its input. So for every
elimination call the build counts the rows that do NOT vanish at the zero,
before and after. `in > 0` would blame our product code; `in = 0, out > 0`
blames the elimination routine. Validated on a known-good instance (N = 20:
every call `in=0 out=0`, correct verdict) and against a deliberately wrong
witness (flags 15 violating generators at the first call), so a clean reading is
not vacuous.

On the failing instance (43,2,2,22), N = 44, |V(I)| = 2, witness verified
against all 43 generators, default `mzd_echelonize(M, 1)`:

    [ech 0]     43 x 149986  rank     43 | in=0 out=0
    [ech 1]  55857 x 149986  rank  51952 | in=0 out=0
    [ech 2] 199768 x 149986  rank 139898 | in=0 out=68559  *** ELIMINATION LEFT THE IDEAL ***

All 199,768 input rows of elimination 2 vanish at the zero -- every one is a
genuine ideal element. 68,559 of the 139,898 output rows do not. A linear
combination of vanishing rows vanishes, so those rows are not in the row space
of the input: the routine is wrong on this matrix, not our code. This is where
the spurious `1 in W_4` at (43,2,2,22) came from. Log preserved as
`evalcheck44_default_FINDING.log` in the session scratchpad and reproduced
here.

**Localised further: the fault is in `mzd_echelonize`'s hand-off, not in
PLE.** The same instance, same witness, with the routine switched to
`mzd_echelonize_pluq` (PLUQ throughout):

    [ech 0 pluq]     43 x 149986  rank     43 | in=0 out=0
    [ech 1 pluq]  55857 x 149986  rank  51952 | in=0 out=0
    [ech 2 pluq] 199768 x 149986  rank 129376 | in=0 out=0

Elimination 2 is clean under PLUQ, on the identical input matrix, with rank
129,376 against the default's 139,898. The default overstates the rank by
10,522: those surplus pivots are rows outside the ideal, and they are what
manufactured `1`. Both routines agree on elimination 1 (rank 51,952), so they
coincide where the default is correct. `mzd_echelonize` starts with the Method
of Four Russians and passes the trailing block to PLE once its density exceeds
0.15; since PLE alone is correct here, the defect lies in that hand-off.
Indicated fix for the instrument: call `mzd_echelonize_pluq(M, 1)` instead of
`mzd_echelonize(M, 1)`. (That run was lost to a container restart after
elimination 2; it was relaunched to obtain the verdict.)

Installed library: libm4ri 20200125 (Ubuntu 24.04), single-threaded (no OpenMP
symbols), so the failure is deterministic and reproducible from the instance.

Consequences for the records, stated before anything is re-measured:

  * Every closure verdict in this run and in RUN-SEMBIN-b6eb9f was computed with
    this routine. The error inflates the row space, which lowers the
    standard-monomial count and pushes toward `sufficient` -- the direction
    that agrees with Assumption 1.
  * Verdicts whose standard-monomial count equals an INDEPENDENT exact count
    (std 6, 15, 24, 42) are internally consistent; a corrupted basis would
    typically undercount and trip the impossibility branch, so those are not
    known to be affected -- but they are not re-verified either until re-run on
    a correct routine.
  * `contains_one` verdicts on empty varieties cannot distinguish a correct
    derivation of 1 from a corrupted one, and are UNVERIFIED.
  * msolve results are unaffected (different code).

**Further eliminations (later session), each by direct test:**

  * **Memory safety.** An AddressSanitizer + UndefinedBehaviorSanitizer build
    of `closure.c` runs clean through full closures at N = 12, 20 and 24, and
    through forced multi-batch streaming at N = 20 (a 0.02 GB cap, correct
    `std = 4 = |V(I)|`; a 0.005 GB cap reports `unreached_memory_cap` rather
    than a wrong answer).
  * **Scratch-buffer overflow.** `tmp` and `rbuf` are allocated `ncols_ + 1`
    entries -- enough for the longest possible row -- so the jump from
    generator-length rows (iteration 1) to basis-length rows (iteration >= 2)
    cannot overflow them.
  * **Iteration 1 at N = 44.** `soundness_probe.py` (runs the closure for k
    iterations, then evaluates every basis row in C at a verified common zero):
    after iteration 1 on the failing instance the rank is 41,415 and every row
    vanishes at the zero. The corruption enters at iteration 2 or later.
    Iteration 2 alone outlasted the harness's background time limit and was
    killed without a result.

**Current suspect: M4RI's own elimination.** `mzd_echelonize(M, 1)` begins
with the Method of Four Russians and switches to PLE decomposition once the
trailing block passes density 0.15 (`echelonform.h`). A report titled "A bug
with mzd_ple()" (M4RI Bitbucket issue #74) describes wrong PLE output on large
GF(2) matrices in 20200125, the installed version; the page is no longer
reachable, so it is a lead and is not cited as evidence. The installed library
exports no OpenMP symbols, so it is single-threaded and any disagreement it
produces is deterministic.

Test, in situ rather than on synthetic matrices: every elimination in
`closure.c` now goes through `ech()`. A `-DECH_CROSSCHECK` build also runs pure
Four Russians (`mzd_echelonize_m4ri`) on a copy and compares the reduced row
echelon forms word by word -- RREF is unique for a row space, so any
difference proves one routine wrong -- logging each call as it completes. A
standalone harness found all three M4RI routines in agreement on random
matrices up to 80,000 rows, full-rank and rank-deficient, so synthetic inputs
do not provoke it and the real matrices are the test that matters. The
cross-check validated at N = 20 (four eliminations, including one of
83,856 rows, all agreeing, correct verdict) and was launched on the failing
N = 44 instance.

The next diagnostic that would settle it, once the onset N is known, is direct
rather than inferential: extract the final basis rows with
`closure_row_masks` and evaluate each at the known solution. Any row that does
not vanish there is not in the ideal, and it identifies which row and which
iteration introduced the error.

All schedulers and workers were stopped when the contradiction was confirmed.

**Fix applied to the instrument (commit fc186e394b, PR #1532).** `ech()` now
calls `mzd_echelonize_pluq(M, 1)` by default; `-DECH_LEGACY` restores
`mzd_echelonize` solely to reproduce this run. Every closure and single-level
Macaulay result now records `elimination`, so no verdict is ever separated
from the routine that produced it. Wording correction to the paragraph above:
what was tested is `mzd_echelonize_pluq` (M4RI's PLUQ path), not PLE in
isolation; "the defect lies in the hand-off" is the most specific reading the
two runs allow, not a localisation inside M4RI's source.

**Re-verification under PLUQ (in progress, nothing here is final).** Every
`completed` closure and single-level Macaulay measurement in this run is being
re-run on the rebuilt library, cheapest first, and compared on rank, column
count, `contains_one`, standard monomials, verdict and the leading-monomial
hash (`scratchpad` script `regress.py`; its output will be committed with this
package). First pass: 140 measurements re-run, 0 disagreements; the remaining,
more expensive ones are paused while the N = 44 run below holds ~9 GB. The
records in this directory remain the legacy-routine measurements and are not
edited; the PLUQ re-measurement is a separate artifact.

The N = 44 verdict under PLUQ with the evaluation check on (every elimination
checked at the verified zero) is running; it is reported here only when it
completes.

**PLUQ is NOT a fix: it fails too, on the same library (later session).** The
full N = 44 run under `mzd_echelonize_pluq` (M4RI 0.0.20200125, evaluation
check on, per-batch memory sizing) was clean through seven eliminations, then:

    [ech 7 pluq] 148601 x 149986 rank 139204 | in=0 out=66598  *** ELIMINATION LEFT THE IDEAL ***
    [ckpt] pivot count 131030 != rank 139204; checkpoint NOT written

The output claims rank 139,204 with only 131,030 distinct leading columns, so
it is not even in echelon form. The run went on to report `std = 127628,
verdict = insufficient`. **That verdict is void** -- it is computed from a
basis that is not an echelon form of any subspace of the ideal -- and it is
recorded here only as the failure it is.

**The defect is in M4RI 0.0.20200125 and is fixed upstream.** M4RI built from
`release-20240729` (git, `--disable-openmp`; its `make check`: 15/15 pass) and
replayed on the identical failing configuration -- legacy batch sizing,
3.5 GiB cap, default `mzd_echelonize`, evaluation check on:

    [ech 0 default]     43 x 149986  rank     43 | in=0 out=0
    [ech 1 default]  55857 x 149986  rank  51952 | in=0 out=0
    [ech 2 default] 199768 x 149986  rank 129376 | in=0 out=0

Same matrix that gave rank 139,898 and 68,559 non-vanishing rows on
0.0.20200125; on 20240729 it gives 129,376 -- the rank PLUQ gave on that
matrix -- and no bad rows. The candidate fix is upstream commit `34b1b56`
(2020-05-14, "fix count for remaining number of rows in a block", fixes M4RI
issue #74 "A bug with mzd_ple()"): it corrects `mzd_remaining_rows_in_block`
for row windows (`row_offset`) into multi-block matrices, which is the regime
of every elimination found unsound here (>= 148,601 rows of 18.7 KB, far past
one block) and of the PLE recursion both failing routines share. That
attribution is NOT yet isolated: 58 commits separate the two releases, and the
test that would settle it is 20200125 plus that one commit, against
20200125 built from the same source as a control.

**Instrument changes (code, this session):**
  * `ech()` validates every output structurally -- leading columns strictly
    increasing, reduced, rows past the rank zero -- and `closure_run` checks
    that no previous pivot is lost. Either failure stops the run with rc 2
    (`error`), never a verdict. This would have stopped the PLUQ run above.
    It cannot see a wrong matrix that is still well formed; the evaluation
    check can, but only where a common zero is known.
  * The library actually loaded is resolved at run time (`dladdr` on
    `mzd_init`) and recorded with every result as `m4ri_library`;
    `make M4RI_PREFIX=...` links a non-system M4RI with an rpath.
  * Memory: batches sized per batch from the live rank, counting the basis,
    the dense copy of the rows being multiplied, and PLUQ's ~r^2/8 workspace.
  * Checkpoint / resume (`CLOSURE_CKPT_DIR`), tested by SIGKILL at three
    points against an uninterrupted run.
  * Single-level Macaulay rank no longer stops at 1 (truncated ranks when the
    block needed several batches; RUN-SEMBIN-9bb990 itself not affected).

**Consequence for this run's records.** Every closure and single-level
measurement in RUN-SEMBIN-9bb990 was computed on M4RI 0.0.20200125 with
`mzd_echelonize`. Agreement with the PLUQ re-runs (same library) does not
clear them, since PLUQ shares the defect. They must be re-measured on a fixed
library before any of them is used; until then each is UNVERIFIED, and the
N = 44 contradiction stands as the demonstration that the defect reaches
verdicts.

## Execution history (host: 4 cores, 15 GB cgroup)

- Phase 1 ran two closure lanes concurrently (the m = 2 window and the
  off-diagonal sweeps) alongside the light single-level pass and the
  certificate-soundness control. The container SIGKILLed the m = 2 lane 1775 s
  into the `(40,2,2,20)` draw-1 closure (wrapper exit -9). **Nothing partial
  reached the record**: `run_cert.measure` emits an instance's records only
  after every instrument on it returns, so the kill cost wall-clock, not data,
  and the directory contains exactly the completed draw-0 instance. Under
  AGENTS.md rule 3 the kill is an infrastructure failure and is not evidence
  about that cell.
- Diagnosis: the two lanes had converged on the same cell. `closure_sw_n19k7`
  and `soundness_n19k7` were both measuring `(19,3,3,7)` draw 0 on the same
  subspace and B, at 3.7 GB each, while the m = 2 lane wanted 6 GB. The sweep
  lane was stopped -- the soundness worker produces the same closure plus an F4
  trace -- and the remaining sweeps moved to a phase-2 schedule that admits ONE
  heavy closure at a time (`schedulers/phase2_sched.py`): it waits until no
  other `run_cert` process holds more than 1.5 GB, and raises the free-memory
  margin from 1.5 GB to 2.5 GB above the cell's own basis and cap.
- The killed instance, `(40,2,2,20)` low-degree subspace, random B, draw 1, is
  re-queued in phase 2 as the first job and is run alone.

## Cross-reference to RUN-SEMBIN-b6eb9f at the first off-diagonal cell

Stated here as a fact about an existing committed record, not as an inference.
`EXP-SEMBIN-c2c312`'s heavy pass completed an msolve F4 trace at
`(17,3,3,7)` -- one unit above the diagonal `k = ceil(17/3) = 6` -- on the
low-degree-polynomial subspace with `B = 1`, seed `20260913001`, draw 0:

    status completed, d_F4 (Semaev reading) 4, naive reading 4,
    quotient dimension 18
    (experiments/EXP-SEMBIN-c2c312/runs/RUN-SEMBIN-b6eb9f, heavy pass)

This run's degree-4 certificate at the same cell on seed `20260913101`, draw 0,
returns sufficient with standard monomials 42 against an exact `|V(I)| = 42`.
Different seeds, so different systems; different instruments; different runs.
What the pair supports and whether it bears on the paper's Section 4.5.1
sentence is for the review stage, not for this report.

## Derived, non-measured artifact

`crypto-scale-arithmetic.json` is arithmetic on the paper's own formulas: the
degree-4 column count at the FIPS parameters, and Table 3's stage-1 cost under
the two readings the paper itself contains -- `n^{4w}` (the block-structured
solver of Section 4.5.2, which the paper never implements) and `[n(m-1)]^{4w}`
(what the same section derives for F4 itself, and F4 is what Tables 1-2 measure).
It is NOT a measurement, NOT an extrapolation of one, and it is evidence for
nothing about Assumption 1. The block-structured caveat is already recorded in
`knowledge/literature/KN-LIT-fa346d.md`; what is added here is the number.

## Limitations stated by the executor

- Scale. The largest cell measured is on the m = 2 diagonal. The paper's
  conclusion needs n = 409 and 571 at m = 11 and 12. Nothing here transfers
  there, and no transfer is claimed.
- The m = 2 window is a five-point window in n at ONE m. Growth in m is
  untouched beyond m = 6 at n = 12.
- A cell whose certificate did not complete is unreached, never insufficient.
- The exact counter is exact for the systems it enumerates and says nothing
  about Groebner behaviour; it is the denominator of the verdict, not a measure
  of degree.

## N = 44 verdict on a fixed M4RI (later session)

(43,2,2,22), N = 44, D = 4, seed 20260913101, draw 0, |V(I)| = 2 (exact
count), on M4RI 0.0.20240729 built from git (`m4ri_library` recorded),
`mzd_echelonize_pluq`, evaluation check at a verified common zero on EVERY
elimination, structural output check on, per-batch memory sizing at 9 GiB,
checkpointing on:

    DONE  status=completed  contains_one=False  std=2  |V(I)|=2  verdict=sufficient

  * 39 eliminations logged, every one `in=0 out=0`; no structural fault.
  * Rank path: 43 -> 51,952 -> 129,383 -> 130,913 -> 139,204 -> 144,020 ->
    149,984 = ncols - 2, then constant through iterations 4-6 (no new
    pivots), so the closure saturated with exactly |V(I)| standard monomials.
    Rank 139,204 at the 148,601 x 149,986 elimination is the genuine value:
    0.0.20200125 reported the same number on the same-shaped matrix with
    66,598 rows outside the ideal and a non-echelon output.
  * One container restart during iteration 6; the run resumed from its
    checkpoint (iteration 6, row 5553 of 5964, rank 149,984) and finished.
    `DONE 12842s` is the post-resume wall time only; the total is not
    recorded as one number.
  * Logs (`m4ri_defect_investigation/`): this run; the 20240729 replay of the
    original failing configuration; both 0.0.20200125 failures; the
    checkpoint kill/resume test.

**Status of this number.** It supersedes, as a diagnosis, the contradictory
N = 44 verdict this run recorded on 0.0.20200125: that verdict came from rows
outside the ideal. It is one instance at one (n, m, D). The evaluation check
uses one of the two common zeros and is a necessary condition for soundness,
not a proof; the structural check sees only malformed output. It is not part
of this run's frozen cell set as measured, and is evidence for nothing until
independently reviewed. The other closure and single-level records here remain
UNVERIFIED until re-measured on a fixed library.
