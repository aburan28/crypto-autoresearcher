# RUN-SEMBIN-5ed13e -- m = t = 2 window re-measured on a fixed M4RI

Re-measurement of the RUN-SEMBIN-9bb990 m = 2 window (n = 40..45) after that
run's closure verdicts were found to rest on M4RI 0.0.20200125, which returns
eliminations outside the row space at this scale (RUN-SEMBIN-9bb990
`NOTES-deviations-and-limitations.md`, sections "STOP" onward). Same design:
per n, the first solution-free and the first solution-bearing draw of the
contract's draw order, chosen from the exact counts in RUN-SEMBIN-9bb990/counts
before any closure was run. Scheduler: `schedulers/window_sched.py`.

Instrument: libclosure built against M4RI release-20240729 (git; `make check`
15/15), `mzd_echelonize_pluq`, structural output check on every elimination,
per-batch memory sizing, cap 11 GiB, checkpointing (`CLOSURE_CKPT_DIR`).
Every closure record carries `m4ri_library`, `elimination`,
`elimination_faults`, `dropped_terms_above_D`, `checkpoint_resumes`.

## Deviations and operations log

- Container restarts: one during n = 40 draw 1 (resumed from its D = 4
  checkpoint at iteration 4); the checkpoint files were renamed to the
  hash-named scheme of closure.c commit a6d3b37e17 before the relaunch.
- Scheduler amendment 2026-10-03: lanes with a `LANE_COMPLETE` marker are
  skipped on relaunch (re-entering run_wrapper would rewrite a finished lane's
  environment.json). Markers for n = 40..44 were written from the scheduler log.
- Paused by the operator at 2026-10-03T18:04 during n = 45 (D = 4 just
  started) to cross-check n = 44 draw 5 (below); resumed afterwards.
- Restarted by the operator at 2026-10-03T22:21 during n = 45 draw 0 on
  closure.c 9096320e22 (memory accounting; see "Code that produced each
  record"), resuming from the D = 4 checkpoint.
- A container restart between 2026-10-04T01:30 and 01:50 did not stop the scheduler or
  the closure process (both kept their PIDs); no resume was needed.

## Cross-check of n = 44 draw 5 (the first insufficient verdict)

Record (PLUQ, cap 11): D = 4 completed, rank 140,853 / 149,986, standard
monomials 9,145 against |V(I)| = 4 (exact count), verdict insufficient,
iterations (rows, rank, new pivots) = (44,43,43), (55857,52075,52032),
(480965,126961,74886), (145089,135749,8788), (143493,140853,5104),
(140853,140853,0) -- the last iteration has no products (every new row has
degree 4), so the closure saturated; no fault, no dropped term.

Cross-check (`crosscheck_n44_d5/`): the same instance file, a DIFFERENT
elimination routine (`mzd_echelonize`, Four Russians + PLE, same fixed
library), different batching, and the evaluation check at a verified common
zero (one of the 4, from count_m2's lister) on every elimination:

  - cap 7 GiB: stopped `unreached_memory_cap` at rank 125,250 in iteration 2
    (batch fell below 1024); 3 eliminations, all `in=0 out=0`. An instrument
    limit, not a result.
  - cap 10.5 GiB: completed, rank 140,853, std 9,145, verdict insufficient,
    identical iteration profile, and basis leading-monomial SHA-256
    `57ed1d33...335db8` EQUAL to the record's. 6 eliminations, all
    `in=0 out=0`; elimination_faults 0.

Two elimination routines and two batchings give the same leading-monomial set,
and no row produced leaves the ideal at the tested zero. Scope: one instance,
(n, m, t) = (44, 2, 2), D <= 4, this generator family and draw. The
evaluation check is a necessary condition for soundness at one zero, not a
proof, and an under-filled closure (missing products) is the failure an
insufficient verdict would hide; both routines share closure.c's product code.

## Results (all 12 instances; window complete 2026-10-04T04:39Z)

Generated from the lane records by `schedulers/window_table.py` (reads
`closure_m2_n*/cells/results.jsonl`; writes nothing). |V(I)| is the exact
count from count_m2's chain walk, cross-checked by the enumerator (`cross`
agrees on every instance). "decided at" is the closure degree whose record
fixed the verdict; standard monomials are counted over every square-free
monomial not divisible by a leading monomial, so they can exceed
columns - rank. Faults and resumes are summed over the lane's per-D records;
see "Record defects" below for the n = 45 draw 4 resume count.

| n | N | draw | |V(I)| (exact) | verdict (D <= 4) | decided at | rank / columns at D | standard monomials | LM SHA-256 (prefix) | D=4 wall s | faults | resumes |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 40 | 40 | 0 | 0 | sufficient | D=4 (1 in W_D) | 101931 / 102091 | 0 | 8b168c1a | 2393 | 0 | 0 |
| 40 | 40 | 1 | 4 | sufficient | D=4 | 102087 / 102091 | 4 | fb4ed73e | 1748 | 0 | 1 |
| 41 | 42 | 0 | 0 | sufficient | D=4 (1 in W_D) | 124314 / 124314 | 0 | 1bd8f57a | 3935 | 0 | 0 |
| 41 | 42 | 4 | 4 | sufficient | D=4 | 124310 / 124314 | 4 | 993125fa | 11437 | 0 | 0 |
| 42 | 42 | 0 | 0 | sufficient | D=2 (1 in W_D) | 904 / 904 | 0 | f1dffe89 | - | 0 | 0 |
| 42 | 42 | 1 | 2 | sufficient | D=4 | 124312 / 124314 | 2 | 12ef5aa2 | 12392 | 0 | 0 |
| 43 | 44 | 0 | 2 | sufficient | D=4 | 149984 / 149986 | 2 | bfdba56e | 20627 | 0 | 0 |
| 43 | 44 | 5 | 0 | sufficient | D=4 (1 in W_D) | 149986 / 149986 | 0 | 855d183f | 7499 | 0 | 0 |
| 44 | 44 | 0 | 0 | sufficient | D=2 (1 in W_D) | 991 / 991 | 0 | 3fb3c969 | - | 0 | 0 |
| 44 | 44 | 5 | 4 | insufficient | D=4 | 140853 / 149986 | 9145 | 57ed1d33 | 6129 | 0 | 0 |
| 45 | 46 | 0 | 2 | insufficient | D=4 | 166705 / 179447 | 13681 | 64f3e3fa | 9626 | 0 | 1 |
| 45 | 46 | 4 | 0 | insufficient | D=4 | 166705 / 179447 | 13681 | c1f9407a | 12910 | 0 | 3 |

Nine of twelve instances are sufficient at D <= 4: every instance at
n = 40..43, and n = 44 draw 0 (that one and n = 42 draw 0 already at D = 2,
where 1 enters W_D). Three are insufficient at D = 4: n = 44 draw 5
(|V| = 4), n = 45 draw 0 (|V| = 2) and n = 45 draw 4 (|V| = 0; its D = 4
closure saturated at rank 166,705 / 179,447 without reaching 1, so 13,681
standard monomials stand against |V(I)| = 0). Every elimination passed the structural output check
(`elimination_faults` 0), and no term above D was dropped.

The two n = 45 draws reach the same D = 4 rank (166,705), the same
standard-monomial count (13,681), the same rank after every iteration, 45 -> 59,603 -> 152,003 -> 161,305 -> 166,705 -> 166,705, and
the same leading-degree counts at degrees 3 and 4 (8,726 and 157,755). Their
leading-monomial SETS differ (SHA-256 64f3e3fa... vs c1f9407a...): draw 4
has two linear leading monomials and 222 quadratic ones where draw 0 has one
and 223. Same-shape systems sharing a rank profile is consistent with generic
behaviour of a degree-capped closure; it is an observation on two draws,
not a claim.

Scope: (n, m, t) = (40..45, 2, 2), chained_eq5 family, low_degree_polynomial
subspace, B_random, the first solution-free and first solution-bearing draw
per n, closure degree D <= 4, cap 11 GiB, this host. An insufficient verdict
at D = 4 says the degree-4 closure does not cut the ideal down to V(I); it
says nothing about D = 5 or about any solver's actual degree of regularity.

## Code that produced each record

The instrument changed between lanes; each lane's `environment.json`
records the hash of the code at that lane's LAST launch, which is not always
the code that produced every record in it:

  - n = 40 draw 0: closure.c d6a21306ee (sha256 7bb7bfdd...), run
    2026-10-02T21:35-22:15. The lane was relaunched at 2026-10-03T00:16
    after a container restart; that relaunch rewrote the lane's
    environment.json to a6d3b37e17 (a499bc29...). The only change between
    the two is checkpoint file naming; the elimination is identical.
  - n = 40 draw 1: started on d6a21306ee, resumed from its checkpoint on
    a6d3b37e17 at iteration 4.
  - n = 41..44: a6d3b37e17 (a499bc29...), as recorded.
  - n = 45 draw 0: a6d3b37e17 through D = 4 iteration 2, row 56,453; the lane
    was restarted at 2026-10-03T22:21 on 9096320e22 (a7da1a1f...; the basis
    is no longer held twice during an elimination, so batches are ~10x
    larger) and resumed from the checkpoint (scheduler log line "restarted
    on closure.c commit 9096320e22"). Memory accounting only; the rows
    produced and the elimination routine are unchanged.
  - n = 45 draw 4: 9096320e22 (a7da1a1f...), as recorded.

All lanes: M4RI release-20240729, `mzd_echelonize_pluq`, structural output
check on every elimination.

## Record defects found after the records were written (not rewritten)

  - `per_D[*].solutions_source` reads "f4_quotient_dimension" in every
    closure record. F4 was skipped in this run; the |V(I)| actually used is
    the exact count, which the record's top-level `solutions_source`
    ("exhaustive_count_chain") states correctly. Fixed for later runs in
    commit 1c042d5f80.
  - n = 45 draw 4: `checkpoint_resumes` reads 1 at D = 2, 3 and 4. That
    instance never resumed; the counter was process-wide and carried draw
    0's one real resume into every later closure of the same process. True
    value 0 for all three. `elimination_faults` shared the defect, but every
    fault count in this run is 0, so none is wrong. Fixed for later runs in
    commit 5e1aa460cb.

## Authority and scope

This re-measurement was run on the user's direct instruction in the
executing session ("re-measure the window on the fixed M4RI") after RUN-SEMBIN-9bb990's closure
verdicts were found to rest on a defective M4RI. The dispatching handoff,
TASK-20260917-b2bf32, declares `write_scope` only for code/** and
runs/RUN-SEMBIN-9bb990/**; this run directory is outside it, and no ledger
record yet names RUN-SEMBIN-5ed13e. The package is committed as an
executor run record and claims no research-state change; covering it with
an additive scope amendment or a new handoff is a Coordinator decision, and
until the dispatcher's verifier accepts it the run is not official.

## Cross-check of n = 45 draw 0

Record (PLUQ, cap 11, closure.c a6d3b37e17 then 9096320e22 after a
checkpoint resume): D = 4 completed, rank 166,705 / 179,447, standard
monomials 13,681 against |V(I)| = 2 (exact count), verdict insufficient,
leading-monomial SHA-256 `64f3e3fa...3e696c5ead`, iterations (rows, rank,
new pivots) = (45,45,45), (63870,59603,59558), (626806,152003,92400),
(171415,161305,9302), (169585,166705,5400), (166705,166705,0); the last
iteration has no products, so the closure saturated.

Cross-check (`crosscheck_n45_d0/`, started by `after_window.sh` once the
scheduler had logged "window schedule done", so the two never shared the
host's memory): the same instance file (system sha 6961f43cb0a6dc45...), a
DIFFERENT elimination routine (`mzd_echelonize`, same fixed library), a
different batching (cap 11.5 GiB), no checkpointing, and the evaluation
check at a verified common zero (one of the 2, from count_m2's lister; it
violates 0 generators) on every elimination. Library built with
-DECH_EVALCHECK from closure.c at 9096320e22 (sha256 a7da1a1f...).

  - completed in 6,003 s: rank 166,705, std 13,681, verdict insufficient,
    identical iteration profile, and leading-monomial SHA-256
    `64f3e3fa0dc10c6e152a06d700a93ffed43001cf4b9b65be9be9c23e696c5ead`,
    EQUAL to the record's. 7 eliminations, all `in=0 out=0`;
    elimination_faults 0.

As for n = 44 draw 5: two elimination routines and two batchings give the
same leading-monomial set, and no row produced leaves the ideal at the
tested zero. Same scope and same caveat: one instance, (n, m, t) =
(45, 2, 2), D <= 4; the evaluation check is necessary, not sufficient, for
soundness, and both routines share closure.c's product generation, so a
missing-product defect would not be caught by this comparison. n = 45
draw 4 was not cross-checked.
