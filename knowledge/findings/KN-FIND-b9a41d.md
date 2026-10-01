---
id: KN-FIND-b9a41d
type: internal_finding
title: "Linear Gaudry/Diem factor bases F_V: the sigma-stable V are exactly the submodules cut by divisors of T^n - 1; the q-power Frobenius quotient alone gains the mean orbit size g <= n (constant factor); under numbered pinned-dimension cost assumptions it is a net win iff q^(l' - l*) < g(l'); at q = 2, n in {131, 163} the only faithful stable subspace has dimension n - 1 and the quotient on it is a net loss for m = 2..5 in every cost model examined"
tags: [ecdlp, frobenius, index-calculus, factor-base, gaudry-diem, subfield-curve, normal-basis, cyclotomic-cosets, orbit-quotient, constant-factor, structural-exact, reviewed]
confidence: established
confidence_note: >-
  `established` for the structural statements (1)-(3) below: they are short
  derivations, computed exactly by RUN-FROB-627924, reproduced by an
  independent validator with its own code, and reproduced by a blind
  re-derivation that read none of the producer's artifacts. Statement (4) is
  established AS A CONDITIONAL on the numbered model assumptions MA-1 to MA-4;
  its verdicts are exact outputs of that model, not measurements of any
  pipeline. Custody caveat: preregistration ordering of the producing experiment
  cannot be shown from git (CORR-20260923-28b2da E3); the basis of this entry is
  derivation plus independent recomputation plus blind agreement, not
  preregistration.
internal_refs: [EV-FROB-d336b0, DEC-20260923-e6cd5d, EXP-FROB-ec08b5, DEC-20260922-5796b8]
internal_refs_note: >-
  EV-FROB-d336b0 is cited only together with CORR-20260923-28b2da, and
  H-FROB-6774fb only as restated by CORR-20260923-9a3529. DEC-20260922-5796b8's
  proposed KN-FIND sentence was NOT adopted (CORR-20260923-f1e5bc D1).
related_refs: [H-FROB-6774fb, RQ-FROB-7d8dd4, GOAL-FROB-6333a9, RUN-FROB-627924, CORR-20260923-9a3529, CORR-20260923-28b2da, CORR-20260923-f1e5bc, REVIEW-FROB-20260923-458763, KN-LIT-796, KN-OPEN-095df5, IDEA-20260918-9abf42]
proof_status: derivation
proof_refs:
  - experiments/EXP-FROB-ec08b5/runs/RUN-FROB-627924/raw-result.json
  - experiments/EXP-FROB-ec08b5/runs/RUN-FROB-627924/checkpoint/target_table.json
  - experiments/EXP-FROB-ec08b5/runs/RUN-FROB-627924/checkpoint/curve_panel.json
  - coordination/goals/GOAL-FROB-6333a9/batches/BATCH-458763/reviews/TASK-20260923-69e71b/computations.json
  - coordination/goals/GOAL-FROB-6333a9/batches/BATCH-458763/reviews/TASK-20260923-33a48b/computations.json
  - coordination/goals/GOAL-FROB-6333a9/batches/BATCH-458763/reviews/TASK-20260923-21ae7f/computations.json
proof_status_note: >-
  Copied from EV-FROB-d336b0 (`derivation`); not exceeded. `derivation` means
  checkable written arguments confirmed by exact computation, not a
  machine-verified proof.
review_refs: [TASK-20260923-69e71b, TASK-20260923-33a48b, TASK-20260923-21ae7f]
promoted_by: DEC-20260923-e6cd5d
added: 2026-09-23
superseded_by: null
---

# Frobenius-stable linear factor bases: classification, pi-quotient gain, and the trade

## Scope (read first)

Every statement below is about the **linear Gaudry/Diem family**
F_V = {P in E(F_{q^n}) affine : x(P) in V}, V an F_q-subspace of F_{q^n}, with
pi(x, y) = (x^q, y^q) the **q-power Frobenius**. It is not about non-linear
factor bases, decomposition cost, solving or first-fall degree, or any
comparison with Pollard rho. claim_kind: **constant_factor**.

## Key claims

**(1) Classification.** With sigma the q-power Frobenius on F_{q^n}, the
sigma-stable F_q-subspaces are exactly the submodules of F_{q^n} as an
F_q[T]-module (T acting as sigma). They correspond one-to-one to the monic
divisors of T^n - 1, so the attainable dimensions are exactly the subset sums
of the degrees of the irreducible factors of T^n - 1, counted with
multiplicity when p | n. For n prime with gcd(q, n) = 1 this is the lattice
{a + b d : a in {0,1}, 0 <= b <= (n-1)/d}, d = ord_n(q), which is the full
interval exactly when q = 1 mod n. sigma is the identity only on {0} and F_q,
so for n prime the least faithful stable dimension is d.
Prior art: for gcd(q, n) = 1 this classification is in Galbraith, Granger,
Merz and Petit 2020, sections 3.2 and 4.1 (KN-LIT-796; provenance retrieved,
verified_by TASK-20260923-33a48b). What this program adds is the p | n cells,
exact spectra at the enumerated degrees, the orbit census and the conditional
trade (4).

**(2) Stability of F_V.** If V is sigma-stable then F_V is pi-stable. The
converse holds for the set of x-coordinates of F_V (pi-stable iff that set is
sigma-stable), so V is sigma-stable whenever the x-coordinates of F_V span V.
Degenerate F_V whose x-coordinates span a smaller subspace can be pi-stable for
non-stable V; every one observed has at most 3 points, all pi-fixed, with no
orbit content (validator F-J1-5).

**(3) The pi-quotient's gain.** For n an odd prime, gcd(q, n) = 1, and E/F_q
ordinary with a Weierstrass model whose coefficients do not all lie in a
proper subfield of F_q (automatic for q prime), every pi-orbit on F_V has
length 1 or n, length 1 exactly on the affine points of E(F_q) in F_V. With f
that number, the pi-quotient divides the class count by
g = |F_V| / (f + (|F_V| - f)/n) <= n, which tends to n only as |F_V|/f grows.
This bound is on the **pi-quotient alone**. On the same F_V, larger groups give
larger classes: pi with negation gives size 2n; extra automorphisms at special
j give more; and if E has a model over F_{q0}, q = q0^k, the q0-power
Frobenius has order kn on E(F_{q^n}) and the Frobenius gain is measured
against kn, the degree over the field of definition, not against n
(certificate: TASK-20260923-33a48b COMP-PTM7). Curves merely isomorphic to a
subfield model were not examined.

The exact orbit-count identity behind (3) is a theorem under its premises. Its
exact agreement with the implementation on 14 toy-scale rows (12 with orbit
content, |F_V| up to 4005) is an implementation-consistency check, **not**
confirmation of a hypothesis that could have failed.

**(4) The trade, conditional.** Under the numbered model assumptions
- MA-1 baseline pinned at l* = ceil(n/m);
- MA-2 orbit pipeline at l' = the least faithful attainable l >= l*;
- MA-3 equal per-relation cost (per-attempt cost times inverse success
  probability) at l' and l*;
- MA-4 relation collection proportional to classes, sparse linear algebra to
  classes squared;

the pi-quotient is a net win in both stages **iff q^(l' - l*) < g(l')**, with
g(l') the exact mean orbit size (not n). Outside MA-1 to MA-4 the verdict at
most enumerated (q, n, m) cells depends on the cost model
(TASK-20260923-33a48b per_cell_classification).

**(5) At (q, n) = (2, 131) and (2, 163).** T^n - 1 = (T - 1) Phi_n with Phi_n
irreducible over F_2, so there are exactly four sigma-stable subspaces, of
dimensions {0, 1, n - 1, n}, and the only faithful ones have dimension n - 1
and n. A faithful linear pi-stable factor base therefore **exists**, at
dimension n - 1. For every m in {2, 3, 4, 5} the pi-quotient on it is a **net
loss**: under MA-1 to MA-4 by 56.97 to 95.97 bits at n = 131 and 72.65 to
121.65 bits at n = 163 (margin log2 g - (l' - l*) log2 q). These values were
computed by the producer, recomputed by the validator on all 64 enumerated
verdicts, and re-derived blind. The loss also holds in every other cost model
the red team examined: the pinned model under two decomposition-probability
variants and any per-decomposition cost non-decreasing in dimension, and a
rebalanced model for per-attempt cost 1 to 2^40 (TASK-20260923-33a48b
COMP-J3-COST, a single review computation). "In every cost model examined" is
the claim; "in every cost model" is not.

## What this finding is NOT

- Not a statement about non-linear pi-stable factor bases. Unions of
  Frobenius orbits of index-calculus size exist at n = 131 (field-level
  witness TASK-20260923-33a48b COMP-PTM5; the open question is KN-OPEN-095df5).
- Not a bound on all symmetry gains (see (3)).
- Not a statement about decomposition cost, Semaev-polynomial constructibility,
  or whether index calculus is competitive with Pollard rho at any parameter.
- Not asserted for even or composite n, for gcd(q, n) > 1 beyond claim (1),
  or for curves with a model over a proper subfield of F_q.
- Not a statement about any deployed curve or system.

## Evidence and review

- Producer: EXP-FROB-ec08b5 / RUN-FROB-627924, EV-FROB-d336b0 (strength
  `strong` on the basis restated by CORR-20260923-28b2da).
- Review round REVIEW-FROB-20260923-458763: validator TASK-20260923-69e71b
  (J1/J2/J5; values reproduced, wording and custody broken), red team
  TASK-20260923-33a48b (J3/J4; scope and cost-model findings), blind
  re-derivation TASK-20260923-21ae7f (J6; every value agrees). Composed in
  DEC-20260923-e6cd5d, with no tripwire fired.
- Custody: preregistration ordering cannot be shown from git; the outputs of any
  other execution of the producing driver, if one occurred, are declared lost
  (CORR-20260923-f1e5bc D4). No value here depends on them.

## Relevance

For the GOAL-FROB-6333a9 lane, (1) fixes which linear stable factor bases exist
at the goal's cells and (5) settles the linear-family case at n = 131 and 163.
The goal's own question, whether an invariant factor base prunes WDSat
conflicts, is untouched.
