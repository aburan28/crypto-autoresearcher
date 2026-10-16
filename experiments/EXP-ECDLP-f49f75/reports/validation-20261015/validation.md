# Validation of EXP-ECDLP-f49f75 (RUN-ECDLP-f49f75-01/02/03)

- Validation id: `VAL-20261015-1c3bff` (random 6-hex suffix; `tools/allocate_id.py` has no VAL type)
- Validator: independent Validator subagent, 2026-10-15. Not the producer.
- Machine-readable record: [`validation_report.yaml`](validation_report.yaml)
- Snapshot validated: branch `claude/p256-ecdlp-factor-base-wq59m1`, commit `d72af7cae29189e5a8066017145d4f52e8e0210f`
  (the task's snapshot). While this validation ran, HEAD moved to `21178ea64c` through two report-only commits
  (`6b084f349b` run report, `21178ea64c` review graphs). `git diff --stat d72af7c 21178ea` over runs/,
  specification.yaml, amendments/, trial-plan.json, pkm_isogeny_fb.py, analyze.py and
  ledger/hypotheses/H-ECDLP-60de36.yaml is empty, so every validated file is byte-identical at both commits.
  Tracked files were clean against HEAD.
- Scope: whether the three runs are admissible evidence, and whether the frozen criteria recompute from the raw results.
  This report does not set any hypothesis status, does not bear on P-256, and does not authorize promotion.

## Terminal verdict: `incomplete`

None of the substantive checks failed. The data, the positive control, the metric recomputation, the launcher
spot-checks and a from-scratch re-execution all hold, and the frozen **falsification** condition is met under
independent recomputation. The verdict is `incomplete`, not `passed`, because the record set the frozen
specification requires is missing items. There is no `manifest.json` in any run, no recorded artifact hashes and
no dirty-tree record. The AMD-02 fix verification left no artifact. The hand-typed amendment and termination
timestamps contradict the system-clock evidence. The unexecuted m = 3, L = 6 cell has no amendment. Each of these
can be fixed with new records (see "What would move this to passed"). None of them changes a number below.

| # | Check | Verdict |
|---|---|---|
| 1 | Amendment discipline (commit order; AMD-02 exclusion vs analyze.py) | **PASS**, with CONCERNs on record accuracy (timestamps; the exclusion is not exactly what analyze.py drops, but the difference does not matter) |
| 2 | Positive control (planted decomposition in the Groebner variety) | **PASS**: 248/248 |
| 3 | Independent recomputation of the frozen criteria | **PASS**: falsification met under both disjuncts; success not met |
| 4 | Launcher correctness and instrument symmetry | **PASS**, with CONCERNs (timer resolution at small L, concurrency, cross-language E timing; none biases A against B) |
| 5 | Reproducibility records | **FAIL** (missing manifest, hashes and dirty-tree state; unrecorded fix verification). Mitigated by this validation's hashes and re-run, which do not replace the missing records |

## Timeline (system-clock sources only: git committer dates, run `started_at`/`finished_at`, file mtimes, the `.pyc` header)

| UTC (2026-10-15) | Event | Source |
|---|---|---|
| 04:59:06 | Frozen protocol committed (`378abed`): spec, launcher, trial plan, hypothesis | git |
| 04:59:12 | RUN-01 starts at `378abed` | started_at, environment.json |
| 05:00:32 | analyze.py committed (`08eeffa`); an analysis-only file | git |
| ~06:19 | RUN-01 last row written (m = 2, L = 11) | raw-result/stdout mtime |
| 06:59:43 | RUN-01 killed by the host's 7200 s limit during m = 2, L = 12 | finished_at, termination.txt |
| 06:59:44 | RUN-01 records + **AMD-01** + trial-plan-run02.json committed (`b9ddeef`) | git |
| 06:59:54 | RUN-02 starts at `b9ddeef` (launcher blob identical to `378abed`: sha256 `b66c09c6…`) | started_at, environment.json |
| ~06:59:55–07:00:00 | RUN-02 m = 3, L = 3 cell (6 instances × about 1.4 s summed wall, 4 workers) | raw wall_s |
| 07:00:50 | Fixed launcher written and first imported. The `.pyc` header records source mtime 07:00:50 and size 14871, which is the fixed version | `__pycache__/pkm_isogeny_fb.cpython-313.pyc` |
| 07:01:14 | **AMD-02** + trial-plan-run03.json + launcher fix committed (`7b09a17`) | git |
| ~07:00–07:08 | RUN-02 m = 3, L = 4 cell (about 240 s per instance, 2 waves) | raw wall_s |
| ~07:08–08:15 | RUN-02 m = 3, L = 5 cell (about 2030 s per instance, 2 waves); stdout mtime 08:15 | raw wall_s, mtime |
| ~09:00 | RUN-02 killed during m = 3, L = 6; records committed 09:00:11 (`41a38de`) | finished_at, git |
| 09:00:25 | RUN-03 starts at `41a38de` (fixed launcher, sha256 `df4dc941…` = HEAD) | started_at, environment.json |
| 09:01:34 | analyze.py with the AMD-02 exclusion and the problem record committed (`eb150cc`). The problem record says "RUN-03 pending" | git |
| 10:21:36 | RUN-03 finishes (exit 0, 24 jobs); records committed 10:21:55 (`d72af7c`) | finished_at, stdout, git |

## Check 1: Amendment discipline (PASS, with CONCERNs)

Evidence:

- **AMD-01 came before the data it affects.** It was committed at 06:59:44, and RUN-02 started at 06:59:54. AMD-01
  says RUN-02 uses an "identical launcher commit". It does: the launcher blob at `b9ddeef` is byte-identical to the
  one at `378abed` (sha256 `b66c09c6359e6c68…`). Seed string, derivation, arms, solvers, timeout and instance
  counts in trial-plan-run02.json match trial-plan.json. Only `L_by_m` and `command` differ.
- **AMD-02 came before the data it affects.** It was committed at 07:01:14, and RUN-03 started at 09:00:25 at a
  commit containing AMD-02 and the fix. The analysis exclusion was committed at 09:01:34. RUN-03's first cell takes
  about 6.5 minutes, so the exclusion was committed before any RUN-03 row existed. The invalidation of RUN-01
  m = 2, L = 8..11 applies a pre-registered rule ("any planted decomposition missing from its Groebner variety
  invalidates that arm's cell") to data that already existed. It is not a post-hoc threshold change, and
  `thresholds_changed: false` is accurate: spec and trial-plan.json are unchanged since `378abed`.
- **RUN-02 was not touched by the fix.** RUN-02 ran the pre-fix launcher: `git_head b9ddeef`, and Python 3.13 on
  Linux uses the `fork` start method, so the pool workers kept the parent's loaded code. AMD-02 says m = 3 is
  unaffected. I verified this directly: the Singular-evaluated summation polynomial S is identical between the pre-fix
  and fixed launchers for m = 3, L = 3, 4, 5 (5 instances). For m = 2 it differs at L = 8 (inst 1), 9 and 11, and is
  identical at L = 7 and at L = 8 inst 0 (where x(T) < 46341). Singular printed **no** overflow warning in either
  version, so the wrap-around is silent (`scripts/launcher_checks.out`). The primes support the stated boundary:
  m = 2, L = 7 has p = 17791 < 46341, and L = 8 has p = 66047.
- **The AMD-02 exclusion compared with analyze.py.** AMD-02 invalidates the *Groebner arms* (A, B, C; std and
  slimgb) of RUN-01 m = 2, L = 8..11. Arm E is declared unaffected. analyze.py drops **whole RUN-01 rows** with
  `m == 2 and L >= 8`: 24 rows, which contain 120 Groebner results (L = 8: 36, L = 9: 36, L = 10: 24, L = 11: 24)
  **plus 24 arm-E results**.
  - The Groebner part matches AMD-02 exactly. `L >= 8` is the same as `L = 8..11` here, because RUN-01 never wrote
    an L = 12 row.
  - analyze.py over-excludes arm E. This changes nothing: RUN-03 re-ran E on the same instances, and seed, p, b,
    chain_c, kind, E status, group_ops, decompositions and fb_size agree on 24/24 instances
    (`scripts/compare_01_03.out`). Only E's `wall_s` for L = 8..11 now comes from RUN-03 alone.
- AMD-02's description of the failure ("planted_in_variety fell to 2/4, 1/4, 0/4, 0/4") is the arm-B series. Arm C
  was 3/4 at L = 8 and 0/4 at L = 9, and arm A was 2/4 at L = 8. The invalidation covers every Groebner arm, so this
  imprecision has no effect.

CONCERNs:

- **C1.1 The hand-typed timestamps contradict the system clock.**
  - AMD-01 says `filed: 07:05Z`, but the commit containing it is 06:59:44.
  - AMD-02 says `filed: 07:20Z`, but its commit is 07:01:14.
  - RUN-02 termination.txt says the four fix-verification solves ran "07:15–07:20Z" and overlapped "the m = 3,
    L = 3 cell". But L = 3 finished within about 6 s of the 06:59:54 start, before the fixed launcher existed
    (07:00:50).
  - On the system-clock evidence, the verification ran about 07:00:50–07:01:14, during RUN-02 m = 3, L = 4 wave 1.
    If it really ran at 07:15–07:20, it overlapped L = 5 wave 1, and then the AMD-02 text "Verified before
    re-running…" was committed before the verification it reports. Either way a stated time or cell is wrong.
  - Commit order, which is what amendment discipline depends on, is not affected. A correction record (a new record,
    not an edit) is needed.
- **C1.2 The AMD-02 fix verification left no log or rows.** RUN-03's own planted checks (all true) and this
  validation's re-run supersede it as evidence, so nothing rests on the unrecorded solves.
- **C1.3 Coverage.**
  - m = 2, L = 12 was deferred by AMD-01. AMD-01's reasoning relied on the RUN-01 arm-A retirement at L = 9, which
    AMD-02 later invalidated. RUN-03 re-established it: 12/12 arm-A results timed out at L = 9.
  - m = 3, L = 6 was killed by the host limit and has **no amendment**. It cannot affect either criterion: arm A was
    retired at m = 3, L = 5, so no joint A/B cell is possible, and B and C have already outlasted A. The frozen
    trial plan is still not fully covered, and nothing on record says so.
- **C1.4** The amendments carry no `approved_by` field. Every commit is authored by one "Claude" identity, so
  separation between the Coordinator and the Executor cannot be checked from the records.

## Check 2: Positive control (PASS)

The positive control was recomputed from raw-result.jsonl over all non-excluded Groebner results with
`kind == planted` and `status == ok` (`scripts/recompute.out`). Every one has `planted_in_variety: true`:

| arm:solver | A std | A slimgb | B std | B slimgb | C std | C slimgb | total |
|---|---|---|---|---|---|---|---|
| true/checked | 31/31 | 31/31 | 47/47 | 47/47 | 46/46 | 46/46 | **248/248** |

- Per cell: m2L3 18/18, m2L4 22/22, m2L5–m2L8 24/24 each, m2L9–m2L11 16/16 each (arm A retired), m3L3 24/24,
  m3L4 24/24, m3L5 16/16.
- No random-target result carries a planted flag.
- For contrast, the excluded RUN-01 rows show the control firing: L = 8 had 2/4 (A, B) and 3/4 (C); L = 9 had 1/4 (B)
  and 0/4 (C); L = 10 and 11 had 0/4.
- Not counted: three planted instances had a degenerate target (T = O). These are m2L3 inst 1 for A, B and E, m2L3
  inst 2 for C, and m2L4 inst 0 for C. The launcher records `degenerate_target` and does not resample, so those cells
  have 3 planted checks instead of 4. This is a small loss of sample, not a control failure.

## Check 3: Independent recomputation of the frozen criteria (PASS; falsification condition met)

My own script, `scripts/recompute.py`, was written from specification.yaml and AMD-01/AMD-02 before I opened
analyze.py, and does not import it.

- Rows: RUN-01 m = 2, L = 3..7; RUN-03 m = 2, L = 8..11; RUN-02 m = 3, L = 3..5.
- Excluded: the AMD-02 Groebner results.
- Per-instance total = `std_ms + fglm_ms`; the cell median is taken over all non-degenerate instances.
- "Completed" means every non-degenerate instance in the cell has `status ok`. No partial cells occur: every cell is
  either fully ok or fully timed out.

**Criterion 1: jointly completed (m, L) cells, arm A median vs arm B median**

| cell | std A / B (ms) | A/B | slimgb A / B (ms) | A/B |
|---|---|---|---|---|
| m2 L3 | 2 / 0 | sub-ms | 1 / 1 | tie at 1 ms |
| m2 L4 | 9.5 / 1.0 | 9.5 | 5.5 / 1.0 | 5.5 |
| m2 L5 | 68.5 / 2.0 | 34 | 26.5 / 4.0 | 6.6 |
| m2 L6 | 774 / 7.5 | 103 | 229.5 / 17.5 | 13 |
| m2 L7 | 13344 / 46.5 | 287 | 3138.5 / 95.5 | 33 |
| m2 L8 | 153435 / 234.5 | 654 | 77357 / 529.5 | 146 |
| m3 L3 | 437.5 / 78.5 | 5.6 | 635.5 / 35.5 | 18 |
| m3 L4 | 176155 / 5049 | 35 | 48804 / 1439.5 | 34 |

- **std:** 8 jointly completed cells; A < B in 0. A ≥ B in 8/8 (100%), all 8 strictly A > B.
- **slimgb:** 8 jointly completed cells; A < B in 0. A ≥ B in 8/8 (100%), 7 strictly, plus one tie at m2 L3, which
  is at the 1 ms timer resolution.
- **Robustness:** keeping only cells with B median ≥ 10 ms leaves std 4/4 and slimgb 5/5 with A > B, by
  13× to 654×. Planted-only medians give the same direction: std 7/7 (m2L3 drops out because of a degenerate
  instance) and slimgb 8/8.
- **Re-execution:** in this validation's re-run on an idle host, every one of the 16 (cell, solver) pairs again has
  A ≥ B.

**Criterion 2: m = 3 retirement**

| arm | L completed (both solvers, all instances ok) | largest | retired at (all instances, both solvers timed out) |
|---|---|---|---|
| A | 3, 4 | 4 | **5** (12/12 timeouts, wall 600.07–600.12 s) |
| B | 3, 4, 5 | 5 | not retired at any observed L (L = 6 killed, no rows) |
| C | 3, 4, 5 | 5 | not retired at any observed L (L = 6 killed, no rows) |

**Result against the frozen text:**

- **Success criterion** ("A below B in ≥ 80% of joint cells under both solvers AND at m = 3 A completes a larger L
  than B and C"): **not met** under either clause.
- **Falsification criterion**, first disjunct (A at or above B in ≥ 80% of joint cells, both solvers): **met**, at
  100% under std and 100% under slimgb.
- **Falsification criterion**, second disjunct (at m = 3 A is retired at an L no larger than B and C): **met**. A was
  retired at L = 5, where B and C completed every instance. Censoring at L = 6 (a host kill, not a measurement) cannot
  reverse this, because B and C's retirement L, if any, is at least 6.
- Either disjunct alone meets the frozen falsification condition. That is an observation about the frozen
  condition; the status decision belongs to the Coordinator's review.
- **Agreement with analyze.py.** After reading analyze.py, its criteria logic agrees with mine on this data:
  - It counts a cell as "jointly completed" when it has at least one ok instance (`n_ok > 0`). With no partial
    cells, that is the same as my definition.
  - Its `retired()` takes the minimum L with zero ok results and at least one timeout over any solver key. It agrees
    here.

**Null and encoding controls.** Arm C (random set, dense encoding) against arm B (same set as A, dense encoding):
the B/C median ratios are 0.93–1.27 across all timed cells and both solvers. The dense encoding does not see the
set's structure, as expected. No positive signal is claimed, so the protocol §3 decay check has nothing to test.
The A-against-B penalty *grows* with L (std 9.5× → 654× over m = 2, L = 4..8).

**Dynamic-range control.** B and C resolve the cost growth with L (m = 2 std: 7.5 → 46.5 → 234.5 → 1743 → 13604 →
107962 ms for L = 6..11). They also resolve the jump from m = 2 to m = 3 (L = 4: 1 → 5049 ms; L = 5: 2 → 344180 ms).
Cells at m = 2, L ≤ 5 are at or below the 1 ms resolution. The robustness filter above shows the criteria do not
depend on them.

## Check 4: Launcher correctness and instrument symmetry (PASS, with CONCERNs)

**Fibre encoding.** `build_chain` asserts:

- |K| = 2^L;
- every Vélu image point lies on its curve at every step;
- the kernel is exhausted after L steps;
- `len(set(V)) == 2^L` with V = {x(R + jK)};
- `chain_eval(v) == c` for every v in V.

Python asserts are active, since the command has no `-O`. Stderr is empty in all runs. Independently of the
launcher's chain code (`scripts/launcher_checks.py`, "fibre"), I recomputed from (R, K) for 18 instances
(m = 2, L = 3..8; m = 3, L = 3..5; inst 0 and 5):

- the Vélu steps (x0, t), using my own scalar multiplication and Vélu maps;
- c;
- x(R + ⟨K⟩).

All agree with the launcher, and a **brute-force F_p fibre** of the composed x-map over c equals V exactly
(|fibre| = 2^L). At ideal level ("elim"), I eliminated the w-variables from arm A's L chain equations for one point.
This gives a principal ideal of degree 2^L that equals arm B's dense minimal polynomial (m2L5, m2L7, m3L4). Across
the runs, `vdim(A) == vdim(B)` on all 94 same-instance, same-solver pairs. **Arms A and B encode the same set.**

**Same instrument for every arm.**

- All arms share one Singular script template, Singular 4.3.2 (identical version string in all three
  environment.json files), `option(redSB)` and `--ticks-per-sec 1000`.
- They share the dp → `{std|slimgb}` → `std` step and fglm to lp, with the same rtimer-timed region and the same
  600 s subprocess timeout.
- A and B share p, b, chain, factor base and target. The target RNG is seeded by `arm in 'C'`, which is False for
  A, B and E. C has its own targets, as the spec says.
- The rings are as specified: A has m·L variables (x(1..m), w(1..m)(1..L−1)) with L quadratic chain equations per
  point; B and C have m variables and one degree-2^L polynomial per point.

**Possible sources of bias other than the overflow. None found.**

- `G = std(G)` after `std`/`slimgb` falls inside the timed region for every arm. I measured this second pass
  separately (m2L6, m2L7, m3L3; arms A and B; both solvers): **0–1 ms** in every case (`scripts/secondstd.out`).
  It cannot bias A against B.
- **Wall-clock timeout against the rtimer metric.** rtimer is real time. Across all ok solves, the untimed overhead
  (startup, resultant, planted `subst`, printing) is at most 0.11 s (`wall_s − (std_ms + fglm_ms)/1000`). The
  timeouts therefore reflect std/slimgb running past about 600 s, not untimed work. fglm_ms is 0–1 ms everywhere
  (vdim is small).
- **Timeout records.** Timed-out rows keep no partial STD line, so whether std would have finished just past 600 s is
  not recorded. This is a property of the frozen instrument, not a defect. The observed growth (m = 2: A std ×11.5
  from L = 7 to 8; m = 3: ×400 from L = 3 to 4) is consistent with the retirements, but I do not use the
  extrapolation as evidence.
- **Stopping rule as implemented.** An arm is retired only if every solver key of that arm timed out on every
  instance. Retired arms were not run afterwards (A is absent at RUN-01/RUN-03 m2 L10–11). RUN-03 starts with all
  arms at L = 8, which is consistent: A was not retired at any m = 2, L ≤ 7.

**Timing integrity under the noted overlaps.** I re-executed m = 2, L = 3..8 and m = 3, L = 3..4 with the HEAD
launcher on an idle host: same seeds, 4 workers, 48 instances, 939.5 s (`rerun/`).

- All **2656/2656 deterministic fields** reproduce exactly: seed, p, b, chain_c, status, vdim, gb_size, gb_maxdeg,
  planted_in_variety, fb_size, and E's group_ops and decompositions.
- Ratios of re-run median to recorded median (`scripts/compare_rerun.out`):
  - **RUN-02 m = 3, L = 3** (the cell the termination note says was overlapped): 0.95–1.15 across all six
    arm/solver keys. A std 437.5 → 416 ms; B std 78.5 → 76.5 ms. No material inflation.
  - **RUN-02 m = 3, L = 4** (the cell the system clock says was overlapped): 0.89–0.99. The recorded wave-1 A std is
    about 5% above the re-run.
  - **RUN-03 m = 2, L = 8** (could have been contaminated if Singular children outlived RUN-02's kill): 0.95–1.15.
    No material inflation.
  - **RUN-01 cells:** within 0.94–1.10 for medians ≥ 30 ms, except m2L7 B std (46.5 → 34, 0.73) and m2L7 A slimgb
    (3138.5 → 2537, 0.81). This is mild contention in RUN-01. It moves both arms, and the A/B ratio stays above 30.
- **RUN-01 against RUN-03 at L = 8..11** (excluded rows, context only): the overflowed systems cost about the same as
  the correct ones. B and C medians are within 0.91–1.03 (RUN-01/RUN-03), and A at L = 8 is 137 s against 153 s. Neither RUN-01's
  invalid timings nor RUN-03's indicate a timing artifact.

CONCERNs:

- **C4.1** Rtimer is wall time measured with 4 concurrent workers on 4 vCPUs. Contention differs between the first
  wave (4 jobs) and the second (2 jobs), by 3–6% in the per-instance data. It applies to every arm.
- **C4.2** Comparisons at m = 2, L ≤ 5 are at the 1 ms resolution, and the criteria do not depend on them.
- **C4.3** Arm E is timed in Python wall seconds and the Groebner arms in Singular rtimer ms. The Coordinator's
  secondary prediction ("every Groebner arm slower than enumeration") therefore compares two implementations. It is
  not a frozen criterion. E is never slower than the fastest Groebner arm, but at m2 L3 both round to 0 ms.
- **C4.4** Whether Singular child processes outlived the host kills of RUN-01 and RUN-02 is not recorded. The re-run
  comparison above bounds the effect on RUN-02's first cells and RUN-03's first cell at about 15% or less.

## Check 5: Reproducibility records (FAIL as recordkeeping; mitigated)

- **Missing required artifact.** specification.yaml `required_artifacts` lists `runs/RUN-ECDLP-f49f75-01/{…,
  manifest.json, …}`. No run has a `manifest.json` or an `execution-receipt.json`. No recorded hash exists anywhere,
  so there was nothing to check with `sha256sum`. I computed the hashes and list them in `validation_report.yaml`
  (`artifact_hashes_observed`) so a Coordinator manifest can bind them.
- **Dirty-tree state not recorded.** environment.json has `git_head` only. Partial reconstruction:
  - RUN-01: launcher at HEAD; analyze.py was untracked until 05:00:32 and is not a launcher input.
  - RUN-02: the launcher working-tree file changed at 07:00:50, after the start. The fork start method keeps the
    loaded pre-fix code, and the re-run shows the deterministic outputs agree.
  - RUN-03: launcher = HEAD.
- **Environment.** sympy (1.14.0 on this host; used only for `isprime`), CPU model and RAM are not recorded. The host
  has 4 vCPUs and 15 GiB.
- **Resources.** There are per-solve `memory(2)` bytes (maximum 1.06 GB, RUN-03 m2L11 inst 1 C slimgb) and wall_s, but no
  run-level CPU time, peak RSS or host load. The contention questions in check 4 can therefore be settled only by
  re-execution, not from the record.
- **Coverage.** See C1.3: m = 3, L = 6 is unexecuted with no amendment, and m = 2, L = 12 is deferred by AMD-01.
- **Reports.** The spec requires `reports/report.md`, `cost-vs-L.svg/.png` and `report.pdf`. Present after
  `6b084f3`: `reports/run-20261015T0459Z/{report.typ, report.pdf, cost-vs-L.svg, cost-vs-L.png, summary.json,
  plot_source_analyze.py}`. The path and format differ (typ in place of md). They were committed after this
  validation began, and I did not open them. `plot_source_analyze.py` is byte-identical to analyze.py (`cmp`).
- **Fix verification** (AMD-02) left no artifact (C1.2).
- RUN-03 has no termination.txt. It exited normally (`exit=0`, 24 jobs), so none is needed.
- **Seeds and primes.** All 96 rows were recomputed: seed = sha256(`EXP-ECDLP-f49f75/v1|m|L|inst`)[:12], and p is
  the smallest prime > 2^(mL) with p ≡ 3 (mod 4) and 2^L | p + 1 (independent trial division). There are 0
  mismatches (`scripts/check_params.out`). p ranges from 7 to 23 bits.

**What would move this to `passed`** (new records only, never edits):

1. A Coordinator-committed manifest per run binding command, git_head, dirty state (stated as unknown where it was
   not recorded), environment and the sha256 values below.
2. A coverage or amendment note for m = 3, L = 6.
3. A correction record for the AMD-01, AMD-02 and RUN-02 termination timestamps and the overlapped-cell statement.
4. A note that the AMD-02 fix verification is unrecorded and superseded by RUN-03's planted checks and this re-run.

## Heuristic-validation, cost-model and protocol-ladder checks

- **Pre-registered prediction.** It is frozen in specification.yaml at `378abed` (04:59:06), 6 s before RUN-01. It
  was informed by smoke runs on seed "smoke", which are disclosed and have no records. It is the Coordinator's
  prediction, not the hypothesis.
- **No Dickman–de Bruijn or similar distributional heuristic is under test.** No correspondence sampling is used
  (`correspondence: null`), and there is no success-probability cost model. Checks 2.3 and 2.6 of the heuristic
  profile are N/A.
- **Scale binding.** The scale is toy: p of 7–23 bits, m ≤ 3, Singular std/slimgb only. The spec claims no
  extrapolation, and the hypothesis's `interpretation_limits` record that P-256 needs m = 6, L = 44.
- **Units.** Units are declared (Singular rtimer ms; E group operations plus Python wall s), and memory is reported
  per solve. The cross-implementation comparison against E is flagged in C4.3.
- **inventor-protocol §6 ladder.** N/A. No speedup or improvement is claimed; the observed direction is negative.

## Limitations of this validation

- Not a blind re-derivation. I read the launcher (needed for check 4). I opened analyze.py only after writing
  `recompute.py`.
- The re-run covered 8 of 12 executed cells. It left out m = 2, L = 9..11 and m = 3, L = 5 (hours of timeouts and
  long B/C solves). Those cells rest on the recorded data plus the parameter, seed, positive-control and
  RUN-01/RUN-03 cross-checks.
- The task card carried no `review_plan`, so no joints were assigned. I report on the five checks the task named.
- The validation id is unchecked against the full repository. A repo-wide `rg` timed out, but the suffix is random
  (`secrets.token_hex(3)`).

## Artifacts written by this validation (all under this directory; nothing else changed)

- `validation.md` (this file) and `validation_report.yaml`.
- `scripts/recompute.py` + `recompute.out`: criteria and positive control.
- `scripts/check_params.py` + `.out`: seeds and primes.
- `scripts/compare_01_03.py` + `.out`: RUN-01 against RUN-03 and the RUN-02 timing structure.
- `scripts/compare_rerun.py` + `.out`: re-run against recorded.
- `scripts/launcher_checks.py` + `launcher_checks.out`, `secondstd.out`: overflow, fibre, elimination and second-std
  checks. Run as `python3 -I launcher_checks.py <dir> <checks>`, where `<dir>` holds `launcher_prefix.py` =
  `git show b9ddeef:experiments/EXP-ECDLP-f49f75/pkm_isogeny_fb.py` and `launcher_head.py` = HEAD's launcher.
- `rerun/{plan.json, raw-result.jsonl, stdout.log, stderr.log, started_at, finished_at}`: the scratch re-execution,
  10:26:45–10:42:29Z, with the HEAD launcher (sha256 `df4dc941…`).
- `SHA256SUMS`: hashes of `scripts/` and `rerun/`.

Nothing was committed. No raw run artifact, ledger record or research status was modified.
