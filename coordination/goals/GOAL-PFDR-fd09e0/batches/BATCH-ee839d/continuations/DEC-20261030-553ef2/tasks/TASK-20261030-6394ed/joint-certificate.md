# A finite joint layer certificate and its specialization interface

TASK-20261030-6394ed · 2026-10-30 · manual derivation, not independently reviewed.

**Result and scope.** For the exact three-equation object below, the formal-modulus module has an exact description by the flag of *joint* ideal-power intersections. A finite localization can make this description commute with specialization. Under the displayed monic-basis and flag certificates it also determines the complete integer lattice's prime-power index when the formal modulus specializes to the known prime. No values of the intersection ranks, no native trace, and no denominator or minor for the actual frozen cells have been computed. This is a conditional interface derivation (`proof_status: derivation`), not a numerical reach result, an executed certificate, or an extraction theorem. The finite localization existence argument is non-effective here and gives no uniform growing-multiplicity guarantee.

## 1. Exact object, coefficient rings and finite domains

Let c=(a,b,q,c1,c2,c3,c4,d1,d2), x=(z1,z2,z3,z4,h1,h2), and

\[
S(A,B,C)=(A-B)^2C^2-2((A+B)(AB+a)+2b)C+(AB-a)^2-4b(A+B),
\]
\[
F_1=S(c_1+z_1,c_2+z_2,d_1+h_1),\quad
F_2=S(c_3+z_3,c_4+z_4,d_2+h_2),\quad
F_3=S(d_1+h_1,d_2+h_2,q).
\]

Set A0=Z[c], K=Frac(A0)=Q(c), B0=A0[x], I0=(F1,F2,F3), and introduce a new indeterminate N, absent from the F_i. For μ≥1 set Jμ=(N,I0)^μ in B0[N]. J∞=0. There is one modulus generator, not three. The coordinate bounds remain (X,X,X,X,Y,Y).

Fix any finite, explicitly ordered set M of distinct x-monomials, d=|M|, and V_A=⊕_{m∈M} A m for a coefficient ring A. A requested cell may use M=(μ conv({0}∪E))∩Z^6, where E is its bound nonzero support union, but this proof neither enumerates that set nor replaces it by a discrete Minkowski sum. M must be fixed before the flag is certified. If specialization is intended to recompute M from nonzero supports, equality with this fixed M is an additional support/domain check. Generic coefficients and the fixed integer fixture need not have identical support.

For j≥0 write I_A=(F1,F2,F3) in A[x] and H_j(A)=I_A^j∩V_A; H_0=V_A. The H_j are intersections of powers of the **whole** joint ideal. They include cancellation and syzygies among all mixed products. They are not the sum of three principal-intersection dimension counts.

### 1a. Lemma U: a universal monic control for this exact object

**Proved manually, not the bound-induced order.** Use the auxiliary positive weighted-degree lexicographic x-order with weights (2,2,2,2,1,1), treating all nine parameters as coefficients. Then

\[
\operatorname{LM}(F_1)=m_1=z_1^2z_2^2,\quad
\operatorname{LM}(F_2)=m_2=z_3^2z_4^2,\quad
\operatorname{LM}(F_3)=m_3=h_1^2h_2^2,
\]

each with coefficient 1. For F1 and F2 the top term has weight 8; the terms A²BC and AB²C have weight at most 7, (A−B)²C² at most 6, and all remaining terms smaller. Replacing an input variable by a center lowers the weight. For F3 the top weight is 4, the q A²B/q AB² terms have weight at most 3, and the q²(A−B)² terms at most 2. These statements hold in Z[c,x], before any specialization. The m_i are pairwise coprime because their variable supports are disjoint.

Introduce independent coefficient indeterminates t1,t2,t3. In A0[t][x], the monic polynomials F_i−t_i have the same pairwise coprime leading monomials. Here is the product-criterion proof over this coefficient ring: if f=m+u and g=n+v are monic with coprime leading monomials m,n, their S-pair n f−m g=u g−v f has a standard representation whose two summands have leading monomial strictly below mn. Inductively reducing the largest remaining leading monomial proves zero remainder; no coefficient division is needed. The monic Buchberger argument therefore applies over A0[t], and these three polynomials are a monic Gröbner basis. Division gives a free A0[t]-basis W of monomials divisible by none of m1,m2,m3. Their quotient is A0[x] via t_i↦F_i. Consequently

\[
A_0[x]\simeq\bigoplus_{w\in W} A_0[t_1,t_2,t_3]w,
\quad t_i\text{ acts by }F_i.
\tag{U1}
\]

In particular the t-polynomial coefficient ring embeds; no algebraic independence of the F_i was assumed. It follows from (U1). For every j, I0^j is the A0-span of F^β w with |β|≥j, and its quotient has A0-basis the classes F^β w with |β|<j. Thus every A0[x]/I0^j is A0-free, and the same statement survives **arbitrary** coefficient specialization.

One can also give an explicit monic Gröbner basis for every power:

\[
G_j=\{F_1^{\beta_1}F_2^{\beta_2}F_3^{\beta_3}:|\beta|=j\}
\quad\text{in this auxiliary order}.\tag{U2}
\]

To prove completeness, each x-monomial factors uniquely as m^β w with w∈W: for each disjoint variable pair take the largest power of m_i dividing the monomial. The polynomials F^βw have these distinct leading monomials, all coefficient1, and lower terms strictly smaller. In a nonzero finite combination of them the largest of their leading monomials cannot cancel. By (U1), an element of I0^j has only |β|≥j, so its leading monomial is divisible by some m^γ with |γ|=j. This proves (U2), as well as the claimed free quotient. The number of product generators is binomial(j+2,2); that is a symbolic count, not a computation or a bound for their expanded coefficients.

This discharges global ideal-power flatness for the exact symbolic object and implies (I_Z^j:p)=I_Z^j after localization at every prime and every integral parameter specialization. It does **not** give H_j=I^j∩V or its base change, the clipped domain's ranks, the bound-induced leading terms, or the native returned span. The actual bound-order weights are separate. An auxiliary-order Gröbner basis can certify ideal membership without reproducing that trace.

## 2. Lemma F: coefficientwise formal-modulus decomposition

**Proved manually, any coefficient ring A.** Since I_A is independent of N,

\[
J_\mu=\sum_{a=0}^{\mu}N^a I_A^{\mu-a}A[N,x].
\]

More precisely, a polynomial g=Σ_{a≥0}N^a g_a(x) belongs to Jμ iff

\[
g_a\in I_A^{\max(\mu-a,0)}\quad\text{for every }a.
\tag{F1}
\]

Proof: expand products of μ elements from (N,I_A). A generator with N-degree b contributes to coefficient a≥b an element of I_A^{μ-b}⊂I_A^{μ-a} when a<μ. Conversely, each term N^a g_a with a<μ is in N^a I_A^{μ-a}, and every term with a≥μ is in (N^μ). The monomials N^a are A[x]-linearly independent, so no cancellation between different N-coefficients defeats this argument.

Consequently the exact supported module is

\[
L_N:=J_\mu\cap V_A[N]
=\sum_{a=0}^{\mu-1}N^aH_{\mu-a}(A)+N^\mu V_A[N].
\tag{F2}
\]

This identity requires neither a regular sequence of the F_i nor disjoint variable blocks. As an A-module, A[x,N]/Jμ is ⊕_{a=0}^{μ−1} N^a(A[x]/I_A^{μ−a}); this is a coefficientwise statement, not an assertion that those quotients have finite dimension.

Over K let r_j=dim_K H_j(K), r_0=d, and choose a basis v1,…,vd adapted to the nested flag: H_j(K)=span_K(v1,…,v_{r_j}). Let κ_i=max({j≤μ:i≤r_j}∪{0}) and λ_i=μ−κ_i. Then

\[
L_N=\bigoplus_{i=1}^d K[N]N^{\lambda_i}v_i,\quad
q_N=\sum_i\lambda_i=\mu d-\sum_{j=1}^\mu r_j.
\tag{F3}
\]

Indeed, in the adapted basis, the coefficient of v_i may occur at N-degree a exactly when a≥μ−κ_i. Thus the N-adic invariant exponents lie between 0 and μ. The determinant is det(v1,…,vd) N^{q_N}; its N-order is q_N. A unit of K has no N-order but can have arbitrarily large integer height or nonzero specialized p-valuation. Therefore (F3) alone is not a p-adic or Euclidean determinant statement.

## 3. Lemma C: an explicit finite certificate, and finite existence

**Conditional certificate implication; finite existence proved manually.** Fix μ and M. The following finite data suffice over A=A0[1/Δ], where Δ∈Z[c] is nonzero.

1. For each 1≤j≤μ, a finite monic Gröbner basis G_j for I_A^j in one declared x-term order. The explicit auxiliary-order family (U2), together with its proof above, is one choice and needs no denominators or unknown Gröbner computation. If another order is used, give both ideal-containment identities and reductions of every S-pair to zero, with leading-term descent. All coefficients and identities live in A[x]; no division by N occurs.
2. For every m∈M, a division identity m=Σ_g u_{mg}g+R_{jm}, with R_{jm} reduced by G_j. Let T_j have columns the coefficients of these remainders in the finite union U_j of their standard x-monomials. The monic Gröbner certificate proves H_j(A)=ker(T_j: A^d→A^{U_j}). It also proves A[x]/I_A^j is free over A on the possibly infinite standard-monomial basis.
3. A single matrix B∈GL_d(A), with columns v_i in the M coordinates, and integers d≥r1≥…≥rμ≥0. For each j give

   T_j B=[0 C_j], and a left inverse L_j C_j=Id_{d−r_j}.

   Also give B^{-1}. Empty tails use the unique empty identity. These identities imply, over A and after *every* coefficient base change, ker T_j=span(v1,…,v_{r_j}). They prove both containment and completeness, not just r_j independent membership witnesses.

Proof of implication: the S-pair and ideal identities establish a monic Gröbner basis. Division gives unique standard remainders over an arbitrary coefficient ring: if two differ, their difference lies in the ideal and has a leading monomial outside its leading ideal, a contradiction. Thus T_j detects membership in I_A^j exactly. Write any coefficient vector as B(u,w). If T_j B(u,w)=C_jw=0, the left inverse forces w=0. The reverse inclusion is immediate. All identities survive base change; monicity and the leading monomials survive too. Applying Lemma F gives (F2)–(F3) over A, with det B a unit of A.

Proof of finite existence: use the explicit universal G_j from (U2) and reduce the finitely many M monomials. These reductions have coefficients in A0. Work over K to choose an adapted flag basis. Every injective finite-column C_j over K admits a left inverse by an invertible maximal minor. There are finitely many rational functions in these data. Take a product of their nonzero polynomial denominators, including the coefficients of B^{-1} and the left inverses, and clear rational-number denominators into a nonzero Δ∈Z[c]. The same finite identities now hold over A. The global ideal bases have now been proved symbolically, but **none of the actual clipped-cell T_j, B, r_j, L_j or Δ has been generated**. A generic Δ can vanish on a whole desired fixed-parameter slice. That slice then needs a separate flag certificate; its usability is not implied by generic existence.

Explicit quantifiers:

\[
\forall\mu\ge1\ \forall M\text{ finite}\quad
\exists(\Delta_{\mu,M}\ne0,\mathcal C_{\mu,M})\quad
\forall(c_0\in\mathbb Z^9,p\text{ prime}):
p\nmid\Delta_{\mu,M}(c_0)\Longrightarrow\text{the certified base changes hold}.
\tag{C1}
\]

This is not ∃Δ∀μ,M, not a bound on deg Δ or its height, and not a probability statement about c0 depending on p. It says nothing when Δ(c0)=0 or p divides Δ(c0). For a fixed finite symbolic row trace, enlarge Δ to include its witness, transformation, inverse, comparison and branch data. Membership-only witnesses need fewer conditions than reproduction of the trace or equality with L_N. A finite trace may have nonconstant-in-N pivots; this certificate never turns them into coefficient units.

## 4. Lemma P: the p-adic layer and full integer index bridge

**Unconditional finite inclusion for the exact object.** At any integral parameter tuple and prime p, set V=O^M, Q_t=(p,I)^t, L=Q_μ∩V, and let A_a be the image of p^{−a}(L∩p^a V) in V/pV, for 0≤a<μ. Lemma U supplies power saturation on every such fiber; the proof of (P1) below therefore holds before any clipped certificate is supplied. Iterating it shows p^{−a}(L∩p^a V)⊂Q_{μ−a}∩V. Reduction gives

\[
A_a\subseteq\bar I^{\mu-a}\cap\mathbb F_p^M.\tag{P0}
\]

Since p^μV⊂L⊂V, choose an O-basis diagonalizing this full-rank submodule, with exponents 0≤η_i≤μ. This is a structure statement over the discrete valuation ring, not a performed computation. Then dim A_a=#{i:η_i≤a}; hence the actual usable p-budget is

\[
K_{\rm actual}=\mu d-\operatorname{length}_O(V/L)
=\sum_{a=0}^{\mu-1}\dim A_a
\le\sum_{j=1}^{\mu}\dim_{\mathbb F_p}(\bar I^j\cap\mathbb F_p^M).
\tag{P0b}
\]

This finite *joint* layer inequality needs no generic flag rank or p-unit minor and evaluates no dimensions. Equality with generic r_j, and the actual domain ranks themselves, are not supplied by it. The next conditional argument is precisely the additional lifting/base-change certificate that yields equality. No principal Newton geometry has been inserted into the right side.

**Proved under Lemma C's checked hypotheses and N0=p.** Specialize c→c0∈Z^9, choose prime p with p∤Δ(c0), and put O=Z_(p), B_O=O[x], I=(F1(c0,x),F2(c0,x),F3(c0,x)). Bar denotes reduction modulo p. Let V=O^M and H_j=I^j∩V. The certificate gives:

* B_O/I^j is O-free, so (I^j:p)=I^j for 1≤j≤μ;
* H_j is a direct summand of V and H_j/pH_j=bar I^j∩F_p^M, of dimension r_j;
* the same B is an adapted O-basis and det B is a p-unit.

For this exact object the first bullet is already supplied universally by Lemma U, without excluding any coefficient fiber. The second and third bullets still require the clipped-flag certificate. Keeping this distinction is essential: global ideal flatness alone does not commute arbitrary intersections with coordinate subspaces.

Write Q_t=(p,I)^t. For 1≤t≤μ,

\[
(Q_t:p)=Q_{t-1}.\tag{P1}
\]

Proof: if ph=Σ_{a=0}^t p^a g_a with g_a∈I^{t−a}, then g0 is divisible by p. Saturation of I^t gives g0=p h0 with h0∈I^t. Division by p gives h=h0+Σ_{a=1}^t p^{a−1}g_a∈Q_{t−1}. The other inclusion follows by multiplying by p. No regular-sequence assumption on the F_i was used.

Set L_t=Q_t∩V. Reducing f∈L_t modulo p puts it in bar I^t∩bar V=bar H_t, so lift its residue to h∈H_t. Then f−h=pv with v∈V, and (P1) gives v∈L_{t−1}. Hence

\[
L_t=H_t+pL_{t-1},\quad L_0=V,
\qquad L_\mu=\sum_{a=0}^\mu p^aH_{\mu-a}
=\bigoplus_i O\,p^{\lambda_i}v_i.
\tag{P2}
\]

This supplies an exact supported p-layer formulation, including cancellations. Define A_a as the image of p^{−a}(Lμ∩p^a V) in V/pV for 0≤a<μ. By the diagonal form,

\[
\dim_{\mathbb F_p}A_a=r_{\mu-a},\qquad
\operatorname{length}_O(V/L_\mu)=\sum_{a=0}^{\mu-1}(d-r_{\mu-a})=q_N.
\tag{P3}
\]

Now use the actual integral ideal I_Z=(F_i(c0,x))⊂Z[x] and the full integer supported lattice

\[
\mathcal L_\mathbb Z=(p,I_\mathbb Z)^\mu\cap\mathbb Z^M.
\]

Localization commutes with this intersection: clear the finitely many denominators in any membership identity. Thus its localization is Lμ. Since p^μ Z^M⊂L_Z⊂Z^M, its finite index has no prime factor other than p. Equation (P3) therefore yields the *global* integer covolume

\[
[\mathbb Z^M:\mathcal L_\mathbb Z]=p^{q_N},\qquad
\det(\mathcal L_\mathbb Z\operatorname{diag}(X^e))
=p^{q_N}\prod_{e\in M}X^{e_1+\cdots+e_4}Y^{e_5+e_6}.
\tag{P4}
\]

The usable determinant-level modulus budget is consequently

\[
K_{\rm full}=\mu d-q_N=\sum_{j=1}^{\mu}r_j.
\tag{P5}
\]

This is a conditional **full ideal lattice** identity, not a determinant inferred from the returned rows. For any d independent integer rows generating L'⊂L_Z, let m=[L_Z:L']. Their scaled determinant is m times (P4); the loss log_p m must be charged. Equality after tensoring with Q, or full row rank, does not show m=1. Equality over O only shows p∤m. A certificate for a complete integer basis needs both membership and a reverse integral span/saturation witness (e.g. exact unimodular transformations), or an independently checked complete-index certificate. Rational denominator clearing may introduce a large prime-to-p m even when it preserves the p-local lattice. Bounds on its size remain necessary for selected-row determinants.

There is no claim that such a factor is unavoidable. Define the p-primary saturation of a raw full-rank integer row lattice by Sat_(p')(L_raw)={v∈Z^M: s*v∈L_raw for some integer s coprime to p}. If L_raw⊂L_Z and their localizations at p are equal, then Sat_(p')(L_raw)=L_Z. Indeed, localization equality supplies such an s for each v∈L_Z. Conversely, multiplication by s is invertible on the p-primary group Z^M/L_Z, so s*v∈L_Z forces v∈L_Z. Thus a checked saturation or canonical p-primary congruence-preimage construction can remove all unit-index factors. Its actual construction, proof of the p-local span equality, integer output basis and bit complexity remain obligations. This distinguishes a raw cleared-row lattice, its saturation, and the full intended integer lattice; denominator clearing is a possible raw-row loss, not an inherent method lower bound.

If N0 is merely a multiple of p, row membership still gives p^μ divisibility, but (P1)–(P5) do not follow as stated. When v_p(N0)>1, (N0,I) is not automatically (p,I); when N0 is composite its full integer index may involve other primes. The present exact index bridge deliberately uses the known-prime case N0=p, appropriate to divisor_bound=1. It does not identify formal N-order with p-valuation without these hypotheses.

## 5. Worked exact joint instance without evaluating ranks

At μ=2 the formal ideal is generated by the ten products

\[
N^2,\ NF_1,\ NF_2,\ NF_3,
\ F_1^2,\ F_1F_2,\ F_1F_3,\ F_2^2,\ F_2F_3,\ F_3^2.
\]

For the given Semaev F_i these are literal polynomial identities, with no irreducibility or regular-sequence premise. For example g=z1 F1 F3−h2 N F2 has witnesses W_(0,1,0,1)=z1 and W_(1,0,1,0)=−h2 (coordinates (N,F1,F2,F3)); at a common root modulo p it evaluates to a multiple of p². It belongs to a supported lattice only if its entire support is included in that lattice's declared M. This example does not assert that a protocol M contains it.

For *any* fixed M, g=g0+Ng1+N²g2+… is in the supported J2-module iff g0∈H2, g1∈H1 and ga∈V for a≥2. If the finite certificate is supplied, its flag consists of r2 basis vectors of exponent λ=0, r1−r2 of exponent λ=1, and d−r1 of exponent λ=2. Thus q_N=2d−r1−r2 and K_full=r1+r2 under the good-prime bridge. No values of r1,r2,d were evaluated.

Mixed syzygies, for example F2·F1−F1·F2=0, already show why counting product generators is not counting independent rows. If an input relation is repeated, the ideal I and every H_j stay exactly the same. Three equal relations therefore give precisely the same budget as one; adding their three principal budgets would fail this control.

Suppress F2,F3 and retain the same declared variable/domain scaling. Then H_j=(F1^j)∩V and (P5) is the principal sum-of-layer dimensions. For an independently specified monic triangular integer basis with pivot exponents a_i and no extra index, q=Σ_i a_i and K=μd−q, exactly the archived t*d−q accounting with t=μ. This reproduces that baseline identity; it does not reproduce or extend a principal Newton-polytope ceiling. The one-polynomial Ostrowski/translate-count step in upstream S3 §2 does not bound the joint H_j. Upstream S4/S5 §7c likewise explicitly leaves multi-ideal lattices outside its closure.

## 6. Worked counterexamples separating certificate requirements

**Nonunit control, disproved shortcut.** Over Q(c)[N,x], (N,cx)=(N,x), so x has the witness x=(1/c)(cx). Specialize c=p,N=p and x=1. Both original generators evaluate to p, but x evaluates to 1. Thus generic membership does not imply p-divisibility of the naively specialized normalized row. The denominator c is not a unit modulo p. Clearing it gives cx, a valid integral row, with coefficient height log2 p. For M={1,x}, the generic H1 is span{x}, so q_N=1. The specialized ideal (p,px)=(p) has full supported lattice p Z², index p² and usable budget zero. The incorrect q=1 transfer fails exactly at Δ=c. For general μ, (p,px)^μ=(p^μ), whereas the generic normalized x^μ row would wrongly claim divisibility of 1 by p^μ. This rejects the shortcut without refuting specialization on the good locus.

**Units alone do not preserve ranks or leading degrees.** The polynomial matrix [[1,1],[1,1+c]] has all coefficient denominators 1. Its generic determinant c is nonzero. At c=p it still has rational rank two, but its reduction modulo p has rank one; a maximal minor must be a p-unit, not merely a nonzero integer. Likewise c x²+x+1 loses its leading degree modulo p at c=p, though its coefficient denominators are 1. A finite trace must record leading coefficients and the pivot/minor conditions separately. Equal generic rank does not certify modular span: integer rows p e1,e2 have full Q-rank but index p in Z².

**Global monicity does not preserve clipping.** In Z[c,x,y], I=(x+c y) has a monic leading x for the order x>y, and its quotient is the free Z[c]-module Z[c,y]. For V=span{x}, I_K∩V_K=0: substitution x=−c y sends any nonzero scalar multiple of x to a nonzero polynomial over Q(c). At c=0 the specialized ideal is (x), so its intersection with V is span{x}. Thus ideal flatness and stable monic leading x coexist with failure of clipped-intersection base change. At c=p over Z_(p), I∩V is still zero, but bar I∩bar V=span{x}; a clipped remainder matrix is [c], so its rank minor c fails the p-unit test. Also (p,x+p y)=(p,x), so the supported p-lattice contains x itself. This is an explicit warning against using the formal flag without its base-change certificate, even when all ideal-power quotients are free and all global denominators are 1. It is a nearby-object control, not a claim that this particular Semaev domain has the same defect.

**Membership is not extraction or object identity.** The archived support-preserving F1+1 control and the x-only signed-lift control remain separate requirements. A false same-support relation cannot use a membership witness against the original bound ideal unless its actual polynomial identity holds. Conversely, a true Semaev modular zero does not identify compatible F_p y-lifts, subgroup membership or signs. None of the flag identities provides these group witnesses or a zero-dimensional recovered ideal.

## 7. Integer heights and multiplicity charges

Use ||P||1 for the sum of absolute integer coefficients of a polynomial in all its displayed variables. Let H=max(1,|a0|,|b0|,|q0|,|c_i0|,|d_i0|). Expanding S as a polynomial in A,B,C,a,b gives total coefficient norm 28 and total degree at most 4. Affine substitution has ||c+z||1≤H+1. Termwise submultiplicativity therefore proves, for each exact F_i,

\[
\|F_i(c_0,x)\|_1\le28(H+1)^4.\tag{H1}
\]

For a raw generator N0^a F^β with a+|β|=μ, its norm is at most |N0|^a[28(H+1)^4]^{μ−a}. This is an explicit bound for raw generators, not for unknown Gröbner transformations.

For any rational symbolic retained row give d_i(c)g_i=P_i∈Z[c,N,x], **and** an integral identity P_i=Σ_{a+|β|=μ}W_{i,a,β}N^aF^β. Let σ_i=||P_i||1, D_i=deg_c P_i and ν_i=deg_N P_i. At integer specialization,

\[
\|P_i(c_0,N_0,x)\|_1\le\sigma_i H^{D_i}\max(1,|N_0|)^{\nu_i}.\tag{H2}
\]

The right side bounds coefficient bit length by 1+log2 σ_i+D_i log2 H+ν_i log2 max(1,|N0|). It also bounds the L1 norm, which includes the support-count contribution. Record the corresponding degree/norm data for d_i, the integral witnesses, B, B^{-1}, G_j and row transformations when their construction/checking cost is claimed. Existence of a finite Δ does not bound any of these quantities as μ,M grow.

Clearing denominators preserves the ideal identity and p^μ divisibility. It can multiply a selected square determinant by ∏|d_i(c0)| relative to a valid rational representation; log_p of this factor must not be discarded merely because p∤d_i(c0). Additional span/saturation work may remove that loss, but the work and resulting integer basis heights need their own evidence.

Alternatively, for d_i(c0) coprime to N0 and Q=|N0|^μ, choose u_i d_i(c0)≡1 mod Q and form the polynomial u_i P_i coefficientwise modulo Q. Each centered representative coefficient has absolute value ≤Q/2. The difference from u_i P_i is a multiple of N0^μ times an integer polynomial, so the resulting integer row is still in (N0,I_Z)^μ. Before coefficient reduction, the inverse can have size up to Q/2; after reduction the coefficient bit length is O(μ log|N0|), with the explicit support count still charged. This is not an O(1) height claim. Changing representatives can change leading coefficients, valuations and selected-row spans, so record and verify the actual representative rows. Congruence modulo p^μ alone does not preserve Euclidean determinant or integer span.

Products of k certified integer base rows belong to (N0,I_Z)^{μk}. Their L1 norm is at most the product of the k base norms; monomial x-shifts do not change it. If each base norm is ≤B, a product has coefficient bit length at most 1+k log2 B. Integer linear combinations with coefficients a_l add the bound Σ_l |a_l| times the corresponding product bounds. This charges transformation size. If a product is reduced coefficientwise, reduction modulo N0^{μk} preserves the target ideal; reduction only modulo N0^μ need not preserve the higher multiplicity.

For a fixed finite base packet (fixed μ,M,G_j,B,rows), σ_i,D_i,ν_i and the base support sizes are constants *depending on that packet*. If H≤p^C and N0=p, (H2) gives polynomial bit length in k and log p for products of k such rows. This is the limited fixed-precomputation height argument consistent with Ryan Appendix C. It does not give polynomial precomputation or degree/height bounds when μ or the domain itself changes with p or k. To assert such a growing family one must provide uniform bounds on the packet sizes, coefficient degrees/norms, denominator/minor degrees and heights, good-specialization locus, transformation size, actual integer span/index, suitability and construction cost. Neither ∀fixed μ∃Δμ nor a fixed fixture supplies them.

## 8. Relation to the primary source and exact remaining obligation

Ryan's pinned 52-page PDF, SHA256 15dd6ae6b939c51f3bc124097f954bd858ef47e4739037381fb4951f0366043f, was actually read here in the relevant sections. Page references below are PDF pages, which match the printed page labels in the inspected text: §2.5/Heuristic 1 p6; ideal construction §3 pp7–8; integer-lattice optimality §4.3 pp11–12; §6.1 pp19–20; §6.2 pp19–20; §6.4 pp21–22; Heuristic 2 p22; Lemma 7/§6.5 p23; Algorithm 3 p24; Appendix C pp48–51 (example continues pp51–52).

* **Retrieved source statement:** §6.1 works over K_c[N,x], and substitutes denominators by inverses modulo N^{k_pre} only when coprime to N. It does not remove the need to certify the witnesses and good locus of a new instance.
* **Retrieved source theorem scope:** §4.3 Theorem 1 concerns the optimal *integer* dual lattice for a fixed ideal and monomial set; its proof uses integer spans. This must not be substituted for a proof that coefficient-field source rows specialize to a complete integer basis.
* **Heuristic, not discharged:** Heuristic 1 says the ideal of recovered integer polynomials in Q[x] has zero-dimensional variety. Heuristic 2 gives polynomial dimension/determinant functions when the constructed sets are suitable. Neither is a proof for this six-variable object.
* **Conditional primary result:** Lemma 7 assumes Heuristics 1 and 2, shared-root and suitable construction conditions, proportional-to-p substituted values, sufficiently large p, strict δ<δ*−ε, and log p=ω(s_dim²/Σ b_i s_xi) in the stated growing-multiplicity regime. Its polynomial-time statement excludes final root recovery. Appendix C explicitly charges polynomial coefficient bit lengths for a fixed finite S1 and products. It does not certify an arbitrary changing μ/S1 or the final extraction.
* **Source semantics, not an execution:** pinned cuso `ideal.py:54–102` puts all three degree-one relations and N in the same ideal; `optimal.py:9–32,36–81` constructs and intersects rows; `asymptotic.py:64–74` reports denominators found in returned S1; `shift_set_properties.py:132–211` extracts formal N exponents and augmented polytope statistics; `limit.py:76–109` performs the μ normalization and a leading-term-ratio analysis. Returned-row denominators alone are not this document's full witness/Gröbner/minor/span certificate, and formal N statistics do not bound integer coefficient height. No cuso or native code was imported or executed.

**Named unresolved obligation JOINT-FINITE-PACKET-6394ed.** Use the proved auxiliary G_j family to produce the remainder/adapted-flag/left-inverse packet for the *actual declared* μ,M, and prove that the selected native rows generate the intended supported module. The formulas above reduce the missing clipped layer theorem to finite identities and rank certificates; they do not supply their values. Then, for a concrete prime specialization, record p∤Δ(c0), actual bound-order leading/pivot/trace checks, integer representatives and the full integer span/index/height witnesses. A failure names that fiber or implementation condition and does not refute the family. A pass qualifies the finite algebraic interface only.

**Named unresolved obligation JOINT-UNIFORM-HEIGHT-6394ed.** Give explicit size/height and good-specialization bounds uniform in the claimed varying μ,k,M and p-dependent parameters, or restrict the claim to a fixed finite base packet. No random-parameter success frequency has been derived. These names refine the existing problem `problems/joint-smallroot-reach-baseline-and-oracle-unverified.md`; that frozen/global record was not edited because this handoff permits only nine new outputs.

**Design-only next checker.** Hash-bind the exact object/rings/order/domain; verify polynomial identities and monic S-pair descent; verify T_j B, B^{-1}, L_j C_j; retain complete row witnesses and inverse trace; specialize with p-unit and leading/pivot checks; verify actual integer span and determinant index; charge heights and bit complexity. Reject incomplete evidence rather than infer ranks from row counts. A future checker needs separately authorized implementation and execution; none ran here. The old 24 cells remain unrun, terminal Q4 remains no-retry, and prior independence exit1 remains unwaived.

Even a completed finite packet does not supply enough HHG-short integer equations, extraction, compatible signed group relations, random-target yield/independence, or a fully charged matched IC/rho comparison. At bounds |z_i|<X,|h_i|<Y, an actual integer row g=Σ a_e x^e of multiplicity T has the elementary sufficient vanishing condition Σ_e |a_e|X^{e1+…+e4}Y^{e5+e6}<p^T. Equivalently a weighted coefficient 2-norm below p^T/√s suffices for s terms. Membership establishes the divisibility premise only. No short vector, root, subgroup instance or measured attack cost was produced.

Novelty is a problem-specific adaptation of ideal powers, monic Gröbner specialization, nested linear flags and p-adic length bookkeeping; broader novelty remains unknown. `dominated_by: n/a (no attack result claimed)`; `sota_delta: no attack or quantitative advantage; finite conditional proof-interface contribution only`; enumerated family closures: none.
