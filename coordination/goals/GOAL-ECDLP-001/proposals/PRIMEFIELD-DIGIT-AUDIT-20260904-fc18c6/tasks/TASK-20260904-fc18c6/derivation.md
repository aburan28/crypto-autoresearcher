# Prime-field digit audit: symbolic derivation

**Task:** `TASK-20260904-fc18c6`  
**Status of this document:** local, unpublished producer work; no independent review, publication, evidence promotion, solver consequence, or hypothesis-status transition is claimed.  
**Fixed scope:** (p>3) is prime, (E/mathbf F_p) is ordinary with (y^2=x^3+ax+b), (K=mathbf F_p(E)), and τ is the Serre–Tate canonical section in the fixed compatible coordinates. The sum domain is (E(mathbf F_p)\setminus\{O\}), not a subgroup.

## Notation and source boundary

Write (u(a)\in\{0,\ldots,p-1\}) for the ordinary integer representative, ([a]\in\mathbf Z/p^2\mathbf Z) for the Teichmüller representative, and

\[
c_p(a)=\frac{[a]-u(a)}p\pmod p.
\]

Let (C_p\in\mathbf F_p[X]) be the unique polynomial of degree (<p) representing (c_p). For (z\in\mathbf Z/p^2\mathbf Z), represented in ([0,p^2)), write (d_1(z)=\lfloor z/p\rfloor\pmod p). Put ψ(_p(t)=e^{2\pi i u(t)/p}) and ψ(_{p^2}(z)=e^{2\pi iz/p^2}).

The external facts actually read for this audit are:

1. Voloch–Walker, *Euclidean weights of codes from elliptic curves over rings*, §§3–4, especially Theorem 3.1, Proposition 4.2 and Remark 4.3 (`retrieved`; <https://www.math.canterbury.ac.nz/~f.voloch/Pdfs/codes15.pdf>; supplied retrieval SHA-256 `626568c410484b7e2df2ca96d895d28329c23650a4b5dfb3003788a8b49f5828`; verified in this task). Proposition 4.2 proves that the canonical second Witt coordinate (x_1) is a polynomial in (x) of degree ((3p-1)/2), and its converse characterizes the canonical lift under the stated global-section and degree hypotheses.
2. Régis Blache, *Lifts of points on curves and exponential sums*, §3, especially the definition of reduced pole order and Theorem 3.1 (`retrieved`; <https://arxiv.org/pdf/math/0202206>; supplied retrieval SHA-256 `324f52f7434afb1ab9fd8998edde15ecefff3f47109d26e1625fc70f83ff6f64`; verified in this task). For a nondegenerate length-one Artin–Schreier class on a genus-(g) curve, the coefficient is (2(g-1)+\sum_P(rp_P(f)+1)\deg P); the local conductor divisor coefficient is (rp_P(f)+1).

The frozen statement and producer protocol were supplied internally by the Coordinator with frozen-statement SHA-256 `0379687db85960f1f8a6558f1312992a4e4453321ba8fba8baaf05194966e46c`. They are constraints, not external mathematical support.

## Lemma 1: ordinary digit, Witt coordinates, and phases

The standard isomorphism (\iota:W_2(\mathbf F_p)\to\mathbf Z/p^2\mathbf Z) is

\[
\iota(a_0,a_1)=[a_0]+p[a_1]\equiv u(a_0)+p\bigl(c_p(a_0)+u(a_1)\bigr)\pmod {p^2}.
\]

Consequently

\[
\boxed{d_1(\iota(a_0,a_1))=a_1+C_p(a_0)\quad\text{in }\mathbf F_p.}
\]

For the canonical lifted (x)-coordinate τ(^*x=(x,x_1)), the ordinary digit phase is therefore the length-one phase attached to

\[
F_{\rm can}=x_1+C_p(x)\in K.
\]

It is not the primitive whole-Witt character. Pointwise,

\[
\psi_{p^2}(\iota(a_0,a_1))
=\psi_{p^2}(u(a_0))\,\psi_p(a_1+C_p(a_0)),
\]

so deleting the first factor changes the observable. Also, the second-coordinate phase ψ(_p(a_1)) differs from the digit phase by the carry factor ψ(_p(C_p(a_0))). Neither (a_1\mapsto\psi_p(a_1)) nor the digit map by itself should be silently called the primitive additive character of (W_2).

Synthetic controls, with (c=C_p(u)), are:

| Witt vector | integer under ι | second-coordinate phase | carry phase | ordinary-digit phase | primitive phase |
|---|---:|---:|---:|---:|---:|
| ((u,0)) | ([u]=u+pc) | (1) | ψ(_p(c)) | ψ(_p(c)) | ψ(_{p^2}([u])) |
| ((u,-c)) | (u) | ψ(_p(-c)) | ψ(_p(c)) | (1) | ψ(_{p^2}(u)) |
| fixed ((a_0,a_1)) at every point | fixed | fixed | fixed | fixed | fixed |

Thus any constant vector produces a sum of absolute value “the number of sampled points” under every phase, even when its phase is not (1). Constants and geometric triviality must be separated from nonconstant Artin–Schreier classes.

Precision-one control: the first Witt coordinate is exactly (x), with ((x)_\infty=2[O]). Because (2) is prime to (p), (x\notin K^p-K+\mathbf F_p). Hence the primitive vector ((x,x_1)) is nondegenerate already at its first component; this says nothing by itself about the digit phase until (F_{\rm can}) is formed.

## Lemma 2: (C_p), its leading coefficient, and its conductor

The Teichmüller identity ([a]^p=[a]\pmod {p^2}) and ([a]=u(a)+pc_p(a)) give

\[
c_p(a)=\frac{u(a)^p-u(a)}p\pmod p.
\]

An exact interpolation formula is

\[
C_p(X)=\sum_{a\in\mathbf F_p}c_p(a)\bigl(1-(X-a)^{p-1}\bigr).
\]

Its (X^{p-1})-coefficient is (-\sum_a c_p(a)). Pairing (u) with (p-u), for (1\le u\le p-1), gives

\[
c_p(p-u)\equiv-c_p(u)-1\pmod p,
\]

because ((p-u)^p\equiv-u^p\pmod {p^2}). There are ((p-1)/2) pairs, hence

\[
\sum_{a\in\mathbf F_p}c_p(a)=-(p-1)/2=1/2,
\qquad
\boxed{\deg C_p=p-1,\quad \operatorname{lc}(C_p)=-1/2.}
\]

Since (x) has its unique pole at (O), of order (2),

\[
(C_p(x))_\infty=(2p-2)[O].
\]

The order (2p-2) is prime to (p). Local Artin reduction cannot remove a leading pole whose order is prime to (p): if (g) has a pole of order (n>0), then (g^p-g) has leading pole order (pn). Therefore

\[
rp_O(C_p(x))=2p-2,
\qquad
\operatorname{cond}_O\mathcal L_{\psi_p(C_p(x))}=2p-1.
\]

This positive reduced pole also proves geometric nontriviality. The sheaf is lisse on (E\setminus\{O\}); (O) is excluded from the sum.

## Lemma 3: the specified canonical representative (F_{\rm can})

Voloch–Walker Proposition 4.2 derives

\[
\frac{dx_1}{dx}=A^{-1}y^{p-1}-x^{p-1}
=A^{-1}(x^3+ax+b)^{(p-1)/2}-x^{p-1},
\]

where the Hasse invariant (A\ne0) because (E) is ordinary. The right side has degree (3(p-1)/2) and leading coefficient (A^{-1}). Since (d=(3p-1)/2\equiv-1/2\pmod p), integration gives

\[
\deg_x x_1=d,\qquad \operatorname{lc}(x_1)=A^{-1}/d=-2A^{-1}\ne0.
\]

The possible additive terms (1) and (x^p) in the source proof do not alter this higher leading degree. Since (p-1<d), adding (C_p(x)) cannot cancel it. Thus

\[
\boxed{\deg_x F_{\rm can}=(3p-1)/2,\quad
(F_{\rm can})_\infty=(3p-1)[O].}
\]

Again (3p-1) is prime to (p), so this specified global representative is already Artin–Schreier reduced at (O):

\[
\boxed{rp_O(F_{\rm can})=3p-1,\qquad
\operatorname{cond}_O\mathcal L_{\psi_p(F_{\rm can})}=3p.}
\]

In particular (F_{\rm can}\notin K^p-K+\overline{\mathbf F}_p), so the associated rank-one sheaf is geometrically nontrivial. These are statements in (K) about the fixed canonical section. Equality of values on (E(\mathbf F_p)\setminus\{O\}) is strictly coarser than equality, or Artin–Schreier equivalence, in (K).

For comparison only, the primitive length-two vector ((x,x_1)) has local weighted pole

\[
\max\{p\cdot2,3p-1\}=3p-1
\]

and therefore the same numerical conductor coefficient (3p), while defining a different phase by Lemma 1.

## Lemma 4: the full-curve bound and what it does not imply

Let (N=\#E(\mathbf F_p)-1) and

\[
S_{\rm digit}=\sum_{P\in E(\mathbf F_p)\setminus\{O\}}
\psi_p(F_{\rm can}(P)).
\]

Blache Theorem 3.1, with genus (g=1), one rational pole, and reduced pole (3p-1), gives

\[
\boxed{|S_{\rm digit}|\le 3p\sqrt p.}
\]

The same coefficient follows by inserting the exact local data into the Voloch–Walker/Schmid bound. The usable statement is

\[
\frac{|S_{\rm digit}|}{N}
\le \min\!\left\{1,\frac{3p^{3/2}}{\#E(\mathbf F_p)-1}\right\}.
\]

The displayed source term is worse than the trivial bound (N): Hasse gives (N\le p+2\sqrt p), whereas (3p^{3/2}>p+2\sqrt p) for (p>3). Hence at the base field the theorem yields no nontrivial normalized bias bound beyond (1).

This is a complete affine-curve sum with (O) removed because it is the pole. It is not a subgroup sum, hybrid sum, digit-bucket statement, scalar-recovery statement, (q_{\rm maj}) statement, or generic-prime-order consequence. A prime-to-(p) subgroup was motivational only. In the anomalous case (\#E(\mathbf F_p)=p), the prime-to-(p) subgroup has only the identity, so it is not a separating subgroup control.

## Lemma 5: sample reduction and collision controls

Let (R_{\rm can}\) be the unique remainder of the polynomial (F_{\rm can}(X)) modulo (X^p-X), with degree (<p). For every affine (P\in E(\mathbf F_p)),

\[
R_{\rm can}(x(P))=F_{\rm can}(x(P)).
\]

But the leading monomial of degree ((3p-1)/2\ge p) folds to lower degree, so the global leading pole (3p-1) does not survive in the remainder: ((R_{\rm can})_\infty\le(2p-2)[O]). Moreover (F_{\rm can}-R_{\rm can}) retains the sole leading pole (3p-1), prime to (p). Therefore

\[
\boxed{F_{\rm can}-R_{\rm can}\notin K^p-K,}
\]

even though the two functions have identical affine ℝ(_p) samples. Their Artin–Schreier classes differ. The exact degree, reduced conductor, and possible constancy of (R_{\rm can}) are curve-dependent obligations not settled here; no minimum over all sample-equivalent representatives is claimed.

The required controls make the distinction sharp:

1. (0) and (x^p-x) agree on all affine ℝ(_p) points and are Artin–Schreier equivalent because (x^p-x=g^p-g) for (g=x). Although the unreduced pole order is (2p), the reduced class is zero and the geometric sheaf is trivial.
2. (0) and (x(x^p-x)=x^{p+1}-x^2) also agree on all affine ℝ(_p) points, but the latter has sole pole order (2p+2), prime to (p). It is reduced, is not an Artin–Schreier coboundary, and has conductor coefficient (2p+3). Sample equality therefore does not determine the sheaf.
3. (F_{\rm can}) and (R_{\rm can}) instantiate the second phenomenon: equal samples, inequivalent classes, and different global leading-pole information.

Optional exact source fixture: for (p=5), Voloch–Walker Remark 4.3 gives the canonical lift of (y^2=x^3+x) with (x_1=4x^7+x^3). Direct symbolic interpolation gives (C_5=2X^4+3X^3), hence (F_{\rm can}=4x^7+2x^4+4x^3), with pole order (14=3p-1) and conductor (15). Modulo (X^5-X), (R_{\rm can}=2x^4+3x^3=C_5), of conductor (9). This fixture checks the formulas and the sample collision only; it is not evidence about generic prime-order curves.

## Lemma 6: transfer boundary for an arbitrary good-reduction lift

There are two different transfer levels.

**Pointwise torsion compatibility.** If (P\in E(\overline{\mathbf F}_p)) has order (n) with ((n,p)=1), then finite étaleness of (n)-torsion gives a unique (n)-torsion lift through reduction on any fixed good-reduction elliptic lift. On the canonical lift, τ is a group homomorphism and reduces to the identity, so τ((P)) is exactly that unique prime-to-(p) torsion lift. This establishes the pointwise compatibility used in the original `b4e6eb` motivation on the canonical model.

**Global-coordinate/conductor transfer.** The preceding uniqueness does not identify the global coordinates of torsion lifts on two different (W_2)-models. For an arbitrary good-reduction lift, a chosen lifted point with Witt (x)-coordinate ((x,x_{1,s})) still satisfies the universal pointwise digit identity

\[
d_1=x_{1,s}+C_p(x).
\]

If (x_{1,s}) is supplied by a global rational section, Blache's theorem can be applied to (F_s=x_{1,s}+C_p(x)) only after its actual reduced poles and nondegeneracy are proved. There is no source-supported reason for (x_{1,s}) to have canonical degree ((3p-1)/2), or for (F_s) to have conductor (3p).

Indeed, the converse in Voloch–Walker Proposition 4.2 says that a lift admitting a scheme section over (E\setminus\{O\}), regular away from (O), with “small” coordinates (deg x_1<3p), (deg y_1<4p), is forced to be the canonical lift and the section is forced to be the elliptic Teichmüller section. Thus those hypotheses cannot be assumed for a genuinely arbitrary noncanonical lift.

The exact (3p) conductor transfers only along an identified presentation that carries the canonical global section and preserves its leading pole. Transfer to an arbitrary good-reduction model remains open without such an identification or a fresh pole calculation. This open transfer issue asserts nothing about ECDLP hardness.

## Proof-search map, limits, and disposition

- **Baseline reproduction:** the precision-one first coordinate is (x), with pole (2[O]); the primitive Witt character and ordinary-digit phase are separately reconstructed.
- **Observation collision:** (0\sim x^p-x) supplies an equal-sample/equal-AS-class control; (0) versus (x(x^p-x)), and (F_{\rm can}) versus (R_{\rm can}), supply equal-sample/different-AS-class controls.
- **Quantifier order:** first fix (p,E), the canonical lift, and compatible coordinates; then define the single global (x_1) and (F_{\rm can}); then prove the formulas uniformly for every affine (P\in E(\mathbf F_p)). No representative is selected after inspecting samples.
- **Method ceiling:** the source theorem certifies only the stated full affine sum for the specified global representative (and here is numerically weaker than trivial). It cannot certify subgroup, hybrid, digit-bucket, or scalar-recovery claims.
- **Dominance/SOTA accounting:** `dominated_by: n/a (no algorithmic result claimed)`; `sota_delta: no attack or ECDLP complexity change; exact representation and conductor audit only`.
- **Unresolved obligations:** exact curve-dependent (R_{\rm can}) degree/conductor; global section and pole data for an arbitrary noncanonical lift; any nontrivial estimate for the actual base-field sample sum. These make every downstream attack interpretation inconclusive.

No experiment, command, computer algebra, benchmark, scalar recovery, novelty claim, or breakthrough claim was performed or made.
