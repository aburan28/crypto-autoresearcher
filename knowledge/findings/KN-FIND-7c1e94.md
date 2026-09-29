---
id: KN-FIND-7c1e94
type: internal_finding
title: "At the n = 17, m = 2, l = 9 RC-1 cell, S_3's lower-degree part is not necessary for degree-4 refutation relative to uniform lower parts: 144/144 N-CONV draws (S_3's quadratic part, linear and constant bits uniform on S_L) are refuted by W_4 with verified certificates, but every one already by plain M_4 through a fallen-space saturation that S_3's own pair never undergoes, so this control never needs W_4 and cannot test S_3's U62 behaviour"
tags: [certbin, semaev, summation-polynomial, s3, weil-descent, characteristic-two, macaulay, mutant-xl, degree-fall, syzygy, saturation, null-control, polynomial-basis, convolution, unsatisfiability-certificate, scoped, toy-scale, ecdlp]
confidence: established
evidence_level: "replicated for the frozen count at toy scope: 144 seed-determined systems, each refutation verified by an author-independent verifier and re-derived blind from the specification; one seed, one curve, one n, one producer run, same model family throughout. The narrowing readings (sections 2-4) rest on single-reviewer computations whose bases are declared per item."
source_refs: [KN-OPEN-3c8f51, KN-FIND-5a8d3e, KN-TECH-b18366]
internal_refs: [EV-CERTBIN-5c9e14, DEC-20260926-cb4487, H-CERTBIN-be6cbd, EXP-CERTBIN-ddfe75, RQ-CERTBIN-836ce2, EV-CERTBIN-4a9d2f]
proof_status: certificate
proof_refs:
  - coordination/review/certbin-20260926-089841/reviews/TASK-20260926-f0e5a4/verification.json
  - coordination/review/certbin-20260926-089841/reviews/TASK-20260926-f0e5a4/seal.txt
  - coordination/review/certbin-20260926-089841/reviews/TASK-20260926-83cebf/rederivation.json
  - coordination/review/certbin-20260926-089841/reviews/TASK-20260926-83cebf/wcerts.jsonl.gz
  - coordination/review/certbin-20260926-089841/reviews/TASK-20260926-83cebf/seal.txt
  - coordination/review/certbin-20260926-089841/reviews/TASK-20260926-59169c/comparison.json
  - coordination/review/certbin-20260926-089841/reviews/TASK-20260926-59169c/checks/cp3_wdag_check.out.json
  - coordination/review/certbin-20260926-089841/reviews/TASK-20260926-59169c/checks/cp3_witness.out.json
  - coordination/review/certbin-20260926-089841/reviews/TASK-20260926-c58e87/j11-ladder/proof-verdicts.yaml
  - coordination/review/certbin-20260926-089841/reviews/TASK-20260926-c58e87/j9-null/j9b-saturation-derivation.yaml
  - coordination/review/certbin-20260926-089841/reviews/TASK-20260926-c58e87/j9-null/j9b-counting.json
  - coordination/review/certbin-20260926-089841/reviews/TASK-20260926-c58e87/j9-null/j9-analysis.json
  - coordination/review/certbin-20260926-089841/reviews/TASK-20260926-c58e87/j9-null/stage1-reference.json
  - coordination/review/certbin-20260926-089841/reviews/TASK-20260926-c58e87/j10-ptm/o4-declaration.yaml
  - coordination/review/certbin-20260926-089841/reviews/TASK-20260926-c58e87/j10-ptm/o4-engine-records.json
  - coordination/review/certbin-20260926-089841/reviews/TASK-20260926-c58e87/j10-ptm/own-crosscheck.json
  - coordination/review/certbin-20260926-089841/reviews/TASK-20260926-c58e87/j10-ptm/o1-o2.json
  - coordination/review/certbin-20260926-089841/reviews/TASK-20260926-c58e87/j12-scope/n19-counting.json
  - coordination/review/certbin-20260926-089841/reviews/TASK-20260926-c58e87/j12-scope/n-trend.json
certificate_refs:
  - experiments/EXP-CERTBIN-ddfe75/runs/RUN-CERTBIN-6ebb0e/certificates.jsonl.gz
  - coordination/review/certbin-20260926-089841/reviews/TASK-20260926-f0e5a4/verification.json
  - coordination/review/certbin-20260926-089841/reviews/TASK-20260926-83cebf/wcerts.jsonl.gz
review_refs:
  - coordination/review/certbin-20260926-089841/review-plan.yaml
  - coordination/review/certbin-20260926-089841/reviews/TASK-20260926-f0e5a4/validation-report.yaml
  - coordination/review/certbin-20260926-089841/reviews/TASK-20260926-83cebf/report.yaml
  - coordination/review/certbin-20260926-089841/reviews/TASK-20260926-0f8aec/validation-report.yaml
  - coordination/review/certbin-20260926-089841/reviews/TASK-20260926-59169c/validation-report.yaml
  - coordination/review/certbin-20260926-089841/reviews/TASK-20260926-c58e87/red-team-report.yaml
added: '2026-09-26'
superseded_by: null
---

## Read this before using anything below

This entry claims no more than `EV-CERTBIN-5c9e14` (direction `supports`,
strength `replicated` for the frozen count, `claim_tier: toy`,
`proof_status: certificate`), decided by `DEC-20260926-cb4487` (`support`,
scoped to claim C-T of `H-CERTBIN-be6cbd`; the hypothesis head is `analyzed`,
not `supported`).

- **One cell.** n = 17 (F_2[t]/(t^17 + t^3 + 1)), m = 2, l = 9,
  V = {deg < 9} (polynomial basis), one random ordinary curve A = 97044,
  B = 126251 (#E = 4 * 32603), the 144 archived x(2E) targets of
  `RUN-CERTBIN-c417e0`, closures at D <= 4 only, one seed per arm.
- **Not** "S_3's structure does not matter". **Not** "N-CONV reproduces S_3's
  W_4 behaviour". **Not** "S_3 systems are refuted at degree 4". **Not**
  evidence for or against Semaev's Assumption 1 (W_4 is a Macaulay-type
  closure, not an F4 step degree).
- **No cost claim.** At m = 2 oracle A (2^9 root-findings per attempt) decides
  satisfiability outright, and parallel Pollard rho dominates the DLP.
  sota_delta zero.

## 1. The finding (certified)

Write each descended equation as f_k = q_k + l_k + b_k (bilinear, linear,
constant). The N-CONV family keeps S_3's quadratic part q_k at x_R exactly and
draws the linear and constant bits uniformly on S_3's union support S_L; one
unsatisfiable draw is kept per archived target (exhaustive 2^18 satisfiability).

> **W_4 refutes all 144 unsatisfiable N-CONV draws (144/144, CP95
> [0.9747, 1]), each with a degree-disciplined certificate verified by an
> author-independent verifier; same-support systems without the convolution
> quadratic part are refuted 0/144 (N-ELL144), 0/62 (NULL-F262) and 0/62
> (NULL-AFF62, one affine draw).** The competing reading "S_3's specific
> linear part or curve constant is load-bearing" (E-LINEAR) is falsified by the
> frozen rule.

Relatives on the same targets: the 17 convolution forms without phi and without
the cokernel fall (N-CONV17) are refuted 144/144 at W_4; S_3's own quadratic and
linear part with a drawn constant (N-CONVL) 144/144. No satisfiable control of
any arm was refuted (0/638).

What this licenses: relative to uniform bits on S_L, S_3's lower-degree part is
**not necessary** for degree-4 refutation at this cell. It is sufficiency
relative to a lower-part law, not a mechanism.

## 2. How it is refuted: at M_4, by saturation (the boundary that matters)

Every N-CONV draw is refuted already by plain degree-4 Macaulay M_4
(iteration 0), also certified author-independently and re-derived blind.

| | N-CONV | N-CONV17 | N-CONVL | S_3 (Stage-1 unsat) |
|---|---|---|---|---|
| M_4 refutation | 144/144 | 143/144 | 105/144 | 324/386 |
| fallen dim(M_4 cap B_{<=3}), of 988 | 988 on 142/144 | 988 on 140/144 | 965-982, never 988 | <= 979 on 386/386 |
| W_4 needs iteration 1 | 0 | 1 | 39 | 62 (U62) |

- **Counting (derivation, verified).** By L-TOP the degree-4 projection rank P
  depends on the quadratic part only; P = 1695 at every target, so at least 88
  non-trivial degree-4 syzygies are FORCED for every lower part. Counting does
  not force saturation: S_3's own lower part is never saturated.
- **Saturation of uniform lower parts (scoped heuristic, per-record signature
  held).** A random-fall-map rule declared before the per-arm records were read
  predicted saturation and M_4 refutation for N-CONV and N-CONV17 and
  non-saturation for N-CONVL; all three held. As a statement about EVERY lower
  part it proves too much (it would refute U62 at M_4).
- **Consequence.** N-CONV never needs W_4 (conditional W_4 rate among
  M_4-unrefuted draws: 0/0). It is a valid null for "is the lower part needed?"
  and CANNOT test the phenomenon that motivated it, refutation that needs W_4 as
  on U62. The M_4 delay lives in S_3's (quadratic, linear) pair: N-CONVL
  reproduces S_3's M_4 rates per target type.
- **Separating invariant.** Excess fallen codimension codim(M_4 cap B_{<=3}) - s
  is >= 3 on all 736 measured systems with S_3's quadratic-plus-linear pair and
  <= 1 on all 576 uniform-lower-part systems. Seconds to compute.

## 3. At W_4 the polynomial basis is not required on one random V'

Over one random 9-dimensional V' (same field, curve, targets, l and lower-part
law; a review verification object, not evidence about the hypothesis by itself):
P' = 1904, so saturation is impossible by counting (fallen <= 850 < 988); M_4
refutes 0/25 unsatisfiable systems and W_4 refutes 25/25, all at iteration 1.
So the M_4 refutation of N-CONV is tied to the polynomial basis (whose products
of degree < 9 polynomials never reduce modulo f), and the W_4 refutation is
not, on that one basis. Neither "basis-specific at W_4" nor "basis-free at W_4"
is established: one basis, 20 slots, W_4 membership of 23 of the 25 resting on
the engine record.

## 4. Not predicted to carry to n = 19 (derivation, unmeasured)

The saturation margin (dim Z_top - trivial - ell-syzygies - dim B_{<=3}) of the
convolution forms on the diagonal polynomial basis runs +88 (+71 with the
ell-syzygies) at n = 17, +3 (-16, ell-syzygies ASSUMED) at n = 19, -130 (-151)
at n = 21. So an N-CONV-type arm at n = 19 is predicted to leave the M_4 ceiling
and, by the V' analogy, to stay at the W_4 ceiling at iteration 1, where its W_4
rate alone would not separate it from S_3. Read such an arm on the first W_4
iteration containing 1 and on the M_4 fall profile, and compute the margin with
a MEASURED ell-syzygy count first (`DEC-20260926-cb4487` NA-1).

## 5. Boundaries (these travel with the finding)

1. One curve, one V (plus one V' in a verification object), n = 17, m = 2,
   l = 9, x(2E) targets, one seed per arm, D <= 4, one pinned engine.
2. The rate over other seeds is the CP95 interval only; no second sample.
3. Non-refutation counts (the nulls, satisfiable controls) carry no
   certificate; they rest on the engine, corroborated by a literal
   transcription on 13 systems, blind agreement on a pool and an exact derived
   dimension (T5) on N-ELL144.
4. Why S_3's pair is never saturated (x_1 <-> x_2 symmetry, or its
   Frobenius-compatible linear part) is not separated; which non-saturated S_3
   systems are refuted at M_4 (C20) and which need W_4 (U62) is unexplained.
5. Same model family for the producer, the engine author and every reviewer.

## 6. What it opens

- `KN-OPEN-3c8f51` item (A) at n = 17 is partly answered (sufficiency of the
  convolution-form span; the M_4 delay located in S_3's pair) and not resolved
  (no exact account; x(2E) modulation open). A successor KN-OPEN is scheduled
  (`DEC-20260926-cb4487` NA-6).
- As resources: the saturation count is a pre-data predictor of per-record M_4
  behaviour computable from the quadratic part alone; the excess codimension is
  a cheap per-instance separator; both are candidate readouts for any
  successor arm (degree-4 polynomial-calculus and first-fall-degree theories
  for Frobenius-compatible Weil descents take them as hypotheses; recalled
  pointers only).

## 7. Provenance

`RUN-CERTBIN-6ebb0e` of `EXP-CERTBIN-ddfe75`, reviewed in
`REVIEW-CERTBIN-20260926-089841`: author-independent certificate verification
(J1, `TASK-20260926-f0e5a4`: 1440/1440 lines, 355/355 own negative controls
rejected), blind re-derivation of the whole N-CONV stream and M_4 on all 144
(J7, `TASK-20260926-83cebf`), construction, closure, instrument, statistics and
rule fidelity (J2-J6, `TASK-20260926-0f8aec`), comparison (J8,
`TASK-20260926-59169c`: every compared quantity agrees up to one flag-semantics
encoding difference), and a red team on the null, proves-too-much, the ladder
and scope (J9-J12, `TASK-20260926-c58e87`). Composed into `EV-CERTBIN-5c9e14`,
decided by `DEC-20260926-cb4487`, archived with this entry by
`TASK-20260926-485baa` after `TASK-20260926-7a06ad`.
