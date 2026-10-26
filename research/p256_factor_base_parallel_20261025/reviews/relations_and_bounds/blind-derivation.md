# Independent derivation before source/certificate comparison

Task TASK-20261025-6d88b2, 2026-10-25 UTC. Scope: local engineering and mathematical check only. Published P-256 and secp256k1 constants are inherited inputs; no new primality or point-count proof is asserted. No producer code has been imported or executed for these derivations.

Custody deviation: the normal committed-and-pushed-input prerequisite is not met. Inputs are the local sealed payload identified by `../local-custody-exception.json`; this work discharges no official scientific gate and authorizes no disclosure, publication, or state transition. Runtime model binding is unprobed; no model attestation is supplied.

Blindness deviation: this file precedes opening producer source, result.json, verification receipts, matrices, or numerical certificates. However, a heading/statement `rg` and subsequent statement-range reads exposed adjacent report prose: F4 fixture counts, F3 constructed-fixture coefficients, F6 stated exponents/thresholds and bounded-example dimensions, and F8 displayed ranks. The handoff's strict before-reading-producer-numbers condition was therefore not achieved. The derivations below are independently reasoned from the mathematical statements, not claimed fully blind. They will be checked by new executable calculations without producer imports. No other reviewer report has been read.

## F3: useful target coefficient

Work over F_r for prime r, with nonzero G of order r and Q=dG. Independent uniform labels (a_i,b_i) map bijectively to (t_i,b_i)=(a_i+d b_i,b_i). Conditional on the entire point vector (t_i G), the b_i remain independent uniform. For a vector c selected measurably from that point vector and independent auxiliary randomness, fix this conditioning. Provided c is nonzero modulo r, choose j with c_j nonzero; after fixing all other b_i, the map b_j -> sum c_i b_i is bijective. Thus B is uniform and Pr[B=0 | points,c]=1/r. Conditioning further on a point-only acceptance predicate preserves this result. The qualifier is nonzero modulo r, not merely a nonzero integer vector.

A point relation gives A+dB=0. If B is nonzero, d=-A/B is checked by scalar multiplication. If B=0 then A=0; the relation carries no target equation. Labels constructed by taking their own linear dependency force A=B=0. Selection using b_i, adaptive labels depending on earlier secret labels, or a later acceptance rule involving B need a new argument. An adaptive point-only stopping rule may remain valid when all unseen labels are fresh and the final finite selected vector is justified by the same conditioning; the simple fixed-sample proof does not automatically cover arbitrary adaptive code.

Proves-too-much control: choose c=(b_2,-b_1) after seeing b_1,b_2; whenever c is nonzero it forces B=0. This need not itself be a point relation, but shows that linear-uniformity cannot extend to label-dependent vector selection. A known point-relation nullspace of dimension >=2 also permits label-dependent B=0 selection.

## F4: uniform sections and all-rational zeros

For m>=2 on an elliptic curve, dim L(mO)=m and dim L((m-1)O)=m-1 (also m=2 because dim L(O)=1). Exact-pole sections up to nonzero scalar therefore number (p^m-p^(m-1))/(p-1)=p^(m-1). With distinct rational anchors, let V be the evaluation kernel of dimension d. If the top-pole linear functional is nonzero on V, its nonzero fibres contain (p-1)p^(d-1) vectors, hence p^(d-1) projective sections, uniformly sampled by uniform coefficients followed by top-pole rejection. These correspond bijectively to effective divisors in |mO| excluding O and containing the anchors. Duplicate anchors impose only repeated evaluations, not higher vanishing order. Inverse anchors force an inverse pair and may eliminate signed information.

Assume E(F_p) is cyclic of prime order r and 2<=m<r. Affine rational points correspond to F_r excluding 0. Burnside counts unordered degree-m multisets of nonzero scalars summing to zero. A permutation with c cycles of lengths l_j has fixed tuples satisfying sum l_j t_j=0. Since every l_j is invertible modulo r, the count is T_c=((r-1)^c+(r-1)(-1)^c)/r, by additive characters. The permutation cycle polynomial is z(z+1)...(z+m-1). Its value at -1 is zero for m>=2. Therefore N_m=binomial(r+m-2,m)/r. These integer counts correspond to rational principal divisors by the elliptic-curve divisor-class criterion and descent over F_p. Probability under uniform exact-pole sections is N_m/p^(m-1). For m=2 all divisors are inverse pairs and signed rank is zero, despite rationality probability near 1/2.

For an inverse-closed base B, replace N_m by the exact count of such multisets supported in B. For anchors require D>=H, and denominator p^(d-1). No all-rational probability can be substituted for a base-specific, anchored, nonuniform sampling or rank probability.

Signed cancellation: if A has outside-orbit columns represented as a linear map from raw-row combinations, full-base combinations are ker A. An unsigned triangle need not give a kernel: the all-positive triangle incidence has determinant 2, so rank 3 over odd r and no nonzero cancelling combination. If D includes complete raw rows, the rank gained after eliminating outside columns is rank(D)-rank(A), interpreting D as the joint [outside,base] map and excluding zero images correctly. Inverse-pair rows can be identically zero.

## F6: determinant, norm and interval cardinality

Suppose f has individual degrees <=e and leading monomial product x_i^e with coefficient 1. For alpha in {0,...,D}^s set k=min(m,min_i floor(alpha_i/e)); the shifted row p^(m-k)x^(alpha-ke)f^k has leading exponent alpha, remains in the box, and evaluates divisible by p^m at a modular root. With n=(D+1)^s, sum k=K=sum_{j=1}^{min(m,floor(D/e))}(D-ej+1)^s. Scaling monomial columns by B^|alpha| gives determinant p^(mn-K) B^(sDn/2).

At |u_i|<=B, Cauchy-Schwarz gives |h(u)|<=sqrt(n)||h(Bx)||_2. A strict bound below p^m turns divisibility into integer vanishing. Delta=3/4 LLL's first-vector guarantee gives the sufficient integer inequality n^(2n) 2^(n(n-1)) B^(2sDn)<p^(4K). It guarantees a lifted polynomial, not enough independent polynomials or a finite extraction ideal.

For D>=e, K< (D+1)^(s+1)/(e(s+1)), so log_p B<2(D+1)/(esD(s+1)). At the smallest admissible D this ceiling is (e+1)/(e^2 s(s+1))*2, namely 1/4 for (s,e)=(2,2), and 5/96 for (3,4). D<e has K=0, hence no positive B satisfying the strict inequality. Before LLL constants, the large-D exponent tends to 2/(es(s+1)), namely 1/6 or 1/24.

An integer interval c,...,c+B has B+1 elements before reduction and at most B+1 distinct field elements. If M is the number of liftable abscissas, there are at most 2M signed affine points. The number of sums of s points, allowing repetition, is at most binomial(2(B+1)+s-1,s). Uniform nonzero-target half coverage therefore requires twice this count >=r-1. This is a capacity condition only. It cannot establish sufficiency of decomposition or uniformity of target sums. Replacing B+1 by B silently changes the exact finite threshold.

A fixture using offsets x(P)-1,x(Q)-1 fixes a known root (1,1). It tests construction and integer lifting; it cannot demonstrate recovery from independently chosen offsets or unknown roots. Even one short polynomial in two variables can leave a curve of solutions.

## F8: signed automorphism and compression

For secp256k1, beta^3=1, beta!=1 yields psi(x,y)=(beta*x,y), an invertible degree-one projective automorphism preserving O. On the inherited prime-order subgroup, checking psi(G)=[lambda]G proves psi([k]G)=[lambda*k]G for all k, with lambda^2+lambda+1=0. With odd r and lambda of order 3, the six factors +/-lambda^j are distinct, and every nonzero subgroup orbit has six points.

For q chosen orbit representatives define C from full-point coefficients to representative coefficients with one nonzero certified scalar in every row. It has full column rank q. Let S contain the full symmetry constraints, so rowspace(S)=ker(C), with dimension N-q. For any raw relation rows R, quotienting rowspace([S;R]) by ker(C) is isomorphic under multiplication by C to rowspace(RC). Thus rank([S;R])-rank(S)=rank(RC), without a randomness assumption. True homogeneous compressed relations annihilate the nonzero representative-log vector, so rank <=q-1. A falsely asserted rank q must be rejected. Supplying symmetry to only one side of a comparison would invalidate the comparison; the fixed group action itself supplies no new exponent or measured cost advantage.

## Independent checks committed to before comparison

Exhaust abstract small prime groups for F3 and F4; compute the F6 integer bound, capacity thresholds and explicit P-256 f3/f4 algebra independently; check actual P-256 relation/divisor certificates and secp256k1 orbit/matrix certificates without producer imports; include zero-Q, inverse-only, unbalanced-triangle, known-root-offset and false-rank controls. Check retained certificate scope, source assumptions and all observed failures. Any incomplete factorization, lattice transform or certificate coverage will be named.
