# Design: TASK-20260814-8bbdd2 -- discard-prefix repeat of the T=20,000 matched-pair extension on shards 5000/6000

Pre-registered BEFORE any data is generated, per handoff `ledger/handoffs/TASK-20260814-8bbdd2.yaml`
constraint "PRE-REGISTER BEFORE RUNNING." `matched_pair_repeat.py`'s driver
implements exactly this document, in this order, and
`matched_pair_repeat_results.json` is written strictly after the run
completes. This document predates that results file (verifiable via
filesystem mtimes and git history in the task's own commit).

Authorized by `ledger/decisions/DEC-20260809-186c86.yaml` next_actions (the
Coordinator's scaling-characterization task, adopting the Red Team's named
counterexample from `ledger/evidence/EV-HQC-3a0372.yaml` observation O8), and
dispatched by `coordination/goals/GOAL-HQC-001/batches/BATCH-0e126d/dispatch_queue.json`
task `TASK-20260814-8bbdd2`, handoff `ledger/handoffs/TASK-20260814-8bbdd2.yaml`.

Claim tier: **TOY, hard ceiling.** PS-R3 reduced parameters only
(`n=7187, n_e=56, n_2=128, dup=1, N=7168`, `m_load_bearing_order=17`). One
defect class (V3, last-block-window-read-early), one injection point
(`decode_blocks`'s block window, last block only, index `n_e-1`). Nothing
here is a statement about HQC's IND-CCA security, its decoding-failure rate,
assumption A17 or A5, or any standardized parameter set. Standardized-
parameter runs are OUT OF SCOPE and unauthorized. The Executor reports
observations only; the Coordinator/Validator/Red Team apply
DEC-20260809-186c86's framing (shard-specific vs. general refutation) to the
number this task supplies.

## 1. What is reused, unmodified, read-only, sha256-pinned

- `coordination/goals/GOAL-HQC-001/batches/BATCH-6fddee/tasks/TASK-20260806-64b506/stage_a.py`
  (expected sha256 `06a0a618432c00fe26c72ecf05a8d89489db61c5183931fdb76a378717681405`) --
  `PARAM_SETS`, `sha_key`, `CTRStream`, `fixed_weight_support`, `ring_mul_sparse`,
  `decode_blocks`, `_t_shard`, `hist_of`, `batch_hists`, `evaluable_k`,
  `N_JACK_BATCHES` (200), `T_STAB_THRESHOLD` (30), `MASTER_SEED` (20260804).
- `coordination/goals/GOAL-HQC-001/batches/BATCH-0a65c0/tasks/TASK-20260806-cde749/measure.py`
  (expected sha256 `a4fd1ecb63f0ddc83c02ef45f2c65ab31cf13d13e7ae94f500e67465b24f5dc8`) --
  `comb_matrix`, `log2_A_from_hists`.
- `coordination/goals/GOAL-HQC-001/batches/BATCH-412513/tasks/TASK-20260809-a79e4f/matched_pair.py`
  -- NEW to this task family, imported read-only via the identical
  `load_module()` fail-closed pattern. Its sha256 is measured at run time
  (not fabricated) and recorded in `run_manifest.yaml` /
  `matched_pair_repeat_results.json.provenance`; this task does not
  pre-declare an expected value for it (none was published before this task
  existed), but the loader still fails closed against silent modification
  *during* this task's own execution by comparing the hash it measures at
  load time against the hash it measured at the very start of the script
  (a self-consistency pin), and the measured value is what future tasks in
  this family should cite as the pin.
  Reused directly, verbatim, not re-derived: `make_defected_decode_blocks`,
  `matched_pair_stats`, `arm_hists`, `cell`, `load_module`, `sha256_file`,
  `core_seconds`, `git_state`, and additionally `run_arm` (the warmup-then-
  timed-call wrapper around `sa._t_shard`) and the two fail-closed selftest
  functions `selftest_fail_closed_sha_mismatch` /
  `selftest_injection_invariant_fail`, all called with `n_trials=15000`
  where `matched_pair.py` itself used 5000 -- `run_arm`'s signature already
  takes `n_trials` as a parameter and is not hardcoded to any particular
  count, so this is the same code path, not a modified copy.
- `coordination/goals/GOAL-HQC-001/batches/BATCH-412513/tasks/TASK-20260809-a79e4f/matched_pair_results.json`
  -- read-only, for two purposes: (a) `stage_1.per_trial_S.shard_5000_defected`
  / `shard_5000_undefected` / `shard_6000_defected` / `shard_6000_undefected`,
  the committed per-trial arrays this task's discarded prefix must reproduce
  bit-identically; (b) `stage_1.matched_pair.primary_cell_k17.{shard_5000,
  shard_6000,pooled}.se_paired`, the T=5,000 and T=10,000 reference SE points
  for the exponent refit in Section 5.

The only genuinely new code in `matched_pair_repeat.py` is: the
discard-prefix driver (one `run_arm` call per (shard, variant) at
`n_trials=15000`, slicing `[0:5000)` vs `[5000:15000)` from the returned
per-trial arrays), the disjointness self-check (Section 3), and the
`F[:, 0:n_e-1]` structural invariant check (Section 4). The matched-pair
jackknife statistics themselves are computed by calling `matched_pair.py`'s
own `arm_hists` / `matched_pair_stats` / `cell` on the retained tail slices,
not by re-deriving the formulas.

## 2. The discard-prefix technique and why it is necessary

`stage_a.py`'s `_t_shard` has no trial-offset parameter: every call's inner
loop indexes trials as `ti = t + i` for `t` starting at 0 (`stage_a.py`
lines ~496-501, verified by reading the function body directly, not taken on
the handoff's word), and each trial's `CTRStream` domain tag is
`b"v<k>" + ti.to_bytes(8, "little")` -- a pure function of
`(shard, trial_index, variant-independent key)`. There is no way to ask
`_t_shard` for trial indices `[5000, 15000)` directly without either editing
`stage_a.py` (prohibited: it is imported read-only and sha256-pinned) or
calling it once with `n_trials = 15000` and discarding the leading 5,000
trials, which are *exactly* `TASK-20260809-a79e4f`'s already-consumed range
on shards 5000/6000 (its `N_TRIALS_STAGE1 = 5000`, trial indices `0..4999`).

No alternative that avoids editing `stage_a.py` was found during design
(consistent with the handoff's instruction to report if one is found; none
is reported here -- see Section 7, "protocol deviations: none of this
kind").

**Constants, fixed here, before any data exists:**

- `N_DISCARD_PREFIX = 5000`
- `N_NEW = 10000`
- `N_TOTAL_PER_CALL = N_DISCARD_PREFIX + N_NEW = 15000`
- Shards: **5000** and **6000** (the same two shards `TASK-20260809-a79e4f`'s
  stage 1 used, per DEC-20260809-186c86's adopted Red Team design)
- Retained slice: **`[5000:15000)`** of each call's per-trial arrays
  (10,000 trials per shard, 20,000 pooled across both shards -- matching
  `TASK-20260809-a79e4f` stage 2's `T2 = 20,000`)
- Discarded slice: **`[0:5000)`** of each call's per-trial arrays --
  computed (never skipped) so the disjointness self-check (Section 3) can
  run, but excluded from every statistic in Section 5/6
- Primary cell: **k = m = 17**
- k range reported: **2..26**, intersected with each arm's own
  `sa.evaluable_k` reachable range (floor 30 trials with `S >= k`), exactly
  as `matched_pair.py`

**Exactly one call per (shard, variant):** `sa._t_shard((ps, shard, 15000,
WALL_CAP_PER_CALL, BATCH, 0))` (via `matched_pair.py`'s `run_arm` wrapper,
which also runs a 300-trial throwaway warmup call on the same shard first,
identical discipline to `matched_pair.py` itself -- the warmup consumes no
shared PRNG state with the timed call, since `CTRStream` is keyed
per-`(shard, trial_index)` and each `_t_shard` invocation is independent).
Four calls total: `(5000, defected)`, `(5000, undefected)`, `(6000,
defected)`, `(6000, undefected)`. A second, independent call at `n_trials=
10000` starting "fresh" is explicitly NOT used anywhere in this script --
that would silently re-derive trial indices `[0, 10000)`, which overlaps
`TASK-20260809-a79e4f`'s already-consumed `[0, 5000)` and does not supply a
disjoint range at all. This is the handoff's own stated failure mode and
this design avoids it by construction (single call, `n_trials=15000`,
slice after the fact).

## 3. Disjointness self-check (FAIL-CLOSED, run before any statistic is computed from the retained tail)

For each of the 4 `(shard, variant)` calls:

1. Slice `S_prefix = S_full[0:5000]` from that call's per-trial `S =
   F.sum(axis=1)` (`F` is `_t_shard`'s returned per-trial block-failure
   array, `(15000, n_e)`).
2. Compare `S_prefix` **elementwise**, trial-by-trial, to the corresponding
   committed array in `TASK-20260809-a79e4f/matched_pair_results.json`
   (`stage_1.per_trial_S.shard_<shard>_<variant>`) via `np.array_equal`.
   This is the strongest available check (per-trial identity, not merely
   histogram identity) and is run first.
3. As a second, redundant confirmation matching the handoff's literal
   wording, also compute `sa.hist_of(S_prefix, n_e)` and compare it
   elementwise to `sa.hist_of(committed_array, n_e)`.

**Fail-closed rule:** if any of the 4 elementwise comparisons (or, as a
secondary confirmation, any of the 4 histogram comparisons) is not
bit-identical, the run ABORTS immediately: no matched-pair statistic is
computed from the retained tail of any call, and the run is reported
`invalid_measurement` / `infrastructure_error` per AGENTS.md rule 5 -- never
as a result about the mathematics. All 4 checks must independently pass
before Section 4 or Section 5/6 proceeds.

## 4. F[:, 0:n_e-1] structural invariant (new standing invariant, FAIL-CLOSED)

For each shard (5000, 6000) separately, on the **retained** 10,000-trial
tail slice `F_tail = F_full[5000:15000]` of both variant calls on that
shard: assert `F_defected_tail[:, 0:n_e-1] == F_undefected_tail[:, 0:n_e-1]`
elementwise, for every retained trial and every one of the `n_e - 1 = 55`
non-last blocks. `decode_blocks` operates per-block independently and the
V3 defect construction only overwrites the last block's bit window
(`lo:hi` at `n_e-1`), so this is a free structural check, at the array
level rather than only at the level of the lossy row-sum `S`, of the
"zero new entropy between variants outside the injected block" claim
(EV-HQC-3a0372 O11). Report the total mismatch count (expected 0) and a
PASS/FAIL verdict per shard. A FAIL is `infrastructure_error` /
`invalid_measurement`, not a result about the mathematics, per AGENTS.md
rule 5, and blocks any conclusion being drawn from this task's diff/SE/z
numbers (though it does not itself invalidate the disjointness check in
Section 3, which is independent).

`F` is retained in full (not discarded down to `S = F.sum(axis=1)` the way
`matched_pair.py` does) specifically so this comparison is possible.

## 5. Matched-pair statistics on the retained tail

Using `matched_pair.py`'s own `arm_hists` and `matched_pair_stats` (imported
read-only, not re-derived), on the 10,000-trial retained tail of each of the
4 calls:

- `H_<shard>_<variant>, B_<shard>_<variant> = arm_hists(sa, S_tail, n_e, NB)`
  with `NB = sa.N_JACK_BATCHES = 200`.
- Per shard: `ks_<shard> = evaluable_k(H_defected) ∩ evaluable_k(H_undefected)
  ∩ [2, 26]`; `stats_<shard> = matched_pair_stats(measure, n_e, ks_<shard>,
  C_<shard>, H_defected, B_defected, H_undefected, B_undefected)`.
- Pooled: `H_pooled_def = H_5000_def + H_6000_def` (and symmetrically for
  undefected); `B_pooled_def = concat([B_5000_def, B_6000_def], axis=0)`
  (and symmetrically); `ks_pooled = ks_5000 ∩ ks_6000 ∩ [2, 26]`;
  `stats_pooled = matched_pair_stats(measure, n_e, ks_pooled, C_pooled,
  H_pooled_def, B_pooled_def, H_pooled_undef, B_pooled_undef)`.

This is bit-for-bit the same jackknife construction `TASK-20260809-a79e4f`
used (leave-one-batch-out on the per-batch DIFFERENCE, paired SE via
`jack_se`, unpaired SE via independent-arm quadrature, ratio
`SE_unpaired/SE_paired`), because it is the same function, called on
different input arrays.

Reported per shard and pooled, at k=17 and across the full evaluable
k=2..26 range: `diff` (defected - undefected point estimate),
`SE_paired`, `SE_unpaired`, `unpaired/paired ratio`, `z_paired`,
`z_unpaired`.

## 6. Fitted SE-vs-trial-count exponent refit (secondary, reported descriptively, no conclusion drawn)

Three points, all at k=17, all on shards 5000/6000 (never shards 8001/8002):

1. `T = 5,000`: the arithmetic mean of shard 5000's and shard 6000's own
   `se_paired` at k=17 from `TASK-20260809-a79e4f`'s **committed** stage 1
   result (`matched_pair_results.json.stage_1.matched_pair.primary_cell_k17.
   {shard_5000,shard_6000}.se_paired`) -- read, not re-measured.
2. `T = 10,000`: `TASK-20260809-a79e4f`'s committed stage 1 **pooled**
   `se_paired` at k=17 (`...primary_cell_k17.pooled.se_paired`) -- read, not
   re-measured.
3. `T = 20,000`: this task's own pooled `se_paired` at k=17, from Section 5.

Fit `log(SE) = log(c) - alpha * log(T)` by OLS (`numpy.polyfit` degree 1),
report `alpha = -slope`, exactly as `matched_pair.py`'s own stage-2 fit
does. `alpha in [0.4, 0.6]` is the pre-registered 1/sqrt(T)-consistency band
from `DEC-20260809-46e85c` design.md Section 5, carried forward unchanged;
this task draws no conclusion about which side of that band the fitted
value falls on, or about which of DEC-20260809-186c86's two named outcomes
(shard-specific vs. general refutation) obtains -- that is Coordinator /
Validator / Red Team judgment, per the handoff.

## 7. Fail-closed checks and protocol notes

- sha256 pin mismatch selftest (`matched_pair.selftest_fail_closed_sha_mismatch`,
  reused verbatim), run once before any real module load.
- Injection-invariant mismatch selftest (`matched_pair.selftest_injection_
  invariant_fail`, reused verbatim), run once after `n_e`/`n_2` are known,
  before any real trial is decoded.
- D2 (exact generation weight) and D3 (support cap) hard invariants, read
  from every `_t_shard` call's own `d2_fail` / `d3_fail` counters, checked
  over the **full 15,000-trial call** on all 4 calls (not sliceable by
  trial range, per the handoff) -- expected 0 on all 4.
- The real injection wrapper's own per-call invariant check
  (`make_defected_decode_blocks`, reused verbatim), fail-closed on every
  batch of every defected-arm call.
- No alternative to the discard-prefix technique that avoids editing
  `stage_a.py` was found; this is stated as a finding per the handoff's
  instruction, not glossed over.
- Write scope: this task writes only under
  `coordination/goals/GOAL-HQC-001/batches/BATCH-0e126d/tasks/TASK-20260814-8bbdd2/`.
  `experiments/EXP-HQC-982268/specification.yaml`, `stage_a.py`, `measure.py`,
  `TASK-20260809-a79e4f/matched_pair.py`, and every ledger record are opened
  read-only only, never written.

## 8. Validity criteria (mechanically checkable, fixed here before the run)

This run is `valid_measurement` iff, in order:

1. Both fail-closed selftests PASS.
2. The disjointness self-check (Section 3) PASSES on all 4 calls (both the
   elementwise per-trial comparison and the histogram comparison).
3. D2/D3 are clean (0) on all 4 calls (full 15,000-trial call each); no
   call was truncated by its wall-clock cap.
4. The injection wrapper's `__wrapped_original_id__` matches
   `id(original_decode_blocks)` on every construction.
5. The F[:, 0:n_e-1] structural invariant (Section 4) PASSES on both
   shards (0 mismatches).
6. The pooled estimator returns a finite `log2_Ahat_17` diff and a finite,
   positive `SE_paired` at k=17 on the retained tail.

If (2) fails: ABORT before any statistic in Section 5/6 is computed;
`invalid_measurement` / `infrastructure_error`. If (5) fails: report the
mismatch but do NOT abort the disjointness-verified statistics computation
in Section 5/6 (Section 3 and Section 4 are independent checks over
different data), but the run's overall validity is `invalid_measurement`
and no scaling-characterization number is reported as reliable; this
asymmetry (Section 3 abort-before-compute vs. Section 4 compute-then-flag)
mirrors the handoff's own framing of the two checks as testing different
things (disjointness of THIS task's own new draws vs. a structural claim
about the injection mechanism) and is stated here in advance rather than
decided after seeing the data.

## 9. Budget

500 core-seconds, 1,800 wall-clock seconds, maximum 2 runs -- authorized by
the handoff / dispatch queue. Expected use ~30-90 core-seconds by arithmetic
on the committed ~2,100 trials/core-second throughput applied to 60,000
total trial-decodes (4 calls x 15,000 trials, of which 40,000 are analyzed
and 20,000 are the discarded-but-computed prefix), plus 4 x 300 = 1,200
warmup trials. Actual spend is measured and reported in `run_manifest.yaml`
and `matched_pair_repeat_results.json`, never estimated after the fact.
