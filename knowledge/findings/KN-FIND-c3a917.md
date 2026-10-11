---
id: KN-FIND-c3a917
type: internal_finding
title: "At the n = 19, m = 2, l = 10 cell (one curve, h = 2), the degree-4 mutant closure W_4 refutes all 400 unsatisfiable x(2E) subgroup-target S_3 descents at its first iteration while plain degree-4 Macaulay refutes none; the refutation belongs to the quadratic tensor's neighbourhood, is carried by degree-2 falls, is not S_3-specific at W_4, and does not run through the n = 17 route"
tags: [certbin, semaev, summation-polynomial, s3, weil-descent, characteristic-two, macaulay, mutant-xl, degree-fall, degree-of-regularity, semi-regular, convolution-tensor, unsatisfiability-certificate, random-model-transfer, nearby-object-control, scoped, toy-scale, ecdlp]
confidence: established
evidence_level: "replicated at toy scope: 400 per-instance wdag-v1 certificates verified by author-independent code, 400 checked M_4 non-membership witnesses, blind re-derivation of 90 systems (3770/3770 agree), author-independent replay of the whole population; one curve, one n, one producer run, same model family throughout"
source_refs: [KN-OPEN-3c8f51, KN-OPEN-d218ec, KN-FIND-5a8d3e, KN-TECH-b18366]
internal_refs: [EV-CERTBIN-091c56, DEC-20260926-901ea1, H-CERTBIN-e3ac93, EXP-CERTBIN-060020, RQ-CERTBIN-836ce2, EV-CERTBIN-4a9d2f]
proof_status: certificate
proof_refs:
  - coordination/review/certbin-20260926-d7249d/reviews/TASK-20260926-401771/verification.json
  - coordination/review/certbin-20260926-d7249d/reviews/TASK-20260926-401771/m4-witnesses.jsonl.gz
  - coordination/review/certbin-20260926-d7249d/reviews/TASK-20260926-401771/post-seal-comparison.json
  - coordination/review/certbin-20260926-d7249d/reviews/TASK-20260926-f0736e/rederivation.json
  - coordination/review/certbin-20260926-d7249d/reviews/TASK-20260926-f0736e/wdag.jsonl.gz
  - coordination/review/certbin-20260926-d7249d/reviews/TASK-20260926-f0736e/ann.jsonl.gz
  - coordination/review/certbin-20260926-d7249d/reviews/TASK-20260926-f50294/comparison.json
  - coordination/review/certbin-20260926-d7249d/reviews/TASK-20260926-f50294/checks/cp3_blind_certs.json
  - coordination/review/certbin-20260926-d7249d/reviews/TASK-20260926-f50294/checks/third_check_m4_witnesses.json
  - coordination/review/certbin-20260926-d7249d/reviews/TASK-20260926-f50294/j8-semantics/proofs.yaml
  - coordination/review/certbin-20260926-d7249d/reviews/TASK-20260926-f50294/j8-semantics/certification_table.yaml
  - coordination/review/certbin-20260926-d7249d/reviews/TASK-20260926-fee7a9/j9-pattern/d2-verdict.yaml
  - coordination/review/certbin-20260926-d7249d/reviews/TASK-20260926-fee7a9/j9-pattern/c-comparison.json
  - coordination/review/certbin-20260926-d7249d/reviews/TASK-20260926-fee7a9/j9-pattern/e-w3.jsonl
  - coordination/review/certbin-20260926-d7249d/reviews/TASK-20260926-fee7a9/j10-semireg/d4-verdict.yaml
  - coordination/review/certbin-20260926-d7249d/reviews/TASK-20260926-fee7a9/j10-semireg/sigma-decomposition.jsonl
  - coordination/review/certbin-20260926-d7249d/reviews/TASK-20260926-fee7a9/j11-nulls/d3-verdict.yaml
  - coordination/review/certbin-20260926-d7249d/reviews/TASK-20260926-fee7a9/j11-nulls/profiles-comparison.json
  - coordination/review/certbin-20260926-d7249d/reviews/TASK-20260926-fee7a9/j13-ptm/o1-table.json
  - coordination/review/certbin-20260926-d7249d/reviews/TASK-20260926-fee7a9/j13-ptm/o2-o3-declaration.json
  - coordination/review/certbin-20260926-d7249d/reviews/TASK-20260926-fee7a9/j13-ptm/o1-o3-engine-check.json
  - coordination/review/certbin-20260926-d7249d/reviews/TASK-20260926-fee7a9/j13-ptm/o4-reading-table.yaml
  - coordination/review/certbin-20260926-d7249d/reviews/TASK-20260926-fee7a9/j13-ptm/o4-engine-and-own.jsonl
certificate_refs:
  - experiments/EXP-CERTBIN-060020/runs/RUN-CERTBIN-a3fc60/certificates.jsonl.gz
  - experiments/EXP-CERTBIN-060020/runs/RUN-CERTBIN-a3fc60/annihilators.jsonl.gz
  - coordination/review/certbin-20260926-d7249d/reviews/TASK-20260926-401771/m4-witnesses.jsonl.gz
  - coordination/review/certbin-20260926-d7249d/reviews/TASK-20260926-f0736e/wdag.jsonl.gz
review_refs:
  - coordination/review/certbin-20260926-d7249d/review-plan.yaml
  - coordination/review/certbin-20260926-d7249d/reviews/TASK-20260926-f0736e/report.yaml
  - coordination/review/certbin-20260926-d7249d/reviews/TASK-20260926-401771/validation-report.yaml
  - coordination/review/certbin-20260926-d7249d/reviews/TASK-20260926-42be88/validation-report.yaml
  - coordination/review/certbin-20260926-d7249d/reviews/TASK-20260926-fee7a9/red-team-report.yaml
  - coordination/review/certbin-20260926-d7249d/reviews/TASK-20260926-f50294/validation-report.yaml
added: '2026-09-26'
superseded_by: null
---

## Read this before using anything below

This entry claims no more than `EV-CERTBIN-091c56` (direction `supports`,
strength `replicated`, `claim_tier: toy`, `proof_status: certificate`), decided
by `DEC-20260926-901ea1` (`support`, scoped to claims C-P and C-M of
`H-CERTBIN-e3ac93` at one cell).

- **One cell.** n = 19 (F_2[t]/(t^19 + t^5 + t^2 + t + 1)), m = 2, l = 10,
  V = {deg < 10} (polynomial basis), one ordinary binary curve A = 46693,
  B = 306147 (#E = 2 * 261823, h = 2), x(2E) subgroup targets drawn by a frozen
  stream, unconditioned on any closure outcome. Nothing is claimed at any other
  n, curve, cofactor, V, modulus, m, target class or solver.
- **Not** "S_3 systems are refuted at degree 4", and **not** "the refutation
  persists in n": two values of n are not a trend, and the n = 17 cell differs
  in l, modulus shape, curve, cofactor and target class.
- **Not** evidence for or against Semaev's Assumption 1 (the cell lies on its
  diagonal, and W_4 is a Macaulay-type closure, not an F4 step degree).
- **No cost claim.** At m = 2 oracle A (2^10 root-findings per attempt) decides
  satisfiability outright, and parallel Pollard rho (about 453 group operations
  at q = 261823) dominates the DLP. sota_delta zero.

## 1. The finding

W_4 is the least subspace of B_{<=4} containing the plain degree-4 multilinear
Macaulay space M_4 and closed under g -> v_j * g for deg g <= 3 (the degree-4
mutant closure of `EXP-CERTBIN-e94b27`).

> **All 400 unsatisfiable primary attempts are refuted by W_4 at its first
> iteration (400/400, CP95 [0.9908, 1]); none is refuted by M_4 or M_3
> (0/400, CP95 [0, 0.0092]).** Every W_4 refutation carries a
> degree-disciplined wdag-v1 certificate verified by code whose author read
> none of the producers' code; 40 are certified a second time by a blind
> re-derivation. Every M_4 non-refutation carries a checked single-functional
> witness.

The same holds on 600 uniform-x_R systems across three target strata (W_4
600/600, M_4 0/600), so no x(2E) modulation is measurable at either closure.
Soundness held: no satisfiable control was refuted (0/300), and on the
satisfiable S_3 systems and the tensor arm W_4 equals the whole degree-4 part
of the ideal (codim = number of solutions on 150/150).

## 2. What carries it: the tensor's neighbourhood, via degree-2 falls

| | S_3 (400) | N-CONV19: S_3's exact tensor, random lower part (200) | N-PERT19: one tensor coefficient flipped (40) | same-support nulls N-F219, N-AFF19 (400) | one linear fall, N-ELL19 (200) |
|---|---|---|---|---|---|
| W_4 refutes | 400 | 200 | 40 (23 with ell broken) | 0 (derived) | 0 (derived) |
| M_4 refutes | 0 | 0 | 0 | 0 | 0 |
| M_4 dims_by_deg | [0, 1-2, 110-112, 1246, 3711] | [0, 1, 122, 1262, 3727] | about [0, 0, 62, 1181, 3779] (ell broken) | [0, 0, 19, 399, 3819] (semi-regular) | [0, 1, 38, 551, 3800] |

- The refutation is reached only by the first mutant iteration: v_j-products of
  the degree-<= 2 falls alone fill B_{<=3} and contain 1 (red team's own code,
  30 systems).
- **Not S_3-specific at W_4.** Systems keeping S_3's exact quadratic tensor
  (Frobenius-twisted convolution forms) with any affine lower part are refuted
  alike, and so are one-coefficient perturbations of that tensor, with or
  without the cokernel functional ell. The same-support nulls are exactly
  semi-regular, so their non-refutation is forced by derivation (D-3); rows
  reading "S_3 above the nulls" mean "S_3's M_4 is not semi-regular and its
  falls suffice", nothing more.
- **Not ell.** The ell route (1 in rowspace(M_4) + ell * B_{<=3}, equivalently
  1 in the ell-substituted Macaulay space R'_4) fails on every one of 1350
  curve-algebra and tensor-arm systems, and ell-broken perturbations still
  refute.
- **One S_3-specific separation, at D = 3, on 5 systems only:** the degree-3
  mutant closure W_3 refutes 3 of 3 S_3 systems and 0 of 2 tensor-arm systems.
  A located observation, not a rate.

> **The random-model (semi-regular) description again transfers exactly to the
> same-support nulls and not at all to S_3 or its tensor arm** (0 of 1350
> reference profiles on the structured arms).

## 3. Against n = 17: same ceiling, different route

| | n = 17 cell (`KN-FIND-5a8d3e`, `EV-CERTBIN-4a9d2f`) | this cell |
|---|---|---|
| W_4, unsatisfiable subgroup-target arm | 386/386 (82 certified + 304 imported Stage-1 flags) | 400/400, all certified |
| plain M_4 | 324/386 (0.839) | 0/400 |
| 1 in R'_4 (ell route) | 62/62 of the remainder | 0/400 |
| R'_4 fills B'_{<=3} ("FULL") | 61/62 | 0/400 (1090-1126 of 1160) |

The quantities that the decay hypothesis said should shrink did shrink; the
W_4 rate stayed at its ceiling because the first mutant iteration compensates.
The cause of the shrinkage is NOT identified: n, l, modulus shape, curve,
cofactor (h = 4 against 2) and target class all change between the cells.
Quote the two W_4 figures only together with this table.

## 4. Boundaries (these travel with the finding)

1. One curve (h = 2), one V, one modulus, n = 19, m = 2, l = 10. A second n = 19
   curve (h = 4) and the n = 17 h = 2 cell are the separators still owed.
2. W_4 is saturated here: a rate at its ceiling cannot rank systems or show
   specificity. Lower closures (W_3) or harder objects are needed for that.
3. N-PERT19 and W_3 are review verification objects (exact computations by the
   pinned engine and one independent implementation), not trials.
4. Ranks and fall profiles are engine records reproduced by independent code on
   subsets (90 blind systems, 30 red-team systems, all 600 control profiles, all
   2100 M_4 profiles); no certificate format covers a rank.
5. Same model family for the producer, the engine's author and every reviewer;
   mitigated by per-instance certificates checkable against the object
   definition.
6. The plain / masked D = 4 Macaulay filter is not supported as a one-bit
   unsatisfiability filter at this cell (0/400); only a W-type (mutant) filter
   has a persisting rate here, and its cost is unmeasured at any m >= 3.

## 5. What it opens

- `KN-OPEN-3c8f51` item (B), answered per closure at its first step for this
  curve: at plain M_4 the rate is at the nulls' level; at W_4 there is no decay.
  Any answer must name the closure. Item (A) sharpens to: what separates S_3
  from its tensor neighbourhood (seen only at D = 3), and where does the refuting
  neighbourhood end?
- As a resource (EV-CERTBIN-091c56 resource_check): the hypothesis of a structure
  theorem on low mutant degree for convolution tensors (polynomial
  multiplication F_2^l x F_2^l -> F_2^{2l-1}); exponent-adjacent only if it
  survives m >= 3 with bounded degree along the diagonal.
- For DREG / SEMBIN (`KN-OPEN-d218ec`): the semi-regular series does not
  transfer to S_3's m = 2 descent at n = 19, as at n = 17.

## 6. Provenance

`RUN-CERTBIN-a3fc60` of `EXP-CERTBIN-060020`, reviewed in
`REVIEW-CERTBIN-20260926-d7249d`: blind re-derivation (J6, `TASK-20260926-f0736e`),
author-independent verification of every certificate and system (J1,
`TASK-20260926-401771`), population, closure, recomputation and package (J2-J5,
`TASK-20260926-42be88`), contrast pattern, semi-regular model, nulls, the
m = 3 flag, proves-too-much with the nearby-object control N-PERT19, and scope
(J9-J14, `TASK-20260926-fee7a9`), comparison and certificate semantics (J7, J8,
`TASK-20260926-f50294`). Composed into `EV-CERTBIN-091c56`, decided by
`DEC-20260926-901ea1`, archived with this entry by `TASK-20260926-dcc7a5` after
`TASK-20260926-c95c60`.
