# Red-team report — planted-correlation control arm for OPEN-6 (TASK-20260806-e19f6c)

**Task** `TASK-20260806-21c8da` (red team) · **Batch** `BATCH-4b8ad3` · **Goal**
`GOAL-HQC-001` · **Reviews** `TASK-20260806-e19f6c`'s snapshot (commit
`8538964c`) · **Produced** 2026-08-06.

**Frozen artifacts verified before anything else.** `snapshot-receipt.json`
(`coordination/goals/GOAL-HQC-001/batches/BATCH-4b8ad3/archives/TASK-20260806-5a3d0e/`)
is reachable from `HEAD` (`git log --oneline`: `cc0fcf0b` merges `8538964c
research: TASK-20260806-5a3d0e snapshot of the planted-correlation control
arm`, parent `24393e4c`). I read `design.md`, `planted_arm.py`,
`planted_results.json`, `comparison_report.md`, `run_manifest.yaml` only as
frozen input under `coordination/goals/GOAL-HQC-001/batches/BATCH-4b8ad3/tasks/TASK-20260806-e19f6c/`
and modified nothing there. Independent session; I did not confer with the
Validator (`TASK-20260806-9f4b27`) and treated the executor's framing as a
claim to attack, not a conclusion to confirm.

---

## VERDICT

# **ADMIT the artifacts, subject to two binding corrections (§6). Independently: OPEN-6 REMAINS OPEN — my injection defeated the arm.**

Per this batch's own pre-declared rule (`TASK-20260806-b673f1`'s handoff
constraint: *"If either review returns DO-NOT-ADMIT, or the red team's
injection defeats the arm, OPEN-6 remains OPEN"*), the second clause fires. I
constructed a copy of the arm's block-partition/reduce machinery, injected the
exact V1/V2/V3 defect classes this campaign already named
(`idxmap_probe.py`, `BATCH-0a65c0/reviews/TASK-20260806-250b29`), and found
that **two of three (V1 off-by-one truncation, V3 last-block-window-read-
early) are undetectable by this arm with mathematical certainty, for any T** —
not merely under-powered. Only V2 (interleaved partition, a much cruder
scrambling) is caught. This is a materially stronger and more specific finding
than the "narrower support / homogeneous blocks" residuals `design.md` Section
3.2 itself already discloses, and it lands squarely on the defect class OPEN-6
exists to rule out.

---

## 1. Does the injection point exercise the code path OPEN-6 is worried about, or bypass it?

**It bypasses the actual code, and this is disclosed, but the disclosure
understates the consequence.**

`design.md` Section 3.2, item 1, states plainly: *"The cryptographic (T)-
sampler itself is not run at all. `stage_a.py` is never imported or executed
by this task."* Confirmed by inspection — `planted_arm.py` imports only
`measure.py` (sha256-pinned) and contains no reference to `stage_a`,
`CTRStream`, `fixed_weight_support`, `ring_mul_sparse/dense`, or a
Walsh–Hadamard transform. The arm's "block-partition / index-map" step
(`design.md` §3, `run_batch()`'s `flat = np.repeat(...); blk =
flat.reshape(...)`) is a **hand-written, from-scratch reimplementation**, not
the real `stage_a.decode_blocks`. `design.md` §3 step 4 itself says the reduce
step is "a genuine per-block reduction... (**not** the real WHT / RM decoder,
see Section 4)" — so even the substitute step is admitted, in the same
sentence, to be a different algorithm from the one that would actually run in
production.

So a MATCH here is, at best, evidence that *a same-day reimplementation of
"repeat-then-reshape-then-threshold" is internally consistent* — not evidence
about `stage_a.py`'s actual `decode_blocks`, which nobody ran. Design.md's own
"what this arm does NOT exercise" list (§3.2) already says this. My objection
is that the framing in `comparison_report.md` §5 ("exercises a genuine
flat-N-bit-vector to `(n_e, L)` reshape... the exact sufficient statistic
`measure.py`'s estimator consumes") reads, out of context, as validating "the
block-partition/index-map path," when what follows in §2 below shows the
*specific vulnerability* that path exists to catch is provably invisible to
this substitute construction regardless of which code implements it.

---

## 2. Injected-defect experiment: does a genuine defect survive undetected?

**Yes — two of three defect classes survive undetected, with probability
exactly 1 (not merely "usually"), independent of T.**

I built a standalone copy of the arm's generation/decode logic (not an edit of
the committed `planted_arm.py` — a fresh reimplementation mirroring `design.md`
§3 and `planted_arm.py`'s `run_batch()`) and injected the same three defect
classes `idxmap_probe.py` used against `stage_a.py`'s real index maps in
`BATCH-0a65c0` (verified faithful translations, index-formula for index-
formula, against `idxmap_probe.py`'s `instrument_map()`):

- **V1 — off-by-one truncation.** A global 1-position circular shift of the
  flat N-bit array before the (correct) `L`-boundary reshape — the decode-side
  analogue of `idxmap_probe.py`'s `trunc = (i+1) % n`.
- **V2 — interleaved partition.** Block `j` reads flat positions
  `{j, j+n_e, j+2·n_e, ...}` (stride-`n_e` gather) instead of the contiguous
  window `{j·L, ..., j·L+L-1}` — the decode-side analogue of
  `idxmap_probe.py`'s `trunc[j + t·n_e]`. Verified index-for-index equivalent
  by construction (`reshape(L, n_e).transpose` = stride-`n_e` gather).
  Encoding is left correct (contiguous), so this is a genuine encode/decode
  mismatch, not the tautological round-trip the committed arm's self-check
  performs.
- **V3 — last-block window read one index early.** Only block `n_e-1`'s
  window is shifted left by one position — the decode-side analogue of
  `idxmap_probe.py`'s `j==n_e-1` special case.

### Result (Phase A, mismatch-rate probe, T = 2,000,000 trials, `n_e=56`, `L=128`):

| variant | self-check (`F==block_fail`) would abort? | mismatch rate |
|---|---|---|
| V0 baseline | No | 0.000000e+00 |
| **V1 off-by-one (all blocks)** | **No** | **0.000000e+00** |
| V2 interleaved | **Yes** (batch 0) | 3.214312e-01 |
| **V3 last-block-early** | **No** | **0.000000e+00** |

### Confirmation this is exact, not statistical (`verify_bitexact.py`, T = 500,000 trials):

```
V0 == block_fail exactly: True
V1 == block_fail exactly: True
V3 == block_fail exactly: True
V1 == V0 exactly: True
V3 == V0 exactly: True
S1 == S0 for all trials: True     (max |S1-S0| = 0)
S3 == S0 for all trials: True     (max |S3-S0| = 0)
```

**Why this is a certainty, not luck.** Because the planted construction makes
every block internally homogeneous (all-0 or all-1, `L=128`), a single
boundary bit borrowed from a neighboring block under V1, or a single-index
shift under V3, can move a block's bit-sum by at most 1 relative to its true
value of `0` or `128`. The majority threshold (`sum > L/2 = 64`) has a margin
of 64 votes on either side of that boundary. **No single-bit perturbation can
ever cross it.** This holds for every trial, at every `T`, including
`T → ∞` — it is not that the arm is under-powered at `T=1e7`; more trials
provide *zero* additional power against this defect class. `design.md` §3.2
item 3 gestures at "not exercised" for heterogeneity-dependent defects; the
correct, sharper statement is that for **boundary/index-shift defects under
majority-threshold reduction over homogeneous blocks, detection probability
is analytically 0**, deterministically.

### Phase B: does this propagate to a MATCH/MISMATCH verdict on `log2_A_k`?

At T = 2,000,000, 40 jackknife batches (reduced from PS-R3's T=1e7/200 batches
purely for probe speed — the reduced T makes several high-k cells noisier and
occasionally MISMATCH by chance for *all three* variants alike; that is an
artifact of my smaller probe, not a finding, and is symmetric across
variants):

```
V0-baseline:              12/17 cells MATCH
V1-offbyone-all-blocks:   12/17 cells MATCH   (bit-identical recovered values to V0)
V3-lastblock-early:       12/17 cells MATCH   (bit-identical recovered values to V0)
```

Every reported `log2_Ahat_k` and every jackknife SE is byte-identical between
V0 and V1, and between V0 and V3, at every k = 2..18. **A defect survives
completely undetected by both the arm's own fail-closed self-check and by the
final MATCH/MISMATCH comparison against the planted value.** This is exactly
the finding the dispatch card calls "the single most valuable finding this
task can return."

**V2 is the one defect this arm does catch**, and it is caught for a coarse
reason unrelated to the concern OPEN-6 raises: a stride-`n_e` (56) gather
across an `L`-length (128) window mixes bits from roughly 55 different true
blocks into one reconstructed block, driving each reconstructed block toward
the population mean (`q ≈ 0.32`) rather than a landslide 0/128 — a near-total
data scramble, not a subtle off-by-one. Catching V2 is not evidence the arm
would catch the more realistic single-index bug class (the class
`CTRL-IDXMAP`'s own construction, and its `RULE-2` defect, were about).

**Cross-reference to the standing record.** `EV-HQC-b71230.yaml`'s own
`unresolved_confounds` already states: *"CTRL-POSHOM is structurally blind to
the shift-equivariant defect class (V1, V2, V3 confirmed blind by injection on
two independent seeds)... V2 in particular is exactly invisible to it AND
changes the estimand."* On the real (heterogeneous-bit) `stage_a.py` data, V1/
V2/V3 were all blind to the *pairwise* control (`CTRL-POSHOM`) but did
perturb the *marginal* `q̂` slightly (−0.0243%, −0.0566%, +0.0015%
respectively, per `TASK-20260806-250b29`'s §3.2). My finding is **stronger**
for this new arm: because its planted blocks are homogeneous rather than
bit-heterogeneous, the marginal statistic this arm actually tests (`S_t`,
hence `log2_Ahat_k`) shows **exactly zero** perturbation under V1/V3, not just
a small one. The homogeneous-block construction doesn't merely fail to
improve on the campaign's known blind spot — for this specific defect class it
removes even the small residual signal the real crypto data would carry.

---

## 3. Is the "identical pipeline" claim honest?

**Mostly yes, with one nuance the record already discloses adequately.**
`comb_matrix` and `log2_A_from_hists` (`measure.py` lines 213-222, 225-246) are
imported unmodified via `importlib` and called directly (`measure.comb_matrix`,
`measure.log2_A_from_hists`), not copied — I read both functions directly from
`measure.py` and they match `comparison_report.md`'s citations exactly,
including the load-bearing orientation comment on `comb_matrix` ("ORIENTATION
IS LOAD-BEARING... matches the generating procedure's own `cmatrix`"). The
`point`/`loo`/`jmean`/`jse` block (`measure.py` lines 734-739) is reproduced
formula-for-formula in `planted_arm.py`. One nuance: `measure.py`'s own
`bh` construction (line 730-733) slices a single `S_all` array via
`np.linspace` batch boundaries; `planted_arm.py`'s `bh` is instead accumulated
per-batch during generation (each of the 200 batches gets its own RNG stream
and histogram directly, never assembled from a monolithic `S_all`). This is a
different code path for producing the *same* object shape, not a byte-for-byte
reuse of lines 730-733 — `comparison_report.md`'s own table already flags this
("the only substitution is that `bh`/`hist` here come from this arm's own
generator rather than from `measure.py`'s `S_all`"), so this is disclosed
honestly rather than hidden; I record it here only because the table's header
row ("copied verbatim") could be misread as covering `bh`'s construction too.

Fail-closed integrity check: verified structurally sound (reads
`MEASURE_PY_EXPECTED_SHA256` against a freshly computed hash and raises
`SystemExit` on mismatch) and the executor's dry-run demonstration
(constant corrupted to zeros, script aborted, reverted) is a legitimate
verification of the *sha256* gate. I did not independently re-run that
dry-run (out of scope for this task's budget; it is a simple, low-risk
mechanical check and I found no reason to doubt the executor's transcript).

---

## 4. Is the planted `log2_A_k(k)` genuinely closed-form, or does it depend on data?

**Genuinely closed-form. I independently re-derived it before consulting
`planted_results.json`'s numbers and it matches to the precision I computed.**
I wrote my own `planted_log2_A()` from `design.md` Section 2's prose
construction (`M_t ~ Uniform{17,18,19}`, uniform random `M_t`-subset, `S_t =
M_t` exactly) using `fractions.Fraction` arithmetic, independent of
`planted_arm.py`'s code. My values for k=2 (`-0.05332724...`) through k=9
(printed in my probe output) match `design.md`'s Section 2.1 table digit for
digit. The derivation genuinely predates any data: `S_t = M_t` is a
tautological consequence of "every subset of size `M_t` sums to `M_t`," so
`mu_bar_k` and `q` are population moments of a fully specified discrete
mixture law, not fitted quantities. I found no dependence on anything only
knowable after sampling.

---

## 5. Baseline and cost-model notes (`agents/red-team.md` contract)

**Baseline comparison.** This is not a Pollard-rho/BSGS-class claim (HQC
decoder-failure instrument, not ECDLP), so the standard baseline-comparison
requirement does not apply in its literal form; the closest analogue —
"compare against the existing instrument-trust control, `CTRL-POSHOM`" — is
already covered in §2 above: the new arm adds no discriminating power over
`CTRL-POSHOM` for the V1/V3 defect class and is *strictly worse* than
`CTRL-POSHOM` in one respect (it never runs against heterogeneous, i.e.
realistic, per-bit data at all, so unlike `CTRL-POSHOM`'s measured small but
nonzero `q̂` shifts under V1/V2/V3, this arm shows literally zero shift).

**Cost-model / heuristic challenges.** Not applicable in the
exponent-first/Wesolowski-profile sense (`docs/target-result-profile.md`) —
this is a toy-tier instrument check on an HQC-shaped decoder statistic, not an
asymptotic ECDLP claim. No heuristic inventory, random-model transfer, or
o(1)-overhead analysis is owed here; noting this explicitly per the report
template rather than silently omitting it.

**Budget.** Authorized 1,800 wall-clock seconds. Measured: `redteam_
injection.py` (Phase A + Phase B, T=2e6 across 4 defect variants) ran ≈165
wall-seconds (`real 2m44.532s`, `user 1m31.6s`, `sys 1m13.1s` — background
execution, contended machine); `verify_bitexact.py` (T=500,000, exact-equality
check) ran a few seconds. Total measured wall-clock for this task's compute:
**≈170 seconds against the 1,800-second budget (≈9.4%). No overrun.** No
result was trimmed or subsampled to fit budget; the reduced T=2e6/40-batch
scale (vs. the committed arm's T=1e7/200) was a deliberate choice for a
falsification probe, not a budget-forced truncation, and it does not weaken
the headline finding (§2 shows the V1/V3 blindness is exact/deterministic, so
no amount of additional T would change the verdict).

---

## 6. Binding corrections (if the artifacts are admitted)

1. **State the injected-defect blindness explicitly, not just the general
   residual.** `design.md` §3.2 item 3 and `comparison_report.md` §5 should be
   amended (in the evidence record that cites this arm, not by editing the
   frozen artifacts) to say: *"Under this arm's homogeneous-block, majority-
   threshold construction, boundary/index-shift defects of the class this
   campaign already named V1 (off-by-one truncation) and V3 (last-block-
   window-read-early) are undetectable with probability exactly 1, for any T.
   Only gross data-scrambling defects (the V2 class) are caught. This arm
   therefore provides no discriminating evidence for or against the specific
   defect class OPEN-6's own precedent (`CTRL-IDXMAP`, `CTRL-POSHOM`) was
   built to detect."*
2. **Do not describe this arm, anywhere downstream, as having exercised
   "the block-partition / index-map path" without the qualifier that it is a
   from-scratch, majority-threshold reimplementation, not `stage_a.py`'s
   actual `decode_blocks`/Reed–Muller-WHT decoder** (§1 above). The
   distinction matters because the real decoder's sensitivity to boundary
   misalignment is unmeasured and unknown — it could plausibly be more or
   less sensitive than the majority-threshold substitute, and nothing here
   bounds it either way.

These are edits to how the result is *read*, not new measurement — matching
the form of the corrections `TASK-20260806-250b29` issued against `CTRL-
IDXMAP` in `BATCH-0a65c0`.

---

## 7. OPEN-6 disposition: **STILL OPEN**

Per this batch's own pre-declared rule, my injection defeating the arm settles
this independent of the ADMIT verdict. To be precise about scope: this arm
*would* provide some evidence against a hypothesis of the form "the real
sampler's block-partition path has a gross, near-total scrambling defect"
(the V2 class) — that narrow sub-hypothesis is weakly disfavored by a MATCH
here, for whatever an unrun `stage_a.py` proxy is worth. But OPEN-6's actual
concern, as stated in `EV-HQC-b71230.yaml` ("a subtly wrong sampler that would
reproduce this exact signature" — i.e., a *subtle* defect, not a gross one) is
untouched: the two subtle, realistic defect classes this campaign has
repeatedly named (off-by-one, last-block-early) are shown here to be
*provably, deterministically* invisible to this instrument, at any scale.
**No T, no replication, and no additional jackknife batches would change
this** — it is a structural property of the construction, not a power
limitation. The −244.1-to−32.4 SD PS-R3 departure (`EV-HQC-b71230`) therefore
still cannot be distinguished from a subtly-wrong sampler by any evidence this
campaign has produced to date.

---

## 8. Cheapest next concrete action

Build a V2 of the planted arm that closes the two gaps identified above
together, since fixing only one leaves the other's blindness intact:

1. **Invoke `stage_a.py`'s actual `decode_blocks` (the real WHT/Reed–Muller
   reduction), not a hand-rolled majority threshold** — import it read-only,
   sha256-pinned, exactly as `measure.py` is already reused.
2. **Construct the planted instance with heterogeneous, per-bit-valid content
   inside each block** (e.g., planted blocks realized as actual forced/valid
   Reed–Muller codewords with a controlled Hamming-distance-to-decision-
   boundary, chosen so the *joint* `S_t` law is still closed-form) rather than
   homogeneous all-0/all-1 blocks. Only with within-block heterogeneity near
   the real decoder's decision boundaries can a boundary-index defect have any
   chance of being expressed as a decode error, closed-form or not.

This is the cheapest control that would actually test what `CTRL-IDXMAP` and
`CTRL-POSHOM` were built to test, on a known-answer instance, through the real
decoder. Absent it, OPEN-6's off-by-one/last-block-early risk class remains
exactly as open as it was before this batch.

---

## 9. Scope

TOY. Nothing here is a statement about HQC, A17, A5, any decoding-failure
rate, or any standardized parameter set. I hold no authority to change
research status and changed none. All committed artifacts under
`TASK-20260806-e19f6c` were read only, not modified; the injected-defect probe
scripts (`redteam_injection.py`, `verify_bitexact.py`,
`verify_bitexact.py`'s companion output) live in this session's scratch space
and are not part of the durable research record — this report's transcribed
numeric results (§2) are what carries the finding forward; a future task that
wants the exact probe code should re-derive it from the index formulas cited
here and in `idxmap_probe.py` rather than treat scratch-space code as an
artifact.

---

## 10. Structured summary (per `agents/red-team.md`)

```yaml
red_team_report:
  id: RT-20260806-21c8da
  task_id: TASK-20260806-21c8da
  claim_under_review: >-
    The planted-correlation control arm (TASK-20260806-e19f6c, snapshot
    8538964c) closes OPEN-6 by showing the PS-R3 measurement pipeline
    recovers a known answer (17/17 cells MATCH) when run on an instance
    whose joint law is derivable in advance.
  objections:
    - The arm never imports or executes stage_a.py; its block-partition/reduce
      step is a from-scratch, hand-rolled majority-threshold reimplementation,
      not the real decode_blocks/WHT-Reed-Muller decoder (design.md 3.2.1;
      confirmed by inspection).
    - Injected boundary/index-shift defects (V1 off-by-one truncation, V3
      last-block-window-read-early -- the exact classes this campaign already
      named in BATCH-0a65c0's idxmap_probe.py) are undetected by both the
      arm's own fail-closed self-check and its final MATCH/MISMATCH verdict,
      with probability exactly 1, for any T -- a structural, not statistical,
      blind spot arising from majority-threshold reduction over homogeneous
      L=128-bit planted blocks.
    - Only the cruder V2 (interleaved partition, near-total data scramble) is
      caught, and catching it is not evidence the arm would catch the more
      realistic single-index bug class.
  required_controls:
    - "A V2 of the planted arm that (a) invokes stage_a.py's actual
      decode_blocks (real WHT/Reed-Muller reduction, sha256-pinned import,
      not a homemade majority threshold), and (b) constructs planted blocks
      with heterogeneous, decision-boundary-adjacent per-bit content rather
      than homogeneous all-0/all-1 blocks, so a boundary-index defect has any
      chance of manifesting as a decode error."
  counterexample_or_mutation: >-
    Standalone reimplementation of planted_arm.py's generate/decode logic with
    V1 (global 1-bit circular shift before reshape) and V3 (last block's
    window shifted left by one) injected on the decode side only (encode left
    correct). Verified over 500,000 trials x 56 blocks: recovered F is
    bit-identical to the uncorrupted baseline for both V1 and V3
    (max |S_variant - S_baseline| = 0); the block-partition self-check never
    fires; recovered log2_Ahat_k is bit-identical to baseline at every
    reported k. V2 (interleaved, stride-n_e gather) DOES fire the self-check
    (32.1% block mismatch rate, aborts at the first sub-chunk).
  baseline_comparison: >-
    Not an ECDLP asymptotic claim; closest analogue is CTRL-POSHOM
    (BATCH-0a65c0), which the standing evidence record (EV-HQC-b71230)
    already documents as blind to V1/V2/V3 on the real (heterogeneous-bit)
    sampler, while still showing small nonzero q-hat shifts under those
    defects. This arm's homogeneous-block construction removes even that
    small residual signal for V1/V3: the shift here is exactly zero, not
    merely small.
  heuristic_challenges: []
  cost_model_challenges: []
  reduction_and_scope_challenges:
    - "The 'identical pipeline' claim holds for the estimator/jackknife stage
      (measure.py's comb_matrix, log2_A_from_hists, and the point/loo/jmean/
      jse formulas, verified against measure.py lines 213-246 and 734-739) but
      not for the block-partition/index-map stage, which is a different
      algorithm (majority threshold vs. the real WHT/Reed-Muller decoder) on
      different data (homogeneous vs. heterogeneous per-bit content). This
      distinction is disclosed in design.md 3.2 but understated in
      comparison_report.md's summary framing."
  proof_architecture_challenges: []
  narrowest_supported_statement: >-
    The planted arm's artifacts are honest, reproducible, and budget-compliant
    (ADMIT), and its MATCH result is valid evidence only that (a) measure.py's
    estimator/jackknife code correctly recovers a known marginal S-histogram
    law from a correctly-generated histogram, and (b) this arm's own
    from-scratch generator/decoder round-trips correctly when uncorrupted or
    when corrupted by gross (V2-class) scrambling. It is NOT evidence bearing
    on whether stage_a.py's real block-partition/index-map path contains a
    subtle (V1/V3-class) defect, because such a defect is provably
    undetectable by this arm's construction regardless of scale. OPEN-6
    remains OPEN.
  next_concrete_action: >-
    Dispatch a V2 planted-arm task that imports stage_a.py's real
    decode_blocks (sha256-pinned, read-only) and constructs planted blocks
    with heterogeneous, decision-boundary-adjacent per-bit content instead of
    homogeneous all-0/all-1 blocks, so that boundary/index-shift defects have
    a non-zero chance of being expressed as decode errors.
  artifact_paths:
    - coordination/goals/GOAL-HQC-001/batches/BATCH-4b8ad3/tasks/TASK-20260806-e19f6c/design.md
    - coordination/goals/GOAL-HQC-001/batches/BATCH-4b8ad3/tasks/TASK-20260806-e19f6c/planted_arm.py
    - coordination/goals/GOAL-HQC-001/batches/BATCH-4b8ad3/tasks/TASK-20260806-e19f6c/planted_results.json
    - coordination/goals/GOAL-HQC-001/batches/BATCH-4b8ad3/tasks/TASK-20260806-e19f6c/comparison_report.md
    - coordination/goals/GOAL-HQC-001/batches/BATCH-4b8ad3/tasks/TASK-20260806-e19f6c/run_manifest.yaml
    - coordination/goals/GOAL-HQC-001/batches/BATCH-0a65c0/reviews/TASK-20260806-250b29/idxmap_probe.py
    - coordination/goals/GOAL-HQC-001/batches/BATCH-0a65c0/coordinator_ruling.yaml
    - ledger/evidence/EV-HQC-b71230.yaml
```

*Red-team record. I wrote only inside this directory. I hold no authority to
change status and changed none.*
