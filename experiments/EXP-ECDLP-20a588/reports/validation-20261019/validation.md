# Independent validation: EXP-ECDLP-20a588 (block elimination order on the chain arm, m = 3)

Validator report id (provisional, random suffix; the Coordinator archive task may reassign): `VAL-20261019-e750db`.
Machine-readable twin: `validation_report.yaml` (same directory).

**Overall verdict: PASSED** — the receipt is admissible evidence for the narrow, toy-scale measurement it records.
It does not support an ECDLP claim, demonstrate a speedup, or authorize promotion. Non-blocking CONCERNS are listed per check.

## Snapshot and independence

* Repo `claude/p256-ecdlp-factor-base-wq59m1`. The task named the snapshot "HEAD includes the run records" = `bb3da2694e`. While I worked, HEAD advanced twice
  with producer commits: `ea3b5e9634` (analyze.py only) and `9dba3eb2b8` (reports/ + a 2-line title change in analyze.py). I validated at `9dba3eb2b8`.
  Between `bb3da2694e` and `9dba3eb2b8` nothing changed in `runs/`, `amendments/`, `specification.yaml`, `trial-plan.json`, `block_order_grid.py`
  (`git diff --stat` empty). `git status` showed no tracked modification during the re-runs (`rerun/git_dirty_tracked.txt` is empty).
  The run directories have not changed since the commits that added them (`44c5a059a9`, `1b1f8c2d02`, `fae66f77d0`).
* Order of work: frozen criteria were recomputed with my own script (`scripts/my_recompute.py`) **before** I opened `analyze.py`, the producer
  report, or `summary.json`. I read no sibling validator report. I did read the producer's `report.typ` and `summary.json` after my own
  computation, to compare (see check 3).
* Tools: msolve 0.6.5-1build2, Singular 4.3.2, Python 3.13.16, 4 vCPU Xeon 2.10 GHz — identical to the run `environment.json` files.
  All my re-runs used `taskset -c 0,1` (at most 2 cores; one 2-second helper, `chain_identity.py`, touched a third core while the two L=6 probes ran).
  The host was shared with the sibling validator, so every timing from my re-runs is informational.

## Check results

| # | Check | Result |
|---|---|---|
| 1 | Freeze and amendment discipline | **PASS** (2 minor CONCERNS) |
| 2 | Positive control, equivalence control | **PASS** |
| 3 | Frozen criteria re-derived from raw rows; analyze.py replay | **PASS**; criteria outcome stated below |
| 4 | Fairness of the A/B comparison | **PASS** with CONCERNS (scope-limiting asymmetries) |
| 5 | Re-run sample with the committed launcher | **PASS** |
| 6 | Reproducibility records | **PASS** with CONCERNS (no resource records in the receipts) |

### 1. Freeze and amendment discipline — PASS

Evidence (git commit time vs recorded `started_at`; all times UTC):

| Event | Commit | Commit time | Run `started_at` | Gap |
|---|---|---|---|---|
| spec + trial-plan + launcher frozen | `b19cbdaf66` (one commit holds all three) | 2026-10-15T23:06:30 | RUN-01: 2026-10-15T23:06:50 | 20 s before |
| AMD-01 + `trial-plan-run02.json` | `44c5a059a9` | 2026-10-16T01:07:25 | RUN-02: 2026-10-19T16:08:43 | 3 days before |
| RUN-02 launcher `run_after_restart_2.sh` | `d2d3f9ef29` | 2026-10-19T16:08:25 | RUN-02: 16:08:43 | 18 s before |
| AMD-02 + `trial-plan-run03.json` + `run_after_restart_3.sh` | `1b1f8c2d02` | 2026-10-19T16:18:39 | RUN-03: 2026-10-19T16:18:49 | 10 s before |

* `specification.yaml`, `trial-plan.json`, `block_order_grid.py` each have exactly one commit in history and no diff to HEAD. The helper files
  (`EXP-ECDLP-502ae2/msolve_grid.py`, `EXP-ECDLP-f49f75/pkm_isogeny_fb.py`) have identical content at `b19cbdaf66`, `d2d3f9ef29`, `1b1f8c2d02`, HEAD
  (sha256 prefixes `a44d2ed6…`, `df4dc941…`), and were committed before RUN-01.
* The pre-registered prediction (A_elim far below A_drl, A_elim at or above B_ms) and both criteria are in the frozen spec, before any data.
  The spec says smoke runs on seed `smoke-blk` are not data.
* Amendments change only cell list, arms, output path (`outputs/amendment_diff.out`): plan → run02 differs in `L_by_m` ({3:[3..7]} → {3:[7]}), `arms`
  (5 → `[A_elim_ms, B_ms]`, the two arms the stopping rule had not retired, verified from RUN-01 stdout: A_drl_ms and A_block_sg retired at L=5, B_sg at L=6),
  `command`/output path, and an `amendment` tag. run02 → run03 differs only in `command`/output path and the tag. Seed string, `timeout_s=600`,
  4 planted + 2 random, workers, experiment id are identical. Both AMD files record `thresholds_changed: false`, `success_or_falsification_criteria_changed: false`.
* AMD-01/-02 were filed before any L=7 data existed (RUN-01's L=7 cell wrote no rows; RUN-02 wrote none), and the trigger is infrastructure (host 7200 s limit,
  `termination.txt`: killed 2026-10-16T01:06:50Z = start + 7200 s; VM recycle), not a data-dependent choice.
* Manifest hashes: `sha256sum` recomputation matches every `files_sha256` entry (RUN-01 8/8, RUN-02 7/7, RUN-03 7/7); no unlisted files. Launcher commit in each manifest
  equals `environment.json.git_head`; `working_tree_dirty_at_launch: false` in all three (tracked files only, `--untracked-files=no`).
* CONCERN (minor): `EXP-ECDLP-8c41d7/amendments/run_after_restart_2.sh`, the script that launched RUN-02, was edited in place in `1b1f8c2d02` to point at RUN-03
  (history preserves it; RUN-03 is launched by the new `run_after_restart_3.sh`). Launcher scripts should be write-once.
* CONCERN (minor): `analyze.py` was first committed (`a658e4e8a7`, 23:07:12) 22 s after RUN-01 started; it was therefore not frozen before the run, but the
  criteria function (`criteria`/`last_ok`/`retired`) is unchanged across all later versions (diffs add multi-run support, labels, the supplementary
  bootstrap, per-arm merge). The commit message of `ea3b5e9634` cites "AMD-03", which is an amendment of the sibling experiment EXP-ECDLP-8c41d7, not of 20a588.
  Replay of the pre- and post-change analyze.py gives identical outputs (`replay_analyze_*`).

### 2. Controls — PASS

* **Positive control** (`planted_in_variety` true on every ok planted result): A_elim_ms 16/16, B_ms 16/16, A_drl_ms 8/8, A_block_sg 8/8, B_sg 12/12 — 0 false
  (`outputs/my_recompute.out`). Random-target instances (inst 4, 5) have no planted point and carry `None`, as designed.
* **Equivalence control**: `elim_equals_B` is true on all 24 instances where both msolve bases finished (L=3..6, 6 each, matching the 24 rows with both arms ok);
  absent on the 6 L=7 rows, where neither finished. 17 of the 24 have a non-trivial B basis (size > 1); 7 are the unit ideal `[1]` (random targets with no
  decomposition: L=3 inst 4,5; L=4 inst 4,5; L=5 inst 5; L=6 inst 4,5), where equality is trivially true. Singular analogue: `vdim` of A_block_sg equals that of B_sg on all 12 instances where both finished.
* **Validator's independent controls** (not the producer's code path for the verdict; `scripts/ctrl_checks.py`, outputs in `rerun/controls/`):
  1. *Variety confusion matrix.* For every triple (x1,x2,x3) in V^3 (L=3: 512 triples x 6 instances; L=4: 4096 triples x inst 0, 1, 4), with w from the chain trace, the
     checker `eval_gb_at(basis, point)` was compared with the ground truth `S_4(x1,x2,x3,xT) = 0 mod p`, for both the A_elim_ms basis and the B_ms basis:
     TP+TN only, **0 false positives and 0 false negatives** in every one of the 9 instances x 2 bases (e.g. L=3 inst 0: 22 true, 490 false). This is a
     positive and a negative control of both the checker and each basis. Off-V negative control: 200/200 off-V points rejected per instance.
  2. *Singular two-way ideal equality.* `eliminate(I_A, w) = <S_4, F_V(x1..x3)>` verified by mutual `reduce` to zero (std-based, independent of msolve) on all 9 instances.
* Dynamic-range control: see check 3 (passes).
* Invalidation rules: no planted decomposition missing from any ok basis; `elim_equals_B` false on 0 instances. No cell is invalidated.
* No 17-bit prime: m=3 primes are 599, 4111, 32831, 262271, 2098559 (10, 13, 16, 19, 22 bits; `p = k*2^L - 1 > 2^{3L}`, so bits = 3L+1); every row's `p` was checked prime,
  `p ≡ 3 mod 4`, and `p.bit_length() != 17`. No msolve result completed at 22 bits (all timeouts); msolve ok results at 10, 13, 16, 19 bits only. No row has an `rcNN` crash status (30 timeouts and 90 ok, nothing else; `outputs/structure_check.out`).
  The 12 L=7 msolve solves ended at 600.08–600.27 s (timeout kill), not by a crash.
* Instance identity: `seed`, `p`, `b` identical to EXP-ECDLP-502ae2 on 30/30 (L=3..7, inst 0..5) and to EXP-ECDLP-f49f75 on the 18 rows it covers; the chain constant `c` regenerated
  from the committed code equals 502ae2's recorded `chain_c` on 30/30 (`outputs/chain_identity.out`). `f4_max_deg` of B_ms and A_drl_ms equals 502ae2's recorded B and A arms on 36/36 comparisons (0 differences).
* Unit tests: `python3 -m unittest tools/test_pkm_isogeny_launchers.py` — 12 tests, OK in 5.4 s (`rerun/unittest.out`; it includes the checker accept/reject test, the one-constant-per-polynomial msolve quirk, and the 17-bit canary).

### 3. Frozen criteria re-derived from raw-result.jsonl — PASS

Own script (`scripts/my_recompute.py`, output `outputs/my_recompute.out`), RUN-01 + RUN-03, 30 rows, no duplicate (L, inst, arm) keys. An arm is retired in a cell when every instance timed out.

| L | p bits | A_elim_ms (ok/6, median s) | B_ms | A_elim / B | A_block_sg | B_sg | A_block / B_sg | A_drl_ms | A_drl / A_elim |
|---|---|---|---|---|---|---|---|---|---|
| 3 | 10 | 6, 0.0329 | 6, 0.0253 | 1.30 | 6, 0.121 | 6, 0.0754 | 1.61 | 6, 0.146 | 4.43 |
| 4 | 13 | 6, 0.591 | 6, 0.309 | 1.91 | 6, 7.33 | 6, 5.11 | 1.43 | 6, 9.93 | 16.81 |
| 5 | 16 | 6, 16.18 | 6, 6.99 | 2.31 | 0 (6 timeouts) | 6, 370.9 | n/a | 0 (6 timeouts) | n/a |
| 6 | 19 | 6, 411.2 | 6, 210.3 | 1.96 | (retired) | 0 (6 timeouts) | n/a | (retired) | n/a |
| 7 | 22 | 0 (6 timeouts) | 0 (6 timeouts) | n/a | (retired) | (retired) | n/a | (retired) | n/a |

* **msolve pair (A_elim_ms vs B_ms).** Jointly completed L = 3, 4, 5, 6. Median A_elim >= median B in 4/4 = 100% of jointly completed cells (0/4 cells with A < B).
  Largest L completed: A_elim 6, B_ms 6. Retirement L: A_elim 7, B_ms 7 (all six instances of both timed out at L=7).
  * Success criterion (A median below B in >= 80% of cells AND A completes an L at least B's): **NOT met** (0% of cells; the L clause alone would hold).
  * Falsification criterion (A at or above B in >= 80% of cells OR A retired at a smaller L): **MET** through the first clause (100%); the retirement clause is not met (same L).
* **Singular pair (A_block_sg vs B_sg).** Jointly completed L = 3, 4 (A_block_sg is all-timeout at L=5). A >= B in 2/2 = 100%. Largest L completed: A_block_sg 4, B_sg 5. Retirement L: A_block_sg 5, B_sg 6.
  * Success criterion: **NOT met** (0/2 cells with A < B, and A completes a smaller L).
  * Falsification criterion: **MET** through both clauses (100% of cells; A_block_sg retired at L=5 < B_sg at L=6).
* **Dynamic-range control** (median A_drl_ms / A_elim_ms >= 2 at the largest L where both complete): L=4 (the spec's named cell and the largest cell where both complete): **16.81**, L=3: 4.43. **PASS**. The instrument resolves a 17x order effect.
* Pre-registered prediction (A_elim far below A_drl but at or above B_ms): matches the measured pattern; this is an observation about the prediction, not an interpretation of the hypothesis.
* Caveat on what the L=7 rows are: 12 right-censored solves (>= 600 s), not a measured relative cost at L=7. They set the retirement L under the frozen stopping rule only.
  Observed growth per L step (A_elim: x18, x27, x25; B_ms: x12, x23, x30) is not used to project L=7.

**analyze.py replay** (HEAD version and the pre-AMD-03 version `836893f74c`, `-I`, 2 cores, `replay_analyze_*`):
the two versions produce identical `criteria.json` and `summary.json` (apart from the added p_bits/runs fields); all 20 per-(L, arm) medians and every
ratio, `jointly_completed_L`, `largest_L`, `retired_at`, and `elim_equals_B` (6/6 at each of L=3..6) agree with my numbers (`outputs/compare_with_analyze.out`: 0 differences);
the committed `reports/run-20261015T2306Z/summary.json` is equal as JSON to my replay of the HEAD analyze.py. analyze.py's `retired` is `n_ok == 0 and n_timeout > 0`, which coincides with "every instance timed out" on this data.

*Supplementary paired per-instance bootstrap* (analyze.py: 4000 Monte-Carlo resamples of the median of n = 6 paired ratios). My independent **exact** enumeration of all 6^6 resamples (no RNG, `outputs/my_bootstrap.out`)
reproduces every interval to 3 decimals: A_elim/B_ms median ratio and 95% percentile interval — L3 1.338 [1.106, 1.576]; L4 1.862 [1.822, 2.040]; L5 2.271 [2.184, 2.351]; L6 1.940 [1.782, 1.987];
A_block/B_sg — L3 1.605 [1.520, 1.637]; L4 1.418 [1.329, 1.726]; A_drl/A_elim — L3 4.568 [3.712, 4.953]; L4 16.206 [15.577, 17.905].
All 24/24 msolve paired instances have A_elim/B > 1 (exact one-sided sign test p = 6e-8), 12/12 for Singular, 12/12 for A_drl/A_elim. With n = 6 the percentile interval for a median is coarse and is bounded by the sample range;
it is supplementary and not a frozen criterion. The criteria outcome does not depend on it.

### 4. Fairness — PASS with CONCERNS

* **Same flags/timeouts.** All msolve arms: `-g 2 -v 2 -t 1`, timeout 600 s; A_elim_ms adds only `-e 3(L-1)` (block order DRL | DRL, w first). Both Singular arms run
  `option(redSB); std(I)` under the 600 s timeout, differing only in ring order (`(dp(#w),dp(3))` vs `dp`). Same prime, same S_4, same T per instance.
* **Same ideal.** Eliminated x-part of A_elim's basis equals B's reduced basis (24/24 string equality of sorted polynomials, 17 non-trivial); my independent
  confusion matrices and Singular elimination check (check 2) agree; Singular `vdim` equal 12/12.
* **Timing definition.** Both solvers: `time.monotonic()` around the whole subprocess (start-up, parse, solve, write), as recorded in `wall_s`; applied identically to all arms of a solver. Singular wall also includes an in-script `vdim`/`size`
  statistic and, on planted instances, the `subst` membership check (outside `std_ms`). The secondary `std_ms` metric gives the same conclusion: median A_block/B_sg
  1.65 (L3), 1.44 (L4) vs 1.61, 1.43 by wall time. The msolve planted check runs outside the timed region.
* **CONCERN — output asymmetry (by design, pre-registered).** A_elim_ms returns B's basis *plus* the chain-variable rows (basis size 13 vs 7, 18 vs 3, ...; F4 max degree 14/32/65/133 vs 16/24/40/72 for L=3..6).
  The experiment compares "full block-order basis of the chain encoding" with "dense DRL basis"; it does not time an A pipeline that discards the w rows early.
* **CONCERN — one configuration per solver.** One variable order and one block split per solver; no other chain orderings or `-c`/linear-algebra variants were tried. msolve's `-e` path is a less-used code path
  than plain DRL; two independent implementations (msolve F4, Singular Buchberger-type) agree in sign, which limits but does not remove that risk.
* **CONCERN — untimed preprocessing.** The dense polynomial `F_V = prod(x - v)` and the chain construction are built outside the timed region (negligible at L <= 6; it would not be at scale).
* **CONCERN — shared-host parallelism and ordering.** Up to 4 solver processes ran concurrently on 4 cores; six instances per cell run as a 4 + 2 wave, so inst 4,5 saw less contention (both arms are
  faster there: L=6 A_elim about 349 s vs 406–419 s, B_ms about 195–197 s vs 209–214 s) while being random (mostly unit-ideal) targets, so contention and instance type are confounded. Arm order within an instance is fixed
  (A_elim, A_drl, B_ms, A_block, B_sg), not randomized. Effect size is small against the ratio: planted-only A/B medians are 1.34, 1.95, 2.29, 1.98 for L=3..6, random-only 1.23, 1.85, 2.18, 1.78 — same sign everywhere.
* **CONCERN — memory.** The receipts record no memory. My probe (`rerun/memory/`, per-child `wait4` peak RSS, informational): L=5 inst 0: A_elim 142 MB vs B_ms 78 MB; L=6 inst 0: A_elim **2666 MB** vs B_ms **1321 MB** (2.0x), both far under the 12 GB advisory cap
  but growing ~17-19x per L, so memory (not only time) may bind at L=7. For L <= 4 the measurement floor (~52 MB inherited from the forking process) hides msolve's real peak.
* Selection / cherry-picking: none visible. L=7 rows were recorded as-is (all timeouts); RUN-02 wrote no rows; no row was dropped or re-run selectively (no duplicate keys; stdout.log lines equal the raw rows 24/24 and 6/6).

### 5. Re-run sample (committed launcher `block_order_grid.py`, HEAD `9dba3eb2b8`, 2 workers on cores 0,1) — PASS

Sample: m=3, L=3 inst 0–5 and L=4 inst 0,1, arms A_elim_ms, B_ms, A_block_sg, B_sg (plans in `rerun/L3`, `rerun/L4`); plus A_drl_ms/A_elim_ms at L=4 inst 0,1 (`rerun/L4_drl`).

* **Deterministic fields: 144 compared, 0 differences** — `seed, p, p_bits, b, kind` per row; per arm `status, f4_max_deg, gb_size, vdim, gb_maxdeg, planted_in_variety`; `elim_equals_B` (`rerun/compare_rerun.out`).
  (Basis content and quotient dimension are not stored in the raw rows; gb_size/vdim/F4 degrees and `elim_equals_B` are the stored proxies, and my confusion-matrix and Singular-elimination controls recomputed the bases' meaning.)
* **Timings (informational only; shared host, 2 vs 4 concurrent workers).** Recorded -> re-run median wall: L=3 A_elim 33 -> 28 ms, B_ms 25 -> 20 ms, A_block_sg 121 -> 112 ms, B_sg 75 -> 77 ms; L=4 (inst 0,1) A_elim 599 -> 670 ms,
  B_ms 326 -> 299 ms, A_block_sg 7.25 -> 8.93 s, B_sg 5.46 -> 5.70 s. Per-instance A/B > 1 in all 16 re-run pairs: msolve L3 1.23–1.45, L4 2.06/2.42; Singular L3 1.39–1.66, L4 1.51/1.63.
  Dynamic range re-run at L=4: A_drl_ms/A_elim_ms = 8.8 and 19.5 (recorded 16.8 median; inst 0 noisy, 1.08 s).
* Larger-L probes with the same inputs (`rerun/memory`): L=5 inst 0 two quiet repeats A_elim 15.8 s / B_ms 7.3 s (recorded 16.5 / 6.9; an earlier probe on a busier host gave 25.8 s for A_elim — host noise of ~1.6x is real,
  the ordering never changed); L=6 inst 0 (parallel on 2 cores) A_elim 446.9 s vs B_ms 232.4 s (ratio 1.92; recorded 405.6 / 213.5 = 1.90), F4 max degrees 133 / 72 as recorded.

### 6. Reproducibility records — PASS with CONCERNS

* Present and consistent: `command.txt` (equals the plan's `command`), `environment.json` (python, platform, 4 cpus, msolve/Singular versions, git_head, git_dirty), `manifest.json` (sha256 verified, coverage statement), `started_at`, `finished_at` (RUN-01, RUN-03; RUN-02 intentionally absent and documented),
  `stdout.log` (lines match the raw rows exactly), empty `stderr.log`, `termination.txt` for the two interrupted runs (consistent with timestamps: RUN-01 killed at start + 7200 s; replaying the recorded per-solve wall times on a 4-worker schedule, the L=7 cell starts at about 5.5 ks and needs about 2 x 1200 s, so it cannot finish inside 7.2 ks, as termination.txt says). Seeds: per-row seed equals `sha256("EXP-ECDLP-f49f75/v1|m|L|inst")[:12]` on 30/30 rows; kinds (inst<4 planted) and the prime form are consistent.
  Row counts: 24 + 0 + 6, six instances per cell, arms per cell equal the stopping-rule schedule.
* CONCERN: no resource records (peak memory, CPU time, concurrent host activity) in any receipt; the run report states that a unit-test run and a short analysis shared the host with RUN-02/RUN-03 (probably harmless since every L=7 solve ended at the 600 s cap; that the cap was far from binding rests on an extrapolation of about x25-30 per L from L=6, which I use only to judge contention sensitivity, not to claim an L=7 result).
* CONCERN: `environment.json` records no host CPU model or RAM (the producer report does: 4 vCPU Xeon 2.10 GHz, 15 GB).
* CONCERN: launcher-script traceability (check 1). No `finished_at` for RUN-02 by design.
* The spec's `required_artifacts` "review report" belongs to the later evidence-review stage and is not part of this validation.

## Heuristic-validation / cost-model checks

Not a Dickman–de Bruijn or Deuring-correspondence experiment; no sampling distribution to recompute. Applicable items:
* Pre-registered prediction: present in the frozen spec before data (check 1). Sample size/seeds/procedure: in plan and per-row records; empirical statistics (medians, ratios, retirement) recomputed from raw rows (check 3).
* Scale binding: toy only — m = 3, L = 3..7, p of 10–22 bits (about 2^{3L}); no transfer to 256-bit p or to large |V| is supported by anything measured. L=7 gives only censored timeouts.
* Cost unit: seconds of process wall time, single thread per solve, 4 concurrent solves; memory not in the receipts (see check 4/6; informational RSS above). No total-expected-cost table or success-probability model is claimed.
  Nothing here is a measured bound (AGENTS.md: "Wall time is never a bound").
* Null-object control (inventor-protocol §3): no correlation/bias/excess is claimed; the closest analogues are the dynamic-range control (an order effect of 4x–17x is detected, so the instrument is not insensitive) and the equivalence control. The A/B ratio does not decay with L (1.30, 1.91, 2.31, 1.96), and its trend beyond L=6 is not measured.
* Validation ladder (inventor-protocol §6): no speedup is claimed (A is slower), so step 2's "measured ratio vs baseline on a scaled-down instance" is what this experiment records; steps 3 (real-scale partial run) is not applicable.

## Limitations (also in the YAML)

1. Toy scale; the L=7 cell is censored at 600 s for both arms and says nothing about relative cost there.
2. One variable/block-order configuration per solver; msolve `-e` and Singular `(dp,dp)` only; A's output includes the w rows by construction.
3. Parallel 4-worker timing on a shared VM; ordering of arms inside an instance not randomized; small n (6, of which 2 random targets are mostly unit-ideal); percentile bootstrap with n = 6 is coarse.
4. No resource (memory/CPU) records in the receipts; independent probe shows A_elim uses ~2x B's peak RSS (L=5, 6).
5. HEAD moved during validation (analysis/report commits only); launcher script `run_after_restart_2.sh` was edited in place; one commit message cites an amendment (AMD-03) of the sibling experiment.
6. A passed validation says the receipt is admissible. It does not decide what the evidence means for H-ECDLP-60de36; that is the evidence review.

## Files

`validation_report.yaml`, `validation.md`; `scripts/` (my_recompute.py, my_bootstrap.py, structure_check.py, extra_checks.py, ctrl_checks.py, mem_probe.py, chain_identity.py, compare_rerun.py, compare_with_analyze.py);
`outputs/` (their outputs + `amendment_diff.out`); `replay_analyze_HEAD/`, `replay_analyze_pre_AMD03/` (analyze.py replays); `rerun/` (L3, L4, L4_drl launcher re-runs, `compare_rerun.out`, `controls/`, `memory/`, `unittest.out`).
`rerun/memory/mem_L4_L5.out` is a first probe whose RSS column mixes in the Singular preprocessing child (superseded by `mem_probe.out`; kept, not deleted).
