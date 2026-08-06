# Red-team report — matched-pair reanalysis + "double dilution" required-T derivation

**Task** `TASK-20260806-2cec38` (red team) · **Batch** `BATCH-fc30b5` · **Goal**
`GOAL-HQC-001`. Reviews the Coordinator-committed snapshot at commit
`2f034e0c` (`TASK-20260806-7bbbc8`) of
`coordination/goals/GOAL-HQC-001/batches/BATCH-fc30b5/tasks/TASK-20260806-e120e8/{design.md,matched_pair_reanalysis.py,reanalysis_results.json,reanalysis_report.md,run_manifest.yaml,stdout.log,stderr.log}`.
Also read `ledger/decisions/DEC-20260806-9a4551.yaml`, `ledger/evidence/EV-HQC-67a6ec.yaml`,
and — because verifying the derivation requires it — the actual estimator
source it claims to model, `measure.py`'s `log2_A_from_hists`/`comb_matrix`
and `stage_a.py`'s `mubar_from_hist`, read directly (both sha256-pinned in
the reviewed artifact and confirmed to match on disk). I am the same role
that wrote `TASK-20260806-92aecb`'s matched-pair probe and 10.7% measurement;
this session re-derives everything from source rather than trusting either
my own prior number or the executor's use of it.

**Bottom line up front.** The matched-pair mechanics (Sections 2-4 of the
reviewed report) are sound and I independently confirm them. The "double
dilution" **algebra** is internally correct given its stated assumptions —
I re-derived it from `log2_A_from_hists`'s actual formula and it matches
exactly. But the derivation rests on an **unquantified, unflagged-as-risky
approximation** (treating the perturbed block's failure as independent of
the other blocks' joint failure pattern) whose own error, by the campaign's
own prior finding of ~12-15% excess correlation in this exact system, is of
the **same order of magnitude as the entire "surviving" effect after
cancellation** — meaning the headline `4.33e8` / `~1,400x` figures are not
reliable to better than roughly an order of magnitude, on top of the
already-disclosed statistical unreliability of Δp itself. I also did the
math the executor's report explicitly declined to do (item 4 of my task
card): a **global (V1-class, all-56-block) injection removes the `k/n_e`
dilution factor entirely** and, under the same model and the same Δp
magnitude, requires **`T_req ≈ 1.4e5`** — *cheaper than the specification's
own undefected `T_req=3.09e5`*, not 1,400x more expensive. That number
carries the identical caveats as the 4.33e8 figure (same 1/Δp² sensitivity,
same unquantified-approximation risk, and V1's own per-block Δp has never
been measured), but it flips the campaign-level implication: this finding
argues *for* running the V1 positive-control pilot next, not for treating
real-sampler injection as dead at this injection point.

---

## 1. Independent re-derivation of the "double dilution" formula

### 1.1 What the estimator actually computes, from source

`measure.py::log2_A_from_hists` (sha256 `a4fd1ecb...f5dc8`, pin verified) and
`stage_a.py::mubar_from_hist` (sha256 `06a0a618...681405`, pin verified)
define, for `T` trials and per-trial block-failure count `S ∈ [0, n_e]`:

```
mu_k  = mubar_from_hist  = (1/T) * sum_s H_s * C(s,k) / C(n_e,k)   = E[C(S,k)] / C(n_e,k)
q     = ssum/(T*n_e)                                                = E[S] / n_e
log2_A_k = log2(mu_k) - k * log2(q)
```

`mu_k` is a pure function of the **histogram of `S`** — it never sees which
*specific* blocks failed, only how many. This matters directly below.

### 1.2 Re-deriving `Delta(mu_k)` from a single-block marginal perturbation

Split the `C(n_e,k)` size-`k` subsets by whether they contain block `n_e-1`
(fraction `k/n_e`) or not (fraction `1-k/n_e`). For a subset `A` containing
block `n_e-1`, the **exact** identity (conditional-probability chain rule,
no approximation yet) is:

```
P(all of A fail) = P(F_{n_e-1}=1) * P(all of A\{n_e-1} fail | F_{n_e-1}=1)
                  = p_{n_e-1} * P(other k-1 fail | F_{n_e-1}=1)
```

The design's model then substitutes the **conditional** probability with the
**unconditional** restricted moment: `P(other k-1 fail | F_{n_e-1}=1) ≈
mubar_{k-1}^{other}` (the k-1 subset average restricted to the other n_e-1
blocks) — this is the model's stated "approximate independence" assumption.
The code then further substitutes the **full-population** `mubar_{k-1}`
(computed by `sa.mubar_from_hist` over *all* n_e blocks) in place of the
**restricted** `mubar_{k-1}^{other}` (over the *other* n_e-1 blocks only).
With those two substitutions, holding the other-block moments and `q`'s
dependence on only block n_e-1 fixed:

```
Delta(mu_k)      ~= (k/n_e) * Δp * mubar_{k-1}
Delta(log2 mu_k) ~= Delta(mu_k) / (mu_k * ln2)
Delta(q)          = Δp / n_e                      [EXACT for a single-block perturbation]
Delta(log2_A_k)  ~= (k/n_e) * (Δp/ln2) * [ mubar_{k-1}/mu_k - 1/q_hat ]
```

**This is algebraically identical to the formula reported in the task
background and in `reanalysis_results.json`.** I confirmed it two ways: (a)
symbolically, as above, from `log2_A_from_hists`'s actual definition, not
from the executor's prose; (b) numerically, by recomputing every term from
`reanalysis_results.json`'s own stored `mubar_k_true=1.8435e-9`,
`mubar_km1_true=6.5444e-9`, `q_hat=0.31941`, `Δp=0.0082` — I reproduce
`leading_term=0.0127490`, `q_shift_term=-0.0112436`, `total=0.0015053`, and
`T_req=4.329e8`, matching the reported `4.33e8` to 4 significant figures.
**The arithmetic is not the problem.**

### 1.3 The problem: the independence approximation is *already falsified* by this system's own baseline data

Here is the sharp objection, not just "it's an approximation, be careful":

Apply the model's own two substitutions (independence between block `n_e-1`
and the rest; `mubar_{k-1}^{other} ≈ mubar_{k-1}`) to the **baseline**
(undefected) system itself, where every block including `n_e-1` has the
*same* marginal rate `p = q` (the average). The same decomposition, applied
with `Δp=0`, forces:

```
mu_k = (k/n_e) * q * mubar_{k-1} + (1 - k/n_e) * mubar_k
     = q * mubar_{k-1}                     [after the (k/n_e) terms cancel]
```

i.e., the independence approximation, applied consistently, predicts
`mu_k = q * mu_{k-1}` for every `k` — which telescopes to `mu_k = q^k`, the
**pure-independence (i.i.d.-blocks) moment sequence**. But this campaign's
own committed baseline data, reused unmodified by this very task, shows the
opposite: at `k=17`, `mu_{16}/mu_{17} = 6.5444e-9/1.8435e-9 = 3.5502`, while
`1/q_hat = 1/0.31941 = 3.1309` — a **13.4% deviation**. That deviation *is*
"excess correlation" — the entire signal this estimator and this research
program exist to detect. Its nonzero value is direct, already-established
evidence (not a new measurement I am proposing) that block failures are
**not** independent of one another in this system: `P(other k-1 fail |
F_{n_e-1}=1)` is not equal to the unconditional `mubar_{k-1}` — under
positive clustering (the natural reading of "excess correlation" in a real
decoder), it should be systematically *larger* than the unconditional
average, because conditioning on one block failing should make the others
more likely to fail too, not equally likely.

**Consequence for the required-T number.** The two terms that "nearly
cancel" in Section 5.2 of the reviewed report (`leading=0.012749`,
`qterm=-0.011244`, `total=0.001505`, an ~88% cancellation) are each
individually about 8.5x larger than what survives. If the true conditional
probability exceeds the unconditional `mubar_{k-1}` by even the same ~12-13%
already visible in the marginal moments, the leading term alone moves by
roughly `0.13 * 0.012749 ≈ +0.00166` — a correction **larger than the
entire reported residual** (`0.001505`). This is not a rounding concern; it
means the specific number `total=0.001505` (and everything downstream of
it — `4.33e8`, `1,400x`, `216,500 core-seconds`) is not derived to better
than roughly a factor of 2-3 in either direction, and the most natural
reading of the sign (clustering → larger conditional-on-failure probability
→ larger true propagated effect than modeled) points toward the **true
required T being smaller than 4.33e8**, not larger. I did not have access to
per-block trial data (only the `S`-histogram is retained in the JSON) to
pin this down exactly; Section 4 below names the cheap, no-new-sampling
control that would.

**What ADMIT does and does not cover here:** the algebra is not wrong and I
am not asserting the executor made an arithmetic error. The objection is
that "this is a genuine structural property of the estimator, not a
modeling artifact" (Section 5.2 of the reviewed report) is **asserted, not
established** — and the campaign's own prior evidence argues the opposite
direction from what that sentence implies.

### 1.4 An unverifiable corroboration claim

`reanalysis_report.md` Section 5.2 states the near-cancellation was
"verified by an independent closed-form recomputation that reproduces the
code's output to machine precision (documented in this task's own working
notes)." **No such artifact exists.** The task directory contains exactly
`design.md`, `matched_pair_reanalysis.py`, `reanalysis_results.json`,
`reanalysis_report.md`, `run_manifest.yaml`, `stdout.log`, `stderr.log` — no
working-notes file, and none is listed in `run_manifest.yaml`'s declared
artifacts. This is a claim of independent verification that cannot actually
be independently checked by a reviewer; it should either have been
committed as an artifact or not asserted as corroboration.

---

## 2. Is the 10.7% flip rate the right input? — Yes, correctly *not* used directly, but re-examine the marginal-shift-only model

The executor's report already gets the first-order issue right: it uses
`Δp` (the net marginal shift), not the raw 10.7% flip rate, as the dilution
input, explicitly labeling the raw-flip-rate version as a hypothetical
upper bound. That is the correct call — flips in both directions partially
cancel in the mean, and the estimator's leading behavior depends on the
mean shift, not the flip probability. I confirm this is the right
translation *for a model that only tracks each block's marginal probability*.

But the marginal-shift-only framing is itself a modeling choice, and it is
the same choice discussed in Section 1: a defect that changes `bits`-level
decode timing (V3's "read one bit-window early") could plausibly correlate
the block-`n_e-1` flip event with the SAME trial's other-block failure
pattern (e.g., flips concentrated in trials that are already noisy/failing
more broadly, or the opposite — flips concentrated in trials the decoder
would have succeeded on anyway). If flips are NOT independent of the other
blocks' joint state, the correct object is not `Δp` alone but a shift in the
**joint** distribution of (block `n_e-1`, other blocks), which the
marginal-only model cannot see. This is testable directly from data already
generated by this task (Section 4, control 1) — split the already-captured
`F_true`/`F_def` arrays by whether block `n_e-1` failed, and check whether
the other-block failure distribution differs between the two subsets. This
was not done, and is the natural companion check to the 4.33e8 figure's
own already-disclosed Δp-significance caveat.

---

## 3. Is 4.33e8 a meaningful number given Δp itself is not significant?

The executor's own analysis (Section 5.1 of the reviewed report,
`delta_p_reliability`) already states this correctly and is the strongest
part of the deliverable: none of the four independent `Δp` point estimates
(`+0.0082`, `+0.0026`, `-0.0022`, `+0.0002`) clears `|z|>=2` against a null
of zero, despite the local flip rate itself being enormously significant in
every sample (z~24-35). I recompute the McNemar-style SE independently and
confirm this: `SE(Δp_hat) = sqrt(flip_rate/T)`, giving `z ≈ 1.7` for the Red
Team's own shard (`0.0082/sqrt(0.1066/5000) = 0.0082/0.004618 ≈ 1.78`), and
smaller `|z|` for the others. **My own assessment, stated plainly:**

`4.33e8` is not a precise required-T. It is `T_req` *conditional on the
point estimate `Δp=0.0082` being the true value* — under `T_req ∝ 1/Δp²`
scaling, a Δp anywhere in a plausible confidence range (which, at `z<2`,
plausibly includes both `Δp=0` — required T undefined/infinite — and values
2-3x larger or of opposite sign) moves the required-T estimate by a factor
of 4-9x or renders it undefined. Combined with the Section 1 modeling
uncertainty (also good for a factor of several), **the honest statement is
an order-of-magnitude one: something in roughly the `10^7`-`10^9` range for
this specific (last-block, V3) injection point, not "`4.33e8`."** The
report's own Section 5.4 table (three effect-size inputs spanning
`2.56e6` to `7.28e11`) already demonstrates this range is enormous and the
report is honest about it — but the framing that reached me for this review
("If this 4.33e8 figure is correct... astronomically infeasible at any
budget this campaign has... roughly 216,500 core-seconds... two orders of
magnitude beyond the entire remaining campaign budget") is **not a claim
made anywhere in the reviewed artifacts** — I grepped `reanalysis_report.md`
and `reanalysis_results.json` for this framing and it does not appear
there. That framing over-precisions a number the executor's own report
already correctly hedges, and (per Section 4 below) is also wrong as a
general statement about "real-sampler defect injection" — it is at most a
statement about this one injection point.

---

## 4. Required-T for a global (V1-class, all-56-block) injection — computed independently, not in the reviewed artifact

Item 4 of my task card asks me to do this arithmetic myself; the executor's
report explicitly declined ("nothing here generalizes to V1's global
shift"). Using the *same* model (Section 1.2) and the *same* `Δp=0.0082`
magnitude, applied to **all `n_e=56` blocks simultaneously** instead of one:

- `Delta(mu_k)_global = n_e * (k/n_e) * Δp * mubar_{k-1} = k * Δp * mubar_{k-1}`
  (linear superposition of `n_e` identical single-block contributions — a
  first-order/small-Δp argument, subject to the same independence caveat as
  Section 1, which if anything biases this *upward*, i.e. makes the true
  effect larger still).
- `Delta(q)_global = Δp` (all `n_e` blocks shift by `Δp`, so the average
  shifts by the full `Δp`, not `Δp/n_e`).
- `Delta(log2_A_k)_global = k * (Δp/ln2) * [mubar_{k-1}/mu_k - 1/q_hat]`
  — **exactly `n_e = 56` times the single-block effect**, because the
  `k/n_e` dilution factor is removed entirely while the bracket term
  (baseline excess-correlation) is unchanged (it is a property of the true
  arm, not of how many blocks are perturbed).

I verified this numerically from the reviewed artifact's own stored
`mubar_k_true`, `mubar_km1_true`, `q_hat`, and `se_paired_at_T_ref_10000`
values (script run in scratch space, no repository files touched, no new
sampling — pure arithmetic on already-committed numbers):

```
single-block (V3, k/n_e=17/56 dilution): total=0.001505   T_req = 4.329e8
global (V1-class, all 56 blocks):        total=0.084299   T_req = 1.380e5
ratio (single/global effect):     56.00  (= n_e, exactly as predicted)
ratio (single/global T_req):    3136.00  (= n_e^2, exactly as predicted)
```

`T_req_global ≈ 1.38e5` is **≈0.45x the specification's own undefected
`T_req=3.09e5`** — cheaper, not 1,400x more expensive — and at ~2,000 t/cs
that is on the order of a few dozen core-seconds, trivially inside every
budget this campaign has used for a pilot so far.

**Caveats on this number, stated as plainly as the executor stated theirs:**

1. It carries the *identical* Δp-reliability caveat as Section 3 — `Δp` for
   a global mechanism has never been measured on the real sampler, and this
   projection assumes it would be of the same order (`~0.008`) as the
   unreliable V3 measurement, which is itself a different defect mechanism
   at a structurally different injection point (per-block shift, not
   last-block-only). This is an assumption, not a measurement.
2. It carries the identical Section 1 modeling-approximation caveat
   (linear superposition across blocks assumes the same independence
   approximation already shown to be in tension with this system's own
   baseline excess-correlation).
3. It is **not** a claim that V1 *will* show a detectable effect — only
   that, *if* it does at a comparable per-block magnitude, the trial count
   to see it is cheap. This is exactly what a positive-control pilot is for:
   to measure V1's own `Δp` rather than assume it.

**What this changes about the campaign-level reading:** the framing that
reached me treats `4.33e8` as evidence that "real-sampler defect injection
at this specific injection point is astronomically infeasible at any budget
this campaign has" — narrowly true of the *last-block-only* point under the
point-estimate `Δp`, but the same arithmetic, applied to the *other* named
injection strategy already sitting in `DEC-20260806-9a4551`'s own
`next_actions` item 3 (V1, global), shows the dilution problem is a
property of *where* the defect is injected, not of "real-sampler injection"
as a method. The correct scope-limited reading is: **the `decode_blocks`
last-block-only (V3) injection point is a poor test object for this
estimator specifically because it perturbs only the marginal rate of one
block out of 56, and this estimator is constructed (via the `-k log2(q)`
term) to subtract out exactly that kind of purely-marginal shift** — not
that defect injection into the real sampler is dead.

---

## 5. Stress-testing the matched-pair statistics themselves (Sections 2-4 of the reviewed report)

I re-verified the arithmetic these depend on:

- `mu_17/mu_16` ratio, `q_hat`, `SE_paired=0.09662`, `T_req` computation —
  all reproduce from the stored intermediate values to the precision
  reported. No arithmetic defect found.
- The sanity check against my own prior probe (`TASK-20260806-92aecb`, shard
  `424242`) reproduces my own numbers essentially exactly (flip count exact,
  `k=17` diff exact to 4 significant figures) — this task's matched-pair
  implementation is genuinely the same method as mine, not a superficially
  similar approximation, confirmed against my own prior artifact rather
  than by trusting the executor's self-report of matching.
- The bit-identical check against `pilot_results.json`'s committed
  histograms (shards `5000`/`6000`) is a real, checkable, fail-closed gate,
  and its logic (regenerate via the same `_t_shard`/seed derivation,
  compare `S_histogram` bin-for-bin) is sound; I did not independently
  re-run it (no new compute authorized beyond arithmetic on already-stored
  numbers), but the check design itself has no gap I can find.
- **The `z_paired` never exceeding `0.632` across `k=2..26`** is consistent
  with genuine ambiguity (not a floor imposed by the design, since the
  matched-pair SE is demonstrably tighter than the pilot's own by the
  reported 1.76x-10.0x factor at every `k`) — I do not find evidence this
  is an artifact of an avoidably weak application of the matched-pair
  method a second time. It reproduces my own probe's qualitative
  power-ratio shape (tighter advantage at low `k`) on independent (the
  pilot's own) shards, which is the right kind of cross-check.
- One internal-consistency note, not decision-relevant: the "genuinely
  ambiguous" classification in `matched_pair_reanalysis.py`'s
  `ambiguity_resolution` block uses **this task's own** combined `Δp`
  (`0.0002`, giving `T_req=7.28e11`) as the threshold test input, not the
  Red Team's `Δp=0.0082` (`T_req=4.33e8`) that is emphasized as the
  headline elsewhere in the report. `design.md` Section 2.5 does not
  specify which of the two should govern the resolution criterion. Using
  "ours" happens to be the more conservative choice (harder to reach
  `resolved_null`), and it does not change the outcome here (neither
  clears the `T<=10,000` bar), but the pre-registration left this
  underspecified and a future task should not assume it is settled which
  input governs.

**I confirm the matched-pair reanalysis (Sections 2-4) genuinely resolves
the SE-floor question it was dispatched to answer** — it demonstrates,
directly and reproducibly, that the pilot's original between-shard design
was leaving real, measured power on the table, exactly as my prior probe
predicted. I do **not** confirm that the required-T derivation (Section 5)
supports a precise, decision-grade `4.33e8`/`1,400x` figure, for the
reasons in Sections 1 and 3.

---

## 6. ADMIT / DO-NOT-ADMIT verdict

**ADMIT** the artifact set (`design.md`, `matched_pair_reanalysis.py`,
`reanalysis_results.json`, `reanalysis_report.md`, `run_manifest.yaml`) as
an honest, reproducible, fail-closed, budget-disciplined record of what was
actually done:

- The matched-pair method is genuinely reused (not reinvented), verified
  against my own independently-reported numbers first, and correctly
  extended to the pilot's own shards and the full `k` range.
- No new sampling occurred; the bit-identical and sanity-check gates are
  real, fail-closed, and I find no gap in their construction.
- The Δp-reliability caveat (Section 5.1) is disclosed honestly and
  prominently, not buried — this is a genuinely good-faith, self-critical
  deliverable on that specific point.
- Scope discipline (toy claim tier, PS-R3-only, no campaign-level call) is
  respected throughout.

**What ADMIT does not mean here, stated as precisely as I can:**

- **DO NOT** treat `4.33e8` / `1,400x` as a precise, load-bearing number for
  a campaign-shaping decision. It is correctly *derived* from its stated
  model, but the model contains one unflagged approximation (Section 1)
  whose own error, by this campaign's own prior evidence, is comparable in
  size to the number it produces — on top of the already-disclosed
  statistical unreliability of the `Δp` input. The right level of trust is
  "order of magnitude, direction uncertain but plausibly an
  underestimate," not "4.33e8."
- **DO NOT** read this task's finding as evidence that real-sampler defect
  injection generally is infeasible. It is, at most, evidence that *this
  specific injection point* (last-block-only marginal shift) is a poor test
  object for *this specific estimator* (which is constructed to subtract
  out purely-marginal shifts) — a scope-limited finding, not a method-level
  one. Section 4's independent calculation shows the opposite conclusion
  holds for the untested V1/global injection point under the same model.
- **DO NOT** treat the "documented in this task's own working notes"
  corroboration claim (Section 5.2 of the reviewed report) as verified
  evidence — no such artifact was committed or is inspectable.

---

## 7. My independent recommendation

**Dispatch the positive-control pilot (item 3 of `DEC-20260806-9a4551`), and
make it specifically a V1-class (global, all-block) injection, not a
further reanalysis of V3.** Reasoning:

1. The matched-pair reanalysis (Sections 2-4) has done what it can do for
   free with the pilot's existing data — it tightened the SE and confirmed
   genuine ambiguity remains at `k=17` for the V3 injection point. There is
   no further free diagnostic left to run against this specific dataset;
   the next unit of information requires either new sampling or a different
   injection point.
2. Section 4's arithmetic — using the executor's own validated model, just
   extended to the case the executor declined to compute — shows a global
   injection is not merely "less diluted" in a qualitative sense (as my own
   prior report already argued) but specifically **affordable at a trial
   count below the specification's own undefected `T_req`**, assuming a
   comparable per-block `Δp`. This is the single cheapest experiment that
   would discriminate between "the propagated effect is genuinely near
   zero for marginal-only shifts in this estimator" and "the detection
   pipeline can produce a fired cell at all" — the same missing positive
   control I named in `TASK-20260806-92aecb`, now with a concrete, cheap
   target trial count rather than a qualitative argument.
3. Before or alongside that pilot, run the **two cheap, no-new-sampling
   controls this review identifies**, since both bear directly on how much
   the V1 pilot's own eventual result should be trusted and roughly how
   large to size it:
   - **Conditional-independence check (Section 1/2):** using the already-
     regenerated `F_true`/`F_def` arrays from this very task (in-memory
     only in the committed run, but trivially re-derivable from the same
     shards/seeds with no new sampling), compute `P(other 16 blocks fail |
     F_{n_e-1}=1)` empirically and compare it to the unconditional
     `mubar_16` used in the model. If they differ by more than a few
     percent, the independence approximation is directly falsified on this
     system's own data, and the required-T formula needs the exact
     (not approximated) restricted moment `mubar_{k-1}^{other}` before its
     output is trusted to better than order-of-magnitude.
   - **SE-scaling check (Section 5.3 of the reviewed report's own caveat):**
     resample the already-collected 10,000 matched pairs at a few smaller
     `T` (e.g. 2,500 / 5,000) and confirm `SE(T) ∝ 1/sqrt(T)` holds within
     the observed range before trusting the 4-5-order-of-magnitude
     extrapolation implicit in any `T_req` figure derived from `T_ref=10,000`.
4. **Do not, on the strength of this batch alone, treat the real-sampler
   defect-injection line of work as settled or deprioritized.** The
   evidence assembled across this batch and its predecessor is consistent
   with "the campaign picked, for good and disclosed reasons (stringency,
   mechanical ease), an injection point this specific estimator is
   structurally least sensitive to" — which argues for testing a different
   point next, not for concluding the whole approach is dead. A closure
   claim here would fail `docs/inventor-protocol.md` §4's standard: it would
   have a named obstruction (the `k/n_e` and marginal-invariance dilution)
   but no argument that the obstruction generalizes beyond this one
   injection point, and it would ignore the forward guidance (V1) that
   `DEC-20260806-9a4551` already named and that Section 4 now shows is
   cheap to test.

---

## 8. Budget

Reading: the reviewed task's five artifacts plus its two upstream inputs
(`DEC-20260806-9a4551.yaml`, `EV-HQC-67a6ec.yaml`) and, to verify the
formula against source, the actual `measure.py`/`stage_a.py` definitions it
claims to implement. Compute: one short Python arithmetic script in scratch
space (no repository files touched, no new sampling, operates only on
numbers already stored in the reviewed `reanalysis_results.json`), a few
seconds. **No budget overrun** — total time for this review is a small
fraction of the 1,800-second authorization.

---

## 9. Structured summary (per `agents/red-team.md`)

```yaml
red_team_report:
  id: RT-20260806-2cec38
  task_id: TASK-20260806-2cec38
  claim_under_review: >-
    reanalysis_report.md (TASK-20260806-e120e8, snapshot 2f034e0c) reports
    (1) a matched-pair reanalysis of the pilot's own data showing continued
    genuine ambiguity at k=17 (z_paired=+0.534, never exceeding |0.632|
    across k=2..26), and (2) a "double dilution" structural derivation
    giving a required T of ~4.33e8 at k=17 for detecting the V3 last-block
    defect's own measured 10.7% local flip rate propagated to log2_Ahat_17,
    ~1,400x the specification's undefected T_req=3.09e5.
  objections:
    - "The dilution formula's algebra is correct given its assumptions (I
      re-derived it independently from log2_A_from_hists's actual source
      definition and it matches to 4 significant figures), but it depends
      on an unflagged independence approximation between the perturbed
      block and the other n_e-1 blocks. Applying that same approximation
      to the baseline (undefected) system predicts mu_k=q^k exactly for
      all k -- which this campaign's own already-committed baseline data
      directly contradicts (mu_16/mu_17=3.550 vs 1/q_hat=3.131, a 13.4%
      deviation -- the 'excess correlation' this estimator exists to
      detect). This means the approximation error is of the same order as
      the entire reported residual effect (leading and q-shift terms are
      each ~8.5x the reported total, i.e. an ~88% cancellation), so the
      headline 4.33e8/1,400x figures are not reliable to better than
      roughly an order of magnitude, and the most natural sign of the bias
      (positive block correlation) points toward the true required-T being
      SMALLER than reported, not larger."
    - "Section 5.2's claim that the near-cancellation was 'verified by an
      independent closed-form recomputation... documented in this task's
      own working notes' cites an artifact that does not exist in the
      committed task directory and is not listed in run_manifest.yaml --
      an unverifiable corroboration claim."
    - "The task's own required-T derivation explicitly declined to compute
      the required T for a global (V1-class, all-56-block) injection,
      despite DEC-20260806-9a4551 item 3 already naming V1 as the intended
      positive-control candidate. Using the executor's own validated model,
      a global injection removes the k/n_e dilution factor entirely
      (T_req scales by exactly n_e^2=3136x smaller), giving T_req~1.38e5 --
      BELOW the specification's own undefected T_req=3.09e5 -- under the
      same Delta_p magnitude. This reverses the campaign-level implication
      the reviewed report's framing suggested."
    - "The framing that reached this review ('astronomically infeasible at
      any budget this campaign has,' '216,500 core-seconds,' 'two orders of
      magnitude beyond the entire remaining campaign budget') does not
      appear anywhere in reanalysis_report.md or reanalysis_results.json --
      it over-precisions a number the executor's own report already
      correctly hedges with a wide sensitivity table (2.56e6 to 7.28e11)."
  required_controls:
    - "Empirically test the independence approximation using data already
      generated by this task (no new sampling): from the regenerated
      F_true/F_def arrays, compute P(other 16 blocks fail | F_{n_e-1}=1)
      directly and compare to the unconditional mubar_16 the model
      substitutes for it. A deviation of more than a few percent directly
      falsifies the approximation on this system's own data and bounds how
      much the required-T figure should move."
    - "Resample the already-collected 10,000 matched pairs at smaller T
      (2,500 / 5,000) to empirically verify SE(T) ~ 1/sqrt(T) holds in the
      observed range before trusting a 4-5-order-of-magnitude extrapolation
      to T_req from T_ref=10,000 -- no new sampling required."
    - "Measure V1's own per-block Delta_p on the real sampler (the positive-
      control pilot already named in DEC-20260806-9a4551 item 3) rather
      than assuming it matches V3's unreliable point estimate -- this is
      the only way to convert Section 4's T_req~1.38e5 projection from a
      conditional arithmetic exercise into an actual measurement."
  counterexample_or_mutation: >-
    Applied the reviewed report's own dilution model, with no modification,
    to a global (all-56-block) rather than single-block perturbation of the
    same magnitude Delta_p=0.0082. The k/n_e dilution factor cancels
    entirely (effect scales by exactly n_e=56, required T by n_e^2=3136),
    giving T_req~1.38e5 -- cheaper than the specification's own undefected
    T_req=3.09e5, not 1,400x more expensive. This is the same model the
    executor used, extended to the case DEC-20260806-9a4551 already named
    as the next step and that the executor's own report explicitly declined
    to compute.
  baseline_comparison: >-
    Not an ECDLP/Pollard-rho/BSGS comparison -- this is an HQC decoding-
    correlation instrument-validation batch. The relevant comparison is the
    specification's own undefected-estimator T_req=3.09e5 (a different
    quantity, per the prior batch's still-live objection) against the
    derived required-T for detecting the injected defect's propagated
    effect: ~4.33e8 (order-of-magnitude uncertain, plausibly an
    overestimate) for the tested V3/last-block point, versus ~1.38e5
    (untested, same caveats) for the V1/global point this batch did not try.
  heuristic_challenges:
    - "The dilution model's core simplifying assumption -- that the
      perturbed block's failure is approximately independent of the other
      blocks' joint failure pattern -- is not numbered or given a random-
      model justification in design.md; it is stated once as 'an
      approximation not re-derived here.' This review shows the assumption
      is in direct tension with the campaign's own prior finding that this
      system exhibits excess (non-independent) block correlation, which is
      the entire object of study."
    - "The SE(T) = SE_ref * sqrt(T_ref/T) scaling assumption used to
      extrapolate ~4-5 orders of magnitude from T_ref=10,000 is disclosed
      as an assumption in design.md Section 3.3 but never independently
      checked, even though a cheap in-range check (resampling the existing
      10,000 pairs at smaller T) was available at zero additional sampling
      cost."
  cost_model_challenges:
    - "The headline 4.33e8/216,500-core-second/1,400x figures are treated
      (in the framing that reached this review, though not in the
      executor's own report) as precise enough to license a campaign-
      shaping conclusion. Given the compounding of (a) Delta_p itself not
      being statistically distinguishable from zero (|z|<2 on all four
      point estimates) and (b) an unquantified independence-approximation
      error of comparable size to the reported effect, the correct
      precision claim is order-of-magnitude, not a specific figure -- and
      total required cost should be read as per-attempt-cost-at-T_req times
      an uncertainty band spanning roughly one to two orders of magnitude,
      not a point estimate."
    - "The n_e=56 amplification identified in this review (Section 4) was
      available from the same model at zero additional compute -- it is
      pure arithmetic on already-derived quantities -- and changes the
      campaign-relevant cost comparison for the untested V1 injection point
      from '1,400x too expensive' to 'cheaper than the existing undefected
      T_req,' conditional on Delta_p transferring at comparable magnitude."
  reduction_and_scope_challenges:
    - "The reviewed report's finding is valid and useful but scoped to
      exactly one injection point (decode_blocks/V3, last-block-only) and
      one estimator (log2_Ahat_k, which by construction subtracts out
      purely-marginal-rate shifts via its -k*log2(q) term). It should not
      be read, in the next Coordinator decision, as a finding about
      real-sampler defect injection generally -- the same model predicts
      the opposite conclusion for a global (V1-class) injection point that
      remains untested."
    - "'Astronomically infeasible at any budget this campaign has' (as
      relayed in this task's framing, not as stated by the executor)
      overclaims scope: it is not established for the V1 injection point,
      and even for V3 it is a budget-relative, not an absolute-
      infeasibility, statement -- 216,500 core-seconds (~60 core-hours) is
      not physically astronomical, only beyond this campaign's toy-scale
      allocation."
  proof_architecture_challenges: []
  narrowest_supported_statement: >-
    The matched-pair reanalysis of the pilot's own data (Sections 2-4 of
    the reviewed report) is sound, genuinely reuses the Red Team's method,
    and correctly establishes that the SE-floor question is resolved while
    genuine ambiguity about the propagated effect remains at k=17 for the
    V3/last-block injection point. The "double dilution" required-T
    derivation is algebraically correct given its stated model, but that
    model rests on an independence approximation this system's own prior
    evidence already argues against, at a magnitude comparable to the
    entire reported residual effect -- so 4.33e8/1,400x should be read as
    an order-of-magnitude, plausibly-conservative (i.e. possibly too large)
    figure specific to this one injection point and this one estimator, not
    as a precise number and not as evidence against real-sampler defect
    injection as a method. The same model, applied (as this review does,
    independently of the executor) to a global/V1-class injection at the
    same Delta_p magnitude, gives T_req~1.38e5 -- below the specification's
    own undefected T_req -- which is the opposite campaign-level
    implication from the one the reviewed report's framing suggested.
  next_concrete_action: >-
    Dispatch the positive-control pilot already named in DEC-20260806-9a4551
    item 3, specifically as a V1-class (global, all-56-block) real-sampler
    injection rather than a further V3 reanalysis, sized using this
    review's T_req~1.38e5 projection as a starting order of magnitude (not
    a precise target). Before or alongside it, run the two cheap,
    no-new-sampling controls named in Section 4/required_controls above
    (empirical conditional-vs-unconditional mubar_{k-1} check; SE-scaling
    in-range check) so the eventual V1 result's own required-T can be
    trusted to better than an order of magnitude, unlike this batch's V3
    figure.
  artifact_paths:
    - coordination/goals/GOAL-HQC-001/batches/BATCH-fc30b5/tasks/TASK-20260806-e120e8/design.md
    - coordination/goals/GOAL-HQC-001/batches/BATCH-fc30b5/tasks/TASK-20260806-e120e8/matched_pair_reanalysis.py
    - coordination/goals/GOAL-HQC-001/batches/BATCH-fc30b5/tasks/TASK-20260806-e120e8/reanalysis_results.json
    - coordination/goals/GOAL-HQC-001/batches/BATCH-fc30b5/tasks/TASK-20260806-e120e8/reanalysis_report.md
    - coordination/goals/GOAL-HQC-001/batches/BATCH-fc30b5/tasks/TASK-20260806-e120e8/run_manifest.yaml
    - coordination/goals/GOAL-HQC-001/batches/BATCH-fc30b5/archives/TASK-20260806-7bbbc8/snapshot-receipt.json
    - ledger/decisions/DEC-20260806-9a4551.yaml
    - ledger/evidence/EV-HQC-67a6ec.yaml
    - coordination/goals/GOAL-HQC-001/batches/BATCH-2ecaa1/reviews/TASK-20260806-92aecb/red_team_report.md
    - coordination/goals/GOAL-HQC-001/batches/BATCH-6fddee/tasks/TASK-20260806-64b506/stage_a.py
    - coordination/goals/GOAL-HQC-001/batches/BATCH-0a65c0/tasks/TASK-20260806-cde749/measure.py
```

*Red-team record. I wrote only inside this directory. I hold no authority to
change status and changed none. This is an independent session's judgement:
I neither confirm the executor's framing nor re-adopt my own prior
(`TASK-20260806-92aecb`) 10.7% measurement without re-scrutinizing how it
was used here, which is what Sections 2-3 above do.*
