# Design: TASK-20260815-e61cca -- single-shard-only local exponent for shards 8001/8002 (new disjoint T=20,000 draw per shard) plus an IVW pooling alternative on already-collected data

Pre-registered BEFORE any data is generated, per handoff `ledger/handoffs/TASK-20260815-e61cca.yaml`
constraint "PRE-REGISTER BEFORE RUNNING." `shard_8001_8002_discard_prefix.py` (Part A) and
`ivw_pooling_check.py` (Part B) implement exactly this document, in this
order; both results JSON files are written strictly after their respective
scripts run to completion. This document predates
`shard_8001_8002_discard_prefix_results.json` and `ivw_pooling_check_results.json`
(verifiable via filesystem mtimes and git history in this task's own commit).

Authorized by `ledger/decisions/DEC-20260814-3f429d.yaml` next_actions
(adopting the Red Team's own named `next_concrete_action` and
`required_controls` items 1 and 3 from `TASK-20260814-a49f1c`), and
dispatched by
`coordination/goals/GOAL-HQC-001/batches/BATCH-174014/dispatch_queue.json`
task `TASK-20260815-e61cca`, handoff `ledger/handoffs/TASK-20260815-e61cca.yaml`.

Claim tier: **TOY, hard ceiling.** PS-R3 reduced parameters only
(`n=7187, n_e=56, n_2=128, dup=1, N=7168`, `m_load_bearing_order=17`). One
defect class (V3, last-block-window-read-early), one injection point
(`decode_blocks`'s block window, last block only, index `n_e-1`). Nothing
here is a statement about HQC's IND-CCA security, its decoding-failure rate,
assumption A17 or A5, or any standardized parameter set. Standardized-
parameter runs are OUT OF SCOPE and unauthorized. The Executor reports
observations only; the Coordinator/Validator/Red Team apply
DEC-20260809-186c86's framing and the shard-specific-vs-general judgment to
the numbers this task supplies.

## 1. What is reused, unmodified, read-only, sha256-pinned

- `coordination/goals/GOAL-HQC-001/batches/BATCH-6fddee/tasks/TASK-20260806-64b506/stage_a.py`
  (expected sha256 `06a0a618432c00fe26c72ecf05a8d89489db61c5183931fdb76a378717681405`,
  independently re-measured at run time -- confirmed matching before this
  document was written) -- `PARAM_SETS`, `sha_key`, `CTRStream`,
  `fixed_weight_support`, `ring_mul_sparse`, `decode_blocks`, `_t_shard`,
  `hist_of`, `batch_hists`, `evaluable_k`, `N_JACK_BATCHES` (200),
  `T_STAB_THRESHOLD` (30), `MASTER_SEED` (20260804).
- `coordination/goals/GOAL-HQC-001/batches/BATCH-0a65c0/tasks/TASK-20260806-cde749/measure.py`
  (expected sha256 `a4fd1ecb63f0ddc83c02ef45f2c65ab31cf13d13e7ae94f500e67465b24f5dc8`,
  independently re-measured, matching) -- `comb_matrix`, `log2_A_from_hists`.
- `coordination/goals/GOAL-HQC-001/batches/BATCH-412513/tasks/TASK-20260809-a79e4f/matched_pair.py`
  (measured sha256 `66266a6178eb46e0b37ec0afdb2620064db56bff82318498e2dd83af1bd1c821`,
  identical to the value TASK-20260814-8bbdd2 measured and both its reviewers
  independently re-confirmed -- this task cites that measured value as its
  own expected pin, consistent with that task's own recommendation that
  "the measured value is what future tasks in this family should cite as
  the pin") -- imported read-only via the identical `load_module()`
  fail-closed pattern. Reused directly, verbatim, not re-derived (genuinely
  imported via the `mp_mod.` namespace, never locally redefined):
  `make_defected_decode_blocks`, `matched_pair_stats`, `arm_hists`, `cell`,
  `run_arm` (the warmup-then-timed-call wrapper around `sa._t_shard`).
  **Disclosed limitation carried over from EV-HQC-469c08 O10, corrected
  here, not repeated**: `sha256_file`, `core_seconds`, `git_state` and
  `load_module` are locally re-defined in this task's driver scripts (as
  `load_module_fail_closed`), NOT imported via `mp_mod.*` -- this is the
  same structurally-forced bootstrap chicken-and-egg problem
  TASK-20260814-8bbdd2 hit (`matched_pair.py`'s own `load_module` cannot be
  called to sha256-verify-and-load `matched_pair.py` itself before it has
  been loaded), and this design states it up front in the SAME bullet as
  the correction, rather than mischaracterizing the four bootstrap
  functions as import-reused. Both scripts' local copies are byte-for-byte
  identical to `matched_pair.py`'s versions (verified below in Section 9).
- `coordination/goals/GOAL-HQC-001/batches/BATCH-412513/tasks/TASK-20260809-a79e4f/matched_pair_results.json`
  -- read-only. `stage_2.hard_invariants.shard_8001_defected/shard_8001_undefected/shard_8002_defected/shard_8002_undefected`
  (D2_violations, D3_violations, D3_cap, D3_max_w) and
  `stage_2.matched_pair.per_shard.shard_8001/shard_8002` (ks,
  point_defected, point_undefected, diff, se_paired, se_unpaired, z_paired,
  z_unpaired, unpaired_over_paired_ratio) are the committed DERIVED values
  Part A's verification call must reproduce (no raw per-trial array exists
  for these shards -- see Section 3). `stage_1.matched_pair.per_shard.shard_5000/shard_6000`,
  `stage_1.matched_pair.primary_cell_k17.pooled`, `stage_2.matched_pair.per_shard.shard_8001/shard_8002`
  and `stage_2.matched_pair.primary_cell_k17.pooled` are read for Part B's
  IVW computation.
- `coordination/goals/GOAL-HQC-001/batches/BATCH-0e126d/tasks/TASK-20260814-8bbdd2/matched_pair_repeat.py`
  and `design.md` -- read for the discard-prefix driver PATTERN and the
  general disjointness-self-check STRUCTURE; NOT copied verbatim, because
  the known data gap (Section 3) forces a materially different Part A
  disjointness check, and Part B (the IVW computation) has no analogue in
  that prior task at all.
- `ledger/evidence/EV-HQC-469c08.yaml` -- O6 (shard 5000 = 2.836, shard
  6000 = 1.402, the two already-committed single-shard exponents this
  task's new numbers complete the table alongside; cited, not recomputed),
  O7 (the four-shard SE table this task completes), O8 (the pooling-
  convention asymmetry Part B addresses).

The only genuinely new code in this task is: the discard-prefix driver for
shards 8001/8002 individually (Part A), the two-step adapted disjointness
proof (Section 3), the F[:, 0:n_e-1] structural invariant check (unchanged
technique, Section 4), the single-shard-only local exponent computation
(Section 5), and the IVW combination (Part B, Section 6). The matched-pair
jackknife statistics themselves are computed by calling `matched_pair.py`'s
own `arm_hists` / `matched_pair_stats` / `cell` on the retained tail slices,
not by re-deriving the formulas.

## 2. Part A: the discard-prefix technique and constants

`stage_a.py`'s `_t_shard` has no trial-offset parameter: every call's inner
loop indexes trials as `ti = t + i` for `t` starting at 0, and each trial's
`CTRStream` domain tag is a pure function of `(shard, trial_index,
variant-independent key, MASTER_SEED)`, independent of call boundaries or
call history (Red Team's own code trace, `TASK-20260814-a49f1c` Section 2,
treated as settled per the handoff, not re-litigated here). There is no way
to ask `_t_shard` for trial indices `[10000, 30000)` directly without either
editing `stage_a.py` (prohibited: imported read-only, sha256-pinned) or
calling it once with `n_trials = 30000` and discarding the leading 10,000
trials -- exactly `TASK-20260809-a79e4f` stage 2's already-consumed range on
shards 8001/8002 (`T2_shard_8001 = T2_shard_8002 = 10000`, independently
confirmed by direct read of the committed `matched_pair_results.json`
`stage_2.stage2_sizing_applied` block: `T2=20000, T2_shard_8001=10000,
T2_shard_8002=10000`).

**Constants, fixed here, before any data exists:**

- `N_DISCARD_PREFIX = 10000`
- `N_NEW = 20000`
- `N_TOTAL_PER_CALL = N_DISCARD_PREFIX + N_NEW = 30000`
- Shards: **8001** and **8002**, treated **INDIVIDUALLY**. No cross-shard
  pooling anywhere in Part A.
- Retained slice: **`[10000:30000)`** of each call's per-trial arrays
  (20,000 new trials per shard)
- Discarded slice: **`[0:10000)`** of each call's per-trial arrays --
  computed (never skipped), used only for the verification-call comparison
  in Section 3 (not for a direct raw-array bit-identity check, which is
  unavailable here -- see Section 3), and excluded from every statistic in
  Section 5
- Primary cell: **k = m = 17**
- k range reported: **2..26**, intersected with each arm's own
  `sa.evaluable_k` reachable range (floor 30 trials with `S >= k`), exactly
  as `matched_pair.py` and `matched_pair_repeat.py`

**Exactly one call per (shard, variant) for the real analysis data:**
`mp_mod.run_arm(sa, ps, shard, 30000, decode_fn, original_decode_blocks)`
(same warmup=300, `BATCH=64`, `WALL_CAP` discipline as every prior task in
this family). Four such calls total: `(8001, defected)`, `(8001,
undefected)`, `(8002, defected)`, `(8002, undefected)`. A second,
independent analysis call at `n_trials=20000` starting "fresh" is explicitly
NOT used anywhere for the retained-tail statistics -- that would silently
re-derive trial indices `[0, 20000)`, which overlaps the already-consumed
`[0, 10000)` and does not supply a disjoint range. This is the handoff's
own stated failure mode and this design avoids it by construction.

**In addition**, four dedicated VERIFICATION calls at `n_trials=10000`,
`mp_mod.run_arm(sa, ps, shard, 10000, decode_fn, original_decode_blocks)`,
one per (shard, variant), run BEFORE and SEPARATE FROM the four
`n_trials=30000` analysis calls -- required by Section 3's adapted
disjointness proof, since no raw per-trial array was persisted for shards
8001/8002 to check the discarded prefix against directly.

Total: 8 `_t_shard` real calls (4 verification at 10,000 + 4 analysis at
30,000), plus 8 warmup calls of 300 trials each (one per `run_arm`
invocation), matching the dispatch queue's budget note.

## 3. Part A: adapted disjointness proof (FAIL-CLOSED, weaker than TASK-20260814-8bbdd2's direct check -- named as such)

**The known data gap.** `TASK-20260809-a79e4f`'s stage 2 did NOT persist raw
per-trial S arrays or histograms for shards 8001/8002 (confirmed by direct
code read: `matched_pair.py`'s stage-2 branch, lines 617-795, never writes
an `R['per_trial_S']` key; independently confirmed above in Section "read
first" investigation that `matched_pair_results.json` has exactly one
`per_trial_S` occurrence, under `stage_1`). `TASK-20260814-8bbdd2`'s exact
disjointness-self-check (bit-identical comparison of the discarded prefix
against a COMMITTED raw array) is THEREFORE NOT AVAILABLE for shards
8001/8002.

**The required alternative, specified by the handoff, not invented here:**

*Step 1 -- verification-call-vs-committed-statistics match.* For each of
the 4 `(shard, variant)` pairs, make ONE dedicated verification call to
`_t_shard` at `n_trials=10000` (via `run_arm`, identical warmup=300,
`BATCH=64`, `WALL_CAP` discipline as the original stage-2 call), separate
from and prior to the real `n_trials=30000` analysis call. From this call,
recompute `D2_violations` / `D3_violations` / `D3_cap` / `D3_max_w` (per
arm) and, after pairing defected/undefected on each shard,
`matched_pair_stats` (`point_defected`, `point_undefected`, `diff`,
`se_paired`, `se_unpaired`, `z_paired`, `z_unpaired`, `ratio`) at every k in
2..26. Assert these match `TASK-20260809-a79e4f`'s COMMITTED `stage_2`
values EXACTLY for the D2/D3/D3_cap/D3_max_w integers, and to full float64
bit-identity for the `matched_pair_stats` arrays (`np.array_equal` /
Python `==` on the raw float64 values, no tolerance applied unless a
disclosed environment difference forces one -- see the run's own report for
the actual outcome).

*Step 2 -- within-task cross-call raw bit-identity.* Make the real
`n_trials=30000` analysis call. From THIS call's own raw per-trial S, slice
the discarded prefix `[0:10000)` and assert it is BIT-IDENTICAL,
elementwise (`np.array_equal`), to the SEPARATE verification call's own raw
per-trial S from Step 1, on all 4 `(shard, variant)` pairs.

*Step 3 -- fail-closed.* If EITHER step fails on ANY of the 4 pairs, ABORT
immediately: no matched-pair statistic is computed from that call's
retained tail, and the run is reported `invalid_measurement` /
`infrastructure_error` per AGENTS.md rule 5 -- never as a result about the
mathematics.

**Step 4 -- the limitation, stated explicitly, not silently accepted as
equivalent.** This two-step check is WEAKER than `TASK-20260814-8bbdd2`'s
direct bit-identical-array-vs-committed-record check. That task compared a
freshly generated discarded prefix directly, elementwise, against a
persisted COMMITTED raw array from a DIFFERENT prior task's run -- a
genuine cross-run, cross-session determinism proof. This task's Step 1 only
confirms that a dedicated verification call, run inside THIS SAME task's
own execution, reproduces the committed DERIVED statistics (not the raw
array itself, which does not exist to compare against); Step 2 only
confirms that the analysis call's own prefix is consistent with THIS SAME
task's OWN verification call, not with any independently-generated or
previously-committed raw data. If `_t_shard`'s trial-index-keying property
were somehow non-deterministic in a way that happened to be internally
self-consistent within one task's process but different from
`TASK-20260809-a79e4f`'s original stage-2 process (e.g. a numpy RNG version
or platform difference changing `CTRStream`'s output while leaving its
*internal* determinism intact), this two-step check would PASS while the
true correspondence to the originally-consumed `[0,10000)` domain would be
broken -- a failure mode the direct raw-array check would have caught by
comparing against the actual originally-consumed data. This gap is real,
disclosed, and not closed by this design; it is the direct consequence of
the data gap named in the handoff's `known_code_gap_note`, not a defect
introduced by this task.

## 4. Part A: F[:, 0:n_e-1] structural invariant (standing invariant, FAIL-CLOSED, needs no committed comparator)

Unchanged technique from `TASK-20260814-8bbdd2` design.md Section 4 /
EV-HQC-3a0372 O11. For each shard (8001, 8002) separately, on the
**retained** 20,000-trial tail slice `F_tail = F_full[10000:30000]` of both
variant calls on that shard (from the `n_trials=30000` analysis calls):
assert `F_defected_tail[:, 0:n_e-1] == F_undefected_tail[:, 0:n_e-1]`
elementwise, for every retained trial and every one of the `n_e - 1 = 55`
non-last blocks. Report the total mismatch count (expected 0) and a
PASS/FAIL verdict per shard. A FAIL is `infrastructure_error` /
`invalid_measurement`, not a result about the mathematics, and blocks any
conclusion being drawn from this task's diff/SE/z numbers -- though it does
not itself invalidate the Section 3 disjointness proof, which is
independent (same asymmetry as `TASK-20260814-8bbdd2` design.md Section 8:
Section 3 aborts-before-compute; Section 4 computes-then-flags).

`F` is retained in full (not discarded down to `S = F.sum(axis=1)`)
specifically so this comparison is possible, on both the verification calls
(needed for Step 1's D2/D3 recomputation from `run_arm`'s own returned
counters, not from `F` directly) and the analysis calls.

## 5. Part A: matched-pair statistics and single-shard-only local exponent

Using `matched_pair.py`'s own `arm_hists` and `matched_pair_stats` (imported
read-only, not re-derived), on the 20,000-trial retained tail of each of the
4 analysis calls, PER SHARD, NO POOLING:

- `H_<shard>_<variant>, B_<shard>_<variant> = arm_hists(sa, S_tail, n_e, NB)`
  with `NB = sa.N_JACK_BATCHES = 200`.
- `ks_<shard> = evaluable_k(H_defected) ∩ evaluable_k(H_undefected) ∩ [2,
  26]`; `stats_<shard> = matched_pair_stats(measure, n_e, ks_<shard>,
  C_<shard>, H_defected, B_defected, H_undefected, B_undefected)`.

Reported per shard (8001 alone, 8002 alone -- never pooled) at k=17 and
across the full evaluable k=2..26 range: `diff`, `SE_paired`, `SE_unpaired`,
`unpaired/paired ratio`, `z_paired`, `z_unpaired`.

**Single-shard-only local exponent, per shard, at k=17:** two points,
`(T=10000, se_paired)` read from `TASK-20260809-a79e4f`'s committed
`stage_2.matched_pair.primary_cell_k17.shard_<shard>.se_paired` (NOT
recomputed -- read only), and `(T=20000, se_paired)` from this task's own
retained tail computed in this section. `alpha = -slope` of the OLS fit
`log(SE) = log(c) - alpha*log(T)` on exactly these 2 points (`numpy.polyfit`
degree 1 on 2 points, i.e. the exact 2-point slope: `alpha = -[log(SE_20000)
- log(SE_10000)] / [log(20000) - log(10000)]`), the SAME method
`TASK-20260814-8bbdd2` used for its own 2-point single-shard exponents
(EV-HQC-469c08 O6). Computed independently for shard 8001 and shard 8002;
no cross-shard pooling anywhere in this computation.

## 6. Part B: IVW combination (no new sampling; pure recomputation on already-committed data)

For (a) shards 5000/6000 at their own committed T=5,000-each stage-1 point
estimates (`stage_1.matched_pair.per_shard.shard_5000` /
`stage_1.matched_pair.per_shard.shard_6000`) and (b) shards 8001/8002 at
their own committed T=10,000-each stage-2 point estimates
(`stage_2.matched_pair.per_shard.shard_8001` /
`stage_2.matched_pair.per_shard.shard_8002`), all read ONLY from
`TASK-20260809-a79e4f`'s already-committed `matched_pair_results.json` --
NO new `_t_shard` call is authorized or performed for Part B -- compute, at
every k in the intersection of both shards' `evaluable_k` (which Section
"read first" investigation shows is `2..26` for both pairs) and reported
first at k=17:

```
w_i        = 1 / se_paired_i^2
diff_ivw   = sum(w_i * diff_i) / sum(w_i)
se_ivw     = 1 / sqrt(sum(w_i))
```

for `i` ranging over the two shards in each pair. Report `diff_ivw` and
`se_ivw` ALONGSIDE (never replacing) the existing concatenated-histogram
pooled values at the same k (`stage_1.matched_pair.primary_cell_k17.pooled`
for (a); `stage_2.matched_pair.primary_cell_k17.pooled` for (b), and the
corresponding non-k17 cells via each stage's `per_shard.*.ks` /
`per_shard.*.se_paired` arrays for the full k range). Report the ratio
`se_ivw / se_pooled_concatenated` at k=17 explicitly for both (a) and (b).

## 7. Fail-closed checks and protocol notes

- sha256 pin mismatch selftest (`matched_pair.selftest_fail_closed_sha_mismatch`,
  reused verbatim via `mp_mod.`), run once before any real module load, in
  `shard_8001_8002_discard_prefix.py` only (`ivw_pooling_check.py` performs
  no sampling and does not need it, though it still sha256-pins the
  `matched_pair_results.json` file it reads).
- Injection-invariant mismatch selftest
  (`matched_pair.selftest_injection_invariant_fail`, reused verbatim), run
  once after `n_e`/`n_2` are known, before any real trial is decoded.
- D2 (exact generation weight) and D3 (support cap) hard invariants, read
  from every `_t_shard` call's own `d2_fail` / `d3_fail` counters, checked
  over the full length of every one of the 8 calls (4 verification at
  10,000, 4 analysis at 30,000) -- expected 0 on all 8, and the
  verification calls' values additionally checked against the committed
  stage-2 values (Section 3, Step 1).
- The real injection wrapper's own per-call invariant check
  (`make_defected_decode_blocks`, reused verbatim), fail-closed on every
  batch of every defected-arm call.
- USE PS-R3's PARAMETERS THROUGHOUT (n=7187, n_e=56, N=7168, k range 2..26,
  m_load_bearing_order=17), identical to every prior task in this family.
- No alternative to the discard-prefix technique that avoids editing
  `stage_a.py` was found; consistent with every prior task in this family.
- Write scope: this task writes only under
  `coordination/goals/GOAL-HQC-001/batches/BATCH-174014/tasks/TASK-20260815-e61cca/`.
  `experiments/EXP-HQC-982268/specification.yaml`, `stage_a.py`,
  `measure.py`, `TASK-20260809-a79e4f/matched_pair.py`,
  `TASK-20260814-8bbdd2/matched_pair_repeat.py`, and every ledger record are
  opened read-only only, never written.

## 8. Validity criteria (mechanically checkable, fixed here before the run)

Part A (`shard_8001_8002_discard_prefix.py`) is `valid_measurement` iff, in
order:

1. Both fail-closed selftests PASS.
2. The Section 3 two-step adapted disjointness proof PASSES on all 4
   `(shard, variant)` pairs (both Step 1's committed-statistics match and
   Step 2's within-task raw bit-identity).
3. D2/D3 are clean (0) on all 8 calls (4 verification + 4 analysis); no
   call was truncated by its wall-clock cap; every call delivered its full
   requested trial count.
4. The injection wrapper's `__wrapped_original_id__` matches
   `id(original_decode_blocks)` on every construction.
5. The Section 4 F[:, 0:n_e-1] structural invariant PASSES on both shards
   (0 mismatches).
6. Each shard's own estimator returns a finite `diff` and a finite,
   positive `SE_paired` at k=17 on its retained tail.

If (2) fails on any pair: ABORT before any statistic in Section 5 is
computed for that pair; `invalid_measurement` / `infrastructure_error`,
matching this design's Section 3 Step 3. If (5) fails: report the mismatch
but do NOT abort the disjointness-verified statistics computation in
Section 5 (Sections 3 and 4 are independent checks over different data),
but the run's overall validity is `invalid_measurement` and no
scaling-characterization number is reported as reliable -- identical
asymmetry to `TASK-20260814-8bbdd2` design.md Section 8.

Part B (`ivw_pooling_check.py`) performs no sampling and has no analogous
fail-closed data-validity gate; it is `valid_measurement` iff the source
`matched_pair_results.json` sha256-pins to the value measured at Part A's
own run start (self-consistency, since no external pin was pre-declared for
that file before it existed) and every value it reads is present and
finite.

## 9. Budget

500 core-seconds, 1,800 wall-clock seconds, maximum 2 runs -- authorized by
the handoff / dispatch queue. Expected use ~75-135 core-seconds by
arithmetic on the committed ~2,100 trials/core-second throughput applied to
roughly 160,000 total trial-decodes (4 analysis calls x 30,000 trials =
120,000, of which 80,000 are retained/analyzed and 40,000 are the
discarded-but-computed prefix; plus 4 verification calls x 10,000 trials =
40,000), plus 8 x 300 = 2,400 warmup trials. Part B performs no new
`_t_shard` calls and adds negligible spend. Actual spend is measured and
reported in `run_manifest.yaml` and both results JSON files, never
estimated after the fact.
