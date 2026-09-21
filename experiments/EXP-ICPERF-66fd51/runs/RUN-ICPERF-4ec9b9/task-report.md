# RUN-ICPERF-4ec9b9 — task report

**Experiment** EXP-ICPERF-66fd51 · **Task** TASK-20260915-dde0a0 · role
executor-mechanical, run by the Coordinator session (see the manifest's
`inference.fallback_reason`) · **Protocol** the frozen
`specification.yaml`, second execution admitted by `AMD-20260915-4ec9b9`

**Scope, binding on everything below (core rule 4).** 60 shipped toy instances
over F_{2^15}, F_{2^17}, F_{2^19} at l ≤ 6, one fixed Koblitz curve, six engine
builds, one 4-CPU host, 504 rows. Nothing here says anything about the security
of any curve, and nothing here compares index calculus with any generic attack:
this run contains no rho column, no relation-yield column and no linear-algebra
column, exactly as the contract says.

**Observations only.** This report records what the run did. It moves no status,
writes no evidence record, and draws no conclusion about any hypothesis.

## What this run was for, and what it found

RUN-ICPERF-305ca3 measured every one of these rows already. Its problem was that
125 of its 474 solve rows started at loadavg > 2, concentrated in the phases
whose engines it wanted to compare — so its own rows cannot tell you whether its
medians are timings or contention. This run repeats the identical protocol with
no concurrent subagent and no VM suspension.

**The answer is that the first run's medians are timings.**

| quantity | agreement between the two runs |
|---|---|
| per-cell median **conflict counts** | **31 of 31 identical to the last digit** |
| per-cell median **wall times** | 55 compared, **median relative move 0.24%** |
| wall moves over 2% / 5% / 10% | **6 / 2 / 1** of 55 |
| largest single move | `n15l5/S` CryptoMiniSat pure-CNF, 0.4668 s → 0.5168 s (1.107×) — the smallest absolute time in the table |

Conflict counts are deterministic, so their agreement is a check on the harness
rather than on load. The wall times are the load-sensitive quantity, and the one
cell that moves more than 10% is a half-second measurement where 50 ms of
anything is 10%.

**What this does not establish.** It is an observation about these two runs on
this host, not a general claim that load average does not matter. It does not
repair the first run's exclusion test, which remains underpowered for want of a
low-load control group — this run supplies the comparison from *outside* that
run, which is a different and weaker thing than a control inside it. And it is
not independent replication: the same code, the same host and the same harness
produced both, so a defect common to both is invisible here by construction. Two
of them are known and named below.

## This run is less contaminated, not clean

| | RUN-ICPERF-305ca3 | RUN-ICPERF-4ec9b9 |
|---|---|---|
| solve rows at loadavg₁ > 2 | 125 | **48** |
| which phases | A 2, B 7, C 31, D 82, E 3 | **C 29, D 19** |
| maximum loadavg₁ at start | 4.55 | **3.81** |
| non-Macaulay2 `wall − cpu` | 0.0003 – 0.1695 s | 0.0004 – **0.3183 s** |

The remaining 48 rows have the same cause in both runs, and it is not an external
competitor: the run's own 32 Macaulay2 rows are multi-threaded, they drive the
1-minute load average up, and its decay tail reaches into the phase that follows.
An uninterrupted host cannot fix that. Reordering the phases so Macaulay2 runs
last, or pinning it to one CPU, would.

## Rows

504 planned, 504 recorded, all five phases finished.

| phase | rows | wall |
|---|---|---|
| A — WDSat 4 configs + certificates | 318 | 6900.4 s |
| B — CryptoMiniSat XOR | 60 | 3153.2 s |
| C — Macaulay2 F4 | 32 | 236.2 s |
| D — pure CNF (CMS, CaDiCaL, MiniSat) + noncore_first + nulls | 90 | 13348.5 s |
| E — Singular std | 4 | 3600.3 s |

Statuses: 212 SAT, 191 UNSAT, 39 budget stops, 32 `infrastructure_exit_-6`
(every Macaulay2 row), 30 certificate rows carrying a verification rather than a
solver status.

**Certificates: 30 of 30 verified, 0 invalid.** Phase A's admission gate passed,
so no stopping rule fired.

## Predictions, as `summary.py` printed them

`{P1: false, P2: null, P3: true, P4: true, P5: true, P6: true}` — identical to
the first run.

**Three of those booleans are known to be wrong as statements about the
predictions**, and were known before this run's summary was produced. They are
recorded in `AMD-20260915-4ec9b9` because `summary.py` was deliberately *not*
repaired while a run using it was in flight:

1. **P3c** — the four ratios are one number copied across cells by a loop
   variable that leaks its scope. Corrected per-cell ratios are 10.40, 34.47,
   67.46, 83.50; all four still clear the threshold of 10, so the verdict
   survives the correction.
2. **P5** — the Gröbner clause is never evaluated. It guards on `engine_cpu_s`,
   a key present on 0 of 504 rows, so `P5: true` covers half the prediction as
   worded and nothing records that the other half was skipped.
3. **P6** — the top-level boolean drops a cell whose value is unevaluable from
   its conjunction, so "holds on every cell" is printed when `n19l6` was not
   testable at all (all six of its nulls timed out).

Repairing `summary.py` is a successor task against the *next* run. Editing it
under a running one would have changed what this run's own summary means.

## Unexpected observations (core rule 8)

**P1 fails identically, and the reason is now known.** The same five SAT answers
on `n19l6-19-U` fail E-membership decoding. Review joint V1 classified them
positively as **twist decompositions**: f₃ = 0 under the LSB-first convention
that verifies all 30 shipped certificates, all four elements have absolute trace
1 so none lies on E, and the decomposition holds on the quadratic twist. An
exhaustive enumeration of every multiset in V³ across all 60 instances agrees
with both runs' SAT/UNSAT verdicts 60 of 60, and finds this instance has exactly
one root — the twist one. So the shipped Weil-descent system does not constrain
its solutions to E, and nothing downstream of the solver filters twist solutions.
P1's failure is a property of the encoding, reproduced here, not a malfunction of
either run.

**The Macaulay2 column is an infrastructure observation, twice over.** Review
joint V2 established that the `std::bad_alloc` is an **RLIMIT_AS artifact**:
under the harness's 6 GB cap the process dies with 5.996 GiB of *address space*
against 2.575 GiB *resident*, and the same committed script completes uncapped,
reserving 145 GiB of address space against a 6.8 GiB resident peak. Under core
rule 5 those 32 rows say nothing about F4's memory behaviour. V2 also found that
every one of the 32 committed `.m2` scripts carries a `convert.py` parse error at
line 49 that fires *after* the computation — so lifting the memory cap alone
would turn 32 aborts into 32 exit-code-1 rows. **Both defects are in this run's
scripts too, so this run does not repair the Gröbner column**, and P2 is null
here for the same reason it was null in the first run. With both repaired, V2
measured F4 returning a 43-element basis at max degree 2.

**Singular's timeout reproduces, and is fairly invoked.** All four rows hit the
900 s budget again. V2 compared both committed scripts as normalised monomial
sets and found Singular got the same ideal as Macaulay2, ran single-threaded, and
still does not finish without `option(redSB)`. But `slimgb` on the same ring and
ideal finishes in 167 s and agrees with F4. So `std` is uncompetitive on these
systems while **the Gröbner column is measurable on this host inside the
contracted budget** once the two defects above are removed.

**The Singular version is still unrecorded.** The probe timed out at 60 s again.
V2 localised it: the probe hangs whenever the child's stdin never reaches EOF,
and Singular run directly is 4.3.2. An instrument defect, not a missing
dependency.

**A note on what the review found about the null-object comparison.** V2's
routed relabelling control shows that a random permutation of variable indices
moves WDSat on `Xn15l5-11-U` from 31 257 conflicts to a median 4 224 251 while
moving the matched null object only 2.14×. That bears directly on how P6's ratios
in this run's `summary.json` may be read, and it is the reviewers' finding rather
than this run's; it is recorded here so a reader of these numbers does not read
them as a structure effect without it.

## Artifacts

`results.jsonl` (504 rows), `summary.json`, `plan.json`, `environment.json`,
`phase_log.txt`, `logs/` (per-row stdout and stderr, and `summary_stdout.txt`),
`null_objects/`, `pure_cnf/`, `scripts/`. `builds/` holds per-instance WDSat
rebuilds including binaries and is not committed: the sources are hashed in
`environment.json` and each row records its `wdsat_constants`, so the builds are
reproducible.

Exact commands are in the manifest's `code.command` and the summary was produced
by `python3 experiments/EXP-ICPERF-66fd51/code/summary.py experiments/EXP-ICPERF-66fd51/runs/RUN-ICPERF-4ec9b9`.

## What this run has not had

**An independent review.** The two reviews cited throughout are of
RUN-ICPERF-305ca3; they are cited because their findings about the encoding, the
RLIMIT_AS artifact and the `.m2` parse error apply verbatim to this run's
identical artifacts. This run's own review chain opens when its round does, and
its task entry in the dispatch queue records that plainly rather than leaving the
absence to be noticed.
