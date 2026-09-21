# Report: TASK-20260815-e61cca -- single-shard-only local exponent for shards 8001/8002 plus an IVW pooling alternative

**Task** `TASK-20260815-e61cca` (executor) · **Batch** `BATCH-174014` ·
**Goal** `GOAL-HQC-001` · **Experiment** `EXP-HQC-982268`. Authorized by
`ledger/decisions/DEC-20260814-3f429d.yaml` next_actions (adopting the Red
Team's own named `next_concrete_action` and `required_controls` items 1 and 3
from `TASK-20260814-a49f1c`). Design pre-registered in `design.md` before any
data was generated.

**Claim tier: TOY, hard ceiling.** PS-R3 reduced parameters only
(`n=7187, n_e=56, n_2=128, dup=1, N=7168`, `m_load_bearing_order=17`). One
defect class (V3, last-block-window-read-early), one injection point
(`decode_blocks`'s block window, last block only). NOTHING here is a
statement about HQC's IND-CCA security, its decoding-failure rate,
assumption A17 or A5, or any standardized parameter set. This is the
Executor's own record: observations are reported separately from
interpretation, and NO conclusion is drawn about which of
`DEC-20260809-186c86`'s two named outcomes obtains, or about whether the
completed table shows shard-specific or general estimator heterogeneity --
that judgment belongs to the Coordinator, Validator and Red Team.

## 1. What was tested and what was not

- Part A: shards **8001** and **8002**, treated INDIVIDUALLY, NO cross-shard
  pooling anywhere. Trial indices `[10000, 30000)` retained per shard (this
  task's new sampling); `[0, 10000)` computed but discarded (already
  `TASK-20260809-a79e4f` stage 2's consumed range on these two shards).
  Defect class V3, injection point `decode_blocks` last block. PS-R3
  parameters throughout. k range 2..26.
- Part B: NO new sampling. Pure recomputation of an inverse-variance-weighted
  combination on already-committed `TASK-20260809-a79e4f` values: (a) shards
  5000/6000 at their own committed T=5,000-each stage-1 points, (b) shards
  8001/8002 at their own committed T=10,000-each stage-2 points.
- NOT tested: any other defect class, injection point, parameter set, or
  shard. NOT recomputed: shards 5000/6000's own single-shard exponents
  (2.836, 1.402) -- cited from `EV-HQC-469c08` O6, not re-derived here.

## 2. Validity

Both scripts ran to completion, exit code 0. `shard_8001_8002_discard_prefix.py`:
`valid_measurement`. `ivw_pooling_check.py`: `valid_measurement`. Full
detail in `run_manifest.yaml` and both results JSON files' own `validity`
blocks.

**Part A's adapted two-step disjointness proof: PASS on all 4 (shard,
variant) pairs.**
- Step 1 (dedicated `n_trials=10000` verification call vs. `TASK-20260809-a79e4f`'s
  committed `stage_2` derived statistics): PASS. D2/D3/D3_cap/D3_max_w
  matched exactly on all 4 pairs; `matched_pair_stats` (`point_defected`,
  `point_undefected`, `diff`, `se_paired`, `se_unpaired`, `z_paired`,
  `z_unpaired`, `ratio` at every evaluable k) matched to full float64
  bit-identity (exact `==`, no tolerance needed) on all 4 pairs, all 25
  evaluable k values each.
- Step 2 (real `n_trials=30000` analysis call's own discarded prefix vs. the
  SAME task's own separate verification call's raw per-trial S): PASS,
  bit-identical elementwise (`np.array_equal`) and by histogram, on all 4
  pairs.
- **Stated explicitly, per the handoff's own requirement: this two-step
  check is WEAKER than `TASK-20260814-8bbdd2`'s direct bit-identical-array-
  vs-committed-record check.** That task compared a freshly generated
  discarded prefix directly against a raw array PERSISTED BY A DIFFERENT,
  EARLIER TASK'S RUN -- a genuine cross-run, cross-session determinism
  proof. This task's Step 1 only confirms a verification call made INSIDE
  this SAME task's own execution reproduces the committed DERIVED
  statistics (no raw array exists for shards 8001/8002 to compare against
  directly); Step 2 only confirms internal, within-task self-consistency
  between two calls in the SAME process. This gap is real and disclosed,
  not silently treated as equivalent, per `design.md` Section 3 and
  `shard_8001_8002_discard_prefix_results.json.disjointness_proof.limitation_note`.

**Part A's F[:, 0:n_e-1] structural invariant: PASS on both shards, 0
mismatches** (0 / 1,100,000 elements checked per shard: 20,000 retained
trials x 55 non-last blocks).

**Hard invariants:** D2/D3 clean (0 violations) on all 8 sampling calls (4
verification at n_trials=10000, 4 analysis at n_trials=30000). No call
truncated; every call delivered its full requested trial count.

## 3. Part A: per-shard matched-pair statistics, k=17

| shard | diff (defected-undefected) | SE_paired | SE_unpaired | ratio (unpaired/paired) | z_paired |
|---|---:|---:|---:|---:|---:|
| 8001 (this task, T=20,000 new) | -0.024883352 | 0.029514096 | 0.323625060 | 10.9651 | -0.8431 |
| 8002 (this task, T=20,000 new) | +0.042503223 | 0.040280054 | 1.179423519 | 29.2806 | 1.0552 |

Full k=2..26 tables for both shards are in
`shard_8001_8002_discard_prefix_results.json.matched_pair.per_shard.{shard_8001,shard_8002}`.
No pooled cell is reported anywhere in this JSON file (`matched_pair.pooled`
is explicitly `null` with a `pooled_note` explaining why) -- Part A never
pools 8001 and 8002.

## 4. Part A: single-shard-only local exponent, shards 8001 and 8002

Method: `alpha = -[log(SE_T2) - log(SE_T1)] / [log(T2) - log(T1)]`, the exact
2-point OLS slope, the SAME method `TASK-20260814-8bbdd2` used for shards
5000/6000 (`EV-HQC-469c08` O6). Point 1 (T=10,000) is
`TASK-20260809-a79e4f`'s committed stage-2 single-shard `se_paired` at k=17
(read, not recomputed). Point 2 (T=20,000) is this task's own new, disjoint
tail. No cross-shard pooling anywhere in this computation.

| shard | SE(T=10,000, committed) | SE(T=20,000, this task's new tail) | local exponent alpha | sign of diff |
|---|---:|---:|---:|---|
| 8001 | 0.024506333 | 0.029514096 | **-0.268** | +0.0065 -> **-0.0249** (flips) |
| 8002 | 0.022096687 | 0.040280054 | **-0.866** | +0.0139 -> +0.0425 (stable, magnitude grows) |

**Anomaly, recorded per AGENTS.md rule 9 (an observation contrary to
expectation is preserved, not discarded), not interpreted:** both exponents
are NEGATIVE -- SE_paired at k=17 INCREASED from T=10,000 to this task's
new, disjoint T=20,000 draw on BOTH shards individually, the OPPOSITE
direction from any 1/sqrt(T) shrinkage and the opposite SIGN from shards
5000's (+2.836) and 6000's (+1.402) exponents, which were both positive
(SE decreased, just far outside the pre-registered [0.4,0.6] consistency
band). This is reported as a measurement, not interpreted.

## 5. The completed four-shard table

| shard | single-shard-only local exponent | source |
|---|---:|---|
| 5000 | **+2.836** | `EV-HQC-469c08` O6 (`TASK-20260814-8bbdd2`), cited, not recomputed |
| 6000 | **+1.402** | `EV-HQC-469c08` O6 (`TASK-20260814-8bbdd2`), cited, not recomputed |
| 8001 | **-0.268** | this task (`shard_8001_8002_discard_prefix_results.json`) |
| 8002 | **-0.866** | this task (`shard_8001_8002_discard_prefix_results.json`) |

All four exponents are far from the pre-registered [0.4, 0.6]
1/sqrt(T)-consistency band; two are positive (5000, 6000) and two are
negative (8001, 8002). No conclusion is drawn here about which of
`DEC-20260809-186c86`'s two named outcomes obtains, whether this pattern
supports "shard-specific to 8001/8002," "general to all four shards," or a
third reading the Red Team's original framing did not anticipate (e.g. sign
of the local exponent itself varying, rather than only its magnitude) --
that judgment belongs to the Coordinator, Validator and Red Team.

Companion four-shard SE table at their respective single-arm trial counts
(NOT all at the same T; each shard's own two measured points, for reference
only, no new arithmetic beyond what is in Sections 3-4 above and
`EV-HQC-469c08` O7):

| shard | SE_paired(T=5,000 or T=10,000, first point) | SE_paired(T=10,000 or T=20,000, second point) |
|---|---:|---:|
| 5000 | 0.125106 (T=5,000) | 0.017520 (T=10,000, `TASK-20260814-8bbdd2`) |
| 6000 | 0.149899 (T=5,000) | 0.056725 (T=10,000, `TASK-20260814-8bbdd2`) |
| 8001 | 0.024506 (T=10,000) | 0.029514 (T=20,000, this task) |
| 8002 | 0.022097 (T=10,000) | 0.040280 (T=20,000, this task) |

## 6. Part B: inverse-variance-weighted (IVW) combination vs. concatenated-histogram pooled

Formula: `w_i = 1/se_paired_i^2; diff_ivw = sum(w_i*diff_i)/sum(w_i); se_ivw
= 1/sqrt(sum(w_i))`. Computed from `TASK-20260809-a79e4f`'s already-committed
per-shard point estimates only -- NO new sampling.

**(a) Shards 5000/6000, T=5,000-each (stage 1):**

| k | diff_ivw | se_ivw | diff_pooled (concatenated) | se_pooled (concatenated) | se_ivw / se_pooled |
|---:|---:|---:|---:|---:|---:|
| 17 | 0.064435 | 0.096049 | 0.051567 | 0.096781 | **0.9924** |

Full k=2..26 table in `ivw_pooling_check_results.json.ivw_a_shards_5000_6000_T5000_each.by_k`.
The ratio se_ivw/se_pooled ranges from about 0.985 (k=13-16) to about 1.036
(k=23-24) across the reported k range -- close to 1 throughout, with no
consistent direction of compression or inflation across the full k range at
this pair.

**(b) Shards 8001/8002, T=10,000-each (stage 2):**

| k | diff_ivw | se_ivw | diff_pooled (concatenated) | se_pooled (concatenated) | se_ivw / se_pooled |
|---:|---:|---:|---:|---:|---:|
| 17 | 0.010616 | 0.016411 | 0.011085 | 0.017905 | **0.9165** |

Full k=2..26 table in `ivw_pooling_check_results.json.ivw_b_shards_8001_8002_T10000_each.by_k`.
The ratio se_ivw/se_pooled ranges from about 0.908 (k=18-20) to about 1.002
(k=2) across the reported k range at this pair -- consistently at or below
1, i.e. se_ivw is consistently the SAME OR SMALLER than the concatenated-
histogram pooled SE at every k in 2..26 for this pair, most pronounced
(smallest ratio, largest divergence) around k=17-20.

No conclusion is drawn here about whether this reflects the
pooling-convention compression `EV-HQC-469c08` O8 flagged as a possibility,
a different effect, or no real bias at all -- that judgment belongs to the
Coordinator, Validator and Red Team.

## 7. Spend

Measured, not modeled: `shard_8001_8002_discard_prefix.py` 93.839
core-seconds / 93.828 wall-seconds; `ivw_pooling_check.py` 0.332
core-seconds / 0.192 wall-seconds. **Total: 94.171 core-seconds / 94.020
wall-seconds**, against the 500 core-second / 1,800 wall-clock
authorization (18.8% / 5.2% of budget). 2 of 2 authorized runs used (one
execution of each script). Full detail in `run_manifest.yaml`.

## 8. Scope

Toy-scale, PS-R3-only, single defect class (V3), single injection point
(`decode_blocks`, block `n_e-1`). Part A: shards 8001 and 8002 only, trial
indices `[10000,30000)` retained per shard (this task's new sampling),
`[0,10000)` discarded-but-computed (already-consumed by
`TASK-20260809-a79e4f`). Part B: reads only already-committed T=5,000-each
(shards 5000/6000) and T=10,000-each (shards 8001/8002) per-shard points;
no new sampling. No claim here about HQC's IND-CCA security, its
decoding-failure rate, assumption A17/A5, or any standardized parameter
set. H-HQC-18d1b4's status is not touched by this record.
