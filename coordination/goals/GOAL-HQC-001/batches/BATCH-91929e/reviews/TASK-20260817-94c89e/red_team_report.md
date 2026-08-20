# red_team_report.md -- TASK-20260817-94c89e

Red Team review of **TASK-20260817-c603c0** at snapshot **9ac60648d**
(BATCH-91929e / GOAL-HQC-001 / EXP-HQC-982268).

**Independent session. I am not the producer. I committed nothing, changed no
record status, edited no producer artifact, and applied no reading rule.**
Claim tier stays **TOY**. H-HQC-18d1b4 stays **PROPOSED**. Nothing below bears
on HQC's IND-CCA security, its decoding-failure rate, assumption A17 or A5, or
any standardized parameter set.

**I reviewed my own lineage's prescription and I was harder on it for that
reason.** TASK-20260817-c603c0 executes, verbatim, the `next_concrete_action`
and `required_controls` of the prior Red Team report TASK-20260815-907c66. An
agent grading its own prescription is the failure mode this task card names.
My finding is that the prescription was executed faithfully and **the
prescription was partly wrong**: the parametric null object I asked for is
structurally the wrong object, and the *second* option in my own predecessor's
required_controls list ("or repeat the SAME (shard, transition) measurement
multiple times with genuinely disjoint fresh trial ranges") was the correct
one, was paid for by this very batch's design, and was not computed.

---

## 0. VERDICT

**`objections_material_to_conclusions` — the measurements are SOUND, the
framing under-claims a decisive result the batch already paid for, and the
frozen reading rule is structurally inevaluable on its own outcome.**

Separating soundness from meaning, as RT12 requires:

**SOUND.** I contest no reported number. I re-derived all four fresh local
exponents from the committed `se_paired` values to 1e-15 (§RT12.1); I
reproduced the executor's entire null ladder from the same pinned modules in
my own script and obtained the null 95% band **bit-identically**
(`[-1.0295584296, 1.7588760236]`, §RT6); every declared hash in the snapshot
receipt verifies against the snapshot tree in both directions (§RT0). The
notarization chain, the two disjointness proofs, the F-invariant, the module
pins and the budget accounting are all as claimed.

**MEANING — five material objections.**

1. **The confound is broken as designed and IMMEDIATELY REPLACED by a larger
   one the design did not name: the estimator's k-dependence.** At the family's
   load-bearing order k=17 the four fresh exponents are 2.05 / 2.96 / 0.32 /
   1.59. **At k=2 the identical four cells, identical windows, identical data,
   are 0.581 / 0.507 / 0.628 / 0.512 — all essentially the forced 0.5 — and
   the regime, shard and interaction contrasts are +0.095 / -0.026 / -0.042,
   i.e. all approximately zero.** The entire five-batch phenomenology (sign
   flips, "far outside [0.4,0.6]", shard heterogeneity, the regime confound)
   is a monotone function of k that is absent at low k and grows without bound
   toward k=n_e (§RT1.3, full table). This is derivable at **zero marginal
   cost** from `cross_regime_arms_results.json` alone and is not stated
   anywhere in the batch.
2. **The batch measured the real-object noise floor and did not report it.**
   Windows P2 and N1 are both T=10,000, same shard, same batch size 50, same
   procedure, disjoint index ranges. The paired SE at k=17 differs between them
   by **16.71x on shard 5000 and 3.72x on shard 8002** (§RT7). Since every
   alpha in this family is exactly `-log2(se_hi/se_lo)`, those gaps are 4.06
   and 1.89 *in alpha units*. The RMS is **3.17** — larger than the largest
   contrast reported (1.55), larger than the fresh spread (2.64), and
   comparable to the entire historical spread (3.702).
3. **The null object is the wrong object, and its band is 22% too narrow.**
   The executor's two arms are drawn from independent RNG streams; the real
   matched pair shares 55 of 56 blocks by construction (that is what the
   F-invariant gate proves). Measured: `unpaired_over_paired` is **0.9965** in
   the executor's null and **2.34–28.69** in the eight real cells. My paired
   null object (arms sharing 55/56 blocks, same law, true diff still 0) gives
   ratio 2.66–2.99 and a 95% band of width **3.398** against the executor's
   **2.788** (§RT3, §RT4).
4. **The anti-blindness leg COULD NOT HAVE FIRED, at any g.** The band
   requires a downward median displacement of 1.3366, i.e. rho >= **2.526**.
   I extended the pre-registered plant class past its pre-registered ceiling:
   rho_median is 1.141 / 1.167 / 1.346 at g = 1.25 / 1.5 / 2.0, then
   **reverses** to 1.038 at g=3, 0.828 at g=4, and saturates at ~0.85 through
   g=50 (§RT5). The class maxes out near rho ~ 1.35, a factor of 1.9 short of
   its own threshold, forever. The BLIND verdict is a fact about the plant, not
   about the instrument.
5. **The frozen four-branch rule is inevaluable on this outcome**, and the one
   contrast that would decide between two of its branches gets **opposite
   verdicts** depending on which of two candidate bands "the corresponding null
   band" means (§RT8).

**Not a closure.** Nothing here says this lane is dead, and I decline to say so.
The obstruction is *named and measured* (a 3.7x–16.7x within-(shard,T) spread
in `se_paired` at k=17 on disjoint real data), it is *localized* (it is a
k-dependent estimator breakdown, near-absent at k<=7), and the forward path is
concrete and nearly free. Per `docs/inventor-protocol.md` §4 that is what a
real obstruction looks like, and it is the opposite of a lane being closed.

---

## RT0. Notarization chain, re-verified in both directions

I did not accept the pre-dispatch verification. Using git plumbing in my own
isolated worktree (`claude/hqc-001-confound-20260817`, HEAD `44a53877e`):

| check | result |
| --- | --- |
| `git cat-file -t 9ac60648d` | `commit` |
| snapshot parent | `9c7dd452c` = "coord: open GOAL-HQC-001 BATCH-91929e", matches `parent_sha` |
| `git merge-base --is-ancestor 9ac60648d HEAD` | true |
| `git diff-tree -r 9ac60648d` | exactly 13 additions: the receipt + 12 producer artifacts, nothing else |
| `git diff-tree -r 9c7dd452c` | batch.yaml, dispatch_queue.json, 5 task cards, 5 handoffs — **the reading rule and the arm-assignment rationale are in the PARENT commit, before any producer artifact existed.** The freeze claim is verifiable and verified. |
| sha256 of all 12 declared paths, `git show 9ac60648d:<path>` | **12/12 match `path_sha256`**; all 12 also match the working tree byte-for-byte |
| receipt's own committed blob | sha256 `7941634d216073ac7b6b95ea6334868a4f47d2e098eca1e834a14c8d7a61cdbb` — exactly the value the receipt claims for itself; the working-tree copy differs (`2ea1c6dc…`) by the two fields the following bookkeeping commit `44a53877e` added, as disclosed |

**PASS, both directions.** No fabrication, no drift, no undeclared file.

**One provenance gap, with a zero-cost fix (OBJ-11).** The DEV-1
pre-registration anchor `7511ecc1698749156cf89c8c476b93d3baf7c35980a36d5812f21b21f7ba25e0`
is **not verifiable by anyone**, because the pre-fill `design.md` whose content
it hashes was overwritten and never committed. `stdout.log` line 3 says the
anchor makes pre-registration "auditable by content rather than by mtime"; as
delivered, the content it certifies no longer exists in the repository, so the
audit reduces to trusting the executor's own sequencing — which is what mtime
would have given. This is not a violation (the deviation was declared in
advance, and its scope — one calibrated constant that is by construction a
Part A output — is minimal and I have no reason to doubt it). It is a
one-line, zero-cost repair: commit the pre-fill file as a second artifact.

**Contract discrepancy I must flag rather than resolve.** My dispatch
orientation named `write_scope: .../red-team/TASK-20260817-94c89e/`. The
**committed** task card, the committed handoff, and the committed
`dispatch_queue.json` archive entry all name
`.../reviews/TASK-20260817-94c89e/` with the single artifact
`red_team_report.md`. I wrote to the committed path, since the committed
artifact is the contract and the archiver reads `artifact_paths`. I wrote
nothing else anywhere in the repository.

---

## RT1. IS THE CONFOUND BROKEN? — broken, then relocated twice

### RT1.1 The 2x2 does decouple shard from regime. Say so plainly.

Yes. Shard 5000 and shard 8002 are each measured at both the 25->50 and the
50->100 transition, in one procedure, on index ranges above both high-water
marks, with the design matrix full rank. The specific collinearity
BATCH-174014 named — every measurement having shard identity 100% aligned with
transition regime — **is gone**, and that is a real, verified structural
achievement. The window arithmetic, the high-water re-derivation (5000 -> 15000
from `matched_pair_repeat_results.json.n_total_per_call`, 8002 -> 30000 from
`shard_8001_8002_discard_prefix_results.json.n_total_per_call`, both re-read at
run time, `cross_regime_arms.py:286-308`) and the pairwise-disjointness
assertion (`cross_regime_arms.py:258-276`) all hold.

### RT1.2 A NEW collinearity was introduced, for free, and was avoidable for free

`cross_regime_arms.py:89-95` fixes the window order **identically for both
shards**: P1,P2 = `[30000:45000)`, N1,N2 = `[45000:75000)`. So in this design
**regime is now 100% collinear with position-within-call**, on both arms. The
producer's own limitation 3 states the shared `START_INDEX` but not this
consequence.

Is that collinearity *mechanistically* live? No — and I say so rather than
inflate it. Trials are index-keyed and deterministic through CTRStream (pure
SHA-256 counter mode; traced directly by BATCH-174014's Red Team, and
re-confirmed here by Arm A's bit-identical cross-machine prefix match). There
is no drift, no state, no time. "Position" is therefore not a mechanism; it is
**which particular 45,000 trials**, i.e. *sampling realization*.

That is precisely why it matters. The design has **four cells and zero
replicates**, so it has **zero degrees of freedom for error** — structurally
the same defect as the 2-point exponent it was built to interrogate. Its three
contrasts are uninterpretable without an external noise estimate, and Part B
was supposed to supply one. **The counterbalance that would have broken this
collinearity was free**: give shard 8002 the window order N,P (regime N at low
indices) and shard 5000 the order P,N. Zero extra decodes. It was not done and
is not discussed.

### RT1.3 The confound that actually survives, and that no one named: k

This is the finding. Recomputing the four cells at every k from the committed
per-k arrays (deterministic arithmetic, no sampling, no decoder):

```
 k | a(5000,P) a(5000,N) a(8002,P) a(8002,N) |  regime  shard  inter | same-T log2 gap (noise) 5000 / 8002 | null bias E log2 A_k
 2 |   +0.581    +0.507    +0.628    +0.512  |  +0.095 -0.026 -0.042 |    +0.061 /   +0.105                | -0.00007
 3 |   +0.608    +0.468    +0.632    +0.495  |  +0.138 -0.025 +0.003 |    +0.058 /   +0.107                | -0.00021
 5 |   +0.697    +0.455    +0.606    +0.493  |  +0.178 +0.027 +0.129 |    +0.116 /   +0.133                | -0.00067
 7 |   +0.812    +0.592    +0.577    +0.562  |  +0.117 +0.133 +0.205 |    +0.338 /   +0.246                | -0.00141
10 |   +1.051    +1.136    +0.576    +0.812  |  -0.160 +0.400 +0.152 |    +1.110 /   +0.616                | -0.00411
13 |   +1.425    +1.919    +0.567    +1.153  |  -0.540 +0.812 +0.092 |    +2.283 /   +1.129                | -0.01504
17 |   +2.049    +2.961    +0.324    +1.594  |  -1.091 +1.546 +0.359 |    +4.063 /   +1.895                | -0.10164
20 |   +2.537    +3.517    -0.027    +1.833  |  -1.420 +2.124 +0.880 |    +5.325 /   +2.570                | -0.37583
23 |   +3.092    +3.826    -0.092    +2.352  |  -1.589 +2.329 +1.710 |    +6.479 /   +3.613                | -1.10980
26 |   +3.943    +4.022    +0.347    +3.860  |  -1.796 +1.879 +3.435 |    +7.652 /   +5.322                | -2.71938
```

(k=17 row reproduces the producer's headline exactly: 2.0488 / 2.9607 / 0.3236
/ 1.5943 and contrasts -1.0913 / +1.5458 / +0.3588. The last column is the
producer's own Forced Value 1, `null_object_control_results.json ->
ladder_rungs.10000.forced_value_1_log2_A_k_vs_zero.arm0_mean_by_k`.)

Read the k=2 row against the k=17 row. **Same data. Same windows. Same shards.
Same regimes. Same estimator.** At k=2 every cell sits at the forced 0.5, every
contrast is zero, and the same-T noise handle is 0.06–0.11. At k=17 the cells
span 2.6, the contrasts reach 1.55, and the noise handle is 1.9–4.1. The
producer's own null-object bias in `log2 A_k` first exceeds 0.01 at **k=13**
and is 7e-5 at k=2.

**Applying the inventor-protocol §3 discipline to this campaign's own signal:
name the parameter that should destroy it, and check.** Here the parameter is
k, and everything the family has reported grows monotonically with it,
tracking the estimator's own measured breakdown, while vanishing where the
estimator is measured to be exact. That is the artifact tell.

Mechanism, stated as a hypothesis and not as a result: `log2_A_from_hists`
(`measure.py:225-246`) forms `sum_s C(s,k) H_s`. For k=17 with mean S=17.88,
`C(s,17)` rises so steeply in s that the numerator is carried by a thin right
tail of high-S trials. The *effective* sample size for the k=17 estimand is
therefore a small fraction of T, so the `T^(-1/2)` reference law is being
applied with the wrong denominator, and a leave-one-batch-out jackknife over
200 batches inherits that tail's instability. That predicts exactly what is
observed: a 16.7x swing in `se_paired` between two disjoint T=10,000 windows at
k=17, and none at k=2.

**Verdict on RT1: the shard/regime confound is BROKEN. It has been replaced by
(a) a benign but zero-df regime/position collinearity that was free to avoid,
and (b) a k-dependent estimator confound that is larger than the one that was
broken and that no artifact in this batch names.**

---

## RT2. TRACE THE CODE, NOT THE ARGUMENT

Traced, not skimmed. What the code actually does, where it differs from the
design document, and what it hides.

**Window slicing** (`cross_regime_arms.py:552-556, 720-744`). Four analysis
calls, one per (shard, variant), n=75,000. `S[(shard,variant)] = r["F"].sum(axis=1)`
over the full 75,000, then `Sd = S[...][a:b]` per window. The pairwise
disjointness / above-prefix / union assertions (lines 258-276) are computed on
the WINDOWS constant, before any data, and fail-closed. Correct.

**Arm A direct proof** (lines 559-598). `S[(5000,variant)][:5000]` vs
`prior1["stage_1"]["per_trial_S"]["shard_5000_<variant>"]`, `np.array_equal`,
plus `sa.hist_of` equality. This is genuinely cross-run/cross-process/
cross-machine/cross-platform (Linux x86_64 CPython 3.11 -> macOS arm64 CPython
3.13) and it **passed**. It also silently establishes something the report does
not claim: trial indexing is independent of `n_trials`, so the 300-trial warmup
in `mp.run_arm` (`matched_pair.py:319-326`) does not consume or shift the
indexed stream.

**Arm B adapted proof** (lines 452-505, 600-614). Step 1 compares recomputed
`matched_pair_stats` against committed derived stats at exact float64
bit-identity — `tolerance_fallback_fired: false`, `max_rel = 0.0`, so the 1e-9
fallback never fired and the disclosed environment difference cost nothing.
Step 2 compares the 75,000-call prefix to the in-process verification call.
Both passed.

**What both proofs actually prove, which the report overstates by a word.**
Both certify a **prefix** (`[0:5000)` for Arm A, `[0:10000)` for Arm B). The
data the statistics are computed on is `[30000:75000)` and is verified against
nothing external, on either arm. The step from "the prefix reproduces" to "the
retained windows are fresh and disjoint" is an **inference from stream
determinism** — well-founded, given CTRStream, but an inference. The honest
label is *prefix-verified, windows determinism-inferred*, not "disjointness
proof". Cost of upgrading it to a proof: **zero** — persist the retained
per-trial S arrays and the next task's prefix check covers the retained range
directly.

**Latent silent-degradation path, checked and clear for this batch.**
`matched_pair.py:269-272`: `jack_se` uses `np.nanmean`/`np.nansum` but divides
by `b = vals.shape[0]`, the *row count*, not the non-NaN count.
`log2_A_from_hists` returns NaN wherever `mu <= 0` (`measure.py:241-245`). A k
with NaN leave-one-out rows would therefore return a **silently deflated**
`se_paired`, and a deflated `se_lo` or `se_hi` maps directly into alpha. Not
triggered here: `evaluable_k` is 2..26 in all eight real cells and identical
across all 200 replicates at all four null rungs, and every reported
`se_paired` is finite and positive. **Reported as checked-and-clear, and named
because nothing in the pipeline would announce it if it were not.**

**One-call-vs-two-call check** (lines 674-713). Genuine: it compares
`sa.batch_hists` on a slice view against a standalone `np.array` copy, 32/32,
and confirms `np.linspace(0,T,201).astype(int)` gives exactly-equal widths.
It shows the batch *structure* is identical. It cannot show procedural
identity, and the executor names that limitation regardless of outcome, which
is the right discipline.

**Where a code trace refutes a report sentence.** `null_object_control.py:508-514`
— see RT5.2. The "forced identity" is an algebraic tautology.

---

## RT3. ATTACK THE NULL OBJECT HARDEST

**Are the three values forced by mathematics or by construction?** Split.

**Forced Value 1 (`log2 A_k = 0` at every k) is a theorem that the pipeline
FAILS, and the failure is the most informative measurement in Part B.** The
producer reports it (report §3.1) and offers no interpretation, as its role
boundary requires. Measured mean at k=17: -0.1441 / -0.1016 / -0.0266 /
-0.0476 across T = 5,000 / 10,000 / 20,000 / 40,000; at k=26, -3.36 / -2.72 /
-1.93 / -1.73; at k=2, 3e-5 to 7e-5. Max absolute per-replicate deviation
4.6–9.1. So the null **did** catch a defect class — a strongly k-dependent,
weakly T-dependent bias in `log2_A_from_hists` — which is exactly the
"decoder-free mechanism that could produce the entire observed confound"
that design.md §3.4 pre-registered as the thing to look for. It found it, and
the batch does not connect it to §RT1.3's k-table. **This is under-claiming a
real finding.**

**Forced Value 2 (paired diff = 0) is forced by construction and would survive
most defects.** Both arms are i.i.d. draws from one law fed through a symmetric
estimator, so `E[diff] = 0` holds by exchangeability of the two arms
*regardless of whether `log2_A_from_hists` is correct*. Any bug that acts
identically on both arms — and a batch-size-dependent bias is exactly such a
bug — cancels exactly. Forced Value 1 is the only leg with discriminating
power, and it is the leg the design describes as diagnostic and the report
declines to read.

**Forced Value 3 (alpha = 0.5) is NOT attained, by 9 sigma, and the
pre-registered excuse is falsified by the producer's own data.** The full-ladder
fit returns alpha = **0.35133** with SD 0.23433 over R=200, i.e. SE 0.01657, so
**z = -8.97** against the forced 0.5. design.md §3.4 pre-committed the excuse:
"the `T^(-1/2)` law is exact only asymptotically, with an `O(T^(-1))` finite-T
correction." **That excuse makes a prediction: |0.5 - alpha| must fall by
roughly 4x across the ladder's 8x range in T.** Measured, from the producer's
own three rung pairs:

| rung pair | mean alpha | \|0.5 - mean\| | SE of mean | z vs 0.5 |
| --- | --- | --- | --- | --- |
| 5000->10000 | 0.353852 | 0.146148 | 0.056558 | -2.58 |
| 10000->20000 | 0.332199 | 0.167801 | 0.049545 | -3.39 |
| 20000->40000 | 0.374306 | 0.125694 | 0.048391 | -2.60 |

**Flat.** It does not decay; it is not even monotone. **A quantity that stays
flat when it should decay is the canonical artifact tell
(`docs/inventor-protocol.md` §3)** — and here the tell is fired by the *control's
own forced value*, against an excuse that was pre-registered before the data
existed. The correct reading is not "finite-T correction" but "with
`N_JACK_BATCHES` pinned at 200, this estimator's paired SE at k=17 scales as
`T^(-0.35)`, not `T^(-0.5)`, across 5,000–40,000." Every directional statement
in this family that used 0.5 as its reference point used the wrong reference
point.

**Would a defect in `log2_A_from_hists`, `evaluable_k` gating, or the jackknife
batching survive this null undetected?** `log2_A_from_hists`: partly — a
symmetric bias is invisible in FV2 and visible only in FV1, which is reported
but unread. `evaluable_k` gating: **yes, entirely undetected** — the null
object's histograms are Binomial(56, 0.319), so `evaluable_k` is 2..26 at every
rung and identical across all 200 replicates at all four rungs
(`evaluable_k_identical_across_all_replicates: true`, four for four). The gate
is never exercised near its `T_STAB_THRESHOLD = 30` boundary
(`stage_a.py:388-398`), so any defect in it is invisible by construction.
Jackknife batching: the NaN/row-count mismatch in `jack_se` (RT2) is likewise
never exercised. **Three of the pipeline's stages are traversed but not
tested.**

---

## RT4. DOES THE CALIBRATION TRANSFER? — no, for a nameable structural reason, and the objection is SCOPED not fatal

The producer names the *symptom* (limitation 4: null `se_paired` 0.34–0.71
versus real 0.017–0.282, "one to two orders of magnitude larger") and correctly
declines to assert transfer. It does not name the *mechanism*, and the
mechanism decides the question.

**`null_object_control.py:256-257`:**

```python
S0 = rng_for(T, r, 0, 0).binomial(n_e, p, size=T).astype(np.int64)
S1 = rng_for(T, r, 1, 0).binomial(n_e, p, size=T).astype(np.int64)
```

Two **independent** streams. The real matched pair is not independent — it is
maximally coupled. The V3 defect touches only block `n_e-1`, so the two real
arms share 55 of 56 blocks on every single trial. **That is exactly what the
F-invariant validity gate proves**: `F_defected[:, 0:n_e-1] ==
F_undefected[:, 0:n_e-1]`, 2,475,000 elements, 0 mismatches, all eight
(shard, window) cells. The batch proves the pairing is total and then
calibrates the *paired* estimator on an object with **no pairing at all**.

Measured, in my own probe:

| object | `unpaired_over_paired` at k=17 |
| --- | --- |
| executor's null, T=10,000 | mean **0.9965**, median 0.9916 |
| executor's null, T=20,000 | mean **0.9984**, median 0.9919 |
| the eight REAL fresh cells | **2.338, 5.604, 6.694, 6.843, 15.266, 15.662, 17.260, 28.691** |

In the executor's null the paired estimator **is** the unpaired estimator. The
pairing gain that defines the real instrument — 2.3x to 28.7x — is set to 1.
`se_paired` is never evaluated in the mode it is used in.

**The right null object, and what it changes.** I built the minimal correction:
`base ~ Binomial(55, p)`, `arm_i = base + Bernoulli_i(p)`. Both arms are still
exactly Binomial(56, p), the true diff is still identically 0, all three forced
values still hold — and the arms now share 55/56 blocks, as the real pair does.
Result:

| | executor's independent-arm null | red team's paired null |
| --- | --- | --- |
| `unpaired/paired`, T=10,000 | 0.9965 (median 0.9916) | **4.087 (median 2.985)** — in the real range |
| `se_paired` k=17, T=10,000 | 0.562720 | 0.165553 |
| alpha 95% band, 10000->20000 | [-1.02956, 1.75888], width **2.788** | [-1.40069, 1.99706], width **3.398** |
| mean alpha | 0.3322 | **0.2747** |

**The executor's band is 22% too narrow and its centre is 0.06 further from
0.5 than it should be.** Direction of the error matters and cuts asymmetrically
across the frozen rule: a *too-narrow* band makes "inside the band" harder and
"exceeds the band" easier, so the rule's branches that read an effect as REAL
by exceeding the band are **anti-conservative**, while the branch that reads
"inside the band" as noise is conservative. Given RT7's real-object noise scale
of 3.17, even my paired band's 3.398 is plausibly still too narrow for the real
arms.

**Fatal or scoped?** **Scoped, and repairable in seconds.** Part B's *method* is
right and its execution is exact; only the coupling of the object is wrong, and
correcting it is a four-line change with no decoder call (my probe's full run,
all five legs, took 9.35 s). It is not a reason to discard Part B. It is a
reason not to use its band as a yardstick for the real arms until the object is
corrected.

---

## RT5. FIFTH-INSTANCE TEST — YES, and I can state the invariance and the ceiling

**Yes. This is the fifth instance**, after CTRL-BS, CTRL-POSHOM, CTRL-IDXMAP
and BATCH-4b8ad3's planted arm. The producer says so too (report §3.6), and it
deserves credit for saying so unprompted. But the producer's account of *why*
is wrong in a way that matters, and the correct account is worse.

### RT5.1 The plant class saturates and reverses. The leg could not have fired.

The producer's blockquote reasons that "the planted departure WAS realized
(measured rho_g rose monotonically 1.134 -> 1.213 -> 1.392 with g) ... and the
resulting median shift in alpha was simply small against a null band roughly
2.79 wide." That frames the outcome as *instrument insensitivity*.

Arithmetic first. Unmodified median alpha at 10000->20000 is 0.30706; the band
floor is -1.02956. The required downward displacement is **1.3366**, i.e.
**rho >= 2.5256**. The largest pre-registered plant delivered rho = 1.346.

Then I extended the *same* pre-registered transform past its pre-registered
ceiling (same code, same seeds, R=200, T=20,000):

| g | 1.25 | 1.5 | 2.0 | **3.0** | **4.0** | **6.0** | **10.0** | **50.0** |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| rho (median) | 1.1414 | 1.1666 | 1.3462 | **1.0381** | **0.8275** | **0.8230** | **0.8532** | **0.8688** |
| alpha (median) | +0.1299 | +0.0594 | -0.1157 | +0.2798 | +0.7280 | +0.7387 | +0.6470 | +0.6417 |
| verdict | IN | IN | IN | IN | IN | IN | IN | IN |

`S_planted = clip(round(mu + g(S - mu)), 0, 56)` with mu = 17.877 on a
[0,56]-bounded variable **saturates to a near-two-point distribution** as g
grows, and the k=17 histogram functional's jackknife SE on that degenerate
object is *lower* than on the base. **rho is non-monotone in g, peaks around
g = 2 at ~1.35, and never approaches the 2.526 the band requires — at any g.**

**Therefore the BLIND verdict was structurally guaranteed by the choice of
plant class before any datum existed.** The three-point monotone rise the
report cites as proof the plant was realized is an artifact of sampling only
g <= 2; it reverses at the very next value. This is the fifth-instance pattern
stated with a mechanism and a measurement: *the boundedness that makes the null
object clean is the same boundedness that caps the plant below the detection
threshold.*

### RT5.2 The "forced identity" is a tautology and carries zero evidential weight

`null_object_control.py:508-514`:

```python
al_pl  = -(math.log(se_pl) - math.log(se17[10000][r])) / math.log(2.0)
al_un  = alpha_by_pair[(10000, 20000)][r]        # = -(log se20000 - log se10000)/log2
rg     = se_pl / se_un                            # se_un = se17[20000][r]
resid  = al_pl - (al_un - math.log2(rg))
```

Substituting: `al_un - log2(rg) = -(log se_hi - log se_lo)/log2 - (log se_pl -
log se_hi)/log2 = -(log se_pl - log se_lo)/log2 = al_pl`. The `se_hi` terms
cancel identically. **The residual is exactly zero for any positive `se_pl`
whatsoever.** I verified by feeding fictional values with no plant realized at
all:

```
se_planted = 0.31    -> residual 0.000e+00
se_planted = 1e-06   -> residual 0.000e+00
se_planted = 4321.0  -> residual 1.776e-15
```

The reported `6.217248937900877e-15` measures **float64 rounding**, nothing
else. The report's §3.6 blockquote offers it as one of two pieces of evidence
that "the planted departure WAS realized ... the forced identity linking it to
alpha held to 6e-15". It establishes nothing of the kind. The *only* evidence
of realization is the measured rho — and RT5.1 shows that evidence does not
survive extending the ladder by one step. **This is the one place in the batch
where a stated verification is not a verification.**

### RT5.3 A numeric-label defect, small but concrete

Report §3.6 line 308: "the resulting median shift in alpha (-0.18, -0.27,
-0.45)". Those are **mean** shifts (0.15494/0.06219/-0.12651 minus the
unmodified mean 0.33220 = -0.1773 / -0.2700 / -0.4587). The **median** shifts
are -0.1772 / -0.2476 / -0.4228. The sentence attributes mean-derived numbers
to the median while the pre-registered verdict rule is a *median* rule. It does
not change any verdict; it should be corrected in a superseding note, never by
editing the frozen artifact.

---

## RT6. INDEPENDENT NOISE-FLOOR PROBE — I AGREE exactly on the number and DISAGREE on what it measures

One probe execution, decoder-free, 9.35 s wall / 49.8 MB peak RSS, from my own
script loading the same three sha256-pinned modules read-only through my own
fail-closed loader (all three pins independently verified by me).

**Agreement, to the bit.**

| quantity | executor | red team | |
| --- | --- | --- | --- |
| null `se_paired` k=17 mean, T=10,000 | 0.562720 | 0.562720 | identical |
| null `se_paired` k=17 mean, T=20,000 | 0.445360 | 0.445360 | identical |
| null 95% band, 10000->20000 | [-1.0295584296, 1.7588760236] | [-1.0295584296, 1.7588760236] | **identical to 1e-9** |

Part B is exactly reproducible from its committed seed specification by an
independent implementation. That is a real quality result and I record it as
one.

**Disagreement, on three counts, each measured (RT4, RT5.1, RT3): the band is
computed on an unpaired object and is 22% narrower than the paired object's
(3.398); the plant class cannot reach the band at any g; and the band's centre
misses its own forced value by 9 sigma with no decay in T.**

**And the disagreement that matters most: the real-object noise floor is not
the null band at all.** See RT7 — it is 3.17 in alpha units, not 2.79/2 = 1.39,
and it is measurable directly from committed data without any parametric object.

---

## RT7. DO THE REPLICATION CELLS REPLICATE? — no, and the reason is measurable in this batch's own data

### RT7.1 The two replication cells

| cell | fresh | historical (cited) | delta |
| --- | --- | --- | --- |
| 5000, regime P | +2.0488128380076307 | +2.836 (EV-HQC-469c08 O6) | **-0.787** |
| 8002, regime N | +1.5943364808460014 | -0.8662355237627483 (EV-HQC-927899 O4) | **+2.461, sign flip** |

I verified both citations against the ledger: EV-HQC-469c08 O6 line 111 gives
2.836 and EV-HQC-927899 O3 line 101 gives -0.8662355237627483. **Citing rather
than recomputing was the right call and is not a gap.** The historical values
are committed, Validator-reproduced to bit-identity (EV-HQC-927899 O3), and
recomputation would have required re-decoding already-consumed index ranges
this design is forbidden to touch. What *is* a gap is that neither the batch
nor the prior records ever obtained a second draw at a fixed (shard, regime) —
which this batch finally does.

### RT7.2 The replication gap is exactly the size of the batch's own unreported noise floor

This is the discharge of my predecessor's second required control, computed
from data this batch already paid for and did not use.

**Windows P2 `[35000:45000)` and N1 `[45000:55000)` are both T = 10,000, both
jackknife batch size 50, on the same shard, from the same call, under the same
procedure, on disjoint indices.** Anything that differs between them is
sampling noise, by construction. Measured `se_paired` at k=17:

| shard | fresh P2 | fresh N1 | historical T=10,000 | max/min | in alpha units (log2) |
| --- | --- | --- | --- | --- | --- |
| 5000 | 0.016872 | 0.281963 | 0.017520 | **16.71x** | **4.063** |
| 8002 | 0.020055 | 0.074586 | 0.022097 | **3.72x** | **1.895** |

(historical values: EV-HQC-469c08 O7 for 5000, EV-HQC-927899 O3 for 8002.)

Every alpha in this family is exactly `-log2(se_hi/se_lo)` — I verified this
identity reproduces all four fresh values to 1e-15. So those log2 gaps *are*
alpha noise, on the real object, distribution-free, requiring no parametric
model. **RMS = 3.17.**

Set that against everything this family has ever reported:

| quantity | value |
| --- | --- |
| **real-object alpha noise scale (this batch's own data)** | **3.17** |
| entire historical exponent spread (2.836 to -0.866) | 3.702 |
| fresh exponent spread | 2.637 |
| largest reported contrast (shard main effect) | 1.546 |
| executor's null band **width** | 2.788 |
| the +2.461 replication gap that "fails to replicate" | 2.461 |

**The replication gap is smaller than the noise floor of the instrument that
produced it.** The 8002 sign flip is not a failure of replication in any sense
that requires explanation; it is the expected behaviour of a statistic whose
own draw-to-draw spread is 3.17 in the same units.

### RT7.3 What this does to O7, and to my own predecessor's reports

`EV-HQC-469c08 O7` reports a **3.24x** between-shard spread of `se_paired` at
T~10,000 across all four shards and reads it as "broad shard-to-shard
heterogeneity in this estimator's variance." **The within-shard, same-T,
disjoint-data spread measured here is 16.71x on shard 5000 and 3.72x on shard
8002.** The within-shard spread *equals or exceeds* the between-shard spread
that O7 called heterogeneity. O7's between-shard signal is fully accounted for
by within-shard sampling variation and requires no shard-to-shard difference at
all.

That is a correction to a finding **my own lineage produced** (O7 is attributed
to the Red Team). It should be recorded as a superseding observation, not by
editing EV-HQC-469c08.

**What a gap of this size does to every number this family has published,
stated at its narrowest valid scope:** it does not falsify any of them as
measurements — they are all reproducible and, where checked, bit-identical. It
removes the basis for reading any of them *directionally* at k=17. Every
statement of the form "shard X's exponent is positive / negative / larger than
shard Y's / outside [0.4, 0.6]" at k=17 is a statement about a draw from a
distribution whose spread is at least as large as the entire range of values
being compared. Concretely this touches: EV-HQC-469c08 O6 and O7,
EV-HQC-927899 O3 and O4, and the "sharpest available discriminator" framing my
predecessor already retracted at TASK-20260815-907c66 — the retraction was
correct and this batch supplies the number that justifies it. **It does not
touch** the validity gates, the disjointness proofs, the F-invariant, the D2/D3
counts, or the reproducibility results, none of which are 2-point exponents.

### RT7.4 The under-claimed positive result

Two things this batch establishes and does not state:

1. **k is the controlling variable** (RT1.3). At k <= 7 all four cells sit at
   0.5, all contrasts vanish, and the noise handle drops to ~0.1 — a **40x
   reduction** from k=17.
2. **A multi-point ladder dominates the 2-point diagnostic on identical data.**
   Fitting the four windows per shard (T = 5,000 / 10,000 / 10,000 / 20,000) by
   OLS in log-log gives alpha = **0.4734** for shard 5000 and **0.0115** for
   shard 8002, with internal residual RMS 1.008 and 0.514 in log units. Shard
   5000's 4-point value lands **inside** the pre-registered [0.4, 0.6]
   1/sqrt(T)-consistency band that EV-HQC-927899 O4 says all four single-shard
   exponents are "FAR OUTSIDE". I am **not** claiming 0.473 is the truth — the
   residual RMS says the fit is badly determined, which is the point. I am
   claiming that the estimator choice, not the shard and not the regime,
   decides which headline this family reports.

---

## RT8. ATTACK THE READING RULE — it does not cover its own outcome, and I show it with arithmetic

I name **no** branch. Adjudication belongs to TASK-20260817-61ed83. What
follows is an attack on the rule's structure, which the task card explicitly
authorizes.

### RT8.1 The rule annihilates itself on a BLIND control

`batch.yaml:245-269` defines Branch N, Branch R and Branch S **entirely in
terms of the null object's band** ("contains the historical exponents", "fall
inside the corresponding null band", "exceeds the null band while ... does
not"). `batch.yaml:230-235` and design.md §3.6 pre-register that if the
anti-blindness leg fails, "the control is declared BLIND and **its null band
carries no interpretive weight at the ledger archive**."

The leg failed. Honouring the fail-closed rule therefore makes **three of the
four branches inevaluable**, leaving only the residual branch — **regardless of
how the four cells fell.** A reading rule whose outcome is fixed by a control's
verdict rather than by the measurement it was written to read is not
pre-registration doing its job. And `batch.yaml:246-247` compounds it: "BRANCH
N IS EVALUATED FIRST AND DOMINATES" — a precedence clause over a branch that,
on this outcome, cannot be evaluated at all.

**This is the campaign's THIRD pre-registered rule that fails to cover its own
outcome**, after DEC-20260809-186c86's binary test on BATCH-0e126d and
DEC-20260806-1ac8fa's stopping rule on BATCH-2ecaa1. The fourth branch was
added *because* of the first two; it catches the failure but does not fix the
cause, which is that all three substantive branches were made dependent on a
single unvalidated instrument.

### RT8.2 "The corresponding null band" is undefined, and the deciding contrast flips on the choice

The rule says main effects must "fall inside the **corresponding** null band."
Two bands exist. The regime main effect is a contrast **spanning both regimes**,
so no band corresponds to it. The consequence is not hypothetical:

| contrast | value | inside regime-P band [-1.4498, 1.7379] | inside regime-N band [-1.0296, 1.7589] |
| --- | --- | --- | --- |
| **regime main effect** | **-1.091319** | **TRUE** | **FALSE** |
| shard main effect | +1.545795 | TRUE | TRUE |
| interaction | +0.358789 | TRUE | TRUE |

**The single contrast that would distinguish two of the four branches gets
opposite verdicts under two equally defensible readings of an undefined
phrase.** A rule that can be steered by choosing which band "corresponds" is
gameable, and it was frozen in that state.

### RT8.3 The rule compares the wrong sampling distributions

A single alpha, a main effect, and an interaction have different null spreads.
With four independent cells of variance sigma^2: a main effect has variance
sigma^2 (the same as one alpha — the rule is accidentally right there), but the
**interaction has variance 4 sigma^2**, so its band should be **twice as wide**.
The rule applies the same single-alpha band to all three. And it applies a
percentile band derived from R=200 (whose 2.5th percentile is the 5th order
statistic, with substantial estimation error at the tail) as though it were
exact.

### RT8.4 The rule's clause-1 and clause-4 conditions are simultaneously present

Branch N clause 1 requires the null distribution to **contain the historical
exponents**. Against the executor's own bands:

| historical cell | value | its regime's band | |
| --- | --- | --- | --- |
| 5000, P | +2.836 | [-1.4498, 1.7379] | **OUTSIDE** |
| 6000, P | +1.402 | [-1.4498, 1.7379] | inside |
| 8001, N | -0.268250 | [-1.0296, 1.7589] | inside |
| 8002, N | -0.866236 | [-1.0296, 1.7589] | inside |

and against the four fresh cells: 5000-P (+2.0488) **OUTSIDE**, 5000-N
(+2.9607) **OUTSIDE**, 8002-P (+0.3236) inside, 8002-N (+1.5943) inside.
Clause 1 is therefore not satisfied wholesale, and the rule joins clause 1 to
clause 2 with "**and/or**" — a connective that specifies no truth condition.
Meanwhile Branch X's own enumerated trigger list includes "a replication cell
that fails to reproduce its own historical value", a condition that is present.
The rule states no resolution when a clause of the dominating branch and an
enumerated trigger of the residual branch are simultaneously satisfied.

### RT8.5 Is Branch N's precedence correct?

**The precedence is right in principle and wrong in this instance.** Evaluating
noise first is correct discipline: an instrument that cannot resolve an effect
cannot license a directional reading, and putting that first is the strongest
thing in the whole rule. It is wrong here for two measured reasons. (a) The
band it defers to is computed on an object with no pairing (RT4) and is 22% too
narrow, so it is the wrong yardstick — and being too narrow makes the
*escape* branches R and S anti-conservative, i.e. the precedence protects
against exactly one of the two errors it appears to protect against. (b) The
real-object noise scale is 3.17 (RT7), larger than the band's full width of
2.788, so a rule built on the null band understates the noise it exists to
guard against. **Fixing this does not require amending the rule's logic — it
requires replacing the band with one measured on the right object, which
Part B's own machinery can produce in seconds.**

---

## RT9. ATTACK THE ARM ASSIGNMENT — the selection criterion is circular, and both replication cells regressed exactly as that predicts

`batch.yaml:123-132` justifies choosing 5000 (+2.836) and 8002 (-0.866) over
6000 (+1.402) and 8001 (-0.268) as "MAXIMUM HISTORICAL CONTRAST ... the largest
available true contrast is the design most likely to clear it."

**The phrase "true contrast" is the whole problem.** The batch exists to test
whether the historical contrast is real. If it is noise — and RT7 measures the
noise scale at 3.17, larger than the 3.702 span being called a contrast — then
selecting the two most extreme members is **selection on the noise**, which
guarantees regression to the mean in precisely the two replication cells and
biases the shard main effect toward whichever shard was selected high. The
justification is valid only under the hypothesis under test.

The prediction is checkable and it came true. Historical extremes +2.836 and
-0.866, midpoint +0.985. Fresh: +2.0488 (moved 0.787 toward the midpoint) and
+1.5943 (moved 2.461 toward the midpoint). **Both replication cells moved
toward the centre, which is the signature of regression to the mean under
extreme selection**, and the larger historical deviation produced the larger
move. That is not proof of the mechanism, but it is the predicted direction on
both cells, and the design offers no competing account.

**Would including 6000 or 8001 have changed what can be concluded?** Yes, in
one specific and cheap way. A 2x2 with four cells has zero error degrees of
freedom (RT1.2). Adding either mid-range shard as a **third** arm at both
regimes would have cost roughly 150,000 more trial-decodes (~87 s at this
batch's own measured 4,478 trials/s) and given 6 cells, 2 error df, and a
shard main effect estimated from three shards rather than the two hand-picked
extremes. The batch spent 4.35% of its wall authorization; it could have
afforded that ten times over.

**Was the four-cell factorial scope creep?** **No — it was a genuine
improvement and was declared as an addition, not a substitute**
(`batch.yaml:113-122`). Both directive-mandated cross-regime cells are present
exactly as specified, and the two extra same-regime cells removed the
procedural confound that the literal two-cell minimum would have carried. That
is the right way to exceed a directive. **The improvement it enabled and did
not take** is that P2 and N1 became two same-T draws on the same shard — the
noise floor of RT7 — which was the batch's most valuable by-product and went
uncomputed.

---

## RT10. DISJOINTNESS-STRENGTH ASYMMETRY — correctly scoped, mildly under-credited, and not a bias on the comparison

**Does the asymmetry bias the arm comparison?** **No.** Both arms' data come
from the identical `mp.run_arm` path in the identical process, differing only
in the integer shard argument. The asymmetry is in **audit strength**, not in
data quality: if a same-process state leak existed, Arm A's external comparator
would catch it and Arm B's would not. Nothing in the comparison of alphas is
skewed by which arm has the better paper trail.

**Is "narrows but does not close" correctly scoped?** **Yes, and if anything it
under-credits Arm A.** The named residual risk is a same-process state leak
(design.md §2.5 step 4, correctly substituted for the refuted numpy-RNG story
that BATCH-174014's Red Team killed — the required carry-forward is genuinely
discharged, in design.md §2.5, `cross_regime_arms.py:619-633`, and report §1,
and I confirm the correction is materially right, not cosmetic). A same-process
leak that corrupted Arm B's stream but not Arm A's would have to be
**shard-selective**, and no mechanism for that is named or plausible given that
the shard enters only as a CTRStream key. So Arm A's cross-machine
bit-identical pass is stronger evidence for Arm B than "different shard,
different key" credits. The residual is nonetheless real — nothing external
pins shard 8002's stream — and the executor is right not to claim closure.

**The asymmetry that does matter and is not named** is RT2's: on **both** arms,
the proof certifies a prefix, and the retained windows `[30000:75000)` — the
data every statistic uses — are covered only by determinism inference. Arm A
and Arm B are equally exposed there. The fix costs nothing: persist the
retained arrays.

---

## RT11. WHAT IS STILL NOT KNOWN, and the single cheapest next control

**Not known after this task:**

1. Whether the k-dependence of RT1.3 is present in the four **historical**
   cells (their per-k arrays are committed but were never read this way).
2. Whether `se_paired`'s instability at k=17 is an artifact to be routed around
   or a **property of the estimand** worth studying in its own right (a
   detection statistic carried by a thin right tail of high-S trials is telling
   you something).
3. What the real arms' noise floor is with more than two draws per (shard, T).
   n = 3 per shard is a scale, not a distribution.
4. Whether **batch size** and **absolute T** can be separated at all. With
   `N_JACK_BATCHES` pinned at 200 they are the same variable up to a constant,
   in every design this family has run and in Part B's ladder too. **No 2x2 can
   break that one; only varying nb can.**
5. Whether Arm B's same-process gap is live. Unchanged, and now cheap to close
   (see below).

**THE SINGLE CHEAPEST NEXT CONTROL — and it costs ZERO new decoder calls.**

> **Recompute the entire four-shard exponent table, the four fresh cells, the
> three contrasts, and the null band at k = 5 and k = 10 instead of k = 17,
> from data already committed.** For the four fresh cells and both 4-point
> ladders this is pure arithmetic over
> `cross_regime_arms_results.json -> per_shard_per_window.*.per_k` (I did it in
> under a second; the table is in RT1.3). For the four historical cells the
> per-k arrays are already committed in
> `BATCH-412513/tasks/TASK-20260809-a79e4f/matched_pair_results.json`,
> `BATCH-0e126d/tasks/TASK-20260814-8bbdd2/matched_pair_repeat_results.json`
> and `BATCH-174014/tasks/TASK-20260815-e61cca/shard_8001_8002_discard_prefix_results.json`.
> For the null band it is Part B re-run at a different `M`, roughly 7
> core-seconds.

It is the cheapest because it needs no sampling; it is the most discriminating
because k is the parameter that is supposed to destroy the signal and the
partial evidence already says it does. **Pre-stated falsification route: if the
historical four cells do NOT collapse toward 0.5 at k <= 7 while the fresh four
do, my k-explanation is wrong and the shard/regime/procedure question is live
again at low k.** That would be a genuinely useful negative result, and I would
rather be refuted that way than have this go unchecked.

**Three follow-ons, each also cheap, in priority order:**

- **(2) Fix the null object's coupling** — `base ~ Binomial(55,p)`,
  `arm_i = base + Bernoulli_i(p)`. Four lines, no decoder call, ~10 s. Until
  then no band from Part B should be used as a yardstick for the real arms.
- **(3) Persist the retained per-trial S arrays**, in this task and every
  successor. ~600 KB as int8 for all eight fresh cells, against a 4 GB cap.
  This is the single change that would (a) upgrade both disjointness proofs
  from prefix-verified to window-verified, (b) make re-analysis at another k or
  another `N_JACK_BATCHES` free instead of impossible, and (c) end the
  five-batch-old "no raw array exists for that shard" gap rather than
  reproducing it a third time.
- **(4) Replace the 2-point diagnostic with a >= 3-rung ladder.** On the
  executor's own identical replicates the 4-rung OLS has SD **0.2343** against
  the 2-point's **0.7007** — **2.99x less noisy on the same data**. This is a
  `dominated_by` fact about the campaign's own instrument (see RT12.3).

**Should this instrument family stop?** **No, and I say so plainly against my
own strongest objections.** Stopping now would be premature closure in the
exact sense `docs/inventor-protocol.md` §4 names: the obstruction is real,
named and measured, but it is *localized to a parameter choice* (k=17) and a
*fixable estimator* (2-point, unpaired null, unpersisted data), all three
correctable at essentially zero marginal cost, with the corrected measurement
already half-computed in this batch's committed artifacts. A count of five
blind controls is a fatigue report about the search, not a statement about the
problem. What should stop is **the 2-point local exponent at k=17 as a
directional instrument**; that is a scoped retirement of a statistic, not a
closure of a lane, and the ledger should record it as the former.

---

## RT12. SEPARATE SOUND FROM MEANS

### RT12.1 Numbers I reproduced and therefore do NOT contest

- All four fresh local exponents, recomputed independently from the committed
  `se_paired` values via `-log2(se_hi/se_lo)`: 2.048812838007631,
  2.9607372685977804, 0.32362272345795434, 1.5943364808459977 — matching the
  reported values to < 1e-14.
- All three contrasts, recomputed: -1.0913 / +1.5458 / +0.3588.
- The null ladder's `se_paired` means at T=10,000 and 20,000 and the null 95%
  band at 10000->20000, from my own independent script: **bit-identical**.
- All 12 declared artifact hashes against the snapshot tree.
- Both historical citations against their ledger evidence records.
- Budget: 78.371 s wall / 80.073 s core, 2 of 2 runs, 6 of 6 decoder calls,
  peak RSS 82 MB — consistent with `stderr.log`'s `/usr/bin/time -l` output
  (72.28 + 6.64 real) and internally consistent across `run_manifest.yaml`,
  `confound_break_report.md` and both results JSONs.

**I found no fabricated measurement, timing, citation or run anywhere in this
task.** Contract compliance is exact: 12 declared, 12 present, 0 undeclared.

### RT12.2 The one place a reported claim is contradicted by its own code

RT5.2. `forced_identity.residual_max_abs = 6.217248937900877e-15` is sound as a
number and false as evidence: the identity it checks is an algebraic tautology,
demonstrated by feeding fictional `se_planted` values and obtaining residual
0. Report §3.6's blockquote and the snapshot receipt's
`producer_summary_for_reviewers.null_control_verdict` both cite it as showing
"the plant was demonstrably realized". It shows no such thing.

### RT12.3 Pareto honesty and end-to-end cost — one omission, one disclosed convention, one clear

Per `AGENTS.md` rule 5 and the `dominated_by` obligation, I checked every axis.

**OMITTED COST (found, not clear): the discarded prefix, which grows without
bound and is charged to no one.** Each analysis call computes `[0:30000)` and
throws it away. That is **120,000 of Part A's 321,800 trial-decodes — 37.3% of
the decoder work produced no datum**, and neither `cost_projection.json` (Part B
only) nor `batch.yaml`'s sizing paragraph separates it. The cost is *monotone in
the family's own history*: high-water went 5,000 -> 15,000 -> 30,000 -> **75,000**,
so the next task in this family must compute a `[0:75000)` prefix, 4 x 75,000 =
**300,000 discarded decodes, ~67 s of pure overhead before its first new
datum**, at this batch's own measured throughput — nearly the whole of this
batch's total spend, for nothing. The one after that pays ~134 s. **This is a
structural, compounding, unbudgeted cost, and RT11's item (3) eliminates it
entirely for ~600 KB of disk.**

**DISCLOSED CONVENTION with an arithmetic consequence the checkpoints do not
surface.** "Only executor-measured wall-clock is debited" is stated openly at
`batch.yaml:348-374` and in every checkpoint since BATCH-412513, so it is not
hidden. Its consequence is: the batch reports "4.35% of authorization used" on
78.371 s, while the batch's real end-to-end envelope is one executor plus one
snapshot archive plus **two 1,800-second reviewer authorizations** plus a
ledger archive. Measured executor spend is ~1.4% of the reviewers'
authorizations alone. The campaign budget is a real pause condition; it is
tracking the cheapest component of the batch.

**CHECKED AND CLEAR:** memory (82 MB peak vs 4 GB), run count (2 of 2), decoder
calls (6 of 6), artifact count (12 of 12), no standardized-parameter run, no
Bedrock.

**PARETO / `dominated_by` on the instrument itself, which no artifact in this
campaign states:** on the executor's own identical R=200 null replicates, the
2-point local exponent has SD **0.700666** and the 4-rung OLS on the *same
data* has SD **0.234334**. **The campaign's primary diagnostic is dominated by
a factor of 2.99 on its single relevant axis, by an alternative the producer
computed and reported in the same file** (report §3.4, "The scatter of the
2-point estimates about this well-determined line IS the calibration of the
diagnostic in question" — a correct sentence whose consequence is not drawn).
A `dominated_by: null` anywhere in this campaign's records for the 2-point
exponent would be a fabrication under AGENTS rule 5; the honest value is
"4-rung OLS on identical data, 2.99x lower SD".

---

## Independence, provenance and boundaries

- **Independent session.** Fresh agent invocation; I did not continue the
  producer's session. I did not read, list, or otherwise access
  `.../reviews/TASK-20260817-6f610c/` or confer with the Validator.
- **Correlated-judgement disclosure, stated plainly.** The sibling Validator
  TASK-20260817-6f610c is running concurrently on the **same model family** as
  me. **Any agreement between our two reports is correlated same-model
  judgement and must NOT be recorded as distinct-model corroboration.** The
  producer and the snapshot archivist also self-report the same model. This
  batch has four same-model opinions, not four independent ones.
- **Committed nothing.** No status changed, no producer artifact edited, no
  pinned module touched, no `knowledge/INDEX.md` touched, no ledger write. One
  file written, inside the committed `write_scope`.
- **Reading rule NOT applied. No branch named.** RT8 attacks the rule's
  structure, which the task card explicitly directs; it adjudicates nothing.
  Adjudication is TASK-20260817-61ed83's.
- **Executions in this session:** one sampling probe (the authorized experiment
  run; 9.35 s wall, 49.8 MB peak RSS, zero decoder calls, five legs) and two
  deterministic arithmetic evaluations over already-committed numbers
  containing no RNG draw, no decoder call and no new data. Declared exactly
  rather than rounded to "one".
- **Real wall-clock for this review:** approximately 24 minutes (session start
  ~01:20Z to report completion ~01:44Z on 2026-08-18), against an 1,800-second
  authorization. Machine shared with a concurrent Validator session, 14 cores.

---

```yaml
red_team_report:
  id: TASK-20260817-94c89e
  role: red-team
  reviews_task: TASK-20260817-c603c0
  binds_snapshot: TASK-20260817-f24a5e
  snapshot_commit: 9ac60648ddede021a854a4777a8979af298b7ad9
  snapshot_parent: 9c7dd452c6372cdfcc7e28fd15a74f0ddac9874f
  goal_id: GOAL-HQC-001
  batch_id: BATCH-91929e
  experiment_id: EXP-HQC-982268
  hypothesis_id: H-HQC-18d1b4
  hypothesis_status_unchanged: PROPOSED
  claim_tier: toy
  recorded_at: '2026-08-18'

  verdict: objections_material_to_conclusions

  verdict_summary: >-
    The measurements are SOUND and independently reproducible -- I re-derived
    all four fresh exponents to 1e-15, reproduced the null 95% band
    bit-identically from my own script, and verified all 12 declared artifact
    hashes against the snapshot tree in both directions. The shard/transition-
    regime confound IS genuinely broken by the 2x2. The objections are about
    MEANING: (1) a larger, unnamed confound -- the estimator's k-dependence --
    replaces it, and at k=2 all four cells return ~0.5 with all three contrasts
    ~0 on identical data; (2) the batch measured the real-object noise floor
    (16.71x and 3.72x spread in se_paired between two same-T disjoint windows,
    = 3.17 in alpha units) and did not report it, and that floor exceeds every
    contrast and nearly the entire historical spread; (3) the null object has
    independent arms where the real pair shares 55/56 blocks, so its band is
    22% too narrow and its unpaired/paired ratio is 0.9965 against the real
    cells' 2.34-28.69; (4) the anti-blindness leg could not have fired at any
    g, because the plant class saturates at rho ~1.35 against a required 2.53;
    (5) the frozen reading rule is structurally inevaluable on its own outcome
    and its deciding contrast flips on an undefined phrase.

  confound_status: BROKEN_AS_DESIGNED_THEN_RELOCATED_TWICE

  is_the_null_object_control_the_fifth_instance: true

  objections:
  - id: OBJ-1
    severity: material
    kind: meaning
    claim: >-
      The k-dependence of the entire phenomenology is unnamed. At k=17 the four
      fresh cells are 2.0488/2.9607/0.3236/1.5943 with contrasts
      -1.0913/+1.5458/+0.3588. At k=2, same data, same windows: 0.581/0.507/
      0.628/0.512 with contrasts +0.095/-0.026/-0.042. The same-T noise handle
      falls from 4.063/1.895 at k=17 to 0.061/0.105 at k=2, and the producer's
      own Forced Value 1 bias goes from -0.10164 at k=17 to -0.00007 at k=2,
      first exceeding 0.01 at k=13.
    where: >-
      cross_regime_arms_results.json -> per_shard_per_window.*.per_k.se_paired;
      null_object_control_results.json ->
      ladder_rungs.10000.forced_value_1_log2_A_k_vs_zero.arm0_mean_by_k;
      measure.py:225-246 (log2_A_from_hists numerator sum_s C(s,k) H_s)
    falsification_route: >-
      Recompute the four HISTORICAL cells at k=5 and k=10 from their committed
      per-k arrays. If they do NOT collapse toward 0.5 while the fresh four do,
      this objection is wrong and the shard/regime question is live at low k.
  - id: OBJ-2
    severity: material
    kind: meaning
    claim: >-
      The real-object noise floor is measurable from this batch's own committed
      data and is not reported. Windows P2 [35000:45000) and N1 [45000:55000)
      are both T=10000, same shard, same batch size 50, same procedure,
      disjoint. se_paired at k=17 differs by 16.712x (shard 5000) and 3.719x
      (shard 8002); with the historical T=10000 values that is three disjoint
      draws per shard. In alpha units the gaps are 4.063 and 1.895, RMS 3.17 --
      against a largest reported contrast of 1.546, a fresh spread of 2.637, a
      historical spread of 3.702 and a replication gap of 2.461.
    where: >-
      cross_regime_arms_results.json -> per_shard_per_window.shard_5000.{P2,N1}
      and .shard_8002.{P2,N1}, primary_cell_k17.se_paired; historical values
      EV-HQC-469c08 O7 (0.017520) and EV-HQC-927899 O3 (0.022096687)
    falsification_route: >-
      Draw a third and fourth disjoint T=10000 window per shard above index
      75000 and show the spread collapses. ~2 additional analysis calls.
  - id: OBJ-3
    severity: material
    kind: meaning
    claim: >-
      The null object's two arms are drawn from independent RNG streams, while
      the real matched pair shares 55 of 56 blocks per trial -- which the
      F[:,0:n_e-1] gate proves over 2,475,000 elements. Measured
      unpaired_over_paired at k=17: 0.9965 in the executor's null versus
      2.338-28.691 in the eight real cells. My corrected paired null (base ~
      Binomial(55,p), arm_i = base + Bernoulli_i(p); same law, true diff still
      0) gives ratio 2.985 median and a 95% band of width 3.398 against the
      executor's 2.788 -- 22% wider, with mean alpha 0.2747 vs 0.3322.
    where: >-
      null_object_control.py:256-257 (two independent rng_for streams);
      design.md Section 3.1; disjointness_proof_results.json ->
      f_structural_invariant
    falsification_route: >-
      Run the paired construction at R=1000 and show its band matches the
      independent-arm band. Four lines, no decoder call, ~30 s.
  - id: OBJ-4
    severity: material
    kind: meaning
    claim: >-
      The anti-blindness leg could not have fired at any g. Required downward
      median displacement 1.3366 => required rho >= 2.5256. The pre-registered
      plant class saturates and REVERSES: rho_median 1.1414 / 1.1666 / 1.3462
      at g=1.25/1.5/2.0, then 1.0381 (g=3), 0.8275 (g=4), 0.8230 (g=6), 0.8532
      (g=10), 0.8688 (g=50). Clipping to [0,56] around mu=17.877 drives the
      planted arm to a near-two-point law whose k=17 jackknife SE is LOWER than
      the base. The BLIND verdict is a fact about the plant's reach, not the
      instrument's sensitivity, and the report's cited monotone rise in rho is
      an artifact of sampling only g <= 2.
    where: >-
      null_object_control.py:129-136 (round_half_away / plant / clip),
      design.md Section 3.6 G_VALUES = [1.25, 1.5, 2.0];
      null_object_control_results.json -> sensitivity_leg
    falsification_route: >-
      Re-run the same transform at g in {3,4,6,10}. If any produces
      rho > 2.53, this objection is wrong. Decoder-free, ~5 s.
  - id: OBJ-5
    severity: material
    kind: soundness_of_stated_evidence
    claim: >-
      The "forced identity" is an algebraic tautology and carries zero
      evidential weight. al_un - log2(rho) reduces identically to al_pl for ANY
      positive se_planted; the se_hi terms cancel. The reported residual
      6.217248937900877e-15 measures float64 rounding only. I verified with
      fictional se_planted (0.31, 1e-6, 4321.0): residual 0.0. It is cited as
      showing "the plant was demonstrably realized" in confound_break_report.md
      Section 3.6 and in the snapshot receipt's producer summary.
    where: >-
      null_object_control.py:508-514; confound_break_report.md lines 282-286 and
      305-309; archives/TASK-20260817-f24a5e/snapshot-receipt.json ->
      producer_summary_for_reviewers.null_control_verdict
    falsification_route: >-
      Exhibit any positive se_planted for which the residual is not O(1e-15).
      None exists.
  - id: OBJ-6
    severity: material
    kind: meaning
    claim: >-
      Forced Value 3 is missed by 9 sigma and the pre-registered O(T^-1)
      excuse is falsified by the producer's own data. Full-ladder alpha =
      0.35133, SD 0.23433, R=200 => SE 0.01657, z = -8.97 vs the forced 0.5.
      The excuse predicts |0.5 - alpha| falls ~4x across the ladder's 8x T
      range; measured it is 0.1461 / 0.1678 / 0.1257 -- flat, not even
      monotone. A quantity that stays flat when it should decay is the
      canonical artifact tell (docs/inventor-protocol.md Section 3), here fired
      by the control's own forced value.
    where: >-
      null_object_control_results.json -> full_ladder_fit and
      adjacent_rung_pair_alpha_distributions; design.md Section 3.4 honest_caveat
    falsification_route: >-
      Extend the ladder to T=160000 and 320000. If |0.5 - alpha| falls as
      1/T from there, the finite-T excuse is right and this objection is wrong.
  - id: OBJ-7
    severity: material
    kind: meaning
    claim: >-
      The frozen four-branch reading rule does not cover its own outcome.
      (a) Branches N, R and S are all defined in terms of the null band, and
      the same batch's fail-closed rule strips that band of interpretive weight
      on a BLIND verdict -- so honouring the rule makes three of four branches
      inevaluable regardless of the data, while the precedence clause elevates
      one of them. (b) "the corresponding null band" is undefined for a
      contrast spanning both regimes, and the regime main effect -1.091319 is
      INSIDE the regime-P band [-1.4498,1.7379] and OUTSIDE the regime-N band
      [-1.0296,1.7589] -- opposite verdicts on the deciding contrast. (c) The
      interaction has 4x the variance of a single alpha and is compared against
      a single-alpha band. (d) Branch N clause 1 fails for the historical 2.836
      and for two of the four fresh cells, and is joined to clause 2 by
      "and/or", which specifies no truth condition. This is the campaign's
      THIRD pre-registered rule to fail to cover its own outcome.
    where: batch.yaml lines 237-290
    falsification_route: >-
      Exhibit a reading of "the corresponding null band" under which the
      regime main effect gets the same verdict from both candidate bands.
  - id: OBJ-8
    severity: minor
    kind: meaning
    claim: >-
      The arm-assignment criterion is circular: "maximum historical contrast"
      presumes the historical contrast is true, which is what the batch tests.
      Under selection on extremes with a noise scale of 3.17, regression to the
      mean is predicted in exactly the two replication cells -- and both moved
      toward the historical midpoint (+2.836 -> +2.0488, -0.866 -> +1.5943).
      A third shard at both regimes (~150,000 decodes, ~87 s, against 4.35% of
      authorization used) would have given 2 error degrees of freedom where the
      2x2 has zero. The four-cell factorial itself was a genuine improvement,
      correctly declared as an addition rather than a substitution.
    where: batch.yaml lines 104-158; cross_regime_arms_results.json -> replication_comparisons
    falsification_route: >-
      Measure 6000 and 8001 at both regimes on fresh ranges; if they land at
      the same extremes as 5000 and 8002 the selection was not on noise.
  - id: OBJ-9
    severity: minor
    kind: meaning
    claim: >-
      A NEW collinearity was introduced for free and was avoidable for free:
      the window order is identical on both shards (P at [30000:45000), N at
      [45000:75000)), so regime is now 100% collinear with position-within-call
      on both arms. Not mechanistically live (CTRStream is deterministic and
      index-keyed, so position = sampling realization, not drift), but the
      design has four cells and ZERO error degrees of freedom, so the
      realization cannot be separated from the effect. Counterbalancing the
      window order across the two shards costs zero additional decodes.
    where: cross_regime_arms.py lines 89-95; design.md Section 6 limitation 3
    falsification_route: >-
      Re-run with the window order reversed on one shard; if the contrasts are
      unchanged, the realization contributed nothing.
  - id: OBJ-10
    severity: minor
    kind: meaning
    claim: >-
      Both "disjointness proofs" certify a PREFIX ([0:5000) Arm A, [0:10000)
      Arm B). The retained windows [30000:75000), on which every statistic is
      computed, are verified against nothing external on EITHER arm; the step
      from prefix to windows is an inference from stream determinism. The
      honest label is prefix-verified / windows determinism-inferred. The
      inference is well-founded (CTRStream is pure SHA-256 counter mode, traced
      by BATCH-174014's Red Team and re-confirmed by Arm A's cross-machine
      bit-identical pass) but it is an inference, and it is symmetric across
      the two arms rather than an Arm-B-only weakness.
    where: >-
      cross_regime_arms.py lines 559-598 (Arm A) and 452-505, 600-614 (Arm B);
      disjointness_proof_results.json
    falsification_route: >-
      Persist the retained per-trial S arrays; the next task's prefix check
      then covers the retained range directly. ~600 KB.
  - id: OBJ-11
    severity: minor
    kind: provenance
    claim: >-
      The DEV-1 pre-registration content anchor
      7511ecc1698749156cf89c8c476b93d3baf7c35980a36d5812f21b21f7ba25e0 is not
      verifiable by anyone, because the pre-fill design.md it hashes was
      overwritten and never committed. stdout.log claims the anchor makes
      pre-registration "auditable by content rather than by mtime"; as
      delivered it reduces to trusting the executor's sequencing. Not a
      violation -- the deviation was declared in advance and its scope (one
      calibrated constant that is by construction a Part A output) is minimal
      and I have no reason to doubt it -- but the audit property claimed is not
      the audit property delivered.
    where: stdout.log lines 2-8; design.md Section 3.2; run_manifest.yaml protocol_deviations
    falsification_route: >-
      Produce a file hashing to 7511ecc1... that differs from the committed
      design.md only in the marked block.
  - id: OBJ-12
    severity: minor
    kind: soundness_of_labelling
    claim: >-
      confound_break_report.md Section 3.6 labels mean shifts as median shifts.
      The cited (-0.18, -0.27, -0.45) are planted MEAN minus unmodified mean
      (0.33220); the median shifts are -0.1772 / -0.2476 / -0.4228. The
      pre-registered verdict rule is a median rule. No verdict changes.
    where: confound_break_report.md line 308
    falsification_route: arithmetic on null_object_control_results.json -> sensitivity_leg

  required_controls:
  - >-
    BEFORE any further ledger interpretation of any k=17 local exponent:
    recompute the four fresh cells, the three contrasts, the two 4-point
    ladders AND the four historical cells at k=5 and k=10, from already-
    committed per-k arrays. Zero decoder calls. Report the same-T noise handle
    at each k alongside. If the historical cells do not collapse toward 0.5 at
    low k while the fresh ones do, the k-explanation is refuted and that is the
    useful result.
  - >-
    Re-run the null object with the arms COUPLED as the real pair is coupled
    (base ~ Binomial(n_e-1, p), arm_i = base + Bernoulli_i(p)), and report
    unpaired_over_paired alongside the band. Until then no Part B band may be
    used as a yardstick for the real arms. Four lines, no decoder call.
  - >-
    Extend the sensitivity leg until it either fires or is shown incapable, and
    report the MINIMUM DETECTABLE rho (and the implied alpha displacement)
    rather than a binary IN/OUT verdict. Replace the fixed g list with a search
    for the detection threshold.
  - >-
    Persist retained per-trial S arrays in this and every successor task
    (~600 KB int8 for eight cells against a 4 GB cap). This upgrades both
    disjointness proofs from prefix-verified to window-verified, makes
    re-analysis at another k or another N_JACK_BATCHES free instead of
    impossible, and ends the recurring "no raw array exists for that shard"
    gap instead of reproducing it a third time.
  - >-
    Vary N_JACK_BATCHES. With nb pinned at 200, batch size and absolute T are
    the same variable up to a constant in every design this family has run,
    including Part B's ladder. No 2x2 can separate them; only re-analysing the
    same data at nb in {100, 200, 400} can, and that costs zero new sampling
    once arrays are persisted.
  - >-
    Record a dominated_by value for the 2-point local exponent. On the
    executor's own identical replicates the 4-rung OLS has SD 0.234334 against
    the 2-point's 0.700666 -- 2.99x less noisy on the same data. A null there
    would be a fabrication under AGENTS.md rule 5.

  heuristic_and_cost_model_challenges:
  - >-
    HEURISTIC "the T^(-1/2) law is exact only asymptotically, with an O(T^-1)
    finite-T correction" (design.md Section 3.4) is pre-registered as the
    explanation for any miss of alpha = 0.5. It is falsified by the producer's
    own three rung pairs: the miss is 0.1461 / 0.1678 / 0.1257 across an 8x
    range in T -- flat, not decaying, not monotone. z = -8.97 on the full
    ladder.
  - >-
    HEURISTIC "the null object's forced values transfer to the real arms"
    is never asserted (correctly) but is the premise of the entire reading
    rule. It fails for a nameable structural reason: independent arms vs 55/56
    shared blocks, unpaired/paired 0.9965 vs 2.34-28.69.
  - >-
    HEURISTIC "maximum historical contrast is the design most likely to clear
    the noise floor" presumes the contrast is signal; measured noise 3.17
    exceeds the contrast being maximized.
  - >-
    OMITTED END-TO-END COST, FOUND: the discarded prefix. 120,000 of Part A's
    321,800 trial-decodes (37.3%) produced no datum, and the cost is monotone
    in the family's own history (high-water 5,000 -> 15,000 -> 30,000 ->
    75,000). The next task must burn 4 x 75,000 = 300,000 decodes (~67 s at
    this batch's measured throughput) before its first new datum; the one after
    ~134 s. Charged in neither cost_projection.json nor batch.yaml's sizing.
  - >-
    DISCLOSED CONVENTION with an unsurfaced consequence: "only executor-
    measured wall-clock is debited" means the reported "4.35% of authorization
    used" covers the cheapest component of a batch that also spends two 1,800 s
    reviewer authorizations plus two coordinator sessions.
  - >-
    CHECKED AND CLEAR: memory (82 MB peak vs 4 GB), runs (2 of 2), decoder
    calls (6 of 6), artifacts (12 of 12, 0 undeclared), no standardized-
    parameter run, no Bedrock, no discarded or repeated run.

  baseline_comparison:
    what_is_being_compared: >-
      The campaign's own 2-point local-exponent diagnostic at k=17 against the
      alternatives available on identical data. This is an instrument, not an
      algorithm, so the Pareto axes are estimator noise, cost, and the
      calibration's transferability -- not time/memory/queries against
      Pollard-rho or BSGS, neither of which is a baseline for anything here.
    dominated_by: >-
      4-rung OLS-in-log-log on the same replicates: SD 0.234334 versus the
      2-point's 0.700666, a 2.99x reduction in noise at zero additional cost
      (null_object_control_results.json -> full_ladder_fit vs
      adjacent_rung_pair_alpha_distributions["10000->20000"]).
    dominated_by_on_the_real_object: >-
      A 4-point ladder over this batch's own four windows gives alpha = 0.4734
      (shard 5000, residual RMS 1.008) and 0.0115 (shard 8002, residual RMS
      0.514) -- shard 5000 INSIDE the [0.4,0.6] band that EV-HQC-927899 O4
      calls all four single-shard exponents "FAR OUTSIDE". Reported as
      arithmetic on committed data, not as a truth claim: the residual RMS says
      the fit is badly determined, which is the point.
    sota_delta: >-
      Not applicable and not claimed. Nothing in this batch advances or bears
      on any cryptanalytic state of the art. Claim tier TOY, hard ceiling.
    lower_cost_alternative_not_taken: >-
      P2 and N1 are two same-T draws on the same shard, produced by this
      design at zero marginal cost, and constitute the "repeat the SAME
      (shard, transition) measurement on disjoint fresh ranges" option that
      TASK-20260815-907c66's own required_controls listed second. It was
      neither computed nor mentioned. It is the strongest noise-floor
      measurement in the batch.

  scope_limits:
  - Everything here is scoped to PS-R3 reduced parameters, one defect class
    (V3, last-block-window-read-early), one injection point, k range 2..26,
    m = 17, shards 5000 and 8002, index range [30000,75000), and this batch's
    budget. Nothing bears on HQC's IND-CCA security, its decoding-failure rate,
    assumption A17 or A5, or any standardized parameter set.
  - The k-dependence finding (OBJ-1) is measured on the four FRESH cells only.
    The four historical cells were not recomputed at low k by me and that check
    is the named next control, not a result.
  - The real-object noise scale 3.17 rests on n = 2 same-T contrasts (one per
    shard), plus one historical value per shard. It is a scale, not a
    distribution, and it should be reported as such.
  - My paired null object is a minimal correction of the coupling, not a model
    of the real S distribution. It shows the band DEPENDS on the coupling; it
    does not claim to be the right band.
  - The g-ladder extension used the executor's own transform and seeds at
    T=20000, R=200. Saturation is demonstrated for THAT plant class only.
  - I hold no authority to change any record status, promote evidence, apply
    the reading rule, or name a branch.

  premature_closure_assessment: >-
    This batch does NOT foreclose a live lane, and I decline to foreclose one
    either. The obstruction is named and measured (3.72x-16.71x within-(shard,
    T) spread in se_paired at k=17 on disjoint real data), localized (near-
    absent at k <= 7), and correctable at essentially zero marginal cost. What
    should be retired is the 2-point local exponent at k=17 as a DIRECTIONAL
    instrument -- a scoped retirement of a statistic, not a closure of a lane.
    A count of five blind controls is a fatigue report about the search, not a
    statement about the problem. Symmetrically, this batch UNDER-claims: it
    contains, in committed artifacts, both an explanation of its own five-batch
    puzzle (the k-table) and the real-object noise floor that justifies the
    prior report's own retraction, and states neither.

  next_concrete_action: >-
    Recompute the four fresh cells, the three contrasts, both 4-point ladders
    and all four HISTORICAL cells at k=5 and k=10, from already-committed per-k
    arrays in cross_regime_arms_results.json,
    BATCH-412513/.../matched_pair_results.json,
    BATCH-0e126d/.../matched_pair_repeat_results.json and
    BATCH-174014/.../shard_8001_8002_discard_prefix_results.json, reporting the
    same-T noise handle at each k, plus Part B's null band re-run at those k
    with the arms COUPLED (base ~ Binomial(n_e-1,p), arm_i = base +
    Bernoulli_i(p)). ZERO decoder calls; the real-cell half is pure arithmetic
    and the null half is roughly 7 core-seconds. Pre-stated falsification: if
    the historical four do not collapse toward 0.5 at low k while the fresh
    four do, the k-explanation is refuted and the shard/regime question is live
    again at low k.

  independence:
    independent_session: true
    is_producer: false
    read_sibling_validator_directory: false
    conferred_with_sibling_validator: false
    correlated_judgement_disclosure: >-
      The sibling Validator TASK-20260817-6f610c runs concurrently on the SAME
      MODEL FAMILY as this Red Team session, and the producer and snapshot
      archivist both self-report the same model. Any agreement among these
      reports is CORRELATED SAME-MODEL JUDGEMENT and must not be recorded as
      distinct-model corroboration or as any form of quorum.

  inference:
    runtime: claude_code
    native_authenticated_session: true
    requested_policy: review-adversarial
    requested_reasoning_effort: xhigh
    this_sessions_actual_resolved_model_id: claude-opus-5[1m]
    this_sessions_actual_resolved_model_id_source: >-
      GENUINE SELF-REPORT from this session's own runtime system context. Not
      read from any configuration file and not copied from any committed
      binding target.
    committed_binding_target_read_for_reference_only: >-
      orchestration/model-bindings.yaml was NOT written by this session and is
      NOT the source of the field above. The two are recorded separately by
      design; the working copy of that file may carry another session's
      uncommitted edits and is therefore not evidence of anything here.
    reasoning_effort_source: >-
      .claude/agents/red-team.md frontmatter, derived from roles.yaml
      default_policy review-adversarial -> model-policies.yaml
      reasoning_effort xhigh. Confirmable with
      tools/check_runtime_bindings.py --list.
    fallback_allowed: false
    fallback_used: false
    degraded_allowed: false
    degraded_requirements: []
    independent_session_required: true
    amazon_bedrock_selected_configured_probed_contacted_or_used: false
    amazon_bedrock_note: >-
      AWS_BEARER_TOKEN_BEDROCK is present in the environment and
      CLAUDE_CODE_USE_BEDROCK is unset. Bedrock was not selected, configured,
      probed, contacted or used. Refused under AGENTS.md rule 16.

  execution_record:
    experiment_runs_authorized: 1
    sampling_probe_executions: 1
    sampling_probe_wall_seconds: 9.35
    sampling_probe_peak_rss_bytes: 49823744
    decoder_calls_made: 0
    deterministic_arithmetic_evaluations: 2
    deterministic_arithmetic_note: >-
      Two evaluations over already-committed numbers containing no RNG draw, no
      decoder call and no new data. Declared exactly rather than rounded down.
    review_wall_clock_seconds_approx: 1440
    review_wall_clock_authorized: 1800
    machine: 14 cores, shared with a concurrent Validator session
    pinned_modules_edited: 0
    producer_artifacts_edited: 0
    files_written: 1
    commits_made: 0
    ledger_records_written: 0
    status_changes_made: 0
    reading_rule_applied: false
    branch_named: false

  write_scope_note: >-
    The committed task card, the committed handoff and the committed
    dispatch_queue.json archive entry all declare write_scope
    coordination/goals/GOAL-HQC-001/batches/BATCH-91929e/reviews/TASK-20260817-94c89e/
    with the single artifact red_team_report.md. The dispatch orientation named
    a .../red-team/... path instead. I wrote to the COMMITTED path, since the
    committed artifact is the contract and the ledger archive reads
    artifact_paths. Nothing else was written anywhere in the repository.

  artifact_paths:
  - coordination/goals/GOAL-HQC-001/batches/BATCH-91929e/reviews/TASK-20260817-94c89e/red_team_report.md
  - coordination/goals/GOAL-HQC-001/batches/BATCH-91929e/tasks/TASK-20260817-c603c0/design.md
  - coordination/goals/GOAL-HQC-001/batches/BATCH-91929e/tasks/TASK-20260817-c603c0/cross_regime_arms.py
  - coordination/goals/GOAL-HQC-001/batches/BATCH-91929e/tasks/TASK-20260817-c603c0/cross_regime_arms_results.json
  - coordination/goals/GOAL-HQC-001/batches/BATCH-91929e/tasks/TASK-20260817-c603c0/null_object_control.py
  - coordination/goals/GOAL-HQC-001/batches/BATCH-91929e/tasks/TASK-20260817-c603c0/null_object_control_results.json
  - coordination/goals/GOAL-HQC-001/batches/BATCH-91929e/tasks/TASK-20260817-c603c0/disjointness_proof_results.json
  - coordination/goals/GOAL-HQC-001/batches/BATCH-91929e/tasks/TASK-20260817-c603c0/confound_break_report.md
  - coordination/goals/GOAL-HQC-001/batches/BATCH-91929e/tasks/TASK-20260817-c603c0/cost_projection.json
  - coordination/goals/GOAL-HQC-001/batches/BATCH-91929e/tasks/TASK-20260817-c603c0/run_manifest.yaml
  - coordination/goals/GOAL-HQC-001/batches/BATCH-91929e/tasks/TASK-20260817-c603c0/stdout.log
  - coordination/goals/GOAL-HQC-001/batches/BATCH-91929e/tasks/TASK-20260817-c603c0/stderr.log
  - coordination/goals/GOAL-HQC-001/batches/BATCH-91929e/batch.yaml
  - coordination/goals/GOAL-HQC-001/batches/BATCH-91929e/archives/TASK-20260817-f24a5e/snapshot-receipt.json
  - coordination/goals/GOAL-HQC-001/batches/BATCH-174014/reviews/TASK-20260815-907c66/red_team_report.md
  - coordination/goals/GOAL-HQC-001/batches/BATCH-412513/tasks/TASK-20260809-a79e4f/matched_pair.py
  - coordination/goals/GOAL-HQC-001/batches/BATCH-6fddee/tasks/TASK-20260806-64b506/stage_a.py
  - coordination/goals/GOAL-HQC-001/batches/BATCH-0a65c0/tasks/TASK-20260806-cde749/measure.py
  - ledger/evidence/EV-HQC-469c08.yaml
  - ledger/evidence/EV-HQC-927899.yaml
```

*Red-team record. I wrote only inside this directory, committed nothing, and
hold no authority to change any record's status, promote evidence, apply
batch.yaml's reading rule, or name a branch. Adjudication belongs to
TASK-20260817-61ed83 and DEC-20260817-2b638b.*
