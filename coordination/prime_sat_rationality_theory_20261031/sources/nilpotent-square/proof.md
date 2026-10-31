# Uniform nilpotent square witness

2026-10-31. Root derivation, unreviewed; no implementation or trials. Scope assigned in scope.json before writing. This supplies a complete rationality-block alternative, including B=0, without changing the frozen chart implementation.

Let p>3 be prime, let f=X^3+aX+b define the nonsingular curve, and let U be a monic degree-k polynomial, k>=1, known to split over F_p. Write U=product_i (X-alpha_i)^m_i with distinct alpha_i in F_p and positive integer multiplicities. Let r be the number of distinct roots. All splitting/interval and chart-norm constraints remain mandatory.

Claim: f(alpha_i) is square-or-zero for every i if and only if there exists C in F_p[X], degree C<k, satisfying

    (C^2-f)^k = 0 in F_p[X]/(U).

Forward: choose beta_i in F_p with beta_i^2=f(alpha_i). By interpolation/Chinese remainder on the distinct linear factors, choose C of degree<r with C(alpha_i)=beta_i, hence degree<k. Every X-alpha_i divides C^2-f. Raising to k gives multiplicity at least k at each root, so U divides the power because m_i<=k. Backward: evaluate the displayed identity at each alpha_i to get (C(alpha_i)^2-f(alpha_i))^k=0 in a field, hence C(alpha_i)^2=f(alpha_i). This proof also applies when k>=p; it divides by no multiplicity or factorial. U=1 is a separate empty case with no C variables or condition.

The weaker-looking nilpotent equation is essential: requiring C^2=f modulo U can reject valid repeated branch roots. Symbolic counterexample: take nonsingular f=X^3+X over any prime p>3 and U=X^2. The support is the rational point (0,0), but C=c0+c1X with C^2=f mod X^2 would force c0=0 from the constant coefficient and then 0=1 from the linear coefficient. The nilpotent equation instead accepts C=0 because f^2 is divisible by X^2. This is an algebraic counterexample, not an executed experiment.

## Exact fibers and cost boundary

Suppose all roots pass and q of the r values f(alpha_i) are nonzero squares. The evaluation map from the k-dimensional coefficient space of C to F_p^r is surjective, with kernel dimension k-r. There are 2^q choices of root values, each with p^(k-r) preimages. Thus the auxiliary fiber has EXACTLY 2^q*p^(k-r) elements. Any nonsquare value gives no witness. In particular repeated roots create potentially large irrelevant coefficient freedom. The checker may evaluate C at recovered roots and discard this freedom, but a solver must project it away rather than enumerate it as separate output.

For a supplied C, compute C^2-f in the quotient and its kth power by a fixed addition chain or binary powering. The quotient dimension is k and the exponent depends on k, not on p. This replaces the Euler rationality test using f(f^((p-1)/2)-1), conditionally on the same split U. It introduces k unknown field coefficients. An arithmetic circuit for quotient multiplication can be lifted into quadratic equations with explicit intermediates; variable-U reduction must also be lifted and counted, not treated as a constant multiplication table. No equation-count or solver-speed improvement is asserted for the complete encoding.

All field variables still range over F_p. Pure algebraic solving without field/range equations can admit extension-field witnesses and is not equivalent to the prime-field predicate. Bit widths, carry equations, range checking, and proof verification retain dependence on log p. Removing a p-dependent exponent from this one field-arithmetic block is not removing p-dependence from the solver.

## Integration with signed recovery and linear-B guards

After verified factor recovery, evaluate C(alpha_i), square-check it, and use that value as a root lift in balanced signed recovery. Its sign does not matter when both signs have equal multiplicity. In unbalanced cases retain the exact residual ratio and local orders. A finite target outside U already has a known rational ordinate and remains explicitly present in norm support and target subtraction. No generic square-root algorithm is required for checking a supplied C. Finding C remains part of search.

This gives three complete candidate rationality designs: full Euler on U; nilpotent square witness on U; and the disjoint B-stratified encoding with a conditional-square guard for nonconstant linear B, no additional rationality test for nonzero constant B, and the full Euler or nilpotent witness for B=0. Every arm retains the identical chart shapes, norm equations, interval witnesses and canonical projected signed outputs. The stratified design must not select only the generic chart.

The next fixed implementation contract should include the symbolic repeated-branch counterexample above, a nonsquare support rejection, a simple square support, a repeated nonbranch square, k>=p, empty U, and a target outside the interval. Fixtures must be frozen before execution. A scientific comparison must charge all candidate construction, auxiliary projection, reconstruction and certificate checking; fixed software checks are not performance evidence. Neither bounded generator degree nor a short exponent establishes degree of regularity.

## Sources and status

Prior internal inputs read: ../shared-chart-signed-recovery/proof.md and ../shared-chart-conditional-square/proof.md (both unreviewed). Primary source read by root 2026-10-31: Stacks Project Lemma10.15.4, tag00DT, https://stacks.math.columbia.edu/tag/00DT, for the standard Chinese remainder decomposition. It supports interpolation/surjectivity, not novelty or an empirical solver claim. No exhaustive literature novelty search was performed; no novelty claim is made. The exact equivalence and fiber count here are elementary derivations awaiting independent review. No canonical research graph or accepted status is changed.
