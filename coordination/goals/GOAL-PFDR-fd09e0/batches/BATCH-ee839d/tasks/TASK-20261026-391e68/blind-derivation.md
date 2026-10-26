# Blind derivation: normalization, domain, and order

Task: `TASK-20261026-391e68`  
Owned joint: `normalization-domain-order`  
Blind phase: this derivation was completed before reading the producer manifest, producer compatibility map, owner implementation, `native-backend-contract.md`, prior design/bound artifacts, or any sibling report.

## Independent affine object

Use the deviation order

\[
(z_1,z_2,z_3,z_4,h_1,h_2).
\]

With \(a=2,b=3\), write

\[
S(A,B,C)=(A-B)^2C^2-2(A^2B+AB^2+2A+2B+6)C
          +A^2B^2-4AB+4-12A-12B.
\]

Direct substitution into the three tree relations gives the following exact integer polynomials. Grouping by the internal deviation makes every support coefficient visible:

\[
\begin{aligned}
f_L={}&S(11+z_1,13+z_2,23+h_1)\\
={}&h_1^2(z_1^2-2z_1z_2+z_2^2-4z_1+4z_2+4)\\
&+h_1(-2z_1^2z_2-2z_1z_2^2+20z_1^2+24z_2^2-188z_1z_2\\
&\qquad -1098z_1-634z_2-6788)\\
&+z_1^2z_2^2-20z_1^2z_2-24z_1z_2^2+100z_1^2+144z_2^2\\
&\qquad -2698z_1z_2-19484z_1-13608z_2-138647,
\end{aligned}
\]

\[
\begin{aligned}
f_R={}&S(17+z_3,19+z_4,29+h_2)\\
={}&h_2^2(z_3^2-2z_3z_4+z_4^2-4z_3+4z_4+4)\\
&+h_2(-2z_3^2z_4-2z_3z_4^2+20z_3^2+24z_4^2-260z_3z_4\\
&\qquad -2250z_3-1642z_4-23180)\\
&+z_3^2z_4^2-20z_3^2z_4-24z_3z_4^2+100z_3^2+144z_4^2\\
&\qquad -4570z_3z_4-49700z_3-40080z_4-572975,
\end{aligned}
\]

and

\[
\begin{aligned}
f_T={}&S(23+h_1,29+h_2,5)\\
={}&h_1^2h_2^2+48h_1^2h_2+36h_1h_2^2+576h_1^2+324h_2^2\\
&+1574h_1h_2+16488h_1+12228h_2+94561.
\end{aligned}
\]

Every displayed coefficient is nonzero. Consequently the exact local support of either child relation is

\[
E_{\rm child}=\{(i,j,k)\in\mathbb Z_{\ge0}^3:
0\le i,j,k\le2,\ i+j+k\le4\},
\]

with 23 exponent vectors. Its slices have 9 points for \(k=0\), 8 for \(k=1\), and 6 for \(k=2\). The target support is

\[
E_{\rm target}=\{(i,j):0\le i,j\le2\},
\]

with 9 exponent vectors.

Embed these into the six deviation coordinates as

\[
\begin{aligned}
E_L&=\{(i,j,0,0,k,0):(i,j,k)\in E_{\rm child}\},\\
E_R&=\{(0,0,i,j,0,k):(i,j,k)\in E_{\rm child}\},\\
E_T&=\{(0,0,0,0,i,j):(i,j)\in E_{\rm target}\},\\
E&=E_L\cup E_R\cup E_T.
\end{aligned}
\]

## Finite monomial domain

For precomputation multiplicity \(\mu\in\{1,2\}\), the statement determines

\[
P_\mu=\operatorname{conv}(\{0\}\cup\{\mu e:e\in E\})
     =\mu\operatorname{conv}(\{0\}\cup E),
\qquad
D_\mu=P_\mu\cap\mathbb Z_{\ge0}^6.
\]

This is a finite six-coordinate domain. It is not merely the union of the three relation supports, a bounding box, or a Cartesian product. The dilation occurs before taking integral points. In particular, \(D_2=(2P_1)\cap\mathbb Z^6\); replacing it by \(D_1+D_1\), or by supports of pairwise products, requires a separate integer-decomposition/normality proof and is not licensed by convexity alone. Ryan's Newton-polytope statement proves that the Newton polytope of a product is the Minkowski sum, while `get_monomials_from_vertices` explicitly returns every integral point of the supplied convex hull. Those are distinct finite constructions unless the needed lattice-polytope property is established.

The formal-modulus ring has seven coordinates in this exact order:

\[
(N,z_1,z_2,z_3,z_4,h_1,h_2).
\]

The domain-to-ring map must therefore prepend the modulus exponent:

\[
(e_1,\ldots,e_6)\longmapsto
(0,e_1,\ldots,e_6)\longmapsto
N^0z_1^{e_1}z_2^{e_2}z_3^{e_3}z_4^{e_4}h_1^{e_5}h_2^{e_6}.
\]

Passing a six-tuple directly to code that zips exponents with the seven ring generators loses/misaligns a coordinate: it assigns the first exponent to \(N\) and omits \(h_2\). This is the concrete lost-leading-modulus-coordinate attack.

## Weighted order and cell dependence

The raw bound-guess ray in cell \((r,\mu)\) is

\[
\beta_r=(1,1,1,1,r,r)/20.
\]

Ryan's source constructs the formal ring with `TermOrder("wdeglex", ...)`, variables `(N,*xs)`, modulus weight \(1/\texttt{divisor_bound}\), and a scale of 1000. Since the divisor bound is 1, the exact integer weight vectors are

\[
\begin{array}{c|c|c}
r & (N,z_1,z_2,z_3,z_4,h_1,h_2)\text{ weights} & \text{primitive equivalent}\\
\hline
2&(1000,50,50,50,50,100,100)&(20,1,1,1,1,2,2)\\
4&(1000,50,50,50,50,200,200)&(20,1,1,1,1,4,4).
\end{array}
\]

The effective finite-domain order is ascending Sage weighted-degree-lexicographic order on the monomials after the six-to-seven-coordinate map; ties use the lexicographic part of that same ring order. The domain \(D_\mu\) depends on \(\mu\), not on \(r\); \(r\) changes the weighted order and leading terms, not membership in the convex integral domain.

The formal \(N\) coordinate is not disposable just because every input-domain monomial has exponent zero in \(N\). Ryan's `lm_no_N` removes \(N\) only when comparing the unknown-variable leading monomial, while `lc_no_N` retains the corresponding \(N\)-power in the leading coefficient. Thus determinant/modulus scaling needs the seven-coordinate leading term split `(unknown monomial, N-valued leading coefficient)`.

## Multiplicity normalization

The precomputation ideal at multiplicity \(\mu\) has shared root modulo \(p^\mu\). Ryan's `get_delta_star` therefore divides every symbolic bound exponent by \(\mu\), and also divides the formal-modulus contribution by \(\mu\):

\[
\log_{p^\mu}X_i=\beta_{r,i}/\mu,
\qquad
\log_{p^\mu}N=(1/\texttt{divisor_bound})/\mu=1/\mu.
\]

This normalization is separate from both (a) the raw weights used to choose the precomputation term order and (b) the dilation \(P_\mu=\mu P_1\). Dividing the domain exponents by \(\mu\), failing to divide the bound/modulus ray by \(\mu\), or dividing twice are three different errors.

## Constant-pivot and coefficient-domain obligation

Ryan's symbolic construction works in \(K_c[N,x]\), where \(K_c=\operatorname{Frac}(\mathbb Q[c])\), and specialization replaces coefficient denominators by inverses modulo \(N^\mu\) only when they are coprime to \(N\). For this numeric affine instance, constant pivots are units in \(\mathbb Q\). A native outside-domain elimination must therefore state and preserve its coefficient domain: division by constant pivots may occur in the base fraction field, but treating a nonconstant polynomial in the formal modulus \(N\) as an arbitrary unit by silently passing to \(K_c(N)\) changes the module and the modulus valuation. Conversely, exact elimination over \(K_c[N]\) must recover the same rows whose outside-domain coefficients vanish. This remains an implementation comparison obligation after the seal.

## Source-derived obligations for comparison

The post-seal implementation comparison must check all of the following without making a bound call:

1. the three expanded integer relations and exact nonzero supports above;
2. six deviation coordinates and the explicit zero-prepend into the seven-coordinate formal ring;
3. \(D_\mu=(\mu\operatorname{conv}(\{0\}\cup E))\cap\mathbb Z_{\ge0}^6\), without an unproved Minkowski/integer-domain substitution;
4. cell-specific `wdeglex` weights and deterministic tie order;
5. retention of the formal \(N\)-power as the leading coefficient when the unknown-variable monomial is compared;
6. one, and only one, division by \(\mu\) in the bound and modulus ray used by the asymptotic expression;
7. constant-pivot elimination in a declared coefficient domain that does not make the formal modulus an unintended unit.

No claim about numerical reach, root extraction, reduction output, relation recovery, an index-calculus improvement, or global optimality follows from this derivation.

## Pre-seal source record

- Keegan Ryan, *Solving Multivariate Coppersmith Problems with Known Moduli*, Cryptology ePrint 2024/1577, full 52-page version retrieved from the Internet Archive capture of the primary IACR PDF (`20250716082047`), PDF SHA-256 `15dd6ae6b939c51f3bc124097f954bd858ef47e4739037381fb4951f0366043f`; full text read, including Sections 3, 4, 6, Algorithm 3, Lemmas 6--7, and Appendix C.
- Keegan Ryan, `keeganryan/cuso`, commit `fb2747d2105a8e48499bf10a3a717cf80c14d079`; relevant source read: `README.md`, `src/cuso/symbolic/{asymptotic,convert,ideal,limit,optimal,polynomial,polytope,problem,shift_set_properties,utils}.py`, and `src/cuso/strategy/problem_converter/monom_ordering.py`.
- Governing repository sources read before derivation: `AGENTS.md`; `docs/agent-contract-extended.md` (literature-first, observation-first, review-architecture, and retrieval sections); `docs/agent-contract-supplement.md` (name-the-obstruction); `docs/lab-contract.md`; `agents/validator.md`; `templates/research-records.md` (review attestation); `orchestration/{roles,model-policies,model-bindings}.yaml`; the frozen handoff; `blind-statement.md`; and the assignment metadata in `review-plan.json`.

