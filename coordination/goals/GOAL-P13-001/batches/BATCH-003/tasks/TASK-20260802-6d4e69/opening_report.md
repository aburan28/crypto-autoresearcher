# TASK-20260802-6d4e69 — Opening report

**Goal** GOAL-P13-001 · **Batch** BATCH-003 · **Role** coordinator ·
**Date** 2026-08-02

**Deliverable frozen:** `experiments/EXP-PEC-49c773/specification.yaml`
(status `approved`, `frozen: true`, `supersedes: EXP-PEC-6be870`).

This task approved a superseding experiment contract. It ran no experiment,
produced no datum, changed no hypothesis status, promoted nothing, and lifted
no prohibition. **The contract contains no results.**

---

## 1. What is superseded, and why

`EXP-PEC-6be870` is **frozen and byte-unchanged**. Its `freeze_rule` makes the
remedy for a defect a superseding contract under a new id, never an edit, and
`DEC-20260802-8227b9` (status_transitions) recorded exactly that. Neither the
superseded contract, nor `RUN-PEC-6be870-a`, nor `EV-PEC-2e67ff`, nor either
BATCH-002 review report is touched by this batch. `RUN-PEC-6be870-a/raw-result.json`
is **read-only input data** to NC2b.

Seven items are replaced (`supersedes.what_is_replaced`, R-1 … R-7):

| id | replaced | driver |
|----|----------|--------|
| R-1 | the extrapolation law `c = gamma·log2(B_opt)/sqrt(log2 p)` | DEC adjudication A |
| R-2 | `fit_protocol.response` × `C-ALT.carry_forward_rule` × `execution_order` step 8 | DEC adjudication B; Validator F-1; RT2-C2 |
| R-3 | C-NULL placed before the optional extension | Validator F-3 |
| R-4 | the absent Cantor–Zassenhaus seed policy | Validator F-4 / Executor U-3 |
| R-5 | `gamma_A` and `gamma_B` reported on mismatched windows | Validator F-1 arithmetic |
| R-6 | the ell grid and j design (ell = 97 absent; extension IMPL-A only at 4 j) | DEC adjudication E; F-2 |
| R-7 | the fixed 8-draw cluster bootstrap | Validator F-7 |

Everything else is carried unchanged and enumerated in
`supersedes.what_is_carried_unchanged`: the counting unit and all counting
conventions, the **instrument itself** (`per_entry_cost.py`, imported read-only),
the instance and its `medium` claim tier, the sampling procedure and all nine
seeds, every control that passed, the OLS/bootstrap/jackknife battery, the
windows with W-MID primary, the curvature rule, the admissibility conditions,
assumptions L1–L4, and the non-claims.

---

## 2. The corrected law, and the intercept's p-scaling

```
c(level, series, window, alpha)
  = [ log2(A) + alpha·log2( log2(p_level) / log2(p_meas) )
      + gamma·log2(B_opt(level)) ] / sqrt( log2(p_level) )
```

`(log2 A, gamma)` are the intercept **and** slope of **the same OLS fit of the
same series over the same window**. A `pairing_rule` in the contract makes any
other combination — `gamma_B` with `A_A`, a W-TOP slope with a W-MID intercept,
a quadratic `gamma_local_top` with a linear intercept — **prohibited**. That
rule is the general form of the defect being repaired: adjudication A's defect
was the special case of pairing a measured slope with an *assumed* intercept
`A = 1`, which silently re-imposed the very Section 4.1 convention the
experiment existed to test.

### Decision on the p-scaling: **APPLIED, alpha = 1 primary; alpha = 0 always reported as a floor**

I read the committed instrument myself rather than accepting the red team's
derivation:

- `set_prime(p)` sets `Q = p*p` (line 70).
- `distinct_roots` computes `h = poly_powmod(xpoly, Q, f, mulf)` (line 411).
- `poly_powmod` takes `bits = bin(e)[2:]` and loops over `bits[1:]` (lines
  349–355) — one squaring per iteration, one extra multiplication per set bit —
  so its iteration count is `bit_length(Q) − 1 ≈ 2·log2(p) − 1`.
- `equal_degree_split` sets `e = (Q−1)//2` (line 381) and calls `poly_powmod` at
  that exponent for **every** Cantor–Zassenhaus attempt (line 394), again at bit
  length ≈ 2·log2 p.
- The cost of one polynomial multiplication **in the counted unit of F_{p^2}
  multiplications** is a function of polynomial degree alone, not of p.
- `instantiate` counts exactly `(ell+1)(ell+2)` and is **p-independent**.

Therefore `mults_rootfind(ell, p) = L(p)·R(ell)` with `L(p) ∝ log2 p`. **RT2-C1
and RT2-C3 are correct for this pipeline.** Because the factor multiplies the
whole cost curve, it shifts `log2 per_entry` by a constant at every ell: it is a
pure **level** effect, so it belongs in the intercept term with gamma untouched.
Applying alpha to `log2(A)` and not to `gamma·log2(B_opt)` is therefore not a
double count.

**Why alpha = 0 is not the honest default.** Section 4.1 charges one
F_{p^2}-operation per entry at the *actual* cryptographic p, so the comparand is
the per-entry cost at that p, in that unit. Reporting alpha = 0 as primary would
assert that the committed pipeline's per-entry cost is independent of p, which
the source above contradicts — a **new instance of the same class of error being
repaired**: discarding a term the code demonstrably contains. alpha = 0 is
nevertheless reported at every level as an explicit floor, correct only for a
hypothetical p-independent implementation.

**Status stated honestly.** alpha = 1 is **DERIVED**, not measured (assumption
L5); in the superseded run p was held at one value, so the p-axis had n = 1.

### Falsification conditions, fixed now

| id | condition | consequence |
|----|-----------|-------------|
| FC-1 | NC2b null gate missed | corrected law reported **FAILED**, not tuned; DEC prohibitions stand |
| FC-2 | C-PSCALE returns alpha interval disjoint from `[0.85, 1.15]` | alpha = 1 **falsified**; primary becomes alpha_hat |
| FC-3 | `max mults_instantiate/cost` over the fitted range > 0.05 | whole-intercept scaling **replaced** by the structure-aware form |
| FC-4 | measured alpha of the null differs from primary by > 0.15 | mechanism claim contradicted; reading labelled MECHANISM-INCONSISTENT |

FC-2 required a new, cheap control. **C-PSCALE** (new, budget-conditional,
non-gating) is a three-point p sweep at p ≈ 2^20, 2^30, 2^40 over
ell ∈ {3,5,7,11,13} at 4 j, plus the same sweep on the null object. It is nearly
free because Phi_ell is a p-**independent** integer polynomial: the
already-retrieved files are simply reduced modulo a different prime. This
converts alpha = 1 from a claim falsifiable only in a future batch into one
falsifiable **inside this run**, which is what a real pre-registration requires.
The `alpha_selection_rule` fixes in advance which reading is primary in each of
the four possible C-PSCALE outcomes, so no choice is left to be made after a
number is visible.

---

## 3. The NC2b self-validation gate (NC2b-G1)

- **Reference:** `REF_null` := median over the null's fitted ell of
  `log2(per_entry_null(ell))`. Because the null's per-entry cost is O(1) in ell
  **by construction**, this *is* the correct answer to "what per-entry overhead
  in bits does this object carry at ell = B_opt".
- **Estimator output:** `N_null(level)` := `log2(A_null) + gamma_null·log2(B_opt(level))`.
- **Criterion:** `|N_null − REF_null| ≤ 0.75 bits`, at **every** field size in
  the constants table, on **each** of the null's fitted windows.
- **Evaluated at alpha = 0**, deliberately: `REF_null` is a level *measured* at
  p_meas, and injecting an unmeasured p-extrapolation into a self-consistency
  check against a measured quantity would make the check untestable. alpha = 1
  null values are reported as a labelled, ungated diagnostic.
- **Tolerance derivation (from the null's own committed properties, not from a
  preferred answer):** the committed null's genuine level variation is 0.202
  bits over its grid (max/min 1.1506); the committed `gamma_null =
  −0.013241522288809005` induces at most `|gamma_null|·26.1 = 0.346` bits of
  drift at the largest field size; 0.202 + 0.346 ≈ 0.55, rounded up to **0.75**
  to absorb the choice of window and of central statistic.
- **Power:** the *superseded* law returns `N = gamma_null·log2(B_opt)`, at most
  0.35 bits in magnitude — about **11.9 bits** from `REF_null`, roughly sixteen
  times the tolerance. The gate discriminates decisively.
- **Failure consequence, binding and pre-registered:** *if the corrected
  estimator fails its own null it is as defective as the one it replaces and
  must be reported as FAILED, not tuned.* No variant may be searched for. The
  DEC-20260802-8227b9 prohibition on the superseded c values then stands
  unchanged and the batch's honest outcome is a failed repair.
- A missed gate is **explicitly not an invalidation** of the run: the
  measurement stands, the estimator does not.
- `NC2b-G1-prime` re-runs the identical gate on the **new full-range** null
  after NC2a, on all three windows, as confirmation.

### Pre-registration honesty, stated rather than glossed

The null series is already committed and I read `gamma_null` and the C-NULL
per-ell values while writing the contract. The gate is therefore **not a blind
prediction about unseen data**; it is an acceptance test on an estimator whose
formula, reference statistic, tolerance, evaluation level and *failure
consequence* are all fixed before the Executor computes anything. The
load-bearing pre-registration is the failure consequence. The contract says this
in `nc2b.preregistration_honesty` rather than claiming a blindness it does not
have.

---

## 4. NC2a: sample count, seam removal, and the pre-registered expectations

**Sample count fixed now: 8 j per ell, for BOTH implementations, across the
ENTIRE grid**, acquired in two ordered passes of 4 (`j 0..3` at every ell first,
ascending; then `j 4..7`). Rationale: a truncation inside pass 2 leaves a
**complete 4-j design across the full ell range** rather than an 8-j design
truncated in ell, so truncation can never reintroduce a j-seam. Pass-1 indices
`0..3` are exactly the superseded extension's indices, which is what makes
control C-REPRO possible.

**The seam is removed structurally, not procedurally.** A `membership_rule`
admits an ell to the fitted grid only if (C-1) both implementations have data
there, (C-2) at the identical j-set, (C-3) C-NULL has data there, and (C-4) it
passed C-BASE.2/.3. An ell failing any condition is **excluded**, not switched
to another definition. The superseded contract *switched* the response when data
were missing; this one *removes the point*. A definition evaluable only where its
inputs exist cannot change inside the range it is evaluated on.

**Exponent of record:** the **pair** `(gamma_A, gamma_B)` on a common window,
with `S-MIN` demoted to an attack-favourable diagnostic — per adjudication B's
repair, and because RT2-C4's ell-dependent term is 13.25 bits at gamma_A vs
11.26 at gamma_B; collapsing that to one number hides that the exponent is an
implementation parameter.

### Pre-registered expectations, each able to fail, each with a stated meaning

- **P1a** `gamma(S-MIN) ≤ max(gamma(S-A), gamma(S-B))` on the identical window.
  Labelled explicitly as a **consistency check, not a scientific prediction** —
  it is mathematically forced. Failure ⇒ the min construction or the fit code is
  defective ⇒ run **INVALID**, not a discovery.
- **P1b** `gamma(S-MIN, W-MID) ≤ 0.9382` (= the superseded homogeneous IMPL-A
  0.9332 + 0.005 for the addition of ell = 97, whose measured W-MID effect was
  0.0013). **This is the falsifiable scientific content.**
  *If it fails on a genuinely seam-free response:* the composition explanation of
  adjudication B is **INCOMPLETE** — part of the superseded elevation reflects a
  real steepening between ell = 101 and 211 that survives homogenisation.
  Adjudication B's arithmetic-impossibility core still stands (0.9739 exceeding
  both constituents remains impossible), but its **magnitude** claim weakens and
  c rises. Report it; the Coordinator re-adjudicates in the ledger archive.
- **P2** the seam-free W-ALL quadratic coefficient is **strictly below 0.0453**,
  the low end of the superseded mixed-response CI `[0.0453, 0.0625]`.
  *If it fails:* the curvature was **not** predominantly a composition artifact,
  and DEC-20260802-8227b9 **adjudication C is contradicted by new data** and must
  be re-adjudicated. This is a genuinely possible outcome and is named as one.
- **P3** on the common window, `gamma_A − gamma_B ≥ 0.10`. (The superseded
  0.1403 was computed on *mismatched* windows; the window-matched superseded pair
  over 11..101 is 0.9179 vs 0.7929 = 0.1250.) *If it fails:* the
  multiplication-routine effect is smaller over the wider range than the record
  suggested, RT2-C4's up-to-13.25-bit term must be re-scoped, and **NC2c's
  priority rises rather than falls.**
- **P4** the `{0..3}` j-subset refit moves each W-MID slope by < 0.010.
  *If it fails:* the `{0..3}` fit — homogeneous in j by construction — becomes the
  reported primary. Stated now so the choice cannot be made after the numbers.

---

## 5. Full-range C-NULL coverage (Validator F-3)

Fixed by **ordering plus membership**, so it cannot recur under any truncation:

1. NC2b in full (step 2, zero compute, written to disk by t = 600 s).
2. **Acquisition of the entire required grid completes before any measurement**
   (step 3), so the achieved grid is known before the null runs.
3. **C-NULL over every acquired ell at j 0..7 (step 5), before the primary
   measurement** (step 6). The null is linear in ell and cheap; running it first
   guarantees 100 % coverage of whatever the primary later achieves.
4. Membership condition **C-3** excludes any ell lacking null coverage from every
   window. Coverage is a precondition of membership, not a verdict recorded
   afterwards.

C-NULL's coverage must be reported as an **explicit fraction** of each fitted
window, not as a verdict word.

---

## 6. Validator F-4: the seeding decision

**Decision: the paired (shared) Cantor–Zassenhaus stream is RETAINED for the
primary series**, seeded on `(ell, j_index)` and not on implementation, with the
seed string recorded per sample.

**The trade, recorded in both directions.** Separate seeds buy *independence*:
`gamma_A` and `gamma_B` would become independent estimates and C-ALT.2 would
exercise the CZ recursion as well as the multiplication routine. Paired seeds buy
*variance reduction*: both implementations traverse identical split structures,
so `cost_A/cost_B` isolates the multiplication routine with no split-structure
noise, and the pointwise minimum defining `S-MIN` is taken between two costs on
the same algebraic path. NC2a's primary question is a **definition** question —
does the seam explain the inflated slope — and injecting split-structure variance
into exactly the comparison under test would degrade the discriminating power of
the one measurement this batch exists to make. The paired design is retained on
that ground.

**What is bought back instead:** new control **C-SEED** — at
ell ∈ {11, 23, 53, 101, 127, 211} × j ∈ {0..3} (24 pairs, spanning both sides of
the superseded seam), IMPL-B is re-run under a *different* recorded CZ stream
(IMPL-B'). This gives a genuine correctness cross-check of the shared pipeline
and the CZ recursion (the split structures now differ) plus an empirical bound on
split-structure variance. IMPL-B' never enters the primary fit.

**Binding consequence carried forward:** `gamma_A` and `gamma_B` remain
**non-independent**. No record under this contract may present their agreement or
their difference as agreement between two independent implementations.

---

## 7. ell = 97

**Re-acquired: YES.** Its absence was a transient `curl 35`; the BATCH-002
Validator independently re-fetched the URL (HTTP 200, 5 651 385 bytes, SHA-256
`093fead9…`), so recovery is known to be possible. Its measured effect on W-MID
was 0.0013 — about 2.5 % of the superseded half-width — so this is a
**completeness** decision, not a numerical one: it allows *this* contract's
completion gate to be met, which the superseded one's could not be.

It does **not** retroactively close `EXP-PEC-6be870`'s gate; that run is immutable
and its gate remains UNMET. If the fetch fails again it is an infrastructure
outcome, the grid proceeds with 25 core ell, this gate is UNMET and reported as
such, and the Validator's supplementary ell = 97 samples may **not** be
substituted (SP-5).

---

## 8. Other repairs pinned

- **C-REPRO (new):** every `(ell, j, impl)` triple overlapping `RUN-PEC-6be870-a`
  must reproduce **bit-for-bit** on every counted field. Any disagreement ⇒
  INVALID pending reconciliation. This is the only check that distinguishes a
  repair from a re-measurement, and it costs nothing — the values are computed
  anyway.
- **Common-window rule (R-5):** every cross-implementation quantity is computed on
  the set of ell where both implementations have data at the same j-set. Quoting
  `gamma_A` fitted on one ell set beside `gamma_B` fitted on another is prohibited.
- **Joint bootstrap (new):** the bootstrap must report the **joint** distribution
  of (intercept, slope) and the percentile interval of `log2(A) + gamma·log2(B_opt)`.
  Separate intercept and slope CIs would overstate the uncertainty of their sum,
  which is the quantity the corrected law actually uses.
- **Bootstrap draw count (R-7):** draws equal the size of the *common* j-set, not
  a fixed 8, removing the F-7 degeneracy.
- **Nested-window curvature with bootstrap CIs** on ell ≥ 11, 23, 43, 101 per
  series — adjudication C recorded that no homogeneous top-of-range curvature with
  adequate power exists anywhere in the record; this supplies it or shows it
  cannot be had.
- **Seam probe tail check:** the residuals at ell = 101 and 103 reported
  individually; on a seam-free response they must not be the two largest in the
  window.

## 9. Budget, stopping rules, tier, artifacts

5400 s / 8 GB / 1 run, with internal reserves (NC2b 600 s, acquisition 900 s,
null 600 s, pass 1 1200 s, pass 2 + controls 900 s, fits/artifacts/receipt
1200 s). Hard gates: NC2b written by t = 600 s or it is reported alone and the
run stops; no new measurement after t = 4200 s; pass 2 starts only if t < 2700 s
and aborts at t ≥ 3900 s; optional tail needs ≥ 1500 s, C-PSCALE ≥ 900 s. The
planning throughput (≈ 1.6 × 10^6 counted multiplications per CPU-second, from the
committed superseded receipt) is declared as an **assumption**, not a prediction.

**Claim-tier ceiling `medium`** (field_bits 80); C-PSCALE's 40- and 60-bit arms
carry `toy`; **the extrapolated c carries no tier at all** at any field size.

Ten artifacts are required: the eight queue-declared paths plus `stdout.log` and
`stderr.log`, which `tools/validate_ledger.py check_run` expects beside a
manifest. **Flag for TASK-20260802-18f85d:** the snapshot archive must stage all
ten, or the committed run package will carry new CI errors.

## 10. Non-claims

The contract's `non_claims` are binding on every downstream record. The two that
bound this batch most tightly:

- **NC2b changes an ESTIMATOR, not a measurement.** It produces no new datum
  about the attack and cannot by itself move any claim about it. A corrected c is
  a corrected *model substitution*.
- **NC2a re-measures at the same p over the same ell range.** It does not reduce
  the ~7.5 unmeasured octaves at NIST-I by a single octave, and it cannot
  discriminate between per-entry cost laws that agree over ell ≤ 251 and diverge
  at ell ≈ 2^14.

Also carried: gamma is an upper bound (unoptimised implementation, L4/RT2-C4 worth
up to 13.25 bits) *and* simultaneously a lower bound with respect to the excluded
costs; the two directions are **not netted**. Passing the null gate makes the
estimator *citable-subject-to-review*, not correct — only the Coordinator, in
TASK-20260802-c1f7c8 and after independent Validator and Red Team review, may
declare a c citable.

## 11. Standing prohibitions from DEC-20260802-8227b9 (restated, none lifted)

Restated inside the contract as SP-1 … SP-6 so the Executor cannot cite forbidden
values:

- **SP-1** `c = 0.864` (and 0.771 / 0.868 / 1.0389 / the `c_kappa` variants) may
  never be cited as an overhead **estimate** — only in a column labelled
  "superseded input being corrected", with adjudication A attached.
- **SP-2** `gamma = 0.9739`, `c_quad = 0.0488`, `gamma_local_top = 1.1706` may not
  be quoted without the seam statement **and** the homogeneous readings
  (IMPL-A 0.9332, IMPL-B 0.7929, curvature 0.0225 with CI [0.0194, 0.0366],
  `gamma_local_top` 1.0187).
- **SP-3** modelled margins quoted at **w = 2^30 only**; larger-w rows are not
  read as improvements.
- **SP-4** nothing in this batch moves `concrete_threat_nist1` off INCONCLUSIVE
  without clearing the irreproducibility band (2.2309 / 3.5133 bits); this batch
  is not designed to produce such evidence.
- **SP-5** the BATCH-002 Validator's supplementary measurements (its null over
  103..211, its ell = 97 samples) may not be cited as run evidence.
- **SP-6** `RUN-PEC-6be870-a` may not be described as having met its completion
  gate; the ell = 97 obstruction is never mathematical evidence.

Only the Coordinator may lift a prohibition, and only in the BATCH-003 ledger
archive after independent review. **No prohibition is lifted by this contract.**

## 12. Inventor-protocol Section 8 determination

**`proof_search_map_required: false`**, recorded with its reason rather than
omitted.

A `proof_search_map` is a hypothesis-level field required before approving
implementation or expensive experiments for a **proof-oriented** proposal — a
theorem, asymptotic bound, certificate family, reduction, or closure argument.
EXP-PEC-49c773 proposes none. It is (a) an arithmetic recomputation from committed
data under a corrected formula and (b) a bounded empirical re-measurement of an
implementation cost profile at the same scale as its predecessor. It advances no
asymptotic claim and closes no lane.

One component *is* argumentative: the alpha = 1 p-scaling (L5) is a **derivation**
about committed code, and adjudication A's own refutation artifact was labelled
`derivation`. That is below the proof-oriented threshold — it is checkable by
reading the source — but argumentative enough that the four audits are addressed
inline rather than silently omitted, and that C-PSCALE was added so the derivation
acquires an **in-batch** empirical falsifier rather than only a deferred one.

Audit dispositions (in the contract, `section_8_determination.audit_dispositions`):

- **Baseline reproduction — DISCHARGED AND STRENGTHENED.** C-BASE.4 (exact PoC
  `count()`), C-BASE.6 (unit alignment, `gamma_paper = 0`), and now **C-REPRO**:
  the baseline reproduced is both the external reference and this programme's own
  prior run.
- **Observation collision — APPLICABLE, NOT CLOSED**, and a *second* collision is
  newly named and partially closed: at a single p, "the intercept is a constant"
  and "the intercept is linear in log2 p" are observationally identical — which is
  precisely why the superseded record could not settle alpha. C-PSCALE is the
  discriminating control and is in this contract. The batched-evaluation collision
  remains open; NC2c is its separator.
- **Quantifier order — STATED.** Supported: "for THIS implementation pair, at
  THIS p, there exists gamma such that for all ell in the measured range,
  per_entry ≈ A·ell^gamma". The uniform form is not supported — which is exactly
  why the contract reports `(gamma_A, gamma_B)` as a pair rather than one exponent.
- **Method ceiling and nearby object — ADDRESSED.** C-NULL is the nearby object
  where the growth must not appear, and here it takes a second role as the
  acceptance object for the **estimator** — "controls before belief" applied to the
  inference layer rather than to the signal. C-PSCALE's null arm is the nearby
  object for L5 (FC-4). The method ceiling is unchanged: it bounds the per-entry
  exponent of an *unoptimised* implementation from above and can never lower-bound
  the cost of an optimal one.

## 13. Inference provenance

`requested_policy: coordinator-orchestration-code`; `fallback_used: true`
(Claude Code cannot resolve the GPT-5.6 policy aliases; `.claude/agents/*.md`
carry `model: inherit`); `degraded_allowed: true`; `model_verified: false`;
`inference_amendment: INFAMEND-20260802-P13-002`. Degraded requirements recorded:
`review-adversarial` xhigh and `executor-implementation` medium are **UNVERIFIED**
rather than asserted as met, because this harness cannot set or verify a
subagent's effort tier. Not degraded: independent-session requirements are
genuinely satisfied for the BATCH-003 Validator and Red Team tasks. No task in
BATCH-003 may claim a `review-breakthrough` tier, which is non-degradable.

## 14. Next action

`TASK-20260802-b33bd4` — snapshot-archive `experiments/EXP-PEC-49c773/specification.yaml`
alone, before the Executor recomputes anything, so the corrected law cannot be
adjusted to produce a preferred `c`. Record the `origin/main` base commit checked
and the merge outcome in the receipt.
