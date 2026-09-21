# Matched-pair reanalysis + required-T derivation (items 1-2 of GOAL-HQC-001's next_action)

`TASK-20260807-db4230` (executor) · `BATCH-2ecaa1` (continuation, no new batch
opened — see Section 0) · `GOAL-HQC-001` · `EXP-HQC-982268` ·
`H-HQC-18d1b4`. Follows `DEC-20260806-9a4551`'s `next_actions` (1) and (2),
as re-stated verbatim in `ledger/goals/GOAL-HQC-001.yaml`'s `next_action`
field (read live 2026-08-07).

**Claim tier: TOY, hard ceiling.** Nothing here is a statement about HQC,
assumption A17, its decoding-failure rate, or any standardized parameter
set. This is pure analysis of already-committed pilot-scale artifacts plus
arithmetic — no new sampling, no new invocation of `stage_a.py` or
`measure.py`, no new run.

Git state at time of writing: commit `0a69c3328063d7454a4a328704623325665514aa`
on branch `claude/run-remaining-experiments-jymjz4`. Working tree carries one
unrelated untracked directory (`experiments/EXP-ECTD-9e4248/driver/`, not
touched by this task) plus this task's own new files; otherwise clean.

**Certificate discipline**: `certificate.kind: none`. This task makes no
discrete-log-solve or factor-base-relation claim; it is a re-analysis of an
existing joint-moment estimator measurement, not a solve.

---

## 0. Staleness check on `ledger/goals/GOAL-HQC-001.yaml`'s `next_action`

Read the live file in full (not a paraphrase). `current_batch_id:
BATCH-2ecaa1` matches the most recently closed batch
(`batch_checkpoints` list ends at `BATCH-2ecaa1`, `status: closed`,
`decision: DEC-20260806-9a4551`). Cross-checked against
`coordination/goals/GOAL-HQC-001/batches/*` by last-commit timestamp: eleven
batch directories exist, and `BATCH-2ecaa1` (2026-08-06T19:44:15Z) is the
most recent — no batch postdates it. `GOAL-HQC-001` has no
`ledger/goals/GOAL-HQC-001/checkpoints/` shard directory (unlike some other
goals); the single `ledger/goals/GOAL-HQC-001.yaml` file is authoritative and
was read directly.

**Conclusion: `next_action` is CURRENT, not stale.** Its text matches the
task brief verbatim (three-item ordered plan: matched-pair reanalysis,
required-T derivation, conditional positive-control pilot; claim tier toy;
`campaign_budget.maximum_batches: null`; ~4,973 of 10,800 wall-clock seconds
remaining as of `BATCH-2ecaa1`'s close, which is still current since no
batch has run since). This task proceeds on that basis. This finding is the
opposite of the GOAL-ECDLP-001 / GOAL-MLDSA-001 staleness pattern the task
brief warned about — recorded explicitly per that instruction rather than
silently proceeding.

This task continues under the existing `BATCH-2ecaa1` batch identifier
(the goal's `current_batch_id`) because opening a new batch is a
Coordinator action outside this role's authority; if the Coordinator judges
a fresh batch id is more appropriate for this follow-up work, the next free
one is obtainable via `python3 tools/allocate_id.py --next batch` (random
6-hex token, no `--area`/`--date`).

---

## 1. Matched-pair reanalysis of TASK-20260806-77a574's own already-collected data

**Result: NOT POSSIBLE — and not merely because the raw data wasn't
serialized. The pilot's own committed data structurally never contained a
matched-pair correspondence, independent of what was or wasn't written to
disk.** Two independent facts, either one alone sufficient, both checked
directly against the code:

### 1a. The raw per-trial arrays were never persisted

`pilot_injection.py`'s `main()` calls `sa._t_shard(...)`, whose return value
(`stage_a.py` line ~487, `_t_shard`) includes `F_all`, a `(n_trials, n_e)`
per-trial-per-block failure-indicator array — this IS the raw per-trial data
a matched-pair analysis would need. But `pilot_injection.py` never writes
`F_all` (or `S = F.sum(axis=1)` per-trial, in trial order) to
`pilot_results.json`. It only calls `sa.hist_of(S, n_e)` — a `np.bincount`
over the **whole arm** — and serializes that histogram
(`pilot_results.json.MEASUREMENT.{defected,undefected}.S_histogram`, 57
integers each). A histogram of per-trial outcome counts discards trial
identity entirely: from `S_histogram` alone it is impossible to say which
histogram entry came from which trial, so even *within* one arm, per-trial
values cannot be recovered, let alone paired against the other arm's trials.

### 1b. Independent of (1a): the two arms were drawn from disjoint PRNG shards, so no shared underlying draws exist to pair

`design.md` §1 calls the undefected arm a "paired... control arm," but reading
`stage_a.py`'s `_t_shard` (and confirmed independently by the Red Team's own
review, §3) shows each trial's randomness is `key = sha_key(ps["id"], "T",
shard, MASTER_SEED)` — a distinct SHA-256-derived key **per shard index**,
with each trial `i` inside a shard then derived via `CTRStream(key, b"v0" +
i.to_bytes(...))` etc. `pilot_injection.py` used **shard 5000 for the
defected arm and shard 6000 for the undefected arm**
(`pilot_results.json` / `run_manifest.yaml`, `seeds_and_randomness`). Because
the two shards have different keys, defected-arm trial `i` and
undefected-arm trial `i` are drawn from cryptographically independent PRNG
streams — **there is no trial in the defected arm whose underlying random
draw is shared with any trial in the undefected arm.** This is a structural
property of the committed design, not a data-retention gap: even a
hypothetical version of `pilot_injection.py` that *had* serialized full
`F_all` for both arms would still not yield matched pairs, because the pairs
were never generated as matched pairs in the first place. "Reconstructing"
a matched-pair comparison from this specific pilot's data is therefore not a
missing-artifact problem but a design-choice problem: the between-shard
design is exactly what the Red Team's review (§0, §2) diagnosed as the
weaker of two equal-cost designs, and this is the mechanism by which it is
weaker — it was never structured to allow post-hoc pairing.

### What would need to have been saved / done differently

A genuine matched-pair reanalysis of *this pilot's own data* would require
having run **one** shard's trials through **both** `decode_blocks` variants
(true and defected) — e.g., `sa._t_shard` called once under the defected
wrapper and once under the unmodified function, **both invocations using the
same shard index** — and having persisted the per-trial `S` values (or the
raw `F_all` arrays) **in trial order** for both resulting arms, so that
entry `i` of one array is known to correspond to entry `i` of the other.
None of this happened: the pilot ran two *different* shards, one arm each,
and serialized only each arm's own aggregate histogram.

### Is this recoverable now, without new sampling?

Because `stage_a.py`'s PRNG (`CTRStream`, keyed by `sha_key(ps_id, "T",
shard, MASTER_SEED)`) is a **deterministic** function of the committed shard
index — confirmed by three independent parties already in this campaign's
record (the executor's own "uncharged shakedown" determinism check,
`run_manifest.yaml.results_determinism_check`; the Validator's bit-identical
reproduction of both S-histograms from shard 5000/6000,
`validation_report.yaml` lines 103-119) — decoding the *already-used* shard
5000 through the **unmodified** `decode_blocks` (or shard 6000 through the
**defected** wrapper) would deterministically reconstruct a genuine
matched pair, using literally the same underlying random bits already
implicit in the committed shard indices, with no new entropy drawn. This is
very likely cheap (the pilot's own throughput figure implies roughly
2-3 core-seconds per 5,000-trial arm). **This task does not do it.** Doing
so requires invoking `stage_a.py`'s real sampler pipeline again — a new
process execution against the real code, which is exactly what this task's
brief instructs me to stop and report rather than launch ("if you find
yourself about to launch anything resembling a new experimental run, stop
and report instead"). I am flagging this distinction explicitly rather than
picking a side of the ambiguity: it is deterministic recomputation, not new
randomness, but it is still a new run of the pipeline, and the budget
instruction for this specific task is narrower than "no new randomness" — it
is "no new sampling," read here conservatively as "no new pipeline
invocation." This is a candidate for a small, explicitly-scoped, Coordinator-
authorized follow-up (re-decode the two already-committed shards through the
opposite variant, nothing else), distinct from and much smaller than the
positive-control pilot named as item 3.

### The closest thing that already exists: the Red Team's own matched-pair probe

`red_team_report.md` §0 ("Probe 1" and "Probe 2") already contains a genuine
matched-pair measurement of this exact defect at this exact injection point
— but it is **not a reanalysis of the executor's pilot data**. It is an
independently-collected sample: the Red Team generated **5,000 fresh
trials on shard 424242** (disjoint from every shard used anywhere in this
campaign, including the pilot's own 5000/6000) and decoded **each trial
through both the true and the defected `decode_blocks`**, which is exactly
the matched-pair structure the pilot's own between-shard design lacks. This
data already exists in the committed record (no new compute is needed from
this task to read it) and is the only matched-pair measurement of the
propagated joint-moment effect on record for this defect/injection point.
Reported numbers, copied verbatim from `red_team_report.md`:

| quantity (k=17, T=5,000, matched pairs, shard 424242) | value |
|---|---:|
| point estimate, true decode | -0.9360 |
| point estimate, defected decode | -0.7438 |
| diff (defected − true) | **+0.1922** |
| SE, unpaired (independent-arm quadrature, same data) | 0.5514 |
| SE, matched-pair jackknife | **0.1982** |
| z, unpaired | 0.349 |
| z, matched-pair | **0.970** |
| power ratio (unpaired SE / paired SE) | 2.78x |
| local (block-level) flip rate, matched pairs | 10.7% (533/5000), z≈24.4 |

For context, the pilot's own (between-shard, misspecified) measurement at
the same T and k: diff = -0.2069, SE = 0.4437, z = -0.466 (magnitude of
diff agrees with the Red Team's fresh sample to within ~8%; **the sign
differs between the two independent samples** — noted, not resolved, below).

### Does the tighter SE resolve the ambiguity outright?

**No — narrower, but genuine ambiguity remains.** Using the correctly
specified (matched-pair) instrument at the same trial count the pilot used:
`z = 0.970` at `k = m = 17`. This clears neither the conventional two-sided
`|z| ≥ 1.96` significance bar nor anything close to it, so it does **not**
demonstrate a real effect. But it is also not the near-zero `z ≈ 0` a
confidently-clean null would show: a 95%-ish interval around the matched-pair
point estimate (`0.192 ± 1.96 × 0.198` ≈ `[-0.20, +0.58]`) comfortably
contains both zero and effect sizes several times the point estimate itself.
**Both "the propagated effect is genuinely near zero" and "the propagated
effect is on the order of ~0.2 log2-units" remain consistent with this
measurement.** This matches, and does not improve past, the Red Team's own
stated verdict ("GENUINELY AMBIGUOUS / INCONCLUSIVE"); tightening the SE by
~2.8x at k=17 moved `z` from -0.466 (pilot, unpaired) to +0.970 (Red Team,
paired) — a real gain in power, but not enough at this trial count to settle
the question either way. The sign disagreement between the pilot's own
unpaired estimate (negative) and the Red Team's fresh matched-pair estimate
(positive) is itself informative: it is additional evidence that the true
effect, whatever it is, is small relative to the noise floor at T=5,000 —
consistent with (not proof of) a small or zero propagated effect, but not
strong enough on its own to exclude one of the magnitude both measurements'
point estimates suggest.

**Bottom line for item 1: raw per-trial data is not recoverable from the
pilot's own committed artifacts without a new (deterministic but real)
pipeline invocation, which this task does not perform. The closest
already-existing matched-pair evidence (Red Team's independent probe, same
defect/point/T, different shard) gives a materially tighter SE (2.78x at
k=17) but still does not cleanly resolve whether the propagated effect is
zero or real at this trial count — ambiguity is narrowed, not resolved.**

---

## 2. Required-T derivation from the defect's own measured local effect size

Full arithmetic, reproducible standalone from cited constants only (no
sampling): `required_t_derivation.py` in this directory. Command:
`python3 required_t_derivation.py`. All inputs are copied verbatim from
already-committed artifacts, cited inline; the only operation performed is
algebra.

### Method

The campaign's actual detection instrument is the joint-moment estimator
`log2_Ahat_k` at the load-bearing order `k = m = 17`, not a raw binomial test
on the local (block-level) flip rate — so the required-T question must be
asked of that instrument, using the **matched-pair** design (§1 established
this is the correctly specified one; the between-shard design the pilot
actually used is demonstrably 2.8-10.6x less powerful at the same cost, per
the Red Team's review). The "size implied by the defect's own measured
10.7% local rate" is read as the propagated joint-moment effect the Red
Team measured **in the same probe** that measured the 10.7% local flip rate
(Probe 1 and Probe 2 both ran on the identical 5,000 matched trials at
shard 424242) — this is the most direct, non-fabricated link between the
local rate and its k=17 consequence available in the record; no independent
first-principles re-derivation of the local→joint-moment transform is
attempted here (that would require a combinatorial argument this task does
not construct).

Standard formula, assuming jackknife SE scales as `1/sqrt(T)` (the same
asymptotic-normal assumption the specification's own `T_req = 3.09e5`
already relies on for a different target quantity — not independently
re-verified here across multiple `T` values for the matched-pair design
specifically, since only one `T` (5,000) of matched-pair data exists in the
record; flagged as an assumption, not a measured scaling law):

```
SE(T) = SE(T0) * sqrt(T0 / T)
require SE(T_req) = delta / z
=>  T_req = T0 * (SE(T0) * z / delta) ** 2
```

with `T0 = 5000`, `SE(T0) = 0.1982` (Red Team's matched-pair jackknife SE,
k=17), `delta` taken from the ~0.19-0.21 range both independent
measurements' point estimates agree on in magnitude, and `z` the combined
significance/power threshold.

### Result

| delta (log2_A_17 units) | z = 1.96 (bare significance) | z = 2.80 (80% power, α=0.05) |
|---|---:|---:|
| 0.192 (Red Team's own matched-pair diff) | 20,426 | 41,686 |
| 0.207 (pilot's own diff magnitude) | 17,625 | 35,970 |
| 0.20 (midpoint) | 18,864 | 38,498 |

**Primary estimate: T_req ≈ 1.8×10⁴ – 4.3×10⁴ trials** for the correctly
specified (matched-pair) comparison to detect a propagated effect of the
magnitude the defect's own measured local rate implies, at k=17, depending
on the exact point-estimate and power convention chosen. This is
**modeled/derived, not measured** — it extrapolates a single T=5,000 SE
measurement via the 1/√T scaling assumption stated above, and is contingent
on the true propagated effect actually being of the magnitude both existing
point estimates suggest (which §1 shows remains unconfirmed).

### Cross-check against the between-shard (misspecified) design and the spec's own T_req

Applying the identical formula to the pilot's *actual* between-shard design
(SE(T0) = 0.4437-0.5514 depending on which sample) gives T_req ≈
88,000-323,000 — the same order of magnitude as, and bracketing,
`experiments/EXP-HQC-982268/specification.yaml`'s existing `T_req = 3.09e5`.
This is a useful consistency check (not a validation of either number as a
measurement): it explains, as the Red Team already noted qualitatively, why
the between-shard SE achieved at T=5,000 "happens to be" roughly what the
spec's own T_req would predict at this scale — the spec's T_req was derived
for the undefected estimator's own precision target, a different question,
and its numeric proximity to this cross-check is not evidence the two
questions are the same one. **The matched-pair design's derived T_req (~1.8-
4.3×10⁴) is roughly 5-18x smaller than the between-shard design's derived
T_req for detecting the identical effect size** — a large, concrete,
already-quantified reason to prefer the matched-pair design for any future
run at this injection point, independent of whether the effect turns out to
be real.

### Secondary note: the local (block-level) effect is already far above its own detection floor

For context only (not the primary instrument): a bare binomial test on the
10.7% local flip rate itself would need only on the order of a few dozen
trials to clear `z ≥ 1.96` (`SE ≈ sqrt(p(1-p)/T)`, `p ≈ 0.1066`, giving
`T ≈ 32` for `z = 1.96`). The pilot's 5,000 trials are massively overpowered
for the local effect (observed `z ≈ 24`) and correspondingly underpowered
for the k=17 joint-moment effect the campaign actually needs resolved — the
bottleneck is entirely in the dilution from block-level to joint-moment
statistic (`k/n_e ≈ 0.30` of subsets touch the perturbed block), consistent
with `design.md` §4's qualitative dilution argument, now given a number.

---

## 3. Recommendation (item 3 is NOT executed here — out of scope)

**Genuine ambiguity remains after items 1 and 2.** Item 1 could not
supply a true reanalysis of the pilot's own data (structural, not a
retention gap) and the best available substitute (Red Team's independent
matched-pair probe) narrows but does not resolve the ambiguity (z=0.970 at
k=17, matched pairs). Item 2's derivation gives a concrete, much smaller
required-T for the correctly specified design (~1.8-4.3×10⁴ trials) than
either the between-shard design's own implied requirement (~9-32×10⁴) or
the specification's original `T_req = 3.09e5` (a different target
quantity).

Per this task's explicit scope, **item 3 (a positive-control pilot at V1) is
not run here.** It requires new sampling and its own Coordinator-approved
budget authorization, which this task does not have. Recommended next step,
naming the concrete quantity this derivation supplies: a matched-pair pilot
at T on the order of **2×10⁴ to 4×10⁴ trials** (not the full `3.09×10⁵`) —
substantially cheaper than the original full-scale commitment, and, per §1,
using a matched-pair design from the outset (same underlying draws decoded
through both `decode_blocks` variants) rather than repeating the
between-shard design's demonstrated power deficit. Whether that pilot should
be run at the same V3/`decode_blocks` injection point or at V1 (the
positive-control candidate the Red Team and `DEC-20260806-9a4551` already
named) is a Coordinator call weighing the same evidence this report and the
Red Team's review already assembled; this task does not make that call.

---

## 4. Scope, budget, and what this task does not say

- No file outside this task's own directory was written.
- No import of `stage_a.py` or `measure.py`; no PRNG draw; no invocation of
  `_t_shard` or any other pipeline code. All numeric inputs are copied
  verbatim, with citation, from already-committed artifacts
  (`pilot_results.json`, `pilot_report.md`, `run_manifest.yaml`,
  `red_team_report.md`, `validation_report.yaml`). The only computation
  performed is the algebra in `required_t_derivation.py`, independently
  re-runnable and checked to reproduce the numbers quoted above.
- Compute used: effectively zero core-seconds beyond the trivial arithmetic
  script (well under the "few hundred core-seconds" ceiling this task was
  given; no wall-clock budget was drawn against `GOAL-HQC-001`'s remaining
  campaign total).
- This task does not change `H-HQC-18d1b4`'s status, does not author a
  Coordinator decision, and draws no conclusion about HQC's IND-CCA
  security, its decoding-failure rate, or any standardized parameter set.
  Per `agents/executor.md`, observations are reported separately from
  interpretation above; the go/no-go call on item 3 and on this campaign's
  stopping rule belongs to the Coordinator and independent reviewers.

## 5. Artifacts

- `reanalysis_report.md` — this file.
- `required_t_derivation.py` — standalone, reproducible arithmetic (no
  sampling); run with `python3 required_t_derivation.py`.

## 6. Sources read in full before this analysis

- `coordination/goals/GOAL-HQC-001/batches/BATCH-2ecaa1/tasks/TASK-20260806-77a574/{design.md,pilot_injection.py,pilot_results.json,pilot_report.md,run_manifest.yaml}`
- `coordination/goals/GOAL-HQC-001/batches/BATCH-2ecaa1/reviews/TASK-20260806-92aecb/red_team_report.md`
- `coordination/goals/GOAL-HQC-001/batches/BATCH-2ecaa1/reviews/TASK-20260806-8d4d48/validation_report.yaml`
- `ledger/decisions/DEC-20260806-9a4551.yaml`, `ledger/decisions/DEC-20260806-1ac8fa.yaml`
- `ledger/goals/GOAL-HQC-001.yaml` (live file, in full)
- `coordination/goals/GOAL-HQC-001/batches/BATCH-6fddee/tasks/TASK-20260806-64b506/stage_a.py`
  (relevant excerpts: `_t_shard`, `hist_of`, `batch_hists`, `evaluable_k`,
  `sha_key`, `N_JACK_BATCHES`, `T_STAB_THRESHOLD`)
