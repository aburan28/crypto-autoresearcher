# Candidate norm-character derivation

Task: TASK-20261027-e6b5bf; IDEA-20261024-3c71a9; GOAL-PEXT-4a1d6b; BATCH-3e067e.
Producer: Coordinator source/proof intake, 2026-10-27.

**[Internal observation]** This is the approved zero-run intake. The five exact internal source pins in [source-map.json](source-map.json) match their opening-DEC SHA-256 values. The two sibling reports were read from their pinned Git blobs, not replayed. There are zero new scientific observations, field/group calculations, enumerations, compiler invocations or Lean checks. The written algebra below is **[Derived candidate]**, including statements phrased as implications or equalities; it has no independent proof verdict.

**[Unresolved]** Both the IACR PDF and the supplied CiteSeerX mirror of 2015/805 returned HTTP 403. Only the abstract and bibliographic page were read. Duplication and novelty remain unverified. The original IDEA and all earlier records are preserved. Readiness in the companion JSON is a preparation assessment, not a scientific status or experiment approval.

Classification applies paragraph by paragraph; all formulas and tables inherit their paragraph's label. Administrative source/access facts are internal observations. No mathematical statement below silently upgrades from candidate to theorem.

## 1. Quartic, rational origin, Jacobian and cubic

**[Derived candidate]** Let \(q\) be an odd prime power, \(K=\mathbb F_{q^n}\), and \(\sigma(z)=z^q\). For the proposed family, \(n\) is an odd prime, \(x\) has exact \(\sigma\)-orbit length \(n\), \(a_1,a_2,a_3,a_4\) are distinct residues modulo \(n\), and \(e_i=\sigma^{a_i}x\). Put \(c\in K^\times\). Let \(C_c\) be the smooth projective model of
\[
 y^2=c\prod_{i=1}^4(z-e_i).
\]
Four distinct branch points and characteristic different from 2 give a separable double cover of the projective line of genus one: the ramification formula is \(2g-2=2(-2)+4=0\). The point \(O=(e_4,0)\) is \(K\)-rational for every \(c\), even when the two points above infinity are not rational. Use \(O\) as origin. The pointed genus-one curve identifies with its Jacobian by \(P\mapsto[P-O]\); this is the Jacobian meant throughout.

**[Derived candidate]** Define
\[
 r_i=e_4-e_i\quad (1\leq i\leq3),\qquad A=c\,r_1r_2r_3\ne0,
 \qquad v=(z-e_4)^{-1},\quad w=y/(z-e_4)^2.
\]
Then
\[
 w^2=c(1+r_1v)(1+r_2v)(1+r_3v).
\]
Setting \(X=Av,\;Y=Aw\) gives the monic cubic
\[
 E_c:\quad Y^2=\prod_{i=1}^3(X-\alpha_i),\qquad
 \alpha_i=-A/r_i.
\]
The inverse on the common affine open is \(z=e_4+A/X,\;y=AY/X^2\). The branch point \(O\) maps to the cubic point at infinity. For \(i\le3\), \((e_i,0)\) maps to \((\alpha_i,0)\). These inverse rational maps extend over the smooth projective curves and give the pointed isomorphism. Distinct \(e_i\) give distinct \(\alpha_i\). The construction uses no division by 3 and works in odd characteristic including 3.

**[Unresolved]** The new derivation supplies an explicit candidate identification rather than assuming the IDEA's universal constant. Independent assessment of this identification and extension at the omitted points remains a gate.

## 2. Exact differences, coefficient and twist normalization

**[Derived candidate]** Write \(d_{ij}=e_i-e_j\). If \(\{i,j,k\}=\{1,2,3\}\), direct subtraction gives
\[
 \alpha_i-\alpha_j
 =-A\frac{e_i-e_j}{(e_4-e_i)(e_4-e_j)}
 =c\,d_{ij}d_{k4}.
\]
Consequently our exact root ordering has
\[
 \Delta_{12}=c\,d_{12}d_{34},\qquad
 \Delta_{13}=c\,d_{13}d_{24},\qquad
 \Delta_{23}=c\,d_{23}d_{14}.
 \tag{2.1}
\]
Here \(\Delta_{ij}=\alpha_i-\alpha_j\), and \(\Delta_{ji}=-\Delta_{ij}\). The universal multiplier in this explicit normalization is exactly 1. The three differences satisfy \(\Delta_{13}=\Delta_{12}+\Delta_{23}\); equivalently \(d_{13}d_{24}=d_{12}d_{34}+d_{23}d_{14}\). The IDEA's displayed ordering of the first and third products must therefore be tied to an explicit root ordering before use. Formula (2.1), not an unlabeled resolvent convention, fixes all signs here.

**[Derived candidate]** Replacing \(c\) by \(dc\) scales \(A,\alpha_i,\Delta_{ij}\) by \(d\). The cubic for \(dc\) is \(Y^2=\prod(X-d\alpha_i)\), with isomorphism over \(K(\sqrt d)\) given by \(X=dX_0,\;Y=d\sqrt d\,Y_0\). This is precisely the quadratic twist relation. If \(d\) is nonsquare, the associated quadratic character flips every difference sign. Define the twist sign here to be \(t=\chi_K(c)\); its bit is \(T\in\mathbb F_2\) with \(t=(-1)^T\). Thus no unknown constant is absorbed into \(t\). Relative to any initial coefficient \(c_0\), the signs are instead \(t=\chi_K(c_0)(-1)^u\); an arbitrary relative bit \(u\) alone cannot replace \(t\) without specifying \(c_0\).

## 3. Correct halving test and rational 4-torsion count

**[Source theorem]** For a monic cubic with three distinct roots in a field of characteristic different from 2, Bekker–Zarhin Theorem 2.1 tests halving by the three square differences from a point's abscissa. Example 2.2 specializes to a nonidentity 2-torsion point and supplies four rational halves when its two nonzero differences are squares. [Primary source, Section 2](https://arxiv.org/html/1702.02255v2#S2).

**[Derived candidate]** Let \(W_i=(\alpha_i,0)\) and \(\varepsilon=\chi_K(-1)\). Set \(s_{ij}=\chi_K(\Delta_{ij})\) for \(i<j\). The zero difference at \(W_i\) is a square; its character is never incorrectly required to be \(+1\). The two *nonzero* tests are
\[
\begin{array}{c|c|c}
\text{point}&\text{actual differences}&\text{halvable iff}\\
W_1&\Delta_{12},\Delta_{13}&s_{12}=s_{13}=+1\\
W_2&-\Delta_{12},\Delta_{23}&\varepsilon s_{12}=s_{23}=+1\\
W_3&-\Delta_{13},-\Delta_{23}&\varepsilon s_{13}=\varepsilon s_{23}=+1 .
\end{array}\tag{3.1}
\]
These reversed signs carry the \(q\bmod4\) distinction.

**[Derived candidate]** If \(h\) of \(W_1,W_2,W_3\) are halvable, then
\[
 |E_c(K)[4]|=4+4h.
 \tag{3.2}
\]
Indeed the rational kernel of doubling is all four points of \(E_c[2]\), so a nonempty rational fibre is a coset of size four. The fibre above \(O\) is those same four kernel points. Fibres above the three \(W_i\) are disjoint. Also \(E_c[2](K)\cap2E_c(K)\) is a subgroup, so \(h\in\{0,1,3\}\), not 2. If \(\varepsilon=-1\), (3.1) prevents two distinct nonidentity points from both being halvable, so 16 is excluded directly. No appeal to an unverified Weil-pairing claim is needed for this check.

**[Derived candidate]** The square-class *coordinates* of each test are affine linear in the input bits below. The truth value of two simultaneous square-class equations is generally a conjunction, not itself an \(\mathbb F_2\)-linear function. This is a necessary precision to the IDEA's phrasing.

## 4. Norm character, negative indices, twist action and shift invariance

**[Derived candidate]** For \(z\in K^\times\),
\[
 \chi_q(N_{K/\mathbb F_q}z)
 =(z^{(q^n-1)/(q-1)})^{(q-1)/2}
 =z^{(q^n-1)/2}=\chi_K(z).
 \tag{4.1}
\]
Let \(C_k=N(x-\sigma^k x)\) for \(k\not\equiv0\bmod n\), and let \(h_n=(n-1)/2\) and \(b_k=\chi_q(C_k)\) for \(1\le k\le h_n\). All \(C_k\ne0\) by the exact orbit hypothesis. Since norm is Frobenius invariant,
\[
 C_{-k}=N(-\sigma^{-k}(x-\sigma^kx))=(-1)^n C_k=-C_k.
\]
For odd \(n\), \(\chi_K(-1)=\chi_q(-1)=:\varepsilon\). Define
\[
 \beta(k)=
 \begin{cases}
 b_k&1\le k\le h_n,\\
 \varepsilon b_{n-k}&h_n<k<n.
 \end{cases}
\]
Then \(N(d_{ij})=C_{a_j-a_i}\) and \(\chi_K(d_{ij})=\beta(a_j-a_i)\). All indices are reduced modulo \(n\) before applying \(\beta\).

**[Derived candidate]** Combining (2.1) with (4.1),
\[
 \begin{split}
 s_{12}&=t\,\beta(a_2-a_1)\beta(a_4-a_3),\\
 s_{13}&=t\,\beta(a_3-a_1)\beta(a_4-a_2),\\
 s_{23}&=t\,\beta(a_3-a_2)\beta(a_4-a_1).
 \end{split}\tag{4.2}
\]
Encoding \(\varepsilon=(-1)^E,\;b_k=(-1)^{B_k}\) turns products into sums in \(\mathbb F_2\). A negative index contributes \(E\). A quadratic twist contributes \(T\mapsto T+1\), flipping all three \(s_{ij}\). Conditions (3.1) then become pairs of explicit affine linear equations.

**[Derived candidate]** Replacing \(x\) by \(\sigma^r x\) leaves every \(C_k\) unchanged. Equivalently translating all \(a_i\) leaves their differences unchanged. Thus the bit vector and (4.2) are invariant under a common Frobenius shift. If the whole curve is conjugated, \(c\mapsto\sigma^r c\) also preserves \(t\). Permuting branch labels changes the chosen origin and root labels; the halvability count is invariant under the resulting pointed elliptic-curve identifications, although the named \(W_i\) may change. This is not a claim that raw \(b_k\) are a complete isomorphism invariant.

## 5. The n=5 cases and the unit being counted

**[Derived candidate]** A four-of-five orbit subset is a common Frobenius translate of \(S=\{0,1,2,3\}\); take that order for \(a_1,\ldots,a_4\). Put \(p=b_1b_2\) and \(r=\varepsilon p\). The gaps in (4.2) give
\[
 (s_{12},s_{13},s_{23})=(t,t,tr)=(t,t,t\varepsilon p).
 \tag{5.1}
\]
In particular the first two are exactly \(t\), rather than merely having some unspecified common square class.

**[Derived candidate]** Substituting (5.1) into (3.1) gives the following complete symbolic table. This table is written algebra, not an enumerated panel.

| \(\varepsilon\) | \(t\) | \(p=b_1b_2\) | halvable nonidentity 2-torsion | \(h\) | \(|E_c(K)[4]|\) |
|---|---|---|---|---|---|
| \(-1\) | \(+1\) | \(+1\) | \(W_1\) | 1 | 8 |
| \(-1\) | \(+1\) | \(-1\) | \(W_1\) | 1 | 8 |
| \(-1\) | \(-1\) | \(+1\) | \(W_2\) | 1 | 8 |
| \(-1\) | \(-1\) | \(-1\) | \(W_3\) | 1 | 8 |
| \(+1\) | \(+1\) | \(+1\) | \(W_1,W_2,W_3\) | 3 | 16 |
| \(+1\) | \(+1\) | \(-1\) | \(W_1\) | 1 | 8 |
| \(+1\) | \(-1\) | \(+1\) | none | 0 | 4 |
| \(+1\) | \(-1\) | \(-1\) | none | 0 | 4 |

**[Derived candidate]** For example, \(W_2\) requires \(t=\varepsilon\) and \(tr=+1\), hence \(r=\varepsilon\); \(W_3\) requires \(t=\varepsilon\) and \(r=+1\). This explicitly accounts for the reversed differences. For \(q\equiv3\bmod4\), every such normalized quartic has size-8 rational 4-torsion and \(8\mid\#E_c(K)\). For \(q\equiv1\bmod4\), the nonsquare coefficient member has size 4 and the square coefficient member has size 8 or 16 as specified. These are candidate statements for every actual orbit configuration; the table does not assert every formal bit cell is realizable.

**[Derived candidate]** For a *fixed ordered branch configuration* with the two coefficient square classes counted once each and equal weight, exactly one entry of its twist pair has size 4 when \(q\equiv1\bmod4\). Averaging this over any multiset of such configurations that retains both entries with equal weight gives exactly one half. No bit equidistribution assumption is needed for that paired count.

**[Unresolved]** An equal share among distinct \(K\)-isomorphism classes does not follow from that count. Multiple orbit representatives, omitted conjugates, branch orderings, projective coordinate changes and distinct configurations can represent the same class with different multiplicities. Automorphisms and self-equivalences can change fibre sizes or identify pair entries. A chosen class measure requires an explicit pushforward of weights, stabilizer handling, and the special-\(j\) convention. Even generic \(j\) does not by itself justify discarding those multiplicities. The IDEA's unqualified share prediction must therefore be scoped to the paired configuration measure or proved separately.

**[Internal observation]** The pinned sibling census reports genus 5 at \(q=3\) on 20 of 60 split classes with size-8 rational 4-torsion and on 0 of 21 with size 4. Its identification of the genus-5 family with four-of-five conjugates is an internal source statement here. This task neither replays that census nor independently proves the entire genus-floor classification. The candidate torsion table is compatible with the reported restriction; compatibility is not independent validation or a converse genus criterion.

## 6. Exceptions, characteristic and nearby objects

**[Derived candidate]** The pointwise normalization and halving algebra require only characteristic different from 2, \(c\ne0\), four distinct branch points and a specified rational branch origin. They do not require short Weierstrass form, generic \(j\), or division by 3. Exact orbit length and distinct residues enforce distinctness for the proposed finite-field family. Repeated branches, \(c=0\), \(x\) of shorter orbit, even characteristic, or a branch sent to infinity outside this affine chart require a changed formulation rather than inserting zero into a quadratic-character bit.

**[Unresolved]** For characteristic greater than 3, \(j=0\) and \(j=1728\) have additional twists beyond the chosen quadratic coefficient pair. The pairwise algebra still concerns the two specified coefficients of a fixed quartic, but does not count every twist form or prove the two entries always remain distinct after forgetting branch structure. In characteristic 3 the values \(0\) and \(1728\) coincide; extra automorphisms must be treated together, and the usual separate generic/quartic/sextic-twist shorthand cannot supply a counting rule. A future class census must retain automorphism and representation information or state exclusions explicitly.

**[Derived candidate]** For a projective change \(z'=(az+b)/(rz+s)\) over \(\mathbb F_q\) with determinant \(D\ne0\) and all \(re_i+s\ne0\), choosing \(y'=y/(rz+s)^2\) changes the quartic coefficient to
\[
 c'=c\,\prod_i(re_i+s)/D^4.
\]
Meanwhile \(d'_{ij}=D\,d_{ij}/((re_i+s)(re_j+s))\). Each product \(c'd'_{ij}d'_{k\ell}\), with all four indices present, is \(cd_{ij}d_{k\ell}/D^2\). Thus the coefficient correction removes the spurious common character factor; keeping only transformed branch differences and the old \(c\) would be wrong. A chart with a pole at a branch requires a separate affine normalization.

**[Unresolved]** Nearby genus-17/genus-25 split curves are not assumed to be four-of-five configurations and must use the general difference test without imposing (5.1). A purported proof that forces size 8 for every split cubic at \(\varepsilon=-1\) proves too much: (3.1) permits size 4 for general triples of signs. The \(n=3\) hyperelliptic family is also a separate branch construction: four distinct points cannot all lie in one orbit of length 3, so (5.1) is inapplicable. These are scope controls for a future design, not new observations about those families.

## 7. Prospective n=7 statement for S={0,2,3,4}

**[Derived candidate]** Before any new data, fix \(a_1=0,a_2=2,a_3=3,a_4=4\), \(e_4=\sigma^4x\) as origin, and \(b_1,b_2,b_3\) as in section 4. Formula (4.2) gives
\[
 (s_{12},s_{13},s_{23})
 =(t b_1b_2,\;t b_2b_3,\;t\varepsilon b_1b_3).
 \tag{7.1}
\]
Write \(R=b_1b_2,\;S_*=b_2b_3\), so \(b_1b_3=RS_*\). The three pre-data indicators are
\[
 \begin{split}
 I_1&=\mathbf1[tR=+1,\ tS_*=+1],\\
 I_2&=\mathbf1[\varepsilon tR=+1,\ t\varepsilon RS_*=+1],\\
 I_3&=\mathbf1[\varepsilon tS_*=+1,\ tRS_*=+1].
 \end{split}
\]
Equivalently \(I_1=1\) iff \(R=S_*=t\);
\(I_2=1\) iff \(S_*=+1,\ tR=\varepsilon\);
\(I_3=1\) iff \(R=\varepsilon,\ tS_*=\varepsilon\).
The candidate prediction is
\[
 |E_c(K)[4]|=4(1+I_1+I_2+I_3).
 \tag{7.2}
\]
All signs, the twist convention and named origin are fixed here. A common Frobenius shift leaves the law unchanged.

**[Derived candidate]** Unlike the \(n=5\) specialization, (7.1) does not algebraically force size 8 at \(\varepsilon=-1\). For instance the *formal* sign choice \(t=+1,R=+1,S_*=-1,\varepsilon=-1\) makes all indicators zero. This is a symbolic possibility, not a constructed finite-field counterexample or a claim that the cell occurs.

**[Unresolved]** Realizability and frequency of the \(n=7\) bit cells, and identification of this subset with a specified minimal-genus family, remain separate. No genus assertion, class fraction, or new \(n=7\) data is supplied by (7.1)-(7.2).

## 8. Deterministic law versus distribution heuristic; readiness

**[Derived candidate]** Equations (2.1), (3.1), (4.2), (5.1) and (7.1)-(7.2) are deterministic candidate formulas for their stated objects. They make no estimate of the distribution of \(b_k\), imply no attack cost, and assert no transfer from native prime-field ECDLP. The \(n=5\) equal-weight twist-pair conclusion is independent of H1.

**[Heuristic]** The IDEA's H1 asserts that \((b_1,b_2)\) is equidistributed with cell error \(O(q^{-1/2})\). Such a sentence needs a specified configuration space and measure, precise range of \(q\), excluded locus, and constants. An ordered \(x\)-space and a quotient by projective transformations with omitted-conjugate and twist labels are different measures. No H1 estimate is established in this intake.

**[Unresolved]** No exact primary Weil/Katz statement with checked hypotheses was located or read for these norm polynomials and this quotient. A future proof would have to identify the relevant characters and varieties, show geometric nontriviality rather than a square or constant relation, control degeneracy and stabilizer strata, and justify the claimed error after the chosen weighting. Those are conditions to prove, not evidence that any ready-made estimate applies. No distribution panel or significance calculation was performed.

**[Source theorem]** The Chao–Momose slides give classification and minimal-genus context under a specified isogeny condition, plus related branch families; they do not independently assess this candidate normalization and bit law. [ECC2007 source](https://maths.ucd.ie/~gmg/ECC2007Talks/chao.pdf), slides 17-21, 24-27.

**[Unresolved]** A complete prospective scientific design is not certified ready by these documents. The normalized deterministic statement is now concrete enough for a separately frozen independent assessment. Full-text prior-art access, independent proof assessment, a chosen counting unit and optional H1 support remain distinct gaps. An experiment contract, implementation, controls, export schema and approvable preapproval packet have not been produced.

**[Unresolved — one recommended next action]** Coordinator should commission one bounded, zero-run independent source-and-proof assessment of this normalized deterministic statement, under a frozen review plan, requiring actual 2015/805 full-text acquisition or an explicit continuing access gap. Its acceptance questions are the pointed quartic/cubic map, signs in all three halving tests, the eight-row \(n=5\) table, and the \(n=7\) formulas; it must preserve paired-configuration weighting and leave H1 unproved unless a checked primary theorem is supplied. Passing would support moving to prospective design; a failed joint requires scoped reformulation. This is a recommendation only, with no new task, decision, approval or scientific status created here.

