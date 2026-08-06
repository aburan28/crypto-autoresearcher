# Design: V2 planted-correlation control arm for OPEN-6 (TASK-20260806-047535)

Written and frozen **before** `planted_arm_v2.py` is run on any data (including
before the authorized T-trial run and before any smoke run at reduced scale).
`run_manifest.yaml` records file-timestamp ordering as evidence this was not
written after seeing results, the same discipline `design.md` used in the V1
arm (`TASK-20260806-e19f6c`).

## 0. What this document is for, and what changed from V1

`TASK-20260806-e19f6c`'s planted-correlation control arm (V1) matched its
closed-form planted value at all 17 reported cells, but the Red Team
(`TASK-20260806-21c8da`, `red_team_report.md`) proved by injection that V1 is
**structurally blind, with probability exactly 1, for any T**, to the exact
defect class OPEN-6 exists to catch (off-by-one index shifts, last-block
window-read-early). Root cause, per the red team: V1 (a) never ran the real
decoder (`stage_a.py`'s `decode_blocks`), using a hand-rolled majority
threshold instead, and (b) used internally **homogeneous** (all-0 or all-1)
128-bit blocks, so any single boundary-index perturbation could move a
block's bit-sum by at most 1 relative to its landslide 0/128 value — never
enough to cross the majority threshold's 64-vote margin.

This V2 arm closes both gaps:

1. **Real decoder.** `planted_arm_v2.py` imports `stage_a.py`'s actual
   `decode_blocks` (sha256-pinned, read-only, unmodified) and calls it
   directly on the constructed flat bit array. The block-partition step
   (`bits.reshape(B, n_e, n_2)`) that OPEN-6 cares about is executed by
   `decode_blocks` itself — not reimplemented by this task — so a defect in
   that reshape, if it existed in `stage_a.py`, would be exercised by exactly
   the code path that would run in production.
2. **Heterogeneous, decision-boundary-adjacent block content.** Instead of
   homogeneous all-0/all-1 blocks, every "succeed" block uses one fixed
   128-bit template `S_TEMPLATE` and every "fail" block uses one fixed
   128-bit template `FAIL_TEMPLATE`, both real, both verified (Section 3
   below) to (a) genuinely decode to their intended label under
   `decode_blocks`, and (b) sit close enough to the WHT argmax decision
   boundary that a boundary-index-shift perturbation of the kind this
   campaign already named V1 (global off-by-one) and V3 (last-block
   window-read-early) has a demonstrated, non-zero chance of flipping the
   decoded outcome `F_j`.

**The reusable trick from V1 still applies, unchanged.** Per-trial, WHICH of
the `n_e = 56` block positions are "planted-fail" is still chosen by the same
exchangeable mechanism V1 used (`M_t ~ Uniform{17,18,19}`, a uniform random
`M_t`-subset of the 56 positions). This keeps `log2_A_k(k)` exactly as
closed-form as V1's, because the marginal law of `S_t = sum_j F_j` depends
only on WHICH positions are marked fail, never on WHAT bit content realizes
"fail" vs. "succeed" at a position — a fact that is true regardless of
whether that content is homogeneous (V1) or a genuine near-boundary
heterogeneous template (V2, this task). Section 1 re-derives this
independently rather than simply citing V1's table, and it reproduces V1's
numbers exactly, as expected from the argument just given.

## 1. Parameters (order-matched to PS-R3, unchanged from V1)

| quantity | value | source |
|---|---|---|
| `n_e` | 56 | PS-R3 (`stage_a.py` `PARAM_SETS`) |
| `n_2` | 128 | PS-R3, `dup=1` |
| `dup` | 1 | PS-R3 |
| `N = n_e * n_2` | 7168 | PS-R3 |
| `L` (this task's block length) | `N // n_e = 128` | **RULE-2**: computed as `N // n_e` in code, never `n_2*dup`. At `dup=1` the two coincide numerically, but the code never takes the shortcut. In this V2 arm, `L` is also exactly the reshape `decode_blocks` performs internally (`bits.reshape(B, n_e, n_2)`) — this arm supplies `n_2` as a parameter to the REAL function, so `L` and `n_2` are the same quantity by construction, and the RULE-2 assertion (`L == N_2`) is checked as a sanity gate rather than silently assumed. |
| `m` (narrative parity only) | 17 | PS-R3 |
| `k_max` | 18 | PS-R3 |
| reported cells | `k = 2..18` (17 cells) | matches PS-R3 |
| `T` planned at PS-R3/V1 scale | 10,000,000 | **not achievable in this arm's budget — see Section 5** |
| `T` actually run by this arm | see Section 5 (budget-reduced) | reported honestly, not silently substituted |
| jackknife batches | 200 (`N_JACK_BATCHES`) | reused constant, `measure.py` line 92 |

## 2. The planted joint law (position-marking mechanism — unchanged from V1)

**Construction**, independently re-derived here (not merely copied from V1,
though it is the same construction and is expected to, and does, reproduce
V1's numbers exactly — see the argument in Section 0):

For every trial `t`, independently:

1. Draw `M_t` uniformly from `{17, 18, 19}` (probability 1/3 each) — the
   number of the `n_e = 56` blocks marked "planted-fail" this trial.
2. Choose the set of `M_t` failing block POSITIONS as a uniformly random
   size-`M_t` subset of `{0, ..., 55}` (every subset of that size equally
   likely, independent across trials).
3. `F_j ∈ {0,1}` (the intended label): `F_j = 1` iff position `j` was chosen
   as "fail" in step 2.

Because every subset of size `M_t` sums to `M_t`, `S_t := sum_j F_j = M_t`
exactly, on every trial. The population factorial moments therefore have the
same two-line closed form V1 derived:

```
mu_bar_k = E[C(S,k)] / C(n_e,k) = E[C(M,k)] / C(n_e,k)
         = (1/3) * ( C(17,k) + C(18,k) + C(19,k) ) / C(56,k)      for k = 2..18

q        = E[S] / n_e = E[M] / n_e = (17+18+19)/3 / 56 = 18/56 = 9/28

log2_A_k(k) = log2( mu_bar_k ) - k * log2( q )
```

### 2.1 Planted `log2_A_k(k)` table (exact, independently recomputed, matches V1's frozen table digit for digit)

| k | mu_bar_k (exact) | mu_bar_k (float) | planted log2_A_k |
|---|---|---|---|
| 2 | 23/231 | 0.09956709956709957 | -0.05332724412846135 |
| 3 | 493/16632 | 0.029641654641654643 | -0.16394044463458357 |
| 4 | 4658/550935 | 0.008454717888680153 | -0.3363079856368989 |
| 5 | 3298/1432431 | 0.002302379660870227 | -0.5755089290487359 |
| 6 | 122/204633 | 0.0005961892754345584 | -0.8873624322504217 |
| 7 | 23/157410 | 0.0001461152404548631 | -1.2785962698872737 |
| 8 | 26/771309 | 3.370892858763479e-05 | -1.7570703364157492 |
| 9 | 17/2337300 | 7.27334959140889e-06 | -2.3320793631074803 |
| 10 | 8/5492655 | 1.4564905314460857e-06 | -3.0147730405328055 |
| 11 | 271/1010648520 | 2.681446562648704e-07 | -3.8187560346206517 |
| 12 | 17/378993195 | 4.4855686656854086e-08 | -4.76097481483005 |
| 13 | 4/595560735 | 6.716359499422003e-09 | -5.8630844320447935 |
| 14 | 113/128045558025 | 8.824983993426585e-10 | -7.153668398603774 |
| 15 | 71/717055124940 | 9.901609727137919e-11 | -8.672097148069227 |
| 16 | 67/7349815030635 | 9.115875667718868e-12 | -10.47587716111893 |
| 17 | 19/29399260122540 | 6.462747674875317e-13 | -12.65660891751783 |
| 18 | 1/31849198466085 | 3.1397964412349716e-14 | -15.382583727766058 |

`q = 9/28 = 0.32142857142857145`. `planted_arm_v2.py` recomputes this exact
table itself (same closed form, same `fractions.Fraction` arithmetic) at the
top of its run, before any trial is sampled, and asserts bit-for-bit
agreement with the frozen table above (a run-time reproduction check,
same discipline as V1's `DESIGN_TABLE_LOG2_A` check).

## 3. Real-decoder templates: construction and pre-registered verification

**This is the new derivation step this task's completion gate requires
before any trial generation, and it is documented here, before
`planted_results.json` exists (see `run_manifest.yaml`'s
`pre_registration_ordering` for the file-timestamp evidence).**

### 3.1 What "near-boundary" means for `decode_blocks`

`decode_blocks` (`stage_a.py` line 286) maps a 128-bit block to a signed
sequence `v_i = 1 - 2*bit_i ∈ {+1,-1}`, applies the fast Walsh-Hadamard
transform `t = wht128(v)` (`stage_a.py` line 270), and decodes via
`idx = argmax_j |t_j|` (ties broken toward the LOWEST index by `numpy`'s
`argmax`), `val = t[idx]`. The block "succeeds" (`F_j = 0`) iff `idx == 0`
and `val > 0` (decoding to the all-zero duplicated RM(1,7) codeword with
positive correlation); otherwise it "fails" (`F_j = 1`).

Define the **margin** of a candidate 128-bit block as
`margin = |t|_(1) - |t|_(2)` (the gap between the largest and second-largest
`|t_j|`, over all 128 coordinates `j = 0..127`). A large margin (e.g. the
all-zero block: `t_0 = 128`, every other `t_j = 0`, margin = 128) is exactly
what made the V1 arm's homogeneous blocks blind: flipping any single bit
changes every `t_j` by exactly `∓2`, so a margin of 128 cannot be crossed by
a handful of single-bit changes. A **small** margin means a modest number of
coordinate changes can plausibly move the argmax to a different index (or
flip `val`'s sign at `idx=0`), changing `F_j`.

### 3.2 Search procedure (pre-registration exploration, not part of the authorized run's charged budget)

Conducted in scratch space (`/tmp/.../scratchpad`, not committed, not
counted against this task's core-second budget — the same convention V1
used for its throughput calibration), using the SAME sha256-pinned
`decode_blocks` import this task's authorized script uses:

1. Start from a pure duplicated RM(1,7) codeword (`a=0`, the all-zero
   codeword, giving `idx=0, val=128, F=0`; or `a=1`, giving `idx=1, val=128,
   F=1` since `idx != 0`).
2. Flip a random subset of `m` bit positions (`m` searched over `20..64`) and
   recompute the exact margin and `F` via the real `decode_blocks`.
3. Also searched directly over i.i.d.-`Bernoulli(0.35)` random 128-bit blocks
   (matching the sparsity this campaign's own NULL-M arm uses for realistic
   crypto-like noise density), filtering for small margin AND for the
   property that a candidate boundary-shift perturbation (Section 3.3) flips
   `F` relative to the unperturbed block.
4. Kept the smallest-margin candidate, among those found, for each of the two
   intended labels (`F=0` "succeed", `F=1` "fail"), subject to `margin >= 1`
   (a margin of exactly 0 is a genuine numpy-argmax tie and was excluded to
   keep the templates' own unperturbed decode deterministic and
   unambiguous).

Margin distribution observed in this search (4,000,000 Bernoulli(0.35)
samples plus a targeted flip-based search over `20..64`-bit perturbations of
the two base codewords): several hundred candidates were found at margin
`<= 8` for each label, out of a much larger pool of near-boundary candidates
generally; the smallest margins found for either label were `margin = 4`
(out of a theoretical maximum of 128), i.e. the winning `|t|` value beats the
runner-up by only 4 (typical differences between adjacent `|t_j|` values
under this construction are small multiples of 2, since a single flipped
input bit moves every `t_j` by exactly `±2`).

### 3.3 The two chosen templates

**`S_TEMPLATE`** (intended label: succeed, `F_j = 0`), 128 bits, flat sequence
(embedded verbatim as a module constant in `planted_arm_v2.py`; exact list
form is `S_TEMPLATE` there):

```
11010001010110100110011100100010001100000101001011001001000111100001101010000111100011100001000010100000001000001111000100100000
```

**`FAIL_TEMPLATE`** (intended label: fail, `F_j = 1`), 128 bits, flat sequence
(embedded verbatim as a module constant; exact list form is `FAIL_TEMPLATE`
in `planted_arm_v2.py`):

```
00001110100110001110100101001100011100000010110000011000100000010110000100000001100000100010011111010000100100000110111110010111
```

Both are asserted, at run time, to sha256-match the values recorded in
`run_manifest.yaml`.

### 3.4 Pre-registered verification (the derivation step required before trial generation)

Both templates were verified, **before any trial was sampled**, by two
INDEPENDENT decoders both imported read-only from the sha256-pinned
`stage_a.py`:

1. `decode_blocks` (the real WHT/Reed-Muller-fold argmax decoder, the actual
   production decode path).
2. `brute_force_decode` (`stage_a.py` line 323), an **exhaustive
   minimum-distance search over all 256 duplicated RM(1,7) codewords**
   returned by `rm17_codewords()` (`stage_a.py` line 310) — a completely
   independent algorithm (brute-force nearest-codeword search vs. a fast
   transform) that exercises `rm17_codewords()` directly, satisfying this
   task's obligation to state precisely which `stage_a.py` machinery is
   invoked.

Results (recomputed at run time by `planted_arm_v2.py` itself, and reproduced
here from the same pre-registration exploration):

| template | intended `F` | `decode_blocks` `F` | `brute_force_decode` `F` | agree? | `W` (block bit-sum) | margin (`\|t\|_(1) - \|t\|_(2)`) | ties flag |
|---|---|---|---|---|---|---|---|
| `S_TEMPLATE` | 0 (succeed) | False | False | YES | 49 | 4 | False |
| `FAIL_TEMPLATE` | 1 (fail) | True | True | YES | 50 | 4 | False |

Both templates' true decode matches their intended label under BOTH
decoders. **No template's true decode ever disagreed with its intended label
during this construction** — this is reported explicitly per the task's
completion gate, and would have been reported just as plainly had it not
held (a template that failed this check would have been discarded or fixed,
never silently used; `planted_arm_v2.py`'s own run-time re-verification
(Section 3.4 below, and `verify_templates()` in the script) aborts
fail-closed if this does not hold at run time, e.g. because of an
environment/library discrepancy in `wht128`'s numpy call conventions).

### 3.5 Boundary-index-shift sensitivity: concrete perturbation check

The two campaign-named defect classes this arm must give a genuine, non-zero
chance of catching are:

- **V1** — a global off-by-one circular shift of the flat `N`-bit array
  before the (correct) `L`-boundary reshape. Applied to ANY interior block
  `j`, its effect (worked out exactly, not by analogy) is: the block's new
  content is `[x_{-1}] + old_content[0:127]`, where `x_{-1}` is the LAST bit
  of the PRECEDING block (position `j-1`'s last bit) — i.e. block `j` drops
  its own true last bit (which becomes the new first bit of block `j+1`) and
  gains a foreign bit borrowed from its predecessor at the front.
- **V3** — the same per-block "read one index early" operation, applied only
  to the last block (`j = n_e - 1`).

This operation is implemented for the verification check as
`shift_read_one_early(block, foreign_last_bit)`, and its effect was tested on
BOTH templates in BOTH of the two cases that actually arise when this arm's
content is tiled at 56 positions: a "same-label neighbor" (the foreign bit
equals the template's own last bit — arises when two adjacent positions
share the same planted label) and a "different-label neighbor" (the foreign
bit comes from the OTHER template — arises at every fail/succeed transition,
which occurs frequently given `M_t ≈ 17-19` of 56 positions are marked
fail). The reverse direction ("read one index late",
`shift_read_one_late`) was also checked as an additional sanity probe (not a
named defect class in this campaign, but a natural mirror-image case).

Result (computed by `decode_blocks`, the real decoder, on the exact
`S_TEMPLATE`/`FAIL_TEMPLATE` byte content above):

| perturbation | template | foreign bit source | unperturbed `F` | perturbed `F` | FLIPPED? |
|---|---|---|---|---|---|
| read-one-early | `S_TEMPLATE` | own last bit (same-label neighbor) | 0 | 1 | **YES** |
| read-one-early | `S_TEMPLATE` | `FAIL_TEMPLATE`'s last bit (diff-label neighbor) | 0 | 1 | **YES** |
| read-one-late  | `S_TEMPLATE` | own first bit | 0 | 0 | no |
| read-one-late  | `S_TEMPLATE` | `FAIL_TEMPLATE`'s first bit | 0 | 0 | no |
| read-one-early | `FAIL_TEMPLATE` | own last bit | 1 | 0 | **YES** |
| read-one-early | `FAIL_TEMPLATE` | `S_TEMPLATE`'s last bit | 1 | 0 | **YES** |
| read-one-late  | `FAIL_TEMPLATE` | own first bit | 1 | 0 | **YES** |
| read-one-late  | `FAIL_TEMPLATE` | `S_TEMPLATE`'s first bit | 1 | 0 | **YES** |

**This concretely establishes the property the task requires**: for at least
one of the two named defect classes (the "read one index early" direction,
which is the literal shape of both V1 and V3 as described in this campaign's
own precedent, `idxmap_probe.py`), BOTH templates flip under BOTH the
same-label and different-label neighbor scenarios. `FAIL_TEMPLATE` is in
fact sensitive to the perturbation in every direction and neighbor
combination tested. This is a genuine (not merely asserted) non-zero chance
of a boundary-index-shift defect being expressed as a decode error — unlike
V1's homogeneous-block construction, which the red team proved has EXACTLY
ZERO chance, deterministically, for any T.

This finding is a per-template, per-scenario deterministic fact (not a
Monte Carlo estimate): given these EXACT fixed templates, the flip either
happens or does not, and the table above reports which. Whether an actual
red-team-injected V1/V3 defect against the FULL 56-position tiled trial
distribution is detected at the level of the `S_t` histogram and the
recovered `log2_Ahat_k` — as opposed to at the level of a single isolated
block decode, shown here — is exactly what `TASK-20260806-ae74c4` (red team)
is dispatched to test, mirroring the relationship between this design
section and `TASK-20260806-21c8da`'s injection experiment against V1.

### 3.6 What this section does NOT establish

- It does not establish that EVERY possible V1/V3 injection, at every
  possible pair of adjacent positions and every possible `M_t` draw, flips
  `F`. Only the specific fixed `(S_TEMPLATE, FAIL_TEMPLATE)` pair, under the
  specific perturbation operators tested, was checked. A defect could in
  principle still be missed on trials/positions where the neighbor
  arrangement happens not to trigger a flip (e.g. `S_TEMPLATE`'s
  read-one-late scenarios above show no flip at all under that direction).
- It does not establish a detection RATE at the level of the full T-trial
  `log2_Ahat_k` statistic — that requires actually injecting the defect into
  a full generator and re-running the estimator, which is red team's task,
  not this one's (this task's binding constraints reserve that experiment
  for `TASK-20260806-ae74c4`).
- Because this arm uses exactly TWO distinct realized bit-content vectors
  (one per label, repeated at every position with that label), it is not a
  test of content-DEPENDENT defects (e.g. a bug that only manifests for
  certain bit patterns unrelated to block boundaries); it is specifically a
  boundary/index-shift-focused construction, as the task requires.

## 4. Generation procedure

Per trial (vectorized over batches of `sub_chunk` trials, one jackknife batch
per generation batch, matching V1's per-batch RNG-stream structure):

1. Draw `M_t ~ Uniform{17,18,19}` and a uniform random `M_t`-subset of the 56
   block positions (`block_fail`, boolean array), via the SAME
   argsort-of-uniform-keys vectorized construction V1 used (a different
   implementation from `stage_a.py`'s Floyd's-algorithm
   `fixed_weight_support`, but the same exchangeable, uniform-subset
   guarantee, exactly as V1 documented).
2. Build the flat `(batch, n_e, 128)` bit tensor by INDEXING a
   `(2, 128)` template table with `block_fail.astype(int)`
   (`TEMPLATES[block_fail]`, fancy indexing: label 0 -> `S_TEMPLATE`, label 1
   -> `FAIL_TEMPLATE`), then reshape to `(batch, N)`.
3. Call `decode_blocks(bits, n_e, n_2, dup)` — THE REAL DECODER, imported
   read-only, sha256-pinned, unmodified — which itself performs
   `bits.reshape(B, n_e, n_2)` (`stage_a.py` line 296), the fold, the WHT,
   and the argmax/tie-break. This IS the block-partition/reshape/decode path
   OPEN-6 is concerned about; it is not reimplemented by this task.
4. Assert `F == block_fail` bit-for-bit (fail-closed self-check: if the REAL
   decoder ever disagrees with the planted label on the templates' own home
   turf — i.e. correctly-partitioned data — the run aborts rather than
   reporting a result from a construction whose premise has failed).
5. `S_t = F.sum(axis=1)`, accumulated into this batch's `(n_e+1,)`
   histogram.

`L = N // n_e` is asserted equal to `N_2` (RULE-2), and is, by construction
here, also the SAME `n_2` value passed into `decode_blocks` — the reshape
this arm relies on IS `decode_blocks`'s own reshape, not a separately
maintained copy of it.

## 5. Budget: T reduced from 1e7, and the residual this leaves

**T = 1e7 is not achievable within this task's 1800 core-second budget.**
V1's hand-rolled majority-threshold reduce measured ~64,700 trials/core-second.
This arm's generator instead runs the REAL WHT/Reed-Muller decoder — a size-128
fast Walsh-Hadamard transform per block, `n_e = 56` blocks per trial — which is
substantially more expensive. A pre-registration throughput calibration (run in
scratch space, `/tmp/.../scratchpad/bench.py`, NOT charged to this task's
budget, the same convention V1 used for its own calibration) measured, over
200,000 trials of the exact generation procedure in Section 4 (same templates,
same `decode_blocks` call, same self-check): **1198 trials/core-second**, a
~54x slowdown relative to V1's hand-rolled reduce. At 1198 trials/core-second,
`T = 1e7` would cost ≈8,347 core-seconds — more than 4.6x this task's entire
1800 core-second budget.

**Planned `T` for the authorized run: 1,000,000 (1e6), a 10x reduction from
PS-R3/V1's `T=1e7`.** Estimated cost at the calibrated rate: ≈834
core-seconds (≈46% of the 1800 s budget), leaving headroom for the
provenance/verification/estimator/jackknife stages and for wall-clock
variance. `planted_arm_v2.py` still carries a wall-clock budget guard
(matching V1's `WALL_BUDGET` pattern) that stops and reports a shortfall as
an INFRASTRUCTURE outcome, never silently truncating, if the actual measured
throughput in the authorized run differs materially from this calibration.
`comparison_report.md` reports the actually-achieved `T` and reconciles it
against this plan.

**Residual this leaves, stated plainly:** at `T=1e6` rather than `T=1e7`,
population-level jackknife standard errors scale up by approximately
`sqrt(10) ≈ 3.16x` relative to what a full `T=1e7` run of this SAME
real-decoder construction would show, all else equal. High-`k` cells (whose
planted `mu_bar_k` is tiny, e.g. `k=18`'s `mu_bar_18 ≈ 3.14e-14`) are the
most exposed to this: at `T=1e6`, the expected count of trials with `S_t=18`
is smaller, and cell reachability (in the `T_stab` sense `measure.py` and
`stage_a.py` both use) is correspondingly weaker than at `T=1e7`. This is
reported here as a pre-registered, honest limitation, not discovered after
the fact: any cell whose distance to the frozen 3-jackknife-SE band is close
should be read with this widened-SE context in mind, and `comparison_report.md`
states the per-cell jackknife SE explicitly so this is checkable, not
asserted.

## 6. What this arm exercises and what it still does not (honest disclosure, matching V1's Section 3.2 pattern)

### 6.1 Newly exercised, relative to V1

- `stage_a.py`'s actual `decode_blocks` (the real fold/WHT/argmax/tie-break
  decoder), sha256-pinned, unmodified, called directly on this arm's
  constructed data — not a hand-rolled substitute.
- `stage_a.py`'s `rm17_codewords()` and `brute_force_decode()`, used as an
  INDEPENDENT cross-check of both templates' true decode (Section 3.4).
- `decode_blocks`'s own internal `bits.reshape(B, n_e, n_2)` block-partition
  step — this arm does not maintain its own separate reshape; the
  block-partition path exercised IS the production one.
- Heterogeneous, near-decision-boundary per-block bit content (two distinct
  templates, `margin = 4` each), verified sensitive to the campaign-named
  V1/V3 "read one index early" perturbation class (Section 3.5).

### 6.2 Still NOT exercised (residuals carried forward from V1, restated precisely)

1. **The cryptographic `(T)`-sampler is still not run at all.** `CTRStream`
   (the SHA-256 counter-mode PRNG), `fixed_weight_support` (Floyd's
   algorithm), `ring_mul_sparse`/`ring_mul_dense` (the `F_2[X]/(X^n-1)` ring
   arithmetic that actually produces `e-tilde`), and the multiprocessing
   shard structure are all still untested by this arm. This arm constructs
   planted per-block content DIRECTLY (two fixed templates), not by sampling
   a genuine fixed-weight-support-derived `(T)`-distributed error vector
   end-to-end.
2. **Narrower marginal support than PS-R3.** `S_t`'s support is still the
   3-point set `{17,18,19}`, versus PS-R3's near-binomial spread over most of
   `{0,...,56}`.
3. **Exactly TWO distinct realized block-content vectors, not full
   heterogeneity across all 56 positions.** Every "succeed" block, at every
   position, in every trial, is bit-identical to `S_TEMPLATE`; every "fail"
   block is bit-identical to `FAIL_TEMPLATE`. This is a substantial
   improvement over V1's homogeneous all-0/all-1 construction (Section 3.5
   shows genuine boundary sensitivity that V1 provably lacked), but it is
   still far short of the real decoder's actual input distribution, where
   every block's 128 bits are close to i.i.d. draws from the ring-arithmetic
   output. A defect that requires bit-pattern DIVERSITY across positions
   (rather than being triggered by the two fixed patterns used here) is not
   exercised.
4. **No sharding/multiprocessing.** Single-process generation, unlike PS-R3's
   8-shard `(T)` arm.
5. **CTRL-POSHOM-style between-block covariance is still not targeted** by
   this arm's own MATCH/MISMATCH statistic, for the same reason V1 noted:
   `measure.py`'s primary estimator is a pure function of the marginal `S_t`
   histogram, so which SPECIFIC positions are marked fail (only their COUNT)
   does not affect the recovered `log2_Ahat_k`.

None of the above is closed by this task. This is a single control arm for
the *real decode_blocks reshape/decode -> S-histogram -> estimator/jackknife*
leg of OPEN-6, exercised on boundary-adjacent (not fully general) planted
content — a strictly stronger control than V1 along the two axes the red team
named, but not a resolution of OPEN-6.

## 7. What is reused vs. newly written

Reused (imported unmodified, sha256-pinned):

- From `measure.py` (`a4fd1ecb63f0ddc83c02ef45f2c65ab31cf13d13e7ae94f500e67465b24f5dc8`):
  `comb_matrix` (lines 213-222), `log2_A_from_hists` (lines 225-246),
  `N_JACK_BATCHES` (line 92, cross-checked), and the batch-histogram +
  point/loo/jmean/jse jackknife block (lines 730-739), copied verbatim with
  the same variable names, exactly as V1 did.
- From `stage_a.py` (`06a0a618432c00fe26c72ecf05a8d89489db61c5183931fdb76a378717681405`):
  `decode_blocks` (line 286), `rm17_codewords` (line 310, via
  `brute_force_decode`), `brute_force_decode` (line 323), `wht128` (line 270,
  called internally by `decode_blocks`). NOT reused: `CTRStream`,
  `fixed_weight_support`, `ring_mul_sparse`/`ring_mul_dense`,
  `support_to_int*`, the `(T)`/NULL-M shard workers, and every phase function
  (`phase_oracle`, `phase_contract_checks`, `phase_smoke`, `phase_calibrate`,
  `main`) — none of those are invoked.

Newly written for this task: the planted-law derivation (Section 2, same
construction as V1, independently re-derived), the template search and
pre-registered verification (Section 3), the generation procedure (Section
4) built around a direct call to the real `decode_blocks`, the seed
derivation (a fresh `SEED_PREFIX`, distinct from both V1's and `measure.py`'s),
and the MATCH/MISMATCH comparison logic (Section 8).

## 8. Comparison rule: MATCH / MISMATCH

Identical convention to V1 (`design.md` Section 5 there), adopted explicitly
for this task, not a verbatim `measure.py` rule (no point-estimate-vs.-
ground-truth interval exists in `measure.py` for a planted arm; its firing
rule instead compares against a pre-calibrated NULL quantile table that does
not apply here):

```
MATCH   iff  planted_log2_A_k(k)  is within  [ point_k - 3*jackknife_se_k ,
                                                 point_k + 3*jackknife_se_k ]
MISMATCH otherwise
```

using `point_k` and `jackknife_se_k` from the reused jackknife computation
(Section 4/7) applied to this arm's own sampled histogram.

## 9. Budget plan (summary)

| item | estimate | charged to this task's budget? |
|---|---|---|
| template search (Section 3.2) | a few minutes wall-clock, scratch space | NO (pre-registration exploration, like V1's throughput calibration) |
| throughput calibration (Section 5) | 200,000 trials, ≈167 wall-seconds, scratch space | NO (same convention as V1) |
| authorized run: provenance + fail-closed checks + template verification | negligible (<1 core-second) | YES |
| authorized run: generation, `T=1,000,000` | ≈834 core-seconds (estimated) | YES |
| authorized run: estimator + jackknife (reused verbatim) | negligible (<1 core-second) | YES |
| **total estimated, authorized run** | **≈835 core-seconds of 1800 authorized (≈46%)** | — |

If the authorized run's ACTUAL measured cost differs from this estimate,
`planted_arm_v2.py`'s wall-clock budget guard stops the run and reports the
shortfall explicitly (INFRASTRUCTURE outcome, never a silently truncated
result); `run_manifest.yaml` and `comparison_report.md` report whichever
actually happened.
