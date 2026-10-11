---
id: KN-FIND-5a8d3e
type: internal_finding
title: "At the n = 17, m = 2, l = 9 Stage-1 cell, the 16% 'not reached at D <= 4' of unsatisfiable S_3 subgroup-target descents is a plain-Macaulay closure artifact: all 62 are refuted by the degree-4 mutant closure W_4 at its first iteration, each with a per-instance degree-disciplined witness; the cause is S_3's non-semi-regular M_4, not the linear consequence ell alone"
tags: [certbin, semaev, summation-polynomial, s3, weil-descent, characteristic-two, macaulay, mutant-xl, degree-fall, degree-of-regularity, semi-regular, polynomial-calculus, unsatisfiability-certificate, closure-artifact, random-model-transfer, scoped, toy-scale, ecdlp]
confidence: established
evidence_level: "replicated at toy scope: exact per-instance certificates on 62 fixed archived systems, blind re-derivation from the specification (0 disagreements), author-independent verification of all 268 run certificates; one curve, one n, one producer run, same model family throughout"
source_refs: [KN-OPEN-3c8f51, KN-OPEN-d218ec, KN-LIT-7604, KN-TECH-b18366]
internal_refs: [EV-CERTBIN-4a9d2f, DEC-20260924-e61f3b, H-CERTBIN-5e71c9, EXP-CERTBIN-e94b27, RQ-CERTBIN-836ce2, EV-CERTBIN-6c3e0a]
proof_status: certificate
proof_refs:
  - coordination/review/certbin-20260924-3d7e1a/reviews/TASK-20260924-1f6a3c/wcerts.jsonl.gz
  - coordination/review/certbin-20260924-3d7e1a/reviews/TASK-20260924-b2c7f1/checks/wcert_check_b2c7f1.py
  - coordination/review/certbin-20260924-3d7e1a/reviews/TASK-20260924-b2c7f1/checks/wcert-check-output.json
  - coordination/review/certbin-20260924-3d7e1a/reviews/TASK-20260924-b2c7f1/checks/wcert-check-controls-output.json
  - coordination/review/certbin-20260924-3d7e1a/reviews/TASK-20260924-7e2d94/verification.json
  - coordination/review/certbin-20260924-3d7e1a/reviews/TASK-20260924-7e2d94/post-seal-checks.json
  - coordination/review/certbin-20260924-3d7e1a/reviews/TASK-20260924-d95e70/j7-mechanism/w1-witnesses.jsonl.gz
  - coordination/review/certbin-20260924-3d7e1a/reviews/TASK-20260924-d95e70/j7-mechanism/j7_verify_witnesses.py
  - coordination/review/certbin-20260924-3d7e1a/reviews/TASK-20260924-d95e70/j7-mechanism/w1-witness-reverification.json
  - coordination/review/certbin-20260924-3d7e1a/reviews/TASK-20260924-d95e70/j7-mechanism/j7a-derivation-verdict.yaml
  - coordination/review/certbin-20260924-3d7e1a/reviews/TASK-20260924-d95e70/j7-mechanism/j7a-fiber.json
  - coordination/review/certbin-20260924-3d7e1a/reviews/TASK-20260924-d95e70/j7-mechanism/fill.json
  - coordination/review/certbin-20260924-3d7e1a/reviews/TASK-20260924-d95e70/j9-ptm/o2-declaration.yaml
  - coordination/review/certbin-20260924-3d7e1a/reviews/TASK-20260924-d95e70/j9-ptm/o2-engine-and-own.json
  - coordination/review/certbin-20260924-3d7e1a/reviews/TASK-20260924-d95e70/j8-nulls/series.json
  - coordination/review/certbin-20260924-3d7e1a/reviews/TASK-20260924-d95e70/j8-nulls/syzygy.json
certificate_refs:
  - experiments/EXP-CERTBIN-e94b27/runs/RUN-CERTBIN-c417e0/certificates.jsonl.gz
  - coordination/review/certbin-20260924-3d7e1a/reviews/TASK-20260924-1f6a3c/wcerts.jsonl.gz
review_refs:
  - coordination/review/certbin-20260924-3d7e1a/review-plan.yaml
  - coordination/review/certbin-20260924-3d7e1a/reviews/TASK-20260924-7e2d94/validation-report.yaml
  - coordination/review/certbin-20260924-3d7e1a/reviews/TASK-20260924-c83b05/validation-report.yaml
  - coordination/review/certbin-20260924-3d7e1a/reviews/TASK-20260924-1f6a3c/report.yaml
  - coordination/review/certbin-20260924-3d7e1a/reviews/TASK-20260924-b2c7f1/validation-report.yaml
  - coordination/review/certbin-20260924-3d7e1a/reviews/TASK-20260924-d95e70/red-team-report.yaml
added: '2026-09-24'
superseded_by: null
---

## Read this before using anything below

This entry claims no more than `EV-CERTBIN-4a9d2f` (direction `supports`,
strength `replicated`, `claim_tier: toy`, `proof_status: certificate`), decided
by `DEC-20260924-e61f3b` (`support`, scoped to claim C1 of `H-CERTBIN-5e71c9`).

- **One cell.** n = 17 (F_2[t]/(t^17 + t^3 + 1)), m = 2, l = 9,
  V = {deg < 9} (polynomial basis), one random ordinary curve A = 97044,
  B = 126251 (#E = 4 * 32603), x(2E) subgroup targets, archived instances of
  `RUN-CERTBIN-3b7e05`. Nothing here is claimed at any other n, curve, V, m,
  target class, or solver.
- **Not** "S_3 systems are refuted at degree 4". **Not** evidence for or against
  Semaev's Assumption 1: the cell lies on its diagonal, so a low refutation
  degree is that assumption's content at work, not a test of it, and W_4 is a
  Macaulay-type closure, not an F4 step degree.
- **No cost claim.** At m = 2 oracle A (2^9 root-findings per attempt) decides
  satisfiability outright, and parallel Pollard rho dominates the DLP.
  sota_delta zero.

## 1. The finding

Plain degree-4 multilinear Macaulay (M_4) refuted 324 of the 386 unsatisfiable
subgroup-target descents at this cell and left 62 "not reached at D <= 4"
(`EV-CERTBIN-6c3e0a`, `KN-OPEN-3c8f51` item (C)). W_4 is the least subspace of
B_{<=4} containing M_4 and closed under g -> v_j * g for deg g <= 3 (the
degree-4 mutant closure, which reuses degree-fallen polynomials the way plain
Macaulay does not).

> **All 62 are refuted by W_4, at its first iteration (62/62, CP95
> [0.9422, 1]).** Each carries a per-instance, degree-disciplined W_4 witness
> (every intermediate of degree <= 4) produced by a blind re-deriver and
> accepted by an independently written checker. The whole unsatisfiable arm is
> therefore refuted at W_4: 386/386, of which 82 were certified in RC-1 (62 by
> W_4 witnesses, 20 by M_4-row certificates) and 304 rest on reviewed Stage-1
> per-instance flags through the definitional inclusion M_4 <= W_4.

The "genuine refutation degree above 4" reading (E-G) is falsified at this cell:
each witness is a counterexample certificate against it on its instance. Plain
degree-5 Macaulay (M_5) also refutes all 62 (author-independently verified).

Soundness held: no satisfiable control was refuted (W_4 0/62, M_5 0/62, W_5
0/10), and on the satisfiable controls codim(W_4 in B_{<=4}) equals the number
of Boolean solutions exactly (62/62), i.e. W_4 is the vanishing ideal in degree
<= 4 there.

## 2. Why: S_3's M_4 is far from semi-regular

The hypothesis offered the linear consequence
ell = sum_k Tr(t^k / x_R^2) f_k = v_0 + v_9 + Tr(B / x_R^2) as the reused fall.
The review found (red team, `RT-20260924-d95e70` J7):

| | S_3, U62 | same-support nulls | semi-regular reference |
|---|---|---|---|
| dim(M_4 cap B_{<=3}) | 964-978 | 323 | 323 |
| independent linear forms in M_4 | 4-12 (modal 10) | 0 | 0 |
| non-trivial degree-4 syzygies | 98-112 | 0 | 0 |
| ell-substituted R'_4 fall profile, d = 0..3 | [1, 18, 154, 834] (61/62), [1, 17, 153, 833] (1/62) | n/a | [0, 0, 16, 288] |

- **ell is sufficient on S_3:** 1 is in rowspace(M_4) + ell * B_{<=3} on
  62/62, with 62 structured witnesses (C_4, a) verified against two
  constructions.
- **ell is not necessary:** v_j-products of the non-ell fallen polynomials
  alone already give W^(1) = B_{<=4} with 1 in it on 62/62.
- **ell is not generically sufficient:** a synthetic family with one linear
  fall in an otherwise generic same-support system (N-ELL, 20 unsatisfiable
  draws) is refuted 0/20, landing on the exactly derived W_4 dimension 3162.
  (N-ELL is a review verification object, not evidence about the hypothesis;
  it bounds how the result is read.)

> **The random-model (semi-regular) description transfers to the same-support
> null systems exactly (rank M_4 = 2771 on 124/124) and does NOT transfer to
> S_3.** The semi-regular series (1+z)^17 / (1+z^2)^16 = 1, 17, 120, 408, 340,
> -2380 (D_reg = 5) is correct arithmetic about a generic system; it is the
> wrong model for S_3 at this cell. Predictions built on it (E-G, the pre-data
> prior, `KN-OPEN-3c8f51`'s "It does not explain degree 4" as applied to S_3)
> fail here for that reason.

The cheapest guard against repeating this: before applying any semi-regular
prediction to an S_3 system, compute its substituted degree-4 fall profile
(about 0.2 s per instance at n = 17; red-team RC-B).

## 3. What the frozen certificate format did and did not certify

The run's certificates were flat sets of (mu, k) with sum mu*f_k = 1. At D = 4,
W^(1) is contained in rowspace(M_5) (a derivation verified by J7), so a flat
certificate certifies unsatisfiability and 1 in rowspace(M_{2 + max deg mu}),
and W_4 membership only when max deg mu <= 2. All 62 U62 flat certificates had
max deg mu = 3; the same flat observation fits null instances that are NOT in
W_4 (observation fiber, 15 exhibited). **The W_4 qualifier is backed by the
review's degree-disciplined witnesses, not by the run's certificates.** Any
contract that counts W_D refutations needs straight-line certificates with a
per-node degree bound (`DEC-20260924-5b1c8e` R-8).

## 4. Boundaries (these travel with the finding)

1. One curve (h = 4), one V, n = 17, m = 2, l = 9, x(2E) subgroup targets. Other
   curves and V are the object of `EXP-CERTBIN-3f06d1`; n = 19 is unmeasured.
2. U62 is conditioned on a Stage-1 M_4 outcome; the 386/386 imports 304
   Stage-1 flags (sample-certified in `EV-CERTBIN-6c3e0a`).
3. "S_3-specific at W_4" is relative to same-support random bilinear nulls
   only; one null family is a single affine draw; neither shares S_3's
   quadratic part (phi of the 17 convolution forms, rank 16). Against systems
   that keep that quadratic part (N-CONV) it is untested.
4. The D <= 5 "clean" label carries no S_3 content: the nulls are refuted at
   M_5 too (124/124), as the semi-regular D_reg = 5 expectation predicts (an
   unnumbered heuristic reading), and the series gives D_reg = 5 at n = 19 too.
5. Same model family for the producer and every reviewer; mitigated by
   per-instance certificates checkable against the object definition.
6. The polynomial-calculus reading (1 in W_D iff a degree-D PC refutation over
   F_2 with Boolean axioms) is the red team's adaptation of a retrieved
   definition; it is a pointer for reuse, not relied on here.

## 5. What it opens

- `KN-OPEN-3c8f51` item (C) is answered at n = 17. Items (A) (mechanism: is it
  the convolution tensor or the curve?) and (B) (persistence along n) stay
  open; `DEC-20260924-e61f3b` ranks an N-CONV control first and a re-based
  n = 19 design, with W_4 beside M_4 and an N-ELL-type control, second.
- As a resource: the measurement is the hypothesis of a degree-fall theory for
  structured bilinear systems (S_3 = phi(x_1 x_2) + x_R^2 (x_1 + x_2)^2 + B),
  consistent with `KN-LIT-7604`'s reported first fall degree 2 (abstract-level).

## 6. Provenance

`RUN-CERTBIN-c417e0` of `EXP-CERTBIN-e94b27` (RC-1), reviewed in
`REVIEW-CERTBIN-20260924-3d7e1a`: author-independent certificate verification
(J1, `TASK-20260924-7e2d94`: 268/268), object and procedure fidelity (J2-J4,
`TASK-20260924-c83b05`), blind re-derivation of all 62 U62 plus 35 controls
(J5, `TASK-20260924-1f6a3c`), comparison and W-certification (J6,
`TASK-20260924-b2c7f1`: 2267 cells agree, 0 disagree; 67/67 pool W_4
refutations W-certified), and a red team on mechanism, nulls, proves-too-much
and readings (J7-J10, `TASK-20260924-d95e70`). Composed into
`EV-CERTBIN-4a9d2f`, decided by `DEC-20260924-e61f3b`, archived with this entry
by `TASK-20260924-7b4e0d` after `TASK-20260924-8f03d6`.
