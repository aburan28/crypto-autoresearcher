# TASK-20260727-004 — adversarial notes on EXP-IC-002

Bound to snapshot commit `6e6fd28e5b6c3ae889053212dc8b13d44e5d2677`
(parent `2bb6487ab759eab7a5174fce127166e0afffb452`, branch `claude/ecdlp-batch006`).
Receipt re-derived from Git, not trusted: parent matches, exactly three paths, all
three blob SHA-256 reproduced, commit reachable from HEAD, task and record IDs in the
message. `docs/target-result-profile.md` confirmed **absent** at this commit; its rule A1
is applied as governing and the path is not cited as present.

Verdict: **REVISE**. Nothing below authorizes execution, changes a status, or edits an
artifact under review.

---

## 0. The thing I found that nobody asked me to look for

I set out to check the reachable-set bound against `harness/semaev.py` and ended up
checking whether the premise of the whole batch is true. It is not.

I read `metrics.decomposition_found`, `metrics.is_trivial_ideal` and
`certificate.{kind,verified}` out of all 748 `experiments/EXP-IC-001/runs/*/raw-result.json`
files at this commit. The certificate census is `{none: 646, decomposition: 68,
discrete_log: 34}`. Sixty-eight runs — 34 fixed-mode and their 34 naive-mode twins —
carry `decomposition_found: true`, `is_trivial_ideal: false`, and a certificate of kind
`decomposition` with `verified: true`.

| bits | seed | N | fixed-mode decompositions |
|---:|---:|---:|---:|
| 8 | 1 | 23 | 9 / 10 |
| 8 | 2 | 41 | 9 / 10 |
| 8 | 3 | 5 | 10 / 10 |
| 12 | 1 | 31 | 1 / 10 |
| 12 | 2 | 37 | 2 / 10 |
| 12 | 3 | 2377 | 2 / 10 |
| 16 | 3 | 479 | 1 / 10 |

Against that, the record says:

- `EV-IC-001` certificate_refs: *"All decomposition runs found no decompositions;
  certificate kind=none, verified=true."*
- `EV-IC-001` boundaries line 55: *"all Groebner solves on trivial ideals (no
  decompositions)"*
- `DEC-20260726-005` limitations: *"all Groebner solves on trivial ideals"*
- `EXP-IC-001/analysis.md`: *"all Groebner solves return trivial ideals (no
  decompositions)"*
- `dispatch_queue.json` batch-opening rationale and goal note `INT-BATCH006-003`: the
  same quotation, used as the reason to open the batch.
- `EXP-IC-002` objective: *"No decomposition ever occurred in the 748 runs that
  DEC-20260726-005 used to conclude support."*

Only `H-IC-001`'s own interpretation_limits get it nearly right — *"T_desc is measured on
trivial ideals (no decomposition found) at bits >= 16"* — and even that is off by the one
16-bit instance.

This is not a pedantic correction. `CTRL-G` requires the run to *"reproduce the '0
decompositions' recorded across all 748 EXP-IC-001 runs"*, and stopping rule 4 says a
CTRL-G disagreement means *"stop immediately and return the run to the Coordinator as a
source-integrity failure rather than continuing."* Executed exactly as frozen, the primary
arm halts on instance 1 of 34 and produces nothing.

The correction does **not** rescue the crossover. All 27 other instances, including
36-bit seeds 2, 5, 10 and 11 — the four that carry `DEC-20260726-005` — genuinely have
zero decompositions. What it destroys is the absolute framing, and what it hands back is
the yield *measurement* the design says it lacks.

---

## 1. Strongest case that the design cannot decide anything

### 1.1 The success criterion is arithmetic where it matters

The spec's `empirical_content_disclosure` deserves credit: it says outright that SC3 and
SC4 follow from SC1 and SC2, and that "no result of this experiment may be reported as
measurement where it is arithmetic." I verified the algebra and it is right.

`charged_ratio_lower_bound = T_attempt · sqrt(N) / |S|`. From the committed records,
`T_attempt` spans 30110–35617 group-op equivalents (1.18×), Groebner wall time spans
0.038–0.044 s across **all 34 instances** (1.15×, over N from 5 to 3.4·10¹⁰), and
`|S| ≤ 392` by combinatorics. `sqrt(N)` spans 2 to 183757. So `log(charged_ratio)` is
`log sqrt(N)` plus a residual bounded by `log(1.18 · 2)`; Spearman ≥ 0.9 is forced and the
required 10× rise is exceeded by three orders of magnitude. SC3 is forced the same way:
`T_attempt·N/|S| ≥ 76·N > sqrt(N)` for all `N ≥ 1`.

Where the disclosure stops short: **SC2's second clause is arithmetic too.**
"`p_dec_target_set_empirical = 0` at every instance with N ≥ 10⁹" is a recomputation of a
fact already in the committed run records, and the recomputation is byte-for-byte the same
code path (`_find_decomposition`) that produced the record.

### 1.2 F2 is decorative — and the stopping rules prove it

The spec insists *"F2 is a genuinely possible outcome."* Trace it.

`p_dec_target_set_empirical > 0` at an instance ⟺ some committed target lies in S ⟺
`_find_decomposition` returns True on it ⟺ CTRL-G disagrees with the committed record ⟺
stopping rule 4 fires ⟺ the run is halted and *"reported as such rather than
interpreted."*

So F2 and "CTRL-G integrity failure" are the *same event*, and the spec assigns them
contradictory dispositions: F2 says the confound claim is wrong and H-IC-001 stands;
stopping rule 4 says do not interpret it at all.

There is exactly one crack. `_find_decomposition` gates the sign search behind
`if s3_eval(a, b, v1, v2, xR, p) != 0: continue`. If that filter were incomplete, a target
could lie in S (per a direct enumeration in `ic_yield.py`) while `_find_decomposition`
reported False in both EXP-IC-001 and CTRL-G. Then F2 fires and CTRL-G passes. But that
outcome is an **instrumentation defect**, not the "confound claim is wrong" finding F2 is
labelled with. Fixing the premise (§0) does not close this: the corrected record still
shows zero decompositions at every N ≥ 10⁹.

**Conclusion: at the four instances that carry the decision, EXP-IC-002 has no reachable
falsifier.**

### 1.3 CTRL-D cannot fail, by the spec's own argument

CTRL-D perturbs the calibration by 10× and 0.1× and requires the trend sign in
`T_desc_charged / sqrt(N)` not to change. The spec explains why: the calibration
*"multiplies charged and uncharged costs identically."* Exactly — so the trend sign is
invariant under any positive rescaling. This is an algebraic identity dressed as a
control, occupying one of four run arms.

Worse, the quantity that *is* calibration-sensitive is not tested. The **uncharged** K*
finiteness — the thing `DEC-20260726-005` actually rests on — depends on the calibration
directly. The 34 committed rho manifests give calibration factors from 554,930 to
1,477,926 group-ops/s: a 2.66× spread that is pure Python-overhead noise, and which moves
the crossover threshold in N by 7.1×.

### 1.4 Seven instances break the metric definitions

`t_desc_charged_lower_bound := T_attempt · N / |S|` is described as *"a LOWER bound on the
charged descent cost."* The true charged cost is `T_attempt / P_dec ≥ T_attempt` for every
`P_dec ≤ 1`. So whenever `N < |S|`, the "lower bound" sits *below* `T_attempt` and is not
a lower bound on anything.

From the committed rho manifests, **7 of 34 instances have N < 420**: N = 5 (8-s3), 23
(8-s1), 23 (16-s1), 31 (12-s1), 37 (12-s2), 41 (8-s2), 349 (24-s3). At N = 5 the metric
undershoots by roughly two orders of magnitude. Simultaneously
`p_dec_counting_bound = |S|/N` exceeds 1 and stops being a probability. These defective
values are then fed to the SC4 Spearman over all 34 instances.

### 1.5 SC1's only genuinely empirical clause can fail for an irrelevant reason

SC1 has two parts. `|S| ≤ 420` is a **theorem**, not a measurement — no correct
enumeration of ≤105 unordered pairs × 4 signs can produce more — and the spec's own
invalidation rule converts any violation into "implementation defect", so F1 is
definitionally unreachable.

The second part, "max |S| over 8-bit and over 36-bit differ by less than 2×", is genuinely
empirical and **genuinely at risk for a reason that has nothing to do with the claim**.
`|S| ≤ min(392, #E − 1)`. At 8 bits the committed primes are p = 137, 163, 241, so #E is
roughly 115–273 and the curve-order term binds, not 392. Under an occupancy model
(392 signed sums into #E slots) the 8-bit maxima land in the high 100s while 36-bit lands
near 392 — a ratio within a few percent of the 2× threshold, on either side. A pigeonhole
failure would sink an ALL-FOUR success criterion and mean nothing.

*(That last paragraph is an analytic prediction, not a measurement. I did not enumerate S.
It is offered as a design risk to be removed by conditioning SC1 on `min(392, #E − 1)`,
not as a result.)*

### 1.6 Degenerate instances are treated as ten independent targets

`_derive_targets` computes `k = ((idx+1)·stride) mod (n−1) + 1`. At 8-bit seed 3, N = 5,
and the ten committed `target_k` values are `3,1,3,1,3,1,3,1,3,1` — two distinct targets
repeated five times. `p_dec_target_set_empirical` there has effective n = 2.

### 1.7 The bound is not tight and the invalidation threshold is set at the wrong number

`4·(C(14,2)+14) = 420` is a valid upper bound, and I confirm the sign correction against
`IDEA-20260727-002`'s 105: `_find_decomposition` really does iterate `for v2 in V[i:]`
(unordered pairs including `i = j`) and really does try `for sA in (A, negate(A)): for sB
in (B, negate(B))`.

But 420 is not tight. For the 14 diagonal pairs the four sign combinations give
`{2A_i, O, O, −2A_i}` — at most **2** distinct non-identity points, and the spec's own
procedure says to drop the point at infinity. The tight maximum is
`4·C(14,2) + 2·14 = 364 + 28 = 392`.

Direction: 420 > 392 **overstates** the reachable set, hence overstates yield and
understates the charged cost by ≤ 6.7%. That is the conservative direction — the spec's
claim that the correction biases the test *against* the confound claim is correct, and the
7% is immaterial against 76× and 10⁴× effects. But the invalidation rule "a measured |S|
exceeding 420 is an implementation defect" now lets 393–420 through, and every value in
that range is necessarily defective.

Separately: the `s3_eval` pre-filter appears nowhere in `counting_derivation`, even though
the queue's own constraint asked for a line-by-line check. The bound survives — S₃
vanishing is *necessary* for `±A ± B = ±R`, and S is closed under global negation, so the
filter cannot reject a true hit — but the spec asserts the code path without recording the
filter, and no control tests its completeness. That untested assumption is the sole route
to F2 (§1.2).

---

## 2. Strongest case AGAINST the confound claim

I argued this before concluding, as required.

1. **Its stated form is false.** "No decomposition ever occurred" is contradicted by 34
   verified certificates. A claim whose headline does not survive contact with its own
   inputs starts at a deficit.

2. **The confound EV-IC-001 actually flags is already refuted by the committed data, in
   H-IC-001's favour.** `EV-IC-001` lists as an unresolved confound: *"T_desc on trivial
   ideals may not represent non-trivial Groebner systems."* From the 340 fixed-mode
   records: pooled median `groebner_seconds` is **0.040484 s over 306 trivial solves**
   versus **0.038775 s over 34 non-trivial solves** — ratio **0.958**. Non-trivial systems
   are, if anything, marginally *faster* at this parameterization. EXP-IC-002 neither
   computes nor cites this, though it costs zero runs and it defends the target.

3. **The counting content is not new — it is already in H-IC-001.** The mechanism states
   `P_dec ~ B²/N` and derives `S_rel = (N/B)·T_desc` from it. `B² = 196` versus the
   sign-corrected `|S| ≤ 392`: a factor 2. So SC1 and SC2 confirm an assumption the
   hypothesis already commits to.

4. **H-IC-001 never claimed a cryptanalytic advantage.** It calls itself
   implementation-bound. `DEC-20260726-005`'s own next_actions record that K* ≈ 3–5·10⁸
   and *"provides no practical advantage at toy scale."* Spending the last batch to weaken
   a claim that already disclaims itself is poor allocation.

5. **B = 14, m = 2 is not an index calculus.** A real point-decomposition index calculus
   sizes B against N so the yield term is not dominant (over F_{q^n}, B ~ q and m = n give
   `P_dec = Θ(1/n!)`). Charging yield at a *fixed* B = 14 proves the tested
   **configuration** useless. It does not prove the multi-target crossover false. The
   spec's `interpretation_limits` say exactly this, and they are right.

### Why the confound nevertheless stands where it matters

The durable point is not "no decompositions". It is that **H-IC-001's cost model is
internally inconsistent**. The same operation — *try randomizations until the target
decomposes over V* — is charged **with** yield inside `S_rel = (N/B)·T_desc` and **without**
yield inside `K·(T_desc + T_verify)`. One of the two is wrong. Since no attempt succeeded
at any instance with N ≥ 10⁹, the recorded `T_desc` is the cost of one *failed* attempt,
so the per-target term is the wrong one.

That correction is a **derivation from H-IC-001's own assumptions**. It needs no run at
all. Which is precisely why spending four run arms on it is defensible only to the extent
that SC1/SC2/F2 add something — and §1 shows that at the decision-bearing instances, they
do not.

---

## 3. The objection that dominates both sides: no multi-target baseline

My role contract requires comparison against Pollard-rho, BSGS, **and the closest
specialized baseline**. `CTRL-E` supplies the first two. Both are *single-target*
algorithms. `H-IC-001` is a fixed-curve, K-target amortization claim. The closest
specialized baselines are absent from both experiments.

### Baseline 1 — exhaustive log table (fully explicit, no citation risk)

Precompute all N multiples of P: `N − 1` group additions, N stored elements. Every
subsequent target is a lookup, 0 group operations.

EXP-IC-001 charges `S_rel = (N/B)·T_desc_gops`, so

```
S_rel / N  =  T_desc_gops / B
```

which is **independent of N** and equals **2151–2544** at the four headline instances
(`T_desc_gops` 30110–35617, B = 14). The index-calculus precomputation is therefore
~2.2·10³–2.5·10³ times *more* expensive than enumerating the entire group, at **every one
of the 34 instances**, and the per-target cost is 32023 group ops against O(1).

The scheme is dominated in **both** terms, uniformly, by a first-week algorithm. A "finite
K*" against rho under those conditions is cryptanalytically vacuous.

### Baseline 2 — the preprocessing frontier the repo already cites

`knowledge/literature/KN-LIT-013.md` (Corrigan-Gibbs & Kogan, EUROCRYPT 2018) records
`S·T² = Ω̃(εN)` and that *"the bound is essentially tight via a matching generic
algorithm."* `H-IC-001`'s own assumptions name this as the correct reference frontier.
Balance at `S = T = N^{1/3}`: online cost `N^{1/3}` per target, advice `N^{1/3}` elements.

| instance | N | N^{1/3} | T_desc_gops | frontier cheaper per target |
|---|---:|---:|---:|---:|
| 36-bit seed 2 | 33,766,959,953 | 3232 | 32021 | 9.9× |
| 36-bit seed 5 | 11,875,729,387 | 2281 | 30110 | 13.2× |
| 36-bit seed 10 | 3,480,617,339 | 1515 | 35014 | 23.1× |
| 36-bit seed 11 | 17,366,619,409 | 2590 | 33191 | 12.8× |

At **all four** headline instances `N^{1/3} < T_desc_gops`. Substituting the correct
multi-target baseline for `sqrt(N)` in
`K* = ceil((S_rel + S_LA)/(baseline − T_desc − T_verify))` gives a **negative denominator**:
`K* = ∞`, **uncharged**, with no yield model, no new run, and no appeal to the
zero-decomposition confound at all. The advice is 1515–3232 elements — trivially small.

Honest caveat: CGK's offline phase is unbounded, so this compares online cost and advice
size, not offline time. Baseline 1 has fully explicit offline cost and already suffices.

**Against the correct baseline for the regime H-IC-001 is stated in, the crossover does not
exist and never did.** That is cheaper, more decisive and less contestable than the yield
charge — and it is missing from both experiments.

---

## 4. The near-tautology charge (the highest-value question)

**Adjudication: the "4/4" is an arithmetic consequence of its own conditioning. The
Coordinator's allegation is correct and understated.**

Let `A = {sqrt(N) > T_desc_gops}` (the v3 conditioning event) and `B = {K* finite}`. From
`EXP-IC-001/specification.yaml` metrics.crossover_K_star, K* is finite exactly when
`T_desc_gops + T_verify < sqrt(N)` with `T_verify = 2` frozen. So
`B = {sqrt(N) > T_desc_gops + 2}`, `B ⊆ A`, and

```
A \ B  =  { T_desc_gops < sqrt(N) ≤ T_desc_gops + 2 }
```

— a window **two group operations wide** against a `T_desc_gops` of ~3.2·10⁴. The v3
criterion asks for `|B| / |A| ≥ 2/3`. It conditions on a 2-operation dilation of the
outcome variable and then reports the outcome rate. That is **selection on the dependent
variable**, and the reported ratio is 1 unless an instance lands in the window.

Margins for the four conditioning-set members, from the committed 36-bit table:

| seed | sqrt(N) | T_desc_gops | margin | window |
|---:|---:|---:|---:|---:|
| 2 | 183757 | 32021 | 151736 | 2 |
| 5 | 108975 | 30110 | 78865 | 2 |
| 10 | 58996 | 35014 | 23982 | 2 |
| 11 | 131782 | 33191 | 98591 | 2 |

The narrowest margin is **1.2·10⁴ times wider** than the failure window. Per instance the
chance of failure is ~2/32000 ≈ 6·10⁻⁵; the chance of falling below the 2/3 threshold
(≥3 of 4 failing) is ~10⁻¹¹. The observed *"4/4 = 100% >> 2/3 threshold"* in `EV-IC-001`
lines 38–41 carries on the order of **10⁻⁴ bits** about H-IC-001.

**It is worse than "near-tautological", because of how it got there.**
`EXP-IC-001/analysis.md` lines 51–54 record that the v2 criterion was **not met** and
*"the result is inconclusive."* `amendments/v2_to_v3.yaml` then revised the criterion,
citing the observed 4/13 and 4/4 in its own `reason` field, into a form that essentially
cannot fail. `EV-IC-001` reports the revision as *"SUCCESS CRITERION MET"* and
`DEC-20260726-005` rationale item 1 is precisely that met criterion.

**What survives as genuine measurement in EXP-IC-001** (I do not dispute these): the
magnitude of `T_desc_gops` (~3.0–3.6·10⁴), and the fact that A is non-empty — 4 of 13
random 36-bit curves have `isqrt(N)` above that constant. The narrowest honest restatement
is: *"sympy's Buchberger on this fixed 2-variable degree-14 system costs ~0.04 s, equal to
~3.2·10⁴ Python group operations, and 4 of 13 random 36-bit curves have an isqrt(N) above
that number."*

### Amendment integrity (Q5)

`docs/task-lifecycle.md` §5, line 47 at this commit: *"Exploratory changes must be labeled
exploratory and cannot be evaluated against the original confirmatory criterion."*

`v2_to_v3.yaml` revised the criterion **after** the original was observed to fail, and its
own `reason` field uses the observed outcome as the justification. It is an exploratory
change by the plain text of the rule. `confirmatory_status: preserved` is the one status
the rule excludes; `exploratory_only` (or `reset` with a fresh pre-registered run set) is
defensible. `affected_runs: []` is also misleading — no run needs re-execution, but **all
748 preceded the amendment**, which is exactly what makes the change exploratory.

By contrast `v1_to_v2.yaml`'s `preserved` **is** defensible: it repaired five blocking
review objections before execution, with no outcome observed.

Consequence: with v2→v3 correctly labelled, `EV-IC-001`'s "SUCCESS CRITERION MET" cannot be
read as a confirmatory result, and `DEC-20260726-005` rationale item 1 loses its support
independently of anything EXP-IC-002 measures. That is a finding about the ledger. Only the
Coordinator may act on it.

---

## 5. Does the missing `run_ids` block this review?

No. `EV-IC-001`, `EV-STR-002` and `EV-GGM-001` all carry `run_ids: []` while citing 748, 22
and 9 runs — AGENTS.md rule 10 unmet. But the EXP-IC-001 run directories exist at this
commit; I enumerated all 748 and read every field the reuse contract depends on. The 34 rho
manifests carry `parameters.prime_order_n`, `metrics.total_group_operations` and
`timing.wall_seconds`; the fixed-mode raw results carry `raw.factor_base`, `raw.target`,
`raw.target_k`. I spot-checked three instances (36-s2, 36-s10, 8-s3) and each has a single
byte-identical factor base across its 10 fixed runs, so the spec's factor-base invalidation
rule will pass. The reuse contract is feasible as written.

It does mean the *committed* records are non-compliant, and `EV-IC-002` must not repeat it —
which the queue already requires of TASK-20260727-009.

---

## 6. What I did not do

- Enumerated no reachable set, ran no solver, timed nothing, created no run record.
- Made no commit; touched nothing in `/Volumes/Volume/crypto-autoresearcher`.
- Changed no hypothesis, goal, evidence or decision record; edited no artifact under review.
- Every number above is either read from a committed record at `6e6fd28e` or arithmetic I
  performed on such numbers and labelled as derivation. The §1.5 occupancy argument is
  explicitly a prediction, not a measurement.
- Requested policy `review-xhigh` (GPT-5.6 Sol, xhigh, per `orchestration/model-policies.yaml`
  line 44). Resolved model: `claude-opus-5` under the Claude Code runtime.
  `fallback_used: true`. **No equivalence to `review-xhigh` is claimed**, and none can be
  verified from this session.

---

## 7. Single recommended action

Before any execution, issue **one** versioned `protocol_amendment` at
`experiments/EXP-IC-002/amendments/v1_to_v2.yaml` with
`confirmatory_status: exploratory_only`, that:

1. replaces the false "zero decompositions across all 748 runs" premise (objective,
   `contrast_with_ev_ic_001`, CTRL-G, SC2, alternative_outcome A1) with the verified
   per-instance table in §0, so stopping rule 4 does not halt the primary arm;
2. records that F2 is unreachable at N ≥ 10⁹ and confines the genuinely empirical content
   to the seven instances with N ≤ 2377;
3. caps `p_dec_counting_bound` at 1 and floors `t_desc_charged_lower_bound` at `T_attempt`;
4. adds **CTRL-E2** — the exhaustive-table and `S·T² = Θ̃(N)` at `S = T = N^{1/3}`
   multi-target baselines, closed form from committed numbers, zero runs;
5. tightens the `|S|` invalidation threshold from 420 to **392**.

Then re-review in a non-originating session.

Correcting the immutable records that carry the false premise — `EV-IC-001`,
`DEC-20260726-005` limitations, `EXP-IC-001/analysis.md`, goal note `INT-BATCH006-003` —
is a **superseding-record** task for the Coordinator at TASK-20260727-009. It is
explicitly **not** authorized here, and none of those records may be edited in place.

---

## 8. Claim boundaries this review must not be read past

- Maximum tier **toy**. Largest tested subgroup order 3.4·10¹⁰ (~35 bits).
- Not target-class **in either direction**, under the rule quoted in goal note
  `INT-BATCH006-002`: no asymptotic exponent and no central structural barrier moves
  whether H-IC-001 is supported, weakened or rejected at B = 14, m = 2.
- Not an ECDLP result, not a closure, not an impossibility result, not a cryptanalytic
  improvement, not evidence about index calculus in general or about any other (B, m),
  solver, field family or deployed parameter size.
- `K* = ∞` here would be a statement about a configuration that essentially cannot
  decompose — not a proof that multi-target amortization is impossible. The controlling
  references remain `S·T² = Ω̃(N)` (KN-LIT-013, KN-TECH-005) and the Shoup bound.
- The 34 verified decompositions I report are a re-derivation from committed records, not a
  new measurement, and concern only instances with N ≤ 2377.
