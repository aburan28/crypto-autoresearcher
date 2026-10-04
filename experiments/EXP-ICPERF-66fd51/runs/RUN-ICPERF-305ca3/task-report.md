# TASK-20260913-0b470b — executor report for RUN-ICPERF-305ca3

Role: executor-mechanical. Observations only. No statement below is about
any curve, about H-ICPERF-cc4847, or about what any value means; the
Coordinator decides after the validator (TASK-20260913-6c5729) has run.

Authorship: the dispatched executor subagent launched `bench.py` and its
session terminated before the run finished. `bench.py` ran to completion on
its own (`BENCH_EXIT=0`). This report and `manifest.yaml` were written
afterwards by the top-level Coordinator session in the executor-mechanical
role; every number here is copied from `results.jsonl`, `summary.json`,
`phase_log.txt`, `environment.json` or `launch_time.txt`, and the validator
is asked to recompute all of them (`manifest.yaml`, `run.inference`).

## 0. Preconditions (contract constraints)

- Frozen contract and code committed before launch: yes — commit
  `90b518384` (snapshot TASK-20260913-f8bdec) contains
  `experiments/EXP-ICPERF-66fd51/specification.yaml` and `code/`; the code
  tree hash is unchanged at the current HEAD (`2616961c8d`).
- No file under `code/` was edited.
- `uptime` / `free -g` before launch: loadavg at start 1.00 / 1.22 / 1.32
  (environment.json). Below the 2.0 threshold; launched without waiting.
- Command, exactly as frozen:
  `python3 experiments/EXP-ICPERF-66fd51/code/bench.py --run-dir experiments/EXP-ICPERF-66fd51/runs/RUN-ICPERF-305ca3 --phases A,B,C,D,E`
  followed by `python3 experiments/EXP-ICPERF-66fd51/code/summary.py <run-dir>`.

## 1. Certificate outcomes (phase A, C-CERT)

30 shipped certificates (10 per cell), 30 verified true, 0 false.
`why` on every row: `P1 + P2 + P3 has x = x_R`. No solver was gated off.

## 2. SAT answers whose verification is false, and SAT answers on U-labelled instances

Both lists are the same five rows. All five are on one instance,
**n19l6-19-U** (shipped label U).

| instance | engine | config | status | x_bits (as recorded) | verification.why |
| --- | --- | --- | --- | --- | --- |
| n19l6-19-U | wdsat | default | SAT | 001010, 010001, 100101 | x = 0x14 is not an x-coordinate on the curve |
| n19l6-19-U | wdsat | core_order | SAT | 001010, 010001, 100101 | x = 0x14 is not an x-coordinate on the curve |
| n19l6-19-U | wdsat | symmetry | SAT | 001010, 010001, 100101 | x = 0x14 is not an x-coordinate on the curve |
| n19l6-19-U | wdsat | gauss_elim | SAT | 001010, 010001, 100101 | x = 0x14 is not an x-coordinate on the curve |
| n19l6-19-U | cryptominisat5 | cnf_xor | SAT | 010001, 001010, 100101 | x = 0x22 is not an x-coordinate on the curve |

Recorded facts about these rows, without interpretation:

- The WDSat rows ran the upstream file directly
  (`inputs/TRIMOSKA-ECICB-2024/upstream/benchmarks/Xn19l6-19-U.anf`, see
  `argv`); the cryptominisat5 row ran the local CNF-XOR conversion of it.
- The three `x_bits` values are the same set in all five rows
  ({001010, 010001, 100101}); the two engines return them in different
  orders.
- `matches_shipped_certificate_as_set` is false on all five (a U instance
  ships no certificate).
- The remaining 9 U instances of n19l6 and all 20 U instances of n15l5 and
  n17l6 returned UNSAT from every finishing configuration.
- Phase D (pure CNF, upstream .dimacs regenerated with matching hash) did
  not include n19l6-19-U: the phase-D subset is instances 1-5 (S) and
  11-15 (U) per cell.

Null-object rows (`default_on_null_object`) also show `status: SAT` on
n15l5-12-U, n15l5-13-U, n17l6-11-U, n17l6-12-U. These rows carry no
`verification` block (a null object has no curve to verify against) and are
not on the shipped instance; they are listed here because the contract asks
for every SAT status on a U-labelled row name.

## 3. pure_cnf hashcheck mismatches

None. 30 regenerated `.dimacs` files, 30 `hashcheck.json` with
`match: true`; 90 phase-D rows, 90 with `pure_cnf_hashcheck.match: true`.

## 4. Rows with loadavg1_at_start > 2

125 of 504 rows. By phase: A 2, B 7, C 31, D 82, E 3. Maximum
`loadavg1_at_start` 4.55. The affected rows in A are the `symmetry` and
`gauss_elim` rows of n17l6-14-U (2.03). In B they are cnf_xor on
n19l6-13-U .. n19l6-19-U (2.01-2.07). Phase C is 31 of 32 rows; phase D is
82 of 90 rows. The per-row values are on the rows; the machine was shared
with GOAL-SEMBIN-5078bc's validator subagent during phases B-D.

## 5. Per-phase wall time

| phase | rows | host wall (phase_log.txt) | sum of row wall_s | sum of row cpu_s |
| --- | --- | --- | --- | --- |
| A | 318 | 49393.5 s | 5508 s | 5502 s |
| B | 60 | 3158.0 s | 3158 s | 3156 s |
| C | 32 | 299.4 s | 299 s | 792 s |
| D | 90 | 63693.8 s | 4657 s | 4655 s |
| E | 4 | 3600.2 s | 3600 s | 3600 s |

Host wall from launch (2026-09-13T22:58:05Z) to end of E
(2026-09-15T08:21:30Z) is 120205 s. The difference between host wall and
row wall in phases A and D is two intervals with no row activity, each
between two consecutive rows, where the VM was suspended between agent
turns: 44046 s between `default_on_null_object` n17l6-12-U and n17l6-13-U,
and 59101 s between minisat pure_cnf n17l6-12-U and cryptominisat5 pure_cnf
n17l6-13-U. These are the only two `recorded_at` gaps above 900 s. No row
has `wall_s > 2*cpu_s + 2`, i.e. no solver invocation spans a suspension.
Phase C's cpu > wall is Macaulay2 using more than one thread.

## 6. Other recorded facts the contract asks to be listed

- **Phase C (Macaulay2 F4 over ZZ/2 with field equations), 32 rows, all
  `infrastructure_exit_-6`.** stderr on every row:
  `terminate called after throwing an instance of 'std::bad_alloc'`. Row wall
  0.87-15.65 s; `max_rss_kb_children_highwater` 2644-2653 MB at exit; the
  child ran under RLIMIT_AS 6 GB. Zero Macaulay2 rows finished; P2 is
  therefore `null` on every cell.
- **Phase E (Singular std over GF(2) with field equations), 4 rows, all
  `budget_stop_timeout` at 900 s.** Zero Singular rows finished.
- **WDSat `noncore_first`**, 30 rows: 8 finished (n15l5 S 5/5, n15l5 U 2/5,
  n17l6 S 1/5), 22 timeouts at 120 s.
- **WDSat null objects**, 18 rows: 9 finished (n15l5 6/6, n17l6 3/6), 9
  timeouts at 180 s (n17l6 3, n19l6 6). All 18 have
  `shape_matches_template: true`.
- **cryptominisat5 cnf_xor**: 2 timeouts (n19l6 U) at 300 s.
- **minisat pure_cnf**: 2 timeouts (n19l6, one S one U) at 300 s.
- **WDSat default/core_order/symmetry/gauss_elim**: 0 timeouts; 60 rows each.
- `max_rss_kb_children_highwater` is the driver's RUSAGE_CHILDREN high-water
  mark and is monotone across rows; after phase C every row reports 2653 MB.
- Executor wall-clock cap: **PD-E1** — the contract's 28800 s executor cap
  was not applied. The single invocation ran unattended for 120205 s host
  time (17223 s solver time) because the executor session had terminated.
  No row was stopped or excluded by the cap.
- In `summary.json` P3, the four `*/cms_pure_cnf_over_wdsat` entries carry
  the identical value 83.50030889840438 for n17l6/S, n17l6/U, n19l6/S,
  n19l6/U. Recorded as written; not checked here.
- In `summary.json` P3, `default_wall_s` values (e.g. n19l6/S 0.0651,
  n17l6/S 0.116) differ from the `wdsat_default_wall_s` values in the
  per-cell table (n19l6/S 0.3162, n17l6/S 0.2909). Recorded as written; not
  checked here.

## 7. summary.py output, verbatim

`summary.py` stdout:

```json
{
 "P1": false,
 "P2": null,
 "P3": true,
 "P4": true,
 "P5": true,
 "P6": true
}
```

Per-cell medians from `summary.json` (`cells`), wall_s medians over
finished rows, `n` = finished rows:

| cell/label | wdsat default | core_order | symmetry | gauss_elim | noncore_first (n) | null (n) | cms cnf_xor (n) | cms pure_cnf | cadical pure_cnf | minisat pure_cnf (n) | M2 F4 | Singular |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| n15l5/S | 0.0651 | 0.0649 | 0.0328 | 0.2656 | 14.2562 (5) | 27.2847 (3) | 0.4414 (10) | 0.4668 | 0.7172 | 2.2725 (5) | none (0) | none (0) |
| n15l5/U | 0.2160 | 0.2159 | 0.0654 | 1.1183 | 114.5009 (2) | 17.2610 (3) | 9.8681 (10) | 12.5040 | 3.6272 | 7.0860 (5) | none (0) | none (0) |
| n17l6/S | 0.2909 | 0.2908 | 0.1406 | 1.8455 | 80.2237 (1) | 29.9413 (1) | 13.8022 (10) | 3.0242 | 7.3359 | 12.9997 (5) | none (0) | none (0) |
| n17l6/U | 2.3216 | 2.3214 | 0.4164 | 16.7068 | none (0) | 49.9407 (2) | 81.1419 (10) | 80.0281 | 51.7916 | 105.3739 (5) | none (0) | none (0) |
| n19l6/S | 0.3162 | 0.3162 | 0.1407 | 1.9952 | none (0) | none (0) | 21.2779 (10) | 21.3309 | 9.6440 | 65.2518 (4) | none (0) | none (0) |
| n19l6/U | 2.3471 | 2.3716 | 0.4166 | 16.5063 | none (0) | none (0) | 121.8064 (8) | 195.9794 | 56.8536 | 123.5298 (4) | none (0) | none (0) |

Prediction detail (`summary.json` `predictions`):

- P1: `n_certificates` 30, `invalid_certificates` [], `n_sat_answers` 205,
  `unverified_sat_answers` the five rows of section 2, `holds: false`.
- P2: `cells` {}, `holds: null`, note "no Groebner engine finished on that
  cell; nothing asserted".
- P3: `core_order_identity` 60 instances compared, 0 mismatching;
  `noncore_first_over_default_wall_censored` ratio lower bounds n15l5/S
  218.65, n15l5/U 555.81, n17l6/S 1034.48, n17l6/U 51.68, n19l6/S 1843.32,
  n19l6/U 50.59 (timeouts counted at their 120 s bound); `holds: true`.
- P4: gauss_elim vs default medians per cell: n15l5/S 0.2656 vs 0.0651,
  n15l5/U 1.1183 vs 0.2160, n17l6/S 1.8455 vs 0.2909, n17l6/U 16.7068 vs
  2.3216, n19l6/S 1.9952 vs 0.3162, n19l6/U 16.5063 vs 2.3471; `holds: true`.
- P5: U/S conflict ratios — WDSat n15l5 3.63, n17l6 6.69, n19l6 6.11; CMS
  cnf_xor n15l5 11.45, n17l6 3.67, n19l6 6.45; `holds: true`.
- P6: null/structured-U median conflicts — n15l5 3540911.5 / 30978.5
  (ratio 114.30), n17l6 5109609.75 / 254656.5 (ratio 20.06), n19l6 null
  median none (all 6 null rows timed out) / 255301.0, ratio null; `holds:
  true` with n19l6 `null`.

## 8. Artifacts

Listed in `manifest.yaml` `run.artifacts`. The 20 `wdsat_solver` ELF
binaries under `builds/*/` are not staged for commit; each build directory
keeps `config_used.json`, `make.log` and `src/` from which the binary is
rebuilt.
