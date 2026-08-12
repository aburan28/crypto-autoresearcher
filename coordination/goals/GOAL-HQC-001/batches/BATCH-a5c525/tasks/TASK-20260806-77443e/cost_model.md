# Cost model: real-(T)-sampler defect-injection feasibility

`TASK-20260806-77443e` (executor) · `BATCH-a5c525` · `GOAL-HQC-001`. Answers
`DEC-20260806-0995d5`'s named next action with a benchmark-backed cost model,
**not** the real-sampler defect-injection experiment itself. No sampler
defect was injected, no defect-injection run was executed, and nothing here
is a measurement of HQC, A17, or any decoding-failure rate. **Claim tier:
toy, hard ceiling.**

All numbers below are labeled **MEASURED** (this task's own benchmark,
`benchmark_results.json`), **MEASURED (prior batch)** (an earlier task's own
recorded run, cited by path), or **MODELED** (arithmetic derived from the
above, or a frozen figure from `experiments/EXP-HQC-982268/specification.yaml`).
Nothing here is presented as measured that was not actually run.

---

## 1. What this task did and did not do

- Imported `stage_a.py` (`coordination/goals/GOAL-HQC-001/batches/BATCH-6fddee/tasks/TASK-20260806-64b506/stage_a.py`,
  sha256 `06a0a618432c00fe26c72ecf05a8d89489db61c5183931fdb76a378717681405`)
  **read-only**, via `importlib`. Zero bytes of it were modified.
- Ran a **fail-closed self-integrity gate** first (`self_integrity_gate()` in
  `benchmark.py`): re-checks WHT-vs-dense-Hadamard agreement,
  `ring_mul_sparse` vs `ring_mul_dense` agreement, and
  `fixed_weight_support` exactness/distinctness against the imported module.
  All four checks passed (`benchmark_results.json.self_integrity_gate.all_pass
  = true`); had any failed, the script calls `sys.exit(1)` before producing
  any benchmark number — verified by construction (the check function raises
  before the timing code runs).
- Ran the REAL generation path — `CTRStream`, `fixed_weight_support`
  (Floyd's algorithm), `support_to_int`, `ring_mul_sparse`, and the real
  `decode_blocks` (WHT/Reed-Muller) — at all four contract parameter sets
  (PS-A, PS-R1, PS-R3, PS-R5), at **500-2,000 trials per set** (2,000 at
  PS-R3, the primary target; 500 at the other three). Total: 3,500 trials
  across all four sets, **1 authorized run**, **5.693 core-seconds**, **5.97
  wall-seconds** — far inside the 600 core-second / 1,800 wall-second budget
  for this task and far too small to be a measurement of anything about HQC.
- Used a domain-separated PRNG tag (`BENCH-TASK-77443e`, vector tags
  `bv0..bv4`) distinct from every real-arm domain (`T`, `NULL-M`, `NULL-P`,
  `CTRL-BS`, vector tags `v0..v4`) stage_a.py itself uses, so no draw in this
  benchmark is or could be reused as part of a measurement.
- Did **not** inject any defect. Did **not** run `measure.py`. Did **not**
  touch `experiments/EXP-HQC-982268/specification.yaml`, `stage_a.py`, or
  `measure.py`.

---

## 2. Per-stage benchmark breakdown (MEASURED, this task)

All figures from `benchmark_results.json`. `stages_summed` is this task's
own separately-timed calls to `fixed_weight_support` → `ring_mul_sparse`/
`support_to_int` → bit-packing → `decode_blocks`, run in that order.
`full_pipeline_via_real_t_shard` calls stage_a.py's own unmodified
`_t_shard()` worker directly (its real per-trial loop, D2/D3 invariant
checks included, batch=64, `want_replay=0` to isolate generation+decode
cost from the D5 replay control) — this is the literal function the real
experiment would call, not a reimplementation.

| set | n | n_e | dup | fixed_weight_support (μs/trial) | ring_mul (μs/trial) | bitpack (μs/trial) | decode_blocks (μs/trial) | **stages_summed** (t/core-s) | **real `_t_shard`** (t/core-s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| PS-A  | 17,669 | 46 | 3 | 421.6 | 164.1 | 140.6 | 737.2 | **683** | **1,662** |
| PS-R1 | 5,923  | 46 | 1 | 204.1 | 51.3  | 4.2   | 213.3 | **2,115** | **2,528** |
| PS-R3 | 7,187  | 56 | 1 | 217.0 | 67.1  | 4.7   | 979.6 | **788** | **2,227** |
| PS-R5 | 11,549 | 90 | 1 | 253.0 | 104.9 | 3.6   | 417.2 | **1,284** | **1,584** |

### 2.1 A disclosed measurement anomaly: `stages_summed` disagrees with `_t_shard` by ~2-3x

Within this benchmark, my own separately-timed stage sum (788 trials/core-s
at PS-R3) is **2.8x slower** than calling stage_a.py's own `_t_shard()`
directly on the same parameter set immediately afterward (2,227
trials/core-s) — even though `_t_shard` does strictly *more* work per trial
(it also runs the D2/D3 invariant checks this benchmark's stage timings do
not charge). This is reported, not resolved to my satisfaction, and not
smoothed over:

- **Cross-check against three independent PRIOR measurements of the same
  quantity, all MEASURED (prior batch), all in the same ~2,060-2,230
  trials/core-second band:** stage_a.py's own Stage-A calibration phase
  measured **2,061 trials/core-second** at PS-R3
  (`coordination/goals/GOAL-HQC-001/batches/BATCH-0a65c0/tasks/TASK-20260806-cde749/measurement_report.md`
  §8); that same task's own pre-run throughput benchmark measured **2,090
  trials/core-second**; and the actual `T = 1e7` PS-R3 measurement that
  produced `EV-HQC-b71230` (8 shards × 1,250,000 trials, 4 cores, 4,613.91
  core-seconds / 1,174.12 wall-seconds) measured **2,168 trials/core-second**
  — the largest-scale, most authoritative figure available, since it comes
  from an actual production run, not a calibration probe. My own
  `full_pipeline_via_real_t_shard` figure (2,227 trials/core-second) sits
  within 3% of that converged band. My own `stages_summed` figure (788
  trials/core-second) does **not** — it is roughly 2.6-2.8x more pessimistic
  than all four other measurements.
- **A plausible, but not confirmed, cause: cold-start/warm-up ordering.**
  In `benchmark.py`, for each parameter set, `decode_blocks` is called for
  the *first time in the whole process* inside that set's `stage3` timing
  block, immediately before `_t_shard` (which calls `decode_blocks` again,
  now warm) is invoked. `fixed_weight_support`/`ring_mul_sparse` were
  already exercised repeatedly by the self-integrity gate and the warm-up
  loop before their own stage timings, but `decode_blocks` was not given an
  equivalent warm-up. A single short-lived, single-process Python benchmark
  (this one: 5.97 wall-seconds total) is also subject to CPU frequency/turbo
  ramp-up over its own short lifetime, which would bias *later*-executed
  code (here, always `_t_shard`, called after that set's own `stage1-3`) to
  look faster in CPU-seconds, independent of any real per-instance cost
  difference.
- **Consistency check that supports the cold-start explanation:** my own
  isolated `decode_blocks`-only figure (980μs/trial at PS-R3, i.e. ~1,021
  trials/core-second) is in the same ballpark as, and not wildly
  inconsistent with, V2's own independently-measured `decode_blocks`-only
  benchmark at a matching content shape (`design.md`,
  `BATCH-558f5b/tasks/TASK-20260806-047535/`): **1,198 trials/core-second**.
  If `decode_blocks` alone really does cost roughly 800-1,000μs/trial in
  isolation (both my figure and V2's agree on this order of magnitude), then
  `stages_summed`'s total (fixed_weight_support + ring_mul + bitpack +
  decode_blocks, ≈1,269μs/trial at PS-R3) is internally consistent with its
  own parts. What is *not* explained is why calling the exact same
  primitives inside `_t_shard`'s tighter loop, immediately afterward, comes
  out 2.6-2.8x faster in CPU-seconds — this benchmark does not resolve that,
  and I am not asserting an explanation with more confidence than the
  evidence supports.

**Consequence for this cost model:** I report a **range**, bounded below by
this task's own `stages_summed` figure (pessimistic, internally consistent
with an independent prior V2 measurement of `decode_blocks` alone) and above
by the converged ~2,060-2,230 trials/core-second band (four independent
measurements: Stage-A calibration, BATCH-0a65c0's pre-run benchmark,
BATCH-0a65c0's actual `T=1e7` production run, and this task's own `_t_shard`
cross-check). I use the **pessimistic bound for affordability floors** (if it
fits even pessimistically, it is safely affordable) and the **converged
~2,100-2,230 band, anchored on the actual production-scale `T=1e7`
measurement, as the primary planning figure**, since it is empirically
better-supported (four convergent measurements at meaningfully larger scale)
than this task's own single small-N anomaly.

---

## 3. Where the defect would be injected (mechanical description)

All four candidate injection points named in the task card exist in
`stage_a.py` and each is a **small, local, single-line-to-few-line change** —
none requires new machinery, a new code path, or touching `measure.py`:

1. **`CTRStream.below()`** (stage_a.py lines 198-203). Currently rejection-samples
   uniformly in `[0, bound)`. An off-by-one/boundary defect: change
   `return v % bound` to admit or shift the boundary value by one (e.g.
   `return (v % bound + 1) % bound`), biasing every downstream draw by a
   fixed index shift. Broadest-scope injection point (affects every vector).
2. **`fixed_weight_support`'s returned indices** (lines 206-219). Floyd's
   algorithm samples over `range(n - w, n)`. The V1-class "off-by-one
   truncation" defect is literally a one-line change to this range, e.g.
   `range(n - w - 1, n - 1)`: shifts the entire sampled index window down by
   one, excluding index `n-1` and admitting an extra low index — breaking
   the uniform-over-`w`-subsets guarantee at exactly one boundary.
3. **`ring_mul_sparse`'s shift-XOr accumulation** (lines 236-241). The loop
   `for s in supp_b: acc ^= a_int << s` accumulates one shift per support
   index. A localized defect confined to the *last* accumulated element only
   (`if s == supp_b[-1]: acc ^= a_int << (s - 1)`) mimics the
   "last-block-window-read-early" shape without touching every term.
4. **`decode_blocks`'s own reshape** (line 296, `blk = bits.reshape(B, n_e,
   n_2)`). Reading the bit window one position early for the *last* block
   specifically (e.g. slicing `bits[:, 1:N+1]` instead of `bits[:, :N]` for
   that block only) is the literal, direct implementation of
   "last-block-window-read-early" — the exact defect-class name V1/V3 used,
   now applied to the real decoder's own input window instead of a planted
   proxy.

All four are confirmed by reading, not estimated: each is a change to an
existing single line or a small conditional wrapped around one existing
line, inside a function this benchmark already calls unmodified and whose
self-integrity was checked in §1. No new sampler, decoder, or estimator code
would need to be written.

---

## 4. Required-T derivation

### 4.1 Primary request: Wilson-CI sizing for a block-level detection RATE

The task requests sizing against the **8.8%-20.1% detection-rate range**
V1-V3 established (`ledger/evidence/EV-HQC-9a30d3.yaml` ~8.8% natural
Bernoulli(0.35) baseline; `ledger/evidence/EV-HQC-163374.yaml`/V3 ~10.47%
unconditional, ~20.12% margin-conditioned), with an explicit precision
target. This is a **block-level flip-rate proportion**, the same kind of
quantity V3 measured — **not** the `log2_Ahat_k` joint-moment estimator
itself (see §4.2).

Using the standard normal approximation to a Wilson interval,
`n ≈ z² · p(1-p) / w²` (z=1.96 for 95% CI, w = target half-width), evaluated
at both ends of the V1-V3 range (using the larger, more conservative
variance at p=20.1% where informative):

| half-width target | T at p=8.8% | T at p=20.1% (conservative) |
|---|---:|---:|
| ±1.0 pp | 3,083 | 6,170 |
| ±0.5 pp | 12,333 | 24,678 |
| ±0.2 pp | 77,080 | 154,240 |

**Adopted precision target for this cost model: ±0.5 percentage points at
95% CI, conservative end → T ≈ 24,700.** This is MODELED (derived
arithmetic from a stated formula and the cited prior detection-rate range),
not measured. It is a normal-approximation to the Wilson interval, adequate
for planning at these sample sizes; it is not an exact numerical inversion.

### 4.2 Secondary, more directly relevant anchor: the frozen spec's own T_req at PS-R3's load-bearing order

The block-level flip-rate sizing above answers "how many trials to pin down
a proportion," but the actual object `measure.py`'s pipeline computes and
PS-R3 was measured with is `log2_Ahat_k`, a higher-order joint-moment
statistic with its own, generally larger, pre-registered sample-size
requirement. `experiments/EXP-HQC-982268/specification.yaml`'s own frozen
`sample_size_derivation` (MODELED, pre-registered, not computed by this
task) already states, for PS-R3 at its load-bearing order k = m = 17:

> `T_req = 3.09e5`, `SE_at_allocated_T = 0.008`

This is roughly **10x larger** than the block-level Wilson sizing above
(24,700), and is the more relevant anchor for a defect-injection experiment
whose stated goal is "whether the resulting joint-moment estimator ...
detects the defect" (the dispatch queue's own wording), because it is sized
to the estimator PS-R3 actually used, not to a block-level flip proportion.
**What this task cannot supply:** the T actually needed to detect an
*injected* defect's effect at the estimator level depends on that defect's
effect size on `log2_Ahat_k`, which is unmeasured and unmeasurable without
running the injection — 3.09e5 is the spec's own sizing for resolving the
*natural* (undefected) estimator to its own stated precision, used here only
as the best available order-of-magnitude anchor, not as a defect-specific
power calculation.

---

## 5. Cost table

All core-second costs below are **MODELED**: measured throughput (§2)
divided into a trial count (§4, or a specification-frozen `T_req`, §2 of
`experiments/EXP-HQC-982268/specification.yaml`). Ranges are
[pessimistic `stages_summed`, optimistic production-anchored ~2,100-2,230
band] where both bounds are available (PS-R3); elsewhere [this task's own
`stages_summed`, this task's own `_t_shard` cross-check].

### 5.a Reduced parameters (PS-R3, n_e=56 order, matching V1-V3) — budget tranches

| tranche (core-seconds) | achievable T, pessimistic (788 t/cs) | achievable T, optimistic (2,168-2,227 t/cs) |
|---:|---:|---:|
| 500   | 394,195   | 1,084,000 – 1,113,620 |
| 2,000 | 1,576,780 | 4,336,000 – 4,454,480 |
| 6,500 | 5,124,535 | 14,092,000 – 14,477,057 |

**Reaching the spec's own pre-registered `T_req(PS-R3, k=m=17) = 3.09e5`
costs 139-392 core-seconds under EITHER the pessimistic or optimistic
throughput bound** — i.e., it fits inside even the smallest (500
core-second) tranche in this table by a wide margin, regardless of which
throughput figure from §2.1 is used. Reaching the Wilson-CI block-level
sizing of §4.1 (T≈24,700) costs on the order of 11-31 core-seconds,
trivially affordable.

**Caveats not priced into this table:**
- A paired *undefected* control arm at the same T would roughly **double**
  the cost, unless the existing PS-R3 undefected dataset
  (`ledger/evidence/EV-HQC-b71230.yaml`, `T=1e7`) is reused as the
  comparison baseline instead of re-measuring it — a design choice for
  whoever authors the follow-on experiment, not decided here, but worth
  flagging since it materially changes affordability.
- Fixed per-run overhead (self-tests, provenance checks, an
  oracle-agreement-style gate if one is included) is not modeled here. In
  Stage A's own authorized run, this class of overhead was ~110 of 1,692
  core-seconds (~6.5%) — a plausible order-of-magnitude reference, not a
  measured figure for an as-yet-undesigned experiment.
- `measure.py`'s own estimator/jackknife computation cost is not benchmarked
  by this task (out of this task's read/write scope; `measure.py` was not
  touched). BATCH-0a65c0's own real `T=1e7` run reports its "(T) analysis +
  jackknife" phase at **0.12 core-seconds for the full 1e7-trial run**
  (`measurement_report.md` §8) — MEASURED (prior batch), suggesting analysis
  overhead is negligible relative to generation cost at these scales, but
  this is one data point from a different (undefected) run, not a
  benchmark of this task's own.

### 5.b Standardized parameter sets — full-scale cost, even if unaffordable

**Gap disclosed up front:** `experiments/EXP-HQC-982268/specification.yaml`
gives PS-A's parameters as HQC-1's **true, deployed, verbatim** parameters
(n=17,669, n_e=46, ω=66, ω_r=ω_e=75, dup=3) — PS-A is a genuine standardized
point. PS-R1/PS-R3/PS-R5 are **order-matched to HQC-1/3/5's shape** (same
n_e, same m) but use **dup=1**, not HQC-3's/HQC-5's real deployed
duplication multiplicity (3 and 5 respectively) — the specification itself
states this reduction has no intermediate rung (`OPEN-2`: dup=2 costs 3.2e20
core-seconds). This task's read scope does **not** contain HQC-3's or
HQC-5's true deployed (n, ω, ω_r, ω_e) at their real dup values; fabricating
them from outside this program's corpus would violate AGENTS.md rule 5, so
they are not estimated here. The table below therefore reports PS-A (a true
standardized point) and PS-R1/R3/R5 labeled explicitly as **order-matched
proxies, not the true deployed HQC-3/HQC-5 parameter sets**.

| parameter set | role | T_req at k=m (MODELED, frozen spec) | cost, pessimistic throughput | cost, optimistic throughput |
|---|---|---:|---:|---:|
| PS-A  | true HQC-1 (=HQC-128), k=m=16, at HQC-1's own real q | 2.06e42 (3.40e41 at optimistic q=p_i) | ~3.0e39 core-s | ~2.0e38 core-s (best case) |
| PS-A  | true HQC-1, k=3 (below m, still reachable order) | 1.61e7 | 23,563 core-s | 9,688 core-s |
| PS-A  | true HQC-1, k=2 | 1.18e5 | 173 core-s | 71 core-s |
| PS-R1 | order-matched to HQC-1 shape, dup=1 (NOT deployed dup) | 2.91e7 (k=m=16) | 13,760 core-s | 11,510 core-s |
| PS-R3 | order-matched to HQC-3 shape, dup=1 (NOT deployed dup) | 3.09e5 (k=m=17) | 392 core-s | 139-147 core-s |
| PS-R5 | order-matched to HQC-5 shape, dup=1 (NOT deployed dup) | 2.72e6 (k=m=30) | 2,118 core-s | 1,584-1,717 core-s |

**Observation, not a conclusion about HQC:** reaching PS-A's own load-bearing
order (k=m=16, at HQC-1's real q) is infeasible by roughly 38-39 orders of
magnitude relative to this table's core-second costs — consistent with, and
not contradicting, this campaign's own prior structural-infeasibility
finding (`BATCH-003`). Even PS-A's k=3 (23,563-9,688 core-seconds) exceeds
this task's own §6 running-budget estimate on its own. Only PS-A's k=2, and
the order-matched-shape proxies PS-R3 (and, in the higher tranches, PS-R5),
fall within plausible remaining-campaign-budget range; PS-R1 and PS-A k≥3
do not.

---

## 6. Campaign budget: this task's own derived running total

`GOAL-HQC-001.campaign_budget.total_wall_clock_seconds = 10,800` (the live
pause condition). `ledger/goals/GOAL-HQC-001.yaml`'s own
`superseded_next_action_20260806_batch0a65c0_paused` entry states "roughly
7,000 of 10,800 wall-clock seconds remain UNSPENT" at the close of
BATCH-0a65c0 (the sixth of six batches under the now-removed cap) — i.e.
**~3,800 wall-clock-seconds spent through BATCH-001/002/003/6fddee/c5703d/0a65c0**,
consistent with BATCH-0a65c0's own single largest run (the `T=1e7` PS-R3
measurement, §2.1) costing 4,613.91 core-seconds at 4 cores ≈ **1,174.12
wall-seconds** — a large fraction of that ~3,800 by itself.

`batch_checkpoints` for the three subsequent batches report **executor
core-seconds used** (not independently converted to wall-clock, since this
task's read scope does not state how many cores each of those three
producer scripts used):

| batch | executor core-seconds used (of 1,800 authorized) | red-team probe compute (disclosed, actual) |
|---|---:|---:|
| BATCH-4b8ad3 | 72.0 | ~170 s |
| BATCH-558f5b | 434.3 | ~252 s (4.2 min) |
| BATCH-f8050e | 946.3 | ~147.7 s |
| **sum** | **1,452.6** | **~569.7 s** |

**My own derived running total: ~3,800 (through BATCH-0a65c0) + 1,452.6
(executor, three subsequent batches) + ~569.7 (disclosed red-team probe
compute, three subsequent batches) ≈ 5,822.3 wall/core-seconds drawn against
the 10,800 total — leaving roughly ~4,978 seconds of headroom, as a
lower-bound estimate.** This is **not** a precise figure: validator-session
compute time is not itemized anywhere in `batch_checkpoints` for any of the
three subsequent batches, and general Coordinator/session overhead is not
tracked against this total at all. It is presented with its components shown
so the gap is visible, rather than as a single confident number. The
dispatch queue's own framing text approximated "roughly 6,500 seconds
already drawn" — my own component-by-component total (~5,822) comes in
somewhat lower, most plausibly because it does not include the unitemized
validator/session overhead the dispatch queue's rounder figure may be
implicitly folding in. **Flagging this discrepancy rather than silently
adopting either number.**

**Consequence for the cost table above:** the 6,500-core-second top tranche
in §5.a, taken as a *wall-clock* draw at 1 core (this benchmark's own
single-process figures are core-seconds = wall-seconds), would by itself
consume more than my own ~4,978-second lower-bound remaining-budget
estimate, and would consume close to it even under the dispatch queue's
looser ~4,300-second implied remaining figure. **It is not needed for the
PS-R3-scale objective in §4.2** — that objective (T_req=3.09e5) is affordable
at 139-392 core-seconds, well inside even the smallest (500-second) tranche.

---

## 7. Recommendation (not a decision)

**PARTIAL-GO, narrowly scoped to PS-R3.**

Reasoning, strictly on feasibility/cost — no statement about A17, HQC's DFR,
or any standardized parameter set is made or implied:

- At PS-R3 (n_e=56 order, matching V1-V3's own scale), reaching the
  specification's own pre-registered `T_req` at the load-bearing order
  (k=m=17, T=3.09e5) costs 139-392 core-seconds under either bound of this
  task's throughput measurements — comfortably inside even the smallest
  (500 core-second) tranche this cost model was asked to size, and small
  relative to this task's own ~4,978-second lower-bound estimate of
  remaining campaign wall-clock budget (§6).
- The mechanical defect injection is a small, local, single-line-to-few-line
  change at any of four named, read-confirmed locations (§3) — no new
  machinery.
- The fail-closed self-integrity gate passed cleanly on the real,
  unmodified functions this experiment would use (§1).
- **Against this:** §2.1's unresolved ~2.6-2.8x internal throughput
  discrepancy means the true steady-state cost at PS-R3 carries real
  uncertainty, even though *both* bounds of that uncertainty land well
  inside the smallest tranche for the PS-R3-scale objective specifically.
  A paired undefected-control arm (if the design does not reuse
  `EV-HQC-b71230`'s existing PS-R3 dataset) would roughly double the cost —
  still affordable at this scale, but not priced into the headline figures
  above without flagging it.
- **NOT recommended at this budget:** any standardized-parameter run beyond
  PS-A's own k≤2 (§5.b) — PS-A's k=3 alone (9,688-23,563 core-seconds)
  exceeds this task's own remaining-budget estimate, PS-A's k=m=16 is
  infeasible by ~38 orders of magnitude, and PS-R1's k=m=16 (11,510-13,760
  core-seconds) also exceeds it. The specification-derived extrapolation to
  standardized parameters remains, on this cost model's own numbers, out of
  reach at this campaign's remaining budget — consistent with, not
  contradicting, this campaign's prior structural-infeasibility finding.
- The 6,500-core-second top tranche this cost model was asked to size is
  **not needed** for the recommended PS-R3-scale scope and, per §6, would by
  itself consume most or all of this task's own estimate of remaining
  campaign budget if drawn at 1 core.

**This is a feasibility recommendation only. The Coordinator makes the
actual go/no-go call**, weighing this cost model against both independent
reviews of it, the goal's declared pause conditions, and whatever budget
figure the Coordinator itself certifies from the ledger.

---

## 8. Artifacts

- `benchmark.py` — the calibration benchmark (this task's only authorized
  run).
- `benchmark_results.json` — its raw, unmodified output.
- `run_manifest.yaml` — command, git commit/dirty-state, environment, seeds,
  timings, validity status.
- This file.
