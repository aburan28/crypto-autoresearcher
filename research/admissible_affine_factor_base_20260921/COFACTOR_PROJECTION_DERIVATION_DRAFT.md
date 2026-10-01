# Sparse cofactor projection — unreviewed derivation for a future protocol

This is a prospective mathematical design note. It is not a validated theorem record, an experiment approval, or an amendment to the N19 search. No group or SAT experiment is reported here. The exact integer-ring identities come from the preserved earlier `research/golden_factor_base_sat_20260921/COFACTOR_PROJECTION_LEAD.md`.

Let E=K0(F2^53), let tau denote coordinate Frobenius, and assume the already declared public fixture order #E=428*r with prime r=21044858204113. In Z[tau]/(tau^2+tau+2), the earlier note gives

    psi = 1 - tau - tau^6 + tau^8 = -15 + 7*tau,
    eta = 1935145 - 2496832*tau,
    psi*eta = tau^53 - 1,
    psi*bar(psi) = 428,
    eta*bar(eta) = r,
    gcd(428,r) = 1.

Conjugation sends tau to -1-tau, so bar(psi)=-22-7*tau. The characteristic identity tau^2+2=mu*tau for Koblitz curves, with mu=-1 for K0, is explicitly stated in Avanzi–Heuberger–Prodinger, section2, equation3. Source provenance: retrieved and opened https://www.finanz.math.tugraz.at/~prodinger/tauext.pdf . This reference supports the characteristic identity and the use of Frobenius expansions; it does not validate the new parameter-specific reasoning below.

An elementary finite-group argument avoids needing a separate geometric separability assertion. On every rational point P in E, (tau^53-1)P=O. Hence

    [r] psi(P) = bar(eta) eta psi(P)
                 = bar(eta) (tau^53-1)P = O.

Thus psi(E) lies in the r-torsion subgroup H of the finite abelian group E. Since #E=428*r and gcd(428,r)=1, H has order r. For any Q in H, choose the public inverse e=428^(-1) modulo r and set P=[e]bar(psi)(Q). Then

    psi(P) = [e]psi*bar(psi)(Q) = [e*428]Q = Q.

Therefore psi(E)=H, and its kernel inside the rational point group has428 elements. These conclusions are conditional on the displayed ring identities, the curve-order/prime-order fixture, and the faithful interpretation as curve endomorphisms; they still require independent review before scientific promotion.

This supplies a candidate encoding strategy. Let S be raw curve points whose x-coordinates have simple affine or subspace membership. Define the factor base B=psi(S). A decomposition of a public synthetic target Q over B is equivalent to finding P_i in S with psi(sum_i P_i)=Q. One may encode the sparse endomorphism on the sum, or construct a rational preimage and account explicitly for all relevant kernel translates. This retains the simple raw membership condition while moving subgroup admission into the image map.

There is an essential equivalence control: [428]=bar(psi)*psi. On H, bar(psi) is invertible. Consequently the usual cofactor-cleared base [428]S is exactly bar(psi)(B). The two bases differ by an automorphism of H and have identical global sumset cardinalities at every decomposition length, after transforming targets. Sparse projection alone cannot improve their uniform target coverage or the generic exponent. A possible benefit is the size and propagation of the concrete encoding, or evaluation cost; it must be compared against this transformed same-problem control.

The sparse expression has four signed Frobenius terms and can be evaluated with three group additions/subtractions plus the required coordinate squarings, before exceptional-case costs. This is an operation-count description, not a measured speedup. Repeated or cancelling terms, kernel collisions, image duplicates, infinity, point lifting, validation and any preimage/kernel enumeration must be charged. Adding a kernel selector can make solving harder even when base membership is simpler.

A discriminating future test should first replay the identities on a fixed public synthetic point panel with an independently written group kernel, then compare the exact same target problem expressed using psi and ordinary cofactor clearing. Hold raw S and target correspondence fixed, count distinct projected points and support exactly at a small scale, and reject a coverage advantage if it survives despite the automorphism equivalence. Only then compare complete SAT construction/search/replay costs. No such test has been run or approved by this note.

Proof-search-map draft: baseline is ordinary cofactor clearing under the stated automorphism; observation collision is falsely attributing a coverage change to isomorphic images; quantifiers are a fixed curve, fixed raw set and all public target correspondences; the ceiling is a representation/evaluation improvement, with no automatic solver, relation-yield or IC asymptotic gain. The cheapest falsifier is a ring/group identity discrepancy or a solver advantage that disappears after charging target transformation and kernel branches. Novelty remains unverified.
