# SNFS-E1 prescribed-fibre surface design audit

- task_id: T-980
- fencing_epoch: 1
- idea_id: IDEA-20261009-b01e42
- hypothesis_id: H-ECDLP-bd1572
- goal_id: GOAL-ECDLP-001
- related_hypothesis_id: H-XEDN-fe3446
- related_experiments: EXP-XEDN-004, EXP-XEDN-affa94
- idea_status: proposed
- idea_approval: false
- parent_hypothesis_status: proposed
- goal_status_change: none
- scientific_result: none
- disposition: keep proposed; do not approve or dispatch
- priority: high conditional on dependency repair

## Scope and novelty boundary

This is a Coordinator design and lineage audit, not an execution record. It
does not approve IDEA-20261009-b01e42, change any hypothesis, experiment, or
goal status, create evidence, or dispatch a task. The idea remains proposed
with approved_by: null; H-ECDLP-bd1572 remains proposed. EXP-XEDN-004 is
approved; EXP-XEDN-affa94 is review_required and is not execution-authorized.
Those statuses are recorded, not modified.

The exact novelty is the realization problem: can a prescribed ordinary curve
E/F_p occur as the fibre at a fixed t_0 of an elliptic surface over F_p(t)
whose Mordell--Weil rank is high? Acceptance therefore requires both an
explicit F_p-fibre isomorphism, including its twist class, and a separate rank
certificate over F_p(t).

This is distinct from the existing free-x XEDN census. EXP-XEDN-004 searches
low-degree integral sections on non-isotrivial surfaces with a != 0,
deg(a) <= 2, deg(b) = 6, and non-constant j, at p in {7,13,19,31}. Its
primary observable is the infinity norm of a shortest verified section
relation. It does not constrain a surface through a selected fibre and does
not measure high-rank realization of a chosen target. E1 may reuse its
discriminant, minimality, group-law, specialization, canonical-height, and
artifact-binding lessons, but must not relabel free-x relations as
prescribed-fibre evidence.

KN-TECH-06bb4e places this adjacent question in the function-field F5 face:
it identifies the lifting obstruction but does not provide a prescribed-fibre
construction. H-ECDLP-bd1572 treats a high-rank function-field lift as one
heuristic escape route from its special-prime hypothesis. A finite E1 census
can test that realization boundary; it cannot close the escape route or make
an asymptotic claim.

## Overlap and the rank ceiling

KN-FIND-004, H-XEDN-fe3446, and EXP-XEDN-004 provide reusable controls:
group-law verification and specialization are required, and a polarization Gram
is not a geometric Mordell--Weil rank. EXP-XEDN-affa94 further requires
height, reducible-fibre, planted-search, and matched E_8 controls. These are
methodological dependencies, not duplicate E1 measurements.

For chi = 1 surfaces in the XEDN all-I_1 class, the Shioda--Tate ceiling is
8 and the canonical height lattice is E_8; this is the ceiling described by
H-XEDN-fe3446 and tested as a design issue by EXP-XEDN-affa94. It does not
answer prescribed-fibre realization. It concerns a restricted surface class,
says nothing about whether a chosen E/F_p is a fibre, and does not distinguish
rank over F_p(t) from geometric rank.

KN-FIND-6b3e17 is also not an answer: its exact rank-8 base-rank example is
over Q(t), and its rank-12 specialization demonstrates why base rank and
specialization rank have different quantifiers. It is useful as a rank and
Shioda--Tate calibration fixture only. A rank-8 unconstrained XEDN surface is
reuse or calibration, not E1 evidence.

## Protocol defects

1. The filed cells p in {2^8, 2^12, 2^16} are not prime fields. They cannot
   be silently treated as extension fields: the fibre, twist, point-count, and
   rank problems would change. A future contract must use a certified prime
   list.

2. Rank over F_p(t) and rank over the algebraic closure must be recorded
   separately. Sections over F_{p^d}(t) do not count as F_p(t) sections. A
   zeta calculation must not be presented as an F_p(t) rank certificate
   without a source-valid interpretation of Frobenius eigenspaces and an
   independent section or upper-bound check.

3. Matching j is insufficient. The future protocol must freeze t_0, the exact
   target equation and model, smoothness, an explicit F_p isomorphism, and the
   exact twist class. A fibre isomorphic only after field extension is a wrong
   target.

4. The proposal uses recalled claims about Tate and Shioda--Tate. The named
   sources must be read and bound, with applicability recorded. If zeta
   reconstruction is used, retain #S(F_{p^k}) for the fixed ladder
   k = 1,...,12*chi-2, the reconstruction receipt, field/bit-operation
   counts, memory, and per-surface point-count cost. A final rank number
   without those inputs is not a certificate.

5. “Random A,B constrained through E” does not specify free coefficients,
   distribution, normalization, minimality, discriminant rejection, or seed
   derivation. Rejection after seeing rank would select the outcome.

6. Ulmer, Shioda/Fermat, constant-j, and supersingular families are selected
   constructions, not a random sample. The family list, equations, twists,
   and testing order must be frozen before target matching. Failed and
   low-rank valid surfaces remain counted.

7. The density denominator is absent. The audit must distinguish
   N_confirmed / N_attempted_valid from target coverage
   |R_(p,chi,r)| / |T_p|, where T_p is the predeclared set of ordinary
   (E, twist-class) targets. Distinct j values, fibre occurrences, and target
   pairs are separate statistics. No post-selection may shrink the denominator.

8. Twist-search success, checked no-match, timeout, and
   arithmetic/infrastructure failure require distinct labels. A bounded failed
   search is right-censored evidence about that search budget, not proof of
   unrealizability. “All but O(1) targets” is not supportable from censored
   counts.

9. Every row needs certificates for the prime, target curve, surface
   coefficients, discriminant, minimality, smooth fibre, isomorphism/twist,
   section identities, and rank. Zeta rows need raw point counts and hashes;
   section rows need exact rational functions, specialization checks, and an
   independent checker. A failed certificate is invalid or infrastructure
   evidence, not a negative mathematical observation.

## Bounded repair path

The first phase should be exactly the 12 cells:

    chi in {1, 2, 3}
    p   in {7, 13, 19, 31}

Use t_0 = 0 and one predeclared ordinary target panel per (chi,p). The target
equations, point encodings, twist classes, and primality certificates must be
in the frozen manifest; the invalid powers-of-two cells must not be inferred
or silently converted.

Use these separate coefficient families:

- C_(chi,p,E), the primary constrained null:
  A(t)=a_0+t A_1(t), B(t)=b_0+t B_1(t), with deg(A)<=4*chi and
  deg(B)<=6*chi. Free-coefficient distributions, leading-coefficient rules,
  minimality tests, rejection reasons, and seeds are fixed before sampling.
- U_(chi,p), the matched unconstrained family with the same degree bounds,
  coefficient law, seed separation, and validity filters, but without the two
  specialization equations. It measures constraint effects and is not a
  prescribed-fibre success arm.
- H_(chi,p), a finite list of source-pinned Ulmer, Shioda/Fermat, or other
  named high-rank families. Twists use A_d=d(t)^2 A and B_d=d(t)^3 B;
  d(t_0) square class is recorded, not inferred from j. The family and
  candidate-twist lists are frozen before target matching.

For every accepted surface, certify the exact F_p fibre/twist, separate
rank_Fp(t) and rank_geometric, and retain the fixed zeta point-count ladder
or an independent rank certificate with exact F_p(t) sections, height/regulator
data, and a source-valid upper bound. Include constant-j, supersingular, and
reducible-fibre nearby controls at the same cells; none is credited as ordinary
prescribed-fibre success. The random constrained null must retain exactly
1,000 attempted surfaces per (chi,p,E) cell, including valid low-rank and
failed-certificate rows.

For every named high-rank family and target cell, freeze 1,000 twist
candidates. Retain every candidate and classify it as success,
checked_no_match, censored_timeout, or invalid_infrastructure. Stop after the
fixed candidates and null attempts are processed or at the declared hard
resource limit; no favorable-hit extension is allowed. Report both density
denominators and the complete censoring table.

The claim ceiling is finite: realization and rank distributions only for the
12 cells, target panel, named families, and fixed search caps. It excludes an
asymptotic density, universal nonexistence, a general rank construction, an
ECDLP improvement, and transfer to cryptographic-size parameters.

## Disposition and next action

Keep IDEA-20261009-b01e42 proposed. Do not approve or dispatch it. Priority is
high, conditional only if the dependencies are repaired: prescribed-fibre
realization is distinct and relevant, but the current cells, rank
quantifiers, target predicate, family measure, denominators, censoring, and
certificates are not runnable.

The next artifact must be written at:

    coordination/goals/GOAL-ECDLP-001/proposals/SNFS-E1-PRESCRIBED-FIBRE-20261010/prescribed-fibre-protocol.yaml

It must bind the target panel, 12 cells, coefficient families, source-pinned
high-rank families, twist caps, rank/zeta certificates, controls, budgets,
censoring, and review handoffs. After an EXP-* record is minted from that
protocol, the exact readiness gate is:

    python3 tools/newest_experiments.py --experiment <minted EXP-SNFS-E1-ID>

It must report execution_state: ready before any approval decision. This audit
does not run that command or python3 tools/research_dispatch.py --ready-only.
