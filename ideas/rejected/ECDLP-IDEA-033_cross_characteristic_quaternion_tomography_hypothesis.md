# ECDLP-IDEA-033 — Cross-characteristic quaternion tomography

## Status and claim labels

- Class: `representation`
- Risk band: `high-risk`
- State: `proposed_unapproved`
- Evidence scale: `toy` construction only
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a compatible lift, a computed maximal quaternion order, or a correct toy projection is not an ECDLP break.

## Falsifiable hypothesis

For a declared family of prime-order inputs `Q=[x]P` in `E(F_p)`, there is a
target-independent cross-characteristic globalization of `(E,P,Q)` to two sections of
one finite flat cyclic order-`N` subgroup scheme, preserving their unknown scalar
relation, with sufficiently many supersingular auxiliary fibers.  In each
fiber, the maximal quaternion endomorphism order admits a certified split realization
modulo `N` and a public rank-one tomography panel whose responses on the specialized
points give exact linear coordinates.  Intersecting the response equations recovers
`x mod N` with complete time and bit-memory exponents below `1/2`, after charging the
globalization degree and height, auxiliary-prime search, endomorphism-ring construction,
quaternion-element degree, coordinate orientation, ambiguity, and verification.

## Mechanism-new operation

Apply **cross-characteristic marked specialization followed by quaternion-module
tomography**.  After specializing a common marked lift at supersingular primes, compute
maximal orders `O_i=End(E_i)` and certified splittings
`O_i/N O_i ~= M_2(F_N)`.  The proposed new operation is a target-independent evaluator
that turns rank-one idempotents in these split quaternion algebras into publicly oriented
linear functionals `c_(i,j):E_i[N] -> F_N` without an `N`-entry point table, a pairing,
or a DLP in the torsion module.

This is not the toric or Tate-curve degeneration of `ECDLP-IDEA-016`: no multiplicative
group DLP is substituted at a bad-reduction fiber.  It is not the height-compressing
global lift of `ECDLP-IDEA-005`: global height relations and lattice reduction are not
used.  It is also not a same-field isogeny walk or endomorphism speedup: the auxiliary
fibers have different residue characteristics, and success requires a new labeled
quaternion coordinate rather than another curve neighbor.  Weil, Tate, and reduced Tate
pairing calls are forbidden in the mechanism arm.

## Assumptions

1. `E/F_p`, `P`, `Q`, and prime `N=ord(P)` with `N=p^(1+o(1))` are public, while `x` remains blinded during construction.
2. A number field, integral elliptic model, common cyclic order-`N` subgroup scheme, its two marked sections, and all primes of reduction are constructed from the encoded input without using `x` or a scalar-indexed table.
3. Specialization preserves the exact unknown relation between the marked sections and is injective on their common order-`N` subgroup at every accepted auxiliary fiber.
4. Each maximal order, its splitting modulo `N`, every lifted idempotent, and the point-response orientation are independently certified.
5. Field degree, coefficient height, unsuccessful lift and prime searches, endomorphism degrees, extension fields, response collisions, and stored bits are charged.
6. Any pairing, same-field isogeny path, hidden torsion basis, known-log coordinate, or target-trained selector invalidates the mechanism arm.
7. All evidence remains toy, heuristic, model-bound, and novelty-unverified.

## Semantic fingerprint

`cross_characteristic_marked_globalization | supersingular_maximal_quaternion_orders | rank_one_mod_N_tomography | public_torsion_coordinate_intersection`

## Five closest ledger entries

1. `ledger/H-ISO-001.yaml` — distinguishes cross-characteristic tomography from a same-field isogeny neighborhood.
2. `ledger/EV-ISO-001.yaml` — supplies the matched same-field isogeny control and no-yield boundary.
3. `ledger/H-REP-001.yaml` — prevents a quaternion basis rewrite without a new point-coordinate operation from counting.
4. `ledger/FINDING-PF-IC-001.md` — motivates replacing relation collection with a direct, fully costed scalar coordinate.
5. `ledger/SYNTHESIS-20260716.md` — supplies the end-to-end verification, generic-baseline, and no-breakthrough boundary.

## Closest primary literature

- Juan Marcos Cerviño, [On the Correspondence between Supersingular Elliptic Curves and maximal quaternionic Orders](https://arxiv.org/abs/math/0404538), gives a deterministic explicit endomorphism-ring computation for supersingular elliptic curves and concrete maximal-order examples.
- John Tate, [Endomorphisms of Abelian Varieties over Finite Fields](https://eudml.org/doc/141848), proves the finite-field relationship between homomorphisms and Tate-module maps that bounds what an endomorphism realization can reveal.
- Victor Shoup, [Lower Bounds for Discrete Logarithms and Related Problems](https://www.shoup.net/papers/dlbounds1.pdf), supplies the generic lower-bound control when the proposed lift and tomography can be simulated using only group operations.

These primary sources establish the supersingular quaternion-order and Tate-module
boundaries.  They do not construct a target-independent globalization of arbitrary
marked prime-field torsion, a sub-square-root family of auxiliary fibers, or a publicly
oriented point-coordinate evaluator.  No novelty claim is made; novelty is unverified.

## Complete factor-base-to-target-descent path

The replacement factor base is the frozen collection of oriented quaternion projection
responses of the public anchor `P`, not a point-support set or relation matrix.

1. Freeze the globalization search space, integral models, auxiliary-prime bounds, maximal-order algorithm, splitting convention, idempotent panel, and rejection rules before inspecting any scalar labels.
2. Construct a common marked lift `(mathcal E, mathcal C, mathcal P, mathcal Q)` whose reduction at the original prime is `(E,<P>,P,Q)`, certify that `mathcal C` is finite flat cyclic of order `N` with both sections in `mathcal C`, and preserve their unknown scalar relation without extracting it; retain every compatible lift branch.
3. Find the frozen number of good auxiliary primes at which the specialized curve `E_i` is supersingular and the marked subgroup specializes injectively; compute and certify `O_i=End(E_i)` and `O_i/N O_i ~= M_2(F_N)`.
4. Construct the frozen rank-one quaternion panels, evaluate every public functional on `P_i` and `Q_i`, and retain all coordinate-orientation and zero-denominator branches.
5. For each usable response solve `c_(i,j)(Q_i)=x*c_(i,j)(P_i) mod N`, intersect all candidate sets across panels and fibers, transport the survivors back to the original curve, and return only a scalar satisfying `[x]P=Q`.

## Full rho/BSGS cost model

Let the reciprocal availability of a compatible marked globalization be `N^zeta`, one
globalization attempt cost `N^c`, number-field degree and coefficient-height handling
cost `N^(d+h)`, and the number of retained auxiliary fibers be `N^m`.  Let search per
fiber cost `N^a`, certified maximal-order and splitting construction per fiber cost
`N^q`, tomography panels per fiber number `N^t`, maximum lifted-endomorphism
degree/evaluation cost `N^kappa`, oriented response extraction cost `N^r`, residual
candidate-list size `N^u`, verification per candidate `N^v`, and other bit storage
`N^s`.  These are total bit-cost exponents, not uncharged algebraic-operation counts.

- Pollard rho costs `(sqrt(pi*N/2)+o(sqrt(N)))` group operations, exponent `1/2`, and `N^o(1)` stored group elements.
- BSGS costs `(2+o(1))*sqrt(N)` group operations, exponent `1/2`, and `N^(1/2+o(1))` stored points.
- Expected globalization costs `N^(zeta+c+o(1))`; arithmetic in the global model costs `N^(d+h+o(1))`.
- Auxiliary search and maximal-order construction cost respectively `N^(m+a+o(1))` and `N^(m+q+o(1))`.
- Quaternion tomography costs `N^(m+t+kappa+r+o(1))`; this includes materializing and evaluating every panel element.
- Candidate intersection and verification cost `N^(u+v+o(1))`.

The complete time exponent is
`lambda=max(zeta+c,d+h,m+a,m+q,m+t+kappa+r,u+v)`.  The bit-memory exponent is
`mu=max(s,d+h,m+t+kappa,u)`, including number-field data, maximal orders, panel
elements, orientations, and candidate lists.  A degree-`N`, norm-`N`, or scalar-labeled
quaternion basis contributes exponent at least `1`; an order-`N` module DLP contributes
at least `1/2`; either kills promotion.

## Likely fatal obstruction

The first obstruction is globalization.  A mod-`p` curve with a marked point of prime
order `N` is level-structure data, and lifting both `P` and `Q` compatibly to a common
characteristic-zero object can require number-field degree or coefficient height at least
`N^(1/2-o(1))`; selecting the compatible lift of `Q` may itself encode `x`.  Supersingular
auxiliary reductions of that same marked object may be too sparse or expensive to find.

The second obstruction is the unlabelled quaternion DLP.  Although
`O_i/N O_i` can split as `M_2(F_N)`, the induced `E_i[N]` module has no public orientation
from ordinary point encodings.  Reading `c_(i,j)(R)` can therefore be exactly an order-`N`
DLP in a different basis.  Because `N` is prime, a small-degree endomorphism restricted
to `<P_i>` is either zero or injective; it does not expose small scalar residues.  Lifting
rank-one idempotents modulo `N` may also force norm or degree `Omega(N)`.  Multiple
fibers preserve the same hidden scalar but do not by themselves label it.

## Proof track

Construct a target-independent marked globalization and a certified family of
supersingular fibers; prove faithful specialization of the order-`N` sections; construct
maximal orders, splittings, and rank-one panels; prove that the point-response evaluator
is public, pairing-free, scalar-table-free, and separating; then prove
`lambda,mu<1/2` with every failed lift, field bit, endomorphism degree, and orientation
branch included.

## Disproof track

Prove that compatible marked globalizations or suitable auxiliary fibers require
square-root-or-larger degree, height, or search; show that every usable quaternion
idempotent has norm or evaluation cost `N^(1/2-o(1))` or larger; or reduce public response
orientation to DLP in `E_i[N]`.  A proof that every panel is zero, injective-but-unlabelled,
or equivalent to a pairing closes only this exact tomography mechanism.

## Positive and negative controls

- Positive algebra control: tiny supersingular curves with exhaustively known maximal orders, full `N`-torsion, and oracle module coordinates.
- Positive transport control: independently verify specialization of `O`, `P`, `Q`, and `P+Q` through every accepted marked lift.
- Negative representation control: randomly conjugate each splitting of `O_i/N O_i`; a claimed public scalar must be invariant after the frozen orientation rule is reapplied.
- Negative fiber control: matched ordinary auxiliary fibers, whose commutative endomorphism algebras must not appear to supply quaternion tomography.
- Same-field control: run the same response accounting on the original curve and on small-degree same-field isogeny neighbors; constant-factor endomorphism gains are not mechanism success.
- Pairing control: audit operation traces for Weil, Tate, reduced Tate, or distortion-map pairing evaluation and invalidate any contaminated run.
- Circularity control: blind scalar labels and forbid point-to-coordinate tables until all lift, order, panel, and orientation hashes are frozen.

## Quantitative promotion and falsification gates

The toy preflight uses prime `N<=31`, original characteristics `p<=251`, global fields of
degree at most `8`, coefficient heights at most `2^16`, auxiliary characteristics at most
`257`, and every compatible branch inside those finite bounds.  Promotion only to a
larger scaling study requires all of the following: exact marked specialization and
maximal-order certificates; zero wrong recovered scalars; at least `90%` usable declared
toy instances after frozen applicability rules; no pairing or scalar-indexed table;
upper 95% fitted bounds `zeta+c<=0.35`, `d+h<=0.35`, `m+q<=0.40`,
`m+t+kappa+r<=0.40`, `u<=0.10`, `lambda<=0.45`, and `mu<=0.45`; and agreement with
matched oracle-coordinate instrumentation on every accepted response.

Falsify the scoped hypothesis if no compatible lift exists within the preregistered
family, specialization loses order `N`, all panels are zero or unlabelled, one accepted
scalar is wrong, orientation calls an order-`N` DLP, a pairing is required, or the lower
95% bound of any mandatory complete-cost term reaches `0.50`.  A software failure or
timeout is infrastructure evidence only, not mathematical falsification.

## Artifact plan

- `ideas/artifacts/ECDLP-IDEA-033/quaternion_tomography_preflight.sage`
- `ideas/artifacts/ECDLP-IDEA-033/preflight_spec.yaml`
- `ideas/artifacts/ECDLP-IDEA-033/runs/<run_id>/manifest.yaml`
- `ideas/artifacts/ECDLP-IDEA-033/runs/<run_id>/globalizations.jsonl`
- `ideas/artifacts/ECDLP-IDEA-033/runs/<run_id>/quaternion_orders.jsonl`
- `ideas/artifacts/ECDLP-IDEA-033/runs/<run_id>/responses.jsonl`
- `ideas/artifacts/ECDLP-IDEA-033/runs/<run_id>/costs.tsv`
- `ideas/artifacts/ECDLP-IDEA-033/analysis.md`

## Interpretation boundary

Every claim remains toy, heuristic, model-bound, and novelty-unverified.  Constructing a
marked lift, finding a supersingular auxiliary fiber, computing a maximal quaternion
order, verifying a split module, or recovering a scalar with oracle coordinates is not a
breakthrough.  Only independently replicated end-to-end public recovery below both rho
and BSGS with globalization, orientation, failures, and bit memory charged could justify
further review; no such result is claimed.

## Exactly one next executable action

1. Run a finite blinded Sage preflight over every prime `N<=31` and supported input `p<=251`, enumerating compatible marked lifts of degree at most `8` and height at most `2^16`, supersingular auxiliary fibers of characteristic at most `257`, and certified quaternion panels, then record whether non-oracle responses recover `x` without pairings, scalar tables, or an order-`N` coordinate DLP.
