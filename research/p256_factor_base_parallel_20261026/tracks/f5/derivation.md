# F5 exact transported-base equivalence

Prospective derivation, 26 October 2026; no second-pass observation data.
Inputs are the certified P-256 curve and four serialized rational maps in the
prior study. No new claim about discovery or solving cost is made.

Let `phi:E -> E'` be one of the degree-ell maps, with `ell` equal to 3, 5 or
11. The prior function-field certificates establish
`dual(phi) phi=[ell]` and `phi dual(phi)=[ell]`. The published rational source
group has prime order `r`, coprime to ell. Isogeny over Fp preserves the point
count, so the endpoint rational group also has order r. Consequently

    tau = [ell^-1 mod r] dual(phi)

is an inverse on these rational groups. This is finite subgroup normalization;
it does not assert that the dual has differential scale one.

Fix signed labels `P_i`, and transport each label to `phi(P_i)` without
resampling or sorting endpoint labels. For every target Q and every multiset
of three labels,

    P_i + P_j + P_k = Q
      iff phi(P_i) + phi(P_j) + phi(P_k) = phi(Q).

The forward direction is homomorphism; the reverse follows by tau. Exact
membership is likewise equivalent under tau. Because phi commutes with
negation and is injective on E(Fp), distinct canonical x-coordinate pairs
remain distinct canonical pairs. The endpoint x-membership polynomial has
one factor for each transported canonical x value, and matches point
membership once rationality and the endpoint equation are checked.

For a normalized odd-degree map with squarefree kernel polynomial h, the
reduced x denominator is h^2 and the y multiplier denominator is h^3. Their
numerators are coprime to h. Checking these exact polynomial identities
certifies genuine geometric poles; it does not manufacture rational
nonidentity kernel points in a prime-order rational group. The new panel
retains this algebraic certificate instead of claiming an extension-field
kernel-point enumeration.

The reference enumerates all signed multisets on the fixed source domain.
The candidate recovers endpoint triples by a separate Jacobian-coordinate
pair lookup, preserving the same labels. These are two actual computations
inside one guarded process with shared setup; no ratio of their work is a
performance comparison. The coordinate-scaling control repeats the same
relation set on an isomorphic model.

Global map/order premises inherit the prior certificates. New bounded checks
can refute an implementation error but cannot prove the universal identities
anew, supply natural large-base yield, or resolve the complete-cost solver
obligation.
