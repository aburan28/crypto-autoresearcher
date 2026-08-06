# Red-team report — V2 planted-correlation control arm for OPEN-6 (TASK-20260806-047535)

**Task** `TASK-20260806-ae74c4` (red team) · **Batch** `BATCH-558f5b` · **Goal**
`GOAL-HQC-001` · **Reviews** `TASK-20260806-047535`'s snapshot (commit
`08d1c07a`) · **Produced** 2026-08-06.

**Frozen artifacts read.** `design.md`, `planted_arm_v2.py`,
`planted_results.json`, `comparison_report.md`, `run_manifest.yaml` under
`coordination/goals/GOAL-HQC-001/batches/BATCH-558f5b/tasks/TASK-20260806-047535/`,
verified reachable from `HEAD` (commit `08d1c07a`). I also re-read
`ledger/evidence/EV-HQC-db1fd9.yaml`, my own prior report
(`TASK-20260806-21c8da`), and `stage_a.py`'s `decode_blocks`/`wht128`
(`BATCH-6fddee/TASK-20260806-64b506`) directly, independent of this task's
own narration of them. I did not read the Validator's report
(`TASK-20260806-01a340`, also committed) — independent session, no
conferring, exactly as I did against V1. I modified none of the frozen
artifacts; all injection/measurement code lives in scratch space
(`/tmp/.../scratchpad/redteam_v2_injection.py`,
`/tmp/.../scratchpad/redteam_v2_naturalness.py`), not committed, per the same
convention my V1 report used.

Both reused source files' sha256 were independently recomputed by me and
match what `planted_arm_v2.py` pins: `stage_a.py` →
`06a0a618432c00fe26c72ecf05a8d89489db61c5183931fdb76a378717681405`;
`measure.py` → `a4fd1ecb63f0ddc83c02ef45f2c65ab31cf13d13e7ae94f500e67465b24f5dc8`.

---

## VERDICT

# **ADMIT the artifacts, subject to one binding correction (§5). OPEN-6: PARTIALLY CLOSED — the specific "detection is mathematically impossible" finding against V1 is retired, but OPEN-6's own concern is not.**

Unlike V1 — which I found structurally blind to boundary-index-shift defects
**with probability exactly 1, for any T** — this V2 arm's two engineered
templates **do** get flipped, and the flip **does** propagate into a large,
easily-detected `log2_Ahat_k` deviation, for every variant of the V1/V3
defect class I injected (global, last-block-only, and an arbitrary interior
position, in both the named "early" and the unnamed mirror "late"
direction). That specific structural objection to the campaign's planted-arm
methodology is now false and should be retired.

But I also found that this "100% detection" is an **artifact of a
deliberately worst-case, hand-searched template pair**, not a property that
transfers to realistic block content. Independently measuring the natural
WHT margin and the natural single-position "read-one-early" flip rate on
Bernoulli(0.35) content — this campaign's **own** stated proxy for
"realistic crypto-like noise density" (`design.md` §3.2) — gives a flip rate
of **~8.8%** overall (and only **~19.6%** even when I restrict to the
sub-population that already shares the templates' margin ≤ 4), not the
**100%, deterministic** flip these two templates show. The templates were
not merely "near-boundary" — per `design.md` §3.2 they were specifically
searched for and kept *because* a boundary-shift perturbation flips them,
which guarantees an all-or-nothing (0% or 100%) result at the population
level for any fixed pair, and this run happened to land in the 100% regime.
That is real, structural progress over V1 (which was mathematically
incapable of ever landing there), but it is not evidence that the *real*,
heterogeneous PS-R3 pipeline — where per-block content is not hand-picked —
would show anywhere near this detection rate if it actually carried a
V1/V3-class bug.

---

## 1. Injection experiment: does the defect propagate to F, S, and `log2_Ahat_k` — not just a self-check?

**Yes, overwhelmingly, for the exact fixed template pair this arm uses — via
both mechanisms, and independent of which position is hit.**

I built a standalone reimplementation of `run_batch()`'s position-marking +
template-lookup + real-`decode_blocks` machinery (not an edit of the
committed script), transcribing `S_TEMPLATE`/`FAIL_TEMPLATE` byte-for-byte
and re-verifying both independently against the real decoder before use
(`[verify]` line in my transcript below). I injected:

- **V1 — global.** The literal circular "read-one-early" shift applied to
  *every* one of the 56 blocks simultaneously (the decode-side analogue of
  the shift `idxmap_probe.py`/my V1 report used).
- **V3 — last-block-only.** The same shift applied only to block 55.
- **Position-generality probe.** The same single-block shift applied to an
  arbitrary interior position (block 10) instead of the last block.
- **Direction probe.** The mirror-image "read-one-late" shift at a single
  position — not one of the campaign's two officially named classes, but the
  direction `design.md` §3.5 itself tested as a "sanity probe" and found
  asymmetric (flips `FAIL_TEMPLATE` in both neighbor scenarios but never
  flips `S_TEMPLATE`).

### Empirical result (real `decode_blocks`, T = 100,000 trials per variant, 20 jackknife batches; closed-form predictions independently derived and cross-checked against the empirical run — they agree to within sampling noise in every case):

| variant | per-block mismatch rate (`F != block_fail`) | positions affected | S_t support shift | recovered vs. planted, using the REAL run's own T=1e6 jackknife SE |
|---|---|---|---|---|
| none (baseline) | 0.000000 | — | {17,18,19} (unchanged) | within a few SE (sampling noise only) |
| **V1 global-early** | **1.000000** (all 56 positions, 100%) | all | {37,38,39} (S → 56−S) | **k=2: −10090 SE; k=18: −13544 SE** — MISMATCH at every k |
| **V3 last-block-early** | 0.017857 overall = **100% at position 55**, 0% elsewhere | {55} | {16,...,20} | **k=2: −1264 SE; k=18: −2372 SE** — MISMATCH at every k |
| **pos10-early** (position generality) | 0.017857 overall = **100% at position 10**, 0% elsewhere | {10} | {16,...,20} | **k=2: −1283 SE; k=18: −2395 SE** — MISMATCH at every k, statistically indistinguishable in magnitude from V3 |
| **last-block-late** (direction probe) | 0.005798 overall = **32.5% at position 55** (not 100% — see §2) | {55} | {16,17,18,19} | **k=2: +113 SE; k=18: +90 SE** — MISMATCH at every k, smaller magnitude but still overwhelming |

Every injected variant produces a `log2_Ahat_k` deviation of many tens to
many thousands of jackknife SE against the *actual* SE this arm achieved at
T=1e6 (`planted_results.json`) — nowhere close to the ±3 SE MATCH band. **This
is not merely "the self-check fires"; the estimator-level statistic itself,
computed the same way `measure.py`'s reused `log2_A_from_hists`/jackknife
code computes it, would show an unambiguous MISMATCH even if the self-check
did not exist.** This directly answers the task's central question: F and S
genuinely change, not just an internal sanity flag.

**Position independence, confirmed.** V3 (position 55) and the interior-position
probe (position 10) give essentially identical mismatch rates and SE
distances (within a few percent of each other, consistent with sampling
noise at T=100,000). For the "early" direction and this fixed template pair,
detection does **not** depend on which of the 56 positions the defect hits.

---

## 2. Is detection an artifact of the specific templates, not a property of realistic content?

**Yes — this is the residual worth naming precisely, and it is large, not
speculative.**

The `late`-direction row above (32.5% mismatch rate, not 100%) is itself the
first hint: even holding the templates fixed, detection is **direction-
dependent**, because `S_TEMPLATE` never flips under "late" (only
`FAIL_TEMPLATE` does — `design.md` §3.5's own table already shows this per-
scenario; I confirmed it aggregates to a 32.5% overall mismatch rate at
T=100,000, matching the closed-form prediction `P(position 55 was
originally fail) = E[M]/56 ≈ 0.321` almost exactly).

To test whether the *templates themselves* are representative, I
independently generated Bernoulli(0.35) 128-bit content — `design.md` §3.2's
**own stated proxy** for "realistic crypto-like noise density," used there to
*search for* the two templates — and measured, on 300,000 fresh draws
against the real `decode_blocks`/`wht128`:

```
margin: min=0  median=8.0  mean=10.70  max=60
fraction of natural blocks with margin<=4 (= S_TEMPLATE/FAIL_TEMPLATE's margin): 38.8%
natural single-position "read-one-early" flip rate (random foreign bit):  8.8%  (overall)
                                                                          19.6%  (conditioned on margin<=4)
```

So while margin ≤ 4 is not itself rare under this content model (38.8% of
blocks), the property the two committed templates actually have — a
**guaranteed, deterministic** flip under this exact perturbation, in *both*
same-label and different-label neighbor scenarios — occurs far less often:
my direct measurement puts the natural single-position flip probability at
**~8.8%** unconditionally and **~19.6%** even restricted to the already-
narrow margin≤4 sub-population, roughly 5–11x lower than the 100% these two
hand-searched templates exhibit.

This is a structural consequence of the construction, not an unlucky draw:
`design.md` §3.2 step 2 explicitly searched by *flipping bits and
recomputing F* to find pairs that "flip `F` relative to the unperturbed
block" — i.e., the search selection criterion for these two specific
templates *was* "guarantees a flip," which can only ever produce an all-or-
nothing result (0% for V1's all-0/all-1 pair, 100% for this pair) at the
population level for a two-fixed-template construction. There is no
intermediate regime this construction can express, and the executor happened
to (successfully) search for the 100% regime rather than land there by
chance on realistic content. **A defect's actual detection RATE against the
real, heterogeneous PS-R3 pipeline remains unmeasured and unmeasurable by
this arm's own construction** — this instrument can show "detection is
*possible*" (a real, meaningful result — V1 could not even show that) but
cannot show "detection occurs at rate X," because rate X is exactly what a
two-fixed-template design collapses to {0%, 100%} by construction.

---

## 3. Is "identical pipeline" (measure.py reuse) still honest?

**Yes, on inspection, and the same nuance from my V1 report still applies
without new problems.** `planted_arm_v2.py` imports `measure.comb_matrix`
and `measure.log2_A_from_hists` via `importlib` and calls them directly
(confirmed by reading the script: `C = measure.comb_matrix(n_e, ks)`,
`point = measure.log2_A_from_hists(hist[None, :], n_e, ks, C)[0]`), and the
`point`/`loo`/`jmean`/`jse` jackknife block is reproduced formula-for-formula
with the same variable names, matching `measure.py` lines 730-739. My own
standalone probe additionally calls `measure.comb_matrix`/
`measure.log2_A_from_hists` directly (not a reimplementation) to compute
recovered values from my injected histograms, and the resulting
`log2_Ahat_k` values are internally consistent with the closed-form
predictions I derived independently — this cross-checks that the reused
estimator code, called on defect-injected data, behaves as expected, not
merely on clean data.

As in V1, `bh`/`hist` here is accumulated from this arm's own per-batch
generator rather than sliced from `measure.py`'s own monolithic `S_all`
construction (lines 730-733) — a different code path producing the same
object shape, not literally lines 730-733 executing on this arm's data. This
is the same disclosed nuance my V1 report already flagged; it is not new and
I found no additional discrepancy beyond it.

**The one genuine upgrade over V1's reuse claim**: `decode_blocks` itself —
the actual block-partition/reshape/WHT/argmax code, `stage_a.py` line 286 —
is now called directly and unmodified (confirmed: `sa.decode_blocks(bits,
n_e, n_2, dup)` in my own reimplementation and in the committed script),
where V1 never invoked it at all. This is the real, substantive fix the
executor's design.md claims, and I found it genuine.

---

## 4. T reduced 10x (1e7 → 1e6): does this weaken the specific findings here?

**Not for the defects I tested — but this is a narrower claim than "the
T-reduction is harmless."**

Every injected variant produced deviations of 90 to over 13,000 jackknife SE
against the arm's *actual* T=1e6 SE. `design.md` §5's own pre-registered
residual (SEs widen by `sqrt(10) ≈ 3.16x` relative to a T=1e7 run) would, if
applied, still leave every one of these deviations many tens to thousands of
SE outside the band — the T-cut does not rescue any of these defects from
detection, and would not have, even at T=1e7. **This is not because the
T-reduction is inconsequential in general — it is because these particular
defects are enormous relative to this arm's own narrow-support noise floor
(§2's `q` distance to the real S_t range is a ~2% shift for even the
single-position defect, and the arm's SE is tiny because its S_t support is
only {17,18,19}), not because T=1e6 is adequate on its own merits.** A
defect an order of magnitude smaller than what I tested here (which,
per §2, is exactly what the *natural* ~8.8%-flip-rate regime would plausibly
produce if it aggregated only partially rather than deterministically) could
plausibly sit closer to the boundary of detectability, and there the
T-reduction's `sqrt(10)`-wider band would matter more. This arm's own report
(`comparison_report.md` §6, `design.md` §5) already discloses the T-cut and
its SE-scaling honestly; I find no additional understatement specific to the
defects I actually measured, but the "residual" as reported focuses on
high-`k` reachability, not on this margin-of-safety-for-smaller-defects
point, which I add here as a distinct, narrower observation.

---

## 5. Binding correction (if the artifacts are admitted)

**State the detection-rate finding at the correct scope, not the scope the
current framing invites.** `comparison_report.md` §4 and `design.md` §3.5
report, correctly, that a "genuine, non-zero chance" of flipping was
demonstrated — that phrasing is defensible and I do not dispute it as
stated. But it should not be read, and should be amended (in the evidence
record that cites this arm, not by editing the frozen artifacts) to make
explicit: *"The demonstrated flip is a deterministic (100%) property of one
specifically hand-searched template pair under this exact perturbation, not
a measured or estimated detection RATE for realistic block content. An
independent Red Team measurement against Bernoulli(0.35) content — this
campaign's own stated proxy for realistic crypto-like noise density — found
a natural single-position flip rate of ~8.8% (and ~19.6% even restricted to
content that already shares these templates' small margin), roughly 5-11x
lower than what these two templates exhibit. Because this arm's construction
uses exactly two fixed templates, it can only ever express an all-or-nothing
{0%, 100%} outcome at the population level and cannot produce a calibrated
estimate of the real pipeline's actual sensitivity to this defect class."*
This is the same category of correction (narrowing an accurate-as-stated but
easily over-read claim) my V1 report issued in its §6.

---

## 6. Baseline and cost-model notes (`agents/red-team.md` contract)

**Baseline comparison.** As with V1, not a Pollard-rho/BSGS-class claim; the
relevant comparison is against `CTRL-POSHOM`'s own measured, real-crypto-data
shifts under V1/V2/V3 (my V1 report §2: −0.0243%, −0.0566%, +0.0015% marginal
`q̂` shifts on real heterogeneous data). This V2 arm's *own* q-shift under a
single-position defect is ≈+1.98% (computed from the closed-form induced law
in §1) — **two orders of magnitude larger** than what the same defect class
produces on real crypto data. This gap is the same phenomenon as §2's
flip-rate gap, expressed in the marginal statistic instead of the per-block
flip rate, and reinforces the same conclusion: this arm's demonstrated
sensitivity is calibrated to its own hand-picked worst-case content, not to
the real pipeline's actual sensitivity.

**Cost-model / heuristic challenges.** Not applicable in the exponent-first/
Wesolowski-profile sense — toy-tier HQC decoder-statistic instrument check,
not an asymptotic ECDLP claim.

**Budget.** Authorized 1,800 wall-clock seconds. Measured: my injection
script (`redteam_v2_injection.py`, closed-form derivations plus 5 empirical
variants × 100,000 trials against the real `decode_blocks`) ran **≈226
wall-seconds core compute** (`real 3m45s`); my naturalness probe
(`redteam_v2_naturalness.py`, 2×300,000-trial margin/flip-rate measurement)
ran **≈22 wall-seconds**; a supplementary margin-conditioned flip-rate check
ran a few more seconds. **Total measured wall-clock for this task's compute:
≈4.2 minutes against the 1,800-second (30-minute) budget (≈14%). No
overrun.** No result was trimmed or subsampled to fit budget.

---

## 7. OPEN-6 disposition: **PARTIALLY CLOSED**

**What is closed.** My V1 report's specific finding — that boundary/
index-shift defects (V1 off-by-one, V3 last-block-early) are undetectable by
this campaign's planted-arm methodology **with probability exactly 1, for
any T**, as a structural/mathematical fact independent of scale — is now
false. V2 demonstrates, by injection against a faithful standalone copy of
its own machinery, that these defects **do** propagate to large,
unambiguous deviations in the same `log2_Ahat_k` estimator the real PS-R3
pipeline's methodology would use, for at least one construction, at every
tested position, in both the officially named direction and its mirror.
That specific negative result is retired; the executor's stated goal
("closes two gaps the Red Team found in V1") is genuinely met for the *first*
gap (real decoder) and *partially* met for the second (heterogeneous,
boundary-adjacent content) — heterogeneous in label, but not in the
underlying bit-content diversity that would let detection RATE be measured.

**What remains open.** OPEN-6's actual question — whether PS-R3's striking
`EV-HQC-b71230` anti-correlation signal could be an artifact of a subtle,
undetected sampler bug in the *real* pipeline — is not answered by a
demonstration that a specifically hand-searched, worst-case template pair is
100%-detectable in a toy 3-point-support law with an artificially tiny
noise floor. Three gaps remain, each independently sufficient to keep OPEN-6
open:

1. **No calibrated detection RATE against realistic content.** §2's
   independent measurement (natural flip rate ≈8.8%, not 100%) shows the
   demonstrated sensitivity does not transfer quantitatively to real
   heterogeneous data; the true detection rate for a genuine defect in the
   real pipeline is unmeasured, and by this arm's own two-template
   construction, unmeasurable.
2. **The real `(T)`-sampler is still never run** (`CTRStream`,
   `fixed_weight_support`, `ring_mul_sparse`/`dense` — `design.md` §6.2 item
   1, unchanged from V1 and correctly disclosed there). Nothing here
   establishes that any such defect actually exists in, or is exercised by,
   the real generation path — only that *if* one existed and *if* it hit
   content this close to the boundary, `decode_blocks` could express it as
   an error.
3. **This arm's own noise floor is not PS-R3's noise floor.** The
   thousands-of-SE detection margins in §1 are a function of this arm's
   narrow `S ∈ {17,18,19}` support; PS-R3's real, near-binomial `S_t`
   spread over most of `{0,...,56}` has a substantially larger natural
   jackknife SE, against which the *same absolute* defect-induced shift
   would represent a much smaller number of SE — a fact §4 already
   anticipates for smaller defects and which this arm has no mechanism to
   quantify for PS-R3 specifically.

**Net read:** the strongest available prior objection to trusting this
campaign's planted-arm methodology (deterministic invisibility) is gone; a
weaker, still-real objection (uncalibrated, worst-case-only sensitivity
demonstration) replaces it. This is progress, honestly reported as partial,
not full, closure.

---

## 8. Cheapest next concrete action

Build a V3 planted arm (or extend this one) that replaces the two fixed
templates with a **genuinely heterogeneous ensemble** — e.g., per-position,
per-trial content drawn from the same Bernoulli(0.35)-style distribution
`design.md` §3.2 already used for its search, filtered only by the
constraint needed to keep `S_t`'s marginal law closed-form (e.g., condition
on decode outcome matching the planted label, but let the *specific*
succeeding/failing bit pattern vary across positions and trials rather than
being fixed). This would let a boundary-shift injection experiment measure
an actual population-level detection RATE (not {0%, 100%}) and let that rate
be compared, quantitatively, against the ~8.8% natural flip-rate baseline
this report establishes — the missing ingredient for turning "detection is
possible" into "detection would occur with probability p," which is the
quantity OPEN-6 actually needs.

---

## 9. Scope

TOY. Nothing here is a statement about HQC, A17, A5, any decoding-failure
rate, or any standardized parameter set. I hold no authority to change
research status and changed none. All committed artifacts under
`TASK-20260806-047535` were read only, not modified; my injection/
naturalness probe scripts live in this session's scratch space
(`/tmp/.../scratchpad/redteam_v2_injection.py`,
`/tmp/.../scratchpad/redteam_v2_naturalness.py`) and are not part of the
durable research record — the numeric results transcribed in §§1-2 are what
carries the finding forward.

---

## 10. Structured summary (per `agents/red-team.md`)

```yaml
red_team_report:
  id: RT-20260806-ae74c4
  task_id: TASK-20260806-ae74c4
  claim_under_review: >-
    The V2 planted-correlation control arm (TASK-20260806-047535, snapshot
    08d1c07a) closes the two gaps the Red Team found in the V1 arm
    (structurally blind, with probability exactly 1, to boundary/index-shift
    defects) by importing the real decode_blocks and using heterogeneous,
    decision-boundary-adjacent templates, and reports 17/17 cells MATCH at
    T=1,000,000.
  objections:
    - "The demonstrated boundary-shift flip sensitivity (design.md 3.5,
      comparison_report.md 4) is a deterministic (0% or 100%) property of one
      specifically hand-searched worst-case template pair, not a measured or
      estimated detection rate for realistic content. Independent
      measurement on Bernoulli(0.35) content -- this campaign's own stated
      proxy for realistic crypto-like noise density -- gives a natural
      single-position flip rate of ~8.8% overall and ~19.6% even restricted
      to content sharing the templates' margin, roughly 5-11x lower than the
      100% these two templates show."
    - "Because the construction uses exactly two fixed templates, it can
      structurally only ever express {0%, 100%} detection at the population
      level, never a calibrated intermediate rate -- so it cannot, even in
      principle, measure how often a real boundary-shift defect in the real
      heterogeneous PS-R3 pipeline would actually be expressed as a decode
      error."
    - "The arm's own SE (jackknife SE ~1e-6 to ~1e-3 at T=1e6) is
      artificially tiny because of its narrow 3-point S_t support ({17,18,19}
      vs. PS-R3's near-binomial spread over {0,...,56}); the thousands-of-SE
      detection margins observed here do not transfer to what the same
      absolute defect-induced shift would look like against PS-R3's actual,
      much larger, natural noise floor."
    - "The real (T)-sampler (CTRStream, fixed_weight_support, ring
      arithmetic) is still never run -- correctly disclosed by the executor,
      restated here as still-binding."
  required_controls:
    - "A V3 arm using a genuinely heterogeneous per-position, per-trial
      template ensemble (e.g. Bernoulli(0.35)-style content, filtered only on
      matching the planted label) so that an injected boundary-shift defect's
      detection RATE -- not merely its possibility -- can be measured and
      compared against this report's independently-measured ~8.8% natural
      flip-rate baseline."
  counterexample_or_mutation: >-
    Standalone reimplementation of the V2 arm's position-marking/template-
    lookup/decode_blocks machinery, injecting V1 (global read-one-early,
    all 56 blocks), V3 (last-block-only), an interior-position analogue
    (block 10), and the mirror "read-one-late" direction. Empirically
    (T=100,000/variant, real decode_blocks) and via independently-derived
    closed-form predictions that agree with the empirical run: every variant
    produces a per-block mismatch rate of 100% at every affected position
    (except read-one-late, 32.5%, matching the closed-form P(position was
    originally fail)) and a recovered log2_Ahat_k deviating by 90 to over
    13,000 jackknife SE from the closed-form planted value, using the real
    run's own T=1e6 jackknife SE as reference -- MISMATCH at every k for
    every variant. Detection is position-independent (V3 vs. an interior
    position give statistically indistinguishable magnitudes) but is an
    artifact of the specific hand-searched template pair: an independent
    measurement on Bernoulli(0.35) content (this campaign's own realistic-
    noise proxy) finds only an 8.8% natural single-position flip rate, not
    100%.
  baseline_comparison: >-
    Not an ECDLP asymptotic claim. Closest analogue: CTRL-POSHOM's own
    measured real-crypto-data marginal q-hat shifts under V1/V2/V3
    (-0.0243%, -0.0566%, +0.0015%, per TASK-20260806-250b29). This arm's own
    closed-form q-shift under a single-position V3-class defect is ~+1.98%,
    roughly two orders of magnitude larger than the real-data shift for the
    same nominal defect class -- consistent with the flip-rate gap found
    directly and reinforcing that this arm's demonstrated sensitivity is
    calibrated to worst-case hand-picked content, not to the real pipeline.
  heuristic_challenges: []
  cost_model_challenges: []
  reduction_and_scope_challenges:
    - "The T=1e6 reduction (from PS-R3/V1's 1e7) does not weaken any finding
      in this report -- every injected defect's deviation (90 to 13,000+ SE)
      would remain far outside a 3-SE band even at the sqrt(10)-narrower SE a
      T=1e7 run would have. This is because the tested defects are large
      relative to this arm's own noise floor, not because T=1e6 is adequate
      on its own merits; a defect an order of magnitude smaller (plausible
      under the ~8.8% natural flip-rate regime measured in section 2) could
      sit closer to the detectability boundary, where the T-cut's SE-scaling
      would matter more."
    - "The 'identical pipeline' (measure.py) reuse claim holds for the
      estimator/jackknife stage exactly as it did for V1 (same sha256,
      confirmed independently); the genuine new element -- decode_blocks
      itself being called directly and unmodified -- is confirmed and is a
      real fix, not merely claimed."
  proof_architecture_challenges: []
  narrowest_supported_statement: >-
    The V2 arm's artifacts are honest, reproducible, and budget-compliant
    (ADMIT), and its injected-defect sensitivity is genuine for the specific
    two-template construction it uses: unlike V1, at least one construction
    exists under which boundary/index-shift defects are detected with
    overwhelming margin, at every tested position, via both the self-check
    and the estimator-level MATCH/MISMATCH statistic. This retires my V1
    report's "detection is mathematically impossible, for any T" finding.
    It does NOT establish a calibrated detection rate for the real,
    heterogeneous PS-R3 pipeline: the demonstrated 100% flip rate is an
    artifact of hand-searching for a worst-case pair and is 5-11x higher
    than the ~8.8-19.6% natural flip rate this report independently measures
    on the campaign's own realistic-noise proxy. OPEN-6 is PARTIALLY CLOSED:
    the specific impossibility objection to this methodology is retired, but
    OPEN-6's underlying question (is PS-R3's real signal explainable by a
    subtle sampler bug) remains open pending a heterogeneous-ensemble arm
    that can measure a real detection rate, and pending any exercise of the
    actual (T)-sampler.
  next_concrete_action: >-
    Dispatch a V3 planted-arm task that replaces the two fixed templates
    with a genuinely heterogeneous per-position, per-trial content ensemble
    (e.g. Bernoulli(0.35)-style, filtered only on matching the planted
    decode label), so an injected boundary-shift defect's detection RATE --
    not merely its possibility -- can be measured and compared against this
    report's ~8.8% natural flip-rate baseline.
  artifact_paths:
    - coordination/goals/GOAL-HQC-001/batches/BATCH-558f5b/tasks/TASK-20260806-047535/design.md
    - coordination/goals/GOAL-HQC-001/batches/BATCH-558f5b/tasks/TASK-20260806-047535/planted_arm_v2.py
    - coordination/goals/GOAL-HQC-001/batches/BATCH-558f5b/tasks/TASK-20260806-047535/planted_results.json
    - coordination/goals/GOAL-HQC-001/batches/BATCH-558f5b/tasks/TASK-20260806-047535/comparison_report.md
    - coordination/goals/GOAL-HQC-001/batches/BATCH-558f5b/tasks/TASK-20260806-047535/run_manifest.yaml
    - coordination/goals/GOAL-HQC-001/batches/BATCH-4b8ad3/reviews/TASK-20260806-21c8da/red_team_report.md
    - coordination/goals/GOAL-HQC-001/batches/BATCH-6fddee/tasks/TASK-20260806-64b506/stage_a.py
    - ledger/evidence/EV-HQC-db1fd9.yaml
```

*Red-team record. I wrote only inside this directory. I hold no authority to
change status and changed none.*
