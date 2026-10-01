# Validation report — joint V2 of REVIEW-ICPERF-20260913-66fd51

- **Task**: TASK-20260915-195b0c (validator, `review-adversarial`, independent session)
- **Round**: REVIEW-ICPERF-20260913-66fd51 — the union of `review-plan.yaml`,
  `review-plan-addendum-V6.yaml`, `review-plan-addendum-split-V2.yaml`
- **Under review**: RUN-ICPERF-305ca3 of EXP-ICPERF-66fd51
- **Joint owned**: **V2 alone** (row re-runs and the Gröbner column). Plus the
  control **proves-too-much object 2**, routed to this task by the dispatching
  instruction because it requires launching a solver.
- **Not owned, not judged**: V1, V3, V4, V5, V6, and proves-too-much object 1.
  No verdict is offered on the claim as a whole or on P1, P2, P3c, P4, P5, P6 as
  predictions. The Coordinator composes.

## Verdict

| item | verdict |
| --- | --- |
| **V2** | **HOLDS** |
| proves-too-much object 2 (relabelling control) | **FAILS**, by the plan's own failure signature |

**The single fact that decided V2**: neither of the plan's two breaking
artifacts occurred. All four WDSat rows reproduced exactly — status, conflict
count, *and* the full assignment bit string — from binaries I rebuilt that are
byte-identical to the producer's; and Macaulay2 without `RLIMIT_AS` did **not**
fail the same way. It ran the same committed script's F4 computation to
completion in ~50 s where the capped run aborted after 12 s at 2.58 GiB
resident — and with the script's broken reporting line repaired it printed the
answer: a basis of 43 elements, maximum degree 2, not the unit ideal. So the
`std::bad_alloc` is an address-space-limit artifact, and the plan's breaking
artifact for this clause ("Macaulay2 failing identically without RLIMIT_AS at
< 6 GB RSS") did not occur.

**The single fact that decided the control**: 9 of 10 uniformly random
relabellings of `Xn15l5-11-U.anf` — the same system, variables renamed by a
bijection — cost **more than 10× the shipped order's 31,257 conflicts**
(median 4,224,251, i.e. **135×**), landing at **0.55× the matched null
object's 7,697,173**. The plan's failure signature for this object is "a
relabelled n15l5-11-U at null-order conflicts (> 10x its structured count)".
It is met.

Both verdicts are scoped to the tested instances, engine builds, host and
budget. Nothing here asserts anything about any curve's security, and nothing
here changes any record's status.

## 0. Conditions, independence, and order of work

Machine: 4 CPUs, 15 GB RAM. Before starting I verified the rerun had exited
(`pgrep -af bench.py` → no `bench.py` process; `uptime` → load average 0.09,
decaying) and I was the only measuring process throughout. All 29 child
processes ran **sequentially, one at a time**; loadavg at the start of every
row is recorded in `artifacts/v2_rows_index.json` and in the tables below. The
observed range is 0.00–1.00, and the non-zero readings are the decay tail of my
own immediately preceding row, not another workload.

**Ordering attested**: every measurement in sections 1–4 was taken and written
down **before** I opened `experiments/EXP-ICPERF-66fd51/runs/RUN-ICPERF-4ec9b9/`.
The rerun appears only in section 5, labelled as a secondary cross-check.

**Blindness**: I did not read anything under
`coordination/review/icperf-20260913-66fd51/TASK-20260913-6c5729/` — not
`report.md`, not `attestation.yaml`, not `work/`, `artifacts/` or `scratch/`,
including the `PTM2-Xn15l5-11-U-perm20260915.anf` that may exist there. My
control object is generated from my own recorded seed by my own generator. My
own task directory contains no `scratch/` (the stale scratch of disclosure D-1
is in the other reviewer's directory, which is off-limits to me).

`tools/check_review_independence.py`, run against the composed plan and my
attestation alone, reports no problem with V2, my `joints_owned`, my verdict
shape or my blindness declaration; it composes the two addenda and confirms V2
is reassigned to this task. Its six complaints are all "joint X is assigned to
TASK-20260913-6c5729, which filed no review_attestation", which is an artifact
of my pointing it at my own file only — I may not read the sibling's.

**Everything I report is my own measurement**, produced by code I wrote for
this task under `work/`: `measure.py` (per-child rusage, `/proc` peaks,
loadavg), `anf_check.py` (independent ANF parser, shape fingerprint, WDSat
sizing, relabelling generator, written from `dimacs.c`), `build_wdsat_v2.py`
(independent rebuild), `cmp_scripts.py` (M2 ↔ Singular system equivalence),
`ptm2_analysis.py`, `collect_rows.py`. None of them imports `bench.py`,
`convert.py` or `summary.py`.

## 1. V2(a) — the four WDSat rows reproduce exactly

**Provenance first.** All 15 vendored WDSat sources verify against the
committed manifest (`sha256sum -c` on `inputs/TRIMOSKA-WDSAT-2024/
UPSTREAM_SHA256SUMS.txt`, 15/15 OK), and `Xn15l5-11-U.anf` matches its recorded
hash `3ea7871d…10c69`. I derived each instance's static sizing myself from the
ANF (`anf_check.py`) rather than reading `config_used.json`, and got the values
the run recorded (e.g. n15l5: `MAX_ID` 502, `MAX_EQ` 1569). My rebuilt binaries
are **byte-identical** to the producer's:

| build | my sha256 | producer's binary | identical |
| --- | --- | --- | --- |
| MAX_ID 502 (`v2_987b7f5ef9`) | `6420d9c6…f051` | `builds/wdsat_987b7f5ef9` | yes |
| MAX_ID 767 (`v2_455326dcb0`) | `76cec2da…8c1a` | `builds/wdsat_455326dcb0` | yes |
| MAX_ID 940 (`v2_bd5f91ccca`) | `dbdd035a…b404` | `builds/wdsat_bd5f91ccca` | yes |

**The four rows** (`wdsat_solver -i <anf>`, no flags, `RLIMIT_AS` 6 GiB, as
`bench.py` runs them):

| instance | RUN-305ca3 status / conflicts | my status / conflicts | assignment string | my wall (s) | my loadavg1 | producer wall (s) | producer loadavg1 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| n15l5-1-S | SAT / 26 | SAT / 26 | identical (42 bits) | 0.0046 | 0.03 | 0.0049 | 1.00 |
| n15l5-11-U | UNSAT / 31257 | UNSAT / 31257 | — (UNSAT) | 0.1937 | 0.03 | 0.2153 | 1.02 |
| n19l6-1-S | SAT / 5312 | SAT / 5312 | identical (51 bits) | 0.0295 | 0.03 | 0.0330 | 1.01 |
| n19l6-11-U | UNSAT / 255958 | UNSAT / 255958 | — (UNSAT) | 2.3091 | 0.03 | 2.3215 | 1.04 |

4/4 exact on status and conflicts, and on the assignment bit strings, which the
plan did not ask for and which is a stronger check than the conflict count
alone. Wall times are reported separately and are not a reproduction criterion;
mine are 4–12 % faster, consistent with the producer's rows having started at
loadavg ≈ 1.0 and mine at 0.03.

One integrity note, not a defect in these rows: the run's
`max_rss_kb_children_highwater` is the driver's cumulative `RUSAGE_CHILDREN`
high-water mark, monotone across rows (the task report says so). It is not a
per-row peak. My `os.wait4` per-child `ru_maxrss` for these four rows is
10.5–10.7 MB.

## 2. V2(b) — the Macaulay2 `std::bad_alloc` is an `RLIMIT_AS` artifact

Six executions of `M2 --script scripts/n15l5-1-S.m2` (the committed script) and
of a minimally repaired copy. `VmPeak` and `VmHWM` are the kernel's own
high-water marks from `/proc/<pid>/status`, sampled at 50 Hz; `VmPeak` is peak
*virtual address space*, which is what `RLIMIT_AS` caps, and `VmHWM` is peak
*resident* memory, which is what "memory exhaustion" would mean.

| # | script | RLIMIT_AS | CPUs | rc | wall (s) | cpu (s) | VmPeak | VmHWM | threads | loadavg1 | outcome |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| C1 | committed | 6 GiB | 4 | −6 | 12.16 | 41.37 | **5.996 GiB** | **2.575 GiB** | 11 | 0.01 | `std::bad_alloc` — reproduces the run |
| C3 | committed | 12 GiB | 4 | −6 | 11.96 | 40.95 | 10.689 GiB | 2.579 GiB | 11 | 0.37 | `std::bad_alloc` |
| C6 | committed | 6 GiB | 1 (`taskset`) | −6 | 39.83 | 39.82 | 5.577 GiB | 2.593 GiB | 8 | 0.15 | `std::bad_alloc` |
| C7 | repaired | 6 GiB | 1 (`taskset`) | −6 | 39.02 | 39.02 | 5.327 GiB | 2.589 GiB | 8 | 0.56 | `std::bad_alloc` |
| C2 | committed | **none** (10 GiB RSS watchdog) | 4 | 1 | 52.20 | 174.93 | 145.370 GiB | **6.823 GiB** | 11 | 0.55 | F4 **completed**; then a syntax error in the *reporting* line |
| C5 | repaired | **none** (11 GiB RSS watchdog) | 4 | 0 | 49.97 | 170.56 | 145.651 GiB | 6.705 GiB | 11 | 0.93 | `RESULT gb_size=43 cpu_s=47.7616 maxdeg_gb=2 is_unit=false` |

**Classification: address-space-limit artifact.** At the moment of death under
the harness's limit the process held 2.58 GiB of resident memory and 6.00 GiB
of address space — it hit the cap on the quantity `RLIMIT_AS` measures while
using 43 % of that in real memory. Removing the cap lets the identical script
run the identical computation to completion in ~50 s wall on a machine with
15 GB of RAM. `RLIMIT_AS` is not a memory limit for this process: Macaulay2's
collector reserves 145 GiB of address space against a 6.8 GiB resident peak, a
21× ratio. Under AGENTS.md core rule 5 the 32 `infrastructure_exit_-6` rows are
an infrastructure observation and are not evidence about F4's memory behaviour
on these systems. The run's own task report already labels them
`infrastructure_exit_-6` and records P2 as `null` with "nothing asserted",
which is the correct handling; what this section adds is the *cause*.

**The Coordinator's prior is confirmed in its main clause and refined in its
escape clause.** The plan said: "Macaulay2 on n15l5-1-S without RLIMIT_AS,
under a wall timeout and an RSS monitor, exceeding 6 GB RSS … then the memory
model is the problem, not the limit." Unconstrained, M2's peak RSS is
**6.71–6.82 GiB, which does exceed 6 GiB by ~12 %**. So both halves are true at
once and the consequence is specific: replacing `RLIMIT_AS` with an *equivalent*
6 GiB RSS watchdog would also kill this row — later, at ~50 s instead of 12 s,
and for an honest reason. A successor run that wants to measure P2 must change
**both** the limit *kind* and its *value* (≥ 8 GiB resident per child on n15l5;
larger cells are unmeasured).

**Multi-threading is not the whole mechanism.** The Coordinator pointed at the
1.27–2.74 cpu-s/wall-s ratio. It is real — I measure 3.35–3.42 on an idle host,
with 11 threads — but pinning to a single CPU (C6, C7) still aborts, at
`VmPeak` 5.33–5.58 GiB against `VmHWM` 2.59 GiB. Even with one runnable CPU M2
starts 8 threads and the address-space-to-resident ratio stays above 2. The
reservation behaviour, not the parallelism, is what the cap catches.

**A second, independent infrastructure defect the plan did not anticipate.**
Every one of the 32 committed `.m2` scripts contains, at line 49:

```
gens_ = flatten entries G;
```

`_` is Macaulay2's subscript operator, so this is a parse error
(`n15l5-1-S.m2:49:7:(3):[5]: error: syntax error at '='`). It is raised when
execution reaches line 49 — i.e. *after* the F4 computation has finished — so
the computation runs and its result is then thrown away with exit code 1. That
is what C2 shows. The defect originates in
`experiments/EXP-ICPERF-66fd51/code/convert.py` lines 51–54, so it is present in
every generated script in both runs. **Consequence: even with unlimited memory
the harness as committed could never have recorded a Macaulay2 result.** Lifting
`RLIMIT_AS` alone would convert 32 rows of `infrastructure_exit_-6` into 32 rows
of `infrastructure_exit_1`. My repaired copy (`work/m2probe/
n15l5-1-S.reportfix.m2`) changes those two lines and nothing else
(`artifacts/m2_reportfix.diff`: `gens_` → `gensG`, 2 lines); ring, ideal, field
equations and the F4 call are byte-identical to the committed script.

## 3. V2(c) — Singular's timeout is a real observation about `std`

Judgement: **the invocation is fair and the 900 s stop is a real, censored
observation about `std` on these systems** — with one provenance defect in the
run's environment record, and one finding that materially changes what the
Gröbner column can be read to mean.

Evidence, in order:

1. **The system Singular was given is the system Macaulay2 was given.** My own
   parser (`work/cmp_scripts.py`) reads both committed scripts for all four
   instances that have a `.sing` and compares the polynomial systems as
   normalised monomial sets: 42 variables, 42 ideal generators, 42 field
   equations, generators identical as a set *and in order*, same degree
   support, same monomial totals (n15l5-1-S: 2684 each). Both are GRevLex over
   characteristic 2 with field equations, as the contract says.
   (`artifacts/m2_vs_singular_system_equivalence.txt`)
2. **The 900 s was spent computing, not waiting.** A bounded 300 s re-probe of
   the committed script under the harness's own 6 GiB cap: single-threaded,
   `cpu/wall = 1.00`, memory climbing monotonically to 0.85 GiB — nowhere near
   the cap, no thrash, no stall. The run's four rows likewise report
   `cpu_s ≈ 899.97` against `wall_s ≈ 900.04`.
   (`artifacts/v2c_singular_probe.json`)
3. **`option(redSB)` is not the cause.** The same script with the `redSB` line
   removed (nothing else changed) also fails to finish in 300 s, at 0.84 GiB.
4. **But `std` is.** The same ring, the same ideal, the same options, with
   `slimgb(I)` in place of `std(I)`, **finishes in 167.4 s**:
   `RESULT gb_size=43 cpu_ticks=167 ticks_per_sec=1 vdim=3 maxdeg_gb=2`, peak
   RSS 3.22 GiB — comfortably inside the contracted 900 s budget and 6 GiB cap.

So the timeout is not an artifact of how the *system* was encoded, of the
memory cap, or of the reduction option; `std` really is uncompetitive here,
which is what the Coordinator expected. What the Coordinator did not anticipate
is point 4: **the Gröbner column is not intrinsically unmeasurable on this
host**. Two independent engines agree on the answer for n15l5-1-S — Macaulay2
F4 (C5) and Singular `slimgb` both return a basis of **43 elements of maximum
degree 2, not the unit ideal**, and `slimgb` adds `vdim = 3` — and both did so
within the contract's per-row budget once the two harness defects are removed.
That is one instance, on one host, and `slimgb` is *not* the contracted engine;
it is recorded here as an observation, not as a substitute for the contract's
`singular_std` column and not as a verdict on P2.

**Provenance defect in the environment record.** `environment.json` records
`"Singular": "unavailable: Command '['Singular', '--version']' timed out after
60 seconds"`, so the run cannot state which Singular produced its four rows.
I reproduced the cause exactly: `bench.py`'s `ver()` helper
(`subprocess.run(argv, capture_output=True, timeout=60)`) leaves **stdin
inherited**, and `Singular --version` prints its banner and then blocks reading
stdin whenever stdin is a terminal or any descriptor that never reaches EOF.

| stdin given to `Singular --version` | result |
| --- | --- |
| pseudo-terminal | **hangs** (killed at 25 s) — reproduces the recorded failure |
| pipe held open, no EOF | **hangs** (killed at 25 s) |
| `/dev/null`, or a pipe closed immediately | returns in 0.0 s, rc 0 |

(`artifacts/v2c_version_probe_stdin.json`.) The four *solver* rows are
unaffected: `bench.py` gives solver children `stdin=DEVNULL`, and the scripts
end in `quit;`. Run directly, the installed engines are **Singular 4.3.2
(4330, 64 bit)** and **Macaulay2 1.22**, which are the versions the hypothesis
names — so the contract's engine statement is right even though the run's own
environment record could not confirm it.

## 4. Proves-too-much object 2 — the relabelling control FAILS

**Object.** `inputs/TRIMOSKA-ECICB-2024/upstream/benchmarks/Xn15l5-11-U.anf`
(sha256 `3ea7871d…10c69`, matching the committed manifest) with a uniformly
random permutation applied to its 42 variable indices. Primary seed
**1661196** = `0x195B0C`, the hex token of this task, with nine supplementary
seeds **1661197–1661205** so the result is not one draw. The permutation is
drawn by `random.Random(seed).shuffle` over `[1..42]` and asserted to be a
bijection; line order, term order, `T` constants and `.d` degree prefixes are
preserved, only indices are renamed. Objects and per-seed pre-check records are
in `artifacts/ptm2/`.

**Required pre-checks, all 10 seeds** (`anf_check.py`, written from
`dimacs.c`): header `p cnf 42 42` identical; equations parsed 42; constant
count 36 = 36; total terms 2147 = 2147; the multiset of per-equation degree
multisets identical; and, additionally, the derived WDSat static sizing
identical (`MAX_ID` 502, `MAX_EQ` 1569, `MAX_DEGREE` 4) so every object runs on
the same byte-identical binary. All 10 pass. The 10 files are pairwise distinct.

**Generator control.** My rewriter applied with the *identity* permutation
produces a file **byte-identical** to the source (same sha256), and running it
returns 31,257 conflicts. So the rewriting itself changes nothing; whatever the
permuted files do differently is the relabelling.

**Result — WDSat default, my build `v2_987b7f5ef9`, 6 GiB cap, sequential:**

| object | status | conflicts | ×shipped order | ×null | wall (s) | loadavg1 |
| --- | --- | --- | --- | --- | --- | --- |
| shipped order (original) | UNSAT | **31,257** | 1.0 | 0.004 | 0.199 | 0.02 |
| identity rewrite | UNSAT | 31,257 | 1.0 | 0.004 | 0.197 | 0.02 |
| perm seed 1661196 | UNSAT | 120,022 | 3.8 | 0.016 | 0.469 | 0.02 |
| perm seed 1661198 | UNSAT | 900,875 | 28.8 | 0.117 | 1.984 | 0.36 |
| perm seed 1661202 | UNSAT | 974,508 | 31.2 | 0.127 | 1.847 | 0.89 |
| perm seed 1661203 | UNSAT | 1,220,093 | 39.0 | 0.159 | 1.530 | 0.98 |
| perm seed 1661205 | UNSAT | 1,245,184 | 39.8 | 0.162 | 1.769 | 0.98 |
| perm seed 1661199 | UNSAT | 7,203,317 | 230.4 | 0.936 | 10.664 | 0.36 |
| perm seed 1661204 | UNSAT | 9,480,678 | 303.3 | 1.232 | 9.508 | 0.98 |
| perm seed 1661197 | UNSAT | 13,047,745 | 417.4 | 1.695 | 22.490 | 0.02 |
| perm seed 1661200 | UNSAT | 22,669,756 | 725.3 | 2.945 | 37.954 | 0.46 |
| perm seed 1661201 | UNSAT | 43,387,710 | 1388.1 | 5.637 | 57.263 | 0.72 |
| **matched null object** (my re-measurement) | UNSAT | **7,697,173** | 246.3 | 1.0 | 45.354 | 0.02 |

Every object returns **UNSAT**, so no permutation bug: the system is preserved.
Median over the 10 seeds is **4,224,251 conflicts = 135× the shipped order and
0.55× the null**; geometric mean 3,271,190 = 105× and 0.43×. **9 of 10 seeds
exceed both thresholds** (≥ 3×10⁵ and > 10× the original); the tenth, at
120,022, is still 3.84× the original and is far outside the "structured order,
~3×10⁴" neighbourhood the plan requires for the control to hold.

**The order-sensitivity contrast is the sharpest number here.** I ran the same
relabelling on the *null* object (seeds 1661196–1661198, same pre-checks, my
byte-identical MAX_ID-940 build): 3,599,979 / 4,795,362 / 7,700,200 conflicts
against the unpermuted null's 7,697,173 — a spread of **2.14×**. The structured
instance's conflict count spans **361×** across orders; the null's spans 2.14×.
The structured system has a privileged variable order; the random system has
none, which is what "no core to find" should look like.

**Mechanism, read off the solver source, not inferred.** In
`inputs/TRIMOSKA-WDSAT-2024/upstream/src/wdsat.c` the default branching
sequence is literally the index order: with `__XG_ENHANCED__` defined (it is, in
the shipped `config.h`), `nb_min_vars = dimacs_nb_unary_vars()` and
`set[j-1] = j` for `j = 1..nb_min_vars`, and `wdsat_solve_rest` descends
`set[0], set[1], …`. There is no dynamic heuristic — no activity, no VSIDS — so
the generator's emission order *is* the branching order. That indices
`1..ml` are the core variables is not my inference: the committed `.sing`
ring lists `x_1_0 … x_3_4` before every `e_*` variable, and the run's own P3(a)
identity check (`-g 1..ml` reproducing the default's conflict count on 60/60
instances) only makes sense if that prefix is the core. A uniform relabelling
scatters them, and the
solver can no longer branch core-first even though the core, the linking
equations and the monomial structure are all still there (the relabelled system
has the same 460 distinct non-unary monomials as the original, against the
null's 898).

**What this means, in the plan's own words.** The plan states the consequence
of this failure: "P6 as a structure claim is not supported by this design; the
evidence record records P6 as 'null objects are slower' without the mechanism
reading, and P3b/P6 are merged into one finding about variable order." My
measurement meets its failure signature, so that consequence is triggered. Put
positively and within my scope: on this instance, the structured-vs-null
conflict gap of 246× is reproduced, to within a factor of two in the median, by
relabelling the structured instance alone. The null comparison therefore cannot
separate "descended structure" from "an index order that exposes the core"; the
two are confounded in this design. This does **not** say the structure is
irrelevant — the structured system remains cheaper per conflict (1.7 µs/conflict
at seed 1661197 against 5.9 µs/conflict for the null) and one order in ten was
still within 4× of the shipped order — it says that P6's comparison, as
designed, does not isolate it. Composing this into the P3b and P6 records is
the Coordinator's; I own neither prediction.

## 5. Secondary cross-check against RUN-ICPERF-4ec9b9 — read only after the above

I opened the rerun only after sections 1–4 were measured and written. It is
corroboration, not a substitute: re-executing the producer's own harness
reproduces a wrong-but-self-consistent implementation faithfully, which is the
one failure mode my own re-implementation is there to catch.

| quantity | my own measurement | RUN-ICPERF-305ca3 | RUN-ICPERF-4ec9b9 |
| --- | --- | --- | --- |
| n15l5-1-S default | SAT / 26 | SAT / 26 | SAT / 26 |
| n15l5-11-U default | UNSAT / 31257 | UNSAT / 31257 | UNSAT / 31257 |
| n19l6-1-S default | SAT / 5312 | SAT / 5312 | SAT / 5312 |
| n19l6-11-U default | UNSAT / 255958 | UNSAT / 255958 | UNSAT / 255958 |
| null n15l5-11-U | UNSAT / 7,697,173 | UNSAT / 7,697,173 | UNSAT / 7,697,173 |
| Macaulay2, 32 rows | `bad_alloc` reproduced under 6 GiB AS | 32 × `infrastructure_exit_-6` | 32 × `infrastructure_exit_-6` |
| Singular, 4 rows | 300 s probe did not finish | 4 × `budget_stop_timeout` @ 900 s | 4 × `budget_stop_timeout` @ 900 s |

The rerun agrees with both the original run and with me on every deterministic
quantity I checked. Note that it also carries both defects of section 2 — its
32 Macaulay2 rows abort the same way, and its scripts contain the same
`convert.py` line — so the rerun does not repair the Gröbner column.

## 6. Unexpected observations (AGENTS.md rule 8)

1. **The `gens_` parse error in all 32 committed `.m2` scripts**, from
   `convert.py` lines 51–54. Independent of the memory limit; it alone would
   have zeroed the Macaulay2 column. §2.
2. **Unconstrained peak RSS (6.71–6.82 GiB) exceeds the contract's 6 GB child
   budget** on n15l5-1-S, so lifting `RLIMIT_AS` is necessary but not
   sufficient to measure P2. §2.
3. **`slimgb` computes the same Gröbner basis in 167 s** where `std` exceeds
   900 s, and it agrees with Macaulay2's F4 on `gb_size = 43`, `maxdeg = 2`,
   non-unit. The Gröbner column is measurable on this host with the contracted
   budget; it was not measured. §3.
4. **`bench.py`'s version probe hangs whenever stdin never reaches EOF**, which
   is why the run cannot name its Singular version. Reproduced under a pty. §3.
5. **WDSat's branching order is the ANF's index order, statically** — a
   two-line fact in `wdsat.c` that makes the relabelling control a direct probe
   of the solver's decision sequence. §4.
6. **The conflict count of a single structured instance spans 361× across
   variable orders** while its matched null spans 2.14×. §4.
7. **A queue-record inconsistency**: the dispatch entry for this task carries a
   top-level `joints_assigned: [V1, V2, V3, V4, V5, proves_too_much]` inherited
   from the pre-split task, while `handoff.joints_assigned` is `[V2]` and the
   split addendum's `owners` map assigns V2 to me and everything else to
   TASK-20260913-6c5729. I followed the handoff and the addendum, and report
   the control separately because the dispatching instruction routed it here.
   The stale top-level list should not be read as a second owner for V1/V3/V4/V5.

## 7. Limitations and scope

- V2(a) covers the four rows the plan names, not all 288 WDSat rows.
- §2 is one instance (n15l5-1-S) on one host with one Macaulay2 (1.22). Peak
  RSS for n17l6 and n19l6 is unmeasured and is likely larger.
- §3's `slimgb` and `no redSB` probes are one instance each, bounded at 300 s;
  the `std` rows remain right-censored lower bounds, and no Gröbner engine's
  *completion time* on these systems is established for any cell.
- §4 is one instance (n15l5-11-U), one engine config (`default`), one label
  (U), 10 relabelling seeds and 3 null relabelling seeds. Whether the same
  collapse occurs on S instances, at l = 6, or under `-x`/`-b`/`-g` is not
  measured here.
- Wall times throughout are load-dependent; loadavg at start is recorded per
  row. Conflict counts are deterministic and reproduce exactly.
- Nothing in this report changes a record's status, and nothing supports or
  weakens any prediction. No evidence or decision record is written; nothing is
  committed to git.

## 8. Artifact index (all under this task directory)

| path | what |
| --- | --- |
| `artifacts/v2_rows_index.json` | all 29 child processes: argv, loadavg at start, wall, cpu, VmPeak/VmHWM, rc |
| `artifacts/v2a_wdsat_reruns.json` | the four WDSat rows |
| `artifacts/anf_sizing_independent.txt` | my sizing derivation vs the run's `wdsat_constants` |
| `artifacts/v2b_m2_C1_C2.json`, `…C3_C5.json`, `…C6_C7.json` | the six Macaulay2 executions |
| `artifacts/m2_reportfix.diff` | the two-line repair, showing the ideal is untouched |
| `artifacts/v2c_singular_probe.json` | 300 s committed-script probe with memory trajectory |
| `artifacts/v2c_singular_fairness.json` | `no redSB` (300 s, unfinished) and `slimgb` (167 s, finished) |
| `artifacts/v2c_version_probe_stdin.json` | the stdin reproduction of the version-probe hang |
| `artifacts/m2_vs_singular_system_equivalence.txt` | M2 ↔ Singular system comparison, 4 instances |
| `artifacts/ptm2/` | 10 permuted objects + identity object + 3 permuted nulls, each with its pre-check record |
| `artifacts/ptm2_wdsat_runs.json`, `ptm2_null_and_identity.json`, `ptm2_analysis.json` | the control's runs and statistics |
| `logs/*.out`, `logs/*.err` | raw stdout/stderr of every child, including the failures |
| `work/*.py` | every tool I wrote; none imports the producer's code |
