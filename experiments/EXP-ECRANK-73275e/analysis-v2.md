# EXP-ECRANK-73275e — analysis v2 (the BATCH-e3cf55 replication round)

Composed by the Coordinator under TASK-20260909-403113 /
REVIEW-PLAN-BATCH-2f2b56, 2026-09-09, from the three independent review
reports (blind re-derivation TASK-20260909-9e06b1, validator
TASK-20260909-868163, red team TASK-20260909-b56824) over
execution-report-v2.yaml and the snapshot-bound run package
(commit 796eed5fa06ac369f592175b55395d5853329dfa). The v1 analysis
(analysis.md, BATCH-a2bf8b / BATCH-24d356) is immutable and untouched; this
file analyzes ONLY the v2 amendment round (R9-R15) under
amendments/v2_replication_protocol.yaml (DEC-20260908-614199).

## Observation

- All seven enumerated runs completed in-cap (ops_cap_respected true on all
  seven); control admission PROCEED (R9 IV-1R PASS and R15 IV-4R PASS at the
  gate; R10 detection 9/9).
- R9 (seed 760912): IV-1R PASS — all eight n=6 d=(1..1) tuples rejected
  degenerate_deg_s_2 (conics, as adjudicated in v1), all x^2 coefficients
  nonzero, certified n=6 total 0. IV-1C graded CERTIFIER_LIMITED: n=8
  top-rung totals [6,6,7,7,7,7,7,6] against closed form 7; the rung ladder
  (1500/10000/100000) is a no-op (identical totals and ops at every rung);
  recorded instrument observation: the committed certifier's good-prime list
  is 60 primes, all below 1500 for these tuples.
- R10 (seed 760908): 9/9 planted ELLIPTIC n=6 detection (IV-3R(a) PASS) —
  the v1 detection-path gap is exercised and closed at the planted scope.
  Gates (b) exponent window (per-plant h_A/h_B from 10.0 down to 1.053
  against [0.699,1.301]) and (c) per-decade calibration ([2.25,1.0] against
  [5,20]) FAILED and are recorded; per the amendment clause they void only
  the planted-height calibration reading. The IV-3R upgrade_clause then
  upgrades the R12/R14 COUNT readings from lower bounds to MEASURED.
- R11 (seed 760914): 9 planted n=8, all elliptic deg s = 3; top-rung totals
  [5,7,7,7,7,7,5,6,6]; ladder no-op recorded.
- R12 (seed 760906, FRESH): found 33 certified instances over the declared
  10^4 b-tuples (n_b_done 10000), feasible_tuples 22 (feasibility_fraction
  0.0022), exhaustion null, counted ops 9,447,724 < 1.0e8. N2R
  reconciliation: N_6^A {100:20, 1000:28, 10000:33}; N_6^B {100:26,
  1000:33, 10000:33}; cross-tabulation 33 rows; out-of-box B observations 0;
  verbatim predicates recorded BEFORE counts. Decade ratios: convention A
  [1.4, 1.1785714285714286] (two-decade 1.65); convention B
  [1.2692307692307692, 1.0] (two-decade 1.2692307692307692); the frozen
  exponent-+2 prediction is x100 per decade. Certificates 33/33 PASS;
  n_classes distribution {3:33}; zero instances with n_classes >= 4 (IV-8
  coverage statement recorded).
- R13 (seed 760906): IV-2R PASS — instance list, counts under RD-2 canonical
  serialization, and the op ledger bit-for-bit identical to R12.
- R14 (seed 760910, N3R rescoped): the enumeration COMPLETED the full 10^4
  b-tuples inside the raised cap (1,503,696,145 < 2.0e9 counted ops),
  found 0, feasible_tuples 0, near_miss_total 0, exhaustion null. The
  IC-732-3 integer (a,b) box [-min(H,20),min(H,20)]^2 with c solved exactly
  is disclosed; non-integer (a,b) are outside the enumerated scope and are
  not claimed empty; the full rational height-H lattice at n=8 is recorded
  as unmeasured scope.
- R15 (seed 760916): IV-4R PASS — exactly 0 solutions over the 64 null
  tuples; infeasibility flag no_real_root raised for all 64; the degenerate
  "1 = 0" sentinel detail (all_disc_negative false; disc = 0; the n=6
  d=(1..1) family is a conic) is recorded; RD-1 non-destructive b_index-0
  proof retained. PD-V2-1: attempt 1 (too-strict iv4r check) preserved under
  attempt-1-iv4r-check-too-strict/ per IV-6; attempt 2 final.
- Provenance: executor resolved vllm/qwen3.8-27b, fallback_used true,
  model_verified false; the same-machine replication disclosure is carried
  verbatim in every manifest.

## Comparison

- Blind re-derivation (TASK-20260909-9e06b1; derivation frozen at commit
  b8a0b94128bab02ea68cd8e0f5127f56b4ec6c7d BEFORE any producer read; verdict
  holds): at the three frozen (b,d) pairs (b_index 649, 1299, 4995) the
  derived n=6 ellipticity conditions yield five nondegenerate rational roots
  that match all five recorded found[] entries EXACTLY — r vectors,
  r_heights, cross-tabulation h_A/h_B, s polynomials, deg_s, and membership
  classifications under both conventions. The single discrepancy (disc_s)
  localized to a formula defect in the re-deriver's OWN frozen phase-1 code
  (non-monic leading-coefficient exponent); corrected values equal the
  recorded values exactly. Q2: every recorded decade ratio, smallest/largest,
  and two-decade total agrees with exact recomputation under both
  conventions; the exact integer inequality tests confirm two-decade growth
  strictly below the exponent-+2 prediction. Blind finding: at pair 649 the
  ellipticity condition is LINEAR in c (the x^5 coefficient of delta
  vanishes, A = 0) — the "single univariate quadratic" label is a family
  label, not a per-tuple guarantee; recorded, no convention switched.
- Validator (TASK-20260909-868163; verdict holds): 10/10 checks PASS —
  snapshot-receipt hash verification (62/62 content paths at HEAD and in the
  commit tree; commit/parent verified against git objects); R12 counts,
  feasibility fraction, cross-tabulation consistency, and decade ratios
  recompute exactly under both conventions; the N2R verbatim predicates
  match the frozen source-v2 lines; R13/R12 bit-identity confirmed by
  INDEPENDENT hashing (what IV-2R establishes is determinism over a shared
  code path at the same seed, not an independent implementation); ALL 33
  certificates recheck exactly from recorded instance fields; the ladder
  no-op is verified from the committed certifier source; the R10 (b)/(c)
  clause reading and the IV-3R upgrade_clause are confirmed against the
  amendment text; the R14 ledger verifies and F3_n8 does NOT fire (a
  completed in-cap zero with an empty near-miss ledger is not the recorded
  infeasibility pattern F3 names); PD-V2-1 satisfies IV-6 and re-scored no
  result; all seven manifests conform (nested run schema, independence
  disclosure, recorded provenance). OBS-1 (caveat, not defect): run_v2.py
  was modified mid-sequence — R9/R10/R11/R15-attempt-1 manifests pin
  c0eb13a0 (pre-fix), R12-R15-final and the snapshot pin 583b0b42 (= disk);
  consistent with the documented PD-V2-1 driver fix; run_v2.py is not in the
  amendment's bound_source_hashes, so this is a reproducibility caveat for
  R9/R10/R11, not a binding violation.
- Red team (TASK-20260909-b56824; verdict breaks): exact n=8 d=(1..1)
  closed-form derivation (Mestre trunc-sqrt; deg s = 3 on all four examined
  tuples; forcing identity, nondegeneracy, on-curve, Mestre sum = O all
  verified) plus prime-bound certification analysis: at the three shortfall
  tuples (b_index 0, 1, 7) the certified total plateaus at 6 for EVERY
  l in {2,3,5,7,11,13} under a 400-prime enlargement (Q-rank 6), while the
  control tuple reaches 7. The [6,6,7,7,7,7,7,6] shortfalls are therefore
  GENUINE dependencies, NOT forced by the prime bound -- the
  instrument-boundary reading breaks. The ladder no-op itself remains an
  instrument fact (60 primes all < 1500). All four declared
  proves-too-much objects break at named steps (calibration validation after
  failed gates; absence-on-the-full-lattice from the integer-box zero, and
  symmetrically the "zero means nothing" reading; refutation-of-HEUR-1 from
  toy-tier ratios; CONV-RESOLVED against convention-B data; both IV-1C
  over-readings). The same-machine fresh-seed replication read as
  machine-independent replication breaks: it tests seed sensitivity and
  pipeline determinism only. The explicit second Q-relation vector at the
  shortfall tuples was NOT derived (bounded search exceeded budget; an SNF
  kernel routine was defective) -- the all-l plateau is strong evidence, not
  an exhibited relation.
- PRIOR REVIEW ROUND (BATCH-8fa16f, already on main when this round's plan
  was frozen; discovered at composition): a parallel review round over the
  same execution landed first -- blind TASK-20260909-07a594 (holds; a gate
  truth-table check, the defining geometry outside its blind input),
  validator TASK-20260909-9ee65f (J2 holds; custody/integrity, 62/62 hashes,
  three exact certificate spot checks), red team TASK-20260909-66f9be
  (J3_scope_and_proves_too_much holds; a scope audit blind to runs and
  source that rejected every scope-removing mutation but carried the
  recorded instrument-boundary statement for IV-1C WITHOUT testing it),
  composed as DEC-20260909-b61396 / EV-ECRANK-039664 /
  analysis-v2-review.md (decision support, bounded; statuses deliberately
  unchanged -- that archive's write scope carried no status file). NO
  FINDING CONFLICTS between the two rounds: every required_preservation of
  BATCH-8fa16f (integer-box qualifiers, CERTIFIER_LIMITED labels and
  lower-bound readings, planted-family/same-machine/failed-calibration
  qualifiers, IV-1R separate from IV-1C) is honoured verbatim in this
  analysis and its records. The differences are DEPTH, not disagreement:
  this round's blind re-derived the actual ellipticity geometry (five exact
  instance matches vs a gate truth table), its validator recomputed all 33
  certificates (vs three spot checks) and re-hashed the replay identity
  independently, and its red team tested the instrument-boundary reading
  the prior round preserved untested -- and broke it (genuine Q-rank-6
  dependencies). The prior round's records are immutable inputs to this
  composition, not superseded observations; the duplication of review
  batches is recorded as a coordination finding in DEC-20260909-5756cb.

## Inference

- The fresh-seed n=6 construct arm REPRODUCES the v1 existence result at the
  tested scope: 33 certified multi-class instances, every certificate
  independently recomputed, five instance data sets blind re-derived from
  the mechanism statement alone, a deterministic replay, and the detection
  path validated by 9/9 planted elliptic recovery (counts MEASURED at the
  tested scope per the pre-registered upgrade clause). This supports the
  existence half of M-B at n=6 at the tested scope at replicated strength,
  with the same-machine qualification recorded.
- N2R branch selection: TENSION-REAL. Both conventions' decade ratios sit
  more than an order of magnitude below the x100 prediction (A: 1.4,
  1.1786, two-decade 1.65; B: 1.2692, 1.0, two-decade 1.2692);
  CONV-RESOLVED is excluded by the recorded data and MIXED has no
  supporting pattern. HEUR-1's construction-side count law stands
  UNVALIDATED with a recorded scoped tension at the tested scope. This is
  NOT a large-scale refutation (toy tier; H <= 10^4; count points of 20-33
  instances; the law's asymptotic regime is unmeasured), and F2_n6 does not
  fire from ratios alone.
- IV-1C correction: the graded CERTIFIER_LIMITED outcome stands as
  non-voiding exactly as the amendment text provides, but the v2 round's
  working interpretation ("shortfalls are a prime-set artifact") is
  CORRECTED by the red team's exact algebra: the shortfalls are genuine
  dependencies in the d=(1..1) n=8 control family (Q-rank 6 at three of
  eight tuples). The contract's expected total 7 is met by five tuples and
  genuinely not met by three. Whether this intersects the M4 ceiling /
  EV-ECRANK-6695dc "ceilings attained exactly" reading is recorded as a
  reconciliation follow-up, not asserted either way here.
- R14: a completed in-cap zero on the disclosed integer sub-lattice is a
  completed measurement — neither evidence of absence on the full rational
  lattice (where HEUR-1 itself predicts H^1 abundance) nor evidence of
  nothing in the tested box. F3_n8 does not fire. The n=8 existence
  question remains unresolved at the tested scope.
- Same-machine replication scope: the round tests seed sensitivity and
  pipeline determinism; machine-dependent behavior is untested. "Replicated"
  carries this qualification wherever it is used.
- Official transitions (Coordinator-only, in the same ledger archive):
  H-ECRANK-36d8d7 analyzed -> replicated; decision support (scoped) at
  strength replicated; claim tier toy; experiment gate stays analyzed (no
  gate transition this round). The transition is made in explicit
  reconciliation with DEC-20260909-b61396 (prior round; statuses left
  unchanged by that archive's declared write scope, its own rationale
  describing the v2 round as "a replicated toy-scope existence and control
  observation relative to v1"): the replicate instruction of
  DEC-20260908-d361ab N2 ("fresh seeds, independent machine/runtime WHERE
  POSSIBLE") is discharged -- the where-possible clause was not attainable
  and is disclosed -- and every unresolved item the prior round named
  (same-machine limitation, failed calibration reading, HEUR-1 tension,
  unmeasured rational lattice, limited certifier) is carried here as a
  qualification blocking `supported` and defining N4-N6, not absorbed.
  C1 stays OPEN and UNPROMOTED; IMP-2 stands; no breakthrough, closure, or
  established-evidence contradiction is proposed, so the nondegradable
  review-breakthrough gate is not engaged.

## Limitation

- Toy tier throughout: n in {6,8}; H <= 10^4 (n=6) and H <= 10^3 (n=8);
  count points of 20-33 instances; declared samples of 10^4 b-tuples
  (~6e-6 of n=6 affine b-space). No transfer to cryptographic parameters;
  correspondence null; no asymptotic claim is made or supported.
- Same-machine replication: machine-independent behavior untested (the
  second-machine route was unavailable in this deployment; disclosed in
  every manifest).
- n=8 zero scoped to the disclosed integer (a,b) box; the full rational
  height-H lattice is unmeasured.
- Detection completeness is validated at the planted shape and scale (9/9);
  MEASURED counts hold at the tested scope only.
- The explicit second Q-relation vector at the three n=8 shortfall tuples is
  not exhibited (all-l certification plateau only).
- OBS-1: run_v2.py mid-sequence change is a reproducibility caveat for
  R9/R10/R11 (not binding; sources hash-bound per run).
- Provenance qualifications (executor and reviewers: fallback_used true,
  model_verified false) are disclosure facts, not evidence.
