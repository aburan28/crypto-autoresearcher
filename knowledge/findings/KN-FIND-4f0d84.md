---
id: KN-FIND-4f0d84
type: internal_finding
title: "On the factor-base locus the Semaev summation fibre S_m(x_1..x_{m-1},T) splits completely over F_p with an exact root multiset and degree formula, so the generic-fibre Frobenius cycle-type census is a no-go as a relation-rate probe (scoped instrument no-go, every m >= 3 by derivation, toy tier)"
tags: [semaev-polynomial, index-calculus, monodromy, chebotarev, relation-rate, prime-field, elliptic-curve, scoped-negative, toy-scale, derivation]
confidence: established
confidence_note: "established for the derivation (two independent blind re-derivations in two rule-12 reviews); not a closure of the relation-rate question"
internal_refs: [EV-MONO-1ef611, DEC-20261017-435b01, DEC-20260810-2f86db, EXP-MONO-4b50b6, RUN-MONO-4b50b6-002, RQ-MONO-001, TASK-20261016-9c1bc5, TASK-20260930-40470a]
proof_status: derivation
proof_refs:
  - coordination/goals/GOAL-MONO-001/review/TASK-20260930-40470a/review_report.md
  - coordination/goals/GOAL-MONO-001/review/TASK-20260930-40470a/s4_construction/computations.json
  - ledger/decisions/DEC-20260930-8553d4.yaml
  - experiments/EXP-MONO-4b50b6/contract.md
  - experiments/EXP-MONO-4b50b6/runs/RUN-MONO-4b50b6-002/verification.json
  - coordination/goals/GOAL-MONO-001/batches/BATCH-003/reviews/TASK-20260802-e2702a/validation_report.md
  - coordination/goals/GOAL-MONO-001/batches/BATCH-003/reviews/TASK-20260802-1b4130/red_team_report.md
  - coordination/goals/GOAL-MONO-001/review/TASK-20261016-9c1bc5/review_report.md
  - coordination/goals/GOAL-MONO-001/review/TASK-20261016-9c1bc5/computations.json
added: 2026-10-17
superseded_by: null
---

Promoted by DEC-20261017-435b01 (knowledge_promotion) from EV-MONO-1ef611,
read with CORR-20261005-a53ac8 and CORR-20261017-4ac525. Every quoted block
below is verbatim from the record named above it.

## Statement

EV-MONO-1ef611 obstruction.scope (i), verbatim:

> (i) CU-1 corrected statement, verbatim: Setting: p > 3, E/F_p
> nonsingular, P_1..P_{m-1} in E(F_p) affine, x_i = x(P_i). Then
> S_m(x_1..x_{m-1},T) = c * prod over sign classes eps (eps_1 = +1) with
> sum eps_i P_i != O of (T - x(sum eps_i P_i)), with c in F_p^*. It splits
> completely over F_p. Its degree is 2^{m-2} minus the number of sign
> classes summing to O, and is exactly 2^{m-2} iff S_{m-1}(x_1..x_{m-1})
> != 0. In P^1 its roots are the 2^{m-2} values x(sum eps_i P_i) with
> multiplicity, where x(O) = infinity. Frobenius fixes every root, so the
> cycle type is 1^{2^{m-2}} on every generic fibre over the factor-base
> locus. [Source: DEC-20260930-8553d4 cures.applied_in_this_decision CU-1
> (file lines 228-237); review_report.md "Corrected statement", lines
> 365-376.]

## Consequence

EV-MONO-1ef611 obstruction.quantity, verbatim:

> The fraction of generic fibres over the factor-base locus (squarefree,
> full degree 2^{m-2}) on which Frobenius acts non-trivially on the roots,
> that is, whose cycle type is other than 1^{2^{m-2}}.

EV-MONO-1ef611 obstruction.value, verbatim:

> 0, an exact dimensionless fraction, BY DERIVATION (the CU-1 corrected
> statement; proof_status derivation). It is NOT a sampled estimate, so no
> sampling error bar applies, and none is stated. The empirical
> corroboration found zero exceptions, cited by location and not
> recomputed here: at m=3, RUN-MONO-4b50b6-002 V4 as EV-MONO-a0a89c OBS-4
> records it ("0 non-split", EV-MONO-a0a89c line 113); and the
> corroboration of review TASK-20260930-40470a, which has no RUN-* id, at
> m=3 and m=4 exhaustively on two curves and m=5 at random, with "Zero
> failures." (review_report.md J1 Findings (a), lines 294-302; raw form in
> computations.json at the keys located in observation OB-1).

CS-QB of DEC-20261017-435b01, verbatim:

> The obstruction value is 0, an exact dimensionless fraction, by
> derivation, for every m >= 3 with p > 3, nonsingular E/F_p and affine
> P_1..P_{m-1} in E(F_p). The "every m" extent rests on the derivation
> alone (the group law and Semaev 2004 Theorem 1, retrieved by
> TASK-20260930-40470a, recalled in TASK-20261016-9c1bc5). Measured
> corroboration, all with zero exceptions and all at toy primes: m=3 in
> RUN-MONO-4b50b6-002 V4 (1,196 off-diagonal factor-base pairs, as
> EV-MONO-a0a89c OBS-4 records it); the TASK-20260930-40470a review
> computations at m=3 and m=4 exhaustive on two curves and m=5 at random
> (2,401 + 117,649 + 10,404 + 182,104 exhaustive tuples, as
> TASK-20261016-9c1bc5 review_report.md Part 4 reads them by key); and
> the TASK-20261016-9c1bc5 blind computations, 439,829 base tuples with
> 316,290 generic fibres at m in {3, 4, 5} on four curves at p in {61,
> 131, 1009, 1999}. No m >= 6 and no prime above 1999 is measured.

## Basis

- proof_status `derivation` (docs/claims-and-verification.md level 2), never
  "proved". proof_refs are EV-MONO-1ef611's proof_refs as corrected by
  CORR-20261017-4ac525 E3 (nine paths).
- The two blind re-derivations named in CORR-20261017-4ac525 E1: "The CU-1
  statement was re-derived blind by two separate rule-12 review-breakthrough
  reviews: TASK-20260930-40470a (DEC-20260930-8553d4 R-BLIND) and
  TASK-20261016-9c1bc5 (Part 1, on disjoint curves and a disjoint code
  lineage)."
- Semaev 2004 Theorem 1, as EV-MONO-1ef611 citations records it: IACR ePrint
  2004/031 (Semaev, "Summation polynomials and the discrete logarithm problem
  on elliptic curves"), provenance retrieved, verified_by
  TASK-20260930-40470a.

## Where the argument stops

The proves-too-much control passes on all three objects (DEC-20261017-435b01
composition.instruments.proves_too_much; TASK-20261016-9c1bc5 review_report.md
Part 5). One sentence per object, as DEC-20261017-435b01 states it:

- Object 1 (generic tuples): the argument stops at "every P_i is in
  E(F_p)", and the statistic varies off the locus, for example 8,120 of
  16,256 generic m=3 fibres on curve A (p=131) and 148,512 of 191,688
  generic m=4 fibres on curve D (p=61).
- Object 2 (D-4 count): the argument stops at "rational over F_p" to "in
  the factor base".
- Object 3 (F_{q^2}, q=131): the argument stops at "rational over F_{q^2}"
  to "in F_q", and the fraction of roots in F_q is not constant.

## What this does not settle

CS-D2 of DEC-20261017-435b01, verbatim:

> What is closed is the generic-fibre Frobenius cycle-type census, in the
> frozen instrument form of EXP-MONO-4b50b6, as a probe of index-calculus
> relation rate. The relation-rate question is NOT closed, the
> relation-supply half of KN-OPEN-009 is NOT answered, and no other
> statistic is closed. The D-4 factor-base-point count is not condemned,
> at any m. EV-MONO-1ef611 resource_check R2 (IDEA-20260803-ff7415) is an
> open, untested lead only: the transfer from F_p to F_{q^n} is an
> untested extrapolation and no exponent statement is made.

CS-K1d of DEC-20261017-435b01, verbatim:

> Nothing in this adoption states or implies that GOAL-MONO-001 criterion
> (a) is met, or that the monodromy on KN-OPEN-009's ordered base is full
> symmetric or wreath. The J4 DISSENT of TASK-20260930-40470a against
> route (a) is carried by reference and persists.

CS-QA of DEC-20261017-435b01, verbatim:

> DEC-20260904-dd58c3 next_action item (3) and the goal-head line
> next_action_2026_09_04 'DECISIVELY CONFIRMED' are read under
> DEC-20260904-dd58c3's own scope_statement: full S_4 monodromy at m=4 over
> the SYMMETRIC base, at toy scale, on 4 curves at 2 primes. Neither
> establishes the absence of an exceptional locus at m=4 for every curve;
> the uniform-in-curve statement is so far a single-reviewer derivation
> (DEC-20260930-8553d4 CU-9) that no committed record has re-derived. This
> closure neither rests on nor asserts those statements, and asserts
> nothing about monodromy on KN-OPEN-009's ordered base (A01 K1d).

CS-N1 of DEC-20261017-435b01, verbatim:

> EV-MONO-1ef611 resource_check R1's sentence "any discriminating content
> left in a relation-search statistic on that locus must therefore come
> from factor-base membership, and factor-base membership is what the D-4
> count measures" is read with one added clause: "or from the
> root-multiplicity structure of the fibre, which is also non-constant on
> the locus (SC-1; IDEA-20260805-90df50)". R1 remains a design input only;
> nothing here states that the D-4 count or the root-multiplicity
> structure discriminates.

Nothing about ECDLP hardness in either direction; toy primes only.

## Supersedes KN-FIND-c41ea9

Supersedes KN-FIND-c41ea9: its at-every-m paragraph is replaced by the
Statement above; its m=3 sections (the discriminant identity, the three
consequences, the density law) stand as committed there and were not
re-reviewed by CU-7; its 'would move an exponent' sentence is read only as
CS-D2's untested R2 lead; its 'No AGENTS.md rule 12 review exists' and
'KN-OPEN-009 is not closed and is not superseded' lines are outdated by
DEC-20261017-435b01.

## Independence

CS-C10 of DEC-20261017-435b01, verbatim:

> Independence is by session and role. By model it holds only as
> reported: the CU-7 reviewer reported claude-fable-5-1; the producers,
> the predecessor reviewer, the A01 author and this composer report
> claude-opus-5-5. No identifier is probe-verified. One reviewer owned
> every joint (plan PD-1), which buys coverage, not cross-reviewer
> independence.
