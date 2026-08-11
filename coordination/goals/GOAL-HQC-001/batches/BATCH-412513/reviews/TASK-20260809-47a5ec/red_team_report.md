# Red-team report — matched-pair SE reconstruction and pre-registered branch rule (TASK-20260809-a79e4f)

**Task** `TASK-20260809-47a5ec` (red team) · **Batch** `BATCH-412513` · **Goal**
`GOAL-HQC-001`. Reviews the Coordinator-committed snapshot at commit
`1f8d61ac9` (`TASK-20260809-a87710`, parent `67f1f0dfae80162aee5d7a0ef3805c14c30fa495`,
backfilled at `18934eb07`; both commits confirmed reachable from `HEAD` and
every declared `path_sha256` re-verified byte-for-byte against the live tree
before this review began — see §0). Also read `ledger/decisions/DEC-20260809-46e85c.yaml`,
`ledger/evidence/EV-HQC-dd85c1.yaml`, and my own campaign's standing objection
at `coordination/goals/GOAL-HQC-001/batches/BATCH-2ecaa1/reviews/TASK-20260806-92aecb/red_team_report.md`
(read as the objection this batch is tested against, not re-adopted uncritically).
Independent session; the Validator's parallel task (`TASK-20260809-603dc5`) was
not consulted and its `write_scope` was not read.

**Headline verdict, stated up front because it changes how the next
Coordinator decision must read this batch's own numbers.** The mechanism is
sound — I independently re-executed the actual committed script end-to-end
(not merely read it) and re-derived the core statistic from scratch, and both
verifications match the committed artifacts to full float precision. But the
pre-registered decision rule's own **exponent-supersession clause fired**,
not any of branches A/B/C1/C2 — the raw z/diff numbers at stage 2 look like
Branch C1 (ambiguous, sizeable diff, consistent sign), but the fitted
SE-vs-T exponent (0.3186) falls outside the pre-registered `[0.4, 0.6]` band,
which `DEC-20260809-46e85c` and `task_card.yaml` both state **supersedes**
A/B/C. If the next Coordinator decision reads stage 2's z/diff as Branch C1
and dispatches a sized extension without addressing the supersession first,
that would misapply the rule it is bound by. Branch A did not fire
(`|z|=1.298 < 1.96`), so my standing objection from `TASK-20260806-92aecb` —
**no batch in this campaign has ever produced a fired cell from a
known-present real-sampler defect** — is **NOT retired** by this batch.

---

## 0. Independent reproduction: what I actually ran

Budget used: two full re-executions of the actual committed `matched_pair.py`
(not a rewrite — the identical file, sha256-pinned reuse of `stage_a.py`/
`measure.py` unchanged), plus two from-scratch reimplementations of the
core statistics, all written to my own scratch directory
(`--out-dir` pointed outside the task's `write_scope`; nothing under
`coordination/goals/GOAL-HQC-001/batches/BATCH-412513/tasks/TASK-20260809-a79e4f/`
was touched). Total compute: ~10.3 core-seconds, well inside the 1,800-second
authorization.

**Check A — full script re-execution, bit-for-bit diff.** I ran
`python3 matched_pair.py --stage 1 --out-dir .` then `--stage 2 --out-dir .`
against the same sha256-pinned `stage_a.py`/`measure.py`, on this session's
own machine (a third environment, distinct from both the pilot's Linux/
Python-3.11/numpy-2.4.6 run and the executor's macOS/Python-3.13.1/numpy-2.4.0
run). A structural diff of my output JSON against the committed
`matched_pair_results.json`, excluding only the `stage{1,2}_run` provenance
blocks (timestamps, git state, environment strings), found **12 differences,
every one a wall-clock/cpu-time measurement** (e.g.
`stage1_per_shard_timing[0].wall_seconds`: mine `1.395`, theirs `1.411`).
Every statistical quantity — `gate_determinism` (both bit-identity checks),
all 20,000 raw per-trial `S` values across the four stage-1 arrays, every
per-shard and pooled `diff`/`paired_jackknife_se`/`unpaired_se_quadrature`/
`ratio`/`z` at every `k` in `2..26` for both stages, `stage2_shards_used`,
`stage2_trial_count_rule.T2`, and `se_vs_trial_count_exponent.exponent`
(`0.3186...`) — **matched exactly** (float equality, not merely within
tolerance).

**Check B — from-scratch reimplementation, not reuse of their code.** To
rule out a shared bug reproducing itself, I wrote my own leave-one-batch-out
jackknife (own `log2_A_k_scalar`, own `hist_of`, own loop over the 200
`linspace`-bounded batches) directly from the raw persisted
`stage1_per_trial_S` arrays, calling neither `matched_pair.py`'s
`matched_pair_stats()` nor `run_stage1()`. Result at stage 1 pooled, k=17:
`diff=0.0515673502`, `SE_paired=0.0966240611`, `z=0.533691` — matching the
committed record to 10 decimal places. I did the same for stage 2 using the
persisted per-shard `S_histogram_{true,defected}` arrays (raw per-trial S is
not persisted for stage 2, disclosed as `protocol_deviations`), confirming
histogram-additivity (`sum of 4 per-shard histograms == pooled histogram`,
exact) and the pooled point diff (`0.1147925209`, exact match).

**Check C — pooling-legitimacy control, computed both ways.** To test the
handoff's specific concern ("`log2_A_k` is a nonlinear function of the
histograms"), I computed the stage-1 pooled diff **two ways**: (i) the
naive, biased way — average the two shards' already-nonlinear point
estimates (`0.5*(0.101778 + 0.010823) = 0.056301`); (ii) the way the code
actually does it — sum the raw histograms first, then apply
`log2_A_from_hists` **once** to the combined histogram (`0.051567`). These
differ by `0.004733` (~9% of the point estimate at this T), which is exactly
the nonlinearity-induced bias the naive method would introduce — **and
confirms the executor's code uses the correct, unbiased method (ii)**, not
the naive one. `matched_pair.py`'s reported pooled diff matches (ii) exactly.

This is a materially stronger check than the prior batch's reviews performed
(which read code and ran independent probes on fresh data, but did not
re-execute the artifact under review end-to-end against its own committed
output).

---

## 1. Is stage 1's reconstruction genuinely zero-entropy, or did it silently draw new randomness?

This was the handoff's sharpest instruction, because the bit-identity gate
only checks two of the four stage-1 arms (shard 5000's **defected** decode
against the pilot's committed defected histogram; shard 6000's **true**
decode against the pilot's committed undefected histogram) — the two
**crossed** arms that are the actual matched-pair data (shard 5000 true,
shard 6000 defected) have no external committed reference of their own.

**I do not read this as a live defect, for a specific, checkable reason: the
architecture makes the crossed arms inherit the gate's validation, not
merely assume it.** Verified by direct reading of the sha256-pinned source
(not asserted from `design.md`'s prose):

- `dual_decode_shard()` (matched_pair.py:244-324) generates the batch's
  `bits` array **once**, then calls `decode_a(bits, ...)` and
  `decode_b(bits, ...)` back-to-back on the literal same array object
  (lines 309-310), before any other operation touches it.
- `decode_blocks` (`stage_a.py:286-307`) is **provably non-mutating**: it
  only reads `bits` (`blk = bits.reshape(...)`, `.sum()`, `wht128()`) and
  returns new arrays; it never writes into its input.
- The defected wrapper (`make_defected_decode_blocks`, matched_pair.py:200-226)
  takes its own defensive copy (`b = bits.copy()`) before perturbing it, so
  it cannot mutate the shared `bits` array either.
- Consequently, for shard 5000: `S_a` (true, the crossed arm) and `S_b`
  (defected, the gate-checked arm) are decoded from the identical in-memory
  bit array in the same loop iteration — there is no code path by which the
  crossed arm could have come from a different generation than the
  gate-validated arm. The same argument applies symmetrically to shard 6000.
- I additionally diffed `dual_decode_shard`'s generation body
  (matched_pair.py:264-313) against `stage_a.py`'s own `_t_shard`
  (`stage_a.py:496-542`) line-by-line: identical `key = sha_key(ps_id, "T",
  shard, MASTER_SEED)` derivation, identical `CTRStream`/`fixed_weight_support`
  call order and byte-string domain separators (`b"v0".."v4"`), identical D2/D3
  checks, identical `buf`/`unpackbits` construction — a byte-identical copy,
  as claimed, not merely a similar-looking reimplementation.
- **Batch size, specifically named by the handoff as a suspect mechanism**:
  `matched_pair.py`'s `BATCH = 64` is literally identical to
  `pilot_injection.py`'s own `BATCH = 64` (verified by grep against both
  files). This is also immaterial even if it had differed, because
  `decode_blocks` operates row-independently on its `(B, n_e, n_2)` reshape
  — no cross-trial coupling exists within a batch, so a different batch size
  cannot change any individual trial's decoded outcome, only how many trials
  are vectorized per `decode_blocks` call.
- **Re-keyed stream, specifically named by the handoff**: the key derivation
  formula is identical (`sha_key(ps["id"], "T", shard, MASTER_SEED)`,
  byte-for-byte), and `MASTER_SEED` is stage_a.py's own module constant,
  reused unmodified. Not re-keyed.
- **Reordered loop, specifically named by the handoff**: the per-trial
  operation sequence (`sx, sy, s1, s2, se` → D2 check → `epp`/`et` → D3
  check → `buf[i]`) is in the identical order in both files. Not reordered.

And Check A above (§0) supplies the strongest possible empirical
corroboration: an independent re-execution, on a **third** machine/OS/Python/
numpy combination distinct from both the pilot's and the executor's, of the
actual committed script reproduces every statistical quantity — including
both crossed arms — to full float precision. Combined with the
determinism gate itself passing across the pilot's Linux/Python-3.11 and the
executor's macOS/Python-3.13 environments (`run_manifest.yaml`
`environment_deviation_from_pilot`), this is now a **three-environment**
agreement on bit-identical output, not a single self-consistent run.

**Verdict on this concern: adequately discharged**, by code-level proof (no
mutation is possible between `decode_a`/`decode_b`, so the gate-checked arm
and the crossed arm on the same shard are provably co-generated) plus
independent cross-environment reproduction. I looked specifically for the
three named failure modes (re-keyed stream, changed batch size, reordered
loop) and found none of them present, and the batch-size question is doubly
closed since it wouldn't have mattered even if present. This is a case where
the concern the handoff raised was a legitimate one to check and does not
survive the check — stated plainly per the red-team charter's instruction to
preserve the narrowest valid conclusion when an objection fails, not to
manufacture a finding where the evidence refutes it.

---

## 2. Is pooling shard 5000 + shard 6000 into T=10,000 legitimate, given the nonlinearity?

**Yes, as implemented** — verified quantitatively in §0 Check C, not merely
argued. `log2_A_from_hists` (`measure.py:225-246`) is a pure function of a
histogram array; pooling by concatenating the raw per-trial `S` values (or
equivalently, summing the two shards' histograms — verified exactly equal,
§0 Check B) before applying the nonlinear transform **once** is the
textbook-correct way to combine independent samples for this class of
estimator, because the histogram is the sufficient statistic and pooling at
that level preserves it. I quantified what the *wrong* method (averaging two
already-nonlinear per-shard point estimates) would have produced instead —
`0.056301` versus the correct `0.051567`, a `0.0047` (~9%) bias at this T —
to make the nonlinearity concern concrete rather than hypothetical, and
confirmed the executor's actual code takes the unbiased path.

**One residual caution, not a defect in the pooling itself**: pooling
assumes the two shards are exchangeable draws from the same distribution.
The measured per-shard point estimates at k=17 disagree substantially
(shard 5000: `diff=+0.1018`, `z=0.814`; shard 6000: `diff=+0.0108`,
`z=0.072`) — an order-of-magnitude difference in point estimate, though
both are within noise of each other given their individual SEs (`0.125`,
`0.150`). This is not evidence against pooling (the between-batch jackknife
SE, which spans both shards' batches, does pick up this heterogeneity and
inflate the reported SE accordingly — a batch drawn from either shard
contributes to the leave-one-out variance), but it is worth carrying
forward: at stage 2 the heterogeneity across the four fresh shards is much
larger still (§3), and a pooling design that averages over that much
per-shard variance needs the between-shard heterogeneity itself
characterized before trusting the pooled SE's asymptotic behavior — which is
exactly what the next action below recommends.

---

## 3. Was the branch that fired actually reachable — and did stage 2 inherit stage 1's known defect?

This is the central finding of this review.

### 3.1 The raw numbers land in Branch C1 — but the supersession clause fires instead

At stage 2 (primary evaluation, k=17, pooled over shards 8000-8003,
`T2=20,000`): `diff=+0.11479`, `SE_paired=0.08841`, `z=1.2985`.

- `|z| = 1.2985 < 1.96` → Branch A (DETECTED) does **not** fire.
- `|diff| + 1.96*SE = 0.1148 + 0.1733 = 0.2881 ≥ 0.19` → Branch B (null
  excluding 0.19) does **not** fire.
- `|diff| = 0.1148 ≥ 0.10`, sign positive and consistent with stage 1's
  pooled sign (also positive, `+0.0516`) → **by the raw arithmetic, Branch
  C1 fires** ("one further matched-pair extension sized for delta = the
  observed |diff| at z=2.80, capped at 2.0e5 trials").

But `DEC-20260809-46e85c` and `task_card.yaml` both state, in identical
substance: *"The fitted SE-versus-T exponent SUPERSEDES A/B/C if it falls
outside [0.4, 0.6]"* — and the measured, independently-reproduced (§0)
exponent is `0.3186`, outside that band. **Per the rule's own text, this
supersedes Branch C1.** The disposition the rule actually specifies is: *"the
derivation's own modeling assumption is refuted, every required-T figure in
EV-HQC-dd85c1 O5 is downgraded to resting on a refuted assumption, and the
next action is a scaling-characterization task before any further sizing"* —
not a further matched-pair extension sized off the now-suspect required-T
formula.

I checked branches D and E too, for completeness: D (invalid/infrastructure)
does not fire — the determinism gate passed, D2/D3 report 0 violations on
20,000 stage-2 trials × 2 decode variants (independently reproduced, §0),
and stage 2 achieved its full planned T2 with no truncation. E (anomaly,
stage 1's two shards disagreeing in sign at `|z|≥1.96` each) does not fire
either — both stage-1 shards are positive (`z=0.814`, `z=0.072`), neither
individually significant.

**This is the single most important thing for the next Coordinator decision
to get right.** If the ledger archive reads stage 2's z/diff at face value
and dispatches a C1-style sized extension (even though its own inputs —
diff at z=2.80 — are legitimate numbers to reuse), that would apply a branch
the pre-registered rule's own supersession clause explicitly overrides. I
raise this as a **finding for the record**, not an instruction — applying
the branch rule is the Coordinator's act, not mine, and I hold no authority
to do it here.

### 3.2 Did stage 2 inherit stage 1's "Branch B is unreachable" defect?

`DEC-20260809-46e85c` states, as a **structural, outcome-independent**
fact, that stage 1 alone cannot reach an effect-excluding null: its pooled
minimum-detectable-effect (~0.275) exceeds both prior point estimates
(0.1922, 0.2069) "no matter what it observes." I checked whether stage 2, as
actually sized and run, escaped that same structural bind — and the answer,
while not as clean a structural guarantee (it depends on realized numbers,
not just the pre-registered design), is **largely no**.

Two things compounded against Branch B specifically:

1. **`T2` landed at the floor, not the value `design.md`'s own "why this
   size" narrative was written against.** `design.md` §3 and the task card
   argued that "at T2 of order 3.9e4... a null whose interval excludes
   0.19 becomes reachable." But `T2` is a function of stage 1's *measured*
   pooled SE (`0.09662`), which came in well below what the campaign had
   assumed going in (the Red Team's `0.1982` at T=5,000, extrapolated to
   `~0.140` at T=10,000 under 1/sqrt(T)). Plugging the *smaller* measured SE
   into the pre-registered formula gives `T2_raw = 18,299`, below the floor
   of 20,000 — so the clamp bound, not the "why this size" target of ~3.9e4,
   is what actually ran. I verified this substitution independently from
   the committed formula and inputs (§0) and it is arithmetically correct;
   the issue is not an error, it is that the design's own narrative
   assumed an SE input that stage 1 itself falsified before stage 2 ran.
2. **The realized SE decay from T=10,000→20,000 was slower than 1/sqrt(T)**
   (that is precisely the anomaly in §3.1) — `SE(20000)=0.08841` versus the
   `~0.0683` that 1/sqrt(T) scaling from `SE(10000)=0.09662` would predict.

I projected forward using the *measured* exponent (0.3186) and the
*currently observed* diff (0.1148, holding it fixed as a working
assumption — clearly stated as such) to ask whether Branch B was reachable
anywhere within this batch's own pre-registered `T2` range or even the
*next* batch's separately-capped C1 extension:

```
at T=60,000 (top of THIS batch's own [20000,60000] clamp range):
  projected SE = 0.06230,  |diff| + 1.96*SE = 0.2369   (need < 0.19)
at T=200,000 (C1's own, LATER, separately-authorized cap):
  projected SE = 0.04245,  |diff| + 1.96*SE = 0.1980   (need < 0.19, misses by 0.008)
```

**Under the exponent and diff actually measured, Branch B looks essentially
unreachable within this batch's own cap, and only marginally reachable at
the very top of a *later* batch's separate, larger cap.** I state this
carefully: unlike `DEC-20260809-46e85c`'s stage-1 claim, this is not a
provable, outcome-independent structural guarantee — it is a projection
built from this run's own point estimates, which carry their own sampling
noise (particularly the fitted exponent itself; see §5). But it is a
directly analogous concern to the one the Coordinator already conceded for
stage 1, evidenced with the same rigor the campaign has applied elsewhere,
and it should be weighed the same way: a design whose null branch is very
hard to reach is not calibrated to answer the question, symmetric to the
concern that a design with no positive-control history is not calibrated to
answer "yes" either.

---

## 4. The 2.78x unpaired-to-paired SE ratio: reproduced or refuted?

**Reproduced in magnitude and direction; not, and should not be expected to
be, reproduced as the identical decimal.** The original `2.78x` came from
the BATCH-2ecaa1 Red Team's own fresh-shard probe (shard `424242`,
T=5,000). This batch's stage 1 is a *different* sample (the pilot's own
shards 5000/6000, reconstructed) and measures:

```
shard 5000 (T=5,000):  ratio = 2.902
shard 6000 (T=5,000):  ratio = 3.224
pooled     (T=10,000): ratio = 3.117
stage 2 pooled (T=20,000): ratio = 3.769
```

All four are independently recomputed and verified exactly against the
reported values (§0 Checks A-B), and all land within the same order of
magnitude as `2.78x` — supporting the qualitative finding (matched-pair
design gives several-fold tighter SEs than the between-shard design at
k=17) robustly, across four independent measurements now, not one. The
literal digits should not match, and don't; a match to the exact decimal
would itself be suspicious for an estimate carrying its own sampling
variance. **This is a genuine first independent replication of the
class of finding EV-HQC-dd85c1 O8 flagged as resting on one unreplicated
source** — the general magnitude is now corroborated by data the original
probe's author (the BATCH-2ecaa1 Red Team) did not generate.

---

## 5. Was the exponent-refutation itself adequately powered? A caution on over-reading it.

The supersession finding in §3.1 is real (the pre-registered rule's own
criterion fired, on independently-reproduced numbers), and I do not
recommend overriding it. But I flag, for the scaling-characterization task
the rule itself calls for, that the exponent estimate resting on just three
points is fragile in ways worth naming explicitly:

- **Two of the three fitted points are not independent replications.** The
  `T=5,000` point is the mean of the two stage-1 per-shard SEs, and the
  `T=10,000` point is the pooled SE computed on the *concatenation of those
  same two shards*. These are not two independent T=5,000 and T=10,000
  experiments; they are the same 10,000 trials sliced two ways. Only the
  `T=T2=20,000` point (stage 2, fresh shards) is a genuinely independent
  draw. A 3-point log-log OLS fit with two correlated points and no
  confidence interval reported on the slope is a weak basis for a
  binary in/out-of-band verdict, and the rule as pre-registered does not
  ask for one — worth flagging for the follow-up task rather than for this
  batch's own disposition.
- **Per-shard SE at fixed T=5,000 is itself far more heterogeneous than the
  two stage-1 shards alone suggested.** Stage 2's four fresh shards at
  T=5,000 each show paired SEs of `0.271, 0.019, 0.019, 0.080` at k=17 — a
  **~14x range** across shards of identical size, with correspondingly wild
  per-shard diffs (`+0.306, -0.020, +0.002, +0.074`; one shard, 8000, is
  individually the largest contributor to the whole pooled effect). This
  order-of-magnitude shard-to-shard SE variability, revealed only by stage
  2's four shards (stage 1's two shards, `0.125`/`0.150`, looked much more
  consistent and would not have exposed this on their own), means the
  `T=5,000` anchor point in the exponent fit could have come out very
  differently under a different pair of shards — which weakens confidence
  in the specific exponent value, though not in the qualitative finding
  that *something* about the 1/sqrt(T) assumption merits closer
  characterization before further sizing decisions rest on it.

Neither point argues the supersession should be ignored — the rule fired on
its own pre-registered terms, on numbers I independently verified — but both
argue that "exponent = 0.3186, 1/sqrt(T) refuted" should be carried forward
with the same epistemic hedge EV-HQC-dd85c1 O8 applied to the original
`SE_paired = 0.1982` figure: a real, disclosed, first-look measurement, not
yet a settled fact.

---

## 6. Is my standing objection (TASK-20260806-92aecb) retired?

**No.** The objection was: *"No batch in this six-batch campaign… has ever
produced a POSITIVE (fired/significant) result from a real-sampler injection
through the full detection pipeline… A null from a pipeline with no track
record of ever detecting anything it was pointed at is weaker evidence than
a null from one with a demonstrated positive control."* `DEC-20260809-46e85c`
itself states this is retired only if Branch A fires. It did not: `|z| =
1.298 < 1.96` at the pre-registered primary evaluation (stage 2, k=17). No
positive-control run (V1 or any less-diluted injection point) has been
executed anywhere in this campaign's committed record either — it remains
sequenced for "the immediately following batch," per `DEC-20260809-46e85c`'s
own binding commitment, not yet dispatched as of this review.

What has changed, and is worth recording precisely rather than folded into
either "retired" or "unchanged": every independent matched-pair-quality
measurement of this exact cell, in chronological order, has landed
progressively closer to significance and with a stable sign — pilot
between-shard `z=-0.466` (T=5,000, an outlier by design flaw, per EV-HQC-dd85c1
O4), Validator between-shard `z=+0.613` (T=2,000), original Red Team
matched-pair probe `z=+0.970` (T=5,000, fresh shard), this batch's stage 1
`z=+0.534` (T=10,000, reconstructed), this batch's stage 2 `z=+1.298`
(T=20,000, fresh shards) — the last four are all positive, and z is rising
with T in a pattern consistent with, though not yet proof of, a small real
effect around the `0.1-0.12` region the two most recent (least noisy)
matched-pair measurements now agree on. This is a legitimate reason to keep
running the design, not a reason to call the standing objection retired: a
rising-but-not-yet-significant trend on the diluted V3 point is a different
question from whether the pipeline has ever shown it can ring on a
known-present, less-diluted defect, and the latter still has zero
occurrences in this campaign's record.

---

## 7. ADMIT / DO-NOT-ADMIT verdict

**ADMIT** the artifacts as an honest, reproducible, and — on the specific
concerns this batch's handoff named — largely vindicated record.

- Every reported statistical quantity I attempted to reproduce, reproduced
  exactly, via two independent methods (full script re-execution on a third
  environment, and a from-scratch reimplementation of the jackknife
  formula) — a standard of verification stronger than either prior
  BATCH-2ecaa1 review or this task's own artifacts individually supply.
- The "zero new entropy" claim for the crossed arms, which the handoff
  correctly flagged as unverified by the bit-identity gate alone, is
  discharged by a code-level proof (no mutation is possible between the two
  decode calls sharing one generation pass) plus three-environment
  cross-reproduction — not merely asserted.
- The pooling method is the textbook-correct one for this nonlinear
  estimator, verified by direct comparison against the biased alternative.
- Two real anomalies are disclosed, not smoothed over, exactly as
  AGENTS.md rule 8 requires: the out-of-band exponent, and (newly
  identified by stage 2's four shards, not disclosed as such in the
  executor's own report) the ~14x per-shard SE heterogeneity at fixed T.
- Scope discipline is clean: 10.3 of 400 authorized core-seconds, no file
  outside `write_scope` touched (independently confirmed via the
  `path_sha256` content check in §0), claim tier held at toy throughout.

**What ADMIT does not mean**: it does not mean the pre-registered branch
rule has been correctly applied yet — that is a Coordinator act that has
not happened as of this review (`TASK-20260809-5c78b2` remains `queued`),
and §3.1 is written specifically so that act does not default to Branch C1
without addressing the supersession clause first.

---

## 8. Structured summary

```yaml
red_team_report:
  id: RT-20260809-47a5ec
  task_id: TASK-20260809-47a5ec
  claim_under_review: >-
    TASK-20260809-a79e4f's matched-pair reconstruction (stage 1, zero-new-
    entropy replay of the pilot's own committed shards 5000/6000) and
    extension (stage 2, fresh shards 8000-8003, T2=20,000 sized by the
    pre-registered clamp formula), reported as observations for
    DEC-20260809-46e85c's pre-registered branch rule to be applied against,
    at the primary cell k=m=17.
  objections:
    - "The raw stage-2 numbers (z=1.2985, diff=0.1148, sign consistent with
      stage 1) satisfy Branch C1's stated conditions, but the pre-registered
      SE-vs-T exponent (0.3186, independently reproduced exactly) falls
      outside the [0.4,0.6] band that DEC-20260809-46e85c and task_card.yaml
      both state SUPERSEDES branches A/B/C. The next Coordinator decision
      must resolve the supersession before applying C1's sized-extension
      next action, or it misapplies its own pre-registered rule."
    - "Stage 2's own realized T2 (20,000, the pre-registered floor) and the
      realized slower-than-1/sqrt(T) SE decay make Branch B (an
      effect-excluding null) appear very hard to reach within this batch's
      own [20000,60000] cap, and only marginally reachable at the very top
      of a later batch's separately-authorized 2.0e5 cap -- an empirical,
      outcome-dependent echo of the same structural defect
      DEC-20260809-46e85c already conceded for stage 1 alone, though not as
      strong a guarantee since it rests on the currently measured diff and
      exponent holding."
    - "The fitted SE-vs-T exponent rests on three points, two of which
      (T=5,000 and T=10,000) are not independent replications -- the
      T=10,000 point is the pooled recombination of the same two shards
      used for the T=5,000 point -- and stage 2's four fresh shards reveal
      ~14x per-shard SE heterogeneity at fixed T=5,000 that the two
      stage-1 shards alone did not expose. The out-of-band verdict is real
      on its own pre-registered terms but should be carried forward with
      the same 'first look, not yet replicated' hedge EV-HQC-dd85c1 O8
      applied to the original SE figure, not treated as a settled scaling
      law."
    - "No positive-control run has yet been executed anywhere in this
      six-plus-batch campaign; V1 remains sequenced for the 'immediately
      following batch' per DEC-20260809-46e85c's own binding commitment,
      not yet dispatched. My BATCH-2ecaa1 standing objection is therefore
      unretired, and this batch's rising-but-short-of-significance z trend
      (z=0.534 at T=10,000, z=1.298 at T=20,000) is a reason to keep running
      the design, not a substitute for the missing positive control."
  required_controls:
    - "Before any further T-sizing decision reusing DEC-20260809-46e85c's
      required-T derivation: run the scaling-characterization task the
      rule's own supersession clause calls for -- ideally with INDEPENDENT
      (non-nested) samples at each T level, given the current fit's two
      correlated points, and report the exponent's own confidence interval
      rather than a bare point estimate."
    - "Dispatch the V1 positive-control pilot DEC-20260809-46e85c already
      committed to for 'the immediately following batch' -- this remains
      the only control that can distinguish 'this pipeline can never ring'
      from 'the V3/k=17 cell's true effect is small and this design is
      slowly closing in on it', and six-plus batches of rising-but-
      short-of-significance z scores do not substitute for it."
    - "Characterize the per-shard SE heterogeneity at fixed T (0.019 to
      0.271 across stage 2's four shards at k=17, T=5,000 each) before
      trusting pooled-SE asymptotics at this estimator's nonlinearity --
      it is plausible, not yet established, that this heterogeneity is a
      contributor to the sub-1/sqrt(T) exponent."
  counterexample_or_mutation: >-
    None found for the mechanism itself. I specifically tested for the
    three failure modes the handoff named (re-keyed stream, changed batch
    size, reordered loop) by diffing dual_decode_shard's generation body
    against stage_a.py's own _t_shard line-by-line, confirming BATCH=64 is
    unchanged from pilot_injection.py, and proving decode_blocks and the
    defected wrapper cannot mutate the shared bits array between the two
    decode calls -- none were present, and batch size would have been
    immaterial even if changed. Independently re-executing the committed
    script on a third machine/OS/Python/numpy combination (distinct from
    both the pilot's and executor's environments) reproduced every
    statistical quantity to full float precision, and a from-scratch
    reimplementation of the jackknife SE (not reusing the executor's
    matched_pair_stats function) matched to 10 decimal places. The mutation
    I did find is in the DECISION LAYER, not the data: the pre-registered
    exponent-supersession clause fires on this batch's own numbers, and a
    naive reading of stage 2's z/diff alone would misapply Branch C1 instead.
  baseline_comparison: >-
    Not applicable in the Pollard-rho/BSGS/ECDLP sense -- this is an
    instrument-calibration measurement for an HQC decoding-correlation
    estimator, toy tier. The relevant comparison is within-design and
    within-campaign: this batch's paired/unpaired SE ratios (2.90x-3.77x
    across four independent measurements) corroborate, in magnitude and
    direction, the single previously-unreplicated 2.78x figure
    (EV-HQC-dd85c1 O8) that the whole required-T derivation rests on --
    genuinely replicated for the first time by an executor other than the
    original probe's author, not merely re-asserted.
  heuristic_challenges:
    - "The 1/sqrt(T) scaling assumption underlying every required-T figure
      in EV-HQC-dd85c1 O5 received its first empirical test in this batch
      and failed it (fitted exponent 0.3186, outside the pre-registered
      [0.4,0.6] band, independently reproduced exactly) -- but the test
      itself rests on only one truly independent point (T=T2) plus two
      correlated points from a single 10,000-trial pool, and stage 2's own
      shard-level SE heterogeneity (~14x at fixed T) suggests the anchor
      point could be noisy. The heuristic is falsified on its own
      pre-registered terms; whether it is falsified robustly is a separate,
      still-open question the next scaling-characterization task should
      settle with independent (non-nested) samples per T level."
  cost_model_challenges:
    - "T2 landed at the pre-registered floor (20,000) rather than the
      ~3.9e4 design.md's own 'why this size' narrative was written against,
      because stage 1's measured SE (0.0966) came in well below the value
      (~0.140) the narrative implicitly assumed. This is not a bug -- the
      substitution is arithmetically correct and independently reproduced
      -- but it means the stated rationale for why stage 2 would make both
      a detection and an effect-excluding null reachable no longer applies
      to the T2 that actually ran, and the report does not flag this
      mismatch between design intent and realized sizing."
    - "Total spend (10.295 core-seconds against 400 authorized, 9.439
      wall-seconds against 1,800) is honestly reported and independently
      corroborated by my own re-execution's comparable timings (~10.3
      core-seconds). No cost-model objection on the executor's own
      accounting."
  reduction_and_scope_challenges:
    - "Claim tier and scope statements (toy, PS-R3 only, V3/decode_blocks
      only, nothing about HQC's IND-CCA security or any standardized
      parameter set) are consistent throughout design.md, the results JSON,
      the report, and run_manifest.yaml, and I found no scope inflation
      anywhere in the artifact set."
  proof_architecture_challenges: []
  narrowest_supported_statement: >-
    The matched-pair reconstruction mechanism is sound: independently
    verified by full re-execution on a third environment and a from-scratch
    jackknife reimplementation, both matching the committed artifacts
    exactly, and the specific "silent new entropy" failure modes the
    handoff named (re-keyed stream, changed batch size, reordered loop) are
    demonstrably absent, with the crossed arms' validity following from a
    code-level non-mutation proof rather than an unverified assumption.
    Pooling is the statistically correct method for this nonlinear
    estimator, quantitatively distinguished here from the biased
    alternative. But the pre-registered decision rule's own
    exponent-supersession clause fired on this batch's numbers (exponent
    0.3186, outside [0.4,0.6]), which supersedes the Branch C1 disposition
    the raw z/diff numbers would otherwise suggest -- the next Coordinator
    decision must address this explicitly, not default to C1. Branch A did
    not fire (z=1.298 < 1.96), so my BATCH-2ecaa1 standing objection --
    this pipeline has never produced a fired cell from a known-present
    real-sampler defect -- is NOT retired, though the trend across four
    independent matched-pair-quality measurements (z rising from 0.534 to
    1.298 as T doubled, sign stable and positive) is a legitimate reason to
    keep investing in this design rather than a reason to treat the
    objection as answered.
  next_concrete_action: >-
    Before any further T-sizing decision: run the scaling-characterization
    task DEC-20260809-46e85c's own supersession clause calls for, using
    independent (non-nested) samples at each T level and reporting a
    confidence interval on the fitted exponent, not a bare point estimate --
    and separately, dispatch the V1 positive-control pilot
    DEC-20260809-46e85c already committed to for "the immediately following
    batch," which remains the only control in this campaign's record that
    could establish this pipeline can ever produce a fired cell from a
    known-present defect.
  artifact_paths:
    - coordination/goals/GOAL-HQC-001/batches/BATCH-412513/tasks/TASK-20260809-a79e4f/design.md
    - coordination/goals/GOAL-HQC-001/batches/BATCH-412513/tasks/TASK-20260809-a79e4f/matched_pair.py
    - coordination/goals/GOAL-HQC-001/batches/BATCH-412513/tasks/TASK-20260809-a79e4f/matched_pair_results.json
    - coordination/goals/GOAL-HQC-001/batches/BATCH-412513/tasks/TASK-20260809-a79e4f/matched_pair_report.md
    - coordination/goals/GOAL-HQC-001/batches/BATCH-412513/tasks/TASK-20260809-a79e4f/run_manifest.yaml
    - coordination/goals/GOAL-HQC-001/batches/BATCH-412513/archives/TASK-20260809-a87710/snapshot-receipt.json
    - ledger/decisions/DEC-20260809-46e85c.yaml
    - ledger/evidence/EV-HQC-dd85c1.yaml
    - coordination/goals/GOAL-HQC-001/batches/BATCH-2ecaa1/reviews/TASK-20260806-92aecb/red_team_report.md
    - coordination/goals/GOAL-HQC-001/batches/BATCH-6fddee/tasks/TASK-20260806-64b506/stage_a.py
    - coordination/goals/GOAL-HQC-001/batches/BATCH-0a65c0/tasks/TASK-20260806-cde749/measure.py
    - coordination/goals/GOAL-HQC-001/batches/BATCH-2ecaa1/tasks/TASK-20260806-77a574/pilot_results.json
```

*Red-team record. I wrote only inside this directory
(`coordination/goals/GOAL-HQC-001/batches/BATCH-412513/reviews/TASK-20260809-47a5ec/`).
All compute for this review ran against my own scratch output directory,
never against the task's own `write_scope`; every declared artifact's
`path_sha256` was independently re-verified against the live tree before
this review began. I hold no authority to change status and changed none —
the branch-supersession finding in §3.1 is reported for the Coordinator's
next act, not applied here. This is an independent session's judgement: I
did not coordinate with the concurrently-running Validator task
(`TASK-20260809-603dc5`) and did not read its `write_scope`.*
