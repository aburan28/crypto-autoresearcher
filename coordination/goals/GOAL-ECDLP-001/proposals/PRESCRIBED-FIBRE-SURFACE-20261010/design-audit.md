# Prescribed-fibre high-rank surface audit

## Audit basis

- Idea: `IDEA-20261009-b01e42`.
- Goal: `GOAL-ECDLP-001`.
- Status: `proposed`; `approved_by: null`.
- Audit role: Coordinator design review only. No experiment was run and no
  status was changed.
- Nearby records: `KN-FIND-004`, `KN-FIND-6b3e17`, the XEDN surface lane, and
  `KN-TECH-06bb4e` face F5.

## Scientific boundary

The proposal asks a meaningful realization question: can a high-rank surface
be made to specialize to a prescribed ordinary curve over `F_p`? That question
must be kept separate from the later section-finding and ECDLP-cost questions.
The current filing mixes a rank census, a fibre-j density assertion, and a
twist construction whose stated specialization operation is not valid at the
prescribed fibre.

## Load-bearing mathematical and protocol repairs

1. Define the surface family and target fibre exactly: an integral minimal
   Weierstrass model over `F_p(t)`, `t_0`, discriminant and bad-fibre list,
   the coefficient-degree/height convention for `chi`, and an explicit
   `F_p`-isomorphism (not merely an algebraic-closure isomorphism) to the
   target curve. Record the twist class and ordinary/nonsingular certificate.
2. Repair the proposed twist arm. A quadratic twist by a factor vanishing at
   `t_0`, such as `(t-t_0)g(t)`, generally creates bad reduction at `t_0`; it
   does not preserve an ordinary prescribed fibre. To change a fibre twist
   class, the twisting factor must be nonzero at `t_0` and its residue must be
   chosen with the required square class. The modified discriminant and
   minimal model must then be rechecked, including the effect on rank and
   conductor.
3. Do not infer rank from ten point counts without a degree-appropriate
   certificate. For `chi <= 3`, the relevant surface cohomology polynomial can
   have degree larger than the proposed `k <= 10` count panel. Specify the
   complete zeta/L-polynomial reconstruction, precision and factor test, or
   provide an independent Shioda-Tate/section basis and an upper-bound proof.
   Separate rank over `F_p(t)` from rank after algebraic closure and label
   searched sections, lower bounds, and certified ranks distinctly.
4. Define the random constrained-surface distribution. “Random `A,B` of
   degree at most ... constrained through `E`” needs coefficient sampling,
   admissibility rejection, model normalization, discriminant conditioning,
   and a proof that every accepted cell has the same fibre object. A sample of
   1,000 surfaces cannot support a universal `>0.99` probability without a
   predeclared finite-population/statistical scope.
5. Remove or prove the claimed `j`-density bound. The statement that
   `F_p`-rational fibres on high-rank surfaces have j-density at most
   `12 chi/p` is not implied by the Shioda-Tate bound and needs a precisely
   defined family, map degree, image set, and target measure. A nonconstant
   j-map can have an image of order `p` over `F_p`; high rank alone does not
   yield the stated `O(1/p)` density. The matching target/twist claim must be
   measured against a specified target distribution.
6. Keep controls on the same field and rank notion. Supersingular controls
   whose high rank appears only after extending the constant field, and
   constant-j surfaces, are useful boundary controls but cannot be compared
   as if they were generic ordinary `F_p(t)` surfaces. Report both ranks and
   the exact fibre twist in every control.
7. Bind the realization output to the next section experiment only through a
   committed certificate: surface identity, fibre map, rank certificate,
   generator/section data, and specialization replay. A high rank alone does
   not show that sections produce usable factor-base relations or target
   solves.

## Claim ceiling and disposition

A valid finite study could report rank and fibre-realization statistics for a
declared surface family and target panel. It would not establish an
unbounded-rank family through arbitrary ordinary fibres, a `j`-density law,
or an ECDLP improvement. Any positive construction remains a realization
result until section costs, relation novelty, and target replay are separately
demonstrated.

Disposition: **retain proposed as a conditional realization study; do not
approve or dispatch as filed.** Repair the twist specialization, rank
certificate, random-family measure, fibre-density claim, and cross-lane
certificate. Recheck readiness and approval capacity only after the exact
surface inputs and executable rank protocol are committed.
