# Design: matched-pair reconstruction and extension (PRE-REGISTERED before any run)

`TASK-20260809-a79e4f` (executor) / `BATCH-412513` / `GOAL-HQC-001` /
`EXP-HQC-982268`. Authorized by `DEC-20260809-46e85c`.

**This document is written and frozen BEFORE `matched_pair.py` is run on any
real data.** Everything below is fixed in advance. `matched_pair_results.json`
and `matched_pair_report.md` are produced afterward and must not cause this
file to be edited retroactively.

Claim tier: **toy, hard ceiling.** PS-R3 only (`n=7187, n_e=56, n_2=128,
dup=1, omega=45, omega_r=omega_e=51, N=7168, m=17`). Nothing here is a
statement about HQC, A17, its decoding-failure rate, or any standardized
parameter set.

---

## 1. What this task does and does not do

- Imports `stage_a.py` and `measure.py` **read-only**, sha256-pinned,
  identically to `pilot_injection.py`'s own `load_module()` pattern.
  Verified pins (re-checked at run time against the files on disk, matching
  the values every prior task in this campaign pinned):
  - `stage_a.py`: `06a0a618432c00fe26c72ecf05a8d89489db61c5183931fdb76a378717681405`
  - `measure.py`: `a4fd1ecb63f0ddc83c02ef45f2c65ab31cf13d13e7ae94f500e67465b24f5dc8`
- Reuses `decode_blocks`, `hist_of`, `batch_hists`, `sha_key`, `CTRStream`,
  `fixed_weight_support`, `support_to_int`, `ring_mul_sparse`, `N_JACK_BATCHES`
  from `stage_a.py`, and `comb_matrix`, `log2_A_from_hists` from `measure.py`,
  all called directly, never reimplemented.
- The injection wrapper (`make_defected_decode_blocks`) is copied in
  behaviour from `pilot_injection.py`'s function of the same name: the exact
  V3 transform (`bits_defected[:, lo:hi] = bits[:, lo-1:hi-1]` at block
  `n_e-1`), with the identical fail-closed injection invariant checked on
  every call.
- **The only genuinely new code is a driver function,
  `dual_decode_shard()`.** It reproduces `stage_a.py`'s own `_t_shard()`
  generation loop verbatim (same `sha_key`/`CTRStream`/`fixed_weight_support`/
  `ring_mul_sparse`/`support_to_int` calls, same D2/D3 hard-invariant checks,
  same batch structure) so that **the bit array for a given shard is
  generated exactly once per batch**, and then calls `decode_blocks` **twice**
  on that same generated array — once through the real, unmodified function
  and once through the defected wrapper — before moving to the next batch.
  This is the literal, load-bearing implementation of "generate once per
  shard, decode twice": `_t_shard` itself cannot do this (it calls
  `decode_blocks` exactly once per batch, resolved by module-global lookup),
  so achieving a true matched pair from a single generation pass requires a
  driver with its own outer loop around the same primitives — this is the
  "driver" work item the handoff's constraints anticipate, not a rewrite of
  `_t_shard`. `_t_shard` itself is additionally called, unmodified, exactly
  as-is, for two purposes: nowhere in the timed measurement (to keep the
  driver honest, `dual_decode_shard`'s generation body is a byte-identical
  copy of `_t_shard`'s own generation lines), but its D2/D3 counters and
  batch/shard/wall-cap conventions are reused verbatim.
- Two runs are authorized: this document treats stage 1 and stage 2 as two
  separate invocations of `matched_pair.py --stage {1,2}` inside one task
  directory (matching `budget.maximum_runs: 2`).

---

## 2. Stage 1: deterministic zero-new-entropy reconstruction (crossed design)

**Four arms, from exactly two generation passes** (one per shard), each
decoded twice:

| shard | decode variant | role |
|---|---|---|
| 5000 | defected (V3 wrapper) | reproduces the pilot's ORIGINAL defected arm — determinism gate |
| 5000 | unmodified (true) | the CROSSED arm — matched with the row above |
| 6000 | unmodified (true) | reproduces the pilot's ORIGINAL undefected arm — determinism gate |
| 6000 | defected (V3 wrapper) | the CROSSED arm — matched with the row above |

Both decode variants on shard 5000 come from **one** call to
`dual_decode_shard(sa, ps, shard=5000, n_trials=5000, ...)`, which generates
the bit array once per batch and decodes it twice; likewise one call for
shard 6000. **No new randomness is drawn beyond what `_t_shard` itself would
draw for these shard indices** — the PRNG is a pure function of
`(ps_id, "T", shard, MASTER_SEED, trial_index)`, unrelated to which decoder
is applied, so this is a replay of the same deterministic generation the
pilot's own separate `_t_shard` calls performed, not a new sample.

### 2.1 Determinism gate (FAIL-CLOSED, RUN FIRST)

Before any stage-1 statistic is computed: the shard-5000 defected arm's
whole-arm `S_histogram` (`hist_of(S, n_e)`) must be **bit-identical** to
`pilot_results.json`'s `MEASUREMENT.defected.S_histogram`, and the shard-6000
undefected arm's `S_histogram` must be bit-identical to
`MEASUREMENT.undefected.S_histogram`. If either comparison fails, the run
ABORTS and reports an infrastructure/determinism regression (AGENTS.md rule
5) — never a result about the mathematics. The committed pilot arrays (read
from `pilot_results.json`, sha256-pinned by the snapshot chain this task's
`read_scope` names) are, respectively:

```
defected   (shard 5000): [0,0,0,0,0,0,0,1,7,13,31,67,124,233,316,406,473,589,
                           610,625,468,348,279,174,104,70,31,20,6,4,1,0,...,0]
undefected (shard 6000): [0,0,0,0,0,0,0,1,1,10,38,76,134,212,316,399,509,602,
                           553,579,491,395,270,176,120,54,36,17,5,3,3,0,...,0]
```

### 2.2 Matched pairs and the estimator

For each shard, trial `i`'s true-decode block-failure sum `S_true[i]` and
defected-decode block-failure sum `S_def[i]` derive from the **same**
generated bit array — a genuine matched pair, auditable because both arrays
are persisted in trial order (Section 2.4).

Per shard (`T=5000`) and pooled across both shards (`T=10000`, shard 5000's
trials followed by shard 6000's, in that fixed order, for both the true and
defected pooled arrays):

- Point estimate: `log2_Ahat_k(true)` and `log2_Ahat_k(defected)` from the
  whole-arm histograms via `measure.log2_A_from_hists` (reused).
- `diff = log2_Ahat_k(defected) - log2_Ahat_k(true)`.
- **Matched-pair jackknife SE** (primary): leave-one-batch-out over
  `N_JACK_BATCHES=200` batches (`stage_a.batch_hists`, reused, applied
  identically to the true and defected arrays so batch boundaries line up
  trial-for-trial). For fold `i`, compute `log2_Ahat_k` on
  `(total_hist - batch_hist[i])` for both arms and take their difference
  `diff_loo[i] = log2_Ahat_k(defected, fold i) - log2_Ahat_k(true, fold i)`.
  `SE_paired = sqrt((b-1)/b * sum((diff_loo - mean(diff_loo))**2))`,
  `z_paired = diff / SE_paired`. This is the jackknife taken on the
  per-batch DIFFERENCE, matching the Red Team's Probe 2 construction and
  the misspecification it flagged in the pilot's own between-shard design.
- **Unpaired SE** (independent-arm quadrature, for the ratio deliverable):
  each arm's own leave-one-batch-out jackknife SE computed separately
  (`SE_true`, `SE_def`), combined as `SE_unpaired = sqrt(SE_true**2 +
  SE_def**2)`.
- **Ratio** = `SE_unpaired / SE_paired`, reported at k=17 as the replication
  of the Red Team's 2.78x.
- Reported for every `k` in the intersection of both arms' evaluable range
  (`stage_a.evaluable_k`, `T_STAB_THRESHOLD=30`), which prior arms in this
  campaign found to be `k = 2..26` at this T; the primary cell is
  `k = m = 17`.

### 2.3 What stage 1 can and cannot show (stated in advance)

Per `DEC-20260809-46e85c` / the task card: under the 1/sqrt(T) assumption
and the Red Team's SE of 0.1982 at T=5,000, the pooled SE over 10,000 pairs
is expected near 0.140 and the minimum detectable effect at z=1.96 is near
0.275 — **above** both existing point estimates (0.1922, 0.2069). Stage 1
therefore cannot produce an effect-excluding null, whatever it measures, and
is calibration/replication, not the primary test.

### 2.4 Retention requirement

`matched_pair_results.json` persists, for every stage-1 arm, the full
per-trial `S` array in trial order (as plain JSON integer lists), so the
pairing is auditable directly from the artifact rather than asserted in
prose — the exact gap `EV-HQC-dd85c1` O2 identified in
`TASK-20260806-77a574`'s data.

---

## 3. Stage 2: matched-pair extension at a pre-registered size

### 3.1 Trial-count rule

```
T2 = clamp(round(10000 * (SE_pooled_measured * 2.80 / 0.20) ** 2), 20000, 60000)
```

where `SE_pooled_measured` is stage 1's own pooled (`T=10000`) matched-pair
jackknife SE at `k=17` (Section 2.2). `delta=0.20`, `z=2.80`, floor `20000`,
cap `60000` are fixed by `DEC-20260809-46e85c` and are not the executor's to
choose. The only input from stage 1 is the single measured SE number;
substituted after stage 1 runs and shown verbatim in
`matched_pair_results.json`.

### 3.2 Stage-2 shard indices (fixed BEFORE stage 1 runs)

Fresh shards `8000, 8001, 8002, ..., 8011` (12 shards), used **in this
order**, each nominally 5,000 trials via `dual_decode_shard` (same matched-
pair construction as stage 1: one generation pass per shard, decoded twice).
Stage 2 uses `ceil(T2 / 5000)` of these shards in order, with the **last**
shard's trial count trimmed so the total achieved trials equals exactly
`T2` (e.g. `T2 = 39000` uses shards `8000..8006` at 5,000 trials each plus
`8007` at 4,000 trials). Twelve shards cover the full `[20000, 60000]`
range of the clamp (`12 * 5000 = 60000`).

These indices are disjoint from every shard used anywhere in this campaign's
committed record: `0-3, 900, 999, 1000-1007, 4900, 4901, 5000, 6000, 7777,
7778, 424242`, and from stage 1's own `5000, 6000`.

### 3.3 Statistics reported

Identical construction to Section 2.2 (point diff, matched-pair jackknife SE
and z, unpaired SE and the ratio, across `k=2..26` and at the primary cell
`k=17`), computed per stage-2 shard and pooled across all stage-2 trials.

### 3.4 SE-vs-trial-count exponent

Fitted from the three available `(T, SE_paired@k=17)` points: `T=5,000`
(mean of the two stage-1 per-shard paired SEs), `T=10,000` (stage-1 pooled
paired SE), and `T=T2` (stage-2 pooled paired SE), via ordinary least
squares on `log(SE)` vs `log(T)`; the fitted exponent is `-slope`. Reported
whatever the primary outcome, per the handoff.

---

## 4. Injection-invariant and D2/D3 dry runs

Both fail-closed selftests from `pilot_injection.py` are reused: (a) a
deliberate sha256-pin-mismatch call to `load_module()` with a wrong expected
hash, confirming `SystemExit`; (b) a deliberate injection-invariant break
(constructed shift-by-2, checked against shift-by-1 semantics), confirming
`SystemExit`. Both run before any real data is generated and gate the run:
`main()` aborts with `FAILED_IMPLEMENTATION` if either does not PASS. D2
(exact generation weight) and D3 (support-cap) hard invariants stay on
throughout `dual_decode_shard` (they run upstream of decoding, identically
to `_t_shard`, and are checked once per shard since they do not depend on
which decoder is applied).

---

## 5. Budget and reporting

- Core-seconds and wall-clock are measured and reported **separately for
  stage 1 and stage 2**, against the 400 core-second / 1,800 wall-clock
  authorizations.
- `run_manifest.yaml` records the exact commands, git commit and dirty-tree
  state, environment, and both stages' timings.
- The Executor reports observations only; it does not apply
  `DEC-20260809-46e85c`'s branch rule and draws no conclusion about A17,
  HQC's DFR, any standardized parameter set, or campaign scale-up/pause.
