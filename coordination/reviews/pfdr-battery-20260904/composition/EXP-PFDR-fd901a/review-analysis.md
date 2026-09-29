# Review analysis — EXP-PFDR-fd901a (H-PFDR-09e1b0)

Composed under TASK-20260904-e6b4dd from the two committed blinded reports of
review plan TASK-20260904-4c0d7d:

- validator `coordination/reviews/pfdr-battery-20260904/reviews/TASK-20260904-4c0d7d/validation-report.yaml`
- red team `coordination/reviews/pfdr-battery-20260904/reviews/TASK-20260904-8c5f97/red-team-report.yaml`

Package under review: six runs of `experiments/EXP-PFDR-fd901a/`, all
`completed_valid`, at p ∈ {4099, 16411, 2^64 − 59, the NIST P-256 prime}, one
digit shape (m, d, s) = (2, 2, 3), 722 recorded draws.

---

## Observation

**Joint-by-joint verdicts.**

| joint | owner | verdict | deciding fact |
| --- | --- | --- | --- |
| V1 run-set validity, manifest schema, seed and prime integrity | 4c0d7d | holds | 36/36 sidecar digests recompute; commit 3a9c1b02, `dirty: false`, identical `run_experiment.py` hash in all six manifests; 2^64 − 59 prime and no prime in (2^64 − 59, 2^64) under the reviewer's own 12-base Miller-Rabin; meter self-test "52 passed" re-run |
| V2 raw/summary agreement | 4c0d7d | holds | every count, interval and difference in `analysis.md` recomputes exactly from `runs/*/raw-result.json` alone: 286/286/316 draws, CP upper 0.08809730287880235 for 0 of 40, single difference row (top_rank@5 −4, fall_dim@5 +4, d_ff −1) identical at all three primes |
| V3 independent certificate re-verification and rank recomputation | 4c0d7d | holds | 245/245 draws recomputed by an implementation sharing no code with the meter give full_rank [0,1,6,15], top_rank [0,1,2,1]; 276 planted certificates (156 decomposition + 120 S_3-root) re-verify with 0 failures |
| V4 control presence and literal criterion accounting | 4c0d7d | holds (**and the joint holding INCLUDES the literal failure of criterion (2)**) | measured first fall is 66 and 130 against the frozen 65 and 129, in 6/6 draws each, under the contract's own d_ff definition; `git diff` of the specification against approval commit c5742969 is empty |
| R1 the derivation: generic rank, Schwartz-Zippel, planted subvariety | 8c5f97 | holds | the degree-4 part of S~ is the parameter-free integer form 16·Q_1·Q_2, so the D = 5 top block cannot drop at any odd prime; exhaustive over 81,947,208 curve-target pairs at p = 4099 the maximum number of zeros of S~ on the 64-point cube is **6**, against a threshold of 16 — the rank-drop locus is EMPTY on the searched axis |
| R2 information content of the sweep and the inverted structural tell | 8c5f97 | **BREAKS** | the whole recorded vector is FORCED: top_rank(D) = Σ_{j+k=D−4} r_1(j)r_2(k) = [1,2,1]; the integer top blocks have invariant factors (16), (16,16), (16), so 2 is the **only** content prime; the fixture triple taken as INTEGERS and reduced mod every prime in {3,5,…,199, 4099, 2^64−59, P-256} gives the reference profile at every one. **p_0 = 3**, three orders of magnitude below the battery's smallest prime, at under a second of compute |
| R3 provenance of the frozen 65/129 versus the measured 66/130 | 8c5f97 | holds | the top forms (x_1^2x_2^2, x_1^B, x_2^B) have lcm syzygies at degrees B+2, B+2, 2B, so the contract's own d_ff MUST return B + 2 with fall_dim 2; the frozen B + 1 is IDEA-20260808-093497's d_reg = ceil((m(B−1)+D_S)/2). The measured 66/130 is correct; the frozen 65/129 was **unsatisfiable by any instance** |
| R4 confounds and secondary arms | 8c5f97 | **BREAKS** | full_rank(D) is invariant under rescaling the nonzero values of S~, hence a function of the zero set Z(S~) **alone**; top_rank(D) is a function of the fixed integer top form alone. Mutation M1 (same zero set, random coefficients) reproduces the recorded **NULL** profile 40/40 at each prime; mutation M2 (same top form, random sub-top coefficients, **no curve, no target, no decomposition, no Semaev polynomial beyond its top monomial**) reproduces the recorded **SEMAEV** profile [(0,0),(1,1),(6,2),(15,1)] with d_ff = 5 and fall_dim [0,0,4,14], 40/40 at each of the three primes |

**Proves-too-much control (8c5f97).** Fired on the p = 2 object (predicted:
every degree-4 entry has content 16, so the top form vanishes mod 2; measured
0 of 24 at the reference profile, four distinct profiles, mean 33.3 zeros on the
cube), fired on p = 3 (23 of 24 at the reference profile, one draw with
full_rank@6 = 13, reproduced by the reviewer's code and by the producer's meter
draw for draw), and fired on the positive control. The interesting outcome is
the **partial survival**: on the Wilson inclusion map W_{1,3} over F_3 with
s = 6 > p = 3, the argument read literally (content of a maximal MINOR) declines
correctly, but read as `stage0-derivation.md` section 4 OPERATIONALIZES it
(content of the ENTRIES) it concludes p-independence, which is FALSE there —
rank 5 < 6 at p = 3 while no entry's content is divisible by 3. The survival
localises exactly at the entry-content-for-minor-content substitution. The red
team then computed the repair itself: the integer invariant factors of the
(2,2,3) top blocks are (16), (16,16), (16), so **after that computation** Stage
0's odd-prime exclusion is correct.

**Literal criterion failures, recorded as failures.** Criterion (2) —
"the positive control shows d_ff = 65 and 129" — is **NOT MET AS WRITTEN**: the
measured integers are 66 and 130 in 6/6 draws at each prime. R3 establishes
that this is a contract transcription error (a degree of regularity written into
a prediction about a first fall) and not an instrument fault, and that the
reading was **recorded, not substituted**: `analyze.py` keeps
`FROZEN.posctrl_d_ff = 65/129` and emits both `first_fall_equals_frozen`
(False, False) and `d_top_full_equals_frozen` (True, True). Criteria (1), (3),
(4), (5) are met as written. No re-scoring is performed here; that would need a
versioned `protocol_amendment`, which this task does not create.

---

## Comparison

**Against the coordinator prior recorded in TASK-20260904-4c0d7d (l.188-226).**

**CONFIRMED, and sharpened.** Every substantive expectation held:

| prior expectation | outcome |
| --- | --- |
| every validation joint holds; six runs complete and pinned; summary tables are the raw records; certificates re-verify; an independent elimination reproduces [(1,1),(6,2),(15,1)] at both large primes | confirmed, and the reviewer went past the plan's floor of three draws per large prime to **all 245 draws at all three primes** |
| the derivation holds and its planted-subvariety step is unproblematic because the whole (2,2,3) profile is decided by the top form, whose only content primes are 2 and 3 | confirmed and **sharpened**: only content prime is **2**; p = 3 deviates for a different reason (zero count above the 16-threshold), and the prior's "2 and 3" is refined to "content prime 2; p = 3 deviates by zero density" |
| the sweep's outcome was determined before it ran; criteria (3) and (5) could only fail by an instrument fault | confirmed verbatim (R2 breaking artifact produced) |
| criterion (4)'s interval is an upper bound coarser than the derived bound, so the "artifact budget" handed to the siblings is a derived bound restated, not a measurement | confirmed and **strengthened**: the event set is not merely thin but EMPTY at p = 4099 on an exhaustive x_R search over 19,992 curves |
| criterion (2)'s frozen 65/129 is a transcription of a semi-regular d_reg = B + 1, while the true first fall is B + 2 = the measured 66/130 | confirmed exactly, by an independent syzygy derivation and by reproduction at B ∈ {4,5,6,8,10,12,64,128} |
| the Semaev-minus-null offset is H-PFDR-4148b8's prediction, so HEUR-002 fails by the pre-registered p-independent integers | confirmed; and R4 adds that the offset is carried by a top form containing no curve, target or Semaev content |
| the non-curve cubic identical to the Semaev arm means the p-axis carries nothing about the curve at this shape | confirmed, and R4 shows the identity is **forced** (identical top form; planted root gives exactly 2 zeros, verified 40/40 per prime) |

**REFINED against the prior's own DECISION I EXPECT.** The prior expected
"evidence strength replicated (three primes, two independent engines)". RT-O10
rejects that label: EXP-PFDR-5726af's H-WIL table covers only p ∈ {4099, 65537},
both far above p_0 = 3, so the second engine is a cross-implementation check of
one forced value, not replication across the p-axis; and three primes are three
evaluations of a forced integer. The prior's expected knowledge entry
("fixed-shape p-independence and the exact Semaev-minus-null offset, reached at
the P-256 prime") must lose the words "reached at the P-256 prime" as an
evidential claim: the P-256 cells are exact ranks of a 64-column matrix costing
3.25 s and 62 MB, and the "cryptographic scale" of the run is field-element
size only.

**NOT OVERTURNED anywhere.** No expectation of the prior was reversed by either
reviewer. Two additional adverse findings the prior did not contain are recorded
below under Inference (RT-O1's vacuous minor-product bound; RT-O6's point-set
determination of four of five reported invariants).

**Reviewer-versus-reviewer.** No disagreement on any shared fact. Both
reviewers independently reach the instance-multiplicity point from different
directions (V2: 31/30/29 distinct (A,B,x_R) triples behind 40 nominal draws;
RT-O4: the pairing is a pairing of seed labels because (A,B) are drawn from p).
That convergence is genuine, since neither read the other.

---

## Inference

**What is established, scoped to (m, d, s) = (2, 2, 3) with window [0, 8), at
p ∈ {4099, 16411, 2^64 − 59, the P-256 prime}, one meter, one host:**

1. **The receipt is admissible.** Six complete, hash-bound, correctly seeded
   runs on a Coordinator-committed snapshot, whose certificates re-verify under
   an implementation sharing no code with the producer's and whose rank profile
   at both large primes is reproduced exactly by an independent elimination.
2. **The hypothesis's title claim is CORRECT and is DERIVABLE, not merely
   observed.** At fixed digit shape the graded Macaulay invariants of the
   prime-field digit-presented system are p-independent above a small threshold
   prime, and the witnesses are now explicit: r = [1,6,15] / [1,2,1], top-block
   invariant factors (16), (16,16), (16), and **p_0 = 3**. The threshold is
   three orders of magnitude below the smallest prime the battery ran.
3. **The p-sweep is therefore calibration and not measurement, exactly as the
   hypothesis's own title says.** Criteria (3) and (5) could fail only by an
   instrument fault; criterion (4)'s interval bounds an event set that is empty
   at the prime it names. That is not a defect in the experiment — it is the
   hypothesis being right — but it fixes what the 722 draws are evidence OF: an
   instrument check, not an independent test of p-independence.
4. **The observable does not see the curve, the target, or the prime.** M1 (a
   different polynomial with the same zero set) lands on the null profile; M2 (a
   different polynomial with the same top form, containing **no elliptic curve,
   no target, no planted decomposition and no Semaev polynomial** beyond its top
   monomial) lands on the Semaev profile, 40/40 at each of the three primes.
   The nodal non-curve cubic reproduces the Semaev arm at every prime, and its
   agreement is **forced** (identical top form, |Z| = 2).
   **This result is therefore not a statement about summation polynomials,
   elliptic curves or the ECDLP.** It is a statement about a fixed integer
   degree-4 form 16·Q_1·Q_2 and a zero-set threshold.
5. **HEUR-001 (rank-drop density c_D/p) is neither supported nor tested by this
   experiment.** For the Semaev arm the c/p law is the wrong functional form: a
   drop requires ≥ 16 zeros of S~ on 64 cube points, a codimension-≥14
   coincidence, so the true rate at p = 4099 is 0 — exhaustively, on the whole
   x_R axis, for 19,992 curves — rather than c/p. The arm where a c/p law is
   real and measurable is the support-matched null's top_rank at D = 5, whose
   rates the red team measured on the ladder p = 5,7,11,13,101,4099 as
   0.2800 / 0.1835 / 0.1035 / 0.0935 / 0.0130 / 0.0005 (2000 draws each,
   consistent with c ≈ 2); the contract sampled it with 200 draws at p = 4099,
   where the expected event count is 0.1.
6. **HEUR-002 fails by exactly the pre-registered integers** (top_rank@5 −4,
   fall_dim@5 +4, d_ff −1, identical at all three primes) — but M2 shows the
   offset is produced by an object with no Semaev, curve or target content, so
   "Semaev-specific structure carried p-independently" overstates it. The
   correction IDEA-20260731-009's HEUR-FF-1 needs is a closed-form tensor
   defect, not a measured offset, and no status of IDEA-20260731-009 changes.
7. **Three stated exclusions are wrong as written and are corrected here, not
   softened.** (a) RT-O1: the committed records define P_D as the PRODUCT of
   nonzero maximal minors, giving deg(P_D) ≤ 4.79e15 at D = 6, so the quoted
   Schwartz-Zippel bound is **vacuous** at p = 4099 and p = 16411 — the usable
   constant 30/4099 comes from Stage 0's single-minor refinement, which is
   correct but is not in the ledger record. (b) RT-O2: `stage0-derivation.md`
   section 4 computes content primes as the gcd of the ENTRIES and concludes
   "no odd prime divides any entry's content", which cannot exclude odd content
   primes — the proves-too-much object 3 is a matrix of entry content 2 whose
   rank drops at p = 3. (c) RT-O6: `CTRL-CONFOUNDERS-NAMED (i)`'s "only
   generator-level rank profiles are read; no ideal-level invariant appears" is
   false — four of the five reported invariants are point-set quantities and the
   fifth is a parameter-free constant. The confound is neutralised only by the
   separate fact that planting pins |Z(S~)| = 2, far below every threshold that
   could move a rank.
8. **Criterion (2)'s literal failure is a contract transcription error and the
   instrument is uncharged.** The control's forced disposition (strictly
   increasing, no early fall, instrument not blind to p) is met, so the O1 bar
   does not fire — but RT-O5 shows the control has **no dynamic range on the
   axis it is supposed to gate**: d_ff = B + 2 is a function of B alone
   (verified at fixed B = 8 across all three primes, all giving 10), and
   B = round(√p) is a deterministic function of p. What DOES discharge
   p-sensitivity of the instrument is RT-C2: the meter itself, on the sweep's
   own (2,2,3) construction, returns a different profile at p = 2 and reproduces
   the p = 3 drop.

**Strength.** The measurement is `replicated` in the sense that matters and is
NOT replicated in the sense a reader will assume, and both must be said.
Replicated: the recorded values are reproduced by four independent
implementations (the producer's meter, the producer's in-run sympy and naive
routes, the validator's from-scratch elimination on 245 draws, the red team's
tensor/symbolic derivation), and the certificates re-verify under a fifth.
**Not** replicated: the three primes are three evaluations of a value forced for
every odd p, so nothing on the p-axis is an independent test; the s-axis is
untested and out of contract scope.

**No cryptographic-scale claim.** The P-256 cells are exact ranks of a
64-column matrix reached by a fixed-shape shortcut. The contract's own `toy`
tier and `interpretation_limits` are correct and are carried through unchanged.

---

## Limitation

1. **One shape, one axis.** Nothing here touches the s-axis, yield, solving
   degree, cost, or the ECDLP. The contract says so and the reviewers agree.
2. **The null arm cannot be rebuilt.** `null_support` polynomials come from the
   producer's seeded RNG and are not stored in the raw records, so the 200 draws
   per prime were checked for internal consistency and seed distinctness but
   **not independently recomputed**. The positive-control and secondary-direct
   ranks and the `syzygy_dim` / `deficit_series` columns were likewise not
   independently recomputed. Reported as not computed, never as agreement.
3. **The nominal sample size exceeds the number of distinct objects.** 40 draws
   per cell realise 31/30/29 distinct (A, B, x_R) triples over 8 curves, because
   a curve whose on-curve window [0,8) holds only two or three x-values cannot
   supply five distinct planted targets. The honest exact CP upper bound at
   4099 is 0.1122 (n = 31), **above** the criterion's own 0.1 threshold; on the
   8 distinct curves it is 0.3694. Criterion (4) is still met as written because
   what the frozen text requires below 0.1 is the RATE (0.0000), but the
   interval must not be quoted as if it were below 0.1.
4. **"40 of 40 paired" is a pairing of seed labels, not of objects.** (A, B) are
   drawn from the seed and p, and the null RNG seed mixes p, so no instance
   exists at two primes. With zero within-arm spread, any bijection between the
   two 40-draw sets yields 40/40.
5. **The contract's primary frozen-fixture route is not executable.** fd901a's
   (2,2,3) p = 4099 fixture is A = 941, B = 428, x_R = 3690 while
   EXP-PFDR-5726af's fixture at the same seed labels is A = 527, B = 72,
   x_R = 2374. The two contracts derive different instances from the same seed
   labels, so **no cross-contract same-instance agreement may be claimed** from
   this package in either direction. The fallback route (an independent second
   implementation in the same run) was the applicable one and it passed.
6. **Ten inference sub-fields required by the Minimum run manifest are absent
   from all six manifests** (`canonical_policy`, `backend`, `provider`,
   `model_provenance`, `model_verified`, `requested_reasoning_effort`,
   `fallback_reason`, `degraded_requirements`, `independent_session`,
   `config_digest`), caused by the disclosed D9 harness defect
   (`harness/runner.py` defines `_inference_block` twice; the later definition
   hard-codes `executor-terra`, a registered ALIAS of
   `executor-implementation`). Most content survives under
   `inputs.parameters.executor_session_inference`. No measured quantity depends
   on them. Recorded as a schema deviation, not a validity defect.
7. **`experiments/EXP-PFDR-fd901a/amendments/` does not exist.** No amendment
   was made, so nothing is missing from it; a packaging nit only.
8. **Neither reviewer opened the Huang-Kosters-Yeo source**, and neither
   re-derived Wilson's theorem from a published source. The corrections at
   RT-O1 / RT-O2 are the reviewers' own computations, not citations.
9. **Correlated judgement.** Producer and both reviewers report the same model
   family with `model_verified: false`; the red team's `doctor --probe` could
   not verify any backend (all API keys unset). What this round buys is
   disjoint joint coverage and blind ordering, not model diversity.
10. **This composition ran no code.** The Coordinator subagent has no shell; it
    read the committed reports and records. No number here was recomputed by
    this session.
11. **Two corrections are owed and are NOT made here** (records are immutable):
    an annotation of H-PFDR-09e1b0 / IDEA-20260903-26aa81 replacing the
    minor-PRODUCT Schwartz-Zippel bound with Stage 0's single-minor form, and an
    annotation replacing `stage0-derivation.md` section 4's entry-content check
    with the integer invariant factors (16), (16,16), (16). Both are named in
    DEC-20260904-36b906's `next_actions`.
