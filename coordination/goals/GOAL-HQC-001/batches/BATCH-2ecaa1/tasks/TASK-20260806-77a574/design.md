# Design: pilot real-sampler defect injection (PRE-REGISTERED before any run)

`TASK-20260806-77a574` (executor) / `BATCH-2ecaa1` / `GOAL-HQC-001` /
`EXP-HQC-982268`. Authorized by `DEC-20260806-1ac8fa`'s next_action, itself
resting on `EV-HQC-bfb257` (cost model) and both of that batch's independent
reviews.

**This document is written and frozen BEFORE `pilot_injection.py` is run on
any real data.** Everything below — the defect choice, the injection point,
the expected-effect direction, and the mechanically-sound/needs-redesign
criteria — is fixed in advance. `pilot_results.json` and `pilot_report.md`
are produced afterward and must not cause this file to be edited
retroactively.

Claim tier: **toy, hard ceiling**. Nothing here is a statement about HQC, A17,
its decoding-failure rate, or any standardized parameter set. This is a
pilot at PS-R3 (`n=7187, n_e=56, n_2=128, dup=1, omega=45, omega_r=omega_e=51,
N=7168, m=17`), one parameter set, one defect class, one injection point, one
small trial count.

---

## 1. What this pilot does and does not do

- Imports `stage_a.py` and `measure.py` **read-only**, sha256-pinned, exactly
  as V1/V2/V3 and the cost-model task did (`load_module()`, identical pattern
  to `planted_arm_v3.py`). Neither file is modified on disk.
- Injects ONE defect at ONE point via a thin wrapper that reuses the real,
  unmodified `decode_blocks` internally (see Section 3). No new sampler,
  decoder, or estimator machinery is written.
- Runs the injected pipeline through `stage_a.py`'s own unmodified
  `_t_shard()` worker (the same function `measure.py` and the cost-model
  benchmark call directly), via monkey-patching the module-level
  `decode_blocks` name `_t_shard` resolves at call time — NOT by editing
  `stage_a.py`'s file on disk.
- Runs a paired **undefected control** arm at the same T, same parameter
  set, disjoint PRNG shards, using the real `decode_blocks` unmodified, so
  any measured deviation can be attributed to the injection specifically
  rather than to finite-T estimator noise alone (prior PS-R3 runs, e.g.
  `EV-HQC-b71230`, showed the undefected estimator itself is not exactly 0
  at finite T).
- Pushes both arms' histograms through `measure.py`'s own `comb_matrix` and
  `log2_A_from_hists`, with a leave-one-batch-out jackknife SE computed the
  same way `measure.py`'s own `main()` computes it (point/loo/jackknife
  pattern), reused via direct call to the imported functions.
- Measures actual wall/core-second throughput of the defect-injected `_t_shard`
  call and reports it against both cost-model figures.
- Does **not** attempt the full `T_req = 3.09e5` run. Does **not** touch
  `stage_a.py`, `measure.py`, or `experiments/EXP-HQC-982268/specification.yaml`.
  Does **not** conclude anything about A17, HQC's DFR, or any standardized
  parameter set.

---

## 2. Defect class chosen: **V3 (last-block-window-read-early)**

Two defect classes were offered by the task card: V1 (off-by-one truncation,
a global circular shift) and V3 (last-block-window-read-early, a
single-position shift confined to one block). **V3 is chosen.**

Rationale:

1. **It pairs naturally, and only, with the `decode_blocks` reshape
   injection point** (Section 3): `cost_model.md` §3 point 4 names this
   defect/point pairing explicitly as "the literal, direct implementation of
   'last-block-window-read-early' — the exact defect-class name V1/V3 used,
   now applied to the real decoder's own input window instead of a planted
   proxy." No other combination of {V1, V3} x {four injection points} is
   this direct a translation from a prior control arm's defect *name* to the
   real sampler's own code.
2. **It is the Red Team's own explicit recommendation** in the
   cost-model review (`TASK-20260806-e13ecc`, §6, item 1): "Fund a single
   pilot injection run at PS-R3, using the **narrowest** of the four named
   injection points (§3 point 4, the last-block-window defect) —
   deliberately the hardest case, not the easiest, since a detectable signal
   there is the strongest evidence the approach will generalize, and a null
   result there is the cheapest way to learn that a much larger T is needed
   before committing more budget." `DEC-20260806-1ac8fa` adopts the Red
   Team's narrower framing over the executor's in its rationale; this design
   follows that adopted framing rather than picking the easiest-to-detect
   variant.
3. **It is confined to exactly one of `n_e = 56` blocks** (the last block,
   index `n_e - 1`), which is the most conservative (least likely to produce
   an artificially large, easy-to-detect effect) of the four candidate
   injection points — `CTRStream.below()` and `fixed_weight_support`'s range
   would perturb *every* draw across all `n_e` blocks, which the Red Team's
   own dose-response argument (§2 of the review) flags as plausibly the
   *easiest* case to detect and therefore the least informative choice for a
   first pilot whose job is to stress-test whether the approach works at
   all, not to pick the injection point most likely to show a signal.

V1 (a global circular shift applied to every draw) is explicitly **not**
tested in this pilot. That is a stated scope boundary, not a claim that V1
is uninformative — a global-shift pilot is a candidate for a *second* pilot
if the campaign continues past this one, and is not run here to keep this
pilot to one defect class as the task card requires.

---

## 3. Injection point: `decode_blocks`'s block-window (last block only)

**Mechanism, stated exactly, before any code is run:**

`decode_blocks(bits, n_e, n_2, dup)` (stage_a.py line 296) reshapes its
`(B, N)` bit array as `blk = bits.reshape(B, n_e, n_2)`, so block `j`
occupies bit columns `[j*n_2, (j+1)*n_2)`. The defect is injected by
constructing a **perturbed bit array** in which every block is left exactly
as generated **except the last block** (`j = n_e - 1`), whose window is
shifted left by exactly one bit position:

```
lo, hi = (n_e - 1) * n_2, n_e * n_2
bits_defected[:, lo:hi] = bits[:, lo - 1 : hi - 1]
```

i.e. the defected last block's position `0` is filled with the TRUE bit at
column `lo - 1` (the true last bit of block `n_e - 2`), and the defected
last block's positions `1..n_2-1` are filled with the true block `n_e-1`'s
own bits `0..n_2-2` — its own true last bit (column `hi-1 = N-1`) is dropped
entirely. This is exactly "the bit window for the last block is read one
position early," applied to the real decoder's actual input, not a
synthetic proxy.

**The ONLY new code is this bit-array preprocessing step.** `decode_blocks`
itself — the fold, the size-128 WHT, the argmax, the tie rule — is called
**unmodified**, on the perturbed array, via the real imported function
(`decode_blocks_original(bits_defected, n_e, n_2, dup)`). This is injected
into `stage_a.py`'s real per-trial pipeline not by editing `stage_a.py`'s
source, but by reassigning the module attribute `sa.decode_blocks` to a
thin wrapper before calling `sa._t_shard()`, whose own bytecode resolves
`decode_blocks` as a global lookup against `sa`'s own module namespace at
call time. `_t_shard`'s D2 (exact generation weight) and D3 (support-cap)
hard invariants run **before** `decode_blocks` is ever called and are
therefore untouched by this injection — they should PASS under the defect
exactly as they do undefected, and a D2/D3 failure would indicate an
implementation bug unrelated to the intended perturbation (see Section 5).

**Fail-closed injection invariant** (checked on every defected trial,
before any decode happens): the perturbed window must satisfy
`bits_defected[:, lo+1:hi] == bits[:, lo:hi-1]` (own bits, shifted) AND
`bits_defected[:, lo] == bits[:, lo-1]` (borrowed bit), with every OTHER
block's bits left bit-identical to the true generated array. Any violation
aborts the run (`SystemExit`) before a single trial is scored. A deliberate
break of this invariant is exercised as a dry run and documented in
`run_manifest.yaml` / `pilot_report.md`, alongside a deliberate sha256
pin-mismatch dry run for the `load_module()` gate (the same convention V1-V3
used).

---

## 4. Expected effect on `log2_Ahat_k`, stated in advance

**No confident directional prediction is offered.** The reasoning, stated
honestly rather than retrofitted:

- The size-128 Walsh-Hadamard decode is a **linear** transform of the `±1`
  recast of the block's bits; changing one input coordinate changes every
  one of the 128 output coefficients by a bounded amount (at most `±2` per
  coefficient, since one coordinate flips sign in every Hadamard row). RM(1,7)
  (used here, duplication 1 at PS-R3) has minimum distance 64 out of 128, a
  large relative margin, so **most** trials should have a decode margin large
  enough that a single bounded perturbation does not flip the argmax —
  a MEASURABLE but likely SMALL fraction of block-`n_e-1` trials, specifically
  those already close to their own decision boundary, are expected to flip.
  No V1-V3 arm ever measured this real-sampler quantity (V1-V3 never ran
  `fixed_weight_support` or the real WHT decoder on genuinely (T)-distributed
  content), so no prior number anchors even the order of magnitude here.
- Because the perturbation touches **only block `n_e - 1`**, only the
  `k`-subsets that include that one block are affected — a fraction
  `k / n_e` of all `C(n_e, k)` subsets (e.g. `17/56 ≈ 0.30` at the
  load-bearing `k = m = 17`). Any true shift in block `n_e-1`'s marginal
  failure probability is therefore substantially diluted in `log2_Ahat_k`
  relative to a hypothetical injection touching every block (e.g. a V1-class
  global shift).
- Combining a plausibly-small per-trial flip probability with this
  `k/n_e` dilution and a low-thousands-trial jackknife noise floor, the
  **pre-registered primary expectation for this pilot's scale is a clean
  null** — no statistically distinguishable deviation between the defected
  and paired undefected arms. This is stated as the primary expectation
  precisely because the Red Team chose this injection point *for* its
  narrowness (Section 2, item 2): a null result here is itself the
  informative, cheap outcome the stopping rule is built around, not a
  failure of the pilot.
- If a signal IS seen, no sign is predicted a priori: the substituted bit is
  not systematically biased toward increasing or decreasing block-`n_e-1`'s
  decode margin relative to its true bit, so there is no principled reason
  to predict `log2_Ahat_k(defected) > log2_Ahat_k(undefected)` over the
  reverse.

This is a genuinely uncertain prediction, stated before running rather than
hedged after seeing a result. Both a clean null and a measurable deviation
are treated as pre-registered-consistent outcomes; only the *absence* of any
usable measurement (crash, undefined estimator, failed invariant) would be
inconsistent with this design succeeding mechanically.

---

## 5. Mechanically-sound vs. needs-structural-redesign criteria (fixed in advance)

**Mechanically sound** requires ALL of the following:

1. No uncaught exception or crash during the full pilot run (both arms,
   provenance phase, self-tests, estimator phase).
2. The fail-closed injection invariant (Section 3) holds on every defected
   trial with no violation in the authorized run.
3. `stage_a.py`'s own D2 (exact generation weight) and D3 (support-cap)
   hard invariants both report zero violations on BOTH arms (they run
   upstream of `decode_blocks` and should be entirely unaffected by a
   decode-only defect).
4. `decode_blocks` itself is called **unmodified** (verified by identity:
   the wrapper calls the literal function object imported from the
   sha256-pinned `stage_a.py`, never a reimplementation) — confirmed by a
   direct equality check between the wrapper's inner call target and
   `stage_a.decode_blocks`'s original id before patching.
5. `measure.py`'s `comb_matrix` / `log2_A_from_hists` produce finite,
   non-NaN `log2_Ahat_k` values (via the point-estimate call on the pooled
   histogram) for at least the load-bearing order `k = m = 17`, on both
   arms, at the achieved T.
6. The two deliberate-mismatch dry runs (sha256 pin, injection invariant)
   both demonstrably abort with `SystemExit` and neither dry run is allowed
   to write a `pilot_results.json`.
7. The measured throughput is a real, reportable number (not `NaN`/undefined
   from a zero-trial or zero-cpu-time degenerate run).

**Needs structural redesign** is the classification if ANY of the following
occurs, regardless of what the estimator numbers show:

1. The defect cannot be expressed as a bit-array preprocessing wrapper
   around the unmodified `decode_blocks` — i.e., achieving the described
   perturbation is found to require editing `decode_blocks`'s own internals
   (not just its input), or editing `_t_shard`'s own body rather than
   monkey-patching a name it resolves at call time.
2. The injection invariant, when deliberately broken by the dry run,
   fails to abort (a genuine fail-open bug in the check itself).
3. D2 or D3 fires on the defect-injected arm (would indicate the
   monkey-patch is somehow altering the generation phase, which the design
   claims is impossible — a real implementation defect, not an intended
   effect).
4. The estimator returns `NaN`/undefined at the load-bearing order `k = m =
   17` on an arm that achieved its full planned T (as opposed to genuinely
   insufficient T, which is an expected, reportable limitation, not a
   redesign trigger).
5. Any uncaught exception during the authorized run.

These criteria are the executor's own factual assessment against the
pre-registered rule above; whether the campaign scales up or pauses on the
strength of this assessment is the Coordinator's and independent reviewers'
call, not this document's.

---

## 6. Trial count and scope actually run

- **Defect-injected arm**: 5,000 trials — within the pre-registered
  2,000-10,000 range for this pilot.
- **Paired undefected control arm**: an additional 5,000 trials at the same
  T, same parameter set, disjoint PRNG shard indices, the real unmodified
  `decode_blocks` — added so any measured deviation is attributable to the
  injection rather than to finite-T estimator behavior alone. This is
  additional to, not a substitute for, the defect-injected count above.
- **Parameter set**: PS-R3 only (`n_e = 56` order, `n=7187, omega=45,
  omega_r=omega_e=51, N=7168, m=17, dup=1`) — the order this campaign has
  used throughout. No other parameter set (PS-A/PS-R1/PS-R5) or any
  standardized HQC parameter set is run.
- **Shard indices**: chosen disjoint from every previously-recorded `T`-arm
  shard usage at PS-R3 found in this campaign's committed record
  (Stage-A: shards `0-3`, `900`; cost-model benchmark: shard `999`;
  `measure.py`'s T=1e7 run: shards `1000-1007`). This pilot uses shards
  `5000` (defected) and `6000` (undefected), both fresh under the `"T"` arm
  key derivation `stage_a.sha_key(ps["id"], "T", shard, MASTER_SEED)`
  `_t_shard` itself computes internally (unmodified) — draws at these shard
  indices have never been sampled before by any committed record in this
  read scope.

This is a **pilot**, not the full statistically-powered `T_req = 3.09e5`
run. No conclusion about detection power at the full scale is drawn from
whatever this pilot's small-T result is.
