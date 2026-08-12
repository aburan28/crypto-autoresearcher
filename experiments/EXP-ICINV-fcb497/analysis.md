# EXP-ICINV-fcb497 — analysis

- **Experiment** `EXP-ICINV-fcb497` v1 (frozen contract, approved by `DEC-20260807-1538f8`)
- **Hypothesis** `H-ICINV-82ee6a` · **Question** `RQ-ICINV-475b5e` · **Goal** `GOAL-ENDO-001`
- **Evidence** `EV-ICINV-c68f13` · **Decision** `DEC-20260807-4261e3` (`replicate`)
- **Parent proposal** `IDEA-20260807-9fb27c`
- Written by: coordinator, 2026-08-07

> **Provenance of this file.** Sections 1–4 below are the analysis document required by
> `/review-evidence` step 2. The reviewing Coordinator subagent could not write to this path
> under the current harness (two attempts, both refused), so the document was materialised by
> the dispatching session from the reviewing Coordinator's own returned content, which is
> archived in full in `EV-ICINV-c68f13` (`observations` OBS-1…OBS-12, `inference`,
> `boundaries`, `unresolved_confounds`, `validity_determination`) and
> `DEC-20260807-4261e3` (`rationale`, `limitations`). Where this file and those records
> differ, **the ledger records govern** — they are the official artifacts and this is a
> reading view onto them.

---

## 0. Validity determination — settled before any number was interpreted

**VALID AND COMPLETE** against the frozen contract.

13 run directories present and matching the reported tally. 13/13 manifests schema-complete
with `code.source.all_pinned: true`, an `inference` block, `resources.memory_reconciliation`
and `result.certificate`; `tools/check_run_source_provenance.py --strict` exits 0 with 13
pinned, 0 unpinned. Seeds and the prime ladder certified at run time, with the k = 24 stream
head reproduced from the recorded seed. Raw-versus-summary agreement spot-checked to full
precision — k14 seed 20260807 median `0.6147614403434642` and `ks_D` 0.121 are bit-identical
between `RUN-ICINV-kf-stage3-k14/distributions.json` and
`RUN-ICINV-kf-decide/decision-rule-evaluation.json`. Controls comparable: the null is matched
on the same `d`, one draw per instance, the identical code path, written and re-read from disk
before the KS statistic, with hashes and timestamps recorded so the ordering is auditable
rather than asserted. `invalidations_fired` is empty as computed inside the run.

### D1 — thirteen runs against a frozen `maximum_runs: 12`

**Accepted as a disclosed deviation. Explicitly NOT retroactively authorised, and no amendment
filed** — an amendment written now could only pretend to have permitted what it did not permit.

Root cause is a **defect in the frozen contract itself**: `required_artifacts` and stopping
rule SR7 both demand the aggregate `decide` run, while `budget_note` enumerates only 10 core
runs. The true core count is 11; 11 + 2 headroom = 13.

Invalidating the excess was rejected on two checkable grounds:

1. Invalidation is the remedy for a defect in a *measurement*, and none exists. Every
   invalidation rule was evaluated inside the run and none fired. A budget-enumeration
   shortfall is not evidence that a number is wrong.
2. The thirteenth run is `RUN-ICINV-kf-decide`, which computes the frozen decision rule.
   Discarding it deletes the very artifact SR7 exists to produce and hands terminal-state
   selection back to a human *after* the data were seen. Enforcing a run cap by destroying the
   anti-outcome-shopping artifact is a worse breach than the overrun.

Recorded as fact rather than excuse: no *resource* cap was approached (25.1 s wall, 0.007
CPU-hours, 99 MB peak RSS against 7200 s / 6 CPU-hours / 4 GB); all 13 runs retained; both
superseded runs are evidentially inert — M0 is `AMBIGUOUS` in both STAGE-0 runs and M4 is
`177 / 0 / 127` in **both** STAGE-1 barrier tables, verified by direct read of each.

### D4 — completion gate G9 PARTIAL

**Accepted as an artifact-completeness defect. No corrective run ordered.** Confirmed by
direct read: `tail-checks.json` T5 carries `analytic_peak_bytes: 93339648` with its band and
components, but no measured value and no ratio. The substance is present and
reviewer-recomputable in all 13 manifests (decide run: 63 553 536 measured / 93 339 648
analytic / ratio 0.6809 / `within_band: true`), with all 13 ratios in [0.68, 1.74] against the
declared [0.25, 4.0]. Success criterion (S-i) is met; (S-j) is partial at the file level for
T5 only. A corrective run would spend a run against an already-exceeded cap to copy verified
numbers into a second file.

### D9, D10 — write scope and deliverable path

D9 accepted: the defect is the handoff's narrow `write_scope`, not the artifact. D10 accepted
and **the Executor's refusal endorsed** — minting a `BATCH` id inside an execution task would
have been the worse error, so the execution report is archived beside the contract it executes.

---

## 1. Observation

**OBS-1 — STAGE 0 is undetermined, and that is an infrastructure outcome.**
`M0_stage0_field_verdict: AMBIGUOUS`; M8 `terminal_state: S0-UNDETERMINED`. Landing pages for
eprint 2020/341 and 2020/1109 retrieved HTTP 200 and pinned (text sha256 `15a4c1c9…` and
`257f3321…`). **Both PDFs returned HTTP 403** behind a Cloudflare interstitial; their response
bodies are pinned as evidence of the failure. The frozen contract requires a full text for a
determinate verdict and caps the `KN-LIT-780` fallback at `AMBIGUOUS`-only. Per AGENTS.md rule
5 the 403 is never negative mathematical evidence and never a `BASE_FIELD` verdict.

**OBS-2 — the one passage that mechanically classifies the count is not a verdict.**
At byte offset 1160 of the pinned 2020/341 **landing-page** text (sha256 `15a4c1c9…`),
`verified_exact_substring: true`, both the windowed and the document-aware classifier label it
`kernel_field`. It sits on an abstract, not a full text. The Executor recorded it and refused
to promote it; the dispatching session independently recomputed the hash and re-tested the
substring at offset 1160 before archiving. 31 passages extracted, 20 operation-count
statements, 0 failing byte verification.

**OBS-3 — controls, all blocking, all PASS.** Planted positive control returns `m = 2` exactly
on all ten frozen `r` (3, 5, 7, 11, 17, 33, 65, 129, 1025, 65537), `d` from 8 to 4 295 098 368,
with `pow_check`, `minimality_check` and `order_verification_ok` true on every row. The `m = 1`
nearby-object fixture passes through `harness.exp_kerfield.multiplicative_order` — the same
code path as STAGE 3 — with `m ∈ {1, 2}`, the eigenvalue case declared by the eigenvalue
computation, and the cost formula degenerating to `Õ(√ℓ)`. **The argument does not prove too
much.**

**OBS-4 — sample and integrity.** Seven decades at p = 4093, 16381, 65521, 262139, 1048573,
4194301, 16777213 (largest prime strictly below 2^k, k ∈ {12,14,16,18,20,22,24}, certified at
run time by `sympy.isprime` BPSW with `nextprime(p) ≥ 2^k`). Three seeds, n = 1000 in every one
of the 21 decade-seed cells, 7 of 7 decades verdict-yielding at the 400-instance floor.
`degenerate_fraction` 0.000 in all 21 cells; `excluded_curve_fraction` in [0.000, 0.006] with
reasons recorded (singular, supersingular, order certificate not unique).
`factorisation_all_verified` true in all 21 cells; 200 instances re-checked independently for
λ^m = 1, λ^(m/q) ≠ 1 for every prime q | m, and product of prime powers = d — 0 failures.

**OBS-5 — distribution.** Decade medians of `log m / log d`, seeds 20260807 / 20260814 /
11235813, `ks_crit` 0.0607 at n = m = 1000 throughout:

| decade | medians | null medians | ks_D |
|---|---|---|---|
| k12 | 0.6869 / 0.6869 / 0.6869 | 0.6877 / 0.6877 / 0.6965 | 0.087 / 0.066 / 0.101 |
| k14 | 0.6148 / 0.6286 / 0.6172 | 0.6437 / 0.6695 / 0.6599 | 0.121 / 0.110 / 0.104 |
| k16 | 0.6473 / 0.6398 / 0.6398 | 0.6667 / 0.6434 / 0.6552 | 0.072 / 0.095 / 0.083 |
| k18 | 0.8016 / 0.8120 / 0.8008 | 0.7949 / 0.8075 / 0.7974 | 0.032 / 0.032 / 0.037 |
| k20 | 0.7241 / 0.6940 / 0.7178 | 0.7409 / 0.7173 / 0.7202 | 0.081 / 0.071 / 0.055 |
| k22 | 0.7232 / 0.7185 / 0.7190 | 0.7314 / 0.7297 / 0.7291 | 0.061 / 0.054 / 0.059 |
| k24 | 0.7924 / 0.7950 / 0.7842 | 0.8023 / 0.7970 / 0.7906 | 0.044 / 0.037 / 0.034 |

Non-monotone but rising overall; the frozen flat-or-decreasing decay tell did **not** fire at
any seed (`median_rising` true, 3/3).

**OBS-6 — the deficit anomaly, recorded as an unexpected observation under AGENTS.md rule 8.**
The matched-null median exceeds the curve-derived median in almost every cell, and KS exceeds
its critical value at the three **smallest** decades at all three seeds, always in the
**deficit** direction — curve-derived `m` runs *smaller* than a uniform unit of the same `d` —
with D ∈ [0.066, 0.121]. Cells that are significant **and** at or above the design's declared
resolvable floor of D = 0.10: k14 at all three seeds (0.121, 0.110, 0.104) and k12 at seed
11235813 (0.101). All other significant cells are below the floor. At k24 every D is below the
critical value at all three seeds.

**OBS-7 — discreteness of the curve-derived sample.** Distinct (d, m) pairs among the 1000
instances of each cell: k12 164–173, k14 271–280, k16 432–440, k18 580–606, k20 742–786, k22
850–854, k24 907–939 — monotone in p and approximately 2√p at the small end. The curve-derived
median at k12 is bit-identical (0.6869344921421261) across all three seeds while the null
medians and excluded fractions differ, i.e. the curve samples are genuinely different and the
sample median lands on the same population atom. This is the observation-collision artifact
`H-ICINV-82ee6a`'s `proof_search_map` required, and it **forbids any use of (d, m) as an
identifying invariant**.

**OBS-8 — a small-m family exists and is exactly characterised.** Every `m = 1` instance in the
T1 small-order tail at k12 and k14 has u = 1, v = −1, λ = 1 with t ∈ {1, 2}; the `m = 2`
instances have λ = d − 1 at t = −1. The family is: ordinary E/F_p with |t| ≤ 2, where the
Z[π]-minimal non-scalar endomorphism has fully rational kernel and m ≤ 2. It did **not** fire
falsification condition F2 and did not falsify HEUR-ORD-1, because the trace-density of |t| ≤ 2
is O(1/√p) → 0 and a density-zero exceptional set is exactly what H1 asserts exists. Named here
and handed forward as a deliverable.

**OBS-9 — barrier table.** 177 rows, `M4_exponent_changed_count` 0, `M4_undetermined_count`
127, `cells_failing_byte_verification` 0, identical in the superseded v1 and in v2.
`audit_outcome: OUTCOME_AUDIT_PARTIAL`, so **AUDIT-Z is not confirmed** and must not be
reported as confirmed. What is established is narrower: among the 50 rows the audit could
classify, none changes its exponent. Both contract-required rows are present —
`IDEA-20260807-c36472`'s `Õ(p^{1/4})` transport row with `exponent_changed: no` and its
`[open]` mark **carried forward undischarged**, and the h ~ p^{1/2} identification-cost row. No
row escalates: `exponent_changed = yes` occurs nowhere.

**OBS-10 — terminal states, emitted by the run itself (SR7).** `stage0_branch: S0_AMBIGUOUS`;
`terminal_state: S0-UNDETERMINED`; `measurement_outcome: OUTCOME_NULL_generic_order`;
`audit_outcome: OUTCOME_AUDIT_PARTIAL`; `seed_votes` NULL 2 / FAMILY 1 / INSTRUMENT 0 with seed
20260807 dissenting; `verdict_yielding_decades` 7; `permitted_evidence_strength: preliminary`;
`claim_tier_cap: toy`; `invalidations_fired: []`.

**OBS-11 — cost and memory.** *Measured*, at PS-TOY-24 only: median `log m / log d` 0.7924,
median d/p 0.8325, n = 1000 — the latter **checks** rather than assumes the d ~ p assumption.
*Modeled* lower bounds, in a separate table sharing no column with a measured value: PS-TOY-24
2^31.0 time and memory, PS-P256 2^384, PS-P384 2^576, PS-ELL-SMALL 2^1.85 — **every one
conditional on STAGE 0 returning `KERNEL_FIELD`, which it did not**, and on HEUR-ORD-1.
`sota_delta` 0.0. Memory: analytic-vs-measured ratio in [0.68, 1.74] against the declared band
[0.25, 4.0], `within_band` true in all 13 manifests.

**OBS-12 — no falsification condition fired.** F-i needs `S0_BASE_FIELD` (verdict was
`AMBIGUOUS`); F-ii needs `OUTCOME_FAMILY_small_m` at ≥ 2 of 3 seeds (fired at 1); F-iii needs a
row with `exponent_changed: yes` (0 of 177); F-iv needs the m = 1 fixture to fail (PASS); F-v
needs degenerate fraction above 20% (0.000 everywhere); F-vi needs any action-step or fixture
instance with m > 2 (none observed).

---

## 2. Comparison

Against the **pre-registered** prediction and thresholds, frozen before execution and not
adjusted after:

| Frozen threshold | Required | Observed | Met |
|---|---|---|---|
| STAGE-0 determinate verdict | full text retrieved | landing pages only, PDFs 403 | no — `AMBIGUOUS` |
| Planted control | m = 2 on all 10 r | m = 2 on all 10 | yes |
| m = 1 fixture | m ∈ {1,2}, cost → `Õ(√ℓ)` | as required, same code path | yes |
| Decades yielding a verdict | ≥ 5 of 7 at n ≥ 400 | 7 of 7 at n = 1000 | yes |
| Null written before KS read | ordering auditable | hashes + timestamps recorded | yes |
| Degenerate fraction | < 20% | 0.000 everywhere | yes |
| KS resolvable floor | D ≥ 0.10 | see OBS-6 | partial |
| Barrier table required rows | 2 | 2, `[open]` carried forward | yes |
| Memory reconciliation | ratio in [0.25, 4.0] | [0.68, 1.74] | yes |
| Evidence strength calibration | 3/3 seeds → `replicated` | 2/3 seeds | caps at `preliminary` |

The strength is **not chosen at review**. The contract's frozen
`evidence_strength_calibration` fixes it: agreement at 3 of 3 seeds and ≥ 6 of 7 decades
permits `replicated`; agreement at 2 of 3 caps the record at `preliminary` with the dissenting
seed named. Observed: 2 of 3 seeds (dissenting seed 20260807, firing `OUTCOME_FAMILY_small_m`),
7 of 7 decades.

The deficit anomaly reads differently against the two frozen thresholds. Against the **KS
critical value** (0.0607) it is significant at the three smallest decades at all three seeds.
Against the **declared resolvable floor** (D = 0.10) — which the contract says in advance
governs what may be reported — only k14 at three seeds and k12 at one seed qualify.

---

## 3. Inference

**3.1 Cost corollary CC remains UNDETERMINED — not refuted, not supported.** STAGE 0 could not
obtain a full text, so no cost statement may be made in either direction and no modeled row of
the concrete-cost table may be cited as a cost claim. The load-bearing `[EXTERNAL, UNVERIFIED]`
assumption of `H-ICINV-82ee6a`, and `IDEA-20260807-9fb27c`'s `novelty_status: unverified` with
its unread Bernstein–De Feo–Leroux–Smith attribution, travel forward with their marks intact.
**No supersession of `IDEA-20260807-9fb27c` is triggered**; that requires `S0_BASE_FIELD`.

**3.2 HEUR-ORD-1 survives at toy scale, at `preliminary`, with seed 20260807 dissenting.** The
dissent rests entirely on deficits at k20 (0.081) and k22 (0.061), **both below** the declared
resolvable floor of 0.10 — which is why the aggregate is a majority null rather than a
contradiction.

**3.3 HEUR-M2-2 is supported at the coverage the contract declared and no further.** The m = 1
fixture passes through the STAGE-3 code path and no instance with m > 2 was found in the static
audit. That coverage is **weaker** than the runtime instrumentation the parent proposal asked
for, by a substitution declared in `H-ICINV-82ee6a` and unchanged here.

**3.4 The deficit anomaly is UNRESOLVED, and here is exactly what the data can and cannot
distinguish.** Three explanations:

- **(A) A small-d arithmetic artefact**, which the contract pre-declared. *Supported* by the
  monotone rise of distinct (d, m) values 167 → 923 across the ladder, and by the deficit being
  significant at exactly the three most atomic decades and sub-critical at k24 at 3/3 seeds.
  But an effect that genuinely shrinks with p would look identical — this is consistency, not
  proof.
- **(B) The null is matched on `d` but NOT on the support of λ.** *The data cannot address this
  at all*, because the design never drew the comparison that would. From the contract's own
  frozen identities: T3 gives v = ±1 and u = round(−t/2), and the λ-rule then gives
  **λ = ±round(t/2) mod d**, so **|λ| ≤ (|t|+1)/2 ≤ √p + 1 ≈ √d**. The curve-derived λ is a
  *small integer* in a window of size O(√d); the matched null draws a *uniform* unit from all
  of (Z/d)^*. A deficit against the uniform null is therefore ambiguous between "CM structure
  makes the order small" (a fact about curves) and "small integers have smaller multiplicative
  order than uniform units mod the same d" (a fact about integers, with no elliptic curve in
  it). **This is a gap in the pre-registered design, not in its execution.** Filed as
  `KN-OPEN-2c095b`. Verified against the table: k24 u = 455, v = −1, λ = 455, d = 16570188,
  hence t = 910 = 2·455.
- **(C) Noise at the floor.** *Excluded as a complete explanation*, because k14 reaches
  D ∈ [0.104, 0.121] — above the declared floor — at all three independent seeds. It plausibly
  explains the sub-floor cells the dissent rests on.

Net: (A) contributes, (B) is untested, (C) is insufficient. The honest label is **unresolved**,
and the remedy is a discriminating replication, not a verdict.

**3.5 AUDIT-Z is not confirmed.** Zero rows change exponent, which is what AUDIT-Z predicted,
but 127 of 177 are undetermined and `OUTCOME_AUDIT_PARTIAL` fired. The contract is explicit
that a partial audit may not be reported as a confirmation.

**3.6 No attack and no speedup, in either direction.** `sota_delta` is 0.0 against
0.886·√N. Even had a small-m family of positive density been found, mechanism STEP 4 —
`H-ENDO-001`, used here as an admissibility filter and **not re-tested** — would still make the
endomorphism useless for the ECDLP, because it acts on the prime-order subgroup as a scalar
computable in O(1).

---

## 4. Limitation

1. **Toy scale, by construction.** p < 2^24 on every decade, capped by the cost of exactly
   factoring d ~ p. No correspondence or embedding is used and none is available, which is why
   crypto scale is *not reachable* rather than merely not attempted. `claim_tier: toy`; no
   downstream citation may raise it.
2. **Ordinary prime-field curves only.** Supersingular curves and extension fields are out of
   scope and nothing here transfers to them.
3. **α is restricted to Z[π].** Where the conductor f > 1 the maximal order O may contain a
   non-scalar element of smaller degree, so every `d` here is a Z[π] statement; the O-minimum
   is a declared secondary for f ≤ 100.
4. **CONFOUND-1 (most serious).** The matched null is matched on d but not on the support of λ
   — see 3.4(B). These 13 runs cannot separate a fact about CM arithmetic from a fact about
   the multiplicative orders of small integers.
5. **CONFOUND-2.** m depends on the curve only through t, so the effective number of distinct
   objects per decade is O(√p), not the nominal n = 1000. The pre-registered critical value
   1.358·√(2/N) is calibrated for 1000 independent continuous draws; the curve-derived sample
   has 164–939 distinct (d, m) values with heavy multiplicities, most extreme exactly where the
   deficit is largest. Whether this makes the nominal threshold conservative or
   anti-conservative under this replicated-atom structure is **not settled** by these data.
6. **CONFOUND-3.** The primitivity and gcd(v, d) = 1 admissibility filter conditions the
   sample. Measured `degenerate_fraction` is 0.000 at every cell, which bounds any conditioning
   effect as small but does not characterise its direction.
7. **CONFOUND-4.** The k = 5 degree window means minimality is not uniqueness. The
   within-window spread is reported (T4), but the primary statistic uses the smallest-degree
   admissible α, and whether the minimiser choice contributes to the deficit is not separately
   tested.
8. **CONFOUND-5.** `RUN-ICINV-kf-decide` bound the **superseded** stage-1 artifact
   (`barrier_table_sha256 ee853b76…`, from `RUN-ICINV-kf-stage1-barrier` rather than `-v2`). M4
   is identical in both tables, verified by direct read, so no number changes; the traceability
   defect is recorded rather than absorbed.
9. **CONFOUND-6.** **No independent Validator or Red Team review exists.**
   `DEC-20260807-1538f8` next action N3 reserved both "before any evidence record is written"
   and they were not run. This review is Coordinator-only, and independent review is a blocking
   next action before this evidence is cited outside the ICINV lane.
10. **The reviewing session had no Bash tool.** Every verification was performed by reading
    artifacts directly; no statistic was recomputed by running code, and the raw-versus-summary
    check is a full-precision comparison between two independently written artifacts rather
    than an independent recomputation from the per-instance table. Declared, not glossed.
11. **`proof_status: empirical_only`, declared.** The distributional statement rests on
    measurement alone; no counterexample certificate and no derivation establishes it, and none
    is claimed. The one derivational component — λ = ±round(t/2), hence |λ| ≤ √p + 1 — is
    flagged as such rather than smuggled in as measurement.
12. **D1 and D4 stand as disclosed deviations**, neither retroactively authorised. These runs
    may be cited as evidence only alongside `DEC-20260807-4261e3`, which settles them.

---

## 5. The scoped claim

> Over the tested instances — ordinary y² = x³ + ax + b over p = 4093, 16381, 65521, 262139,
> 1048573, 4194301, 16777213; 1000 admissible instances per prime per seed at seeds {20260807,
> 20260814, 11235813}; α ∈ Z[π], primitive, gcd(v, d) = 1; m = ord_d(λ) from exact
> trial-division factorisation, verified per instance; pure-Python `exp_kerfield` under
> 7200 s / 4 GB / 6 CPU-hours — **no deviation of the distribution of log m / log d for the
> curve-derived λ from that of a uniformly random unit modulo the same d, meeting the
> pre-registered two-sample KS criterion at the three largest decades, was observed at two of
> three seeds; and no cost claim recorded in this ledger was found to change its stated
> exponent under the corrected cost model (0 of 177 rows, 127 undetermined).** A deficit
> against the matched null, in the direction that would matter if real, was observed at the
> three smallest decades at all three seeds and is **unresolved**. The field over which the
> square-root Vélu operation count is stated remains **undetermined**, so no corrected cost
> figure is asserted in either direction.

This establishes behaviour only on the tested toy distribution. It does not establish that all
parameterisations behave so, that all related representations behave so, that no undiscovered
structure exists, or that no future algorithm exploits the mechanism.

---

## 6. Decision and next actions

**`DEC-20260807-4261e3` — transition `replicate`.** `H-ICINV-82ee6a`: `proposed` → `analyzed`.

Not `support`: the frozen calibration caps at `preliminary`, HEUR-ORD-1 is a toy-scale
heuristic, no independent review exists, and a surprising result on first observation gets
`replicate`. Not `weaken` or `reject_scoped`: no falsification condition fired, nothing adverse
was found, and an adverse call here could rest only on a single unreplicated empirical-only
basis. Not `inconclusive` as the headline: the experiment resolved what it was powered to
resolve at 2 of 3 seeds, and a cheap pre-specifiable replication discriminates the one live
ambiguity. The parts that *are* inconclusive are named individually — **CC undetermined,
AUDIT-Z not confirmed, the deficit anomaly unresolved.**

Next actions, per the decision record:

- **N2 (blocking)** — dispatch the independent Validator and Red Team reserved by
  `DEC-20260807-1538f8` N3 and not run. This evidence may not be cited outside the ICINV lane
  until they report.
- **N3 (the one preserved `GOAL-ENDO-001` next action)** — the discriminating replication: a
  second null drawn over **small integers of matched magnitude** modulo the same d, plus
  per-trace stratification. This is the test that separates 3.4(B) from 3.4(A), and it is
  cheap.
- Successor for STAGE 0 — obtain the ANTS XIV proceedings version of the square-root Vélu
  paper, or a locally archived PDF, since the eprint PDFs are Cloudflare-blocked at HTTP 403.
  Until then CC stays undetermined.

**Knowledge promotion.** `promoted: [KN-OPEN-2c095b]` — the deficit question, stated exactly,
with its derivation, the cheapest discriminating test, and its closure conditions. No `KN-FIND`
is warranted: that gate requires `support` or `reject_scoped` at `replicated` or `strong`
strength, and this is `replicate` at `preliminary`. Two candidates are recorded in OBS-8 and
refused *for now* rather than dropped — the λ = ±round(t/2) closed form, and the |t| ≤ 2 family
— both becoming `KN-FIND` candidates after N2 and N3.
