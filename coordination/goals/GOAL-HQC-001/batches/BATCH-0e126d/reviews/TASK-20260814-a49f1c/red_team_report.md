# Red-team report — discard-prefix repeat of the T=20,000 matched-pair extension on shards 5000/6000 (TASK-20260814-8bbdd2)

**Task** `TASK-20260814-a49f1c` (red team) · **Batch** `BATCH-0e126d` · **Goal**
`GOAL-HQC-001`. Reviews the Coordinator-committed snapshot at commit
`ae1b8ed2bc5e4b53f9cabbf50d889ae221f5392e` (task `TASK-20260814-0bb33f`) of
`coordination/goals/GOAL-HQC-001/batches/BATCH-0e126d/tasks/TASK-20260814-8bbdd2/{design.md,matched_pair_repeat.py,matched_pair_repeat_results.json,matched_pair_repeat_report.md,run_manifest.yaml}`.
Also read `ledger/decisions/DEC-20260809-186c86.yaml` IN FULL, `ledger/evidence/EV-HQC-3a0372.yaml`
IN FULL (O1-O14, including my own prior O8/O9/O11/O12 observations from
`TASK-20260809-47a5ec`), `coordination/goals/GOAL-HQC-001/batches/BATCH-412513/tasks/TASK-20260809-a79e4f/`
in full (design.md, matched_pair.py, matched_pair_results.json), and
`stage_a.py`/`measure.py` directly (CTRStream, `_t_shard`, `decode_blocks`,
`hist_of`, `batch_hists`, `evaluable_k`), sha256-pinned, read-only. Independent
session; I did not continue the producing agent's session and have not read
the concurrent Validator's report before writing this one.

**What I did beyond reading the artifacts:** I re-ran `matched_pair_repeat.py`
unmodified, in place (read-only sha256-pinned imports of `stage_a.py`,
`measure.py`, `matched_pair.py`; the file itself untouched), with `--out-dir`
pointed at my own scratch directory — no producer artifact was written to or
modified. I also wrote small instrumentation scripts (outside the repo) that
reuse the same pinned modules to regenerate raw per-trial data myself and
check things the committed JSON does not directly report (per-arm,
per-shard-only exponents; NaN counts in the jackknife leave-one-out
replicates). All numbers below marked "independently reproduced" or
"independently computed" come from my own execution, not from re-reading the
executor's numbers.

I do **not** contest the reported numbers. Every one I checked — the pooled
SE/diff/z at k=17, the 3-point OLS exponent, the disjointness self-check, the
F-invariant check, the sha256 pins — reproduces exactly, either via a
bit-for-bit re-run of the executor's own script or via my own from-scratch
recomputation. My objections are about whether the pre-registered binary
framing can be honestly applied to what was measured, and about several
things the framing and the fit construction do not control for that this
task's own new data lets me check directly.

---

## 1. Does DEC-20260809-186c86's binary framing cleanly cover the measured value?

**No.** State this plainly per the handoff's own instruction: the frozen
next_actions text names exactly two outcomes — "lands near 0.068-0.070"
(shard-specific) or "collapses the same way stage 2 did" (general, ≈0.017905)
— and the measured pooled SE at k=17, **0.032968**, is neither.

| reference point | value | distance from measured (linear) | distance from measured (log) |
|---|---:|---:|---:|
| "clean continuation" (0.096781/√2) | 0.06843 | 0.03546 | ln ratio 0.7385 |
| stage 2 fresh-shard collapse | 0.017905 | 0.01506 | ln ratio 0.6109 |

The measured value is roughly **2.4x closer in absolute distance**, and
**~1.2x closer in log-distance**, to the "collapse" reference than to the
"clean continuation" reference — so if forced into a single bucket it leans
toward "general," but it is a **judgment call**, not a mechanical application
of the frozen rule: the rule as written has no stated tolerance band around
either number, and 0.032968 satisfies neither literal condition. The
executor's own report (Section 4) correctly reports this as a measurement
without drawing the conclusion — that discipline is right. But the
ledger-archive task that must apply DEC-20260809-186c86's framing needs
either (a) an explicit tie-break/tolerance rule that DEC-20260809-186c86 does
not currently state, or (b) to record this batch's disposition as
**ambiguous/intermediate**, not force it into "shard-specific" or "general."
Forcing it into either bucket without saying so would misstate what a
pre-registered rule actually decided, which is exactly the overclaiming
AGENTS.md rule 9 and the inventor protocol's closure standard forbid. This is
a finding about the **frozen decision's coverage**, not a defect in this
task's measurement.

## 2. Disjointness self-check attack: is there a hidden shared dependency?

I traced `_t_shard`'s inner loop directly (not the design document's summary
of it). The only randomness source is `CTRStream(key, dom)`, and
`key = sha_key(ps_id, "T", shard, MASTER_SEED)` — **independent of
`n_trials`, of which `decode_blocks` is installed, of batch size, and of
call history.** Each trial `ti` constructs five fresh `CTRStream` objects
(`b"v0"+ti..b"v4"+ti`) with no persistent PRNG state across trials or across
calls. `decode_blocks` itself (`wht128`, `argmax`, tie logic) operates
row-wise on the `(B, n_e, n_2)` reshape with **zero cross-row (cross-trial)
mixing anywhere in the function** — confirmed by reading the reshape/sum/WHT
chain directly. This matters specifically because the discard/retain
boundary at trial index 5000 falls **mid-batch** (`BATCH=64`; trial 5000 is
row 8 of the 79th batch, `4992..5055`), so the discarded prefix and retained
tail are computed inside the *same* vectorized `decode_blocks` call for that
one straddling batch — and I confirm this produces no numerical coupling,
because the function has no batch-level statistic anywhere (no shared
mean/variance/normalization term across rows). The 300-trial warmup call
(`run_arm`) reuses local indices 0..299 on the *same* shard and is thrown
away, but since `CTRStream` is freshly instantiated per trial with no
call-to-call state, this cannot taint the subsequent real call either. I
found no bug in this mechanism, corroborating (with a batch-boundary check
this task's design.md does not itself mention) my own prior code trace in
`TASK-20260809-47a5ec` §3.

The one thing that genuinely *is* shared across every arm on a shard is the
`key` itself — but that is the deliberate, load-bearing design (it is what
makes matched pairs matched); it is not a hidden defect. My own re-run
independently reproduces `disjointness_self_check.overall_status == PASS`
and `f_invariant_check.overall_status == PASS` (0/1,100,000 mismatches) from
a driver I ran myself, not merely re-read from the committed JSON.

## 3. Alternative explanations for the SE drop, tested where cheap

**(a) NaN-jackknife-dropout artifact (my own O-analogue of the still-open
`unresolved_confounds` item in `EV-HQC-3a0372`): tested, refuted at k=17 and
at the tested boundary of the reported k-range.** `matched_pair.py`'s
`jack_se` uses `np.nanmean`/`np.nansum` but normalizes by the *full* batch
count `b = vals.shape[0]`, not the count of finite replicates — a latent bias
risk if any leave-one-batch-out replicate is non-finite. I instrumented this
directly (recomputing the 200-per-shard, and pooled 400, leave-one-out
`log2_A` values at k=17) and found **0/200 non-finite replicates on all four
of this task's retained-tail arms**, and, checking near the edge of the
reported k=2..26 range where `evaluable_k`'s 30-trial floor is closest to
binding, **0/200 at k=25 and k=26 as well**, on both shards, both variants.
I also re-derived this for the original stage-1 (T=5,000) and stage-2
(fresh shards, T≈10,000/shard) arms for comparison: **0/200 everywhere
checked.** This specific mechanism does not explain the SE collapse at the
primary cell or at the range I tested. This *narrows*, but does not
*close*, the concern — it is not re-checked here at every k or for any other
defect class/parameter set.

**(b) "Shard-specific to 8001/8002": tested, directly undercut by this
task's own new data.** I recomputed, from raw per-trial data I generated
myself, the **single-shard** local exponent (no pooling with the other
shard) between each shard's own committed T=5,000 stage-1 SE and its own new,
disjoint T=10,000 tail from this task:

| shard | SE(T=5,000) | SE(new disjoint T=10,000) | single-shard local exponent | sign of diff |
|---|---:|---:|---:|---|
| 5000 | 0.125106 | 0.017520 | **2.836** | + → **−** (flips) |
| 6000 | 0.149899 | 0.056725 | 1.402 | + → + (stable) |

Shard 5000's own single-shard local exponent (**2.836**) is *more extreme*
than the original pooled fresh-shard step (2.434) that this whole
scaling-characterization task was designed to disambiguate — and its sign
flips between the two disjoint samples, consistent with a small,
noise-dominated point estimate rather than a real signal. This is direct
evidence *against* attributing the phenomenon to "shards 8001/8002
specifically": one of the two *original*, previously well-behaved shards now
shows the same kind of large single-arm collapse when a fresh disjoint
sample is drawn from it alone. Sharpening this further, across all four
shards this campaign has ever measured at T≈10,000/shard:

| shard | SE_paired(k=17), T≈10,000/shard | source |
|---|---:|---|
| 5000 | 0.017520 | this task (new tail) |
| 6000 | 0.056725 | this task (new tail) |
| 8001 | 0.024506 | prior task, stage 2 |
| 8002 | 0.022097 | prior task, stage 2 |

a **3.24x spread among just four shards**, with shard 5000 — an *original*
shard — now showing the single **lowest** SE of all four, lower than either
"anomalous" fresh shard. This looks like broad shard-to-shard heterogeneity
in this estimator's variance at T≈10,000/shard for this defect class, not a
property specific to 8001/8002. It is genuinely new evidence this task's
design did not itself surface (the committed report and results.json report
only the *pooled* fit, never the single-shard-only local exponents above),
and it is the sharpest available discriminator between the two named
outcomes: it argues *against* the "shard-specific" half of the dichotomy more
directly than the pooled 20,000-trial number alone does.

**(c) Pooling-convention risk (my own O12, still untested, now sharper):
flagged, not tested — correctly out of this task's scope, but now more
clearly motivated.** `matched_pair.py`'s pooling concatenates raw histograms
(`H_pooled = H_5000 + H_6000`) rather than inverse-variance-weighting the two
shards' point estimates. Given the 3.24x per-shard SE spread just measured,
it is directly checkable whether concatenation is *compressing* the reported
pooled SE (0.032968) relative to what a between-shard-heterogeneity-aware
combination would give — the pooled value sits much closer to shard 5000's
own SE (0.0175) than to shard 6000's (0.0567) or their simple average
(0.0371), which is at least consistent with (not proof of) exactly this
compression. I did not compute the inverse-variance-weighted alternative
myself (outside this review's declared scope and not needed to answer the
must-attack items), but name it as the cheapest concrete follow-up (see
`required_controls`).

## 4. Are the two 3-point SE-vs-T fits (original alpha=1.470 vs this task's alpha=1.030) actually measuring the same thing?

**Not cleanly, and the same asymmetry sits inside both fits, unaffected by
holding shard identity fixed.** In both the original 4-shard fit and this
task's 2-shard-only fit, the **T=5,000 point is the arithmetic mean of two
independent, single-shard point-in-isolation SEs** (`(SE_5000+SE_6000)/2`),
while the **T=10,000 and T=20,000 points are the SE of a single, jointly
pooled (concatenated-histogram) two-shard dataset.** These are two
structurally different statistics — "average of two separate SEs" versus
"SE of one combined estimate" — and nothing in either fit's construction
establishes that they should sit on the same log-log line even under a
correct 1/√T law. Holding shard identity fixed (this task's whole purpose)
removes the shard-identity confound between steps but does **not** remove
this pooling-convention asymmetry, which is present identically in the
original and repeat fit. A cleaner design would report **either** a genuine
single-shard-only local exponent at every step (which I computed above for
the 5,000→10,000→20,000... wait, only two points are available per shard so
far, see §3b) **or** hold the pooling convention fixed across all three
points (e.g., always pool, never average) — this design does neither. This
is a previously-unflagged critique that applies retroactively to
`TASK-20260809-a79e4f`'s alpha=1.470 fit as much as to this task's alpha=1.030
fit: **neither exponent is a clean, single-construction test of 1/√T
scaling.** Separately, note (not a defect, but worth stating precisely): none
of the three T points in either fit are *nested* — T=20,000 is not "T=10,000
plus 10,000 more trials on a growing dataset," it is a wholly disjoint,
freshly-drawn 20,000-trial sample (`stage_a.py`'s `_t_shard` has no
trial-offset parameter, which is exactly why the discard-prefix technique
exists). This is conventionally fine for testing 1/√T on i.i.d. trials, but
combined with (a) the pooling-convention asymmetry above and (b) the §3b
shard heterogeneity, "SE-vs-trial-count" here conflates at least three
effects a cleaner design would separate: pure trial-count scaling, on one
fixed shard, at one fixed pooling convention.

## 5. Were `matched_pair.py`'s reused functions silently changed?

**The statistically load-bearing functions: no, genuinely reused, verified.**
I confirmed by direct code read that `make_defected_decode_blocks`,
`matched_pair_stats`, `arm_hists`, `cell`, `run_arm`, and both selftest
functions are called via the `mp_mod.` namespace in
`matched_pair_repeat.py` — i.e., genuinely imported from the sha256-pinned
`matched_pair.py` module, never reimplemented locally. I independently
recomputed `matched_pair.py`'s sha256
(`66266a6178eb46e0b37ec0afdb2620064db56bff82318498e2dd83af1bd1c821`) via
`sha256sum` directly on the committed file and it matches the executor's
measured/self-consistency-pinned value exactly; `stage_a.py` and
`measure.py`'s hashes also independently reconfirm their pre-declared
expected values exactly.

**A real, undisclosed provenance deviation — harmless to correctness, but a
genuine finding.** `design.md` §1 lists `sha256_file`, `core_seconds`,
`git_state`, and `load_module` in the *same* "reused directly, verbatim, not
re-derived" bullet as the genuinely-imported statistical functions above.
This is **factually wrong**: I diffed the actual code, and all four are
**locally copy-pasted redefinitions** in `matched_pair_repeat.py`
(`load_module` renamed to `load_module_fail_closed`), not imports —
structurally necessary, since `matched_pair.py`'s own `load_module` cannot be
called to sha256-verify-and-load `matched_pair.py` itself before it has been
loaded (a bootstrap/chicken-and-egg problem this task is the first in the
family to hit, since it is the first task to reuse another task's driver
script rather than only `stage_a.py`/`measure.py`). I verified all four
local copies are **byte-for-byte identical** (`diff` exit 0) to
`matched_pair.py`'s versions, so **no correctness impact**. But this is
exactly the class of thing the handoff explicitly required to be reported:
*"If you find yourself rewriting any reused function to make this work, stop
and report that instead -- it is a finding, not an obstacle to route
around."* `matched_pair_repeat_report.md` §6 ("Protocol deviations and
anomalies") discloses that additional functions were reused *beyond* the
minimum list, but never discloses that four of the functions *on* that list
were duplicated rather than imported. This should be corrected going
forward (see `required_controls`).

## 6. Independent reproduction and position

I re-ran `matched_pair_repeat.py` exactly as committed (sha256-pinned
read-only imports unchanged; `--out-dir` pointed at my own scratch
directory). The result is **deep-equal to the committed
`matched_pair_repeat_results.json`** on every field except the expected
run-to-run fields (`started_at_utc`/`finished_at_utc`/`command`/`git`/`budget`
timings) — confirmed programmatically, not by spot-check. My own independent
OLS refit of the 3-point exponent from the three `(T, SE)` values gives
**alpha = 1.030146864960655**, an exact match. The disjointness self-check
and the F-invariant both independently reproduce PASS. My own separately
generated raw per-trial data (regenerated from scratch via the same pinned
modules, not read from the committed JSON) confirms the k=17 diff/SE/z
values reported.

**I do not contest the numbers.** I contest (1) whether DEC-20260809-186c86's
binary framing can be applied to 0.032968 without an undisclosed judgment
call, (2) the strength of the "shard-specific" reading given the new
single-shard evidence in §3b, (3) whether the SE-vs-T fit construction
itself is clean enough (in either this task or the original) to license
"general refutation" language even if the ledger archive leans that way, and
(4) a disclosed-but-mischaracterized provenance detail in `design.md` §1
that does not affect correctness.

## 7. Standing objection, carried forward

Branch A (positive detection) has still never fired. This task's own pooled
numbers at k=17 (`|z|=0.3846<1.96`, `|diff|+1.96·SE=0.07728<0.19`) would
*also* satisfy Branch B's literal un-superseded condition, just as stage 2's
did (my `TASK-20260809-47a5ec` §2) — whatever is producing these small SEs
at large T continues to co-occur with "no detected effect." My BATCH-2ecaa1
standing objection is **not retired** by this batch either.

## 8. Scope

Toy-scale, PS-R3-only, single defect class (V3), single injection point
(`decode_blocks`, block `n_e-1`), shards 5000/6000 only, trial indices
`[5000,15000)` per shard (this task) plus the committed `[0,10000)`
(prior task, per shard). No claim here about HQC's IND-CCA security, its
decoding-failure rate, assumption A17/A5, or any standardized parameter set.
Pollard-rho/BSGS baseline comparison is not applicable to this HQC
decode-path instrument task; the relevant baseline is the campaign's own
between-shard design, whose documented power deficit this line of work
exists to correct. This batch's measured spend (36.818 core-s / 36.785
wall-s, independently corroborated by my own ~37s re-run) is far under its
500/1,800 authorization and does not license any change to that comparison.

---

```yaml
red_team_report:
  id: RT-20260814-a49f1c
  task_id: TASK-20260814-a49f1c
  claim_under_review: >-
    matched_pair_repeat_report.md (TASK-20260814-8bbdd2, snapshot
    ae1b8ed2bc5e4b53f9cabbf50d889ae221f5392e) reports a pooled SE_paired at
    k=17 of 0.032968496689324056 on a genuinely new, disjoint T=20,000
    matched-pair extension on shards 5000/6000 themselves, with a refitted
    3-point SE-vs-trial-count exponent alpha=1.030146864960655 (shards
    5000/6000 only, T=5,000/10,000/20,000), reported descriptively with no
    conclusion drawn about DEC-20260809-186c86's shard-specific-vs-general
    framing.
  objections:
    - "DEC-20260809-186c86's pre-registered binary framing does not cleanly
      cover the measured value. 0.032968 satisfies neither the 'near
      0.068-0.070' condition nor is it equal to the 'collapses the same way
      stage 2 did' reference (0.017905); it is 2.4x closer in absolute
      distance and ~1.2x closer in log-distance to the collapse reference,
      but this is a judgment call the frozen rule does not itself resolve
      (no stated tolerance band around either named number). The ledger
      archive must either state an explicit tie-break or record this
      batch's disposition as ambiguous/intermediate rather than forcing it
      into 'shard-specific' or 'general' silently."
    - "Independently recomputed single-shard-only (unpooled) local exponents
      directly undercut the 'shard-specific to 8001/8002' reading: shard
      5000 ALONE shows local exponent 2.836 between its own committed
      T=5,000 SE and its own new disjoint T=10,000 tail -- MORE extreme than
      the original pooled fresh-shard step (2.434) this task was designed to
      disambiguate -- and its point-estimate sign flips (+0.1018 -> -0.0215).
      Across all four shards this campaign has measured at T~10,000/shard
      (5000=0.0175, 6000=0.0567, 8001=0.0245, 8002=0.0221), shard 5000 -- an
      ORIGINAL shard -- now shows the single lowest SE of all four. This is
      new evidence this task's own committed artifacts do not surface (only
      the pooled fit is reported) and is the sharpest available
      discriminator between the two named outcomes."
    - "The 3-point SE-vs-T fit construction (both this task's alpha=1.030 AND
      the original alpha=1.470) mixes two different statistics across its
      own three points: T=5,000 is the arithmetic MEAN of two independent
      per-shard SEs, while T=10,000/T=20,000 are the SE of a single, jointly
      POOLED (concatenated-histogram) dataset. Holding shard identity fixed
      removes the shard-identity confound between steps but does not remove
      this pooling-convention asymmetry, which is baked into both fits
      identically and has never been isolated from genuine trial-count
      scaling."
    - "design.md Section 1 claims sha256_file/core_seconds/git_state/
      load_module are 'reused directly, verbatim, not re-derived' via
      import, in the same bullet as the genuinely-imported statistical
      functions. This is factually wrong: I diffed the code directly and all
      four are locally copy-pasted redefinitions in matched_pair_repeat.py
      (structurally necessary to bootstrap-load matched_pair.py itself
      before it can be sha256-verified). Verified byte-for-byte identical to
      the originals (no correctness impact), but this is exactly the kind of
      rewritten-reused-function deviation the handoff required to be
      disclosed as a finding, and matched_pair_repeat_report.md's own
      'protocol deviations' section does not disclose it."
    - "This task's own pooled numbers at k=17 (|z|=0.3846<1.96,
      |diff|+1.96*SE=0.07728<0.19) also satisfy Branch B's literal
      un-superseded condition, exactly as stage 2's did -- reinforcing that
      whatever produces these small SEs continues to co-occur with 'no
      detected effect.' Branch A has still never fired anywhere in this
      campaign; my BATCH-2ecaa1 standing objection is not retired."
  required_controls:
    - "Report an inverse-variance-weighted combination of the two shards' own
      point estimates at k=17 (and ideally k=2..26) alongside the
      concatenated-histogram pooled estimate, to check whether the pooling
      convention is compressing the reported SE relative to the now-measured
      3.24x between-shard heterogeneity (EV-HQC-3a0372 O12, still untested,
      now more directly motivated by this task's own retained-tail data)."
    - "Instrument and report, per arm and per k across the full k=2..26
      range, the count of non-finite (NaN) leave-one-batch-out jackknife
      replicates. I independently checked k=17, 25, and 26 on all four of
      this task's arms plus the prior task's stage-1/stage-2 arms and found
      0/200 everywhere -- ruling this specific artifact out at the cells
      checked, but it remains unverified at every k and for any future
      defect class or parameter set."
    - "Run the same discard-prefix, disjoint-trial-range design on a SINGLE
      shard in isolation (no pooling) at 2-3 trial counts, on each of shards
      5000, 6000, 8001, 8002 separately, to obtain a pooling-convention-free,
      shard-identity-fixed exponent per shard -- the cheapest remaining
      control that would isolate trial-count scaling from both shard
      identity and pooling convention, which every fit run so far (original
      and repeat) still conflates."
    - "Correct design.md's Section 1 claim about which functions are
      import-reused vs. locally re-derived, or factor sha256_file/
      core_seconds/git_state/load_module into a separately-pinned shared
      bootstrap module so future tasks in this family can genuinely import
      them without the chicken-and-egg problem this task solved by
      duplication."
  counterexample_or_mutation: >-
    Cheapest discriminating experiment, already partially run by my own
    independent instrumentation: compute the SINGLE-SHARD-ONLY (unpooled)
    local exponent for each of the four shards this campaign has ever used,
    using each shard's own committed T=5,000 SE and its own new/committed
    T=10,000 SE, with no cross-shard pooling anywhere. I computed this for
    shards 5000 (2.836) and 6000 (1.402) from this task's own new data;
    8001/8002 already have single-arm T=10,000 data in the committed record
    and should be refit the same way for a complete four-shard table. If
    single-shard local exponents cluster well above [0.4,0.6] across most or
    all four shards (as the two I computed already suggest), that is
    confound-free evidence the collapse is a property of this
    estimator/defect/parameter-set combination in general, not of any
    specific shard pair or of the pooling convention -- a materially
    stronger basis for "general" than the pooled 3-point fit this task
    reports, and one that does not require DEC-20260809-186c86's binary
    framing to resolve an intermediate value.
  baseline_comparison: >-
    Not applicable in the Pollard-rho/BSGS sense (this is an HQC decode-path
    instrument measurement, not an ECDLP claim). The relevant specialized
    baseline is the campaign's own between-shard design, whose documented
    power deficit (BATCH-2ecaa1 red-team report) this line of work exists to
    correct; this batch's measured 36.818 core-seconds / 36.785 wall-seconds
    (independently corroborated by my own ~37-second re-run, well inside the
    500/1,800 authorization) does not approach or license any change to that
    comparison.
  heuristic_challenges: []
  cost_model_challenges:
    - "Budget and spend are honestly reported and measured, not modeled
      (36.818 core-seconds / 36.785 wall-seconds against 500/1,800
      authorized). My own independent re-run of the identical script
      measured ~36.97 core-seconds / ~36.8 wall-seconds, the same order of
      magnitude, with no infrastructure event. No objection to the cost
      accounting itself."
  reduction_and_scope_challenges:
    - "Claim tier correctly stays TOY throughout matched_pair_repeat_report.md
      and run_manifest.yaml; PS-R3-only, V3-only, decode_blocks-only, shards
      5000/6000-only, trial-indices-[5000,15000)-only scope is stated
      repeatedly and accurately. I found no HQC-security, decoding-failure-
      rate, A17/A5, or standardized-parameter-set claim latent anywhere in
      the executor's artifacts."
    - "H-HQC-18d1b4 is correctly left untouched by this task's own artifacts
      (the executor does not apply DEC-20260809-186c86's framing, as
      instructed); any movement of that hypothesis is the ledger archive
      task's responsibility, not this task's, and is outside what I am
      reviewing here."
  proof_architecture_challenges: []
  narrowest_supported_statement: >-
    The disjoint-trial-range, fixed-shard-identity design was implemented
    correctly and does isolate shard identity from trial count as intended:
    the disjointness self-check and the new F[:, 0:n_e-1] structural
    invariant both PASS, independently reproduced from my own from-scratch
    driver, and the reported diff/SE/z/exponent values are exactly
    reproducible, bit-for-bit, from a re-run of the committed script. The
    measured pooled SE at k=17 (0.032968) does NOT land near DEC-20260809-
    186c86's "shard-specific" reference (0.068-0.070) and is closer, though
    not identical, to its "general refutation" reference (0.017905) -- this
    is an intermediate value the frozen binary rule does not cleanly cover,
    and applying either named label to it requires an undisclosed judgment
    call. Independently recomputed single-shard-only local exponents (shard
    5000: 2.836; shard 6000: 1.402) are BOTH far outside [0.4,0.6], and
    shard 5000's alone exceeds the original fresh-shard anomaly's local
    exponent (2.434) -- evidence against, not for, attributing the
    phenomenon specifically to shards 8001/8002. A pooling-convention
    asymmetry (T=5,000 as an average of two per-shard SEs vs. T=10,000/20,000
    as SEs of a jointly pooled dataset) is present identically in both the
    original and repeat 3-point fits and has never been isolated from
    genuine trial-count scaling. The NaN-jackknife-dropout artifact I tested
    as an alternative explanation is refuted at k=17, 25, and 26 on every
    arm checked (0/200 everywhere). Branch A has still never fired anywhere
    in this campaign.
  next_concrete_action: >-
    Before the ledger archive applies DEC-20260809-186c86's framing: compute
    and record the single-shard-only (unpooled) local exponent for all four
    shards used in this campaign (5000, 6000 from this task; 8001, 8002 from
    the committed record), since this is a materially stronger,
    pooling-convention-free basis for "shard-specific vs. general" than the
    pooled 3-point fit either task reports, and my own partial computation
    (5000: 2.836, 6000: 1.402) already argues against the "shard-specific"
    reading. Separately, correct design.md's mischaracterization of which
    functions are import-reused vs. locally re-derived (or factor the
    bootstrap functions into a shared pinned module) before the next task in
    this family reuses matched_pair_repeat.py the same way.
  artifact_paths:
    - coordination/goals/GOAL-HQC-001/batches/BATCH-0e126d/tasks/TASK-20260814-8bbdd2/design.md
    - coordination/goals/GOAL-HQC-001/batches/BATCH-0e126d/tasks/TASK-20260814-8bbdd2/matched_pair_repeat.py
    - coordination/goals/GOAL-HQC-001/batches/BATCH-0e126d/tasks/TASK-20260814-8bbdd2/matched_pair_repeat_results.json
    - coordination/goals/GOAL-HQC-001/batches/BATCH-0e126d/tasks/TASK-20260814-8bbdd2/matched_pair_repeat_report.md
    - coordination/goals/GOAL-HQC-001/batches/BATCH-0e126d/tasks/TASK-20260814-8bbdd2/run_manifest.yaml
    - coordination/goals/GOAL-HQC-001/batches/BATCH-0e126d/archives/TASK-20260814-0bb33f/snapshot-receipt.json
    - ledger/decisions/DEC-20260809-186c86.yaml
    - ledger/evidence/EV-HQC-3a0372.yaml
    - coordination/goals/GOAL-HQC-001/batches/BATCH-412513/tasks/TASK-20260809-a79e4f/design.md
    - coordination/goals/GOAL-HQC-001/batches/BATCH-412513/tasks/TASK-20260809-a79e4f/matched_pair.py
    - coordination/goals/GOAL-HQC-001/batches/BATCH-412513/tasks/TASK-20260809-a79e4f/matched_pair_results.json
    - coordination/goals/GOAL-HQC-001/batches/BATCH-412513/reviews/TASK-20260809-47a5ec/red_team_report.md
    - coordination/goals/GOAL-HQC-001/batches/BATCH-6fddee/tasks/TASK-20260806-64b506/stage_a.py
    - coordination/goals/GOAL-HQC-001/batches/BATCH-0a65c0/tasks/TASK-20260806-cde749/measure.py
```

*Red-team record. I wrote only inside this directory. I hold no authority to
change status and changed none. This is an independent session's judgement,
formed by re-running the committed script bit-for-bit from a separately
directed output path, independently regenerating raw per-trial data through
my own driver against the same sha256-pinned modules, and re-deriving every
reported statistic (SE, diff, z, the 3-point exponent, and the previously
unreported single-shard-only local exponents) from that data rather than
accepting the committed report's arithmetic on faith.*
