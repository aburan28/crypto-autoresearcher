# Review analysis — EXP-PFDR-cbdefb (H-PFDR-c88f14)

Composed under TASK-20260904-e6b4dd from the two committed blinded reports of
review plan TASK-20260904-42b33a:

- validator (blind re-derivation) `coordination/reviews/pfdr-battery-20260904/reviews/TASK-20260904-42b33a/validation-report.yaml`
- red team `coordination/reviews/pfdr-battery-20260904/reviews/TASK-20260904-3a2ff5/red-team-report.yaml`

Package under review: twenty-three runs of `experiments/EXP-PFDR-cbdefb/`, all
`completed_valid`: fifteen m = 2 ladder cells (s ∈ {1..5} × p ∈ {4099, 16411,
65537}), three equal-dˢ cells, two m = 3 cells, and the three Stage-1 controls
(known-answer fixture, s = 1 baseline slice, d_ff-agreement).

**This is the only experiment of the five where BOTH reviewers break, on two
independent defects.**

---

## Observation

**Joint-by-joint verdicts.**

| joint | owner | verdict | deciding fact |
| --- | --- | --- | --- |
| V1 blind re-derivation of (d_ff, d_lf) under the HKY closure and the slope | 42b33a | holds | phase boundary 02:34:03Z, `rederivation.yaml` sha256 `04a55734…`: all 48 systems (12 instances × s = 2..5) give exactly **(5,5), (5,5), (6,6), (6,6)** with a single fall degree, uncensored under the reviewer's own certificate; V_{F,d_ff} equals the full ideal cap I(Z) ∩ B_{≤d_ff} on all 48 |
| V2 run-set validity, schema, pinning, the two closure.py hashes, seeds | 42b33a | **BREAKS** | see below — an **unrepairable receipt gap on the three blocking instrument controls** |
| V3 instance and certificate checks and the distinct-instance count | 42b33a | holds | 12/12 non-singular with generic j; every declared x_R is a window-pair sum with an exhibited witness; every digit solution lies in the window |
| V4 CTRL-DFF-AGREEMENT and cross-engine coverage | 42b33a | holds | 24/24 agreement rows, `disagreements: []`, `same_instance_all: true`; the four sibling EXP-PFDR-5726af manifests independently record 5, 5, 6, 6; the reviewer's own closure returns 5, 5, 6, 6 on the same instance |
| R0 raw/summary agreement, slopes, labels, band table, iteration counts | 3a2ff5 | holds | 75 cell-arm rows × 17 fields regenerated with **zero** differences; the primary fit reproduces slope 0.400000, CI [0.38202515, 0.41797485], residual variance 0.050209, n = 480 exactly; 0 of 600 Semaev draws censored |
| R1 pseudo-replication: the slope interval, the outcome rule, the falsifier statistic | 3a2ff5 | **BREAKS** | see below — **the pre-registered falsifier does not fire** |
| R2 is the frozen closure HKY, and is the completeness certificate sound? | 3a2ff5 | holds | on a planted late-fall object (n = 10, g of degree 8, true fall at D = 8) the certificate **REFUSED**: dim V_7 = 112 against dim(I ∩ B_{≤7}) = 582, C1 false, `right_censored` true; two independent C2 implementations agree at D = 4..8; largest dense partial sum 2^41.92 against 2^53 |
| R3 the single-fall observation: does the closure solve at d_ff? | 3a2ff5 | holds | **DERIVED (Lemmas 0-4, Theorem A)**: if V_{F,D0} = I ∩ B_{≤D0} for some D0 ≥ e(Z)+1 then no fall occurs above D0 at any degree. MEASURED: `V_complete_at_D` is TRUE at the first fall on all **3752** fallen systems and the degree condition holds on **3660** of them, so **d_lf = d_ff is DERIVED, not fitted**, on those 3660 |
| R4 nulls, nearby object, censoring design, presentational budget, confounds | 3a2ff5 | holds | the **non-curve (singular, nodal) cubic reproduces the Semaev (d_ff, d_lf) pair AND the censoring status at all 15 cells on 600 draws**; the count-1 tell separates perfectly on the 1200 s = 1 systems (fires exactly when Z_size ≥ 1); CTRL-EQUAL-DS-SPREAD observed 0 falls on 45/45, so the presentational artifact budget is the **empty set** |
| R5 claim (A): the non-transferring steps B1/B2 | 3a2ff5 | holds | Theorem 2.6 of arXiv:2103.07282 as displayed has TWO hypotheses — F a set of k'-**LINEARIZED** polynomials AND F reducible for k — and the package names only the second. Claim (A)'s **CONCLUSION holds**; its stated grounds are incomplete, and the missing linearized hypothesis is a third, cheaper non-transferring step (S~ has degree 4 and is not additive) |

### The two breaks, at full strength

**V2 — an unrepairable receipt gap on all three blocking instrument controls.**
Exactly two `closure.py` versions are pinned, but not in the partition the plan
expected: `74e659bb…` on **three** runs — `RUN-PFDR-cbdefb-fixture`,
`-s1-slice` and `-dff-agreement`, i.e. the known-answer fixture, the s = 1
baseline slice and the d_ff-agreement control, **all three blocking instrument
controls in their Stage-1 form**, all started 21:53 UTC — and `63475db5…` on the
other twenty, from 22:08:31 UTC on, i.e. every ladder cell, every equal-dˢ cell
and both m = 3 cells. The tree copy hashes to `63475db5`. `git log --all` shows
`closure.py` entering history exactly once, in `a3a81e33`, with content
`63475db5`, and a scan of `git rev-list --all` finds **no reachable commit
containing 74e659bb**. Those three receipts pin a file that no longer exists;
they cannot be re-run, and the plan's own disposition for the joint ("a
disclosed change whose metric-neutrality only the red team, who may read the
file, can judge") **is not executable by anyone**.

*Coordinator verification independent of the reports* (round-closure.md item 1,
re-checked here): confirmed. `closure.py` appears in exactly one commit in all
of git history, `a3a81e33`, at `63475db5…`; the version `74e659bb…` pinned by
the `fixture`, `dff-agreement` and `s1-slice` manifests is in no reachable
commit and not in the tree. The 20 measurement runs pin `63475db5` and are
unaffected.

*Scope of the break, stated precisely so it is neither inflated nor absorbed.*
The 20 runs producing every number in the ladder, the equal-dˢ cells and the
m = 3 cells are pinned to a retained, tree-identical version and are
reproducible. The break is confined to three control runs and is **partly
mitigated**: the s = 1 floor was re-measured under `63475db5` in the three m2-s1
ladder cells, and the closure-vs-graded d_ff identity P1 is recomputed inside
all 15 ladder cells under `63475db5`. **What is unmitigated is the comparison
against EXP-PFDR-5726af's recorded values, which exists only under the lost
version** — and which the validator's own independent re-derivation of the
(1101, 1) instance reproduces (5,5), (5,5), (6,6), (6,6). Per
`docs/evidence-and-reproducibility.md` a missing reproduction-package element is
**incomplete** evidence, not invalid evidence, and no wrong number was found
anywhere.

**R1 — PSEUDOREPLICATION: the pre-registered falsifier does not fire.**
Within-cell range of d_lf is **0 at all twelve cells** and the between-prime
range at fixed s is **0**, so the 480 observations are **four integers each
repeated 120 times**. The reported interval [0.3820, 0.4180] is the lack of fit
of a line to a step function with a fictitious sample size; the residual sum of
squares is pure lack of fit and the standard error shrinks as 1/√n with no
statistical content. On the four independent s-points the interval is
**[−0.2085, 1.0085]** (t_{2,0.975} = 4.30, s² = 0.1, S_xx = 5), which
**contains 0**, and 0.25, and 0.5, and 1. **The "excludes 0" falsifier
statistic therefore DOES NOT FIRE.** Five draws per s-level already buy
"excludes 0.5". The producer's own bootstrap over draws within cells returns the
degenerate [0.4, 0.4], which is the same tell. Both reviewers computed the
four-point interval independently and agree to four decimal places.

Two consequences the red team adds, both adverse and both recorded:

- **The frozen three-outcome rule could not have returned anything but
  "unresolved".** Outcome II's clause "the d_ff interval lies strictly below the
  d_lf point estimate" asks an interval to lie strictly below its own centre
  whenever d_ff = d_lf on every draw, which is the case here: it is
  unsatisfiable on any single-fall system. With n = 480 the half-width is 0.018,
  so Outcome I reduces to "d_lf = s + const exactly" and Outcome III to "d_lf
  constant on s = 2..5". Every integer step between them — **including the
  contract's own frozen prediction 5, 5, 6, 6** — lands in "unresolved" by
  construction. "Unresolved" is a fact about the rule, not about the last fall
  degree.
- **0.400 is a property of the window.** The measured values are exactly
  H-PFDR-4148b8's derived step 4 + ⌊s/2⌋, whose finite-window OLS slope is 0.4
  on [2,5], 0.5 on [2,6], 0.4571 on [2,7] and tends to 1/2. The reported
  interval [0.382, 0.418] therefore **excludes the true growth rate of the law
  the data reproduce with residual 0**.

**Proves-too-much control (3a2ff5).** Failure signature absent on objects 1-3
(the NULL-1 support-matched generator rises as s + 3; the planted late fall is
correctly refused; the direct presentation at B = 4 shows no fall in (4,7],
reproducing IDEA-20260808-afe4ce) and **present as designed on object 4**: at
s = 1 an argument reading every count-1 fall as an instrument fault does prove
too much, because at n = 2 the ring has 4 monomials and W_0(3) is already the
ideal cap whenever a root exists. The tell fires exactly when Z_size ≥ 1 (405
Semaev/non-curve + 165 of 600 NULL-1) and never when Z_size = 0 (450 + 15). The
corrected reading is "iteration_count = 1 AND W0_saturated = false". No number
in the package changes; s = 1 is outside the primary fit and raw values are
reported beside the rule-applied ones.

---

## Comparison

**Against the coordinator prior recorded in TASK-20260904-42b33a (l.232-292).**

**CONFIRMED, in near-verbatim detail, on all five of its numbered parts — with
one substantial addition the prior did not anticipate and one the prior asked
for conditionally and got.**

| prior expectation | outcome |
| --- | --- |
| (1) "unresolved" survives mechanically but for a reason the rule did not anticipate; Outcome II unreachable because d_lf = d_ff on every draw; the t-interval is an artifact of pseudo-replication; within-cell variance exactly zero; 480 "draws" are four values each repeated 120 times; on four independent s-points the slope is still 0.40 but the interval is roughly 0.4 ± 0.61, containing 0 and 1; **"the HEUR-002 falsifier statistic fires" does not survive an honest interval** | **confirmed exactly, to four decimal places** ([−0.2085, 1.0085] against the prior's "roughly ±0.61") and confirmed independently by both reviewers |
| (2) 0.40 is the OLS of the step 4 + ⌊s/2⌋ over s = 2..5; d_lf tracks the derived first-fall law exactly and is not flat over any four consecutive cells (longest flat run 2); Outcome III's flatness fails on the integers themselves | confirmed exactly, and extended: the asymptotic slope of that step is 1/2 and the reported interval excludes it |
| the honest reading for HEUR-002 is "not supported at the tested scale, contradicted in substance by the integers"; **weaken** with the refutation basis empirical plus a derivation note **IF** the red team can argue d_lf = d_ff = 4 + ⌊s/2⌋ from the closed form and the closure's saturation; **never `reject_scoped` on the artifactual interval** | **the conditional resolved in favour of the derivation**: R3's Theorem A plus the per-draw `V_complete_at_D` diagnostic make d_lf = d_ff DERIVED on 3660 fallen systems. The decision is `weaken` with `proof_status: derivation`, and `reject_scoped` is not taken |
| (3) the new fact: V_{F,d_ff} = I ∩ B_{≤d_ff} at every cell means the HKY closure SOLVES the digit system at d_ff = 4 + ⌊s/2⌋, a solving degree of slope 1/2 against the null's s + 3; promotable if C1/C2 is right; this is the law EXP-PFDR-c04716's D_0 must be read against | confirmed, and the certificate is sound (R2 holds, with the planted late-fall object refusing correctly) |
| (4) HEUR-001 holds where testable (c = 1) but D_max = 7 censored the null's own last fall at s = 5; NULL-3 reproduces the full pair at s = 3..5 and the non-curve cubic at every cell, so the measurement licenses no Semaev-specific statement | confirmed exactly, including the censoring defect (all 615 null objects censored at s = 5) |
| (5) instrument risks to clear: the dense float64 engine at s = 5, the C2 criterion, the count-1 rule over-triggering at tiny n | all three cleared or bounded: the exactness bound holds with margin 2164× at the binding case; C2 is a theorem for every D ≥ e(Z)+2 so **none of the 480 recorded C2 checks could have failed** and the censoring decision rests on C1 alone; the count-1 rule's over-trigger is characterised exactly (Z_size) |
| decision: claim (A) holds as a derivation; the label is unresolved; HEUR-002 weakened; HEUR-001 supported where testable; strength replicated for the integers and inconclusive for the slope; a knowledge finding for the single-fall/closure-solves observation and the measured D_0(s) law if the certificate holds | reached, with the additions below |

**NOT ANTICIPATED by the prior, and adverse: the V2 retention gap.** The prior
listed three instrument risks and none of them was this one. All three blocking
instrument controls in their Stage-1 form pin a `closure.py` version retained
nowhere. That is a receipt defect the prior did not foresee, it is unrepairable
as such, and it is the reason this experiment's decision carries a mandatory
replication next action rather than only a weaken.

**NOT ANTICIPATED by the prior, and favourable: R5's third non-transferring
step.** The missing **linearized** hypothesis of Theorem 2.6 is cheaper than
either of the package's two steps, needs no proof-body reading, and carries
claim (A)'s conclusion on its own — while showing that the package's "formal
analogue constant 4m = 8" is a substitution into a formula whose variable ranges
over linearized generators, i.e. a category error rather than merely a
theorem-less number. The step "Lemma 2.1 has no F_p analogue, therefore no
version transfers" leans on a proof body nobody read and is not needed.

**Reviewer-versus-reviewer.** No disagreement on any shared fact; the four-point
interval is computed identically by both. The validator additionally records a
**convention sensitivity** the red team does not: a defensible third reading of
"closed under multiplication" in the quotient ring (allowing degree-D elements
to be multiplied because idempotency keeps the reduced degree at D) moves the
ladder from 5,5,6,6 to **4,5,5,6** and the slope from 0.4 to 0.6. It is not the
reading the plan designates, and the producer's `convention_id` string in all 23
manifests describes the designated reading — so the agreement is on the intended
object — but the frozen convention document is load-bearing for every number in
the package and the validator hashed it without opening it.

---

## Inference

**What is established, scoped to m = 2, d = 2, s ∈ {2,3,4,5}, p ∈ {4099, 16411,
65537}, 8 curves × 5 planted targets per cell, D_max = 7, planting window [0,4),
the frozen convention `cbdefb-closure-v1` and its C1 certificate:**

1. **Every fallen system of the digit presentation has EXACTLY ONE fall
   degree**, and at that degree the closure has already computed the entire
   degree-≤ d_ff part of the vanishing ideal I(Z). Consequently **d_lf = d_ff**
   with values 5, 5, 6, 6 on all 480 Semaev draws, residual 0 against
   H-PFDR-4148b8's derived law 4 + ⌊s/2⌋. Given the recorded saturation
   diagnostic, the identity and the absence of any fall above d_ff at ANY degree
   are **DERIVED, not fitted**, on 3660 of the package's fallen systems.
2. **The measured solving degree GROWS with s.** D_0(s) = d_lf = d_ff =
   4 + ⌊s/2⌋ at m = 2. This is the law EXP-PFDR-c04716's `D_0` — a CONSTANT
   parameter in that table — must be read against, and the table's D_0 ≤ 6
   requirement at 256 bits with ω = 2 is exceeded from s = 6 on.
3. **The fitted slope is not a supported statement about growth.** On the four
   independent s-points the interval is [−0.2085, 1.0085]; the falsifier
   statistic does not fire; the frozen three-outcome rule could not have returned
   anything but "unresolved". The `unresolved` label stands as the measurement's
   own, and it is a fact about the rule.
4. **HEUR-002 (bounded last fall, digit form) is NOT SUPPORTED at this scale and
   is contradicted in substance by the integers** — d_lf rises from 5 to 6
   between s = 3 and s = 4 on 480 of 480 draws at three primes with certified
   histories. That it fails for ALL s follows from d_lf ≥ d_ff together with the
   derived d_ff law, and **inherits that law's conditions**: H-TOP at m = 2,
   Wilson's rank theorem, and the `analyzed` (formerly `specified`) status of
   H-PFDR-4148b8, whose own fall_dim clause this round refuted by counterexample.
   No bound uniform in s is refuted by the data alone, and no impossibility is
   claimed.
5. **Claim (A) of H-PFDR-c88f14 — no bounded-last-fall theorem transfers —
   HOLDS as a derivation**, on a third and cheaper ground than the two the
   package states. Its stated grounds are incomplete and a correction is owed.
6. **HEUR-001 (last-fall semi-regularity of the null) is supported where
   testable and NOT TESTED where it matters most.** The offset
   c = d_lf − (s + 2) is exactly 1 on every uncensored NULL-1 and NULL-2 draw at
   s = 2, 3, 4, and at s = 5 **every one of the 615 null objects is censored by
   D_max = 7** — the top cell, where a widening band would first show, was not
   measured. The "c grows with s" flag is an s = 1 ring-size artifact.
7. **The cost consequence, computed and recorded because it is the one
   cost-bearing statement in this lane.** At the measured solving degree the
   reduced column count is N_D = Σ_{j≤D} binom(2s, j) with log_B N_D = 1.99,
   1.95, 1.95 at s = 3, 4, 5 tending to 2H(1/4) = 1.6226, so the linear-algebra
   cost is about B^{3.9} at s = 4,5 and tends to B^{3.245} at ω = 2 — against
   B^1 for exhaustive enumeration of one digit block and O(√N) for Pollard rho.
   **σ > 1 by a wide margin at every s: the algebraic route at its own measured
   solving degree is dominated by brute-force enumeration of the digit cube, let
   alone by rho or BSGS.** Memory is the same N_D columns. `dominated_by` is
   therefore NOT null for this lane at m = 2, d = 2.

**SCOPE, stated plainly and without hedging.** The singular non-curve nodal
cubic reproduces the Semaev (d_ff, d_lf) pair **and the censoring status** at
every one of the 15 cells, on 600 draws; NULL-3, the block-factored null,
matches the full pair at s = 3, 4, 5 with difference 0 in both coordinates. By
the contract's own pre-registered F5 reading this is a controlled null.
**None of this is a statement about summation polynomials, elliptic curves or
the ECDLP.** It is a statement about a single degree-4 multilinear generator in
2s squarefree digit variables whose top form is the tensor square of the digit
linear forms.

**Validity disposition.** The run set is **admissible for the ladder measurement
and INCOMPLETE for its instrument controls.** The 20 measurement runs are
schema-complete, hash-consistent, correctly seeded, within budget, pinned to a
retained version, and their load-bearing quantity was blind re-derived by an
implementation that shares no code with the producer's. The three Stage-1
control runs are **not admissible as instrument controls** in their Stage-1
form. That is not a reason to discard the measurement and it is not a reason to
treat the controls as discharged; it is a reason to re-run them, which the
decision requires and which costs about 13 minutes.

---

## Limitation

1. **The convention is load-bearing and the frozen convention document was not
   opened by the blind reviewer** (hashed only, as the plan requires). A
   defensible third reading of "closed under multiplication" moves the ladder to
   4,5,5,6 and the slope to 0.6. The primary reading is the plan's designated
   one and the manifests' `convention_id` describes it, but every number in the
   package depends on that document.
2. **117 of the 120 s = 5 Semaev draws rest on the dense float64 engine alone**
   (cross-engine coverage is 40/40 at s ≤ 4 and 1/40 at s = 5). That engine is
   **not** the validated meter — `VALIDATION.md` states "no floating point
   anywhere in a rank", so the dense path lives in `closure.py` and its
   correctness rests on the declared exactness bound, which holds arithmetically
   with a 2164× margin at p = 65537 with 968 columns. The reviewer's own
   independent exact computation at s = 5 agrees on all 12 instances.
3. **The certificate is one test, not two.** C2(D) is a theorem for every
   D ≥ e(Z)+2 (Lemma 3), and all 480 recorded Semaev C2 checks are at D ≥ 8 with
   e(Z) ≤ 3, so none of them could have failed. The censoring decision rests on
   C1 alone. C1 is the right test and it refuses correctly on the known-false
   object; the certificate must not be read as two independent checks.
4. **Certification is equivalent to a low last fall.** C1 says the closure has
   already computed the whole ideal cap at D_max, i.e. the system has SOLVED by
   D_max, so censoring is a deterministic consequence of a high one. Censored
   draws are excluded from the d_lf fit, so any future cell with d_lf > D_max
   would be dropped and the fit biased toward Outcome III. No bias was realised
   at s ≤ 5, but the fitted SAMPLE is selected by an ideal-level predicate even
   though each d_lf value is generator-level.
5. **The ladder cannot be lengthened under the frozen instrument.** At m = 2,
   s = 6, n = 12 gives 2^n = 4096 > `CERTIFICATE_COLUMN_LIMIT` = 1024, so
   `certify_history` returns "certificate not attempted" and every draw is
   right-censored **by declaration**. Outcome III's "four consecutive uncensored
   cells" clause can never be satisfied on more than the four already measured.
6. **The presentational artifact budget is UNMEASURED.** All 45
   CTRL-EQUAL-DS-SPREAD instances at B = 64 report no fall and are censored,
   because D_max = 6 sits below the derived first fall 7 of the (2,6) arm. The
   observed spread is the empty set, so IDEA-20260830-84cdb7's "a claimed effect
   must exceed the presentational spread by a factor 2" rule has **no
   denominator anywhere in this lane** and must not be cited until it does.
7. **Three of the twelve declared instances carry a DOUBLING** (ell_1 = ell_2,
   x_R = x(2P)) rather than a two-summand decomposition, with solution-set size
   1 rather than 2. Legitimate window pairs, and (d_ff, d_lf) is unaffected, but
   a quarter of the subsample is not a genuine two-summand decomposition.
   Recorded as an unexpected observation.
8. **Distinct-system counting.** A cell holds at most 8 × 9 = 72 and at least
   8 × 4 = 32 distinct generator systems among its 40 draws, and at p = 16411
   curve 3101 a duplicate is FORCED (target seeds 2 and 3 share x_R = 4634). The
   binding replication fact is not that count but the observable's **zero
   within-cell variance**, which is what makes the 480-draw interval meaningless.
9. **The m ≥ 3 extension is not measured here.** Extending the law to m ≥ 3 uses
   H-PFDR-4148b8's closed form, whose H-TOP ingredient is a symbolic obligation
   at m ≥ 5, and this experiment's own m = 3 evidence is one cell at s = 2
   (below the formula's range) plus one cell not computable at D_max = 7.
10. **Two literature defects, both corrections owed.** KN-LIT-7605 records
    authors [] and year null (actual: Ming-Deh Huang, 2021) and states as a key
    claim that bounded-fall-degree results are stated for summation-polynomial
    systems over F_2 — the abstract and displayed theorems name **linearized
    polynomials** and no summation polynomials. The definition of the measured
    invariant V_{F,i} is `recalled` in H-PFDR-c88f14 ("corpus note read, paper
    not opened") and the eprint page does not contain it, so the definition the
    experiment measures **remains unverified against the source**. Internal
    validity is unaffected (the convention is frozen, explicit and pinned).
11. **Ten inference sub-fields are missing from all 23 manifests** and the
    legacy alias `executor-terra` is recorded where the handoff wrote
    `executor-implementation`; the content survives under
    `inputs.parameters.session_inference`, with `fallback_used: "unknown"`
    disclosed rather than asserted false.
12. **Correlated judgement**: `model_verified: false` for producer and both
    reviewers.
13. **This composition ran no code.** The Coordinator subagent has no shell; the
    `closure.py` retention finding cited above was verified by the orchestrating
    session directly in git history, independently of the reports.
14. **Four corrections are owed and are NOT made here** (records are immutable):
    the corrected reading of CTRL-ITERATION-COUNT, the annotation of
    KN-LIT-7605's authors/year/scope, the annotation of claim (A) recording the
    missing linearized hypothesis, and the record that the reported HEUR-002
    falsifier statistic does not fire on an honest unit of replication. All are
    named in DEC-20260904-d4a554's `next_actions`.
