# Design: matched-pair reanalysis + defect-specific required-T derivation
# (PRE-REGISTERED before `matched_pair_reanalysis.py` is run on any real data)

`TASK-20260806-e120e8` (executor) / `BATCH-fc30b5` / `GOAL-HQC-001` /
`EXP-HQC-982268`. Authorized by `DEC-20260806-9a4551`'s `next_actions` items
1-2, itself resting on `EV-HQC-67a6ec` and the Red Team's independent review
`TASK-20260806-92aecb` of the pilot `TASK-20260806-77a574`.

**This document is written and frozen before any regeneration or analysis
code is run.** The method, the data-provenance rule, the sanity-check
procedure, and the power/precision target for the required-T derivation are
fixed here in advance. `reanalysis_results.json` and `reanalysis_report.md`
are produced afterward and must not cause this file to be edited
retroactively.

Claim tier: **toy, hard ceiling**, identical scope boundary to the pilot this
task reanalyzes (PS-R3 only, `n_e=56, n=7187, N=7168, dup=1, m=17`, V3 defect
class, `decode_blocks` last-block injection point). Nothing here is a
statement about HQC, A17, any decoding-failure rate, or any standardized
parameter set.

---

## 1. What this task does and does not do

- **NO NEW (T)-SAMPLING.** Every random draw used below is either (a) read
  directly from `pilot_results.json`'s already-committed summary fields, or
  (b) a deterministic regeneration of a shard **already used** somewhere in
  this campaign's committed record (the pilot's own shards `5000`/`6000`, or
  the Red Team's own probe shard `424242`, itself already a matter of
  committed record in `red_team_report.md`), via `stage_a.py`'s real,
  unmodified `_t_shard()`, with the identical `MASTER_SEED`/`DERIV_STRING`/
  `sha_key()` derivation the pilot and the Red Team both used. Regeneration
  reproduces existing, already-recorded data; it does not collect new data.
  This is stated explicitly in `reanalysis_results.json.provenance` and
  `run_manifest.yaml`.
- Imports `stage_a.py`, `measure.py`, and `pilot_injection.py` **read-only**,
  sha256-pinned (`load_module()`, identical fail-closed pattern to every
  prior batch in this read scope). None of the three files is modified on
  disk. `pilot_injection.py`'s own `make_defected_decode_blocks` is reused
  directly (not reimplemented) so the V3 transform applied here is bit-for-
  bit the same object the pilot and this reanalysis both exercise.
- Reuses `measure.py`'s `comb_matrix` / `log2_A_from_hists` and `stage_a.py`'s
  `hist_of` / `batch_hists` / `evaluable_k` / `mubar_from_hist` /
  `N_JACK_BATCHES` / `T_STAB_THRESHOLD`, by direct call, exactly as the pilot
  and every prior estimator-using batch in this campaign did. No estimator
  math is reimplemented from scratch.
- Does **not** run the full `T_req` run. Does **not** run a positive-control
  pilot (that is item 3 of `DEC-20260806-9a4551`, out of this batch's scope).
  Does **not** touch `stage_a.py`, `measure.py`, `pilot_injection.py`, or
  `experiments/EXP-HQC-982268/specification.yaml`.
- Does **not** make the campaign-level call (full run / positive-control /
  PAUSE). Reports observations only, per `agents/executor.md`.

---

## 2. Deliverable 1: matched-pair reanalysis

### 2.1 Method, reused from the Red Team's `TASK-20260806-92aecb` §0 probe, not reinvented

The Red Team's method, read from `red_team_report.md` §0, is exactly this:
for a set of trials generated once, **decode each trial's bit array twice**
— once through the real, unmodified `decode_blocks` (the true bits) and once
through `pilot_injection.py`'s `make_defected_decode_blocks`-wrapped
`decode_blocks` (the V3-perturbed bits) — on the **identical underlying
random draws**, so the two arms share every source of trial-to-trial noise
except the one bit-window perturbation. This is reproduced here mechanically
as follows:

1. `sa._t_shard()` is called **unmodified** (same function, same signature,
   same per-trial generation loop as the pilot and Stage A both use). The
   ONLY new code is a monkey-patched `sa.decode_blocks` — reassigned to a
   thin wrapper, exactly the pilot's own monkey-patch convention — that,
   given a batch's `bits` array, calls the real `original_decode_blocks`
   **and** the pilot's own `defected_decode_blocks` (imported, not
   reimplemented) on the **same** `bits`, captures both `(F, W, ties)`
   triples into an external accumulator (indexed by call order, i.e., trial
   order), and returns the true-decode triple (so `_t_shard`'s own return
   value, used only for a bit-identical cross-check below, reflects the
   undefected path).
2. Because `_t_shard`'s D2/D3 hard invariants and the trial-generation loop
   run **before** `decode_blocks` is ever called (identical to the pilot's
   own reasoning in `design.md` §3), this patch cannot alter generation; it
   only adds a second decode call per batch.
3. This is applied to **both** of the pilot's own already-used shards:
   `5000` (the pilot's defected arm) and `6000` (the pilot's undefected
   control arm), at `n_trials=5000` each (identical to the pilot's own
   `N_TRIALS_DEFECTED`/`N_TRIALS_UNDEFECTED`), giving **two independent
   batches of 5,000 matched pairs each, 10,000 matched pairs total** — using
   strictly more of the pilot's own already-collected shard budget than
   either the pilot's between-shard design (which never matched draws) or
   the Red Team's own probe (which used one fresh shard, `T=5,000`).

### 2.2 Sanity check, run BEFORE any new result is reported (fixed in advance)

Before trusting this task's own implementation of the matched-pair method
on the pilot's shards, the identical code path is run against the Red
Team's own probe shard (`424242`, `T=5,000`, disjoint from every shard used
anywhere else in this campaign's record, exactly as `red_team_report.md`
states) and its output is compared, field by field, against the Red Team's
own reported numbers in `red_team_report.md` §0:

- last-block flip count/rate (`533/5000 = 0.1066`), matched-pair binomial SE
  (`0.00436`), and `z` (`~24.4`);
- marginal `P(F_{n_e-1}=1)`: true `0.3198`, defected `0.3280`, diff `0.0082`;
- `log2_Ahat_17`: `point_true=-0.9360`, `point_def=-0.7438`,
  `diff=+0.1922`, `SE_unpaired=0.5514` (`z=0.349`),
  `SE_paired=0.1982` (`z=0.970`), power ratio `2.78x`;
- power ratios at `k=2` (`~10.6x`) and `k=24` (`~1.63x`).

Because the underlying PRNG is a deterministic function of
`(set_id, arm, shard, MASTER_SEED, trial_index)`, and both this task and the
Red Team load the identical sha256-pinned `stage_a.py`, the flip
count/marginal counts are expected to match **exactly** (integer counts over
5,000 trials); the `log2_Ahat_k` point estimates and jackknife SEs are
expected to match to within ordinary floating-point/reporting-precision
tolerance (`atol=5e-3` on point estimates/SEs, `rtol=2%` on power ratios,
chosen to be forgiving of the Red Team's own 4-significant-figure reporting
while still catching a genuine methodological or arithmetic divergence).
**A failure of this sanity check is FAIL-CLOSED**: it aborts
(`SystemExit`) before any new (pilot-shard) result is computed or reported,
because it would mean this task's reproduction of the Red Team's method is
not, in fact, the same method.

### 2.3 Bit-identical reproduction check (fixed in advance)

Because this task regenerates the pilot's own shards `5000`/`6000` from
scratch (rather than reading raw per-trial data out of `pilot_results.json`,
which does not retain it — only summary histograms), the following
FAIL-CLOSED check runs before any new result is reported: the regenerated
shard-`5000` **defected**-decode histogram must equal
`pilot_results.json.MEASUREMENT.defected.S_histogram` **exactly** (bit-for-
bit integer match), and the regenerated shard-`6000` **true**-decode
histogram must equal `pilot_results.json.MEASUREMENT.undefected.S_histogram`
exactly. A mismatch on either aborts the run before further computation.

### 2.4 Scope of the k range

Reported for `k = 2..26`, the pilot's own `ks_reported` intersection range
(`pilot_results.json.reachability.ks_reported`), including the pre-specified
load-bearing order `k = m = 17`. Both the **paired** (matched-pair
jackknife-on-the-difference, Red Team's method) and **unpaired**
(independent-arm jackknife, quadrature-summed — the pilot's own original
method) statistics are reported at every `k`, so the power ratio the Red
Team found (2.8x-10.6x) can be checked across the full range on the pilot's
own data, not just at `k=17`.

### 2.5 What "resolves the ambiguity" means here, fixed in advance

The Red Team's finding was that the pilot's between-shard design could not
distinguish "genuinely near-zero propagated effect" from "an effect of the
magnitude the raw point estimates suggest, invisible to that design's wider
SE." This reanalysis resolves that specific ambiguity if, and only if, the
matched-pair `z_paired` at `k=17` (and, informatively, across the reported
range) is **either** clearly significant (a stated numeric threshold,
`|z| >= 3`, is used here as "clearly significant" — chosen because it is
the same order of stringency this campaign's own hard invariants and prior
batches have used for a non-arguable signal, not a post-hoc pick) **or**
tight enough that the modeled propagated effect size derived in Section 3
below would have been clearly visible at this `T` had it been present (i.e.
the achieved paired SE is smaller than the modeled effect divided by the
same `z`-threshold). If neither holds — the paired result is still
consistent with both "no effect" and "an effect of the modeled magnitude" —
this task reports that the ambiguity **remains**, explicitly, rather than
rounding to either conclusion. Which of these outcomes obtains is not
decided in advance; both are pre-registered-consistent.

---

## 3. Deliverable 2: required-T derivation for THIS defect

### 3.1 Effect-size input, stated in advance

The **Red Team's measured 10.7% local flip rate** at block `n_e-1`
(`red_team_report.md` §0, `533/5000`) is the effect-size input, per this
batch's task card. This task also independently remeasures the same
quantity on the pilot's own two shards (10,000 matched pairs total, Section
2.1) as a corroborating, higher-precision measurement, and reports both.

**The flip rate is not, by itself, the correct input to a dilution-based
projection of the effect on `log2_Ahat_k`.** The flip rate `P(F_true !=
F_def)` counts trials that change the block-`n_e-1` outcome in **either**
direction; what determines the shift in the joint-moment statistic's
expectation is the **net marginal shift**, `Δp = P(F_def=1) - P(F_true=1)`,
which can be — and, per the Red Team's own numbers, is — substantially
smaller than the flip rate when flips partially cancel (RT: flip rate
`10.66%`, net marginal shift `0.82%`, roughly a `13x` gap). This derivation
therefore traces the full chain, stated in advance: **measured flip rate ->
measured net marginal shift `Δp` -> modeled shift in `log2_Ahat_k` via the
`k/n_e` dilution argument `design.md` (of the pilot) already gave
qualitatively -> required `T` under the matched-pair design's measured SE
scaling.** Skipping directly from the flip rate to the `log2_Ahat_k` shift
(treating the whole 10.7% as if it were a one-directional marginal shift)
would be an avoidable overestimate of the propagated effect and is reported
separately, labeled explicitly as an upper-bound/hypothetical, not used as
the primary input.

### 3.2 Dilution model, stated in advance

Only block `n_e-1` is perturbed. `mubar_k = E[C(S,k)]/C(n_e,k)` is, by
construction (`stage_a.py`'s own `mubar_from_hist`), the probability that a
uniformly random `k`-subset of the `n_e` blocks are all failing. A uniformly
random `k`-subset contains block `n_e-1` with probability `k/n_e`. Treating
block `n_e-1`'s failure as approximately independent of the other blocks'
joint failure (the same simplifying assumption `design.md` used
qualitatively, an approximation not re-derived here) gives:

```
mubar_k = (k/n_e) * p_{n_e-1} * mubar_{k-1}^{other} + (1 - k/n_e) * mubar_k^{other}
```

where `mubar_{k-1}^{other}`/`mubar_k^{other}` are the (defect-independent)
moments restricted to the other `n_e-1` blocks. Since the defect changes
only `p_{n_e-1}` by `Δp` (to first order, and the `mubar^{other}` terms are
shared between arms):

```
Delta(mubar_k) ~= (k/n_e) * Δp * mubar_{k-1}
Delta(log2_A_k) = Delta(log2(mubar_k)) - k*Delta(log2(q))
                ~= Delta(mubar_k) / (mubar_k * ln 2)         [dominant term]
```

using the pilot's own **true**-arm `mubar_k`/`mubar_{k-1}` (computed via
`sa.mubar_from_hist`, unmodified, on the pooled 10,000-trial true-decode
data from Section 2.1) as the baseline, since the true arm is what the
defect is a perturbation of. The `k*Delta(log2 q)` term (`Delta(q) ~=
Δp/n_e`, two further orders of magnitude smaller) is computed and reported
alongside but is not expected to change the leading-order conclusion; this
is stated in advance as a legitimate simplification, not hidden after the
fact.

### 3.3 Power/precision target, stated in advance

- Two-sided significance level `alpha = 0.05` (`z_{1-alpha/2} = 1.95996`).
- Target power `1 - beta = 0.90` (`z_{1-beta} = 1.28155`).
- Combined factor `z_sum = z_{1-alpha/2} + z_{1-beta} = 3.24151` (the
  standard normal-approximation two-sample/paired power formula:
  `T_req = T_ref * (z_sum * SE_ref / Delta_target)^2`, `SE_ref` being the
  **matched-pair jackknife SE at the reference T**, `T_ref = 10,000`, i.e.
  this task's own combined-shard result from Section 2, not the pilot's
  wider between-shard SE and not the specification's undefected-estimator
  `T_req = 3.09e5` from a different quantity).
- SE is assumed to scale as `SE(T) = SE_ref * sqrt(T_ref / T)` (ordinary
  central-limit / jackknife-of-a-smooth-statistic scaling). This is an
  explicit, stated **assumption**, not a re-derivation: it may not hold
  exactly at a `T_req` far from `T_ref`, particularly if `T_req` implies
  `k` values near the `T_STAB_THRESHOLD` reachability boundary behave
  non-Gaussian, which this task does not independently verify.

`T_req(k)` is reported for every `k` in the reported range, computed from
`Delta_target(k)` (Section 3.2, both using this task's own measured `Δp`
and, separately, the Red Team's stated `Δp=0.0082`, as a sensitivity check),
highlighted at the pre-specified load-bearing order `k=17`.

---

## 4. Mechanically-sound criteria for this task (fixed in advance)

**Sound / results reportable** requires ALL of:

1. Both fail-closed self-tests (sha256 pin mismatch, reused from the
   pilot's own `selftest_fail_closed_sha_mismatch`-style construction)
   demonstrably abort.
2. The Section 2.2 sanity check against the Red Team's own reported numbers
   passes within the stated tolerances.
3. The Section 2.3 bit-identical reproduction check against
   `pilot_results.json`'s own committed histograms passes exactly.
4. No uncaught exception; neither regenerated shard is truncated
   (`truncated=False`).
5. The estimator returns finite values at `k=m=17` on the combined
   matched-pair data.

Any failure of 1-3 is FAIL-CLOSED (`SystemExit`, no results file written).
A failure of 4-5 is reported as `invalid_measurement`, not silently retried.

---

## 5. What this task does not conclude

Per `agents/executor.md`: this task reports the matched-pair statistics, the
sanity-check/bit-identical cross-checks, and the required-`T` derivation as
facts. Whether the campaign proceeds to the full `T_req`-scale run, a
positive-control pilot, or a PAUSE review is the Coordinator's and the two
independent reviewers' call on this batch's evidence, not this document's or
`reanalysis_report.md`'s. Claim tier stays toy throughout.
