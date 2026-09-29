# Design: TASK-20260809-a79e4f -- matched-pair reconstruction and extension at the V3/decode_blocks injection point

Pre-registered BEFORE any data is generated, per the handoff constraint
"PRE-REGISTER BEFORE RUNNING." Nothing below is discovered after seeing a
result; `matched_pair.py`'s driver implements exactly this document, in this
order, and `matched_pair_results.json` is written strictly after both stages
complete.

Authorized by DEC-20260809-46e85c (`ledger/decisions/DEC-20260809-46e85c.yaml`),
task card `coordination/goals/GOAL-HQC-001/batches/BATCH-412513/tasks/TASK-20260809-a79e4f/task_card.yaml`,
handoff `ledger/handoffs/TASK-20260809-a79e4f.yaml`.

Claim tier: **TOY, hard ceiling.** PS-R3 reduced parameters only
(`n=7187, n_e=56, n_2=128, dup=1, N=7168`). One defect class (V3,
last-block-window-read-early), one injection point (`decode_blocks`'s block
window, last block only, index `n_e-1`). Nothing here is a statement about
HQC's IND-CCA security, its decoding-failure rate, assumption A17 or A5, or
any standardized parameter set. Standardized-parameter runs are OUT OF SCOPE
and unauthorized. The Executor reports observations only; the Coordinator
applies DEC-20260809-46e85c's pre-registered decision rule.

## 1. What is reused, unmodified, read-only, sha256-pinned

- `coordination/goals/GOAL-HQC-001/batches/BATCH-6fddee/tasks/TASK-20260806-64b506/stage_a.py`
  (expected sha256 `06a0a618432c00fe26c72ecf05a8d89489db61c5183931fdb76a378717681405`) --
  `PARAM_SETS`, `sha_key`, `CTRStream`, `fixed_weight_support`, `ring_mul_sparse`,
  `decode_blocks`, `_t_shard`, `hist_of`, `batch_hists`, `evaluable_k`,
  `N_JACK_BATCHES` (200), `T_STAB_THRESHOLD` (30), `MASTER_SEED` (20260804).
- `coordination/goals/GOAL-HQC-001/batches/BATCH-0a65c0/tasks/TASK-20260806-cde749/measure.py`
  (expected sha256 `a4fd1ecb63f0ddc83c02ef45f2c65ab31cf13d13e7ae94f500e67465b24f5dc8`) --
  `comb_matrix`, `log2_A_from_hists`.
- Both files are loaded via `importlib.util`, identical `load_module()`
  fail-closed pattern to `pilot_injection.py` (BATCH-2ecaa1/TASK-20260806-77a574)
  and the Red Team's own probes. Neither file is opened for writing.
- The V3 injection wrapper (`make_defected_decode_blocks`) is copied,
  unchanged in behaviour, from `pilot_injection.py`'s own construction:
  `bits_defected[:, lo:hi] = bits[:, lo-1:hi-1]` at block `n_e-1`, with the
  identical fail-closed injection-invariant check on every call.

The only new code in `matched_pair.py` is: the injection wrapper (copied
behaviour, not logic-changed), the driver (shard/stage sequencing, JSON
I/O), and the matched-pair jackknife on the per-batch difference (Section 4
below), which does not exist verbatim in either reused file.

## 2. Stage 1: deterministic, zero-new-entropy reconstruction

`_t_shard`'s only source of randomness is `CTRStream(sha_key(ps_id, "T",
shard, MASTER_SEED), ...)`, keyed per-(shard, trial-index) -- **not** a
function of which `decode_blocks` is installed on the module at call time.
Re-invoking `sa._t_shard((ps, shard, n_trials, wall_cap, batch, 0))` twice
with the same `shard` and different `sa.decode_blocks` therefore regenerates
BIT-IDENTICAL underlying draws both times and decodes them differently --
zero new PRNG consumption, genuine matched pairs.

Four arms are run, crossing {shard 5000, shard 6000} x {unmodified
decode_blocks, V3-defected wrapper}:

| shard | variant      | role                                                         |
|-------|--------------|--------------------------------------------------------------|
| 5000  | defected     | GATE arm A -- reproduces TASK-20260806-77a574's original config |
| 6000  | undefected   | GATE arm B -- reproduces TASK-20260806-77a574's original config |
| 5000  | undefected   | CROSSED arm -- the missing half of shard 5000's pair          |
| 6000  | defected     | CROSSED arm -- the missing half of shard 6000's pair          |

`N_TRIALS = 5000` per arm, `WALL_CAP_PER_CALL = 600.0`, `BATCH = 64`,
identical constants to `pilot_injection.py`. Both variants are warmed up
(300-trial throwaway calls, both shards, both variants) before any timed
call, identical discipline to `pilot_injection.py`'s warm-up phase.

Execution order: GATE arm A, GATE arm B (determinism gate evaluated
immediately after), then CROSSED arm on 5000, CROSSED arm on 6000. The gate
is evaluated and can abort the run **before** either crossed arm consumes
any compute.

### Determinism gate (FAIL-CLOSED, run first)

Immediately after GATE arms A and B complete, assert:

```
hist_of(S_gate_5000_defected, n_e) == pilot_results.json["MEASUREMENT"]["defected"]["S_histogram"]   (bit-identical, elementwise int equality)
hist_of(S_gate_6000_undefected, n_e) == pilot_results.json["MEASUREMENT"]["undefected"]["S_histogram"] (bit-identical, elementwise int equality)
```

against the array committed in
`coordination/goals/GOAL-HQC-001/batches/BATCH-2ecaa1/tasks/TASK-20260806-77a574/pilot_results.json`.
If either comparison fails, the run ABORTS immediately: no crossed arm is
run, no jackknife is computed, and the outcome is reported as
`infrastructure_error` / `invalid_measurement` (determinism or environment
regression) per AGENTS.md rule 5 -- **never** as a result about the
mathematics. If both comparisons pass, the run reports `PASS` and proceeds.

### Matched-pair construction from the four arms

- Shard 5000 pair set: trial `i`'s defected `S` (GATE arm A) paired with
  trial `i`'s undefected `S` (CROSSED arm), same trial index, same
  underlying draws -- 5,000 pairs.
- Shard 6000 pair set: trial `i`'s defected `S` (CROSSED arm) paired with
  trial `i`'s undefected `S` (GATE arm B), same trial index -- 5,000 pairs.
- Pooled: the concatenation of both shards' pair sets, 10,000 pairs total.

### Retention requirement

Per-trial `S` (i.e. `F.sum(axis=1)` from `decode_blocks`'s output, exactly
as `pilot_injection.py`'s `arm_estimate` derives it) is persisted, in trial
order, for all four arms, inside `matched_pair_results.json` under
`stage_1.per_trial_S`. This is the exact retention gap
(`EV-HQC-dd85c1` O2) that made `TASK-20260806-77a574`'s data unpairable
after the fact; it is not repeated here.

### What stage 1 can and cannot show (stated in advance)

Under the 1/sqrt(T) assumption and the Red Team's SE of 0.1982 at T=5,000,
the pooled SE over 10,000 pairs is expected around 0.140, giving a minimum
detectable effect around 0.275 at z=1.96 -- **above** both existing point
estimates (0.1922, 0.2069). Stage 1 therefore cannot produce a null that
excludes a ~0.19-0.21 effect, whatever it observes, and is unlikely to reach
significance on its own. It is calibration and replication of the SE input
stage 2 is sized from, not the primary test.

## 3. Stage 2: matched-pair extension at a pre-registered size

Fresh, previously unused shard indices, chosen here BEFORE stage 1 runs:
**8001** and **8002**. Disjoint, by inspection, from every shard used
anywhere in this campaign's committed record: `0-3, 900, 999, 1000-1007,
4900, 4901, 5000, 6000, 7777, 7778, 424242`.

Trial-count rule, fixed in advance and not the executor's to choose:

```
T2 = clamp(round(10000 * (SE_pooled_measured * 2.80 / 0.20) ** 2), 20000, 60000)
```

where `SE_pooled_measured` is stage 1's own pooled matched-pair jackknife SE
at k=17 over the 10,000 reconstructed pairs (Section 2), `delta = 0.20`,
`z = 2.80`, floor `20000`, cap `60000`.

`T2` trials are split as evenly as possible across the two fresh shards:
`T2a = ceil(T2 / 2)` on shard 8001, `T2b = T2 - T2a` on shard 8002. Each
shard is decoded twice (unmodified, then V3-defected), consuming the SAME
underlying draws both times (identical zero-new-entropy-between-variants
mechanism as stage 1, but here BOTH variants are new sampling relative to
every prior committed shard -- "new randomness" in the handoff's sense
refers to these being previously unused shard indices, not to the pairing
mechanism, which is the same deterministic re-decode trick).

Per-shard and pooled matched-pair diff/SE/z are computed identically to
stage 1 (Section 4). No further determinism gate applies to stage 2 (there
is no prior committed measurement on shards 8001/8002 to reproduce); the
D2/D3 hard invariants and the injection-invariant check remain fail-closed
on every trial of every arm, exactly as stage 1.

### Why this size (stated in advance)

At T2 of order 3.9e4 the SE is expected around 0.069, giving a minimum
detectable effect around 0.135 at z=1.96 -- below both existing point
estimates. Both a significant detection and an effect-excluding null become
reachable for the first time in this campaign.

## 4. Primary cell, primary statistic, jackknife construction

**Primary cell: k = m = 17** (`is_prespecified_cell`), matching PS-R3's own
load-bearing order.

**Primary statistic:** `log2_Ahat_17(defected) - log2_Ahat_17(true)` on
matched pairs, with standard error from a **matched-pair jackknife
(leave-one-batch-out) on the per-batch DIFFERENCE**, computed as follows,
for any pair of arms (defected histogram total `H_d`, undefected histogram
total `H_u`, and their respective batch-histogram arrays `Bd`, `Bu` of
shape `(nb, n_e+1)` from `sa.batch_hists(S, n_e, nb)` with
`nb = min(sa.N_JACK_BATCHES, T) = 200`, batch boundaries aligned by trial
index across the two arms of a pair because both arms share the same `T`
and the same `np.linspace` partition):

```
point_k      = measure.log2_A_from_hists(H_d[None,:], n_e, ks, C)[0]
             - measure.log2_A_from_hists(H_u[None,:], n_e, ks, C)[0]
loo_d_i,k    = measure.log2_A_from_hists((H_d - Bd[i])[None,:], n_e, ks, C)[0]      for i in 0..nb-1
loo_u_i,k    = measure.log2_A_from_hists((H_u - Bu[i])[None,:], n_e, ks, C)[0]
loo_diff_i,k = loo_d_i,k - loo_u_i,k
jack_mean_k  = mean_i(loo_diff_i,k)
SE_paired_k  = sqrt( (nb-1)/nb * sum_i (loo_diff_i,k - jack_mean_k)^2 )
z_paired_k   = point_k / SE_paired_k
```

Pooling two shards' arms (stage 1's pooled row, and stage 2's pooled row):
`H_d`, `H_u` are summed across shards; `Bd`, `Bu` are the row-wise
concatenation of the two shards' own batch-histogram arrays (`2*nb` rows
total), preserving per-index pairing within each shard's own block.

This is exactly the construction the BATCH-2ecaa1 Red Team's Probe 2 uses
("a matched-pair jackknife on the per-batch difference itself"), extended
here to every `k` via `measure.log2_A_from_hists`'s vectorized form rather
than the scalar `log2_A_from_hist`, and extended to a two-shard pooled
statistic (Probe 2 used one shard only).

**Secondary, reported alongside the paired SE at every k:** the UNPAIRED SE
(independent-arm quadrature, i.e. each arm's own leave-one-batch-out
jackknife SE combined as `sqrt(se_d^2 + se_u^2)`), and the ratio
`SE_unpaired / SE_paired`, replicating the Red Team's 2.78x figure at k=17.

**k range reported:** the intersection of `sa.evaluable_k` (floor 30 trials
with `S >= k`, `T_STAB_THRESHOLD`) across every arm contributing to a given
pooled statistic, intersected with `[2, 26]` per the task card's authorized
range; k=17 must be in range for a stage to be reportable at the primary
cell.

## 5. Fitted SE-vs-trial-count exponent (secondary, reported whatever the primary outcome)

Three points, all at k=17:

1. `T = 5,000` ("per shard"): the arithmetic mean of the two individual
   shards' own matched-pair paired SE at T=5,000 (shard 5000's pair SE,
   shard 6000's pair SE) -- one representative value per trial count, not
   a fourth pooled point.
2. `T = 10,000` (stage 1 pooled): `SE_pooled_measured` from Section 2/3.
3. `T = T2` (stage 2 pooled): stage 2's own pooled paired SE.

Fit `log(SE) = log(c) - alpha * log(T)` by ordinary least squares
(`numpy.polyfit` degree 1 on `(log T, log SE)`); report `alpha` as the
fitted exponent. Consistency with `1/sqrt(T)` is `alpha` in `[0.4, 0.6]`,
declared in advance (DEC-20260809-46e85c). This is descriptive; the
Executor draws no conclusion from where `alpha` falls.

## 6. Fail-closed checks (both stages)

- sha256 pin mismatch selftest (`load_module` with a deliberately wrong
  hash argument, identical to `pilot_injection.py`'s
  `selftest_fail_closed_sha_mismatch`), run once before any real module
  load.
- Injection-invariant mismatch selftest (`selftest_injection_invariant_fail`,
  identical construction to `pilot_injection.py`), run once after
  `n_e`/`n_2` are known, before any real trial is decoded.
- D2 (exact generation weight) and D3 (support cap) hard invariants, read
  from every `_t_shard` call's own `d2_fail`/`d3_fail` counters, on every
  arm of both stages -- expected 0 on all arms (D2/D3 run upstream of
  `decode_blocks` and are not touched by a decode-only defect).
- The real injection wrapper's own per-call invariant check (identical to
  `pilot_injection.py`'s `make_defected_decode_blocks`), fail-closed on
  every batch of every defected-arm call.

Both selftests must report `PASS` before any real module load / real
injection use, exactly as `pilot_injection.py`'s `main()` gates on them.

## 7. Validity criteria (mechanically checkable, fixed here before either run)

**Stage 1** is `valid_measurement` iff: both selftests PASS; the wrapper's
`__wrapped_original_id__` matches `id(original_decode_blocks)` on every
construction; D2/D3 are clean (0) on all four arms; the determinism gate
PASSES; the pooled estimator returns a finite `log2_Ahat_17` diff and a
finite, positive `SE_paired` at k=17; no arm was truncated by its wall-clock
cap. If the determinism gate fails, stage 1 is `invalid_measurement`
(`infrastructure_error` reason: determinism/environment regression) and
stage 2 does NOT run (BRANCH D of DEC-20260809-46e85c fires, no branch
A/B/C/E is evaluated).

**Stage 2** is `valid_measurement` iff: both selftests PASS (re-run); D2/D3
clean on both fresh-shard arms; the pooled estimator returns a finite
`log2_Ahat_17` diff and finite, positive `SE_paired` at k=17; `T2` actually
run equals the pre-registered clamp formula applied to stage 1's measured
`SE_pooled_measured`, substitution shown; no arm truncated.

## 8. Budget

400 core-seconds, 1800 wall-clock seconds, 2 runs (one per stage) --
authorized by DEC-20260809-46e85c / task card. Expected use ~30-80
core-seconds by arithmetic on the committed ~2,100 trials/core-second
throughput (stage 1: 4 arms x 5,000 trials = 20,000 trials; stage 2: 2
shards x 2 variants x up to 30,000 trials/shard = up to 120,000 trials).
Actual spend is measured and reported per stage in `run_manifest.yaml`,
never estimated after the fact.
