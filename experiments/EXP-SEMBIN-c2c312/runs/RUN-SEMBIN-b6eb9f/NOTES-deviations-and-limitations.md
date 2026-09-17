# RUN-SEMBIN-b6eb9f: protocol deviations, execution history, limitations

Written by the executing session as the run progressed; every item is a fact
about how the measurement was performed, not an interpretation of it.

## Supersession

This run supersedes `RUN-SEMBIN-595308`, whose directory holds the interim
snapshots that were committed while workers were still writing (a violation of
the append-only rule once they reached `main`). Its raw partial records
(controls, the (15,5,3,3) cell, the first memory-cap failures) remain there as
outputs of failed and partial attempts. Nothing in it is edited; a
superseded-by note was added.

## Deviations from specification.yaml v1 (all for cost, none for content)

1. **Draws.** 5 draws per (cell, subspace, B) instead of 20, one per declared
   seed (draw d uses seeds[d]). The contract's 20 x 8 cells x 4 variants = 640
   instances would have cost an estimated 30+ hours of msolve time on this
   host; the seed list itself is the contract's.
2. **Closure instrument on draw 0 only** (`--closure-draws 1`), while the F4
   trace and the single-level Macaulay rank ran on every draw. A degree-4
   closure costs 4 minutes at N = 35 and 40 minutes at N = 42 on this host.
3. **Field-equation convention.** No Boolean-ring F4 engine (PolyBoRi/BRiAl,
   MAGMA) is available, so the `engine_implicit` convention is measured only
   by the closure and single-level instruments (which work in the Boolean
   ring, squarefree monomials, x^2 = x implicit) and the `explicit_generators`
   convention only by msolve. The two conventions are therefore confounded
   with the two instruments; the contract listed the convention as an
   independent variable and it is not separately varied here.
4. **Memory-capped F4 traces.** msolve with explicit field equations exceeds
   7 GB on every cell with N >= 38 variables ((13,4,4,4) N=42, (17,3,3,7) N=38,
   (17,3,3,8) N=41, (19,3,3,7) N=40, (21,3,3,7) N=42): the exponent-vector /
   hash tables grow past 2^25-2^26 entries. These traces are recorded as
   `unreached_memory_cap` (with the rounds completed before the cap, every one
   at step degree <= 4) or `unreached_declared` (deferred), and re-attempted
   one at a time in the heavy pass with a larger cap where the host allowed.
   An unreached trace is not evidence about d_F4 at that cell.
5. **Closure D = 5** was never attempted where the degree-5 column count
   exceeded the cap (N >= 35: 384k+ columns); the closure decided at D = 4 on
   every measured chained instance, so D = 5 was not needed for the verdict.
6. **Single-level Macaulay at D = 4** was not computed for the (12,6,6,2)
   cell (N = 60, 523,685 columns > 200,000 cap); D = 3 was.
7. **Instrument-identity control** compares the F4 round profiles without
   msolve's printed timings and the closure profiles by (D, rank, leading
   monomial hash, per-iteration rows/rank); it was run on the first instance
   of each reproduction cell. Where the F4 trace was deferred on that cell,
   the F4 half of the control is recorded as null, not as a pass.

## Execution history (host: 4 cores, 15 GB cgroup)

- Two concurrent workers (A: reproduction + off-diagonal, B: separation), 7 GB
  msolve cap each. Worker A was OOM-killed by the container at 9.7 GB RSS
  during the (13,4,4,4) degree-4 closure while worker B held 5.8 GB in its
  own closure; M4RI's working memory is roughly twice the dense-matrix
  estimate the batch cap bounds. Worker A was relaunched with a 3 GB closure
  estimate cap (`--closure-mem-cap`), which kept its peak near 6 GB.
- A relaunch of worker B briefly ran twice on the same directory (pids 9160
  and 9336); both appended to `workerB/cells/results.jsonl`. The duplicate
  (instance, instrument) records are resolved by `summarize.py` (first
  completed record wins) and counted in `summary.json`.
- Worker B was stopped deliberately when free memory fell to 1 GB with two
  large closures in flight; its F4 traces and single-level records were
  complete, and its remaining closures ((19,3,3,7) random-subspace/random-B
  draw 0, (21,3,3,7) draw 0 x 4) moved to the heavy pass.
- Worker C measured the off-diagonal cells' F4 traces (unreached at N = 38)
  and single-level ranks.
- The heavy pass (single process) re-attempted the deferred F4 traces and
  closures; its records live in `heavy/cells/` and are folded into the base
  instances by `summarize.py`.

## Limitations stated by the executor

- Commensurability only. Nothing here supports or refutes Assumption 1,
  bears on Assumption 2, or says anything about any deployed curve.
- Scale: n <= 21 on the diagonal, one off-diagonal extension to k = 8, N <= 60.
  The paper's conclusion needs n = 409, 571.
- The closure certificate's equivalence with "F4 completes at step degree <= D"
  is argued in `closure_cert.py` (truncated Buchberger criterion for a
  pair-selection-by-degree F4); the run measures both and reports their
  agreement per instance rather than relying on the argument.
- The single-level Macaulay statistic is compared against the archived
  GOAL-DREG-001 semi-regular prediction formula copied verbatim; the archived
  n = 12 fixture hash was not reproducible by the fixture builder on this host
  (a known limitation of that builder), so no numeric calibration against an
  archived DREG rank was possible.

## Matched-null outcome (recorded as it happened)

At (17,3,3,6), N = 35, the shape-matched random Boolean system behaved very
differently from the chained system built on the same shape:

| instrument | chained S_3 system | matched null |
| --- | --- | --- |
| msolve F4 trace | completed in 55 s, 15 rounds, step degree 4 | wall cap at 3600 s after 3 rounds |
| degree-4 closure | rank 59530 of 59536 columns, SUFFICIENT | rank 11186 of 59536, undetermined |
| degree-5 closure | not needed | unreached (384168 columns > cap) |

At (13,4,4,4), N = 42, the same contrast: the chained system's degree-4 closure
reached rank 124278 of 124314 columns and was sufficient, the null reached 12779.

This is the control the contract asks for: it shows that a SUFFICIENT verdict at
degree 4 is not an artifact of the Macaulay construction's shape, since a system
of the same variable count, equation count and degree profile does not produce
one. It says nothing about why the chained system is easier.
