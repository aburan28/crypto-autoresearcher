# Independent joint algebra and quantifier derivation

TASK-20261030-0cd7c6 · 2026-10-30 · session `joint-blind-validation-20261030`

This is a manual derivation from the original public object, primary paper, pinned source, and expressly allowed older history. No new producer, snapshot receipt, or current sibling report was read. Statements below are my own scoped mathematical arguments, not a vote on an unavailable producer result. No algebra system, scientific computation, bound search, reduction, or extraction was used.

## 1. Object and coefficient rings

Let (A_0=\mathbb Z[a,b,q,c_1,c_2,c_3,c_4,d_1,d_2]), (K=\operatorname{Frac}(A_0)=\mathbb Q(c)), and (x=(z_1,z_2,z_3,z_4,h_1,h_2)). Define exactly

\[
S(A,B,C)=(A-B)^2C^2-2((A+B)(AB+a)+2b)C+(AB-a)^2-4b(A+B),
\]
\[
F_1=S(c_1+z_1,c_2+z_2,d_1+h_1),\quad
F_2=S(c_3+z_3,c_4+z_4,d_2+h_2),\quad
F_3=S(d_1+h_1,d_2+h_2,q).
\]

Set (I=(F_1,F_2,F_3)\subset K[x]), (R=K[N,x]), and (J=(N)+IR). The formal variable (N) is not a coefficient-field unit. In particular, passing from (K[N]) to (K(N)) would make (J=R) and erase the modular information. Here (J_\mu=J^\mu) and (J_\infty=0).

The common-root premise is an integer specialization (c\mapsto c_0), (N\mapsto n\ne0), a prime (p\mid n), and (r\in\mathbb Z^6) such that every (F_i(c_0,r)\equiv0\pmod p). The bounds remain (B=(X,X,X,X,Y,Y)); no equality (X=Y) is assumed. This premise establishes only modular polynomial relations. It does not supply finite-field y-lifts, compatible signs, subgroup membership, or a decomposition oracle.

## 2. Finite row membership and divisibility: proved conditional interface

Fix an integer (\mu\ge1) and a finite collection of symbolic rows (g_j\in K[N,x]). A sufficient *soundness* witness for each row is

\[
g_j=\sum_{e_0+e_1+e_2+e_3=\mu}
 A_{j,e}(c,N,x)N^{e_0}F_1^{e_1}F_2^{e_2}F_3^{e_3},
\qquad A_{j,e}\in K[N,x]. \tag{1}
\]

Choose a nonzero polynomial (D_j(c)\in A_0) clearing the denominators of both the row and *all its membership witnesses*. Multiplying (1) gives an identity in (A_0[N,x]):

\[
h_j:=D_jg_j=\sum_e W_{j,e}N^{e_0}F_1^{e_1}F_2^{e_2}F_3^{e_3},\quad W_{j,e}\in A_0[N,x]. \tag{2}
\]

For any common-root specialization above, every summand of (2) evaluates to a multiple of (p^\mu). Hence (p^\mu\mid h_j(c_0,n,r)). This conclusion uses no unit hypothesis, no regular-sequence claim, no independence of the three relations, and no numerical test. It remains valid when (D_j(c_0)=0), although then the rational row (g_j) need not be defined and (h_j) may degenerate. Clearing only displayed row coefficients, without clearing witness denominators, does not establish (2).

There are two distinct implementations of this interface:

* **Integer clearing:** retain (h_j\in\mathbb Z[x]) and its actual integer heights. Its divisibility follows directly from (2).
* **Modular inversion:** require (\gcd(D_j(c_0),n)=1), choose an integer (u_jD_j(c_0)\equiv1\pmod {n^\mu}), and retain a declared coefficient lift \(\widetilde g_j\equiv u_jh_j\pmod {n^\mu}\). Then \(\widetilde g_j-u_jh_j=n^\mu t_j\) for an integer polynomial (t_j). Both terms on the right belong to \((n,F_1(c_0),F_2(c_0),F_3(c_0))^\mu\), so \(\widetilde g_j\) belongs to that integer ideal and vanishes modulo (p^\mu) at (r). Unit status merely modulo (p) suffices for a purely (p)-local proof, but Ryan's inversion modulo (n^\mu) requires coprimality with (n).

Products of (k) certified base rows have modulus (p^{\mu k}). Multiplication by an (x)-monomial preserves that divisibility. With (J_\infty=0), no extra exact integer relation is available for free. Three input polynomials do not change the guaranteed modulus to (p^{3\mu}): the guarantee is indexed by total ideal-power degree (e_0+e_1+e_2+e_3=\mu), once, not once per label.

Equation (1) certifies membership of the retained rows. It does not certify that the rows generate the full support-restricted module or form an independent suitable lattice basis.

## 3. Exact formal-N joint module identity: independently proved

For a fixed finite monomial set (M\subset\mathbb Z_{\ge0}^6), write (d=|M|), (V_K=\operatorname{span}_K\{x^\alpha:\alpha\in M\}),

\[
T_s=I^s\cap V_K\quad(0\le s\le\mu),\qquad T_0=V_K,
\]
\[
\mathcal V=K[N]\otimes_KV_K,\qquad
\mathcal L_\mu=J^\mu\cap\mathcal V.
\]

All (F_i) are independent of (N). Therefore

\[
J^\mu=\sum_{s=0}^{\mu}N^{\mu-s}I^sK[N,x]. \tag{3}
\]

If (f=\sum_{e\ge0}N^ef_e(x)), its membership in (3) is equivalent to (f_e\in I^{\mu-e}) for (e<\mu), with no restriction for (e\ge\mu). One direction follows by collecting coefficients; the coefficient ideal is \(\sum_{s\ge\mu-e}I^s=I^{\mu-e}\). Conversely those coefficients explicitly express (f) using the corresponding summands of (3). Imposing support in (M) gives the exact (K)-vector-space decomposition

\[
\mathcal L_\mu/N^\mu\mathcal V
\simeq\bigoplus_{e=0}^{\mu-1}N^eT_{\mu-e}. \tag{4}
\]

Consequently, with (d_s=\dim_KT_s),

\[
E_{\rm formal}(\mu,M)=\dim_K(\mathcal L_\mu/N^\mu\mathcal V)
=\sum_{s=1}^{\mu}d_s. \tag{5}
\]

The full-rank (K[N])-module \(\mathcal L_\mu\) contains (N^\mu\mathcal V). Over the PID (K[N]), its invariant factors have the form (N^{a_j}), (0\le a_j\le\mu). Thus its determinant has (N)-valuation

\[
q_{\rm formal}=\sum_j a_j=\mu d-E_{\rm formal}. \tag{6}
\]

Also \((J^\mu:N^i)=J^{\max(\mu-i,0)}\), directly from the same coefficient calculation. These exact formal identities require neither a regular sequence of (F_1,F_2,F_3) nor disjoint variables. They use the independence of (N) as a polynomial variable. They are not automatically identities for integer specialization (N=p).

Crucially, (T_s) is the space for the *whole* joint ideal power. Although (I^s\) is generated by the mixed products (F_1^{a}F_2^{b}F_3^{c}), (a+b+c=s), the dimension of its intersection with (V_K) is not the number of those products or the sum of dimensions of three principal spaces. Syzygies, overlaps, and cancellations across supports occur inside this intersection. The shared (h_1,h_2) prevent any unproved tensor-product decomposition.

## 4. Exact finite (p)-adic formulation, and sufficient transfer hypotheses

First take (n=p). Let (B=\mathbb Z_{(p)}[x]), (I_p=(F_i(c_0,x))\subset B), (J_p=(p)+I_p), (V=\operatorname{span}_{\mathbb Z_{(p)}}M), and (L=J_p^\mu\cap V\). Then (p^\mu V\subset L\subset V\). Define, for (0\le i<\mu),

\[
W_i=\{\overline{p^{-i}f}:f\in L\cap p^iV\}\subset V/pV.
\]

Equivalently (W_i) is the reduction of \((J_p^\mu:p^i)\cap V\). The exact, unconditional finite-index identity is

\[
E_p:=\operatorname{length}_{\mathbb Z_{(p)}}(L/p^\mu V)
=\sum_{i=0}^{\mu-1}\dim_{\mathbb F_p}W_i,
\quad q_p=\mu d-E_p. \tag{7}
\]

Proof: diagonalize the finite-index submodule over the DVR \(\mathbb Z_{(p)}\) with invariant exponents (a_j\in[0,\mu]\). Layer (W_i) has one direction for each (a_j\le i). Summing counts direction (j) exactly \(\mu-a_j\) times. This is a mathematical proof, not an executed Smith/rank algorithm.

Replacing (W_i) by \(\bar I_p^{\mu-i}\cap\bar V\) needs more than (3). The following explicit sufficient conditions establish that replacement:

1. Every (B/I_p^s\), (1\le s\le\mu), is (p)-torsion-free; equivalently (I_p^s:p=I_p^s\).
2. For every such (s), reduction of the finite-support intersection is surjective onto the specialized intersection:
   \[
   \overline{I_p^s\cap V}=\bar I_p^s\cap\bar V. \tag{8}
   \]
3. To equate the finite dimensions with (d_s), those intersections have the generic dimensions (d_s\) after reduction. This is a rank condition in addition to unit denominators.

For condition 1, if (ph\in J_p^s\), write (ph=a_s+ph_1\), (a_s\in I_p^s\), (h_1\in J_p^{s-1}\). Saturation yields (h-h_1\in I_p^s\), hence \((J_p^s:p)=J_p^{s-1}\). Iterate for (i) steps. Any reduction of (J_p^s\cap V\) lies in \(\bar I_p^s\cap\bar V\). Conversely (8) lifts any element of that intersection into (I_p^s\cap V\subset J_p^s\cap V\). It follows that

\[
E_p=\sum_{s=1}^{\mu}\dim_{\mathbb F_p}(\bar I_p^s\cap\bar V)
=\sum_{s=1}^{\mu}d_s \tag{9}
\]

under conditions 1–3. These are sufficient, not claimed necessary. No particular joint object's (d_s\), minors, or ideal witnesses have been computed here.

If (n=up\) with (p\nmid u\), its localized ideal agrees with (J_p\), so the local statement still applies. The real determinant of an integer row lattice can also contain factors from other primes or prime-to-(p) row indices. Those factors cannot be dropped. For arbitrary (p\mid n\), \((n,F_i)^\mu\subset(p,F_i)^\mu\), so (7) for the latter is at most an enlarged-module bound; exact equality for the actual rows requires a separate spanning/index certificate. Higher (v_p(n)) must be retained if a stronger modulus valuation is claimed.

## 5. A finite good-specialization certificate exists; its size is not uniform here

Here is a self-contained sufficient construction establishing the quantifier order, without computing it. For **each fixed** \((\mu,M)\), there exists a nonzero \(\Delta_{\mu,M}(c)\in A_0\) so that conditions 1–3 hold for every integer (c_0\) and prime (p\) with \(p\nmid\Delta_{\mu,M}(c_0)\).

For each (1\le s\le\mu\), choose a finite monic Gröbner basis (G_s\) of (I^s\subset K[x]\). Retain representations of its members in the mixed-product generators, representations of those generators in (G_s\), and terminating Buchberger reduction identities. Clear the finitely many coefficient denominators by localizing \(A_0\) at a product \(\Delta\). Since all leading coefficients are 1 and all identities hold over this localization, every permitted specialization has the same monic leading monomials and a monic basis for its specialized (I_p^s\). Standard monomials are a free basis of the quotient over \(\mathbb Z_{(p)}\); equivalently normal form shows (p\operatorname{NF}(h)=0\) implies \(\operatorname{NF}(h)=0\). This proves condition 1. This argument uses finite field-polynomial basis existence and the displayed identities, not an assumption that these joint generators form a regular sequence.

To prove (8), reduce the finitely many monomials of (M\) by (G_s\). Let (C_s\) be the finite matrix of their normal forms in the finite union of standard monomials appearing in these reductions. Then

\[
T_s=\ker_K C_s.
\]

Choose a nonzero maximal-rank minor of (C_s\), or the empty minor 1 if rank is zero. Enlarge \(\Delta\) to invert its numerator and the remaining reduction denominators. The chosen minor is now a unit. Larger minors are identically zero and remain zero on specialization. Block elimination by this invertible submatrix gives a split kernel commuting with reduction modulo (p\). Its rank is constant. This proves conditions 2 and 3. A matrix with no standard-monomial rows has zero rank and full kernel, handled by the same convention.

The certificate must retain the basis identities and the normal-form matrix, its rank witness, and the split-kernel operations. Merely listing denominators of returned rows proves neither saturation nor kernel completeness. Monicity handles ideal leading terms; nonzero kernel minors handle support intersection ranks. A source-specific pivot sequence, a chosen row basis, suitability, and equality of that basis with the full module need their own trace and invertible change-of-basis witnesses. They can enlarge \(\Delta\) further, if such a finite trace has been obtained.

The assertion proved is

\[
\forall(\mu,M)\text{ finite}\;\exists(\Delta,G_s,C_s,\text{identities})\;
\forall(c_0,p):p\nmid\Delta(c_0)\Longrightarrow (9). \tag{10}
\]

It is **not** \(\exists\Delta\;\forall\mu,M,c_0,p\), and not a claim that a growing family \(c(p)\) avoids \(\Delta_{\mu(p),M(p)}\). No degree, height, denominator exponent, bad-prime frequency, or computation bound for these certificates as \(\mu,M\) grow has been supplied. For fixed (c_0,\mu,M\) with \(\Delta(c_0)\ne0\), only finitely many prime divisors are excluded; this says nothing analogous for changing (c(p)\). The latter can lie in the bad locus for every (p\).

Fixed-base row products are a useful narrower uniformity: if one base set at \(\mu_0\) has (1) over a single localization, every product of (k\) rows remains in \(J^{\mu_0k}\) over that localization for all (k\). This proves uniform *soundness* of those product rows. It proves neither that they span the full \(J^{\mu_0k}\cap V_{M_k}\) nor that all the higher ideal-power quotients and kernel ranks satisfy (9) under one localization.

## 6. Worked controls required by the original plan

**Nonunit specialization.** Over \(\mathbb Q(c)[N,x]\), \((N,cx)=(N,x)\), with witness \(x=c^{-1}(cx)\). Specialize (c(p)=p\), (N=p\), (x=1\). The original integral generators are (p\) and (px\), and both vanish modulo (p\) at 1. Yet the generic row (x\) evaluates to 1, not 0 modulo (p\). For multiplicity \(\mu\), the generic row (x^\mu\) has witness \(c^{-\mu}(cx)^\mu\) and likewise fails modulo (p^\mu\). Clearing gives (c^\mu x^\mu\), whose value is (p^\mu\) and is correctly divisible. The localization must invert (c\), so the good-specialization predicate (p\nmid c(p)\) rejects this family. A nonzero rational function is not a finite unit. This is an exact counterexample to the shortcut, not to the conditional lemma.

**Rank separate from denominators.** The one-entry matrix \([c]\) has no denominators and generic rank 1. At (c(p)=p\), its reduction has rank 0. Thus (D=1\) passes a denominator test while the pivot numerator fails. The split-kernel minor condition detects the difference. Nonzero characteristic-zero pivots are also insufficient for modular rank preservation.

**Repeated relations.** Replacing (F_2,F_3\) by (F_1=f\) leaves (I=(f)\) and every (T_s\) unchanged, however many generator labels or duplicate rows are listed. Equations (5) and (7) therefore give the same budget. A sum-of-three-principal-gains rule would fail this control. No assumption of independence is made about the actual three relations.

**Equal support with incorrect coefficients.** The permitted historical control and pinned native source use (a=2,b=3\), (S(1,3,41)=4545=45\cdot101\), while (S(1,3,41)+1\equiv1\pmod{101}\). The constant term was already nonzero. Therefore support equality cannot imply root preservation or correct row membership. This is a previously recorded manual/source control, not a new executed finite-field trial.

**Signed lifts.** In that historical control (R=P+T\) for (P=(1,39),T=(3,6),R=(41,15)\), yet the all-positive sum is (P+T+R=2R\ne O\). The x-only polynomial zero does not certify the chosen signed relation. The present certificates stop before that interface.

**Principal ceiling.** Suppress (F_2,F_3\). Then (T_s=f^sK[x]\cap V_K\). The local index budget is (K_{\rm budget}=t d-q\) for total multiplicity (t\), exactly the archived determinant convention, where (d\) denotes row/column count and the formal modulus is still (N\). For convex (M\), Newton-product rigidity reduces this *principal* space to allowable translates of the Newton polytope of (f^s\). For the joint (I^s\), cancellation among several mixed generators prevents replacing its dimension by one principal erosion count or a sum of three such counts. Neither the S3 ceiling nor the S4/S5 source's explicitly principal corollaries settle this joint ideal.

## 7. Heights, determinant, and integer vanishing

Let \(H=\max(1,|c_{0,1}|,\ldots,|c_{0,9}|)\). For an integer coefficient polynomial (P(c,N)\), the elementary bound

\[
|P(c_0,n)|\le\|P\|_1 H^{\deg_cP}\max(1,|n|)^{\deg_NP} \tag{11}
\]

is enough to expose the missing charge. For each cleared row retain its coefficient polynomials, their degrees and coefficient norms, (D_j\), and a declared lift. Multiplying a square independent row basis rowwise by (D_j(c_0)\) multiplies its real covolume by \(\prod_j|D_j(c_0)|\), although (p\)-unit factors leave its (p\)-adic index unchanged. Conversely modular inversion can produce coefficients on the scale of \(|n|^\mu\). Even a fixed denominator 2 has inverse \((p^\mu+1)/2\) modulo an odd (p^\mu\); unit status gives no constant bound on that inverse's representative.

Large trailing coefficients need not change a genuinely triangular determinant. They still affect input bit lengths, and a denominator-clearing or leading-coefficient change can affect the determinant itself. Thus one must charge the *actual* lift and basis; one cannot universally add all coefficient heights to the determinant, nor universally discard them. A prime-to-(p\) scalar on an otherwise valid row already shows that divisibility alone does not imply a useful small-height row.

For (k\) products of a fixed finite base, degrees grow at most linearly in (k\), and coefficient \(\ell_1\)-norms multiply. Repeated denominator clearing can contribute (k\log|D(c_0)|\). With six variables and fixed base degrees, product support size has a polynomial upper bound from its degree box. This supports a finite bit-size argument when the base data are fixed, but does not prove that the exact dimension/determinant functions are the interpolated polynomials required by Heuristic 2. If (H=p^{O(1)}\), the term \(\deg_cP\log H\) in (11) is on the scale of \(\log p\), not an (O(1)\) loss. If the base multiplicity, trace, or support changes, the base constants themselves need uniform control.

For an actual integer row (g=\sum_{\alpha\in M}g_\alpha x^\alpha\), let

\[
v_B(g)=(g_\alpha X^{\alpha_1+\cdots+\alpha_4}Y^{\alpha_5+\alpha_6})_{\alpha\in M}.
\]

At any common root in the stated box, Cauchy–Schwarz gives

\[
|g(r)|\le\sqrt d\,\|v_B(g)\|_2.
\]

If (p^t\mid g(r)\) and \(\|v_B(g)\|_2<p^t/\sqrt d\), then (g(r)=0\) over the integers. This is the HHG argument with total multiplicity (t=\mu k\); it does not produce enough independent equations or guarantee extraction.

For a square independent coefficient basis with determinant (p^q U\), (p\nmid U\), column scaling gives

\[
\log_p\det\Lambda_B=q+\log_p|U|+
 s_{\rm leaf}\log_pX+s_{\rm internal}\log_pY.
\]

Here the two (s\)'s are sums of exponents over the four leaf and two internal columns respectively. The determinant-level budget after the coefficient determinant is charged is

\[
t d-q-\log_p|U|.
\]

The finite LLL/norm correction and the number of short vectors required remain additional charges. The formula is not a determinant formula for an unspecified dependent or rectangular row list. For (n=p\), the full integer module containing (p^\mu\mathbb Z^M\) has no non-(p\) index factors, but a chosen proper row sublattice can have such factors. Source span/completeness and real-height bookkeeping therefore matter even after (9).

## 8. Primary source comparison and remaining quantifiers

I read the pinned full-primary text's relevant sections, not only prior reports: §2.5 and Heuristic 1 (PDF p.6); §3.2 and §4.1–4.2 (pp.8–9); §6.1–6.3 (pp.19–21); §6.4/Heuristic 2 (pp.21–22); §6.5/Lemma 7 and §6.6 (p.23); Algorithm 3 (p.24); Appendix C and C.1 (pp.48–52). Page numbers refer to PDF pages; section boundaries can straddle pages.

Ryan's §6.1 uses (K_c[N,x]\) and explicitly requires precomputed denominators to be coprime to (N\) for modular inversion. §3.2 puts all same-modulus relations in one ideal. Heuristic 1 concerns zero-dimensionality of the ideal of *recovered integer polynomials*; several linearly independent coefficient vectors do not establish it. Heuristic 2 is a polynomiality assumption for suitable shift sets, not a consequence of finitely many interpolation samples. Lemma 7 assumes Heuristics 1 and 2, the shared-root premise, suitable lattice/statistic representation, substituted values proportional to (p\), strict margin (\delta<\delta^*-\epsilon\), sufficiently large (p\), and the stated growth condition

\[
\log p=\omega\!\left(\frac{s_{\rm dim}(k,k\tau)^2}{\sum_i b_i s_{x_i}(k,k\tau)}\right).
\]

Appendix C explicitly removes the final root-recovery step from its polynomial-time assertion. Its fixed precomputation has constant-size base data, followed by polynomial-size products as (k\) grows. It supplies no certificate that the present growing coefficients avoid all exceptional loci, or that a changing base multiplicity has controlled height. Nor does it turn an interpolation degree check into an unconditional proof of Heuristic 2. The parameter choices in its asymptotic statement cannot certify a fixed finite prime or the 24 unrun cells.

Pinned cuso's `ideal.py` introduces one modulus generator and groups equal modulus degrees; `optimal.py` uses support closure and echelon intersection; `utils.py` strips (N\) from unknown monomials while retaining it in coefficient expressions. `asymptotic.py` collects denominators of final (S_1\), which is a substitution condition, not the full witness/flatness/rank certificate above. `shift_set_properties.py` tracks augmented support and modulus exponents; `polynomial.py` interpolates finitely many values with degree checks; `limit.py` normalizes by the precomputation multiplicity and uses leading-term ratios. These are static source observations, not source execution or a proof that their interpolants govern every (k\).

Pinned native `model.hpp` freezes (a=2,b=3\), centers (11,13,17,19,23,29\), and target 5, with rational coefficients. `backend.hpp` treats the first modulus name as a polynomial variable over the rational field and explicitly enumerates ideal-power products. `exact.hpp` performs rational constant-pivot normalization; `pipeline.hpp` stores coefficient-height and specialization-obligation labels. This bounded fixture is not the full symbolic (c(p)\) family. No native call or full-cell parity is established by reading those files.

## 9. Minimal future proof-of-certificate design, not an authorization or run

A finite native certificate checker could check supplied identities by exact polynomial addition/multiplication, without trusting a solver's verdict:

1. Bind exact (c_0,n,p,\mu,M\), coordinate order, original coefficient hashes, and each row's support. Keep the modulus variable distinct from the row count.
2. Verify (2) for every returned row, or verify a localized witness plus the exact modular-lift identity. Check all required units against the correct modulus.
3. For an asserted full-module layer equality, verify (G_s\)'s two-way generator identities, monic leading terms, and reduction identities for all (s\le\mu\); verify (C_s\)'s normal-form columns, the unit maximal-rank minor, the vanishing larger-rank relations, and split-kernel transforms. This checks saturation and intersection/base-change separately.
4. Verify actual row independence/suitability and full spanning if claimed, with both-direction basis transformations and all index factors; compute the determinant from that certified basis, rather than counting input rows or product labels.
5. Verify the integer lift, denominator-clear multipliers, resulting coefficient heights and coordinate scaling, and retain exact finite norm and reduction factors. A layer count alone is not a small-height certificate.
6. Require the nonunit (c(p)=p\), rank-drop, repeated-relation, support-corruption and signed-lift controls at their respective interfaces. Keep the group controls outside the polynomial-divisibility certificate.

No checker of this design has been implemented or run in this task. It is the next exact artifact requirement for a future authorized conformance task. Before existing scientific cells, the original source/guard/readiness gates and no-retry restrictions still bind. After them, theorem suitability/Heuristics 1–2, finite root recovery, y/sign/subgroup verification, random-target yield/rank, and complete matched IC/rho costs remain separate obligations. No principal family ceiling, runtime refusal, or missing certificate closes the joint family.

The named existing obstruction is `problems/joint-smallroot-reach-baseline-and-oracle-unverified.md`. This derivation localizes one part of it to explicit finite bases, normal-form kernel minors and uniform-height/exceptional-family bounds. That shared record was read but not edited; only the Coordinator may compose this result and update shared records.
