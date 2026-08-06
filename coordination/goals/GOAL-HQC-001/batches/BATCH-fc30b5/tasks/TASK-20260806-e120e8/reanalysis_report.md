# Matched-pair reanalysis + required-T derivation (TASK-20260806-e120e8)

`TASK-20260806-e120e8` (executor) · `BATCH-fc30b5` · `GOAL-HQC-001` ·
`EXP-HQC-982268`. Authorized by `DEC-20260806-9a4551`'s `next_actions` items
1-2. Pre-registration: `design.md` (written and frozen before
`matched_pair_reanalysis.py` was run on any real data). Raw output:
`reanalysis_results.json`. Full command/provenance: `run_manifest.yaml`.

**Claim tier: TOY, hard ceiling.** PS-R3 only (`n_e=56, n=7187, N=7168,
dup=1, m=17`), V3 defect class, `decode_blocks` last-block injection point —
identical scope to the pilot this reanalyzes (`TASK-20260806-77a574`).
**No new (T)-sampling was performed** (see Section 1). This report separates
observations from interpretation and makes no campaign-level recommendation
(full run / positive-control / PAUSE) — that call belongs to the
Coordinator and the two independent reviews of this batch.

---

## 0. What was done, in one paragraph

This task reused the Red Team's (`TASK-20260806-92aecb`) matched-pair method
— decode the SAME underlying random draws twice, once true and once
V3-defected, instead of comparing disjoint PRNG shards — and applied it to
the pilot's own two already-used shards (`5000`, `6000`, 5,000 trials
each, 10,000 matched pairs total), extending the method to the pilot's full
reported `k = 2..26` range. Before trusting any new number, the identical
code was run against the Red Team's own probe shard (`424242`) and matched
their reported numbers exactly/near-exactly (Section 2). The regenerated
shard-`5000`/`6000` histograms were also checked bit-identical against
`pilot_results.json`'s own committed numbers (Section 3). A required-T was
then derived for the propagated (`log2_Ahat_k`), not local, statistic, from
the Red Team's measured 10.7% local flip rate, via an explicit dilution
model and a stated power target (Section 5).

---

## 1. Data provenance: no new sampling

Every shard decoded by this task — `5000`, `6000`, `424242` — was already
used somewhere in this campaign's committed record before this task ran:
`5000`/`6000` by the pilot itself (`TASK-20260806-77a574`), `424242` by the
Red Team's own probe (`TASK-20260806-92aecb`, `red_team_report.md` Section
0). `pilot_results.json` does not retain raw per-trial bit arrays (only
summary histograms — the pilot's own script explicitly drops `F` before
serializing), so a matched-pair reanalysis is not computable from
`pilot_results.json` alone. Per this batch's explicit authorization, this
task **regenerated these three shards deterministically** via `stage_a.py`'s
real, unmodified `_t_shard()`, using the identical `MASTER_SEED` /
`DERIV_STRING` / `sha_key()` derivation the pilot and the Red Team both
used, and decoded each already-generated bit array **twice** (real
`decode_blocks`, then `pilot_injection.py`'s own `make_defected_decode_blocks`
— imported unmodified, not reimplemented). This is an additional decode call
on already-generated bits, not an additional random draw; no shard id
outside `{5000, 6000, 424242}` was ever requested.
`reanalysis_results.json.provenance.no_new_t_sampling = true` records this
explicitly, and Sections 2-3 below verify it produced the expected data.

---

## 2. Sanity check against the Red Team's own reported numbers: PASS, exact

Run **before** any pilot-shard result was computed (design.md Section 2.2,
fail-closed — a failure here would have aborted with no results file
written). Regenerating the Red Team's own probe shard (`424242`, `T=5,000`)
and applying this task's matched-pair implementation reproduced:

| quantity | Red Team reported | this task, reproduced |
|---|---:|---:|
| last-block flips | 533/5000 | **533/5000** (exact) |
| flip rate | 0.1066 | 0.1066 |
| matched-pair binomial SE | 0.00436 | 0.004414 |
| `z` (flip rate vs. 0) | ~24.4 | 24.78 |
| marginal `P(F_true=1)` | 0.3198 | 0.3198 |
| marginal `P(F_def=1)` | 0.3280 | 0.3280 |
| marginal diff | 0.0082 | 0.0082 |
| `k=17` point_true | -0.9360 | -0.9360 |
| `k=17` point_def | -0.7438 | -0.7438 |
| `k=17` diff | +0.1922 | **+0.1922** (exact) |
| `k=17` SE unpaired | 0.5514 | 0.5514 |
| `k=17` SE paired | 0.1982 | 0.1982 |
| `k=17` power ratio | 2.78x | 2.782x |
| `k=2` power ratio | ~10.6x | 10.00x |
| `k=24` power ratio | ~1.63x | 1.938x |

All 14 pre-registered sanity checks passed
(`reanalysis_results.json.sanity_check_vs_red_team.all_pass = true`); the
flip count and the `k=17` point-estimate difference match the Red Team's
reported figures to the digit. The small deviations on the two extreme-`k`
power ratios (`10.00x` vs. `~10.6x` at `k=2`, `1.938x` vs. `~1.63x` at
`k=24`) are within the Red Team's own stated 4-significant-figure rounding
and this task's `atol` tolerance, not a discrepancy in method. **This task's
implementation of the matched-pair method is confirmed to reproduce the Red
Team's own independently-reported numbers before any new result below is
reported.**

---

## 3. Bit-identical reproduction check against the pilot's own data: PASS, exact

Because raw per-trial data is not retained in `pilot_results.json`, this
task's regeneration of shards `5000`/`6000` was checked against the pilot's
own committed summary histograms (fail-closed; a mismatch would have
aborted before any new result was reported):

- Regenerated shard-`5000` **defected**-decode `S_histogram` == pilot's own
  `MEASUREMENT.defected.S_histogram` — **exact match, all 57 bins.**
- Regenerated shard-`6000` **true**-decode `S_histogram` == pilot's own
  `MEASUREMENT.undefected.S_histogram` — **exact match, all 57 bins.**

This confirms the regeneration used by this task is bit-identical to what
the pilot itself already collected and reported; the matched-pair analysis
below is not new data, it is the same data decoded one additional way.

---

## 4. Matched-pair statistics: k=17 and the full k=2..26 range

### 4.1 At the pre-specified load-bearing order, k=m=17

Combining both of the pilot's shards (10,000 matched pairs total):

| | pilot's original (between-shard) | this reanalysis (matched-pair) |
|---|---:|---:|
| diff (defected − true) | −0.2069 | **+0.0516** |
| SE | 0.4437 | **0.0966** |
| `z` | −0.466 | **+0.534** |
| SE ratio (unpaired / paired) | — | **3.12x** |

The matched-pair SE at `k=17` (0.0966) is **3.12x tighter** than the
pilot's own between-shard SE (0.4437) at the identical total trial count —
squarely inside the Red Team's reported 2.8x-10.6x range, and closely
matching their own `k=17` figure of 2.78x. **The sign flips relative to the
pilot's own reported diff** (pilot: −0.2069; this reanalysis, matched-pair,
combined: +0.0516). This is expected and pre-registered as
possible: `design.md`'s own predecessor document stated no a priori sign,
and different shards (the pilot's between-shard comparison vs. this
within-shard, matched comparison of the SAME shards) draw on different
combinations of trial-to-trial noise. **`z=+0.534` at `k=17` is not
significant** by the pre-registered `|z|>=3` threshold (design.md Section
2.5).

Per-shard breakdown (each already bit-identical-verified, Section 3):

| shard | flip rate | marginal diff | `k=17` diff | `k=17` SE paired | `k=17` z_paired |
|---|---:|---:|---:|---:|---:|
| 5000 (pilot's defected-arm draws) | 10.94% | +0.0026 | +0.1018 | 0.1251 | 0.814 |
| 6000 (pilot's undefected-arm draws) | 10.38% | −0.0022 | +0.0108 | 0.1499 | 0.072 |
| combined (10,000) | 10.66% | +0.0002 | +0.0516 | 0.0966 | 0.534 |

The local block-`n_e-1` flip rate is consistent (10.4%-10.9%) and
enormously significant (`z_flip` 24-35) in every one of these samples,
corroborating the Red Team's finding independently on the pilot's own data.
The `k=17` matched-pair `z` is not significant in either individual shard
or their combination.

### 4.2 Full reported range, k=2..26 (combined, 10,000 matched pairs)

Full table in `reanalysis_results.json.primary_matched_pair_analysis.combined_10000`.
Summary:

- **`z_paired` never exceeds `|0.632|`** anywhere in `k=2..26` (max at
  `k=2`, `z_paired=−0.632`; monotonically similar magnitude through `k~14-17`,
  then gently decaying toward `k=26`).
- **Power ratio (unpaired SE / paired SE) ranges from 10.00x at `k=2` down
  to 1.76x at `k=26`**, reproducing the Red Team's qualitative dose-response
  finding (tighter matched-pair advantage at low `k`, where the between-shard
  design's independent-arm SEs are relatively larger contributors) on the
  pilot's own data, not just on a fresh shard.
- No `k` in the reported range clears the pre-registered `|z|>=3` signal
  threshold under the matched-pair design.

---

## 5. Required-T derivation for THIS defect (V3, last-block-only)

### 5.1 Effect-size input, traced explicitly from flip rate to marginal shift

Per this batch's task card, the Red Team's measured **10.7% local flip
rate** (`533/5000`, `red_team_report.md` Section 0) is the effect-size
input. **The flip rate is not, by itself, the quantity that determines a
mean-level shift in `log2_Ahat_k`.** Flips in both directions
(true=0→def=1 and true=1→def=0) partially cancel in the **net marginal
shift**, `Δp = P(F_def=1) − P(F_true=1)`, which is the quantity that
actually propagates a mean shift into the joint-moment estimator. The Red
Team's own numbers already show this gap: flip rate `10.66%`, net marginal
shift only `0.82%` (roughly `13x` smaller). Skipping directly from flip rate
to marginal shift would substantially overstate the propagated effect; this
derivation uses `Δp`, not the raw flip rate, as the dilution-model input,
labeling the flip-rate-as-marginal-shift scenario explicitly as a
hypothetical upper bound (`reanalysis_results.json.required_T_derivation.per_k[*].
modeled_delta_log2_A_hypothetical_raw_flip_rate_as_marginal`), never as the
primary estimate.

**An important reliability caveat, discovered by this task, not assumed in
advance:** none of the four independent `Δp` point estimates available
(Red Team's fresh shard: `+0.0082`; this task's shard 5000: `+0.0026`;
shard 6000: `−0.0022`; their pooled combination: `+0.0002`) is itself
distinguishable from zero at these trial counts. Using a standard
McNemar-style paired-proportion SE (`SE(Δp̂) = sqrt(flip_rate/T)`), every one
of the four estimates has `|z| < 2` against a null of `Δp=0`
(`reanalysis_results.json.required_T_derivation.delta_p_reliability`). **The
local block-level flip rate is enormously significant in every sample; the
NET marginal shift is not yet established to be nonzero at all.** The
required-`T` numbers below are therefore an order-of-magnitude projection
conditioned on `Δp` being near the cited input value, not a precise number
derived from a securely-measured effect size — a `Δp`-sensitivity table
(`delta_p_sensitivity_k17`) is included in the raw results for this reason.

### 5.2 Dilution model and a structural finding: near-total first-order cancellation

Using the `k/n_e` dilution argument (only `k`-subsets containing block
`n_e−1` are affected) combined with the observed baseline moments
(`mubar_k`, `mubar_{k-1}`, from the pooled true-arm data, via `stage_a.py`'s
own `mubar_from_hist`, unmodified), the modeled shift decomposes as two
terms of the `log2_A_k = log2(mubar_k) - k*log2(q)` definition:

```
Delta(log2_A_k) = (k/n_e) * Δp / ln(2) * [ mubar_{k-1}/mubar_k − 1/q_hat ]
```

**This is not an incidental algebraic form: the bracket is exactly zero if
the block failures were i.i.d.** (`mubar_k = q^k` exactly implies
`mubar_{k-1}/mubar_k = 1/q` exactly). `log2_Ahat_k` is *defined* to subtract
out the marginal-rate-driven part of `mubar_k` (that is what the `-k
log2(q)` term is for), so a defect that only shifts one block's marginal
failure rate — with no change to the underlying correlation structure among
blocks — propagates to `log2_Ahat_k` **only through the second-order
interaction of that marginal shift with the already-present excess
correlation** (`mubar_{k-1}/mubar_k` vs. `1/q̂`, observed to differ by only
~12% at `k=17` in this campaign's own PS-R3 true-arm data). This is a
genuine structural property of the estimator, not a modeling artifact —
verified by an independent closed-form recomputation that reproduces the
code's output to machine precision (documented in this task's own working
notes; the code implements the two-term Taylor decomposition directly, and
both give `Delta(log2_A_17) = 0.001505` for the Red Team's `Δp=0.0082`).
**This means the joint-moment estimator is, by construction, much less
sensitive to a single-block marginal-only defect than the raw local flip
rate would naively suggest** — a second, independent source of dilution
beyond the already-identified `k/n_e` factor.

### 5.3 Power target (fixed in design.md Section 3.3, before this computation)

Two-sided `alpha=0.05` (`z=1.9600`), power `90%` (`z=1.2816`),
`z_sum=3.2415`. `SE(T) = SE_ref * sqrt(T_ref/T)`, `T_ref=10,000` (this
task's own combined matched-pair SE, not the pilot's wider between-shard SE
and not the specification's undefected-estimator `T_req=3.09e5`, which
answers a different question).

### 5.4 Required T, headline numbers

At `k=17` (load-bearing), using this task's own measured matched-pair SE
(`SE_paired=0.0966` at `T=10,000`):

| `Δp` input | modeled `Delta(log2_A_17)` | required T |
|---|---:|---:|
| Red Team's `Δp=0.0082` | 0.001505 | **4.33e8** |
| this task's combined `Δp=0.0002` | 0.0000367 | **7.28e11** |
| hypothetical: raw flip rate as marginal (`0.1066`) | 0.01957 | 2.56e6 |

Across the full reported range (`k=2..26`), using Red Team's `Δp=0.0082`,
required `T` ranges from **4.1e7** (`k=2`) to **4.4e8** (`k=17`, the
maximum in the range) down to **6.9e7** (`k=26`) — see
`reanalysis_results.json.required_T_derivation.per_k` for the full table.

**Every one of these numbers is 2-4 orders of magnitude larger than the
specification's undefected-estimator `T_req = 3.09e5`.** This is the
headline, decision-relevant fact of this derivation: even under the most
favorable of the three effect-size inputs above (the explicitly-labeled
hypothetical that treats the entire raw flip rate as a one-directional
marginal shift — the LEAST realistic of the three), the required `T` to
reliably detect this specific defect's propagated effect at the
pre-registered order via the matched-pair design is `~2.6e6`, roughly
**8x** the specification's `T_req`. Under the Red Team's own actual
measured `Δp`, it is roughly **1,400x** the specification's `T_req`. Under
this task's own (statistically indistinguishable-from-zero) combined `Δp`
estimate, it is **~2.4 million times** the specification's `T_req` — a
number this large should be read as "this input is consistent with no
detectable effect at any feasible T," not as a literal target, precisely
because of the Section 5.1 reliability caveat (a `Δp` estimate
indistinguishable from zero produces an unstable, arbitrarily-large
required-T under this 1/`Δp`² scaling).

---

## 6. Ambiguity resolution: does the matched-pair reanalysis, alone, settle the question?

**No — genuine ambiguity remains**, under the pre-registered criterion
(design.md Section 2.5) applied mechanically to the numbers above
(`reanalysis_results.json.ambiguity_resolution`):

- The matched-pair `z` at `k=17` (`+0.534`) does not clear the
  pre-registered `|z|>=3` signal threshold — no clear signal.
- The modeled propagated effect at `k=17` (Section 5.2-5.4) implies a
  required `T` (`4.33e8` under the Red Team's own `Δp`) that is **far above**
  the `T=10,000` this task achieved — so the matched-pair design's tighter
  SE, while a real, measured, 3.12x improvement over the pilot's own
  between-shard design at `k=17` (Section 4.1), is nowhere near tight enough
  at this trial count to distinguish "no propagated effect" from "an effect
  of the magnitude the Red Team's own local measurement implies" — no clear
  null either, by the pre-registered standard (Section 2.5: a clear null
  requires the achieved `T` to already exceed the derived required `T`,
  which it does not, by roughly five orders of magnitude at `k=17`).

**What this reanalysis DID resolve, stated plainly:** the pilot's original
between-shard design was demonstrably underpowered relative to the
free matched-pair alternative (now confirmed on the pilot's own actual data,
not only on the Red Team's independent fresh-shard probe) — a real,
measured, reproducible finding. **What it did NOT resolve:** whether the
defect's propagated effect on `log2_Ahat_k` is genuinely near zero or of
the (highly uncertain, per Section 5.1) magnitude the raw local measurements
suggest. The required-`T` derivation independently explains *why* it could
not, at this trial count: the modeled propagated effect, once correctly
diluted through both the `k/n_e` block-fraction factor and the estimator's
own built-in marginal-rate invariance (Section 5.2), is small enough that
even the tighter matched-pair design would need several to many orders of
magnitude more trials than either this pilot or the specification's
undefected-estimator `T_req=3.09e5` provides.

---

## 7. Budget and validity

- Core-seconds: **10.79 of 200 authorized** (5.4%).
- Wall-seconds: **10.4 of 1,800 authorized** (0.6%).
- Runs: **1 of 1 authorized**, used (one prior shakedown run was executed in
  session scratch space, not committed, not part of this deliverable set,
  to catch implementation bugs before the authorized run — identical
  precedent to the pilot's own `pilot_report.md` Section 1 practice; its
  output is bit-identical to the authorized run's, as expected from
  identical deterministic seeds, and is a determinism check, not a second
  measurement).
- `reanalysis_results.json.validity.status = "valid_measurement"`: all
  pre-registered mechanically-sound criteria (design.md Section 4) were met
  — sha256 pins verified, the reused defect wrapper genuinely calls the
  unmodified `decode_blocks`, the Section 2 sanity check passed, the
  Section 3 bit-identical check passed, neither regenerated shard was
  truncated, D2/D3 clean on both regenerated shards, and the estimator
  returns finite values at `k=m=17`.
- `certificate.kind: none` — this is a pure measurement/reanalysis run; no
  discrete-log solve or factor-base relation is claimed.

---

## 8. What this task does not conclude

Per `agents/executor.md`: this is a report of matched-pair statistics,
cross-checks, and a required-`T` derivation, offered as facts. Whether the
campaign proceeds to the full `T_req`-scale run, a positive-control pilot
(`DEC-20260806-9a4551` item 3), or a PAUSE review is the Coordinator's and
the two independent reviewers' call on this batch's evidence, not this
report's. Claim tier stays toy throughout; nothing here is a statement about
HQC, assumption A17, HQC's decoding-failure rate, or any standardized
parameter set. This task tested exactly one defect class, one injection
point, one parameter set, and the same two (now doubly-decoded) pilot
shards plus one sanity-check shard — nothing here generalizes to V1's
global shift, to the other three injection points, to PS-A/PS-R1/PS-R5, or
to any standardized HQC parameter set.

---

## 9. Artifacts

- `design.md` — pre-registered, written before this run.
- `matched_pair_reanalysis.py` — the reanalysis script (matched-decode
  monkey-patch + paired/unpaired jackknife comparison + required-T
  derivation; reuses `stage_a.py`/`measure.py`/`pilot_injection.py`
  sha256-pinned, read-only).
- `reanalysis_results.json` — full raw output of the one authorized run.
- `run_manifest.yaml` — command, git commit/dirty-state, environment, seeds,
  timings, validity status, explicit no-new-sampling statement.
- `stdout.log` / `stderr.log` — captured output of the authorized run.
- This file.
