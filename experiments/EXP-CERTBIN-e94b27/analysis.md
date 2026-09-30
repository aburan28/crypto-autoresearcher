# EXP-CERTBIN-e94b27 (RC-1): analysis of RUN-CERTBIN-c417e0

Composed by the Coordinator in /review-evidence from
REVIEW-CERTBIN-20260924-3d7e1a. Evidence record: EV-CERTBIN-4a9d2f. Decision:
DEC-20260924-e61f3b (support, scoped to H-CERTBIN-5e71c9 claim C1). Claim tier:
toy. sota_delta zero; oracle A per attempt and parallel rho for the DLP
dominate. Every number below is read from the run files or a reviewer file
named beside it.

## Validity (checked before any interpretation)

- Run count: 1 of 2 permitted; no failed attempt and no infrastructure re-run
  (DEC-20260924-5b1c8e validity_precheck).
- Schema: complete through manifest_v2.yaml; J3 found no existing key changed
  or removed and eight leaf keys added (VAL-20260924-60b7cf, manifest_v2_key_diff).
- Seeds: S_selftest 2026092430099 only; no instance was drawn.
- Raw/summary agreement: J4 recomputed 71 items from the per-instance records
  with its own aggregation code, with 0 differences.
- Controls: all eleven pass, with the J3 findings F-J3-1 (C-VERIFIER negatives
  from one kind; remedied), F-J3-2 (C-MONO's W_5 clauses cannot fail here),
  F-J2-1 (C-SELF never reached a fixpoint index >= 2; remedied).
- Certificates: 268 submitted, 268 verified by the run's same-author verifier
  (EX-10), and 268 of 268 by the author-independent verifier J1
  (VAL-20260924-d235c7). J1's 1340 negative controls were all rejected.
- Admissibility (plan composition): J1, J2, J3 and J6 hold, so the run is
  admissible. J4 holds, so the mechanical verdicts stand.

## Observation

- MR1: a = 62 of 62 U62 instances refuted by W_4, CP95 [0.942237365570709, 1].
  All 62 are first refuted at iteration 1. RC1-DR-1: ARTIFACT (predominant).
  E-A is not falsified; E-G is falsified.
- MR2: b = 62 of 62 refuted by M_5. MR3: r = 62 of 62, labels {W4: 62}.
  RC1-DR-2: CLEAN (L1 = L2 = CLEAN). RC1-DR-3: M_5 SUFFICES.
- MR4: N-AFF62 and N-F262 are each W_4 0/62 (CP95 [0, 0.0577626344292909])
  and M_5 62/62. W_5 never ran on them. RC1-DR-4: S_3-SPECIFIC at W_4, NOT
  DISTINGUISHED at M_5.
- MR5: satisfiable controls refuted W_4 0/62, M_5 0/62, W_5 0/10. On S62,
  codim(W_4 in B_{<=4}) = s on 62/62 (J9 O1).
- Certificate shape (J1): every U62 W_4 flat certificate has max deg mu = 3
  and max row degree 5; every C20 one has max deg mu = 2. |C| for W_4|U62 is
  1296 / 1372 / 1542 (min / n//2 element / max).
- W_4 certification (J6): every one of the 62 U62 W_4 refutations carries a J5
  W-certificate (every intermediate of degree <= 4). J6's own checker accepts
  it. Separately, J7 verified 62 structured witnesses (C_4, a) against two
  constructions.
- Mechanism (J7): after substituting ell, R'_4 contains 1 on 62/62. Its fall
  profile (d = 0..3) is [1, 18, 154, 834] on 61 instances and
  [1, 17, 153, 833] on 1, against the semi-regular [0, 0, 16, 288].
  dim(M_4 cap B_{<=3}) is 964-978 on U62, against 323 on the nulls. M_4 holds
  4-12 independent linear forms. The non-ell fallen polynomials alone give
  W^(1) = B_{<=4} on 62/62. M_4 + ell * B_{<=3} has dimension only 3047 (or
  3046).
- Nulls (J8): exactly semi-regular at D = 4 on 124/124 (rank M_4 = 2771,
  W_4 = M_4). They attain the bilinear-support rank ceiling 12364 at M_5.

## Comparison

- Blind re-derivation against the run (J5 vs run, compared by J6): 97
  instances; 2267 cells agree, 0 disagree, 231 are re-deriver only and 218 are
  not applicable. Most items sit at a floor or ceiling. The discriminating ones
  also agree: U62 ranks, the R_4 fall profile at d = 3, per-iteration
  low-basis sizes, S62 s and S62 W_4 dimensions.
- Author-independent against same-author verification (J1 vs run): 268 of 268
  agree on verdict, |C| and max deg mu. MR1-MR4 recounted from J1 alone give no
  verdict change.
- Literal against semi-naive W_D (J2): equal on 6 archived instances. On
  15090 constructed systems there are 0 mismatches, with fixpoint index >= 2
  on 545 + 8359 + 65 of them.
- S_3 against nulls against N-ELL (J8, J9): S_3 is refuted by W_4 62/62. The
  same-support nulls are refuted 0/62 each, forced by exact semi-regularity.
  A one-linear-fall generic family (N-ELL, a verification object) is refuted
  0/20, at the exactly predicted dimension 3162.
- Against the pre-data prior: (a) expected MIXED (a in [15, 50]) and is
  overturned. (b), (c) and (d) are consistent.

## Inference

1. The 16% of the Stage-1 unsatisfiable arm "not reached at D <= 4" is a
   plain-Macaulay closure artifact at this cell. Every one of the 62 has a
   refutation inside W_4, so the whole arm is refuted at W_4: 386/386, with 82
   certified in RC-1 and 304 resting on reviewed Stage-1 flags. E-G is
   falsified.
2. The cause is that S_3's M_4 is far from semi-regular. ell is one sufficient
   route but is neither necessary nor generically sufficient. The semi-regular
   model fits the same-support nulls exactly and does not transfer to S_3.
   That is why pre-data prior (a) failed.
3. The W_4 S_3-specificity is real, but it is relative to same-support random
   bilinear systems. It restates the M_4 fall-profile difference.
4. The CLEAN label carries no S_3 content: the nulls would be CLEAN through
   M_5, and D_reg = 5 again at n = 19. DEC-20260923-f25b97 NA-5 is therefore
   decided on the D = 4 signal, not on CLEAN.

## Limitation

- One run, one curve (h = 4), one V, n = 17, m = 2, l = 9, x(2E) subgroup
  targets only. U62 is conditioned on a Stage-1 outcome. No transfer to other
  n, curves, V, m, target classes or F4 is assumed.
- The run's flat certificates certify rowspace(M_5), not W_4
  (DEC-20260924-5b1c8e R-8). The W_4 qualifier rests on review witnesses.
- The executor and every reviewer share one model family (PD-R3).
- The mechanism readings rest on exact reviewer computations, one
  implementation each, and on a verification object (N-ELL) that is not
  evidence about H-CERTBIN-5e71c9.
- N-AFF62 is one affine draw. No null shares S_3's quadratic part. N-CONV is
  untested.
- The development-run ordering is unauditable. Code-at-use binding covers
  closure.py and verify_cert.py only.
